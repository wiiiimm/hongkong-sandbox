"""Exact June Garden proposal-only retained terrain interpretation; no publisher approval.

Preserves both pre-existing source/support failures. One pair has identical
rendered terrain; the other source stays wholly above every old/new terrain
facet and its unchanged installed support passes the current full regression.
This never approves the old source/support interface or bypasses publisher checks.
"""
import argparse, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
CHECKS = 'government-xl-tower3-227380-chain-current-checks-v1-20261102'
PATCH = 'government-xl-tower3-227380-retained-chain-validated-v4-20261102'
PHYSICAL = 'government-xl-tower3-june-garden-six-original-physical-review-v2-20261102'
EXACT = 'government-xl-tower3-227380-flagged-originals-v1-20261102-retained-177605-0'
DISTANT = 'government-xl-tower3-retained-distant-support-v1-20261102-20270-0'
PAIRS = {'landsd/177605:0':'landsd/177604:0','landsd/20270:0':'landsd/159422:0'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True); p.add_argument('--resources-plan',required=True)
    p.add_argument('--owned',action='store_true'); a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out = BASE/a.batch; pp = (ROOT/a.resources_plan).resolve(); assert pp.is_relative_to(BASE)
    resources = read(pp)['resources']; lp = HERE/'local'/a.batch/'reservation.json'
    if not a.owned:
        assert not out.exists() and not lp.parent.exists()
        claim = reservations.claim('june-retained-context-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease = read(lp); assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    refs, pins = [Path(__file__),pp], {}
    def take(batch,name='summary.json'):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]; refs.append(BASE/batch/'result.json')
        path = BASE/batch/name; assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    physical = take(PHYSICAL,'ROOT-PHYSICAL-REVIEW.json'); selected = set(physical['uids'])
    assert physical['sourceSpecificPhysicalInterpretationAccepted'] and len(selected) == 6
    manifest = ROOT/'3d-viewer/city/data/manifest.json'; before = digest(manifest.read_bytes())
    assert before == physical['currentManifestSHA256']; refs.append(manifest)
    current = {}
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT/'3d-viewer'/url; refs.append(path)
        for row in read(path)['models']:
            assert row['uid'] not in current; current[row['uid']] = row
    assert len(current) == 7095 and not selected & set(current)
    scope = take(CHECKS+'-scope','scope.json'); n = take(CHECKS+'-neighbours')
    required = set(n['requiredNativeUids']); native = {r['uid']:r for r in n['nativeRows']}
    assert len(native) == len(n['nativeRows']) == len(required) == 69
    assert required == set(native) == set(scope['touchingNativeUids'])
    assert {'building:'+u for u in required|selected} <= set(resources)
    assert n['forms'] == 786 and {r['uid'] for r in n['basicFlags']} <= selected
    assert {u for u,r in native.items() if not r['passed']} == set(PAIRS)
    contexts = {u:take(EXACT if u == 'landsd/177605:0' else DISTANT) for u in PAIRS}
    for uid,c in contexts.items():
        assert c['nativeUid'] == uid and c['supportUid'] == PAIRS[uid]
        assert not c['existingNativeReaccepted'] and not c['rawSupportPolicyPassed']
        assert c['rawNativeRegression'] == native[uid]
        rows = {r['uid']:r for r in c['rows']}; assert set(rows) == {uid,PAIRS[uid]}
        for u,r in rows.items():
            assert r['sourceSHA256'] == current[u]['sha256']
            assert r['rootCoarseMaskUnchangedAcrossCompleteBounds']
        if uid == 'landsd/177605:0':
            assert c['proposalTerrainNonRegressionProved']
            assert all(r['exactRenderedTerrainMultisetUnchanged'] for r in rows.values())
        else:
            assert c['terrainDistantSourceContextProved'] and not c['proposalTerrainNonRegressionProved']
            source, support = rows[uid], rows[PAIRS[uid]]
            assert all(r['sourceGeometryAndPoseUnchanged'] for r in rows.values())
            assert source['minimumConservativeClearanceM'] > 2
            assert source['sourceMinimumHeight'] > max(source['beforeCompleteFacetMaximumHeight'],source['afterCompleteFacetMaximumHeight'])+2
            assert source['terrainRelevantBefore'] is source['terrainRelevantAfter'] is False
            assert support['currentFullNativeRegressionPassed'] and support['rawNativeRegression'] == native[PAIRS[uid]]
    reviews = []
    for uid,raw in native.items():
        t = raw['terrain']
        assert t['newlyWhollyBuried'] == t['newlyUpwardWhollyBuried'] == 0
        if uid in PAIRS:
            assert t['maximumBurialIncrease'] == 0 and t['minimumGapBefore'] == t['minimumGapAfter']
            assert t['whollyBuriedBefore'] == t['whollyBuriedAfter']
            assert t['upwardWhollyBuriedBefore'] == t['upwardWhollyBuriedAfter']
        reviews.append(dict(uid=uid,proposalTerrainNonRegressionPassed=True,raw=raw,
            basis='unchanged-terrain' if uid == 'landsd/177605:0' else ('terrain-distant-unchanged-source-and-current-passing-support' if uid in PAIRS else 'current-full-native-regression'),
            existingSourceReapproved=False,existingSupportReapproved=False))
    proposal,pins[PATCH] = authenticate(BASE/PATCH); refs.append(BASE/PATCH/'result.json')
    assert proposal['allEffectiveMembersRequired'] and len(proposal['members']) == 3
    for member in proposal['members']:
        for path,sha in [(ROOT/member['candidate']['path'],member['candidate']['sha256']), (ROOT/'3d-viewer'/member['replaces']['url'],member['replaces']['sha256'])]:
            assert digest(path.read_bytes()) == sha; refs.append(path)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == before
    summary = dict(uids=sorted(selected),currentManifestSHA256=before,retainedNativeActors=69,
        basicForms=786,replacedBasicFlagUids=sorted(r['uid'] for r in n['basicFlags']),
        rows=reviews,proposalTerrainNonRegressionPassed=True,rawSupportFailuresPreserved=sorted(PAIRS),
        terrainWidePublicationReviewApproved=False,visualAcceptance=False,installationApproved=False,
        publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification=__doc__)
    save(out/'summary.json',summary)
    module('june_retained_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-june-garden-retained-terrain-context-reviewed',refs,summary)


if __name__ == '__main__': main()
