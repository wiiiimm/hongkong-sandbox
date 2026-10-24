"""Private podium-shaped terrain core; retain complete touching runtime facets."""
from pathlib import Path
import copy
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from native_patch_resolution import _faces,grid_surface_faces
from source_surface_inset import plane,lift
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-shaped-terrain-v3-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
RAW=BASE/'government-xl-plaza-ascot-terrain-diagnostic-v1-20261020';REC=BASE/'government-xl-plaza-ascot-adjacent-original-recovery-v1-20261020';SCOPE=BASE/'government-xl-plaza-ascot-current-scope-v1-20261020';UID='landsd/258411:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [RAW,REC,SCOPE,BASE/'government-xl-plaza-ascot-basic-ground-v2-20261020']:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rawpath=HERE/'local'/RAW.name/'unvalidated-terrain.json';patch=take(RAW,rawpath);terrain=_faces(patch)
 row=next(r for r in take(REC,REC/'recovery.json')['rows']if r['uid']==UID);asset=ROOT/row['assetPath'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);model=decode_original_world_triangles(asset.read_bytes())
 projection=shapely.union_all(shapely.polygons(model[:,:,[0,2]]));protected=projection.buffer(1,join_style='mitre')
 polygons=shapely.polygons(terrain[:,:,[0,2]]);keep=shapely.intersects(polygons,protected);ids=np.flatnonzero(keep);core=shapely.union_all(polygons[keep]);outer=core.buffer(10,join_style='round')
 # Preserve the full actual BASIC mesh bounds of the unrelated external tower.
 basicdir=BASE/'government-xl-plaza-ascot-basic-ground-v2-20261020'
 basic=next(r for r in take(basicdir,basicdir/'ground.json.gz')['rows'] if r['uid']=='landsd/161720:0')
 vertices=np.asarray(basic['position']).reshape(-1,3);lo=vertices.min(0);hi=vertices.max(0)
 preserved=shapely.box(lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1)
 assert core.disjoint(preserved),'neighbour-preservation-would-change-protected-source-core'
 outer=outer.difference(preserved);ring=outer.difference(core)
 scope=take(SCOPE,SCOPE/'scope.json');rectangle=shapely.box(*scope['baseReplacementExtent']);assert rectangle.covers(outer),'shaped-core-crosses-parent-boundary'
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(SCOPE,parentpath);take(SCOPE,ROOT/'3d-viewer/city/data/manifest.json')
 builder=module('ascot_shaped_parent',HERE/'resolve-pass-indexed-parent-clipping.py');sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
 parentfaces=np.asarray(grid_surface_faces(sampler,rectangle));parentpolys=shapely.polygons(parentfaces[:,:,[0,2]]);tree=shapely.STRtree(parentpolys)
 output=list(terrain[ids]);lineage=[dict(kind='unchanged-protected-runtime-face',face=int(i))for i in ids];transition=0
 for i in np.flatnonzero(~keep):
  part=polygons[i].intersection(ring)
  if part.area<=1e-10:continue
  coefficients=plane(terrain[i])
  for j in tree.query(part,predicate='intersects'):
   fragment=part.intersection(parentpolys[j])
   if fragment.area<=1e-10:continue
   parentplane=plane(parentfaces[j])
   for face in lift(fragment,coefficients):
    for v in face:
     point=shapely.Point(v[[0,2]]);inside=point.distance(core);outside=point.distance(outer.boundary);weight=outside/(inside+outside) if inside+outside else 1
     parentheight=float(v[[0,2]]@parentplane[:2]+parentplane[2]);v[1]=weight*v[1]+(1-weight)*parentheight
    output.append(face);lineage.append(dict(kind='bounded-parent-transition',face=int(i),parentFace=int(j)));transition+=1
 for i,face in enumerate(parentfaces):
  for fragment in lift(parentpolys[i].difference(outer),plane(face)):
   output.append(fragment);lineage.append(dict(kind='unchanged-parent-plane-fragment',parentFace=i))
 output=np.asarray(output);assert np.array_equal(output[:len(ids)],terrain[ids]);assert np.isfinite(output).all()
 candidate=copy.deepcopy(patch);candidate['nativeMesh']['position']=output.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(output.size//3));candidate['nativeMesh'].pop('sourceOverlap',None)
 candidate['nativeMesh']['source']['shapedCore']=dict(sourceSHA256=row['sourceSHA256'],protectedProjectionBufferM=1,outerTransitionM=10,outerJoinStyle='round',preservedNeighbourUid='landsd/161720:0',preservedNeighbourDomainWKT=preserved.wkt,policy='Every complete prior Float32 terrain facet touching the full source projection plus1m retained verbatim. Parent planes outside buffered core; deterministic bounded transition, split on parent planes. Private unapproved.')
 out=LOCAL/'candidate-terrain.json';save(out,candidate);refs.append(out);save(DOC/'lineage.json.gz',dict(rows=lineage,retainedOriginalFaceIds=ids.tolist(),coreWKT=core.wkt,outerWKT=outer.wkt))
 validationError=None
 try:
  proof=module('ascot_shaped_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof.DOC=DOC;proof.overlap_proof(candidate,[rawpath,asset,Path(__file__)]);save(out,candidate);builder.validate_patch(candidate,parent)
 except AssertionError as error:validationError=str(error)
 summary=dict(uids=[UID],oldFaces=len(terrain),candidateFaces=len(output),protectedUnchangedFaces=len(ids),preservedNeighbourUid='landsd/161720:0',preservedNeighbourDomainWKT=preserved.wkt,transitionFaces=transition,fullSourceProjectionAreaM2=float(projection.area),nativeCoreAreaM2=float(core.area),outerAreaM2=float(outer.area),withinTriangleBudget=len(output)<=25000,terrainValidationPassed=validationError is None,validationError=validationError,installationApproved=False,productionTerrainChanges=0,buildingGeometryChanges=0)
 save(DOC/'summary.json',summary);save(DOC/'terrain-candidates.json',[dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),uids=[UID],bounds=scope['baseReplacementExtent'],triangles=len(output))])
 refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','native_patch_resolution.py','source_surface_inset.py','resolve-pass-indexed-parent-clipping.py','sham_shui_po_pool_shared_terrain_v2_20261016.py'])
 module('ascot_shaped_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-complete-source-shaped-terrain-proposal',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
if __name__=='__main__':main()
