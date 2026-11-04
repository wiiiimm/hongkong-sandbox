"""Join source-local station terrain to the current nested parent; private candidate only."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon,Point,box
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from stanford_local_terrain_join_v4_20261015 import split_vertical
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-parent-join-candidate-v3-20261015';DOC=BASE/BATCH;PREV=BASE/'government-xl-ets-nested-runtime-candidate-v2-20261015'
def main():
 assert not DOC.exists();r=read(PREV/'result.json');refs=[Path(__file__),PREV/'result.json'];pins={}
 for q in r['evidenceRefs']:
  assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 plan=read(PREV/'plan.json');parentpath=ROOT/'3d-viewer'/plan['parentURL'];parent=read(parentpath);patch=read(PREV/'private-patch.json.gz');bounds=plan['nestedBounds'];domain=box(*bounds)
 source=next(r for r in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if r['modelId']=='B360171738601063C0');asset=ROOT/source['asset']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());whole=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));inner=whole.buffer(.1,join_style='mitre');outer=whole.buffer(.8,join_style='mitre');assert domain.contains(outer)
 helper=module('ets_join_helpers',HERE/'primrose_private_terrain_join_v1_20261015.py');patches=module('ets_parent_faces',HERE/'native_patch_resolution.py');resolution=module('ets_join_parent_sampler',HERE/'resolve-pass.py');sampler=resolution.terrain.fine.DemSampler(parent,rendered=True)
 before=np.asarray(patches.grid_surface_faces(sampler,domain));after=np.asarray(patch['nativeMesh']['position']).reshape(-1,3)[np.asarray(patch['nativeMesh']['index']).reshape(-1,3)];out=[];lineage=[]
 def emit(region,face,kind,i,other=None,j=None):
  for poly in helper.pieces(region):
   points=[]
   for x,z in list(poly.exterior.coords)[:3]:
    y=helper.height(face,x,z)
    if other is not None:
     point=Point(x,z);di=point.distance(inner);do=point.distance(outer.boundary);assert di+do>0;alpha=do/(di+do);y=alpha*y+(1-alpha)*helper.height(other,x,z)
    points.append([x,y,z])
   out.append(points);lineage.append({'kind':kind,'sourceFace':i,'parentFace':j})
 for kind,faces,region in [('station-core',after,inner),('current-parent',before,domain.difference(outer))]:
  for i,f in enumerate(faces):
   poly=Polygon(f[:,[0,2]])
   if poly.area==0:
    for part in split_vertical(f,region):out.append(part);lineage.append({'kind':kind+'-vertical','sourceFace':i})
   else:emit(poly.intersection(region),f,kind,i)
 band=outer.difference(inner);bp=shapely.polygons(before[:,:,[0,2]]);tree=shapely.STRtree(bp)
 for i,f in enumerate(after):
  poly=Polygon(f[:,[0,2]])
  if poly.area==0:
   projection=shapely.MultiPoint(f[:,[0,2]]).convex_hull
   for j in tree.query(projection,predicate='intersects'):
    if bp[j].area<=1e-10:continue
    for vertices in split_vertical(f,band.intersection(bp[j])):
     points=[]
     for x,y,z in vertices:
      point=Point(x,z);di=point.distance(inner);do=point.distance(outer.boundary);assert di+do>0;alpha=do/(di+do);points.append([x,alpha*y+(1-alpha)*helper.height(before[j],x,z),z])
     out.append(points);lineage.append({'kind':'transition-vertical','sourceFace':i,'parentFace':int(j)})
  else:
   region=poly.intersection(band)
   if region.is_empty:continue
   for j in tree.query(region,predicate='intersects'):
    if bp[j].area>1e-10:emit(region.intersection(bp[j]),f,'transition',i,before[j],int(j))
 patch['id']=BATCH;patch['nativeMesh']['position']=np.asarray(out).reshape(-1).tolist();patch['nativeMesh']['index']=list(range(len(out)*3));patch['nativeMesh']['source']['privateStationParentJoin']={'innerPaddingM':.1,'outerPaddingM':.8,'sourceSHA256':source['sourceSHA256'],'sourceGeometryChanges':0,'publication':False}
 packed=np.asarray(out,dtype='<f4').astype(float);polys=shapely.polygons(packed[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;union=shapely.union_all(polys[valid]);gap=domain.symmetric_difference(union).area;overlap=shapely.area(polys[valid]).sum()-union.area
 try:resolution.validate_patch(patch,parent);validation={'passed':True}
 except (AssertionError,ValueError)as e:validation={'passed':False,'error':str(e)}
 DOC.mkdir();save(DOC/'private-patch.json.gz',patch);save(DOC/'lineage.json.gz',{'rows':lineage,'sourceProjectionGeoJSON':shapely.to_geojson(whole),'currentParentFaces':before.tolist()});summary={'triangles':len(out),'coverageGapM2':float(gap),'projectionOverlapM2':float(overlap),'validation':validation,'sourceGeometryChanges':0,'publication':False,'fullAcceptance':False};save(DOC/'summary.json',summary)
 refs.extend([asset,HERE/'stanford_local_terrain_join_v4_20261015.py',HERE/'primrose_private_terrain_join_v1_20261015.py',HERE/'native_patch_resolution.py',HERE/'resolve-pass.py'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 module('freeze_ets_join',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-station-source-local-parent-join-v3',refs,{'uids':['landsd/323703:0'],'summary':summary,'fullAcceptance':False});print(summary,flush=True)
if __name__=='__main__':main()
