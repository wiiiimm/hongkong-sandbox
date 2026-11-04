"""Complete original and three actual render coordinate foundation/support checks."""
from pathlib import Path
import json,subprocess,sys,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-render-foundations-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SOURCE=BASE/'government-xl-yoho-mall-i-private-runtime-v3-20261020'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();receipt=read(SOURCE/'result.json');refs=[Path(__file__),SOURCE/'result.json']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};consumed={}
 def take(p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k],p;consumed[k]=pins[k];refs.append(p);return read(p)
 row=take(SOURCE/'selection.json.gz')['rows'][0];runtime=take(HERE/'local'/SOURCE.name/'runtime-geometry.json.gz')['rows'][0];assert row['uid']==runtime['uid']=='landsd/189427:0'
 ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3);mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(mp)
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 cats=[ref(ROOT/'3d-viewer'/u)for u in manifest['officialModelCatalogues']]
 tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==row['uid'])==row['source']['building'];refs.append(tile)
 save(DOC/'input.json.gz',dict(rows=[dict(uid=row['uid'],entry=row['candidate']['entry'],building=row['source']['building'],path=row['candidate']['path'])],currentManifest=ref(mp),currentCatalogueRefs=cats,evidenceRefs=[ref(p)for p in refs]))
 tool=HERE/'yoho_mall_i_actual_attributes_v1_20261020.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 cap=read(DOC/'attributes.json.gz');assert cap['startEndAllInputsVerified'] and not cap['rejected']and len(cap['rows'])==1;captured=cap['rows'][0]
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];worlds={'original':decode_original_world_triangles(raw)}
 for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(captured[field]).reshape(-1,3)[np.asarray(captured['completeOriginalIndex']).reshape(-1,3)]
 final=module('yoho_mall_foundation',HERE/'xl-final-script-pass.py');b=row['source']['building'];summary=[];supporttool=HERE/'wave_retained_basic_support_v1_20261017.mjs'
 for mode,tri in worlds.items():
  assert len(tri)==21928 and reservations.owns(lease);foundation=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));folder=DOC/mode
  save(folder/'foundation.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],foundation=foundation))
  save(folder/'input.json.gz',dict(rows=[dict(uid=row['uid'],position=tri.reshape(-1).tolist(),index=list(range(len(tri)*3)))],podium=ground.tolist()))
  subprocess.run(['node',str(supporttool),str(folder.relative_to(ROOT))],cwd=ROOT,check=True);support=read(folder/'support.json.gz');proof=support['rows'][0]['proof']
  for p,h in support['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  item=dict(mode=mode,foundation={k:v for k,v in foundation.items()if k!='components'},strictSupportPassed=proof['passed'],samples=proof['samples'],strictContacts=proof['strictContacts'],wallIntersections=proof['wallIntersections'],unresolved=len(proof['unresolved']));summary.append(item);print(item,flush=True)
 for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in consumed.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=[row['uid']],rows=summary,installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',result);refs.extend([tool,supporttool,HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('yoho_render_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-four-world-foundation-and-strict-support',list(dict.fromkeys(refs)),result)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
