"""Only review metadata may change between tested and installed catalogues."""
from copy import deepcopy
MODEL_REVIEW_FIELDS={'sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview'}
TOP_REVIEW_FIELDS={'kind','diagnosticOnly','physicalAcceptance','publicationApproved'}

def verify_catalogue_review(original, approved):
    assert len(original['models'])==len(approved['models'])>0
    stripped=deepcopy(approved)
    for field in TOP_REVIEW_FIELDS:
        if field in original:stripped[field]=original[field]
        else:stripped.pop(field,None)
    for model,old in zip(stripped['models'],original['models']):
        assert model['uid']==old['uid'] and not model.get('supportDependencies') and not model.get('suppressesBuildingUids')
        assert model['proceduralWindows']is False
        assert all(model[k]is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
        assert model['aiGeometryModelling']is False
        for key in MODEL_REVIEW_FIELDS:
            if key in old:model[key]=old[key]
            else:model.pop(key,None)
    assert stripped==original,'Rendering/source metadata changed after the private browser'
    assert approved['kind']=='official-model-catalogue' and approved['diagnosticOnly']is False
    assert approved['physicalAcceptance']is True and approved['publicationApproved']is True
    return True
