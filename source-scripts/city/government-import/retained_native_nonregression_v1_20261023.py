"""A terrain-change decision without reapproving an unchanged installed actor.

Callers must authenticate all input receipts and bind exact old/new terrain mesh
bytes. A legacy support failure remains false in rawNativeRegression.
"""
import copy

def terrain_decision(raw, context, installed):
    assert context['proposalTerrainNonRegressionProved'] is True
    assert context['existingNativeReaccepted'] is False and context['rawSupportPolicyPassed'] is False
    assert context['sourceGeometryChanges'] == 0
    assert context['nativeUid'] == raw['uid'] and context['rawNativeRegression'] == raw
    assert raw['passed'] is False
    terrain = raw['terrain']
    assert terrain['minimumGapBefore'] == terrain['minimumGapAfter']
    assert terrain['maximumBurialIncrease'] == terrain['newlyWhollyBuried'] == terrain['newlyUpwardWhollyBuried'] == 0
    expected = {context['nativeUid'], context['supportUid']}
    rows = context['rows']
    assert len(rows) == 2 and {r['uid'] for r in rows} == expected
    for r in rows:
        assert r['sourceSHA256'] == installed[r['uid']]['sha256']
        assert r['exactRenderedTerrainMultisetUnchanged'] is True
        assert r['completeIntersectingTerrainFaces'] > 0
        assert len(r['completeFourWorldBounds']) == 4
        assert all(len(b) == 2 and all(len(p) == 3 for p in b) for b in r['completeFourWorldBounds'])
    return dict(uid=raw['uid'], passed=True, terrain=copy.deepcopy(terrain),
                qualification='Terrain-change nonregression only: complete rendered terrain face multisets and installed source bytes are unchanged across all four-world bounds of this actor and its existing support. No new support or source approval.',
                rawNativeRegression=copy.deepcopy(raw), rawSupportPolicyPassed=False,
                existingNativeReaccepted=False, exactWholeTerrainUnchanged=True)
