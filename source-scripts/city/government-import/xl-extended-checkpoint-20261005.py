"""Verify the 37-source extended pass and all follow-ups against fenced Neon jobs."""
from collections import Counter
import json
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

BATCH='government-xl-extended-checkpoint-20261005'
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/BATCH
CONTROLLERS=['government-xl-extended-14-20261005','government-xl-extended-23-20261005']
FOLLOWUPS=['government-xl-extended-rise-twin-supports-20261005',
    'government-xl-extended-estate-indexed-supports-20261005',
    'government-xl-hoi-tai-original-support-group-20261005',
    'government-xl-extended-on-ning1-original-podium-20261005',
    'government-xl-extended-silvercord-nested-20261005',
    'government-xl-extended-china-merchants-nested-20261005',
    'government-xl-extended-parkview11-retained-20261005',
    'government-xl-extended-parkview6-retained-20261005',
    'government-xl-extended-on-ning6-retained-20261005',
    'government-xl-extended-on-ning6-source-regions-20261005',
    'government-xl-extended-on-ning3-retained-20261005',
    'government-xl-extended-hoi-tai-parent-20261005',
    'government-xl-extended-hoi-tai-full-parent-20261005',
    'government-xl-extended-component-fit-20261005']
SUPPORT_UIDS=['landsd/'+str(i)+':0' for i in [294323,223206,233190,273271,254491,315025,235557,264935]]


