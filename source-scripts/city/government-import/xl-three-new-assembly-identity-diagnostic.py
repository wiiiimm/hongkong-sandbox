"""Diagnose three explicitly pinned untried tower/podium assemblies without approval.

Keep raw individual spatial failures, exact bytes, pose, whole GeoRef cells and
all unrelated-form bounds. The original strict interface and the unchanged
95% coverage/10m extent/1m2 overlap limits apply to each complete assembly.
No review, publication, terrain change or installation credit is granted here.
"""
import argparse, json, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, dict_row, Jsonb, NATIVE_RUN
from original_source_assembly_diagnostic import verify_files
from publication_lock import locked_publication
PAIRS = frozenset((f'landsd/{u}:0', f'landsd/{s}:0') for u,s in [
    ('259613','259803'),('132578','9778'),('203438','232089')])

def ref(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':digest(path.read_bytes())}

def verified_inputs(closure, a):
    prior=read(closure/'result.json');sync=read(closure/'neon-sync.json')
    assert sync == {'jobId':prior['jobId'],'resultVerified':True}
    assert not prior['publication'] and prior['newlyInstalled']==0
    assert prior['modelGeometryChanges']==prior['scriptExternalAICalls']==0
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    for evidence in prior['evidenceRefs']:assert ref(ROOT/evidence['path'])==evidence
    inputs=read(closure/'support-inputs.json');assert len(inputs['pairs'])==3
    assert {(p['uid'],p['supportUid']) for p in inputs['pairs']}==PAIRS
    pair=next(p for p in inputs['pairs'] if p['uid']==a.tower)
    wanted={pair['uid'],pair['supportUid']}
    selected=[r for r in inputs['sources'] if r['uid'] in wanted]
    assert len(selected)==2 and {r['uid'] for r in selected}==wanted
    interfaces=read(closure/'support-checks.json.gz')
    interface=next(r for r in interfaces['rows'] if r['uid']==a.tower)
    assert {k:interface[k] for k in ('uid','supportUid')}==pair
    inputs={**inputs,'sources':selected,'pairs':[pair]}
    for path,sha in interfaces['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    return prior,inputs,interface

def owned(a,doc,local,closure):
    with locked_publication(ROOT):
        receipt=read(local/'reservation.json');assert reservations.owns(receipt)
        prior,inputs,interface=verified_inputs(closure, a)
        rows=inputs['sources'];contexts={r['uid']:r for r in read(closure/'context.json.gz')['rows']}
        manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_ref=ref(manifest)
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            for row in rows:
                native=row['native']
                assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,native['cacheKey'])).fetchone()==(native['resultSha'],)
        proof=verify_files(rows,contexts,local/'identity',interface)
        assert proof['diagnosticOnly'] and not proof['installationApproved'] and not proof['publication']
        save(doc/'assembly-identity.json',proof)
        save(doc/'inputs.json',{'closure':ref(closure/'result.json'),'supportInputs':ref(closure/'support-inputs.json'),
            'context':ref(closure/'context.json.gz'),'interface':ref(closure/'support-checks.json.gz'),
            'manifest':manifest_ref,'runner':ref(Path(__file__)),'policy':ref(HERE/'original_source_assembly_diagnostic.py')})
        assert ref(manifest)==manifest_ref
        refs=[ref(p) for p in sorted(doc.iterdir()) if p.is_file()]
        payload={'evidenceRefs':refs,'uids':proof['uids'],'sourceSHA256s':proof['sourceSHA256s'],'runner':ref(Path(__file__))}
        stage='explicit-three-new-original-assembly-identity-diagnostic-v1'
        jid=jobs.enqueue(a.batch,stage,payload);job=jobs.claim(a.batch,receipt['owner'],[stage],lease_seconds=1800)
        assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':a.batch,'identityPassed':proof['passed'],'reasons':proof['reasons'],
            'measures':proof['measures'],'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,
            'scriptExternalAICalls':0,'requiresAI':False,'requiresHumanDecision':False,'activeWorkers':0,'queuedFollowups':0,
            'qualification':'Exact original assembly diagnostics only. Positive identity must still be rebound and followed by complete physical/runtime/staged/live/publication acceptance.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
            assert reservations._current(con,receipt)
            for evidence in refs:assert ref(ROOT/evidence['path'])==evidence
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'uids':proof['uids'],'identityPassed':proof['passed'],'reasons':proof['reasons'],'measures':proof['measures'],'jobId':jid,'neonVerified':True}),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--closure',required=True);p.add_argument('--batch',required=True);p.add_argument('--tower',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
    closure=(ROOT/a.closure).resolve();assert closure.parent==ROOT/'docs/astra-city/government-import'
    doc=closure.parent/a.batch;local=HERE/'local'/a.batch
    if a.owned:return owned(a,doc,local,closure)
    assert not doc.exists(),'Fresh immutable diagnostic only'
    _,inputs,_=verified_inputs(closure, a)
    claim=reservations.claim('codex-xl-assembly-diagnostic-'+str(uuid.uuid4()),['building:'+r['uid'] for r in inputs['sources']],batch=a.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
