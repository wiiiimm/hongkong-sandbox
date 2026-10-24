"""Exact Ever Court boundary-retention contract; no new general overlap exception."""
UID = 'landsd/158003:0'
NATIVE = 'landsd/266918:0'
TERRAIN = 'city/data/government-native-mongkok-original-v1-20261021.json'


def merge(model_forms, terrain_forms, scope, neighbours, resolution):
    assert scope['uids'] == [UID] and scope['currentNativeActors'] == 6911
    assert scope['regionalParentExtent'] == [1162.5, -4237.5, 1232.5, -4097.5]
    assert scope['touchingNativeUids'] == [NATIVE]
    assert scope['positiveAreaTerrainOverlaps'] == 0
    assert len(scope['terrainContacts']) == 1
    contact = scope['terrainContacts'][0]
    assert contact['url'] == TERRAIN
    assert contact['extent'] == [1232.5, -4377.5, 1512.5, -4167.5]
    assert contact['coarseOverlapAreaM2'] == 0 and contact['packedContacts']
    assert all(p['overlapAreaM2'] == 0 for p in contact['packedContacts'])
    assert len(terrain_forms) == len({f['uid'] for f in terrain_forms}) == scope['intersectingForms'] == 25
    forms = {f['uid']: f for f in terrain_forms}
    assert UID in forms and NATIVE in forms
    assert model_forms and set(model_forms) <= set(forms)
    assert all(k == f['uid'] and f == forms[k] for k, f in model_forms.items())
    assert neighbours['uids'] == resolution['uids'] == [UID]
    assert neighbours['forms'] == 25
    assert neighbours['requiredNativeUids'] == neighbours['nativeResolved'] == [NATIVE]
    assert len(neighbours['nativeRows']) == 1
    native = neighbours['nativeRows'][0]
    assert native['uid'] == NATIVE and native['passed'] and native['triangles'] == 63844
    t = native['terrain']
    assert t['newlyWhollyBuried'] == t['newlyUpwardWhollyBuried'] == t['maximumBurialIncrease'] == 0
    assert t['minimumGapBefore'] == t['minimumGapAfter']
    assert t['whollyBuriedBefore'] == t['whollyBuriedAfter']
    assert t['upwardWhollyBuriedBefore'] == t['upwardWhollyBuriedAfter']
    assert resolution['rawBasicFlagsPreserved'] == neighbours['basicFlags']
    assert resolution['allBasicFlagsResolved'] and resolution['allRetainedNativeChecksPassed']
    assert not resolution['remainingBasicFlags']
    assert len(resolution['proofs']) == len(neighbours['basicFlags']) == 2
    assert {p['uid']: p['supportUid'] for p in resolution['proofs']} == {
        'landsd/263574:0': 'landsd/227319:0', 'landsd/263773:0': 'landsd/226694:0'}
    for proof in resolution['proofs']:
        assert proof['ownerForm'] == forms[proof['uid']] and proof['supportForm'] == forms[proof['supportUid']]
        assert proof['footprintCoverage'] >= .9999 and abs(proof['unchangedVerticalGap']) <= .1
        assert proof['horizontalToleranceMetres'] == .002
    assert {p['uid'] for p in neighbours['basicFlags']} == {p['uid'] for p in resolution['proofs']}
    assert all(p['reasons'] == ['increased-neighbour-ground-gap'] for p in neighbours['basicFlags'])
    return forms


def retained_views(views, current, width):
    assert len(views) == 2 and width in [390, 1280]
    assert {(v['uid'], v['width'], v['time']) for v in views} == {(NATIVE, width, t) for t in ['15:00', '22:00']}
    model = current[NATIVE]
    for v in views:
        assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
        assert v['sourceSHA256'] == model['sha256'] and v['originalTriangles'] == model['triangles'] == 63844
        assert v['meshVisibility'] and all(v['meshVisibility'])
        assert v['wireframeFlags'] and not any(v['wireframeFlags'])
    return True
