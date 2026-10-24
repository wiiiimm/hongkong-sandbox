"""Closed catalogue-entry contract for the exact reviewed podium/two-tower originals."""
from copy import deepcopy
from run import ROOT,read,digest
from original_supported_catalogue_scope_v1_20261024 import verify as verify_supports
SOURCES={'landsd/84014:0':'2f0657211c031b7a4744fa4c1f0397511d1f43e2160919d3ea885eaf12354d80','landsd/155042:0':'709128d4fc6bb2d963ea6309591ff6e7139e783930dc1f5ff606ad5abd4476f0','landsd/269721:0':'368998781f636a151356de6f08a92aa58cc1a80e53b298ec14b43abd68db7be2'}
SUPPORTS={'landsd/155042:0':'landsd/84014:0','landsd/269721:0':'landsd/84014:0'}
BASELINE=ROOT/'source-scripts/city/government-import/local/government-xl-84014-three-original-private-browser-v1-20261025/catalogue.json'
BASELINE_SHA='575a468316fe0dbe1f8be78bc50460dc7f1ced1ab1440af21f759128aee43fc3'
REVIEW_FIELDS={'sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview'}


def verify_metadata(models):
    assert digest(BASELINE.read_bytes())==BASELINE_SHA
    expected={m['uid']:m for m in read(BASELINE)['models']}
    assert verify_supports(models,SOURCES,SUPPORTS)
    for m in models:
        assert m['rootTranslation']==[-834500,0,816500]
        assert not m.get('retainedBasicSupportDependencies')and not m.get('suppressesBuildingUids')
        a,b=deepcopy(m),deepcopy(expected[m['uid']])
        for key in REVIEW_FIELDS:a.pop(key,None);b.pop(key,None)
        assert a==b,'Rendering/source metadata differs from the exact tested private catalogue'
    return True
