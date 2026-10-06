"""Consolidate finished explicit stages with exact evidence and fenced Neon readback."""
import argparse
from collections import Counter
import json
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row


def ref(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':digest(path.read_bytes())}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True)
    p.add_argument('--primary',action='append',required=True)
    p.add_argument('--followups',action='append',default=[])
    p.add_argument('--base',action='append',required=True)
    p.add_argument('--extra-stage',action='append',default=[],help='Fresh completed result directory for an explicit primary UID')
    p.add_argument('--installation',action='append',default=[],help='Completed installed result directory')
    args=p.parse_args()
    assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/args.batch
    assert not doc.exists(),'Completed checkpoints are immutable'
    commands=[];extra=[];references=[];contexts={}
    for path in args.primary+args.followups+args.base+args.extra_stage+args.installation:
        assert (ROOT/path).resolve().is_relative_to(ROOT)
    for path in args.primary:
        file=ROOT/path/'commands.json';commands.extend(read(file)['rows']);references.append(ref(file))
    for path in args.followups:
        file=ROOT/path/'commands.json';extra.extend(read(file)['rows']);references.append(ref(file))
    for path in args.extra_stage:
        file=ROOT/path/'result.json';result=read(file)
        uids={r['uid'] for r in result.get('rows',[])}
        uid=result.get('uid') or (next(iter(uids)) if len(uids)==1 else None)
        assert uid, 'Extra stage needs one explicit primary UID'
        extra.append({'uid':uid,'batch':result['batch'],'returncode':0,'result':result,'log':None})
        references.append(ref(file))
    assert commands and len({r['uid'] for r in commands})==len(commands)
    for path in args.base:
        for name in ['check-selection.json.gz','context.json.gz','preflight.json','explicit-uids.json']:
            references.append(ref(ROOT/path/name))
        for row in read(ROOT/path/'context.json.gz')['rows']:
            assert row['uid'] not in contexts;contexts[row['uid']]=row
    assert set(contexts)=={r['uid'] for r in commands}
    phases=[];completed={};tokens=[];scope=set(contexts)
    by_uid={r['uid']:[] for r in commands};latest={r['uid']:r['result'] for r in commands}
    failures=[]
    for command in commands+extra:
        uid=command['uid'];assert uid in contexts
        target=ROOT/'docs/astra-city/government-import'/command['batch']
        if command['returncode']!=0 or not command['result']:
            failures.append({'uid':uid,'batch':command['batch'],'returncode':command['returncode'],
                             'log':command['log'],'reason':'incomplete-command-evidence','recoveredBy':None})
            continue
        result=read(target/'result.json');sync=read(target/'neon-sync.json')
        assert result==command['result'] and sync['resultVerified'] and sync['jobId']==result['jobId']
        assert not result['activeWorkers'] and not result['queuedFollowups']
        assert not result['newlyInstalled'] and not result['publication']
        assert result['jobId'] not in completed
        for evidence in result['evidenceRefs']:
            assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256']
        tokens.append(read(HERE/'local'/command['batch']/'reservation.json')['token'])
        completed[result['jobId']]=result
        references.extend([ref(target/'result.json'),ref(target/'neon-sync.json')])
        phase={'uid':uid,'batch':command['batch'],'jobId':result['jobId'],'supportRows':result.get('rows',[]),
               'sourceSHA256':result.get('sourceSHA256'), 'reasons':result.get('reasons')}
        phases.append(phase);by_uid[uid].append(phase)
        if result.get('uid')==uid:
            assert result['sourceSHA256']==contexts[uid]['sourceSHA256'];latest[uid]=result
        else:
            for pair in result.get('rows',[]):
                if pair.get('supportUid'):scope.add(pair['supportUid'])
    for failure in failures:
        successors=[p for p in by_uid[failure['uid']] if p['sourceSHA256']==contexts[failure['uid']]['sourceSHA256']]
        if successors:failure['recoveredBy']=successors[-1]['jobId']
    assert not any((r['returncode']!=0 or not r['result']) and not latest[r['uid']] for r in commands), 'Primary failures need explicit recovered evidence'
    installations={}
    for path in args.installation:
        directory=ROOT/path;result=read(directory/'result.json');sync=read(directory/'neon-sync.json')
        assert result['publication'] and sync['resultVerified'] and sync['jobId']==result['jobId']
        assert result['newlyInstalled']==len(result['installedUids']) and not result['activeWorkers'] and not result['queuedFollowups']
        completed[result['jobId']]=result
        for evidence in result['evidenceRefs']:assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256']
        for uid in result['installedUids']:
            assert uid in contexts and uid not in installations and result['sourceSHA256']==contexts[uid]['sourceSHA256']
            installations[uid]={'jobId':result['jobId'],'sourceSHA256':result['sourceSHA256'],'result':ref(directory/'result.json'),'installedAcceptance':ref(directory/'installed-acceptance.json')}
        references.extend([ref(directory/'result.json'),ref(directory/'neon-sync.json')])
        tokens.append(read(HERE/'local'/result['batch']/'install-reservation.json')['token'])
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer=read(pointer_path);references.append(ref(pointer_path))
    progress_path=ROOT/'3d-viewer/city/data/building-progress.json';references.append(ref(progress_path))
    cohort={r['uid'] for r in read(ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923/selection.json.gz')['rows']}
    claim=reservations.claim('codex-xl-explicit-checkpoint-'+str(uuid.uuid4()),
        [('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)],batch=args.batch)
    assert claim['ok'],claim
    lease=claim['reservation']
    try:
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            actual={id:(status,result) for id,status,result in con.execute(
                'SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',(list(completed),))}
            assert set(actual)==set(completed)
            assert all(actual[id]==('complete',result) for id,result in completed.items())
            assert not con.execute('SELECT token FROM astra_modelling.reservation_groups WHERE token=ANY(%s::uuid[]) AND released_at IS NULL AND lease_until>clock_timestamp()', (tokens,)).fetchall()
            reviews=dict(con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(pointer['snapshotId'],)))
        rows=[]
        for command in commands:
            uid=command['uid'];result=latest[uid]
            if uid in installations:
                assert reviews.get(uid)=='installed-verified'
                rows.append({'uid':uid,'name':command['name'],'sourceSHA256':contexts[uid]['sourceSHA256'],
                    'humanStatus':'installed','installed':True,'reasons':[],'blockerGroup':'installed',
                    'projectionFailures':[],'phases':by_uid[uid],'installation':installations[uid],
                    'commandFailures':[f for f in failures if f['uid']==uid],'requiresAI':False,'requiresHumanDecision':False,'nextStep':None})
                continue
            assert result and result['reasons'], 'Passing candidates must reach guarded installation or an explicit failed acceptance stage first'
            assert reviews.get(uid)!='installed-verified','Installed successors need installation evidence'
            identity=contexts[uid]['identity'];fit=[]
            if identity['targetCoveredBySourceProjection']<.95:fit.append('target-coverage')
            if not (identity['sourceProjectionInsideTarget']>=.98 or
                identity['sourceExcessFraction']<=.1 and identity['sourceExcessCoveredByUnrelatedFormsM2']<=1
                and identity['sourceExcessMaximumDistanceFromTargetM']<=10):fit.append('source-excess')
            group='source-footprint-fit' if result['reasons']==['source-identity-fit'] else (
                  'terrain-runtime-budget' if any('terrain-runtime-budget' in r for r in result['reasons']) else 'terrain-neighbours-or-support')
            rows.append({'uid':uid,'name':command['name'],'sourceSHA256':result['sourceSHA256'],
                'humanStatus':'held-unknown','installed':False,'reasons':result['reasons'],
                'blockerGroup':group,'projectionFailures':fit if group=='source-footprint-fit' else [],
                'phases':by_uid[uid], 'commandFailures':[f for f in failures if f['uid']==uid],
                'requiresAI':False,'requiresHumanDecision':False,
                'nextStep':'Reuse pinned originals and completed source/contact/support evidence. Resolve the explicit technical blocker without geometry edits or acceptance-limit increases.'})
        installed=sum(reviews.get(uid)=='installed-verified' for uid in cohort)
        payload={'evidenceRefs':references,'runnerSHA256':digest(Path(__file__).read_bytes()),'reviewSnapshot':pointer['snapshotId']}
        stage='explicit-source-continuation-checkpoint-v1';jobid=jobs.enqueue(args.batch,stage,payload)
        job=jobs.claim(args.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
        result={**payload,'batch':args.batch,'jobId':jobid,'rows':rows,'primarySources':len(rows),
            'completedPhaseJobs':len(completed),'phases':phases,'commandFailures':failures,
            'blockerGroups':dict(Counter(r['blockerGroup'] for r in rows)),
            'projectionFailureGroups':dict(Counter(','.join(r['projectionFailures']) for r in rows if r['projectionFailures'])),
            'newlyInstalled':len(installations),'humanCounts':{'installed':len(installations),'to-do':0,'held-human':0,'held-ai':0,'held-unknown':len(rows)-len(installations),'in-process':0},
            'widerXLCheckpoint':{'models':len(cohort),'installed':installed,'held':len(cohort)-installed},
            'activeWorkers':0,'queuedFollowups':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,
            'publication':bool(installations),'progress':read(progress_path),
            'qualification':'Exact current Neon/readbacks and immutable completed source phases. Installation credit requires complete installed successor receipts and current installed-verified ledger. Technical holds alone do not establish an AI/human requirement. Original payload caches remain local-only.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
        save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
        print(json.dumps({'primarySources':len(rows),'phases':len(completed),'blockerGroups':result['blockerGroups'],'XL':result['widerXLCheckpoint'],'jobId':jobid,'neonVerified':True}),flush=True)
    finally:
        reservations.release(lease)


if __name__=='__main__':main()
