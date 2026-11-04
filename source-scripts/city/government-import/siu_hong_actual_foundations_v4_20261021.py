"""Complete original assembly foundation/support diagnostics; no publication."""
from pathlib import Path
import json, subprocess, sys, uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-siu-hong-actual-foundations-v4-20261021'
DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-siu-hong-private-capture-v2-20261021'
RUNTIME=BASE/'government-xl-siu-hong-private-runtime-v4-20261021'
def owned():
 lease=read(LOCAL/'reservation.json'); assert reservations.owns(lease) and not DOC.exists()
 refs=[Path(__file__)]; pins={}
 for folder in [CAP,RUNTIME]:
  receipt=read(folder/'result.json'); refs.append(folder/'result.json')
  with connect() as db:
   db.execute('SET TRANSACTION READ ONLY')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for e in receipt['evidenceRefs']:
   if e['path'] in pins: assert pins[e['path']]==e['sha256']
   pins[e['path']]=e['sha256']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))],p
  refs.append(p); return read(p)
 rows=take(CAP/'selection.json.gz')['rows']; cap=take(CAP/'attributes.json.gz')
 assert cap['startEndAllInputsVerified'] and not cap['rejected'] and len(rows)==len(cap['rows'])==2
 for p,h in cap['inputHashes'].items():
  assert digest((ROOT/p).read_bytes())==h,p
  refs.append(ROOT/p)
 runtime=take(HERE/'local'/RUNTIME.name/'runtime-geometry.json.gz');assert {r['uid']for r in runtime['rows']}=={'landsd/190963:0','landsd/233417:0'}
 ground=np.unique(np.concatenate([np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3)for r in runtime['rows']]),axis=0)
 worlds={m:{} for m in ['original','literal','leftF32','balancedF32']}; captured={r['uid']:r for r in cap['rows']}
 for row in rows:
  uid=row['uid']; asset=ROOT/row['candidate']['path']; raw=asset.read_bytes()
  assert digest(raw)==row['sourceSHA256']; refs.append(asset)
  worlds['original'][uid]=decode_original_world_triangles(raw); c=captured[uid]
  for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
   worlds[mode][uid]=np.asarray(c[field]).reshape(-1,3)[np.asarray(c['completeOriginalIndex']).reshape(-1,3)]
   assert len(worlds[mode][uid])==len(worlds['original'][uid])
 final=module('yoho_assembly_foundation',HERE/'xl-final-script-pass.py'); tool=HERE/'wave_retained_basic_support_v1_20261017.mjs'; summary=[]
 for mode,world in worlds.items():
  mall=world['landsd/233417:0']
  for row in rows:
   assert reservations.owns(lease); uid=row['uid']; tri=world[uid]; b=row['source']['building']
   support=ground if uid=='landsd/233417:0' else np.concatenate([ground,mall])
   folder=DOC/mode/uid.split('/')[1]
   foundation=final.foundation_context(tri,support,Polygon(b['rings'][0],b['rings'][1:]))
   save(folder/'foundation.json',foundation)
   # Towers use the original podium for their strict support interface.
   save(folder/'input.json.gz',dict(podium=(ground if uid=='landsd/233417:0' else mall).tolist(),rows=[dict(uid=uid,position=tri.reshape(-1).tolist(),index=list(range(len(tri)*3)))]))
   subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True)
   report=read(folder/'support.json.gz'); proof=report['rows'][0]['proof']
   for p,h in report['inputHashes'].items():
    assert digest((ROOT/p).read_bytes())==h; refs.append(ROOT/p)
   item=dict(uid=uid,mode=mode,foundation={k:v for k,v in foundation.items() if k!='components'},strictContacts=proof['strictContacts'],samples=proof['samples'],unresolved=len(proof['unresolved']),strictSupportPassed=proof['passed'])
   summary.append(item); print(json.dumps(item),flush=True)
 for p in set(refs):
  key=str(p.relative_to(ROOT))
  if key in pins: assert digest(p.read_bytes())==pins[key]
 for p,h in cap['inputHashes'].items(): assert digest((ROOT/p).read_bytes())==h
 refs.extend([tool,HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 result=json.loads(json.dumps(dict(uids=[r['uid'] for r in rows],rows=summary,installationApproved=False,sourceGeometryChanges=0,qualification='Four renderer arithmetic modes against complete actual drawn private V4 terrain under conditional private two-form footprint scope; no publication approved.')))
 save(DOC/'summary.json',result)
 module('yoho_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-four-mode-assembly-foundation-and-support',list(dict.fromkeys(refs)),result)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600); assert claim['ok']
 lease=claim['reservation']; p=LOCAL/'reservation.json'; save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
