"""Private joint terrain proposal preserving both original-building ground surfaces.
No building edits, installation approval, optimisation job, or publication.
"""
from pathlib import Path
import json,subprocess,sys,uuid
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import plane,lift
from native_patch_resolution import _faces
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-grandiose-joint-surface-v3-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SOURCES=['government-xl-tko-podium-private-terrain-v1-20261021','government-xl-grandiose-private-terrain-v9-20261021']
UIDS=['landsd/265489:0','landsd/246824:0']
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
 refs=[Path(__file__)]; hashes={}
 def take(folder,path):
  receipt,pins=authenticate(folder); key=str(path.relative_to(ROOT)); assert digest(path.read_bytes())==pins[key]
  refs.extend([folder/'result.json',path]);hashes[key]=pins[key];return read(path)
 surfaces=[];domains=[];descriptors=[]
 for name in SOURCES:
  folder=BASE/name; descriptor=take(folder,folder/'terrain-candidates.json')[0]
  patch=take(folder,ROOT/descriptor['path']); surfaces.append(_faces(patch));domains.append(shapely.box(*descriptor['bounds']));descriptors.append(descriptor)
 cap=BASE/'government-xl-tko-grandiose-joint-capture-v1-20261021';rows=take(cap,cap/'selection.json.gz')['rows'];projections=[];models=[]
 for uid in UIDS:
  row=next(r for r in rows if r['uid']==uid);path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];hashes[str(path.relative_to(ROOT))]=row['sourceSHA256'];refs.append(path)
  model=decode_original_world_triangles(path.read_bytes());models.append(model);projections.append(shapely.union_all(shapely.polygons(model[:,:,[0,2]])))
 assert projections[0].disjoint(projections[1]),'building-projections-overlap'
 # Keep numerical clipping boundaries clear of original building facets.
 protected=[g.buffer(.05,join_style='mitre') for g in projections]
 assert protected[0].disjoint(protected[1])
 scope=BASE/'government-xl-grandiose-regional-ground-v8-20261021'
 transition=shapely.from_wkt(take(scope,scope/'protected.json')['outerWKT']).union(protected[1])
 assert domains[1].covers(transition)
 shared=transition.intersection(domains[0])
 save(DOC/'transition.json',dict(sharedWKT=shared.wkt,protectedWKT=[g.wkt for g in protected],guardBufferM=.05))
 polys=[shapely.polygons(s[:,:,[0,2]]) for s in surfaces]; tree=shapely.STRtree(polys[1]);output=[];lineage=[]
 def add(faces,record):
  for face in faces: output.append(face);lineage.append(record)
 for side in [0,1]:
  for i,face in enumerate(surfaces[side]):
   p=polys[side][i]
   if p.area<=1e-10:
    # Preserve degenerate source surface facets without using them as height planes.
    add([face],dict(kind='retained-degenerate',side=side,face=i));continue
   part=p.difference(shared) if side==0 else p.difference(domains[0])
   if part.area>1e-10:add([face] if part.equals(p) else lift(part,plane(face)),dict(kind='outside-shared-domain',side=side,face=i))
   # Preserve the chosen source tessellation beneath each building. The other
   # source surface contributes nothing here, so do not intersect its triangles.
   keep=p.intersection(shared).intersection(protected[side])
   if keep.area>1e-10:add([face] if keep.equals(p) else lift(keep,plane(face)),dict(kind='protected-building-plane',side=side,face=i))
 for i,face in enumerate(surfaces[0]):
  if i%1000==0:
   assert reservations.owns(lease);print(json.dumps(dict(tkoFace=i,total=len(surfaces[0]),outputFaces=len(output))),flush=True)
  if polys[0][i].area<=1e-10:continue
  ac=plane(face)
  for j in tree.query(polys[0][i],predicate='intersects'):
   region=polys[0][i].intersection(polys[1][j]).intersection(shared)
   if region.area<=1e-10:continue
   bc=plane(surfaces[1][j]); remaining=region.difference(protected[0]).difference(protected[1])
   for f in lift(remaining,ac):
    for v in f:
     point=shapely.Point(v[[0,2]]); da=point.distance(protected[0]);db=point.distance(protected[1]);assert da+db>0
     edge=point.distance(transition.boundary)
     # Fade to the retained TKO surface at the exact Grandiose transition edge.
     grandioseWeight=(da/(da+db))*(edge/(edge+db) if edge+db else 1)
     weight=1-grandioseWeight;xz=v[[0,2]];v[1]=weight*(xz@ac[:2]+ac[2])+(1-weight)*(xz@bc[:2]+bc[2])
    add([f],dict(kind='between-building-transition',tkoFace=i,grandioseFace=int(j)))
 result_faces=np.asarray(output);assert np.isfinite(result_faces).all()
 path=LOCAL/'joint-terrain-faces.json.gz';save(path,dict(triangles=result_faces.tolist(),notPublishable=True));refs.append(path)
 save(DOC/'lineage.json.gz',dict(rows=lineage));save(DOC/'source-candidates.json',descriptors)
 final=module('joint_surface_foundation',HERE/'xl-final-script-pass.py');foundation=[]
 for uid,model,proj in zip(UIDS,models,projections):
  row=next(r for r in rows if r['uid']==uid);b=row['source']['building'];context=final.foundation_context(model,result_faces,shapely.Polygon(b['rings'][0],b['rings'][1:]))
  save(DOC/(uid.split('/')[1]+'-foundation.json'),context);foundation.append(dict(uid=uid,**{k:v for k,v in context.items() if k!='components'}))
 summary=dict(uids=UIDS,faces=len(output),bounds=list(shapely.union_all(domains).bounds),buildingSeparationM=projections[0].distance(projections[1]),foundations=foundation,sourceGeometryChanges=0,installationApproved=False,productionChanges=0,qualification='Private joint terrain proposal only; full coverage, seams, runtime rounding, budgets, neighbour and browser checks remain required.')
 save(DOC/'summary.json',summary)
 for p,h in hashes.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease);refs.extend([HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py'])
 receipt=module('joint_surface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-joint-original-installation-terrain',list(dict.fromkeys(refs)),summary)
 print(json.dumps(dict(jobId=receipt['jobId'],**summary)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
