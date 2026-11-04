"""Exact original Garden Terrace assembly and unchanged installed neighbour boundary."""
from original_supported_catalogue_scope_v1_20261024 import verify as verify_supports

SOURCES = {
    'landsd/109491:0': 'd6f60c07b429bd89b7c45b09f3a3077960ecbd96898c833684a564d1a4fb9f2e',
    'landsd/162285:0': '331e11c7d4e5834397430c9b10d10e753f550e080f398c75d8b390741ebc1cbd',
    'landsd/21894:0': 'ea3b2a1531c7cce1f1d3915bc3014bc5eab2f0cef807fe3f581bf9f1320f4e5f',
}
PARENT = 'landsd/162285:0'
SUPPORTS = {u: PARENT for u in ['landsd/109491:0', 'landsd/21894:0']}
RETAINED = {'landsd/304714:0'}
RETAINED_SHA = 'f06178309a08955ef93e0d5424e864075632670d3bb2902d3c7d9aaee933beca'
PAIRS = {('landsd/109491:0', 'landsd/304714:0'), (PARENT, 'landsd/304714:0')}
MODES = {'original', 'literal', 'leftF32', 'balancedF32'}


def verify_metadata(models):
    assert verify_supports(models, SOURCES, SUPPORTS)
    for model in models:
        assert model['rootTranslation'] == [-834500, 0, 816500]
        assert model.get('verticalPlacementOffsetHKPD', 0) == 0
        for field in ['retainedBasicSupportDependencies', 'sourceWorldBounds', 'partialSource',
                      'partialGeometry', 'embeddedModel', 'embeddedModels', 'renderGroups',
                      'suppressesBuildingUids']:
            assert not model.get(field)
    return True


def verify_native_scope(scope, native, current):
    assert len(current) == 6881 and not set(SOURCES) & set(current)
    assert set(scope['uids']) == set(SOURCES) and len(scope['rows']) == 3
    nominated = set()
    for row in scope['rows']:
        assert row['sourceSHA256'] == SOURCES[row['uid']]
        assert row['currentNativeActorsChecked'] == 6881
        for actor in row['nearbyNativeActors']:
            assert actor['uid'] in RETAINED
            assert actor['sourceSHA256'] == current[actor['uid']]['sha256'] == RETAINED_SHA
            nominated.add(actor['uid'])
    assert nominated == RETAINED
    assert len(native['rows']) == 2
    assert {(r['uid'], r['nativeUid']) for r in native['rows']} == PAIRS
    for row in native['rows']:
        entry = current[row['nativeUid']]
        assert entry == row['rawCurrentNativeEntry']
        assert entry['sha256'] == row['nativeSHA256'] == RETAINED_SHA
        assert row['sourceSHA256'] == SOURCES[row['uid']]
        assert not entry.get('supportDependencies') and not entry.get('retainedBasicSupportDependencies')
        assert len(row['modes']) == 4 and {r['mode'] for r in row['modes']} == MODES
        for measured in row['modes']:
            assert measured['areaContactPairs'] == 0
            assert measured['positiveSurfaceContactPairs'] == (62 if row['uid'] == PARENT else 0)
    return True
