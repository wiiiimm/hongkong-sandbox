"""Retain current parent's exact authored boundary vertices; no model changes."""
import json,importlib.util,uuid,copy
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from native_patch_resolution import _faces,_patch_bounds
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_unchanged_adjacent_terrain_boundary_20261010 import verify,sha
BATCH='xl-terrain-recovery-20261010-ching-hin-exact-parent-boundary-proposal-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;local=HERE/'local'/BATCH;assert not doc.exists();prior=base/'government-xl-ching-hin-complete-current-recheck-20261007';candidate=read(prior/'terrain-candidates.json')[0];original=ROOT/candidate['path'];parent_path=ROOT/'3d-viewer'/candidate['replaces']['url'];parent=read(parent_path);assert digest(parent_path.read_bytes())==candidate['replaces']['sha256']=='46982b10f64af071916ff14984174b26e491664373f888765d4aad8b4c75b6d9';assert digest(original.read_bytes())==candidate['sha256']=='42455e3f708bc9af846facb6e04d8a43a353f3adcd36680b0b7adf46e692c0c0';q=copy.deepcopy(read(original));bounds=candidate['bounds'];assert _patch_bounds(parent)==_patch_bounds(q)==bounds
 source=read(prior/'selection.json.gz')['rows'][0];asset=ROOT/source['candidate']['path'];tri=decode_original_world_triangles(asset.read_bytes());assert digest(asset.read_bytes())==source['sourceSHA256'];projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri]);boundary=shapely.box(*bounds).boundary;assert projection.disjoint(boundary)
 p=_faces(parent).reshape(-1,3);raw=np.asarray(q['nativeMesh']['position'],float).reshape(-1,3);before=raw.astype(np.float32).astype(float);old={}
 def edge(x,z):return x in [bounds[0],bounds[2]] or z in [bounds[1],bounds[3]]
 for x,y,z in p:
  if edge(x,z):
   key=(float(x),float(z));assert key not in old or old[key]==float(y);old[key]=float(y)
 mask=np.array([edge(x,z) for x,y,z in before]);assert set((float(x),float(z)) for x,y,z in before[mask])==set(old),'Authored boundary XZ inventory changed'
 for i in np.flatnonzero(mask):raw[i,1]=old[(float(before[i,0]),float(before[i,2]))]
 q['nativeMesh']['position']=raw.reshape(-1).tolist();after=raw.astype(np.float32).astype(float);assert np.array_equal(before[~mask],after[~mask]) and np.array_equal(before[:,[0,2]],after[:,[0,2]]);assert q['nativeMesh']['index']==read(original)['nativeMesh']['index']
 target=local/'government-native-26653-0.json';save(target,q);updated={**candidate,'path':str(target.relative_to(ROOT)),'sha256':digest(target.read_bytes())};save(doc/'terrain-candidates.json',[updated]);terrain=read(prior/'terrain.json');terrain.update(patch=updated,currentParentBoundaryPreservation=dict(parentAsset=ref(parent_path),originalProposal=ref(original),completeOriginalBoundaryXZVertices=len(old),changedRenderedBoundaryVertices=int(np.any(before!=after,axis=1).sum()),maximumBoundaryYRestoreM=float(np.max(np.abs(before[mask,1]-after[mask,1]))),sourceGeometryChanges=0,interiorRenderedTerrainChanged=False));save(doc/'terrain.json',terrain)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);proofs=[];refs=[ref(x) for x in [Path(__file__),asset,original,parent_path,prior/'terrain-candidates.json',prior/'terrain.json',target,manifest,HERE/'original_unchanged_adjacent_terrain_boundary_20261010.py',HERE/'test_original_unchanged_adjacent_terrain_boundary_20261010.py',HERE/'native_patch_resolution.py']]
 for e in read(manifest)['terrainPatches']:
  if e['url']==candidate['replaces']['url']:continue
  a_path=ROOT/'3d-viewer'/e['url'];a=read(a_path);ab=_patch_bounds(a) if not a.get('patches') else a.get('bounds');assert ab is not None
  if not shapely.box(*ab).intersects(shapely.box(*bounds)):continue
  binding=dict(completeOriginalParentTrianglesSHA256=sha(_faces(parent)),completeProposalTrianglesSHA256=sha(_faces(q)),completeUnchangedAdjacentTrianglesSHA256=sha(_faces(a)),currentManifestSHA256=start['sha256'],parentAsset=ref(parent_path),proposalAsset=ref(target),unchangedAdjacentAsset=ref(a_path));proof=verify(_faces(parent),_faces(q),_faces(a),parent_bounds=bounds,proposal_bounds=bounds,adjacent_bounds=ab,expected_binding=binding,current_binding=binding);proofs.append(dict(adjacentURL=e['url'],proof=proof));refs.append(ref(a_path))
 assert proofs and ref(manifest)==start
 result=dict(uids=[source['uid']],terrainProposal=updated,parentBoundaryPreservation=terrain['currentParentBoundaryPreservation'],completeExactAdjacentSeamProofs=proofs,completeSourceProjectionDistanceFromRestoredBoundaryM=float(projection.distance(boundary)),modelGeometryChanges=0,sourceGeometryChanges=0,onlyCurrentParentBoundaryTerrainValuesRestored=True,currentFullPhysicalRerunRequired=True,fullAcceptance=False,installationApproved=False,evidenceRefs=refs);save(doc/'diagnostic.json.gz',result)
 spec=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'source-disjoint-exact-current-parent-boundary-preservation-proposal-v1',[ROOT/r['path'] for r in refs],dict(uids=result['uids'],sourceProjectionDistanceFromBoundaryM=result['completeSourceProjectionDistanceFromRestoredBoundaryM'],boundaryXZVertices=len(old),maximumBoundaryYRestoreM=terrain['currentParentBoundaryPreservation']['maximumBoundaryYRestoreM'],exactAdjacentSeams=len(proofs),terrainProposalSHA256=updated['sha256'],sourceGeometryChanges=0,fullAcceptance=False,currentFullPhysicalRerunRequired=True));print(json.dumps(dict(patchSHA256=updated['sha256'],exactAdjacentSeams=len(proofs),sourceDistanceM=result['completeSourceProjectionDistanceFromRestoredBoundaryM'])),flush=True)
if __name__=='__main__':main()
