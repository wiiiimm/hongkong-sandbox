"""Private local original-TIN inset with a return to the current Ronsdale parent terrain."""
from pathlib import Path
import copy,traceback
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from china_merchants_finite_inset_v4_20261021 import plane,lift as parent_fragment_lift,lower_region as convex_lower_region
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-local-inset-v1-20261022';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UIDS=['landsd/233771:0']
def lower_region(region,difference):
 parts=list(shapely.get_parts(region));polygons=[]
 while parts:
  p=parts.pop()
  if p.geom_type=='Polygon':polygons.append(p)
  elif p.geom_type in ('GeometryCollection','MultiPolygon'):parts.extend(shapely.get_parts(p))
  else:assert p.area==0
 assert abs(sum(p.area for p in polygons)-region.area)<1e-10
 return shapely.union_all([convex_lower_region(p,difference)for p in polygons])
def lift(region,coefficients):
 # Preserve positive-area fragments; the renderer decides height-index eligibility.
 result=[];parts=list(shapely.get_parts(region))
 while parts:
  part=parts.pop()
  if part.geom_type in ('MultiPolygon','GeometryCollection'):parts.extend(shapely.get_parts(part))
  elif part.geom_type=='Polygon' and part.area>0:
   for tri in shapely.get_parts(shapely.constrained_delaunay_triangles(part)):
    if tri.geom_type!='Polygon' or tri.area<=0:continue
    xz=np.asarray(tri.exterior.coords[:3]);y=xz@coefficients[:2]+coefficients[2];result.append(np.column_stack([xz[:,0],y,xz[:,1]]))
 return result
