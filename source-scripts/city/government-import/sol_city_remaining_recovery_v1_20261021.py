"""Recover four exact neighbouring government originals under existing leases."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-remaining-recovery-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/251569:0','landsd/268424:0','landsd/65157:0','landsd/76890:0']
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();refs=[Path(__file__),HERE/'xl-second-pass.py'];allrows=[];recoveries=[]
 helper=module('sol_remaining_recovery',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL
 for version in [1,2]:
  folder=BASE/f'government-xl-sol-city-remaining-neighbours-v{version}-20261021';receipt=read(folder/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  p=folder/'nominations.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);rows=[]
  for hit in read(p)['rows']:
   m=hit['model'];rows.append(dict(uid=hit['uid'],source=hit['source'],modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],triangles=m['triangles'],native=dict(cacheKey=hit['nativeStageKey'],resultSha=hit['nativeStageSHA256'],sheet=hit['sheet'],model=m)))
  assert len(rows)==2;sheet=rows[0]['native']['sheet'];prior=HERE/'local/government-xl-sol-city-adjoining-ground-v1-20261021/sheets'/sheet/'directory/result.json';priorhash=digest(prior.read_bytes());refs.append(prior)
  recoveries.append(helper.source_sheet(sheet,rows,read(prior),{},[]))
  for row in rows:
   asset=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');assert digest(asset.read_bytes())==row['sourceSHA256'];row['assetPath']=str(asset.relative_to(ROOT))
  assert digest(prior.read_bytes())==priorhash;allrows.extend(rows)
 assert sorted(r['uid']for r in allrows)==sorted(UIDS);assert reservations.owns(lease)
 save(DOC/'recovery.json',dict(rows=allrows,recoveries=recoveries,installationApproved=False));refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 module('sol_remaining_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-exact-neighbour-original-recovery',refs,dict(uids=UIDS,recovered=4,sourceGeometryChanges=0,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+uid for uid in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
