"""Positive terrain/publisher binding for exact One Peking nested-cycle sources.
No CLI, source approval or publication call. Ordinary publisher source/dependency,
retained-support, replacement, review, transaction and rollback checks stay intact.
"""
from pathlib import Path
from run import ROOT,HERE,read,digest
from primrose_compound_foundation_v2_20261015 import module
import one_peking_nested_cycle_boundary_v2_20261101 as boundary
from original_coordinated_retained_contract_v1_20261027 import verify_metadata,verify_retained_entries,verify_native_interfaces
SOURCES={'landsd/233985:0':'73c65ee4568e2feb34e51e379db43a189824eb71eebba995b13de9d5456e9331','landsd/240487:0':'d075d9ad511e0ccd6b84a49eedb68542422cbc70356ffd46a384100c183c11e1'}
SUPPORTS={'landsd/240487:0':'landsd/233985:0'}

def verify_terrain(prior,candidate,patch,current_sha,new_sha,current_manifest_sha):
 assert patch['status']=='private-cycle-validator-passed'and patch['terrainValidatorPassed']is True
 assert patch['currentManifestSHA256']==current_manifest_sha and patch['candidate']['sha256']==new_sha
 assert set(patch['uids'])==set(SOURCES) and len(patch['replacedNativeTerrain'])==1
 old=patch['replacedNativeTerrain'][0];assert old['sha256']==current_sha==boundary.PARENT_SHA
 assert old['retainedUids']==prior['meta']['targetUids']
 assert patch['sourceGeometryChanges']==patch['sourcePoseChanges']==0
 assert patch['metadataRefinementChangedRenderedGeometry']is False and patch['retainedOverlapRefreshChangedRenderedGeometry']is False
 assert patch['newlyDerivedTerrainWorkFaces']==5773<=25000
 own=boundary.marker(candidate['patches'][12]);assert own and own['policy']==boundary.POLICY
 proof,bound_prior,members,edges=boundary.load(own['proof'],candidate)
 assert proof['parent']['sha256']==current_sha and boundary.nested.reference(proof['parent'])==prior
 assert len(edges)==3 and len(candidate['patches'])==len(prior['patches'])+1==18
 assert set(candidate['meta']['targetUids'])==set(prior['meta']['targetUids'])|set(SOURCES)
 checked=boundary.verify_parent(bound_prior,candidate,proof,members,own['proof'])
 assert checked==patch['retention'] and checked['retainedChildren']==14 and checked['metadataOnlyOverlapRefreshChild']==16
 boundary.validate_effective(candidate['patches'])
 return dict(**checked,allThreeFiniteEdgesRequired=True,allRetainedTargetsPreserved=True,retainedUids=old['retainedUids'],sourceGeometryChanges=0,sourcePoseChanges=0)

def publisher(name,prior_path,candidate_path,sources,supports,patch):
 assert sources==SOURCES and supports==SUPPORTS
 prior_path,candidate_path=Path(prior_path).resolve(),Path(candidate_path).resolve()
 assert prior_path.is_relative_to(ROOT)and candidate_path.is_relative_to(ROOT)
 assert str(candidate_path.relative_to(ROOT))==patch['candidate']['path']
 prior,candidate=read(prior_path),read(candidate_path);manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes())
 retention=verify_terrain(prior,candidate,patch,digest(prior_path.read_bytes()),digest(candidate_path.read_bytes()),manifest_sha)
 canonical=module(name,HERE.parent/'island-detail-integration/publish.py');ordinary=canonical.validate_patch
 rootpath=ROOT/'3d-viewer/city/data/terrain.json';root_sha=digest(rootpath.read_bytes());root=read(rootpath)
 def validate(node,parent):
  if node==candidate:
   assert digest(manifest.read_bytes())==manifest_sha and digest(rootpath.read_bytes())==root_sha and parent==root
   assert digest(prior_path.read_bytes())==boundary.PARENT_SHA and digest(candidate_path.read_bytes())==patch['candidate']['sha256']
   verify_terrain(prior,node,patch,digest(prior_path.read_bytes()),digest(candidate_path.read_bytes()),manifest_sha)
   with boundary.private_validator():boundary.validator.validate_patch(node,parent)
  else:ordinary(node,parent)
 canonical.validate_patch=validate
 return canonical,retention