def main():
 assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  d=BASE/batch;_,p=authenticate(d);path=d/name;assert digest(path.read_bytes())==p[str(path.relative_to(ROOT))];pins.update(p);refs.extend([d/'result.json',path]);return read(path)
 scope=take('government-xl-ronsdale-terrain-scope-v2-20261022','scope.json');assert not scope['overlappingTerrain'];scope['regionalParentExtent']=scope['baseReplacementExtent']
 selected=take('government-xl-ronsdale-podium-original-ground-v1-20261022','selection.json.gz')
 for name in ['government-xl-ronsdale-podium-original-ground-v1-20261022','government-xl-ronsdale-adjacent-ground-v1-20261022']:
  _,bound=authenticate(BASE/name);refs.append(BASE/name/'result.json')
  for key,h in bound.items():
   assert key not in pins or pins[key]==h; pins[key]=h
 recovery=dict(terrainPaths=[p for p in pins if '/terrain/'in p and p.endswith('.gltf')]);assert len(recovery['terrainPaths'])==2
 checkpoint=BASE/'government-xl-ronsdale-repair-checkpoint-v1-20261022';_,fp=authenticate(checkpoint);oldpath=BASE/'government-xl-ronsdale-private-terrain-v1-20261022/failed-or-proposed-terrain.json';assert digest(oldpath.read_bytes())==fp[str(oldpath.relative_to(ROOT))];old=read(oldpath);refs.extend([checkpoint/'result.json',oldpath])
 cap=BASE/'government-xl-remaining-forty-assembly-runtime-v1-20261021';_,cp=authenticate(cap);runtimepath=HERE/'local'/cap.name/'runtime-geometry.json.gz';assert digest(runtimepath.read_bytes())==cp[str(runtimepath.relative_to(ROOT))];refs.extend([cap/'result.json',runtimepath])
 g=next(r for r in read(runtimepath)['rows']if r['uid']=='landsd/233771:0');faces=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert g['sourceSHA256']==selected['rows'][0]['sourceSHA256']
 projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in faces])
 parentpath=HERE/'local/government-xl-ronsdale-parent-capture-v1-20261022/parent.json';captured=read(parentpath);refs.extend([parentpath,HERE/'ronsdale_parent_capture_v1_20261022.mjs'])
 for key,h in captured['inputHashes'].items():
  assert digest((ROOT/key).read_bytes())==h;assert key not in pins or pins[key]==h;pins[key]=h;refs.append(ROOT/key)
 baseline=np.asarray(captured['triangles']);assert len(baseline)==18;assert shapely.union_all(shapely.polygons(baseline[:,:,[0,2]])).symmetric_difference(shapely.box(*scope['regionalParentExtent'])).area==0
 core=projection.buffer(1,join_style='mitre');outer=core.buffer(5,join_style='mitre')
 domain=shapely.box(*scope['regionalParentExtent']);assert domain.covers(outer)and outer.distance(domain.boundary)>0
 assert core.covers(projection)
 # Complete neighbour regression remains a separate required acceptance stage.
 X0,Z0,X1,Z1=outer.bounds
 # A shared triangulated return band defines one continuous piecewise-affine
 # blend field. Intersect all terrain fragments with these same sectors.
 sectors=[(core,None)];band=outer.difference(core);sector_records=[]
 for region in shapely.get_parts(shapely.constrained_delaunay_triangles(band)):
  if region.geom_type!='Polygon' or region.area<=0:continue
  xz=np.asarray(region.exterior.coords[:3]);weights=[]
  for x,z in xz:
   point=shapely.Point(x,z);inside=point.distance(core.boundary)<1e-8;outside=point.distance(outer.boundary)<1e-8
   assert inside != outside
   weights.append(0. if inside else 1.)
  coefficients=plane(np.column_stack([xz[:,0],weights,xz[:,1]]))
  sectors.append((region,lambda x,z,c=coefficients:x*c[0]+z*c[1]+c[2]))
  sector_records.append(dict(regionWKT=region.wkt,weightPlane=coefficients.tolist()))
 assert shapely.union_all([p for p,_ in sectors]).symmetric_difference(outer).area<1e-8
 loader=module('parkview_private_original_tin',HERE/'xl-second-pass.py');loader.LOCAL=LOCAL;source=[]
 for name in recovery['terrainPaths']:
  p=ROOT/name
  for q in p.parent.iterdir():
   if q.is_file():assert digest(q.read_bytes())==pins[str(q.relative_to(ROOT))];refs.append(q)
  t=loader.terrain_triangles(p);mask=(t[:,:,0].max(1)>=X0)&(t[:,:,0].min(1)<=X1)&(t[:,:,2].max(1)>=Z0)&(t[:,:,2].min(1)<=Z1)
  for f in t[mask]:
   poly=shapely.Polygon(f[:,[0,2]])
   if poly.area>1e-10:source.extend(lift(poly.intersection(outer),plane(f)))
 source=np.asarray(source);rawsource=source.copy();polys=shapely.polygons(source[:,:,[0,2]]);union=shapely.union_all(polys);oldexcess=float(shapely.area(polys).sum()-union.area);tree=shapely.STRtree(polys);planes=[plane(f)for f in source];upper=[];upperlineage=[]
 for i,poly in enumerate(polys):
  cuts=[]
  for j in tree.query(poly,predicate='intersects'):
   if i==j:continue
   overlap=poly.intersection(polys[j])
   if overlap.area<=1e-10:continue
   if np.array_equal(planes[i],planes[j]):
    if j<i:cuts.append(overlap)
   else:
    higher=lower_region(overlap,planes[j]-planes[i])
    if higher.area>0:cuts.append(higher)
  keep=poly.difference(shapely.union_all(cuts))if cuts else poly
  for face in lift(keep,planes[i]):upper.append(face);upperlineage.append(i)
 source=np.asarray(upper);polys=shapely.polygons(source[:,:,[0,2]]);newunion=shapely.union_all(polys);newexcess=float(shapely.area(polys).sum()-newunion.area)
 assert abs(newexcess)<1e-6,'Highest original terrain still overlaps'
 assert newunion.symmetric_difference(union).area<1e-6,'Highest original terrain coverage changed'
 tree=shapely.STRtree(polys);planes=[planes[i]for i in upperlineage];output=[];lineage=[];changed=[];removed=inserted=0.
 print(dict(originalClippedTerrainFaces=len(rawsource),originalExcessM2=oldexcess,highestTerrainFaces=len(source),remainingExcessM2=newexcess),flush=True)
 for i,f in enumerate(baseline):
  poly=shapely.Polygon(f[:,[0,2]])
  if poly.area<=1e-10 or not poly.intersects(outer):output.append(f);lineage.append(dict(kind='unchanged',parentFace=i));continue
  parentplane=plane(f);cuts=[];added=[]
  for j in tree.query(poly,predicate='intersects'):
   intersection=poly.intersection(polys[j])
   if intersection.area<=1e-10:continue
   lower=lower_region(intersection,parentplane-planes[j])
   if lower.area<=1e-10:continue
   cuts.append(lower)
   for region,weight in sectors:
    for face in lift(lower.intersection(region),planes[j]):
     if weight is not None:
      w=np.clip(np.array([weight(x,z)for x,_,z in face]),0,1);parentheight=face[:,[0,2]]@parentplane[:2]+parentplane[2];face[:,1]=face[:,1]*(1-w)+parentheight*w
     added.append((face,int(j),'original-TIN'if weight is None else'transition'))
  if not cuts:output.append(f);lineage.append(dict(kind='unchanged',parentFace=i));continue
  cut=shapely.union_all(cuts);removed+=cut.area;changed.append(i)
  for part in parent_fragment_lift(poly.difference(cut),parentplane):output.append(part);lineage.append(dict(kind='parent-fragment',parentFace=i))
  for part,j,kind in added:output.append(part);lineage.append(dict(kind=kind,parentFace=i,sourceFace=j));inserted+=shapely.Polygon(part[:,[0,2]]).area
 assert abs(removed-inserted)<1e-6;output=np.asarray(output);candidate=copy.deepcopy(old);candidate['nativeMesh']['position']=output.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(output.size//3));candidate['nativeMesh'].pop('sourceOverlap',None);candidate['nativeMesh']['source'].pop('numericalCoverageGap',None)
 policy='Private lower original-TIN inset limited to full original-source projection plus one metre, with a shared piecewise-affine five-metre return band; exact old ground outside. No source building geometry or pose changes.'
 for meta in [candidate['nativeMesh']['source'],candidate['meta']['source']]:meta['ronsdalePrivateRepair']=dict(policy=policy,parentSHA256=digest(oldpath.read_bytes()),coreBounds=list(core.bounds),outerBounds=list(outer.bounds))
 candidate['meta']['targetUids']=UIDS
 DOC.mkdir(parents=True);LOCAL.mkdir(parents=True,exist_ok=True);save(DOC/'lineage.json.gz',dict(parentFaceCount=len(baseline),sourceFaces=source.tolist(),originalClippedTerrainFaces=rawsource.tolist(),highestSourceLineage=upperlineage,originalProjectedExcessM2=oldexcess,remainingProjectedExcessM2=newexcess,changedParentFaces=changed,outputLineage=lineage,coreBounds=list(core.bounds),outerBounds=list(outer.bounds),coreWKT=core.wkt,outerWKT=outer.wkt,blendSectors=sector_records,removedAreaM2=removed,insertedAreaM2=inserted))
 error=None
 try:
  from float32_coverage import approve_roundoff
  from native_patch_resolution import projected_context
  _,polygons,missing,_=projected_context(candidate,scope['regionalParentExtent']);difference=shapely.union_all(polygons).symmetric_difference(domain).area
  if difference:save(DOC/'numerical-coverage.json',approve_roundoff(candidate,scope['regionalParentExtent']))
  overlap=module('parkview_private_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=DOC;overlap.overlap_proof(candidate,[oldpath,Path(__file__)])
  builder=module('parkview_private_validator',HERE/'resolve-pass-indexed-parent-clipping.py');rootpath=ROOT/'3d-viewer/city/data/terrain.json';assert digest(rootpath.read_bytes())==pins[str(rootpath.relative_to(ROOT))];refs.append(rootpath);builder.validate_patch(candidate,read(rootpath));assert len(output)<=25000,'terrain-runtime-budget'
 except Exception as e:error=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc());save(DOC/'validation-failure.json',error)
 path=LOCAL/'candidate-terrain.json';save(path,candidate);save(DOC/'terrain-candidates.json',[dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=UIDS,bounds=scope['regionalParentExtent'],triangles=len(output))]);summary=dict(uids=UIDS,terrainValidationPassed=error is None,error=error,oldFaces=len(baseline),newFaces=len(output),changedOldFaces=len(changed),sourceGeometryChanges=0,installationApproved=False,productionChanges=0);save(DOC/'summary.json',summary)
 refs.extend([path,HERE/'china_merchants_finite_inset_v4_20261021.py',HERE/'xl-second-pass.py',HERE/'float32_coverage.py',HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py']);module('parkview_private_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-terrain-composition',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
