"""Restore exact government tower originals from immutable source bundles, no geometry edits."""
import os,sys,uuid,tarfile,json,subprocess
from pathlib import Path
from collections import defaultdict
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-park-avenue-lookup-v1-20261018';BATCH='government-xl-olympian-two-park-avenue-restored-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);r=read(PRIOR/'result.json');pins={};groups=defaultdict(list);artifacts={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  for row in read(PRIOR/'matches.json')['matches']:
   resultsha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['cacheKey'],)).fetchone();assert resultsha==row['resultSHA256'];assert row['model']in result['models'];groups[row['cacheKey']].append(row);artifacts[row['cacheKey']]=result['artifacts'][0]
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 recovery=module('olympian_direct_government_recovery',HERE/'xl-second-pass.py');recovery.LOCAL=LOCAL
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 old_sheets={x['sheet']:x for x in read(BASE/'government-xl-olympian-two-source-local-terrain-20261008/source-recovery.json')['sheets']};restored=[];refs=[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins],HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py'];sourceproof=[]
 for key,members in groups.items():
  sheet=members[0]['sheet'];old=ROOT/old_sheets[sheet]['cache'];directory=read(old/'directory/result.json');receipt=old/'original/download.json';retained=[(receipt,read(receipt))];rows=[dict(uid=x['matchedUids'][0],modelId=x['model']['modelId'],sourceSHA256=x['model']['asset']['sha256'],native=dict(model=x['model'],cacheKey=key,sheet=sheet))for x in members]
  result=recovery.source_sheet(sheet,rows,directory,{},retained);sourceproof.append(result);refs.extend([old/'directory/result.json',receipt,HERE.parent/'citywide-native/download.py',HERE.parent/'citywide-native/convert.py',HERE.parent/'enhancement-screening/shape_prepare.py'])
  for row in members:
   m=row['model'];sha=m['asset']['sha256'];dest=LOCAL/'assets'/(sha+'.glb.gz');raw=dest.read_bytes();assert digest(raw)==sha and len(raw)==m['asset']['bytes'];t=decode_original_world_triangles(raw);assert len(t)==m['triangles'];assert len(row['matchedUids'])==1;uid=row['matchedUids'][0];assert not m.get('candidate') or m['candidate']['uid']==uid;refs.append(dest);restored.append(dict(uid=uid,modelId=m['modelId'],sheet=sheet,cacheKey=key,sourceSHA256=sha,assetPath=str(dest.relative_to(ROOT)),triangles=len(t),worldBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],matching=m['matching'],candidate=m.get('candidate'),identityApproved=False));print(dict(uid=uid,triangles=len(t)),flush=True)
  assert reservations.owns(lease)
 save(DOC/'source-recovery.json',dict(sheets=sourceproof,sourceGeometryChanges=0));refs.extend(p for p in (LOCAL/'sheets').rglob('*')if p.is_file())
 assert len(restored)==8;save(DOC/'restored.json',dict(rows=restored,originalGeometryChanges=0,fullAcceptance=False));out=module('olympian_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-eight-adjoining-original-source-recovery-v1',refs,dict(uids=[x['uid']for x in restored],restoredOriginals=8,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();rows=read(PRIOR/'matches.json')['matches'];uids={u for r in rows for u in r['matchedUids']};assert len(uids)==8;c=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in sorted(uids)],batch=BATCH,ttl=3600);assert c['ok'],c;lease=c['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
