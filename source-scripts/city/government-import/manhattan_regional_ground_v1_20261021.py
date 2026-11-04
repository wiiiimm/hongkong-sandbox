"""Full-source foundation diagnostic preserving the installed terrain domain."""
from pathlib import Path
import json, subprocess, sys, uuid
import numpy as np, shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from native_patch_resolution import _faces,grid_surface_faces
from source_surface_inset import plane,lift
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-regional-ground-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SCOPE=BASE/'government-xl-manhattan-regional-scope-v2-20261021';GROUND=BASE/'government-xl-three-clear-original-ground-v1-20261021';SELECTION=BASE/'government-xl-next-twenty-current-terrain-v6-20261021'
CORE=BASE/'government-xl-manhattan-terrain-boundary-transition-v1-20261021'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
 refs=[Path(__file__)];pins={};consumed={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SCOPE,GROUND,SELECTION,CORE]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))],p
  consumed[str(p.relative_to(ROOT))]=pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 scope=take(SCOPE,SCOPE/'scope.json');take(SCOPE,ROOT/'3d-viewer/city/data/manifest.json')
 row=next(r for r in take(SELECTION,SELECTION/'selection.json.gz')['rows']if r['uid']=='landsd/276331:0')
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 model=decode_original_world_triangles(asset.read_bytes());assert len(model)==17758
 groundfile=HERE/'local'/GROUND.name/'276331:0-ground.json.gz';ground=np.asarray(take(GROUND,groundfile)['completeAdjoiningTerrain'],dtype='float64')

 records=scope['retainedPatches']
 domains=[shapely.box(*r['extent']) for r in records]
 for i,d in enumerate(domains):
  for other in domains[:i]:assert d.intersection(other).area<=1e-8
 old=np.concatenate([_faces(take(SCOPE,ROOT/'3d-viewer'/r['url'])) for r in records]) if records else np.empty((0,3,3));domain=shapely.union_all(domains)
 # Retain the full current terrain away from the source-shaped transition.
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(SCOPE,parentpath)
 builder=module('yoho_shaped_baseline',HERE/'resolve-pass-indexed-parent-clipping.py')
 sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
 rectangle=shapely.box(*scope['regionalParentExtent'])
 baseline=list(old)
 for face in grid_surface_faces(sampler,rectangle):
  face=np.asarray(face,dtype='float64');p=Polygon(face[:,[0,2]])
  baseline.extend(lift(p.difference(domain),plane(face)))
 baseline=np.asarray(baseline)
 projection=shapely.union_all(shapely.polygons(model[:,:,[0,2]]))
 polygons=shapely.polygons(ground[:,:,[0,2]])
 privateFaces=np.asarray(take(CORE,HERE/'local'/CORE.name/'private-terrain.json.gz')['triangles'])
 # Bound replacement by the actual complete source projection, not whole
 # government TIN triangles that happen to intersect its bounding rectangle.
 sourceDomain=projection.convex_hull.buffer(2,join_style='mitre');clipped=[]
 for face in privateFaces:
  polygon=Polygon(face[:,[0,2]])
  if polygon.area<=1e-10:
   if polygon.intersects(sourceDomain):clipped.append(face)
  else:clipped.extend(lift(polygon.intersection(sourceDomain),plane(face)))
 coreFaces=np.asarray(clipped);core=shapely.union_all(shapely.polygons(coreFaces[:,:,[0,2]]));outer=core.buffer(8,join_style='mitre');ring=outer.difference(core)
 assert rectangle.covers(outer),'source-transition-crosses-regional-boundary'
 # Bind and protect the complete actual projections of all seven installed actors.
 protected=[];manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 for url in manifest['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url;catalogue=read(cp)
  for entry in catalogue['models']:
   if entry['uid']not in scope['touchingNativeUids']:continue
   take(SCOPE,cp);ap=cp.parent/entry['asset'];raw=ap.read_bytes();assert digest(raw)==entry['sha256']==pins[SCOPE][str(ap.relative_to(ROOT))];refs.append(ap)
   tri=decode_original_world_triangles(raw);projected=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
   protected.append(dict(uid=entry['uid'],sourceSHA256=entry['sha256'],sourceFaces=len(tri),sourceProjectionWKT=projected.wkt,transitionDistanceM=projected.distance(outer)))
   # All touching actors require full before/after checks; no disjointness exemption.
 assert len(protected)==len(scope['touchingNativeUids'])
 bpolys=shapely.polygons(baseline[:,:,[0,2]]);tree=shapely.STRtree(bpolys)
 output=list(coreFaces);lineage=[dict(kind='verified-private-core',face=i)for i in range(len(coreFaces))]
 for i in range(len(ground)):
  part=polygons[i].intersection(ring)
  if part.area<=1e-12:continue
  coeff=plane(ground[i])
  for j in tree.query(part,predicate='intersects'):
   fragment=part.intersection(bpolys[j])
   if fragment.area<=1e-12:continue
   bc=plane(baseline[j])
   for face in lift(fragment,coeff):
    for v in face:
     point=shapely.Point(v[[0,2]]);inside=point.distance(core);outside=point.distance(outer.boundary);weight=outside/(inside+outside)if inside+outside else 1
     v[1]=weight*v[1]+(1-weight)*float(v[[0,2]]@bc[:2]+bc[2])
    output.append(face);lineage.append(dict(kind='source-to-current-transition',sourceFace=int(i),baselineFace=int(j)))
 for i,face in enumerate(baseline):
  if bpolys[i].disjoint(outer):
   output.append(face);lineage.append(dict(kind='unchanged-baseline-face',face=i));continue
  for fragment in lift(bpolys[i].difference(outer),plane(face)):
   output.append(fragment);lineage.append(dict(kind='baseline-plane-fragment',face=i))
 output=np.asarray(output,dtype='float64');assert np.array_equal(output[:len(coreFaces)],coreFaces);assert np.isfinite(output).all()
 save(DOC/'protected.json',dict(rows=protected,coreWKT=core.wkt,outerWKT=outer.wkt))
 b=row['source']['building'];final=module('yoho_retained_foundation',HERE/'xl-final-script-pass.py')
 result=final.foundation_context(model,output,Polygon(b['rings'][0],b['rings'][1:]))
 save(LOCAL/'diagnostic-height-surfaces.json.gz',dict(triangles=output.tolist(),notPublishable=True))
 save(DOC/'foundation.json',result)
 summary=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],completeSourceFaces=len(model),retainedTerrainSHA256ByURL={r['url']:r['sha256'] for r in records},protectedInstalledModels=protected,retainedPrivateCoreFaces=len(coreFaces),transitionWidthM=8,diagnosticFaces=len(output),foundation={k:v for k,v in result.items()if k!='components'},installationApproved=False,productionChanges=0,qualification='Private shaped surface diagnostic. Whole-neighbour before/after, coverage, seams, overlaps, actual renderer and publication checks remain required.')
 save(DOC/'lineage.json.gz',dict(rows=lineage));save(DOC/'summary.json',summary)
 for key,h in consumed.items(): assert digest((ROOT/key).read_bytes())==h,key
 assert digest(asset.read_bytes())==row['sourceSHA256']
 assert reservations.owns(lease)
 refs.extend([LOCAL/'diagnostic-height-surfaces.json.gz',HERE/'xl-final-script-pass.py',HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py',HERE/'exact_packed_world_geometry_20261009.py'])
 r=module('yoho_retained_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'full-original-on-exact-retained-domain-ground',list(dict.fromkeys(refs)),summary)
 print(json.dumps(dict(jobId=r['jobId'],diagnosticFaces=len(output),foundation=summary['foundation'],neighbours=len(protected))),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/276331:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
