"""Prepare exact PRIVATE cycle bindings, then run complete nested validators.
No publisher entry point or installed-source acceptance is modified.
"""
import copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
import one_peking_nested_cycle_boundary_v3_20261101 as boundary
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'cycle-preparation-v3-20261101'
def main():
 out=BASE/BATCH;assert not out.exists();sourcebatch=P+'three-member-original-return-v2-20261101';receipt,pins=authenticate(BASE/sourcebatch);refs=[Path(__file__),BASE/sourcebatch/'result.json'];assert digest(refs[-1].read_bytes())==boundary.COMPOSITION_SHA
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 parentpath=ROOT/'3d-viewer'/receipt['parentURL'];prior=take(parentpath);assert digest(parentpath.read_bytes())==boundary.PARENT_SHA;members={};nodes={};out.mkdir()
 old_overlap=prior['patches'][16]['nativeMesh']['sourceOverlap'];auditpath=ROOT/old_overlap['evidencePath'];assert digest(auditpath.read_bytes())==old_overlap['evidenceSHA256'];audit=read(auditpath);refs.append(auditpath);sources=[];stale_context=[]
 for item in audit['source']['files']:
  path=ROOT/item['path'];actual=digest(path.read_bytes())
  if actual!=item['sha256']:
   assert item['path']=='3d-viewer/city/data/manifest.json';stale_context.append(dict(path=item['path'],historicalSHA256=item['sha256'],currentSHA256=actual));continue
  sources.append(path);refs.append(path)
 assert len(stale_context)==1
 producer=module('one_peking_retained_overlap_producer',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');producer.DOC=out/'retained-69025-overlap';fresh=copy.deepcopy(prior['patches'][16]);producer.overlap_proof(fresh,[*sources,Path(__file__)])
 old=copy.deepcopy(prior['patches'][16]);new=copy.deepcopy(fresh);old['nativeMesh'].pop('sourceOverlap');new['nativeMesh'].pop('sourceOverlap');assert old==new
 freshpath=out/'retained-69025-overlap'/'metadata-refreshed-node.json';save(freshpath,fresh);refresh=dict(childIndex=16,candidate=dict(path=str(freshpath.relative_to(ROOT)),sha256=digest(freshpath.read_bytes())));refs.append(freshpath)
 for name,record in receipt['members'].items():
  source=take(ROOT/record['candidate']['path']);node=boundary.refined_new_metadata(source,prior)if name=='new-root'else copy.deepcopy(source)
  roundoff=boundary.declare_roundoff(node);save(out/(name+'-roundoff-proof.json'),roundoff)
  assert all(node['nativeMesh'][f]==source['nativeMesh'][f]for f in ['position','index']);path=out/(name+'-unmarked.json');save(path,node);refs.append(path);members[name]=dict(candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),canonicalSHA256=boundary.nested.canonical_sha(node));nodes[name]=node
 proof=dict(policy=boundary.POLICY,parent=dict(path=str(parentpath.relative_to(ROOT)),sha256=boundary.PARENT_SHA),composition=dict(path=str((BASE/sourcebatch/'result.json').relative_to(ROOT)),sha256=boundary.COMPOSITION_SHA),members=members,retainedOverlapRefresh=refresh);proofpath=out/'cycle-proof.json';save(proofpath,proof);ref=dict(path=str(proofpath.relative_to(ROOT)),sha256=digest(proofpath.read_bytes()));refs.append(proofpath);successor=copy.deepcopy(prior);successor['patches'][16]=fresh
 for name,node in nodes.items():
  node=copy.deepcopy(node);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=boundary.POLICY,proof=ref,member=name)
  if name=='new-root':successor['patches'].append(node)
  else:successor['patches'][int(name.split('-')[1])]=node
 successor['meta']['targetUids']=sorted(set(prior['meta']['targetUids'])|boundary.OWNERS);loaded=boundary.load(ref,successor);retention=boundary.verify_parent(loaded[1],successor,proof,loaded[2],ref);boundary.validate_effective(successor['patches'])
 # Boundary callbacks are nominated by the unchanged nested validator; coverage,
 # parent/root heights, refined grids and child overlaps still run in full.
 status='private-cycle-validator-passed';failure=None
 try:
  with boundary.private_validator():boundary.validator.validate_patch(successor,read(ROOT/'3d-viewer/city/data/terrain.json'))
 except AssertionError as error:status='private-cycle-validation-investigation';failure=str(error)
 path=out/'unapproved-successor-terrain.json';save(path,successor);refs.append(path);manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==receipt['currentManifestSHA256'];refs.append(manifest)
 result=dict(uids=receipt['uids'],currentManifestSHA256=receipt['currentManifestSHA256'],status=status,terrainValidatorPassed=status=='private-cycle-validator-passed',failure=failure,retention=retention,allThreeFiniteEdgesBound=True,candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),replacedNativeTerrain=[dict(url=receipt['parentURL'],sha256=boundary.PARENT_SHA,retainedUids=prior['meta']['targetUids'])],newlyDerivedTerrainWorkFaces=sum(r['afterFaces']-r['beforeFaces']+r['changedParentFaces']for r in receipt['members'].values()),metadataRefinementChangedRenderedGeometry=False,roundoffDeclarationChangedRenderedGeometry=False,retainedOverlapRefreshChangedRenderedGeometry=False,staleManifestContext=stale_context,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False)
 save(out/'summary.json',result);refs.extend([HERE/'one_peking_nested_cycle_boundary_v3_20261101.py',HERE/'fuying_whole_parent_five_boundary_v1_20261029.py',HERE/'finite_native_boundary_strip_v1_20261023.py',HERE/'coordinated_native_boundary_v1_20261023.py',HERE/'nested_native_terrain_validation_v1_20261027.py',HERE/'nested_terrain_patch_validation_v1_20261027.py',HERE/'nested_coordinated_native_boundary_v1_20261027.py',HERE/'float32_coverage.py',HERE/'native_patch_resolution.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',ROOT/'3d-viewer/city/data/terrain.json']);module('one_peking_cycle_preparation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-parent-three-edge-cycle-private-surface-admission',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
