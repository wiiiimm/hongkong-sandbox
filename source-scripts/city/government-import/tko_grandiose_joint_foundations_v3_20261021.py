"""Complete original assembly foundation/support diagnostics; no publication."""
from pathlib import Path
import json, subprocess, sys, uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tko-grandiose-joint-foundations-v3-20261021'
DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-tko-grandiose-joint-capture-v1-20261021'
RUNTIME=BASE/'government-xl-tko-grandiose-joint-runtime-v2-20261021'
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
 assert cap['startEndAllInputsVerified'] and not cap['rejected'] and len(rows)==len(cap['rows'])==11
 for p,h in cap['inputHashes'].items():
  assert digest((ROOT/p).read_bytes())==h,p
  refs.append(ROOT/p)
 runtime_rows={r['uid']:r for r in take(HERE/'local'/RUNTIME.name/'runtime-geometry.json.gz')['rows']};assert set(runtime_rows)=={r['uid']for r in rows}
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
  mall=world['landsd/265489:0']
  for row in rows:
   assert reservations.owns(lease); uid=row['uid']; tri=world[uid]; b=row['source']['building']
   actual=runtime_rows[uid];assert actual['sourceSHA256']==row['sourceSHA256']
   ground=np.asarray(actual['drawnGroundGeometry']).reshape(-1,3,3)
   terrain_founded=uid in {'landsd/265489:0','landsd/246824:0'}
   support_source=ground if terrain_founded else world['landsd/246824:0' if uid=='landsd/81731:0' else 'landsd/265489:0']
   support=ground if terrain_founded else np.concatenate([ground,support_source])
   folder=DOC/mode/uid.split('/')[1]
   foundation=final.foundation_context(tri,support,Polygon(b['rings'][0],b['rings'][1:]))
   save(folder/'foundation.json',foundation)
   # Towers use the original podium for their strict support interface.
   save(folder/'input.json.gz',dict(podium=support_source.tolist(),rows=[dict(uid=uid,position=tri.reshape(-1).tolist(),index=list(range(len(tri)*3)))]))
   subprocess.run(['node',str(tool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True)
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
 result=json.loads(json.dumps(dict(uids=[r['uid'] for r in rows],rows=summary,installationApproved=False,sourceGeometryChanges=0)))
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
