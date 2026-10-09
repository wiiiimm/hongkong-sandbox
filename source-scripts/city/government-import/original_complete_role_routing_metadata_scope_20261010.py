"""Archival source-provenance pointers inside a complete frozen current role.

Role/core/source/ground/actor evidence remains fully numeric and recursive.
Only a manifest entry's original acquisition metadata receives a boundary.
"""
from original_disjoint_routing_metadata_scope_20261010 import boundaries,canonical,subtree

def role_boundaries(role,manifest,candidates,*,candidate_ref,manifest_ref,expected_uids):
 assert expected_uids==sorted(set(expected_uids)) and expected_uids
 assert role['uids']==expected_uids and role['independentPhysicalChecksPassed'] is True and role['unresolvedIndependentPhysicalReasons']==[]
 assert role['installationApproved'] is False and role['publication'] is False and role['sourceGeometryChanges']==0
 assert role['completeOriginalFaces']>0 and role['completeOriginalComponents']>0
 assert manifest_ref==dict(path='3d-viewer/city/data/manifest.json',sha256=role['manifestSHA256']) and manifest_ref in role['evidenceRefs']
 assert candidate_ref['path'].startswith('docs/astra-city/government-import/') and candidate_ref['path'].endswith('/terrain-candidates.json') and candidate_ref in role['evidenceRefs']
 assert len(candidate_ref['sha256'])==64 and all(c in '0123456789abcdef' for c in candidate_ref['sha256'])
 assert len(candidates)==1 and candidates[0]['uids']==expected_uids and not candidates[0].get('replaces') and not candidates[0].get('replacesMany')
 candidate=candidates[0];assert candidate['path'].startswith('source-scripts/city/government-import/local/') and len(candidate['sha256'])==64 and candidate['triangles']>0
 preflight=dict(immutableTerrainProposal=candidate,completeCurrentTerrainRouting=role['completeCurrentTerrainRouting'])
 return [dict(**row,documentType='complete-current-original-role-routing-provenance-v1',boundCandidateRef=candidate_ref,boundCandidateUIDs=expected_uids,boundCandidateSHA256=candidate['sha256'],boundCandidateBounds=candidate['bounds'],boundManifestRef=manifest_ref) for row in boundaries(preflight,manifest)]

def verify_role_boundaries(role,manifest,candidates,declared,*,candidate_ref,manifest_ref,expected_uids):
 expected=role_boundaries(role,manifest,candidates,candidate_ref=candidate_ref,manifest_ref=manifest_ref,expected_uids=expected_uids);assert declared==expected
 for row in declared:assert canonical(subtree(role,row['pointer']))==row['canonicalSHA256']
 return {row['pointer'] for row in declared}
