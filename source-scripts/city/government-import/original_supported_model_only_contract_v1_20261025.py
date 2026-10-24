"""Exact tested-entry contract for co-imported original supports on unchanged terrain."""
from copy import deepcopy
from original_supported_catalogue_scope_v1_20261024 import verify as support_contract
from original_independent_model_only_contract_v1_20261024 import verify_native_scope

REVIEW_FIELDS = frozenset(['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved',
                          'sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling',
                          'sourceEvidenceInterpretationUsedAI','placementReview'])


def verify_metadata(models, sources, supports, original_entries):
    assert len(sources) >= 2 and supports and set(original_entries) == set(sources)
    assert support_contract(models, sources, supports)
    for model in models:
        uid = model['uid']
        expected = deepcopy(original_entries[uid])
        assert expected['uid'] == uid and expected['sha256'] == sources[uid]
        assert expected['rootTranslation'] == [-834500, 0, 816500]
        assert expected.get('verticalPlacementOffsetHKPD', 0) == 0
        assert not any(expected.get(k) for k in ['sourceWorldBounds','partialSource','partialGeometry',
                       'embeddedModel','embeddedModels','retainedBasicSupportDependencies','suppressesBuildingUids','renderGroups'])
        assert not expected.get('supportDependencies'), 'Canonical unapproved source must not supply its own dependency graph'
        expected.update(asset='assets/'+sources[uid]+'.glb.gz', priority='landmark', proceduralWindows=False)
        if uid in supports:
            parent = supports[uid]
            expected['supportDependencies'] = [dict(uid=parent, state='installed',
                buildingCSUID=original_entries[parent]['buildingCSUID'], sha256=sources[parent])]
        actual = deepcopy(model)
        for key in REVIEW_FIELDS:
            expected.pop(key, None)
            actual.pop(key, None)
        assert actual == expected, 'Rendering metadata differs from the exact reviewed original entry'
    return True
