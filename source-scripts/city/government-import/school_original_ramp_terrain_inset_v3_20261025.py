"""Private exact original-ramp terrain cut using the existing source-surface routine."""
from copy import deepcopy
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_surface_inset import inset_faces
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-quality-music-school-original-ramp-inset-v3-20261025'
PATCH='government-xl-quality-music-school-three-original-inset-v1-20261025'
RAMPS='government-xl-quality-music-school-podium-eight-ramp-context-v1-20261025'
RUNTIME='government-xl-quality-music-school-three-original-private-runtime-v1-20261025'

def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();refs=[Path(__file__)];pins={};receipts={}
 def take(batch,path):
  if batch not in pins:receipts[batch],pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 ramps=take(RAMPS,BASE/RAMPS/'summary.json');selected=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');r=next(r for r in selected['rows']if r['uid']=='landsd/244789:0')
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==ramps['sourceSHA256']==r['sourceSHA256'];refs.append(asset)
 ids=[x['face']for x in ramps['rows']];source=decode_original_world_triangles(asset.read_bytes())[ids]
 assert np.array_equal(source,np.asarray([x['vertices']for x in ramps['rows']])), 'Recorded ramps must equal exact original source faces'
 take(PATCH,BASE/PATCH/'terrain-source-context.json');candidate=receipts[PATCH]['candidate'];before=take(PATCH,ROOT/candidate['path']);patch=deepcopy(before)
 mesh=patch['nativeMesh'];terrain=np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
 after,proof=inset_faces(terrain,source);assert len(after)<=25000 and after[:,:,1].min()>=1.2
 assert proof['changedTerrainFaceIndices'] and abs(proof['removedProjectedAreaM2']-proof['insertedProjectedAreaM2'])<1e-6
 footprint=shapely.union_all(shapely.polygons(source[:,:,[0,2]]))
 for item,t in zip(proof['lineage'],after):
  if item['kind']=='inset-source-plane-fragment':assert shapely.Polygon(t[:,[0,2]]).difference(footprint).area<1e-10
 mesh['position']=after.reshape(-1).tolist();mesh['index']=list(range(after.size//3))
 binding=dict(uid=r['uid'],sha256=r['sourceSHA256'],sourceFaceIndices=ids,sourceFaceSHA256=digest(source.astype('<f8').tobytes()),originalTerrainCandidate=candidate,policy=proof['policy'],continuousReturnClaimed=False)
 for metadata in [mesh['source'],patch['meta']['source']]:metadata['authoredRampInset']=binding
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(PATCH,parentpath)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 helper=module('school_ramp_existing_validator',HERE/'resolve_pass_indexed_parent_clipping_v2.py');bounds=helper.extent(patch['coarseCells'],parent)
 from native_patch_resolution import projected_context
 from float32_coverage import approve_roundoff
 _,polygons,_,_=projected_context(patch,bounds)
 doc.mkdir();local.mkdir()
 if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:save(doc/'numerical-coverage.json',approve_roundoff(patch,bounds))
 overlap=module('school_ramp_existing_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=doc;overlap.overlap_proof(patch,refs)
 save(doc/'before-validation-terrain.json',patch);helper.validate_patch(patch,parent)
 path=local/'candidate-terrain.json';save(path,patch);refs.append(path);save(doc/'inset-proof.json.gz',proof)
 scope=take(PATCH,BASE/PATCH/'scope.json');save(doc/'scope.json',scope)
 reference_batch='government-xl-quality-music-school-original-ramp-inset-v1-20261025'
 old_receipt,old_pins=authenticate(BASE/reference_batch);refs.append(BASE/reference_batch/'result.json')
 reference_path=ROOT/old_receipt['candidate']['path'];assert digest(reference_path.read_bytes())==old_receipt['candidate']['sha256'];refs.append(reference_path)
 reference=read(reference_path);comparison=deepcopy(reference)
 for key in ['evidencePath','evidenceSHA256']:comparison['nativeMesh']['sourceOverlap'][key]=patch['nativeMesh']['sourceOverlap'][key]
 assert comparison==patch, 'Artifact binding fix changed data beyond its overlap-evidence path/hash'
 assert patch['nativeMesh']['sourceOverlap']['evidencePath']==str(doc.relative_to(ROOT))
 result=dict(uids=receipts[PATCH]['uids'],sourceSHA256ByUid=receipts[PATCH]['sourceSHA256ByUid'],status='private-terrain-validator-passed',candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),terrainTriangles=len(after),changedTerrainFaces=len(proof['changedTerrainFaceIndices']),sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=True,installationApproved=False,publication=False,qualification='Existing exact source-surface lower envelope applied only to eight original upward ramp projections. No shifted floor, source geometry edit, extrapolation, blend/continuous-return claim or clearance-limit change. Original terrain remains outside exact ramp projection; internal height-step visibility and all scene/source/neighbour checks still require independent review.')
 save(doc/'summary.json',result);refs.extend([HERE/'source_surface_inset.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'native_patch_resolution.py',HERE/'float32_coverage.py'])
 module('school_ramp_proposal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-ramp-exact-terrain-lower-envelope-proposal',refs,result);print(result,flush=True)
if __name__=='__main__':main()