def ref(path): return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
    assert not DOC.exists(),'Fresh immutable checkpoint only'
    commands=[r for name in CONTROLLERS for r in read(BASE/name/'commands.json')['rows']]
    assert len(commands)==37 and len({r['uid'] for r in commands})==37
    assert all(r['returncode']==0 and r['result'] for r in commands)
    claim=reservations.claim('codex-xl-extended-checkpoint-'+str(uuid.uuid4()),
        ['building:'+u for u in sorted({r['uid'] for r in commands}|set(SUPPORT_UIDS)|{'landsd/34255:0'})],batch=BATCH)
    assert claim['ok'],claim
    lease=claim['reservation']
    try:
        refs=[];completed={};phases=[]
        for name in [r['batch'] for r in commands]+FOLLOWUPS:
            folder=BASE/name;result=read(folder/'result.json');sync=read(folder/'neon-sync.json')
            assert sync['resultVerified'] and sync['jobId']==result['jobId']
            assert not result['activeWorkers'] and not result['queuedFollowups']
            assert not result['newlyInstalled'] and not result['publication']
            for evidence in result['evidenceRefs']:
                assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256']
            assert not reservations.owns(read(HERE/'local'/name/'reservation.json'))
            completed[result['jobId']]=result
            refs.extend([ref(folder/'result.json'),ref(folder/'neon-sync.json')])
            phases.append({'batch':name,'jobId':result['jobId'],'uid':result.get('uid'),
                           'reasons':result.get('reasons'),'rows':len(result.get('rows',[]))})
        for name in CONTROLLERS:
            refs.append(ref(BASE/name/'commands.json'))
        for size in (14,23):
            for filename in ['check-selection.json.gz','context.json.gz','preflight.json']:
                refs.append(ref(BASE/f'government-xl-extended-{size}-inputs-20261005'/filename))
        refs.append(ref(BASE/'government-xl-extended-on-ning-installed-support-inputs-20261005/check-selection.json.gz'))
        pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
        pointer=read(pointer_path);refs.append(ref(pointer_path))
        progress_path=ROOT/'3d-viewer/city/data/building-progress.json';progress=read(progress_path);refs.append(ref(progress_path))
        cohort={r['uid'] for r in read(BASE/'government-xl-remaining-20260923/selection.json.gz')['rows']};assert len(cohort)==352
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            actual={id:(state,result) for id,state,result in con.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',(list(completed),))}
            assert set(actual)==set(completed)
            assert all(actual[id]==('complete',result) for id,result in completed.items())
            reviews=dict(con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(pointer['snapshotId'],)))
            assert all(reviews.get(r['uid'])!='installed-verified' for r in commands)
        installed=sum(reviews.get(u)=='installed-verified' for u in cohort);assert installed==44
        rows=[]
        for command in commands:
            raw=command['result'];uid=command['uid'];assert raw['reasons']
            related=[p for p in phases if p['uid']==uid and p['batch']!=command['batch']]
            support_phases=[{'batch':name,'jobId':completed[read(BASE/name/'result.json')['jobId']]['jobId']}
                for name in FOLLOWUPS[:4] if any(r['uid']==uid for r in read(BASE/name/'result.json')['rows'])
                or (name=='government-xl-hoi-tai-original-support-group-20261005' and uid=='landsd/229881:0')]
            rows.append({'uid':uid,'name':command['name'],'sourceSHA256':raw['sourceSHA256'],
                'humanStatus':'held-unknown','installed':False,'reasons':raw['reasons'],'primaryJobId':raw['jobId'],
                'followups':related+support_phases,'requiresAI':False,'requiresHumanDecision':False,
                'blockerGroup':'source-footprint-fit' if raw['reasons']==['source-identity-fit'] else
                    'terrain-runtime-budget' if any('terrain-runtime-budget' in r for r in raw['reasons']) else 'terrain-neighbours-or-support',
                'nextStep':'Reuse exact source hashes and completed diagnostics; resolve recorded component/terrain/support blockers with all existing gates before acceptance.'})
        groups=dict(Counter(r['blockerGroup'] for r in rows));assert sum(groups.values())==37
        support_results=[read(BASE/name/'result.json') for name in FOLLOWUPS[:4]]
        pairs=[{'uid':r['uid'],'supportUid':r['supportUid'],'unresolvedSamples':r['unresolvedSamples'],'jobId':v['jobId']}
               for v in support_results for r in v['rows'] if 'supportUid' in r]
        hoi=support_results[2];assert len(hoi['rows'])==1
        pairs.append({'uid':'landsd/229881:0','supportUid':hoi['rows'][0]['uid'],
                      'unresolvedSamples':hoi['rows'][0]['unresolved'],'jobId':hoi['jobId']})
        assert len(pairs)==10 and sum(p['unresolvedSamples'] for p in pairs)==363
        payload={'evidenceRefs':refs,'runnerSHA256':digest(Path(__file__).read_bytes()),'reviewSnapshot':pointer['snapshotId']}
        stage='extended-37-source-checkpoint-v1';id=jobs.enqueue(BATCH,stage,payload)
        job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==id
        result={**payload,'batch':BATCH,'jobId':id,'rows':rows,'primarySources':37,'newlyInstalled':0,
            'completedPhaseJobs':len(completed),'phases':phases,'blockerGroups':groups,
            'supportPairs':pairs,'distinctAdditionalSupportSources':8,'installedSourceDiagnosticOnly':'landsd/34255:0',
            'humanCounts':{'installed':0,'to-do':0,'held-human':0,'held-ai':0,'held-unknown':37,'in-process':0},
            'widerXLCheckpoint':{'models':352,'installed':installed,'held':352-installed},
            'activeWorkers':0,'queuedFollowups':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,
            'publication':False,'progress':progress,
            'excludedSource':{'uid':'landsd/276331:0','reason':'Existing pending review detected before freeze; not overridden or counted among the 37.'},
            'qualification':'Completed mechanical investigations and fenced exact readbacks, with no acceptance/publication credit. Technical holds do not establish AI or human requirements. Eight additional supports and one previously installed source are diagnostics, not new installations. Ignored source payloads are local-only.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),id,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(id,)).fetchone()[0]==result
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':id,'resultVerified':True,'reviewSnapshot':pointer['snapshotId']})
        print(json.dumps({'models':37,'completedPhaseJobs':len(completed),'newlyInstalled':0,'XL':result['widerXLCheckpoint'],'blockerGroups':groups,'jobId':id,'neonVerified':True}),flush=True)
    finally:reservations.release(lease)


if __name__=='__main__':main()
