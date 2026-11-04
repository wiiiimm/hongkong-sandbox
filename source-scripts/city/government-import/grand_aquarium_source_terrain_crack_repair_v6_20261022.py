"""Private source-backed Float32 crack caps; original building geometry unchanged."""
from pathlib import Path
import numpy as np,shapely,traceback
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-source-terrain-crack-repair-v6-20261022'
def height(face,xz):
 a,b,c=face;n=np.cross(b-a,c-a);assert abs(n[1])>1e-10
 return a[1]-(n[0]*(xz[:,0]-a[0])+n[2]*(xz[:,1]-a[2]))/n[1]
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();prior=BASE/'government-xl-grand-aquarium-narrow-boundary-return-v1-20261022';r,pins=authenticate(prior);path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['candidate']['sha256'];patch=read(path);rp=BASE/'government-xl-grand-aquarium-narrow-return-runtime-v1-20261022';_,gpins=authenticate(rp);gp=HERE/'local'/rp.name/'runtime-geometry.json.gz';assert digest(gp.read_bytes())==gpins[str(gp.relative_to(ROOT))];g=read(gp)['rows'][0];model=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];mesh=patch['nativeMesh'];old=np.asarray(mesh['position'],dtype=np.float32).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)].astype(float);polygons=shapely.polygons(old[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;union=shapely.union_all(polygons[valid]);projection=shapely.union_all(shapely.polygons(model[:,:,[0,2]]));missing=projection.difference(union);gaps=[p for p in shapely.get_parts(missing)if p.geom_type=='Polygon'and p.area>0];assert gaps and missing.area<.25
 refs=[Path(__file__),prior/'result.json',path,rp/'result.json',gp];decoder=module('crack_source_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=local/'decode';source=[]
 sourcebatch=BASE/'government-xl-grand-aquarium-retained-boundary-inset-v6-20261022';_,sourcepins=authenticate(sourcebatch);sourcepath=sourcebatch/'unapproved-terrain.json';assert digest(sourcepath.read_bytes())==sourcepins[str(sourcepath.relative_to(ROOT))];refs.extend([sourcebatch/'result.json',sourcepath])
 for entry in read(sourcepath)['meta']['source']['nativeSources']:
  p=ROOT/entry['path'];assert digest(p.read_bytes())==entry['sha256'];refs.append(p);metadata=read(p)
  for b in metadata.get('buffers',[]):refs.append(p.parent/b['uri'])
  values=decoder.terrain_triangles(p);source.extend(values)
 parentpath=ROOT/'3d-viewer'/r['candidate']['replaces']['url'];assert digest(parentpath.read_bytes())==r['candidate']['replaces']['sha256'];refs.append(parentpath);pm=read(parentpath)['nativeMesh'];parent=np.asarray(pm['position'],dtype=np.float32).reshape(-1,3)[np.asarray(pm['index']).reshape(-1,3)].astype(float);pp=shapely.polygons(parent[:,:,[0,2]]);good=shapely.area(pp)>1e-10;parent,pp=parent[good],pp[good];pt=shapely.STRtree(pp)
 source=np.asarray(source);sp=shapely.polygons(source[:,:,[0,2]]);ok=shapely.area(sp)>1e-10;source,sp=source[ok],sp[ok];st=shapely.STRtree(sp);ot=shapely.STRtree(polygons);added=[];caps=[];maximum=0.
 for gap in gaps:
  from exact_original_projection_coverage_v2_20261010 import exact_coverage
  # Discard floating union artefacts only after exact same-facet proof.
  leaves=list(shapely.get_parts(shapely.constrained_delaunay_triangles(gap)))
  if leaves and all(exact_coverage(np.column_stack([np.asarray(q.exterior.coords[:3])[:,0],np.zeros(3),np.asarray(q.exterior.coords[:3])[:,1]]),old)['exactProjectionCovered']for q in leaves):continue
  points=[]
  for q in np.asarray(gap.exterior.coords)[:-1]:
   brackets=[]
   for value in q:
    rounded=np.float32(value)
    brackets.append([float(rounded)]if float(rounded)==value else sorted([float(rounded),float(np.nextafter(rounded,np.float32(-np.inf if rounded>value else np.inf)))]))
   points.extend([x,z]for x in brackets[0]for z in brackets[1])
  hull=shapely.MultiPoint(points).convex_hull;assert hull.covers(gap)
  vertices=[];sourceids=[]
  for q in np.asarray(hull.exterior.coords)[:-1]:
   point=shapely.Point(q);ids=ot.query(point,predicate='intersects');ids=[int(i)for i in ids if valid[i]]
   if ids:
    values=[float(height(old[i],q[None,:])[0])for i in ids];k=int(np.argmax(values));y=values[k];sourceids.append(ids[k])
   else:
    i=int(ot.nearest(point));assert valid[i]and polygons[i].distance(point)<=.002
    y=float(height(old[i],q[None,:])[0]);sourceids.append(i)
   vertices.append([q[0],y,q[1]])
  # A conservative floor under the existing boundary avoids lifting any terrain.
  levels=[]
  for i in ot.query(hull,predicate='intersects'):
   if not valid[i]:continue
   coords=shapely.get_coordinates(hull.intersection(polygons[i]))
   if len(coords):levels.extend(height(old[i],coords).tolist())
  assert levels
  floor=float(np.nextafter(np.float32(min(levels)),np.float32(-np.inf)))
  v=np.asarray(vertices,dtype=np.float32).astype(float);v[:,1]=floor;faces=[v[[0,i,i+1]]for i in range(1,len(v)-1)];assert v[:,1].min()>=1.2
  a,b,c,d=hull.bounds
  for face in faces:
   polygon=shapely.Polygon(face[:,[0,2]])
   for i in ot.query(polygon,predicate='intersects'):
    if not valid[i]:continue
    overlap=polygon.intersection(polygons[i])
    for part in shapely.get_parts(overlap):
     if part.geom_type!='Polygon'or part.area<=0:continue
     q=np.asarray(part.exterior.coords);error=float(np.max(height(face,q)-height(old[i],q)));maximum=max(maximum,error)
  caps.append(dict(originalGapWKT=gap.wkt,originalGapAreaM2=gap.area,float32CapBounds=[a,b,c,d],officialCornerSourceFaces=sourceids));added.extend(faces)
 assert maximum<=.004,'Cap raises existing terrain beyond established sampler tolerance'
 new=np.concatenate([old,np.asarray(added)]);mesh['position']=new.reshape(-1).tolist();mesh['index']=list(range(new.size//3));mesh.pop('sourceOverlap',None)
 for key in ['numericalCoverageGap','numericalProjectionOverlap']:mesh['source'].pop(key,None)
 patch['meta']['source']['numericCrackCaps']=dict(policy='Minimal Float32 hulls over exact gaps, constant floor at the minimum height of authenticated adjacent terrain over the hull boundary, rounded downward by one Float32 ULP; existing terrain facets retained, caps may extend beneath existing facets; any height increase over existing facets is bounded by the existing .004m criterion. Every old terrain facet remains; lower overlapping cap surfaces cannot replace the existing highest surface. Terrain correction only.',caps=caps,maximumExistingHeightIncreaseM=maximum)
 builder=module('crack_patch_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py');rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);refs.append(rootpath);bb=builder.extent(patch['coarseCells'],root);result=dict(uids=r['uids'],retainedUids=r['retainedUids'],installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0)
 try:
  from float32_coverage import approve_roundoff
  save(doc/'coverage.json',approve_roundoff(patch,bb));proof=module('crack_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof.DOC=doc;proof.overlap_proof(patch,refs);builder.validate_patch(patch,root);assert len(new)<=r['terrainTriangleBudget'];out=local/'candidate-terrain.json';save(out,patch);refs.append(out);result.update(status='private-terrain-validator-passed',candidate=dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),replaces=r['candidate']['replaces']),newTerrainFaces=len(added),terrainTriangles=len(new),maximumExistingHeightIncreaseM=maximum,originalGapAreaM2=float(missing.area),caps=caps)
 except Exception as e:result.update(status='source-terrain-crack-investigation',reason=str(e));save(doc/'failure.json',dict(message=str(e),traceback=traceback.format_exc()));save(doc/'unapproved-terrain.json',patch)
 save(doc/'scope.json',dict(uids=r['uids'],cells=patch['coarseCells'],bounds=bb));save(doc/'summary.json',result);refs.extend(HERE/n for n in ['xl-second-pass.py','resolve_pass_indexed_parent_clipping_v2.py','sham_shui_po_pool_shared_terrain_v2_20261016.py','float32_coverage.py']);refs.extend(p for p in local.rglob('*')if p.is_file());module('crack_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-backed-numeric-terrain-crack-cap',refs,result);print(result,flush=True)
if __name__=='__main__':main()
