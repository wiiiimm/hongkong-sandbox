"""Recover exact government neighbour bytes; no geometry edits or acceptance."""
from pathlib import Path
import json,sys,uuid,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-neighbour-recovery-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-sol-city-companion-sources-v1-20261021'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();receipt=read(SRC/'result.json');p=SRC/'sheet-source-index.json';assert digest(p.read_bytes())==next(e['sha256']for e in receipt['evidenceRefs']if e['path']==str(p.relative_to(ROOT)));index=read(p);refs=[Path(__file__),SRC/'result.json',p,HERE/'xl-second-pass.py']
 reg=next(r for r in index['registries']if any(m['modelId']=='B206693418401063C0'for m in r['models']))
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  sha,result=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(reg['cacheKey'],)).fetchone();assert sha==reg['resultSHA256'];m=next(m for m in result['models']if m['modelId']=='B206693418401063C0')
 row=dict(uid='landsd/170270:0',modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],triangles=m['triangles'],native=dict(cacheKey=reg['cacheKey'],resultSha=sha,sheet=index['sheet'],model=m))
 assert row['sourceSHA256']=='4270cb7898cb9b5a4efd571c9c7d2e9a23a11c16dd961130463dd327fc666bae'
 prior=HERE/'local/government-xl-sol-city-star-house-supports-20261005/sheets/6-NW-9D/directory/result.json';refs.append(prior);priorSHA=digest(prior.read_bytes())
 helper=module('sol_exact_neighbour_recovery',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;recovered=helper.source_sheet(index['sheet'],[row],read(prior),{},[])
 asset=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');assert digest(asset.read_bytes())==row['sourceSHA256'];assert digest(prior.read_bytes())==priorSHA;row['assetPath']=str(asset.relative_to(ROOT));save(DOC/'recovery.json',dict(rows=[row],recovery=recovered,installationApproved=False))
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');assert reservations.owns(lease)
 module('sol_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-neighbour-recovery',refs,dict(uids=[row['uid']],exactHashMatched=True,sourceGeometryChanges=0,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/170270:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
