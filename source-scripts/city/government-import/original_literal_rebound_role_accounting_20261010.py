"""Account an immutable full numerical role within a verified unchanged region.

This is not new numerical acceptance; no formerly failed source can use it.
The file adapter must independently pin/read fenced inputs and replay inventory,
full source/literal/F32 bounds, current identities and exact regional hashes.
"""
from copy import deepcopy
from verified_disjoint_manifest_rebind_20261009 import disjoint

def account(role,region,identities,*,expected_owned,expected_retained,protected_scope,old_manifest,current_manifest):
 assert role['currentTypedPhysicalAccepted']is True and role['reasons']==[] and role['sourceGeometryChanges']==0
 assert role['publication']is False and role['newlyInstalled']==0 and role['installationApproved']is False
 assert role['currentManifest']==dict(path='3d-viewer/city/data/manifest.json',sha256=old_manifest)
 assert current_manifest['path']=='3d-viewer/city/data/manifest.json' and current_manifest['sha256']!=old_manifest
 assert role['uids']==sorted(expected_owned) and role['sourceSHA256s']==expected_owned and role['completeOriginalFaces']>0 and role['completeOriginalComponents']>0
 assert region['verifiedDisjointGlobalManifestRebind']is True and region['allFrozenNumericAndSourceInputHashesUnchanged']is True and region['numericAcceptanceRecomputed']is False and region['installationApproved']is False
 assert region['oldManifestSHA256']==old_manifest and region['currentManifestSHA256']==current_manifest['sha256']
 assert region['changedCompleteInventory']
 for change in region['changedCompleteInventory']:
  assert change['kind']in ['terrain','native'] and (change['before']is not None or change['after']is not None)
  for item in [change['before'],change['after']]:
   if item is not None:assert item['id']==change['id'] and disjoint(item['completeWorldXZBounds'],region['completeFrozenRegionWorldXZBounds'])
 assert {r['uid']:r['sourceSHA256']for r in protected_scope if r['kind']=='owned'}==expected_owned
 assert {r['uid']:r['sourceSHA256']for r in protected_scope if r['kind']=='retained-native'}==expected_retained
 assert len(protected_scope)==len(expected_owned)+len(expected_retained) and all(r['allOriginalVerticesAccounted']is True for r in protected_scope)
 box=region['completeFrozenRegionWorldXZBounds']
 for item in protected_scope:
  assert len(item['completeOriginalLiteralAndFloat32Bounds'])==3
  for lo,hi in item['completeOriginalLiteralAndFloat32Bounds']:assert box[0]<=lo[0]<=hi[0]<=box[2] and box[1]<=lo[2]<=hi[2]<=box[3]
 assert len(identities)==len(expected_owned) and len({p['uid']for p in identities})==len(identities)
 for p in identities:assert p['uid']in expected_owned and p['sourceSHA256']==expected_owned[p['uid']] and p['passed']is True and p['reasons']==[] and p['exactRouteManifestSHA256']==current_manifest['sha256']
 out=deepcopy(role);out['contract']=role['contract']+'-source-bound-disjoint-current-replay-v1';out['historicalNumericalAcceptanceManifest']=out['currentManifest'];out['currentManifest']=deepcopy(current_manifest)
 if 'completeCurrentSourceIdentities'in out:out['historicalNumericalSourceIdentities']=out['completeCurrentSourceIdentities'];out['completeCurrentSourceIdentities']=deepcopy(identities)
 if 'currentOwnedIdentity'in out:assert len(identities)==1;out['historicalNumericalOwnedIdentity']=out['currentOwnedIdentity'];out['currentOwnedIdentity']=deepcopy(identities[0])
 out['allOriginalNumericalRolesPreserved']=True;out['newNumericalAcceptanceCredit']=False;out['currentNativeReacceptance']=False
 return out
