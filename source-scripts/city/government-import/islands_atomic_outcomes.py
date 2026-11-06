"""Persist whole terrain-group outcomes without granting partial install credit."""
import argparse
import json
from pathlib import Path
import uuid
from islands_direct_stage import ROOT, HERE, read, save, sha, rel
from run import connect, reservations, jobs, dict_row


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-batch',required=True);a=p.parse_args()
    assert a.source_batch.startswith('government-islands-') and '/' not in a.source_batch
    doc=ROOT/'docs/astra-city/government-import'/a.source_batch;runtime=doc/'runtime-current'
    path=runtime/'results.json.gz';report=read(path);sync=read(runtime/'neon-sync.json')
    assert sync['exactResultMatch']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        state,stored=db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(sync['jobId'],)).fetchone()
    assert state=='complete' and stored['evidence']=={'path':rel(path),'sha256':sha(path)}
    assert {k:v for k,v in stored.items() if k not in ('jobId','evidence')}==report
    rows={r['uid']:r for r in report['rows']};groups=read(runtime/'neighbour-checks.final.json')['patches']
    assert 0<len(rows)<=50 and set().union(*(set(g['uids'])for g in groups))==set(rows)
    assert sum(len(g['uids'])for g in groups)==len(rows)
    outcomes=[]
    for group in groups:
        failed=[u for u in group['uids'] if rows[u]['reasons']]
        for uid in group['uids']:
            outcomes.append({'uid':uid,'sourceSHA256':rows[uid]['sourceSHA256'],'rawReasons':rows[uid]['reasons'],
                'atomicGroup':group['uids'],'failedGroupMembers':failed,
                'status':'queued-script-follow-up' if failed else 'awaiting-browser-review',
                'reasons':rows[uid]['reasons']+(['atomic-terrain-group-has-failed-member'] if failed else []),
                'requiresAI':False,'requiresUserDecision':False,'newlyInstalled':0})
    manifest=ROOT/'3d-viewer/city/data/manifest.json';expected=read(runtime/'selection.json.gz')['manifestSHA256'];assert sha(manifest)==expected
    refs=[path,runtime/'neon-sync.json',runtime/'neighbour-checks.final.json',manifest,Path(__file__)]
    pins={rel(p):sha(p) for p in refs}
    output=doc/'atomic-actionable-outcomes.json.gz';assert not output.exists()
    result={'rows':outcomes,'models':len(rows),'jointlyInstallableGroups':sum(not any(rows[u]['reasons']for u in g['uids'])for g in groups),
        'runtimeJob':sync['jobId'],'inputHashes':pins,'modelReviewWrites':0,'newlyInstalled':0,'publication':False}
    save(output,result);payload={'path':rel(output),'sha256':sha(output)}
    batch=a.source_batch+'-atomic-outcomes';claim=reservations.claim('codex-islands-atomic-'+str(uuid.uuid4()),['building:'+u for u in rows],batch=batch,ttl=600)
    assert claim['ok'],'Existing owner; no takeover'
    receipt=json.loads(json.dumps(claim['reservation'],default=str));save(HERE/'local'/batch/'reservation.json',receipt)
    try:
        stage='islands-original-atomic-group-outcomes-v1';jobid=jobs.enqueue(batch,stage,payload)
        job=jobs.claim(batch,receipt['owner'],[stage],lease_seconds=600,job_ids=[jobid]);assert job and job['id']==jobid
        result={**result,'jobId':jobid,'evidence':payload}
        with connect() as db:
            db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
            owned=reservations._current(db,receipt);assert owned and {'building:'+u for u in rows}<=set(owned['resources'])
            for p,h in pins.items():assert sha(ROOT/p)==h,p
            assert jobs.finish(job,result=result,connection=db)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',result)
        save(doc/'atomic-actionable-outcomes-neon-sync.json',{'jobId':jobid,'exactResultMatch':True,'models':len(rows),'jointlyInstallableGroups':result['jointlyInstallableGroups']})
        print({'models':len(rows),'jointlyInstallableGroups':result['jointlyInstallableGroups'],'jobId':jobid,'publication':False},flush=True)
    finally:
        if reservations.owns(receipt):reservations.release(receipt)


if __name__=='__main__':main()
