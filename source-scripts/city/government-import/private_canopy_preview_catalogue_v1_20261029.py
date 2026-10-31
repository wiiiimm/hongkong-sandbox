"""Apply one source-bound, explicitly unapproved private canopy experiment."""
from copy import deepcopy

def apply(models,sources,forms,review):
    assert review['privateCanopyExperimentApproved']is True
    assert review['installationApproved']is False and review['publication']is False
    uid,basic,sha=review['sourceUid'],review['basicUid'],review['sourceSHA256']
    assert uid in sources and sources[uid]==sha and basic not in sources and uid!=basic
    assert forms[basic]==review['exactBasicForm']and forms[basic]['structureType']=='Open-sided Structure'
    assert forms[basic]['baseHeightHKPD']is None and forms[basic]['topHeightHKPD']is None and forms[basic]['heightSource']=='estimated'
    assert review['proposedSuppression']==dict(ownerUid=uid,sourceSHA256=sha,suppressesBuildingUids=[basic],onlyWhileExactOwnerActive=True)
    out=deepcopy(models);assert {m['uid']:m['sha256']for m in out}==sources
    for model in out:
        assert not model.get('suppressesBuildingUids')
        assert all(model[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
    owner=next(m for m in out if m['uid']==uid);owner['suppressesBuildingUids']=[basic]
    return out
