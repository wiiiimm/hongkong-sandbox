"""Compose unchanged scalar canopy guards with an exact multi-canopy lifecycle."""
from copy import deepcopy
from conditional_canopy_install_contract_v1_20261029 import verify as verify_one


def verify(models, review, physical, lifecycle, features, forms):
    assert len(models) == 1
    replacements = review['conditionalCanopyReplacements']
    assert replacements == physical['conditionalCanopyReplacements']
    assert 1 < len(replacements) <= 8 and len(features) == len(replacements)
    basics = [r['basicUid'] for r in replacements]
    assert len(basics) == len(set(basics)) and models[0]['suppressesBuildingUids'] == basics
    assert [f['basicUid'] for f in features] == basics
    for case in lifecycle['cases']:
        for row in case['canopyLifecycle']:
            assert set(row) == {'phase', 'ownerActive', 'canopies'}
            assert [c['uid'] for c in row['canopies']] == basics
            assert all(set(c) == {'uid', 'basicCanopyVisible'} for c in row['canopies'])
    proofs = []
    for replacement, feature in zip(replacements, features):
        basic = replacement['basicUid']
        model = deepcopy(models[0])
        model['suppressesBuildingUids'] = [basic]
        source = {**review, 'conditionalCanopyReplacement': replacement}
        body = {**physical, 'conditionalCanopyReplacement': replacement}
        phases = deepcopy(lifecycle)
        for case in phases['cases']:
            case['canopyLifecycle'] = [dict(phase=r['phase'], ownerActive=r['ownerActive'],
                basicCanopyVisible=next(c['basicCanopyVisible'] for c in r['canopies'] if c['uid'] == basic)) for r in case['canopyLifecycle']]
        proofs.append(verify_one([model], source, body, phases, feature, forms))
    return dict(sourceUid=models[0]['uid'], sourceSHA256=models[0]['sha256'], basicUids=basics,
                exactCanopyFeaturesBound=True, completeLifecycleVerified=True,
                scalarProofs=proofs, publication=False)
