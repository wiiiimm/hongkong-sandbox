"""Whole original sources against current ground/support in four render representations."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-thei-four-mode-foundations-v1-20261021';DOC=BASE/BATCH;CAP=BASE/'government-xl-thei-candidate-runtime-v3-20261021';ATTR=BASE/'government-xl-thei-actual-render-attributes-v1-20261021'
PAIRS={'landsd/259613:0':None,'landsd/259803:0':None}
def owned():
 assert reservations.owns(read(LOCAL/'reservation.json'))
 assert not DOC.exists();pins={};refs=[Path(__file__)];worlds={'original':{}}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,ATTR]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(CAP/'selection.json.gz')['rows'];capture=read(ATTR/'attributes.json.gz');assert capture['startEndAllInputsVerified']
 for r in rows:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];worlds['original'][r['uid']]=decode_original_world_triangles(raw)
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in capture['rows']}
 runtime={r['uid']:r for r in read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows']};final=module('star_park_foundation_four',HERE/'xl-final-script-pass.py');out=[]
 for mode,world in worlds.items():
  for r in rows:
   uid=r['uid']
   if uid not in PAIRS:continue
   tri=world[uid];assert len(tri)==r['triangles'];support=np.asarray(runtime[uid]['drawnGroundGeometry']).reshape(-1,3,3)
   if PAIRS[uid]:support=np.concatenate([support,world[PAIRS[uid]]])
   b=r['source']['building'];f=final.foundation_context(tri,support,Polygon(b['rings'][0],b['rings'][1:]))
   audit=module('thei_four_contact',HERE/'resolve-pass-indexed-parent-clipping.py');points,bottom=audit.sample_points(dict(position=tri.reshape(-1).tolist(),index=list(range(tri.size//3))));contact=audit.audit_native(points,bottom,support)
   passed=contact['passed'] and f['completeTerrainTriangles']==len(tri) and f['fullyBuriedAreaFraction']==0 and f['fullyBuriedUpwardTriangles']==0
   save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),dict(uid=uid,sourceSHA256=r['sourceSHA256'],mode=mode,worldSHA256=digest(np.asarray(tri,dtype='<f8').tobytes()),foundation=f,contact=contact,strictFoundationAccepted=passed,installationApproved=False))
   s=dict(uid=uid,mode=mode,passed=passed,buried=f['fullyBuriedTriangles'],complete=f['completeTerrainTriangles'],contact=contact);out.append(s);print(s,flush=True)
 save(DOC/'summary.json',dict(rows=out,installationApproved=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('star_park_four_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-four-world-foundations',list(dict.fromkeys(refs)),dict(uids=list(PAIRS),rows=out,installationApproved=False,modelGeometryChanges=0))


import subprocess
import sys, uuid, json
from run import reservations
LOCAL=HERE/'local'/BATCH
UID='landsd/33396:0'
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/259613:0','building:landsd/259803:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

