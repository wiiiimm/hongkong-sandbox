"""Exact-source, lease-fenced canonical publisher for the reviewed Elegant group.

--prepare-only does not claim a lease or publish. No generic publisher changes.
"""
import argparse
import copy
import sys
from contextlib import contextmanager
from pathlib import Path
import sha_tin_installation_contract_v1_20261029 as stage
from run import ROOT, HERE, read, save, digest, connect, reservations, dict_row
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from three_member_native_boundary_v1_20261027 import private_validator

BATCH = stage.P + 'seven-original-installed-v1-20261029'
APPROVAL_KEYS = {'sourceIdentityReviewed', 'identityReviewApproved', 'placementReviewed',
                 'publicationApproved', 'sourceIdentityReview', 'sourceFunctionalApplicability',
                 'placementReview', 'aiGeometryModelling', 'sourceEvidenceInterpretationUsedAI',
                 'sourceHeightDiscrepancyReview'}


def verify_models(original, qualified, source_hashes):
    assert len(original) == len(qualified) == len(source_hashes) == 7
    before = {m['uid']: m for m in original}
    after = {m['uid']: m for m in qualified}
    assert len(before) == len(after) == 7 and set(before) == set(after) == set(source_hashes)
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
        assert not model.get('supportDependencies') and not model.get('retainedBasicSupportDependencies')
        assert model.get('suppressesBuildingUids',[]) == (['landsd/92340:0'] if uid=='landsd/231013:0' else [])
    return True


def verify_plan(plan):
    assert set(plan)=={'status','areas','topLevelTerrainPatches','illustrativeFoundations','nativeBasicFallbackGrounds'}
    assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==len(plan['illustrativeFoundations'])==1
    area=plan['areas'][0]
    assert set(area)=={'area','catalogue','destination'}
    assert area['catalogue']==str((stage.STAGE/'catalogue.json').relative_to(ROOT))
    assert area['destination']=='city/data/official-models/'+stage.BATCH+'/catalogue.json'
    terrain=plan['topLevelTerrainPatches'][0]
    assert set(terrain)=={'source','destination','sha256','resolution','area'}
    assert terrain['destination']=='city/data/government-native-sha-tin-seven-original-v1-20261029.json'
    assert terrain['sha256']=='cf1ce7032398cb3119973d7f4723e0c94bac280870f8ec7b89103d2acd93eecd'
    assert plan['illustrativeFoundations'][0]['uid']=='landsd/92340:0'
    hints=plan['nativeBasicFallbackGrounds']
    assert len(hints)==3 and {r['uid']for r in hints}=={'landsd/271344:0','landsd/92881:0','landsd/238142:0'}
    assert all(r['terrainURL']==terrain['destination']and r['hint']['terrainSHA256']==terrain['sha256']for r in hints)
    return True


def evidence():
    result,pins=authenticate(stage.DOC)
    assert result['canonicalFullPlanDryRunPassed'] and result['qualifiedForLiveVerification'] and result['qualifiedExactStage']
    assert result['uids']==stage.UIDS and not result['publication']
    for relative,sha in pins.items():assert digest((ROOT/relative).read_bytes())==sha,relative
    _,qpin=authenticate(stage.QUALIFICATION.parent)
    assert digest(stage.QUALIFICATION.read_bytes())==qpin[str(stage.QUALIFICATION.relative_to(ROOT))]
    q=read(stage.QUALIFICATION)
    assert all(q[k] is True for k in ['identityAccepted','originalSourceApplicabilityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance','collisionReviewApproved','privateStageQualified'])
    assert q['uids']==stage.UIDS and q['sourceGeometryChanges']==q['sourcePoseChanges']==0 and not q['publication']
    q={**q,'currentManifest':stage.ref(ROOT/'3d-viewer/city/data/manifest.json')}
    assert q['currentManifest']['sha256']==q['currentManifestSHA256']
    oldfolder=stage.BASE/(stage.P+'source-bound-production-fixture-v1-20261029')
    _,oldpins=authenticate(oldfolder)
    cfgpath=HERE/'local'/oldfolder.name/'config.json';assert digest(cfgpath.read_bytes())==oldpins[str(cfgpath.relative_to(ROOT))]
    original=ROOT/read(cfgpath)['stage']/'catalogue.json';assert digest(original.read_bytes())==oldpins[str(original.relative_to(ROOT))]
    models=read(stage.STAGE/'catalogue.json')['models'];verify_models(read(original)['models'],models,q['sourceSHA256ByUid'])
    assert set(q['sourceSHA256ByUid'])==set(stage.UIDS)
    for model in models:
        assert stage.ref(stage.STAGE/model['asset'])['sha256']==model['sha256']
        assert model['sourceFunctionalApplicability']==stage.ref(stage.QUALIFICATION)
    plan=read(stage.STAGE/'plan.json');verify_plan(plan)
    # Final exact-stage browser evidence is a separate gate from the earlier
    # prototype and production fixtures. Never substitute either old receipt.
    browser=stage.BASE/(stage.P+'qualified-stage-atomic-lifecycle-v1-20261029')
    life,lpins=authenticate(browser)
    assert life['browserPassed'] and life['cases']==life['expectedCases']==8 and life['actualProductionGeometryHTTP'] and life['moduleSubstitution'] is False
    for path,sha in lpins.items():assert digest((ROOT/path).read_bytes())==sha,path
    report=read(browser/'browser/report.json');assert report['passed'] and len(report['cases'])==8
    inputs=read(stage.DOC/'fixture-inputs.json')
    assert len(inputs['resources'])==len(set(inputs['resources']))==71
    q['finalStageLifecycle']=stage.ref(browser/'result.json')
    return set(inputs['resources']),q


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
        save(stage.BASE / (stage.P + 'guarded-publisher-preflight-v1-20261029') / 'summary.json',
             dict(uids=q['uids'], passed=True, resources=sorted(resources),
                  stageReceipt=stage.ref(stage.DOC / 'result.json'),
                  publisher=stage.ref(Path(__file__)), publication=False))
        print('Exact source/plan/71-resource preflight passed; no publication.')
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
