"""Private exact original-ramp terrain cut using the existing source-surface routine."""
from copy import deepcopy
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from bounded_original_ramp_return_v1_20261025 import inset as inset_faces
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-quality-music-school-original-ramp-return-v5-20261025'
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
 outer=shapely.from_wkt(proof['outerWKT'])
 assert shapely.union_all(shapely.polygons(terrain[:,:,[0,2]])).covers(outer)
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
 result=dict(uids=receipts[PATCH]['uids'],sourceSHA256ByUid=receipts[PATCH]['sourceSHA256ByUid'],status='private-terrain-validator-passed',candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),terrainTriangles=len(after),changedTerrainFaces=len(proof['changedTerrainFaceIndices']),sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=True,installationApproved=False,publication=False,qualification=proof['policy'])
 save(doc/'summary.json',result);refs.extend([HERE/'bounded_original_ramp_return_v1_20261025.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'native_patch_resolution.py',HERE/'float32_coverage.py'])
 module('school_ramp_proposal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-ramp-plane-derived-terrain-local-return-proposal',refs,result);print(result,flush=True)
if __name__=='__main__':main()
