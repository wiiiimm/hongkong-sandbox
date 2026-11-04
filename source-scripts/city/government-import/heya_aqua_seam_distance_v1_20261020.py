"""Bound nearest original podium surfaces at all unresolved witnesses; no waiver."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-heya-aqua-seam-distance-v1-20261020'
DOC=BASE/BATCH
SUP=BASE/'government-xl-heya-aqua-current-support-v3-20261020'
REN=BASE/'government-xl-heya-aqua-render-foundations-v1-20261020'
def main():
 assert not DOC.exists()
 refs=[Path(__file__),HERE/'pool_incident_wall_contacts_v1_20261017.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SUP,REN]:
   r=read(folder/'result.json')
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256']
    pins[e['path']]=e['sha256']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
  refs.append(p)
  return read(p)
 sources=take(SUP/'support-inputs.json')['sources']
 contacts=take(SUP/'finite-contacts.json.gz')['targets']
 cap=take(REN/'attributes.json.gz')['rows']
 original={}
 for r in sources:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p)
  original[r['uid']]=decode_original_world_triangles(p.read_bytes())
 modes={'original':original}
 for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  modes[mode]={r['uid']:np.asarray(r[field]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in cap}
 out=[]
 for mode,tri in modes.items():
  podium=tri['landsd/184285:0'];lo=podium.min(1);hi=podium.max(1)
  for row in contacts:
   point=np.asarray(row['witness']['position'])
   # AABB lower bounds permit exact pruning only after a real triangle establishes an upper bound.
   lower=np.linalg.norm(np.maximum(np.maximum(lo-point,point-hi),0),axis=1)
   best=float('inf');hit=None
   for i in np.argsort(lower):
    if lower[i]>best:break
    q=closest(point,podium[i]);dist=float(np.linalg.norm(q-point))
    if dist<best:best=dist;hit=(int(i),q)
   i,q=hit
   out.append(dict(mode=mode,originalWitness=row['witness'],incidentSourceFaces=row['incidentFaces'],positiveOriginalContactCount=len(row['positiveContacts']),podiumFace=i,podiumTriangle=podium[i].tolist(),nearestPoint=q.tolist(),distanceM=best,horizontalDistanceM=float(np.linalg.norm((q-point)[[0,2]])),verticalDeltaM=float(q[1]-point[1])))
 result=dict(uids=['landsd/184287:0','landsd/184285:0'],rows=out,diagnosticOnly=True,installationApproved=False,sourceGeometryChanges=0,qualification='Distances from unchanged original witness positions to complete podium surfaces in four representations; no support tolerance or acceptance change.')
 save(DOC/'distances.json',result)
 for p in list(dict.fromkeys(refs)):
  key=str(p.relative_to(ROOT))
  if key in pins:assert digest(p.read_bytes())==pins[key]
 module('heya_seam_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-podium-nearest-surface-seam-diagnostic',list(dict.fromkeys(refs)),result)
 print([(r['mode'],r['distanceM']) for r in out if not r['positiveOriginalContactCount']],flush=True)
if __name__=='__main__':main()
