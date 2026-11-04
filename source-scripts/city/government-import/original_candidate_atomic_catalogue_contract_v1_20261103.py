"""Validate the exact tested candidate-native representation of atomic originals.

The publisher and runtime already classify candidate/installed as native. Only
an in-memory copy is normalized for the existing strict original-entry contract;
tested catalogue bytes remain untouched. This grants no acceptance or approval.
"""
from copy import deepcopy
from original_coordinated_retained_contract_v1_20261027 import verify_metadata
from primrose_compound_foundation_v2_20261015 import module
from run import HERE


def verify(models, sources, supports, original_entries, ground_owners):
    assert supports and len(models) == len(sources)
    assert len({m['uid'] for m in models}) == len(models)
    normalized = deepcopy(models)
    dependency = module('candidate_atomic_canonical_dependency_rows', HERE.parent/'island-detail-integration/model_dependencies.py')
    for tested, model in zip(models, normalized):
        if model['uid'] in supports:
            assert len(model['supportDependencies']) == 1
            assert model['supportDependencies'][0]['state'] == 'candidate'
            model['supportDependencies'][0]['state'] = 'installed'
        else:
            assert model.get('supportDependencies', []) == []
            if 'supportDependencies' not in original_entries[model['uid']]:
                model.pop('supportDependencies', None)
        assert dependency.dependency_rows(tested) == dependency.dependency_rows(model)
    return verify_metadata(normalized, sources, supports, original_entries, ground_owners)
