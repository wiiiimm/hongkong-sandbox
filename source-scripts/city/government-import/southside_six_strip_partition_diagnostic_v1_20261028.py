"""Private spatial partition of unchanged runtime terrain; explicit conservation/drift evidence."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-six-strip-partition-diagnostic-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PRIOR='government-xl-southside-unchanged-highest-surface-proof-v1-20261028';SCOPE='government-xl-southside-private-terrain-overlap-v1-20261028';UID='landsd/315025:0'
def clip(points,x,keep_greater):
 out=[]
 for a,b in zip(points,points[1:]+points[:1]):
  ia=a[0]>=x if keep_greater else a[0]<=x;ib=b[0]>=x if keep_greater else b[0]<=x
  if ia:out.append(a.copy())
  if ia!=ib:
   q=a+(b-a)*((x-a[0])/(b[0]-a[0]));q[0]=x;out.append(q)
 return out

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={}
 for name in [PRIOR,SCOPE]:
  _,bound=authenticate(BASE/name);pins.update(bound);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 contract=take(BASE/PRIOR/'summary.json');assert contract['existingNativeHeightContractPassed']and not contract['runtimeNodeBudgetPassed'];patch=take(BASE/PRIOR/'height-contract-only-terrain.json.gz');scope=take(BASE/SCOPE/'scope.json');mesh=patch['nativeMesh'];tri=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)];assert len(tri)==76293;bounds=scope['bounds'];cells=scope['cells'];assert cells[2]-cells[0]==6;cuts=np.linspace(bounds[0],bounds[2],7);parent_area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;represented=np.zeros(len(tri),int);area=np.zeros(len(tri));strips=[];max_displacement=0;max_ray_error=0;collapsed_area=0;bad_ray_faces=[]
 for j in range(6):
  low,high=float(cuts[j]),float(cuts[j+1]);parts=[];parent_ids=[]
  candidates=np.flatnonzero((tri[:,:,0].max(1)>=low)&(tri[:,:,0].min(1)<=high))
  for raw in candidates:
   i=int(raw);face=tri[i]
   if face[:,0].min()==face[:,0].max() and j<5 and face[0,0]==high:continue
   points=clip(list(face),low,True)
   if points:points=clip(points,high,False)
   if not points:continue
   while len(points)<3:points.append(points[-1].copy())
   for k in range(1,len(points)-1):
    part=np.asarray([points[0],points[k],points[k+1]]);a=float(np.linalg.norm(np.cross(part[1]-part[0],part[2]-part[0]))/2)
    if a==0 and parent_area[i]>0:continue
    represented[i]+=1;area[i]+=a;parts.append(part);parent_ids.append(i)
  assert parts;values=np.asarray(parts);runtime=values.astype('<f4').astype('<f8');max_displacement=max(max_displacement,float(abs(runtime-values).max()));parent_ids=np.asarray(parent_ids,int)
  normals=np.cross(tri[parent_ids,1]-tri[parent_ids,0],tri[parent_ids,2]-tri[parent_ids,0]);projected=np.cross(runtime[:,1]-runtime[:,0],runtime[:,2]-runtime[:,0])[:,1];valid=normals[:,1]!=0
  for local_id in np.flatnonzero(valid):
   original=tri[parent_ids[local_id]];normal=normals[local_id];p=runtime[local_id];height=original[0,1]-((p[:,0]-original[0,0])*normal[0]+(p[:,2]-original[0,2])*normal[2])/normal[1];error=float(abs(height-p[:,1]).max());max_ray_error=max(max_ray_error,error)
   if error>=.01:bad_ray_faces.append(dict(strip=j,parentFace=int(parent_ids[local_id]),pieceFace=int(local_id),heightEquationErrorM=error))
   if projected[local_id]==0:collapsed_area+=abs(float(normal[1]))/2
  p=LOCAL/('strip-'+str(j)+'.json.gz');save(p,dict(position=values.reshape(-1).tolist(),index=list(range(len(values)*3)),parentFaceIndices=parent_ids.tolist(),bounds=[low,bounds[1],high,bounds[3]],coarseCells=[cells[0]+j,cells[1],cells[0]+j+1,cells[3]]));refs.append(p);strips.append(dict(strip=j,faces=len(values),runtimeBudgetPassed=len(values)<=25000,asset=dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))))
 missing=np.flatnonzero(represented==0);relative=np.abs(area-parent_area)/np.maximum(parent_area,1);result=dict(uids=[UID],parentRuntimeFaces=len(tri),strips=strips,allNodeBudgetsPassed=all(r['runtimeBudgetPassed']for r in strips),missingParentFaces=missing.tolist(),maximumParentAreaConservationErrorM2=float(abs(area-parent_area).max()),maximumRelativeAreaError=float(relative.max()),maximumRuntimeVertexDisplacementM=max_displacement,maximumSourcePlaneHeightDriftM=max_ray_error,heightDriftViolations=bad_ray_faces,collapsedSourceProjectedAreaUpperBoundM2=collapsed_area,sourceBuildingGeometryChanges=0,terrainHeightEditing=False,terrainValidatorPassed=False,physicalAccepted=False,identityAccepted=False,installationApproved=False,qualification='Private partition diagnostic only. Complete Float32 parent facets clipped linearly at exact coarse-cell strip boundaries; every piece retains parent-face provenance. Explicit missing faces, 3D-area errors, Float32 displacement and source-plane ray drift. No highest-surface approval transfer to pieces, shared-boundary proof, coverage/current-map/browser or installation acceptance.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('southside_six_strip_partition_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-runtime-terrain-partition-conservation-and-drift-diagnostic',refs,result);print({k:result[k]for k in ['allNodeBudgetsPassed','missingParentFaces','maximumParentAreaConservationErrorM2','maximumSourcePlaneHeightDriftM']},flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-six-strip-private-partition-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
