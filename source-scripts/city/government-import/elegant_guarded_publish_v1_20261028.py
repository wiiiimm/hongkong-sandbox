"""Exact-source, lease-fenced canonical publisher for the reviewed Elegant group.

--prepare-only does not claim a lease or publish. No generic publisher changes.
"""
import argparse
import copy
import sys
from contextlib import contextmanager
from pathlib import Path
import elegant_qualified_stage_v1_20261028 as stage
from run import ROOT, HERE, read, save, digest, connect, reservations, dict_row
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from three_member_native_boundary_v1_20261027 import private_validator

BATCH = stage.P + 'original-installed-v1-20261028'
APPROVAL_KEYS = {'sourceIdentityReviewed', 'identityReviewApproved', 'placementReviewed',
                 'publicationApproved', 'sourceIdentityReview', 'sourceFunctionalApplicability',
                 'placementReview', 'aiGeometryModelling', 'sourceEvidenceInterpretationUsedAI',
                 'sourceHeightDiscrepancyReview'}


def verify_models(original, qualified, source_hashes):
    assert len(original) == len(qualified) == len(source_hashes) == 16
    before = {m['uid']: m for m in original}
    after = {m['uid']: m for m in qualified}
    assert len(before) == len(after) == 16 and set(before) == set(after) == set(source_hashes)
    for uid, model in after.items():
        prior = before[uid]
        assert {k: v for k, v in prior.items() if k not in APPROVAL_KEYS} == {
            k: v for k, v in model.items() if k not in APPROVAL_KEYS}, 'Original runtime metadata changed'
        assert model['sha256'] == source_hashes[uid]
        assert set(model['activationGroup']) == set(source_hashes)
        assert model['rootTranslation'] == [-834500, 0, 816500]
        assert model['proceduralWindows'] is False and model['aiGeometryModelling'] is False
        assert all(model[k] is True for k in ['sourceIdentityReviewed', 'identityReviewApproved',
                                             'placementReviewed', 'publicationApproved'])
        if uid == 'landsd/224123:0':
            assert model['recordedTopHeight'] == 88.7
            assert model['sourceHeightDiscrepancyReview']
    return True


def verify_plan(plan):
    assert set(plan) == {'status', 'areas', 'topLevelTerrainPatches', 'illustrativeFoundations', 'basicPodiumFootings'}
    assert len(plan['areas']) == 1 and len(plan['topLevelTerrainPatches']) == 2
    area = plan['areas'][0]
    assert area['catalogue'] == str((stage.STAGE / 'catalogue.json').relative_to(ROOT))
    assert area['destination'] == 'city/data/official-models/' + stage.BATCH + '/catalogue.json'
    assert not area.get('estimates') and not area.get('terrain')
    assert len(plan['illustrativeFoundations']) == 2 and len(plan['basicPodiumFootings']) == 1
    assert {r['uid'] for r in plan['illustrativeFoundations']} == {'landsd/99061:0', 'landsd/336456:0'}
    assert {r['uid'] for r in plan['basicPodiumFootings']} == {'landsd/213586:0'}
    terrain = plan['topLevelTerrainPatches']
    assert len({r['source'] for r in terrain}) == len({r['destination'] for r in terrain}) == 2
    assert {r['replaces']['url'] for r in terrain} == {
        'city/data/government-native-fung-yip-original-v1-20261025.json',
        'city/data/government-native-kwong-fung-original-v1-20261025.json'}
    assert all(r.get('nativeReview') and not r.get('replacesMany') for r in terrain)
    return True


def evidence():
    result, pins = authenticate(stage.DOC)
    assert result['canonicalPublisherDryRunPassed'] and result['qualifiedForLiveVerification']
    assert result['newVisibleModels'] == 16 and result['expectedFixedXLDelta'] == 2
    assert result['expectedRuntimeCount'] == 7007 and not result['publication']
    for relative, sha in pins.items():
        assert digest((ROOT / relative).read_bytes()) == sha, relative
    q = read(stage.DOC / 'qualification.json')
    assert all(q[k] is True for k in ['identityAccepted', 'originalSourceApplicabilityAccepted',
                                      'sourceSpecificPhysicalInterpretationAccepted', 'visualAcceptance',
                                      'privateStageQualified'])
    assert q['heightConflictRetained'] == ['landsd/224123:0']
    assert q['sourceGeometryChanges'] == q['sourcePoseChanges'] == 0 and not q['publication']
    assert stage.ref(ROOT / '3d-viewer/city/data/manifest.json') == q['currentManifest']
    fixturefolder = stage.BASE / (stage.P + 'supported-activation-fixture-v2-20261028')
    _, fixturepins = authenticate(fixturefolder)
    path = fixturefolder / 'fixture-inputs.json'
    assert digest(path.read_bytes()) == fixturepins[str(path.relative_to(ROOT))]
    inputs = read(path)
    cfg = read(ROOT / inputs['configPath'])
    original = ROOT / cfg['stage'] / 'catalogue.json'
    assert digest(original.read_bytes()) == fixturepins[str(original.relative_to(ROOT))]
    models = read(stage.STAGE / 'catalogue.json')['models']
    verify_models(read(original)['models'], models, q['sourceSHA256ByUid'])
    for model in models:
        assert stage.ref(stage.STAGE / model['asset'])['sha256'] == model['sha256']
        assert model['sourceFunctionalApplicability'] == stage.ref(stage.DOC / 'qualification.json')
    plan = read(stage.STAGE / 'plan.json')
    verify_plan(plan)
    assert len(inputs['resources']) == len(set(inputs['resources'])) == 159
    return set(inputs['resources']), q


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--receipt')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    assert not (args.prepare_only and args.apply)
    resources, q = evidence()
    if args.prepare_only:
        assert not args.receipt
        save(stage.BASE / (stage.P + 'guarded-publisher-preflight-v1-20261028') / 'summary.json',
             dict(uids=q['uids'], passed=True, resources=sorted(resources),
                  stageReceipt=stage.ref(stage.DOC / 'result.json'),
                  publisher=stage.ref(Path(__file__)), publication=False))
        print('Exact source/plan/159-resource preflight passed; no publication.')
        return
    assert args.receipt
    lease = read(Path(args.receipt))

    @contextmanager
    def fence():
        with connect() as db:
            db.row_factory = dict_row
            db.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            live = reservations._current(db, lease)
            assert live and resources <= set(live['resources'])
            assert stage.ref(ROOT / '3d-viewer/city/data/manifest.json') == q['currentManifest']
            yield

    with fence():
        pass
    pub = module('elegant_exact_live_publisher', HERE.parent / 'island-detail-integration/publish.py')
    pub.PUBLICATION_GUARD = fence
    pub.DOC = ROOT / 'docs/astra-city/model-integration-20260909' / BATCH
    sys.argv = ['publish.py', str((stage.STAGE / 'plan.json').relative_to(ROOT))] + (['--apply'] if args.apply else [])
    with private_validator():
        pub.main()


if __name__ == '__main__':
    main()
