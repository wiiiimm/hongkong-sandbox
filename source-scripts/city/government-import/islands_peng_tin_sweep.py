"""Examine remaining current disjoint Peng originals using ordinary CPU workers.

Preserves every negative and writes source-bound actionable outcomes to Neon.
Clear groups await actual browser review; this driver never installs anything.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import uuid
from islands_direct_stage import ROOT, HERE, read, save, rel, sha
from run import connect, reservations, jobs, dict_row


def checkpoint(doc, batch):
    nomination=read(doc/'nomination.json');stage=read(doc/'terrain-stage.json')
    runtime_path=doc/'runtime-current/results.json.gz';runtime={};runtime_job=None
    refs=[doc/'nomination.json',doc/'terrain-stage.json',Path(__file__)]
    if runtime_path.exists():
        result=read(runtime_path);sync=read(runtime_path.parent/'neon-sync.json')
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            state,stored=db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(sync['jobId'],)).fetchone()
        assert sync['exactResultMatch'] and state=='complete'
        assert stored['evidence']=={'path':rel(runtime_path),'sha256':sha(runtime_path)}
        assert {k:v for k,v in stored.items() if k not in ('jobId','evidence')}==result
        runtime={r['uid']:r for r in result['rows']};runtime_job=sync['jobId']
        refs.extend([runtime_path,runtime_path.parent/'neon-sync.json'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
    assert sha(manifest)==nomination['manifestSHA256']
    outcomes=[]
    for row in nomination['rows']:
        uid=row['uid'];source=ROOT/row['candidate']['path'];assert sha(source)==row['candidate']['entry']['sha256']
        reasons=runtime[uid]['reasons'] if uid in runtime else stage['reasons'][uid]
        outcomes.append({'uid':uid,'sourceSHA256':row['candidate']['entry']['sha256'],
            'status':'held-for-compute' if reasons else 'awaiting-browser-review','reasons':reasons,
            'requiresAI':False,'requiresUserDecision':False,'sourceGeometryChanges':0,
            'next':'Resolve recorded source/terrain/neighbour negatives; retain current model' if reasons else 'Actual staged/live browser review and guarded installation'})
    assert len(outcomes)==len(nomination['uids']) and 0<len(outcomes)<=50
    pins={rel(p):sha(p) for p in refs}
    report={'rows':outcomes,'models':len(outcomes),'heldForCompute':sum(bool(r['reasons']) for r in outcomes),
        'awaitingBrowserReview':sum(not r['reasons'] for r in outcomes),'requiresAI':0,'requiresUserDecision':0,
        'runtimeJob':runtime_job,'inputHashes':pins,'publication':False,'newlyInstalled':0,'modelReviewWrites':0}
    output=doc/'actionable-outcomes.json.gz';assert not output.exists();save(output,report)
    ledger_batch=batch+'-outcomes';claim=reservations.claim('codex-peng-sweep-outcomes-'+str(uuid.uuid4()),['building:'+r['uid'] for r in outcomes],batch=ledger_batch,ttl=600)
    assert claim['ok'],'Existing owner; no takeover'
    receipt=json.loads(json.dumps(claim['reservation'],default=str));save(HERE/'local'/ledger_batch/'reservation.json',receipt)
    try:
        payload={'path':rel(output),'sha256':sha(output)};jobid=jobs.enqueue(ledger_batch,'islands-original-actionable-outcomes-v1',payload)
        job=jobs.claim(ledger_batch,receipt['owner'],['islands-original-actionable-outcomes-v1'],lease_seconds=600,job_ids=[jobid]);assert job and job['id']==jobid
        result={**report,'jobId':jobid,'evidence':payload}
        with connect() as db:
            db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
            group=reservations._current(db,receipt);assert group and {'building:'+r['uid'] for r in outcomes}<=set(group['resources'])
            for p,h in pins.items():assert sha(ROOT/p)==h,p
            assert jobs.finish(job,result=result,connection=db)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',result)
        save(doc/'actionable-outcomes-neon-sync.json',{'jobId':jobid,'exactResultMatch':True,'models':len(outcomes)})
    finally:
        if reservations.owns(receipt):reservations.release(receipt)
    return {k:v for k,v in report.items() if k not in ('rows','inputHashes')}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bounds',type=Path,required=True);parser.add_argument('--waves',type=int,required=True);args=parser.parse_args()
    assert 1<=args.waves<=16
    bounds=args.bounds.resolve();assert bounds.is_relative_to(ROOT)
    expected=read(bounds)['currentManifest']['sha256']
    base=ROOT/'docs/astra-city/government-import';control=base/'government-islands-peng-chau-sweep-control-20261106-v1'
    assert not control.exists();save(control/'state.json',{'state':'starting','publication':False})
    completed=[];seen=set()
    def call(phase,command):
        assert sha(ROOT/'3d-viewer/city/data/manifest.json')==expected
        log=control/(batch+'-'+phase+'.log');assert not log.exists()
        save(control/'state.json',{'state':phase,'batch':batch,'completed':completed,'publication':False})
        with log.open('x') as stream:
            code=subprocess.run([str(x) for x in command],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT).returncode
        if code:
            save(control/'state.json',{'state':'script-error','batch':batch,'phase':phase,'exitCode':code,'log':rel(log),'completed':completed,'publication':False})
            raise RuntimeError('Inspect retained exact failure before resuming; no automatic publication')
    for number in range(1,args.waves+1):
        batch=f'government-islands-peng-chau-sweep-{number:03d}-20261106-v1';doc=base/batch
        call('nominate',[sys.executable,HERE/'islands_peng_tin_sweep_nominate.py','--batch',batch])
        nomination=read(doc/'nomination.json');uids=set(nomination['uids']);assert not(uids&seen);seen.update(uids)
        if not uids:
            save(control/'state.json',{'state':'current-disjoint-nominations-exhausted','completed':completed,'sourcesExamined':len(seen),'publication':False,'newlyInstalled':0});return
        call('terrain',[sys.executable,HERE/'islands_stage_owned.py','--batch',batch,'--script','islands_peng_tin_sweep_stage.py','--pass-batch'])
        identity=doc/'identity-evidence.json.gz'
        if read(doc/'terrain-stage.json')['stagedSourceCandidates']:
            call('scope',[sys.executable,HERE/'islands_tin_current_scope.py','--batch',batch,'--bounds',bounds,'--identity',identity])
            call('runtime',[sys.executable,HERE/'islands_tin_runtime.py','--source-batch',batch,'--batch',batch+'-runtime','--wait'])
            if read(doc/'runtime-current/summary.json')['clearScriptCandidates']:
                call('clear',[sys.executable,HERE/'islands_tin_clear_subset.py','--source-batch',batch,'--batch',batch+'-clear','--identity',identity])
        outcome=checkpoint(doc,batch);completed.append({'batch':batch,**outcome})
        print(json.dumps(completed[-1]),flush=True)
    save(control/'state.json',{'state':'explicit-wave-limit-complete','completed':completed,'sourcesExamined':len(seen),'publication':False,'newlyInstalled':0})


if __name__=='__main__':main()
