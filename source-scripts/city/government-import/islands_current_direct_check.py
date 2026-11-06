"""Fresh direct-original checks after nearby installed terrain has changed.

Explicit <=50-source cohorts; immutable government assets, no proposed terrain,
no browser approval/publication and no model-review writes.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid
from collections import Counter
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, policy
from run import connect, reservations, jobs, dict_row


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert a.batch.startswith('government-islands-') and '/' not in a.batch
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch;stage=HERE/'accepted'/a.batch
    selected=read(doc/'selection.json.gz');rows=selected['rows'];assert 0<len(rows)==len({r['uid'] for r in rows})<=50
    assert selected['manifestSHA256']==sha(ROOT/'3d-viewer/city/data/manifest.json')
    if not a.owned:
        assert not local.exists();owner='codex-islands-direct-recheck-'+str(uuid.uuid4());deadline=time.monotonic()+14400
        while True:
            assert selected['manifestSHA256']==sha(ROOT/'3d-viewer/city/data/manifest.json') and time.monotonic()<deadline
            claim=reservations.claim(owner,['building:'+r['uid'] for r in rows],batch=a.batch,ttl=3600)
            if claim['ok']:break
            time.sleep(15)
        receipt=json.loads(json.dumps(claim['reservation'],default=str));path=local/'reservation.json';save(path,receipt)
        subprocess.run([sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',path,'--ttl','3600','--',sys.executable,__file__,'--batch',a.batch,'--owned'],cwd=ROOT,check=True)
        return
    receipt=read(local/'reservation.json');assert reservations.owns(receipt) and not stage.exists()
    pins={**selected['inputHashes'],rel(Path(__file__)):sha(Path(__file__))}
    for path,h in pins.items():assert sha(ROOT/path)==h,path
    catalogue=read(HERE.parent/'kai-tak-port/staged/catalogue.json');catalogue={k:v for k,v in catalogue.items() if k not in ('area','models','counts')};models=[]
    for row in rows:
        entry={**row['candidate']['entry'],'priority':'detail','proceduralWindows':False,'placementReviewed':False,'sourceIdentityReviewed':False,'identityReviewApproved':False,'publicationApproved':False}
        source=ROOT/row['candidate']['path'];assert sha(source)==entry['sha256'];pins[rel(source)]=entry['sha256'];target=stage/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());models.append(entry)
    catalogue.update(area='Island originals rechecked on current installed terrain',models=models,counts={'packedModels':len(models)})
    save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']})
    save(doc/'source-forms.json',{r['uid']:r['source'] for r in rows})
    commands=[([sys.executable,HERE/'dependency_preflight.py','--catalogue',stage/'catalogue.json','--out',doc/'dependency-preflight.json'],(0,)),
              (['node',HERE/'original_private_catalogue_preflight_v1_20261103.mjs',rel(stage/'catalogue.json')],(0,)),
              (['node',HERE.parent/'building-batch/validate_candidates.mjs','--candidates',rel(stage),'--source-forms',rel(doc/'source-forms.json'),'--out',rel(doc/'validation.json')],(0,1)),
              (['node',HERE/'acceptance-metrics.mjs','--selection',rel(doc/'selection.json.gz'),'--candidates',rel(stage),'--out',rel(doc/'metrics.json')],(0,))]
    for args,allowed in commands:assert subprocess.run([str(x) for x in args],cwd=ROOT).returncode in allowed
    metrics=read(doc/'metrics.json');by_uid={r['uid']:r for r in rows};validation={r['uid']:r for r in read(doc/'validation.json')['results']};deps={r['uid']:r for r in read(doc/'dependency-preflight.json')['rows']}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');states=dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',(list(by_uid),)))
    outcomes=[]
    for m in metrics['rows']:
        uid=m['uid'];row=by_uid[uid]
        reasons=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['candidate']['entry']['sha256'],'identityProof':row.get('identityProof')},m,metrics['profiles']['mobile'])
        if validation[uid]['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
        if deps[uid]['requiresAssemblyInvestigation']:reasons.append('dependency-investigation')
        if states.get(uid) in ('held','source-unavailable','identity-unresolved','installed-verified'):reasons.append('current-review-requires-resolution')
        outcomes.append({'uid':uid,'sourceSHA256':row['candidate']['entry']['sha256'],'reasons':sorted(set(reasons)),'metrics':m,'validation':validation[uid],
            'status':'held-for-compute' if reasons else 'awaiting-browser-review','requiresAI':False,'requiresUserDecision':False,'publication':False})
    assert {r['uid'] for r in outcomes}==set(by_uid)
    for path,h in {**pins,**metrics['inputHashes']}.items():assert sha(ROOT/path)==h,path
    report={'batch':a.batch,'models':len(rows),'rows':outcomes,'clearScriptCandidates':sum(not r['reasons'] for r in outcomes),'reasonCounts':dict(Counter(x for r in outcomes for x in r['reasons'])),'sourceGeometryChanges':0,'terrainChanges':0,'publication':False,'modelReviewWrites':0,'inputHashes':pins}
    result_path=doc/'results.json.gz';save(result_path,report);payload={'path':rel(result_path),'sha256':sha(result_path)};jobid=jobs.enqueue(a.batch,'islands-current-terrain-direct-check-v1',payload)
    job=jobs.claim(a.batch,receipt['owner'],['islands-current-terrain-direct-check-v1'],lease_seconds=600,job_ids=[jobid]);assert job and job['id']==jobid
    result={**report,'jobId':jobid,'evidence':payload}
    with connect() as db:
        db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));group=reservations._current(db,receipt)
        assert group and {'building:'+u for u in by_uid}<=set(group['resources'])
        for path,h in {**pins,**metrics['inputHashes']}.items():assert sha(ROOT/path)==h,path
        assert jobs.finish(job,result=result,connection=db)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',result)
    save(doc/'neon-sync.json',{'jobId':jobid,'exactResultMatch':True,'models':len(rows),'clearScriptCandidates':report['clearScriptCandidates'],'modelReviewWrites':0})
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','inputHashes')}),flush=True)


if __name__=='__main__':main()
