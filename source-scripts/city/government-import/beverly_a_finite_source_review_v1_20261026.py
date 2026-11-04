"""Bind A's exact original, finite support, native availability and inspected exports."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-beverly-a-finite-source-review-v1-20261026'
CONFIG = BASE / 'government-xl-beverly-a-finite-native-original-install-config-v1-20261026.json'


def main():
    out = BASE / BATCH
    assert not out.exists()
    cfg = read(CONFIG)
    refs, pins = [Path(__file__), CONFIG], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    uid = 'landsd/255539:0'
    selection = take(cfg['runtime'], 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == uid)
    assert cfg['sources'] == {uid: source['sourceSHA256']}
    identity = take('government-xl-beverly-ad-after-fe-identity-v1-20261025', '255539:0/identity.json')
    assert identity['passed'] and identity['sourceSHA256'] == source['sourceSHA256'] and all(identity['proof'].values())
    metrics = take(cfg['runtime'], 'metrics.json')
    policy = module('beverly_a_acceptance_policy', HERE / 'acceptance-policy.py')
    reasons = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=source['sourceSHA256'], identityProof=identity['proof']), next(r for r in metrics['rows'] if r['uid'] == uid), metrics['profiles']['mobile'])
    assert reasons == ['ground-contact-unresolved'], reasons
    numeric = take('government-xl-beverly-ad-after-fe-identical-numerics-v1-20261025', 'summary.json')
    assert numeric['allFourWorldSourceAttributesIdentical'] and numeric['allActualLiteralSourceAndDrawnGroundInputsIdentical']
    assert numeric['currentBatch'] == cfg['runtime'] and uid in numeric['uids']
    foundation = take('government-xl-beverly-255539-after-k-foundations-v1-20261025', 'summary.json')
    assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
    assert all(r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundation['rows'])
    continuous = next(r for r in take('government-xl-beverly-ad-after-fe-continuous-v1-20261025', 'summary.json')['rows'] if r['uid'] == uid)
    assert continuous['wholeSourceFaces'] == 15248 and continuous['wholeSourceUncoveredFaces'] == 0 and not continuous['continuousAffectedFaces']
    assert continuous['sourceSHA256'] == source['sourceSHA256'] and continuous['upwardContinuousMinimumGapM'] > 0
    scope = take(cfg['scope'], 'summary.json')
    forms = {r['building']['uid']: r['building'] for r in take(cfg['scope'], '255539:0-forms.json.gz')}
    assert set(forms) == {uid, 'landsd/233218:0', 'landsd/256136:0', 'landsd/255543:0'}
    assert scope['rows'][0]['currentNativeActorsChecked'] == cfg['currentNativeActors'] == 6957
    finite = take(cfg['finiteEvidence'], 'finite-basic-evidence.json')
    bindings = take(cfg['finiteEvidence'], 'support-bindings.json')
    assert finite['verifiedFinitePaths'] == 40 and finite['completeFourWorldCanonicalRetainedBasicSupport'] is False
    assert bindings[0]['currentBasicForm'] == forms['landsd/233218:0']
    native = [r for r in take(cfg['nativeContext'], 'summary.json')['rows'] if r['uid'] == uid]
    retained = {r['nativeUid']: r['rawCurrentNativeEntry'] for r in native}
    assert set(retained) == set(cfg['retainedNativeUids'])
    assert retained['landsd/256136:0']['publicationApproved'] is False
    ab = next(r for r in native if r['nativeUid'] == 'landsd/256136:0')
    assert all(m['finiteContactPairs'] == 35 and m['areaContactPairs'] == 5 for m in ab['modes'])
    assert all(m['finiteContactPairs'] == 0 for r in native if r != ab for m in r['modes'])
    # The previously measured dimensional/area context is reused only after
    # complete current contact streams and immutable native entry match exactly.
    historical = 'government-xl-beverly-adf-after-k-native-contacts-v1-20261025'
    old_ab = next(r for r in take(historical, 'summary.json')['rows'] if r['uid'] == uid and r['nativeUid'] == 'landsd/256136:0')
    assert old_ab == ab
    for mode in ['original', 'literal', 'leftF32', 'balancedF32']:
        name = '255539:0--256136:0--' + mode + '.json.gz'
        assert take(cfg['nativeContext'], name) == take(historical, name)
    orientation = take('government-xl-beverly-a-e-after-k-contact-orientation-v1-20261025', 'summary.json')
    assert orientation['currentFootprintOverlapM2'] == orientation['currentFootprintDistanceM'] == 0
    assert all(r['horizontalAreaPairs'] == 5 and r['sumHorizontalPairAreaM2'] == 0.002911760304943147 and max(r['maximumContactDistanceToEachFootprintBoundaryM']) < .075 for r in orientation['rows'])
    roles = take('government-xl-beverly-ad-after-fe-native-roles-v1-20261025', 'summary.json')
    assert all(r['roles'].get('transverse-surface-crossing') == 15 for r in roles['rows'] if r['uid'] == uid and r['nativeUid'] == 'landsd/256136:0')
    primary = 'government-xl-beverly-ab-after-fe-primary-records-v1-20261025'
    structures = take(primary, 'structures.json')['features']
    assert len(structures) == 2 and all(r['attributes']['Storeys'] == 37 and r['attributes']['OPNo'] == 'H141/88' for r in structures)
    take(primary, 'footprints.json'); take(primary, 'relations.json')
    foreign = [r for r in take('government-xl-beverly-ad-after-fe-foreign-basics-v1-20261025', 'summary.json')['rows'] if r['uid'] == uid]
    assert len(foreign) == 1 and foreign[0]['foreignUid'] == 'landsd/233218:0'
    reports, images, retained_images = [], [], []
    for width in [390, 1280]:
        report = take(cfg['browser'], str(width) + '/staged-browser.json')
        assert report['passed'] and not report['errors']
        p = BASE / cfg['browser'] / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())))
        for v in [v for v in report['views'] if 'time' in v] + report['retainedNativeOwnViews']:
            path = p.parent / v['file']
            assert digest(path.read_bytes()) == pins[cfg['browser']][str(path.relative_to(ROOT))]
            refs.append(path)
            image = dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
            (images if v['uid'] == uid else retained_images).append(image if v['uid'] == uid else dict(**image, uid=v['uid'], width=width, time=v['time']))
    assert len(images) == 4 and len(retained_images) == 8
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == scope['currentManifestSHA256']
    refs.append(manifest)
    review = dict(uids=[uid], sourceSHA256ByUid=cfg['sources'], sourceSpecificPhysicalInterpretationAccepted=True,
                  identityAccepted=True, completeNeighbourInterpretationAccepted=True, completeFourWorldSourceClearance=True,
                  completeFourWorldCanonicalRetainedBasicSupport=False, completeFourWorldFiniteRetainedBasicSupport=True,
                  completeCurrentNeighbourChecks=4, identityProof=identity['proof'], identityProofByUid={uid: identity['proof']},
                  currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())),
                  retainedCurrentBasicSupportUids=['landsd/233218:0'], retainedBasicSupportDependencies=bindings,
                  leaseResources=sorted('building:' + u for u in forms), terrainEdits=False, sourceGeometryChanges=0,
                  sourcePoseChanges=0, installationApproved=False, publication=False, visualAcceptance=True,
                  originalSourceReviewAccepted=True, imagesActuallyViewed=images, retainedImagesActuallyViewed=retained_images,
                  browserReports=reports, retainedNativeEntries=retained, runtimeAvailabilityDependenciesByUid=cfg['nativeAvailabilityDependenciesByUid'],
                  sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                  qualification=cfg['placementReview'] + ' The35 A/B contacts remain verbatim:15 transverse,11 source-edge,5 tiny horizontal roof-plane areas at188.990005m (pair-area sum0.0029117603m2),4 points. All contacts lie within0.075m of each recorded footprint boundary; this is bounded exact-original join interpretation, not a zero-interpenetration or engineering-intent claim. Both primary records identify37-storey towers under H141/88. B and K entries/bytes remain unchanged and B is not reapproved. ROOT actually opened all12 individual V2 exports: A4 and retained B/K8; facades, roofs and podium interfaces readable with ordinary adjoining-tower overlap. Existing grey/dark night materials and BASIC windows remain. V1 obstructed retained angles are retained as negatives. No geometry or terrain edits. Separate guarded installation/live review/full readback remain mandatory.')
    from finite_basic_native_admission_v2_20261025 import replay
    refs.extend(replay(cfg, review))
    save(out / 'ROOT-PHYSICAL-REVIEW.json', review)
    save(out / 'ROOT-SOURCE-REVIEW.json', review)
    refs.extend([HERE / 'acceptance-policy.py', HERE / 'test_finite_basic_native_admission_v2_20261025.py'])
    module('beverly_a_finite_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-original-finite-v2-basic-support-native-role-and-availability-review', list(dict.fromkeys(refs)), review)


if __name__ == '__main__':
    main()
