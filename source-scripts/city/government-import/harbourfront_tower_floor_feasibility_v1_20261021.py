"""Private terrain floor feasibility beneath exact original Harbourfront projection.
The floor is a derived terrain proposal, not a claimed government source surface.
No building geometry, placement or validation thresholds change.
"""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_merchants_finite_inset_v4_20261021 import inset_faces,lift
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-tower-floor-feasibility-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(n,p):
 _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
sn='government-xl-next-twenty-current-terrain-v6-20261021';selection=take(sn,BASE/sn/'selection.json.gz')['rows'];final=module('harbourfront_floor_foundation',HERE/'xl-final-script-pass.py');results=[]
for uid in ['landsd/118230:0']:
 row=next(r for r in selection if r['uid']==uid);p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());floor=float(tri[:,:,1].min());projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));core=projection.buffer(2,join_style=2);patch=np.asarray(lift(core,np.array([0.,0.,floor])))
 gn='government-xl-harbourfront-tower-original-ground-v1-20261021';ground=np.asarray(take(gn,HERE/'local'/gn/(uid.split('/')[1]+'-ground.json.gz'))['completeAdjoiningTerrain'])
 print(dict(uid=uid,terrainFaces=len(ground),floorDatum=floor,footprintPlaneFaces=len(patch)),flush=True)
 out,proof=inset_faces(ground,patch)
 flat=out.reshape(-1,3);dist=shapely.distance(shapely.points(flat[:,[0,2]]),core);weight=np.clip(1-dist/8,0,1);before=flat[:,1].copy();flat[:,1]=np.minimum(before,before+weight*(floor-before));assert np.all(flat[:,1]<=before+1e-12)
 proof.update(coreWKT=core.wkt,transitionWidthM=8,sourceProjectionWKT=projection.wkt,maximumTransitionLoweringM=float((before-flat[:,1]).max()))
 proof['policy']='Derived private horizontal terrain floor at exact original minimum Y, two metre collar around full original projection with eight metre linear return to original terrain; not original source terrain or original architectural surfaces. No acceptance.'
 save(LOCAL/(uid.split('/')[1]+'-terrain.json.gz'),dict(triangles=out.tolist(),notPublishable=True));save(DOC/(uid.split('/')[1]+'-construction.json.gz'),proof)
 b=row['source']['building'];f=final.foundation_context(tri,out,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(uid.split('/')[1]+'-foundation.json'),f)
 r=dict(uid=uid,sourceSHA256=row['sourceSHA256'],floorDatum=floor,terrainFaces=len(out),changedTerrainFaces=len(proof['changedTerrainFaceIndices']),changedProjectedAreaM2=proof['removedProjectedAreaM2'],foundation={k:v for k,v in f.items()if k!='components'},installationApproved=False);results.append(r);print(r,flush=True)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend(HERE/n for n in ['china_merchants_finite_inset_v4_20261021.py','native_patch_resolution.py','exact_packed_world_geometry_20261009.py','xl-final-script-pass.py'])
result=dict(uids=[r['uid']for r in results],rows=results,sourceGeometryChanges=0,installationApproved=False,qualification='Private derived terrain feasibility only, including a two metre core collar and eight metre transition. Original source geometry and pose are immutable. Boundary continuity, physical support, complete current neighbour regression, runtime and visual acceptance are still required.')
save(DOC/'summary.json',result);r=module('harbourfront_floor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-harbourfront-projection-floor-feasibility',refs,result);print(r['jobId'],flush=True)
