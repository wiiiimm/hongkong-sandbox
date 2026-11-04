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
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-podium-transition-feasibility-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SCOPE=BASE/'government-xl-tko-podium-regional-scope-v1-20261021';GROUND=BASE/'government-xl-tko-podium-original-ground-v1-20261021';SELECTION=BASE/'government-xl-tko-podium-current-terrain-v2-20261021'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
 refs=[Path(__file__)];pins={};consumed={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SCOPE,GROUND,SELECTION]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))],p
  consumed[str(p.relative_to(ROOT))]=pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 scope=take(SCOPE,SCOPE/'scope.json');take(SCOPE,ROOT/'3d-viewer/city/data/manifest.json')
 row=next(r for r in take(SELECTION,SELECTION/'selection.json.gz')['rows']if r['uid']=='landsd/265489:0')
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 model=decode_original_world_triangles(asset.read_bytes());assert len(model)==4851
 groundfile=HERE/'local'/GROUND.name/'265489:0-ground.json.gz';ground=np.asarray(take(GROUND,groundfile)['completeOriginalTerrain'],dtype='float64')
 assert digest(ground.astype('<f8').tobytes())==take(GROUND,GROUND/'265489:0.json')['terrainWorldSHA256']
 assert len(scope['retainedPatches'])==1;record=scope['retainedPatches'][0];oldpath=ROOT/'3d-viewer'/record['url'];oldpatch=take(SCOPE,oldpath);old=_faces(oldpatch);domain=shapely.box(*record['extent'])
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
 keep=shapely.intersects(polygons,projection.buffer(1,join_style='mitre'))
 ids=np.flatnonzero(keep);core=shapely.union_all(polygons[keep]);outer=core.buffer(8,join_style='round');ring=outer.difference(core)
 regionalBoundaryCovered=rectangle.covers(outer)
 # Bind and protect the complete actual projections of all seven installed actors.
 protected=[];manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 for url in manifest['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url;catalogue=read(cp)
  for entry in catalogue['models']:
   if entry['uid']not in scope['touchingNativeUids']:continue
   take(SCOPE,cp);ap=cp.parent/entry['asset'];raw=ap.read_bytes();assert digest(raw)==entry['sha256']==pins[SCOPE][str(ap.relative_to(ROOT))];refs.append(ap)
   tri=decode_original_world_triangles(raw);projected=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
   protected.append(dict(uid=entry['uid'],sourceSHA256=entry['sha256'],sourceFaces=len(tri),sourceProjectionWKT=projected.wkt,transitionDistanceM=projected.distance(outer)))
   protected[-1].update(coreOverlapM2=projected.intersection(core).area,transitionOverlapM2=projected.intersection(ring).area,bufferedDisjoint=outer.disjoint(projected.buffer(1,join_style='mitre')))
 assert len(protected)==len(scope['touchingNativeUids'])==6
 summary=dict(uids=[row['uid']],protectedInstalledModels=protected,regionalBoundaryCovered=regionalBoundaryCovered,coreWKT=core.wkt,outerWKT=outer.wkt,coreSourceFaceIds=ids.tolist(),coreFaces=len(ids),transitionWidthM=8,installationApproved=False,terrainChanged=False)
 save(DOC/'feasibility.json',summary)
 for key,h in consumed.items():assert digest((ROOT/key).read_bytes())==h,key
 assert reservations.owns(lease)
 refs.extend([HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py',HERE/'exact_packed_world_geometry_20261009.py'])
 result=module('tko_feasibility_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-terrain-core-neighbour-feasibility',list(dict.fromkeys(refs)),dict(uids=[row['uid']],regionalBoundaryCovered=regionalBoundaryCovered,coreFaces=len(ids),touching=[{k:r[k] for k in ['uid','coreOverlapM2','transitionOverlapM2','bufferedDisjoint']} for r in protected],installationApproved=False))
 print(dict(jobId=result['jobId'],regionalBoundaryCovered=regionalBoundaryCovered,neighbours=[{k:r[k] for k in ['uid','coreOverlapM2','transitionOverlapM2','bufferedDisjoint']} for r in protected]),flush=True)

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/265489:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
