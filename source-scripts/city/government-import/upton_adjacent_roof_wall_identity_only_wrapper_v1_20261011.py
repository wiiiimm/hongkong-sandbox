"""UNEXECUTED wrapper of ROOT's narrow source-identification interpretation.

Existing tested draft and both ordinary policies are unchanged. Never a physical
foreign exception, intended joint, shared edge, solid clearance or root proof.
"""
from copy import deepcopy
import upton_adjacent_original_roof_wall_identity_context_draft_v1_20261011 as draft
POLICY='upton-exact-original-named-adjacent-roof-wall-source-identity-v1'
FOREIGN_POLICY='original-routed-georef-cell-exact-finite-facet-coverage-v1'

def apply_identity_only(root,own_raw,foreign_raw,foreign_owned,forms,current,context,triangles):
 proposed=draft.assess_draft(root,own_raw,forms,current,context,triangles)
 assert foreign_raw['uid']==draft.ADJACENT and foreign_raw['policy']==FOREIGN_POLICY
 assert foreign_raw['sourceSHA256']==draft.EXACT[draft.ADJACENT][0] and foreign_raw['worldTrianglesSHA256']==draft.EXACT[draft.ADJACENT][1]
 assert foreign_raw['exactRouteManifestSHA256']==current['manifestSHA256']
 assert foreign_raw['originalOwnership']['sourceGraphVerified'] and foreign_raw['modelGeometryChanges']==0
 assert foreign_raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==392
 assert foreign_raw['exactWholeCellCoverage']['covered'] and len(foreign_raw['exactWholeCellCoverage']['halves'])==2
 for h in foreign_raw['exactWholeCellCoverage']['halves']:
  assert h['completeOriginalGroundTrianglesAccounted']==392 and h['completeGroundSHA256']==draft.EXACT[draft.ADJACENT][1] and h['exactProjectionCovered'] and h['exactUncoveredAreaM2']=='0' and h['noToleranceOrBufferCredit']
 assert foreign_raw['passed'] and foreign_raw['reasons']==[], 'Foreign actor needs its existing unchanged full-cell proof, not a new waiver'
 assert foreign_owned['uid']==draft.ADJACENT and foreign_owned['sourceSHA256']==draft.EXACT[draft.ADJACENT][0]
 # Existing full-cell route may replace only cached shape proxies; never turn an
 # arbitrary failing owned proof into a second source-specific exception.
 assert set(foreign_owned['reasons'])<= {'cached-spatial-officialCandidates','cached-spatial-officialMatches','cached-spatial-viewerMatches'}
 assert set(foreign_raw['cachedShapeProxyReasonsReplaced'])==set(foreign_owned['reasons'])
 passed=proposed['draftContextQualified']
 out=deepcopy(own_raw)
 out.update(policy=POLICY,passed=passed,reasons=deepcopy(proposed['proposedIdentityReasons']),rawOrdinaryIdentityRetained=deepcopy(own_raw),acceptedSourceIdentificationInterpretationOnly=True,identityContext=proposed,identityAccepted=passed,proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},foreignFullCellIdentityRetained=deepcopy(foreign_raw),foreignOwnedProxyNegativesRetained=deepcopy(foreign_owned),physicalAccepted=False,installationApproved=False,foreignCollisionExemption=False,foreignTerrainExemption=False,sharedEdgeCredit=False,rootCredit=False,solidClearanceCredit=False,intentionalJointEstablished=False,engineeringOrLegalClaim=False,modelGeometryChanges=0,qualification='ROOT accepted only identification of the unchanged12728 source as Upton podium with named adjacent original12662 roof/wall context. This does not resolve23 actual original face-interior crossings or physical/terrain/support/current-four-world obligations. Foreign12662 uses only its existing fresh full-cell route; cached proxy negatives remain. No intended joint, common ownership, precise shared edge, root, solid, legal or engineering inference.')
 return out
