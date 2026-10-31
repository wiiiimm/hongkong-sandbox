"""Exact original pair admission; no source, ground or global-support guard bypass."""
from copy import deepcopy
from peninsula_private_group_roof_contract_v2_20261029 import apply as private_apply
from peninsula_private_group_roof_contract_v1_20261029 import SOURCES,OWNER,TOWER,ROOF,form_sha
PUBLIC_FIELDS=['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview']
def verify(models,review,physical,lifecycle,private_review,forms,*,approved=False):
    assert {m['uid']:m['sha256']for m in models}==SOURCES and len(models)==2
    for decision in [review,physical]:
        assert decision['sourceSHA256ByUid']==SOURCES and all(decision[k]is True for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
        assert decision['sourceGeometryChanges']==decision['sourcePoseChanges']==0 and decision['terrainEdits']is False
        assert decision['activationGroup']==sorted(SOURCES)and decision['supportByUid']=={TOWER:OWNER}
        assert decision['retainedBasicSupportDependencies']==decision['retainedCurrentBasicSupportUids']==[]
    assert review['currentManifest']==physical['currentManifest']==private_review['currentManifest']
    replacement=review['conditionalOsmRoofReplacement'];assert replacement==physical['conditionalOsmRoofReplacement']
    assert replacement==dict(sourceUid=OWNER,basicUid=ROOF,sourceSHA256=SOURCES[OWNER],sourceFormSHA256=form_sha(forms[OWNER]),basicFormSHA256=form_sha(forms[ROOF]),onlyWhileExactOwnerActive=True,approved=True)
    assert lifecycle['passed']is True and lifecycle['sourceSHA256ByUid']==SOURCES and lifecycle['completeAtomicPairAndRoofLifecycleVerified']is True
    assert private_review['sourceSHA256ByUid']==SOURCES and not private_review['publication']and not private_review['installationApproved']
    clean=deepcopy(models)
    for m in clean:
        assert m['activationGroup']==sorted(SOURCES)and m['proceduralWindows']is False and not m.get('retainedBasicSupportDependencies')
        expected=[dict(uid=OWNER,state='installed',buildingCSUID=forms[OWNER]['buildingCSUID'],sha256=SOURCES[OWNER])]if m['uid']==TOWER else []
        assert m.get('supportDependencies',[])==expected
        assert all(m[k]is approved for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
        m.pop('activationGroup');m.pop('suppressesBuildingUids',None);m.pop('reviewedOsmRoofReplacement',None)
        for k in PUBLIC_FIELDS:m.pop(k,None)
        m.update(publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
    replay=private_apply(clean,forms,private_review)
    stripped=deepcopy(models)
    for m in stripped:
        for k in PUBLIC_FIELDS:m.pop(k,None)
        m.update(publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
    assert replay==stripped,'Only reviewed availability/roof declarations and explicit approval fields may differ'
    return dict(sourceSHA256ByUid=SOURCES,exactPairAvailabilityAndConditionalRoofVerified=True,sourceGeometryChanges=0,terrainEdits=False,publication=False)
