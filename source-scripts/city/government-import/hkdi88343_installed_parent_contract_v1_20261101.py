"""Exact HKDI A/platform metadata admission; no generic flag override.

Caller must authenticate the component review and its complete evidence closure.
The legacy parent entry is compared verbatim, never amended for validation.
"""
from copy import deepcopy
from original_installed_support_model_only_contract_v1_20261027 import FORBIDDEN
from original_supported_model_only_contract_v1_20261025 import REVIEW_FIELDS
UID = 'landsd/88343:0'
PARENT = 'landsd/22089:0'
SHA = '98e25a696418680d31f70de499561a68412fc1b08d50ab4e49365ef63adadcc8'
PSHA = '5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40'

def verify_metadata(models, sources, supports, original_entries, current, review):
    assert sources == {UID: SHA} and supports == {UID: PARENT}
    assert set(original_entries) == {UID} and UID not in current and PARENT in current
    assert len(models) == 1 and models[0]['uid'] == UID and models[0]['sha256'] == SHA
    parent = current[PARENT]
    assert parent == review['rawInstalledEntry']
    assert parent['sha256'] == review['sourceSHA256'] == PSHA
    assert parent['objectId'] == 22089 and parent['buildingCSUID'] == '4418318510T20100222'
    assert parent['modelId'] == 'B441831851001063C0'
    assert parent['publicationApproved'] is True and parent['placementReviewed'] is True
    assert parent['identityReviewApproved'] is False and parent['wholeLandmarkAccepted'] is False
    assert not parent.get('supportDependencies') and not any(parent.get(k) for k in FORBIDDEN)
    assert parent.get('verticalPlacementOffsetHKPD', 0) == 0
    assert review['uids'] == [PARENT] and review['sourceComponentIdentityAccepted'] is True
    assert review['wholeLandmarkAccepted'] is False
    assert review['installedMetadataChanges'] == review['sourceGeometryChanges'] == review['sourcePoseChanges'] == review['genericThresholdChanges'] == 0
    assert review['sourceFormSHA256'] == '446f5838577d29e5407190a459e5566dd04a618ae9e6b21cc5eeb84070a08aa1'
    assert review['worldTrianglesSHA256'] == 'ac1f46abeb0bb3924b23d14eb0100ec4901078a2bac3685700969f8351b94788'
    assert all(review['reviewedIdentityProof'][k] is True for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted'])
    assert review['rawIdentityReasonsPreserved'] == ['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM', 'full-source-maximum-extent']
    expected = deepcopy(original_entries[UID])
    assert expected['uid'] == UID and expected['sha256'] == SHA
    assert expected['rootTranslation'] == [-834500, 0, 816500]
    assert expected.get('verticalPlacementOffsetHKPD', 0) == 0
    assert not expected.get('supportDependencies') and not any(expected.get(k) for k in FORBIDDEN)
    expected.update(asset='assets/' + SHA + '.glb.gz', priority='landmark', proceduralWindows=False,
        supportDependencies=[dict(uid=PARENT, state='installed', buildingCSUID=parent['buildingCSUID'], sha256=PSHA)])
    actual = deepcopy(models[0])
    for field in REVIEW_FIELDS:
        expected.pop(field, None)
        actual.pop(field, None)
    assert actual == expected, 'Only the exact unchanged source and reviewed native dependency are admitted'
    return True
