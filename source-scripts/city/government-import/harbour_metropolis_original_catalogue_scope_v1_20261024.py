"""Closed exact-original hotel dependency on its unchanged installed native podium.
This binds reviewed metadata/evidence; it neither approves nor publishes models.
The independent-model zero-contact contract remains unchanged.
"""
UID, PARENT = 'landsd/259378:0', 'landsd/240841:0'
SOURCES = {UID: '1f7f3f42844aa20b23bf30f398b7f67035953c98b1b530d5529c8be4dd4c8034'}
SUPPORTS = {UID: PARENT}
RETAINED = {PARENT}
PARENT_SHA = 'e17d2d53e8d2c8b186f3bbbedf32bd6a8f7121e2d8b598f4b1fe36a65b791bf3'
PARENT_CSUID = '3684418149P20060311'
MODES = {'original', 'literal', 'leftF32', 'balancedF32'}


def verify_support_scope(models, sources, supports):
    assert sources == SOURCES and supports == SUPPORTS
    assert len(models) == 1 and models[0]['uid'] == UID and models[0]['sha256'] == SOURCES[UID]
    expected = [dict(uid=PARENT, state='installed', buildingCSUID=PARENT_CSUID, sha256=PARENT_SHA)]
    assert models[0].get('supportDependencies') == expected
    return True


def verify_metadata(models):
    assert verify_support_scope(models, SOURCES, SUPPORTS)
    m = models[0]
    assert m['rootTranslation'] == [-834500, 0, 816500]
    assert m.get('verticalPlacementOffsetHKPD', 0) == 0
    assert m['proceduralWindows'] is False
    for field in ['retainedBasicSupportDependencies', 'sourceWorldBounds', 'partialSource',
                  'partialGeometry', 'embeddedModel', 'embeddedModels', 'renderGroups',
                  'suppressesBuildingUids']:
        assert not m.get(field)
    return True


def verify_native_scope(scope, native, current):
    assert len(current) == 6895 and UID not in current
    assert PARENT in current and current[PARENT]['sha256'] == PARENT_SHA
    assert current[PARENT]['buildingCSUID'] == PARENT_CSUID
    assert not current[PARENT].get('supportDependencies') and not current[PARENT].get('retainedBasicSupportDependencies')
    # The authenticated capture can include other candidates; the complete hotel
    # row and every one of its neighbours remain mandatory.
    matching = [r for r in scope['rows'] if r['uid'] == UID]
    assert len(matching) == 1 and matching[0]['sourceSHA256'] == SOURCES[UID]
    assert matching[0]['currentNativeActorsChecked'] == len(current)
    actors = matching[0]['nearbyNativeActors']
    assert len(actors) == 1 and actors[0]['uid'] == PARENT and actors[0]['sourceSHA256'] == PARENT_SHA
    assert len(native['rows']) == 1
    row = native['rows'][0]
    assert row['uid'] == UID and row['nativeUid'] == PARENT
    assert row['sourceSHA256'] == SOURCES[UID] and row['nativeSHA256'] == PARENT_SHA
    assert row['rawCurrentNativeEntry'] == current[PARENT]
    modes = row['modes']
    assert len(modes) == 4 and {r['mode'] for r in modes} == MODES
    for r in modes:
        assert r['sourceFaces'] == 14504 and r['nativeFaces'] == 101394 and r['areaContactPairs'] == 15
        fp32 = r['mode'] in {'leftF32', 'balancedF32'}
        assert r['finiteContactPairs'] == (5198 if fp32 else 1398)
        assert r['positiveSurfaceContactPairs'] == (951 if fp32 else 1066)
    return True
