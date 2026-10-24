"""Strict unchanged government assembly support, diagnostic only."""
from pathlib import Path
import json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-original-assembly-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-yoho-mall-i-tower-recovery-v1-20261020'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();receipt=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};p=CAP/'recovery.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);rows=read(p)['rows'];world={}
 for row in rows:
  p=ROOT/row['assetPath'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p);world[row['uid']]=decode_original_world_triangles(p.read_bytes())
 runtimeFolder=BASE/'government-xl-yoho-mall-i-private-runtime-v3-20261020';rr=read(runtimeFolder/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(rr['jobId'],)).fetchone()==('complete',rr)
 rpins={e['path']:e['sha256']for e in rr['evidenceRefs']};refs.append(runtimeFolder/'result.json')
 def take(p):
  assert digest(p.read_bytes())==rpins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 mall=take(runtimeFolder/'selection.json.gz')['rows'][0];asset=ROOT/mall['candidate']['path'];assert digest(asset.read_bytes())==mall['sourceSHA256'];refs.append(asset);world[mall['uid']]=decode_original_world_triangles(asset.read_bytes())
 runtime=take(HERE/'local'/runtimeFolder.name/'runtime-geometry.json.gz')['rows'][0];ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath);forms={}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for building in read(p)['buildings']:
   if building['uid']in world:forms[building['uid']]=building;refs.append(p)
 assert set(forms)==set(world)
 summary=[];tool=HERE/'wave_retained_basic_support_v1_20261017.mjs' 
 for parent,children in [('landsd/189427:0',[u for u in world if u!='landsd/189427:0'])]:
  assert reservations.owns(lease);folder=DOC/parent.split('/')[1]
  save(folder/'input.json.gz',dict(podium=world[parent].tolist(),rows=[dict(uid=u,position=world[u].reshape(-1).tolist(),index=list(range(world[u].size//3))) for u in children]))
  subprocess.run(['node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True);report=read(folder/'support.json.gz')
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  for r in report['rows']:
   proof=r['proof'];summary.append(dict(uid=r['uid'],supportUid=parent,samples=proof['samples'],strictContacts=proof['strictContacts'],wallIntersections=proof['wallIntersections'],unresolved=len(proof['unresolved']),passed=proof['passed']))
 from shapely.geometry import Polygon
 final=module('yoho_original_foundations',HERE/'xl-final-script-pass.py');foundations=[]
 for u,tri in world.items():
  if u=='landsd/189427:0':continue
  b=forms[u];f=final.foundation_context(tri,np.concatenate([ground,world['landsd/189427:0']]),Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(u.split('/')[1]+'-foundation.json'),f)
  foundations.append(dict(uid=u,worldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],foundation={k:v for k,v in f.items()if k!='components'}))
 save(DOC/'foundations.json',dict(rows=foundations,installationApproved=False));refs.append(HERE/'xl-final-script-pass.py')
 save(DOC/'summary.json' ,dict(rows=summary,installationApproved=False,sourceGeometryChanges=0,qualification='Source-coordinate support only. Does not approve identity, complete foundations, runtime, or publication.'))
 refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('ascot_original_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-assembly-strict-support',list(dict.fromkeys(refs)),dict(uids=list(world),rows=summary,foundations=foundations,installationApproved=False));print(summary,flush=True)

def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
