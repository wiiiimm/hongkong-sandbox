"""Stage reviewed unchanged originals and run the unmodified canonical publisher.

Dry run only. Keeps the recorded height discrepancy and all native/BASIC guards.
"""
import argparse
import copy
import shutil
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from three_member_native_boundary_v1_20261027 import private_validator

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-elegant-garden-'
BATCH = P + 'sixteen-original-qualified-stage-v2-20261028'
DOC = BASE / BATCH
STAGE = HERE / 'accepted' / BATCH


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    leasepath = HERE / 'local' / BATCH / 'reservation.json'
    resources = read(BASE / (P + 'sixteen-original-updated-terrain-plan-v1-20261028.json'))['resources']
    assert not DOC.exists() and not STAGE.exists()
    if not args.owned:
        assert not leasepath.parent.exists()
        claim = reservations.claim('elegant-qualified-stage-' + str(uuid.uuid4()), resources,
                                   batch=BATCH, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath, [sys.executable, __file__, '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease)
    refs, pins, receipts = [Path(__file__)], {}, {}

    def take(suffix, name='summary.json'):
        folder = BASE / (P + suffix + '-20261028')
        if suffix not in pins:
            receipts[suffix], pins[suffix] = authenticate(folder)
            refs.append(folder / 'result.json')
        if name == 'result.json':
            return receipts[suffix]
        path = folder / name
        assert digest(path.read_bytes()) == pins[suffix][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    physical = take('physical-dependency-review-v1')
    assert physical['composedPhysicalApplicabilityAccepted'] and physical['originalSupportDependencyRolesAccepted']
    identity = take('identity-boundary-reviews-v1')
    assert identity['allSixteenSourceAssociationsQualified']
    applicable = take('224123-original-applicability-review-v2')
    assert applicable['sourceSpecificOriginalApplicabilityAccepted'] and applicable['rawTopHeightConflictUnresolved']
    life = take('supported-activation-browser-v3')
    assert life['browserPassed'] and life['cases'] == life['expectedCases'] == 17
    clean = take('clean-context-views-v1')
    exact = take('exact-camera-views-v1')
    assert clean['allPassed'] and exact['allPassed']
    images = []
    for name in ['desktop-root-observations.json', 'mobile-root-observations.json']:
        path = BASE / (P + 'full-scene-image-qa-v1-20261028') / name
        notes = read(path)
        assert notes['actualOriginalImagesInspected'] == 50
        for relative, sha in notes['sourceImageHashes'].items():
            image = ROOT / relative
            assert digest(image.read_bytes()) == sha
            images.append(ref(image))
            refs.append(image)
        refs.append(path)
    assert len(images) == 100
    auditpath = BASE / (P + 'completed-browser-audit-v1-20261028') / 'summary.json'
    audit = read(auditpath)
    assert audit['lifecycleCasesPassed'] == 17 and audit['targetedCleanExports'] == 28
    assert len(audit['exactCameraFrames']) == 4
    refs.append(auditpath)
    for binding in audit['inputRefs'] + audit['exactCameraFrames']:
        path = ROOT / binding['path']
        assert digest(path.read_bytes()) == binding['sha256']
        refs.append(path)
    main_visual = take('main-canopy-visual-review-v2', 'result.json')
    other_visual = take('remaining-foundation-visual-reviews-v1')
    assert main_visual['visualReviewApproved'] and other_visual['visualReviewApproved']
    assert {r['uid'] for r in other_visual['rows']} == {'landsd/213586:0', 'landsd/336456:0'}
    fixture_inputs = take('supported-activation-fixture-v2', 'fixture-inputs.json')
    cfgpath = ROOT / fixture_inputs['configPath']
    assert digest(cfgpath.read_bytes()) == pins['supported-activation-fixture-v2'][str(cfgpath.relative_to(ROOT))]
    cfg = read(cfgpath)
    prior = ROOT / cfg['stage']
    catpath = prior / 'catalogue.json'
    cat = read(catpath)
    assert digest(catpath.read_bytes()) == pins['supported-activation-fixture-v2'][str(catpath.relative_to(ROOT))]
    refs.extend([cfgpath, catpath])
    sources = physical['sourceSHA256ByUid']
    assert len(cat['models']) == len(sources) == 16
    assert {m['uid']: m['sha256'] for m in cat['models']} == sources
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    before = ref(manifest)
    assert before['sha256'] == physical['currentManifestSHA256'] == fixture_inputs['currentManifestSHA256']
    refs.append(manifest)
    current = [m for url in read(manifest)['officialModelCatalogues']
               for m in read(ROOT / '3d-viewer' / url)['models']]
    assert len(current) == len({m['uid'] for m in current}) == 6991
    assert not set(sources) & {m['uid'] for m in current}
    qualification = dict(
        uids=sorted(sources), sourceSHA256ByUid=sources, currentManifest=before,
        identityAccepted=True, originalSourceApplicabilityAccepted=True,
        sourceSpecificPhysicalInterpretationAccepted=True, visualAcceptance=True,
        qualifiedForLiveVerification=True, privateStageQualified=True,
        physicalReview=ref(BASE / (P + 'physical-dependency-review-v1-20261028') / 'summary.json'),
        applicabilityReview=ref(BASE / (P + '224123-original-applicability-review-v2-20261028') / 'summary.json'),
        visualBasis='ROOT100original day/night exports plus28targeted clean exports and4exact camera frames, three separately approved BASIC foundation close-ups and all28authored interface views. Dark source surfaces at night and natural tower/podium occlusion retained; no measured performance or every-facet visibility claim.',
        heightConflictRetained=['landsd/224123:0'],
        sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
        evidenceInterpretationUsedAI=True, installationApproved=False, publication=False)
    save(DOC / 'qualification.json', qualification)
    for model in cat['models']:
        asset = prior / model['asset']
        assert digest(asset.read_bytes()) == sources[model['uid']] and asset.stat().st_size == model['bytes']
        refs.append(asset)
        dest = STAGE / model['asset']
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(asset, dest)
        model.update(sourceIdentityReviewed=True, identityReviewApproved=True,
                     placementReviewed=True, publicationApproved=True,
                     sourceIdentityReview=ref(BASE / (P + 'identity-boundary-reviews-v1-20261028') / 'summary.json'),
                     sourceFunctionalApplicability=ref(DOC / 'qualification.json'),
                     placementReview=BATCH, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True)
        if model['uid'] == 'landsd/224123:0':
            model['sourceHeightDiscrepancyReview'] = qualification['applicabilityReview']
    save(STAGE / 'catalogue.json', cat)
    formpath = prior / 'source-forms.json'
    assert digest(formpath.read_bytes()) == pins['supported-activation-fixture-v2'][str(formpath.relative_to(ROOT))]
    refs.append(formpath)
    shutil.copyfile(formpath, STAGE / 'source-forms.json')
    save(STAGE / 'catalogue-index.json', dict(models=16, catalogues=['catalogue.json']))
    draftdir = BASE / (P + 'integration-draft-v1-20261028')
    draft_inputs = read(draftdir / 'draft-inputs.json')
    assert draft_inputs['currentManifestSHA256'] == before['sha256']
    for binding in draft_inputs['inputRefs']:
        path = ROOT / binding['path']
        assert digest(path.read_bytes()) == binding['sha256']
        refs.append(path)
    plan = copy.deepcopy(read(draftdir / 'integration-plan-DRAFT.json'))
    plan['status'] = 'qualified-for-canonical-dry-run-only'
    plan['areas'][0]['catalogue'] = str((STAGE / 'catalogue.json').relative_to(ROOT))
    assert plan['areas'][0]['destination'] == 'city/data/official-models/' + P + 'sixteen-original-qualified-stage-v1-20261028/catalogue.json'
    plan['areas'][0]['destination'] = 'city/data/official-models/' + BATCH + '/catalogue.json'
    neighbours = take('sixteen-original-updated-neighbours-v1')
    assert len(neighbours['nativeRows']) == 9 and all(r['passed'] for r in neighbours['nativeRows'])
    checks = DOC / 'retained-native-mesh-checks.json'
    save(checks, dict(rows=neighbours['nativeRows'], aiCalls=0, modelGeometryChanges=0,
                     physicalReview=qualification['physicalReview']))
    for i, entry in enumerate(plan['topLevelTerrainPatches']):
        assert len(plan['topLevelTerrainPatches']) == 2
        old = ROOT / '3d-viewer' / entry['replaces']['url']
        new = ROOT / entry['source']
        assert digest(old.read_bytes()) == entry['replaces']['sha256']
        assert digest(new.read_bytes()) == entry['sha256']
        retained = read(old)['meta']['targetUids']
        assert set(retained) <= set(neighbours['nativeResolved'])
        reviewpath = DOC / f'native-replacement-{i}-review.json'
        save(reviewpath, dict(status='approved-for-integration',
            supersededURL=entry['replaces']['url'], supersededSHA256=entry['replaces']['sha256'],
            replacementSHA256=entry['sha256'], sourceGeometryChanged=False,
            aiCalls=0, modelGeometryChanges=0, retainedUids=retained,
            replacementTargetUids=read(new)['meta']['targetUids'], fullMeshCheck=ref(checks)))
        entry['nativeReview'] = ref(reviewpath)
        refs.extend([old, new])
    save(STAGE / 'plan.json', plan)
    cfg.update(stage=str(STAGE.relative_to(ROOT)) + '/', catalogueURL=plan['areas'][0]['destination'],
               terrain=plan['topLevelTerrainPatches'])
    save(STAGE / 'live-browser-config.json', cfg)
    pub = module('elegant_canonical_qualified_publisher', HERE.parent / 'island-detail-integration/publish.py')
    pub.DOC = DOC / 'publisher-dry-run'
    argv = sys.argv[:]
    try:
        sys.argv = ['publish.py', str((STAGE / 'plan.json').relative_to(ROOT))]
        # The installed North terrain already uses this stricter chain schema.
        # Reuse its complete effective-member dispatcher; ordinary/new pair
        # validation remains delegated to the original finite pair verifier.
        with private_validator():
            pub.main()
    finally:
        sys.argv = argv
    assert not read(pub.DOC / 'publication-plan.json')['published'] and ref(manifest) == before
    refs.append(HERE.parent / 'island-detail-integration/publish.py')
    refs.append(HERE / 'three_member_native_boundary_v1_20261027.py')
    refs.extend(p for p in STAGE.rglob('*') if p.is_file())
    assert reservations.owns(lease)
    module('elegant_canonical_qualified_stage_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'qualified-sixteen-originals-two-native-members-three-basic-foundations-canonical-dry-run',
        list(dict.fromkeys(refs)), dict(**qualification, canonicalPublisherDryRunPassed=True,
                                      newVisibleModels=16, expectedFixedXLDelta=2, expectedRuntimeCount=7007))
    print('Canonical publisher dry run passed; live installation remains pending.')


if __name__ == '__main__':
    main()
