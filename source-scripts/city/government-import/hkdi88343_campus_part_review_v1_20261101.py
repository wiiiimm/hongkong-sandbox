"""Bounded review of one unchanged campus part on its existing original platform.

Actual earth, original finite interfaces and current full scene scope are checked
separately. A multi-level peer's maximum roof envelope is not an earth surface.
No generic predicate, numerical tolerance or installed-parent metadata changes.
"""
import sys, uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hkdi88343-campus-part-review-v1-20261101'
P = 'government-xl-hkdi88343-after-one-peking-'
RUNTIME = P + 'current-v1-20261101-runtime'
NATIVE = 'government-xl-cohort19-installed-native-contacts-v1-20261101'
ROLES = 'government-xl-cohort19-native-contact-roles-v1-20261101'
PARENT_REVIEW = 'government-xl-hkdi22089-component-identity-review-v1-20261101'
UID, PARENT = 'landsd/88343:0', 'landsd/22089:0'
SHA = '98e25a696418680d31f70de499561a68412fc1b08d50ab4e49365ef63adadcc8'
PSHA = '5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40'

def main():
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not out.exists()
    resources = ['building:' + u for u in [PARENT, UID]]
    if '--owned' not in sys.argv:
        assert not local.exists()
        c = reservations.claim('hkdi-campus-part-review-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], local / 'reservation.json', [sys.executable, __file__, '--owned'])
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}
    def take(batch, name='summary.json', localfile=False):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        f = (HERE / 'local' / batch if localfile else BASE / batch) / name
        assert digest(f.read_bytes()) == pins[batch][str(f.relative_to(ROOT))]
        refs.append(f)
        return read(f)
    selection = take(RUNTIME, 'selection.json.gz')
    source = selection['rows'][0]
    assert source['uid'] == UID and source['sourceSHA256'] == SHA and source['triangles'] == 11866
    geom = take(RUNTIME, 'runtime-geometry.json.gz', True)['rows'][0]
    attrs = take(P + 'attributes-v1-20261101', 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    child = attrs['rows'][0]
    assert child['uid'] == UID and child['sourceSHA256'] == SHA
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == SHA
    refs.append(asset)
    ix = np.asarray(child['completeOriginalIndex']).reshape(-1, 3)
    worlds = {'original': decode_original_world_triangles(asset.read_bytes())}
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(child[field], dtype='<f8').reshape(-1, 3)[ix]
    assert np.array_equal(worlds['literal'], np.asarray(geom['position']).reshape(-1, 3)[np.asarray(geom['index']).reshape(-1, 3)])
    ground = np.asarray(geom['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    margin = min(float(t[:, :, 1].min() - ground[:, :, 1].max()) for t in worlds.values())
    assert margin > 0 and all(len(t) == 11866 for t in worlds.values())
    earth = take(P + 'foundations-v1-20261101')
    assert earth['establishedFoundationPolicyPassed'] and len(earth['rows']) == 4
    assert all(r['triangles'] == r['completeTerrainTriangles'] == 11866 and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in earth['rows'])
    identity = take(P + 'current-v1-20261101-identity', '88343:0/identity.json')
    assert identity['passed'] and identity['reasons'] == []
    assert identity['uid'] == UID and identity['sourceSHA256'] == SHA
    proof = identity['proof']
    assert all(proof[k] is True for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted'])
    metrics = take(RUNTIME, 'metrics.json')
    metric = metrics['rows'][0]
    policy = module('hkdi_unchanged_original_policy', HERE / 'acceptance-policy.py')
    raw_policy = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=SHA, identityProof=proof), metric, metrics['profiles']['mobile'])
    assert raw_policy == ['ground-contact-unresolved']
    assert metric['missingTerrain'] == 0 and metric['maxSamplerDelta'] <= .004
    scope = take(P + 'scope-v1-20261101')
    assert scope['uids'] == [UID] and scope['rows'][0]['currentNativeActorsChecked'] == 7071
    assert [r['uid'] for r in scope['rows'][0]['nearbyNativeActors']] == [PARENT]
    forms = take(P + 'scope-v1-20261101', '88343:0-forms.json.gz')
    assert len(forms) == 2 and {r['building']['uid'] for r in forms} == {UID, PARENT}
    assert all(r['building']['parent'] == 'way/185631747' for r in forms)
    parent_review = take(PARENT_REVIEW, 'ROOT-COMPONENT-IDENTITY-REVIEW.json')
    assert parent_review['sourceComponentIdentityAccepted'] and not parent_review['wholeLandmarkAccepted']
    assert parent_review['sourceSHA256'] == PSHA and parent_review['installedMetadataChanges'] == 0
    native = take(NATIVE)
    pair = next(r for r in native['rows'] if r['uid'] == UID and r['nativeUid'] == PARENT)
    parent = pair['rawCurrentNativeEntry']
    assert parent == parent_review['rawInstalledEntry'] and parent['sha256'] == pair['nativeSHA256'] == PSHA
    assert parent['publicationApproved'] and parent['placementReviewed'] and parent['identityReviewApproved'] is False and parent['wholeLandmarkAccepted'] is False
    assert pair['sourceSHA256'] == SHA
    # Historical numerical contacts are reusable only with identical actual
    # source/parent streams and all other native capture inputs, not by count.
    support = take(P + 'support-v1-20261101')
    assert support['historicalSourceArraysIdentical'] and support['allOtherHistoricalNativeInputsIdentical']
    parent_attrs = take(NATIVE, 'native-attributes.json.gz')
    native_attr = next(r for r in parent_attrs['rows'] if r['uid'] == PARENT)
    assert native_attr['sourceSHA256'] == PSHA
    for name, sha in parent_attrs['inputHashes'].items():
        if name == '3d-viewer/city/data/manifest.json': continue
        f = ROOT / name
        assert digest(f.read_bytes()) == sha
        refs.append(f)
    roles = take(ROLES)
    deck = take('government-xl-hkdi88343-original-deck-paths-v2-20261101')
    assert deck['fourWorldPathCounts'] == [6, 6, 6, 6] and deck['exactNativeDeckFace'] == 3896
    assert deck['allCurrentEarthFoundationsPassed'] and deck['deckStrictlyAboveAllCapturedEarth']
    facts = {}
    for mode, tri in worlds.items():
        raw = take(P + 'support-v1-20261101', mode + '/diagnostic.json.gz')
        assert raw['sourceWorldSHA256ByUid'][UID] == digest(tri.astype('<f8').tobytes())
        assert raw['support']['strictContacts'] == 0 and raw['support']['wallIntersections'] == 4 and len(raw['support']['unresolved']) == 6 and not raw['support']['passed']
        assert raw['unresolved'] == raw['finitePaths'] == 6
        contacts = take(NATIVE, '88343:0--22089:0--' + mode + '.json.gz')
        assert contacts['allPairsExamined'] and contacts['sourceFacesOmitted'] == 0 and len(contacts['contacts']) == 2459
        assert all(c['dimension'] == 1 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2 for c in contacts['contacts'])
        classified = next(r for r in roles['rows'] if r['uid'] == UID and r['nativeUid'] == PARENT and r['mode'] == mode)
        assert classified['roles'] == {'transverse-surface-crossing': 2459} and classified['sourceWorldSHA256'] == digest(tri.astype('<f8').tobytes())
        paths = take('government-xl-hkdi88343-original-deck-paths-v2-20261101', mode + '.json.gz')
        assert len(paths['paths']) == 6 and all(r['originalDeckFace'] == 3896 and r['conservativeDeckMinusAllCapturedGroundMaximumM'] > 0 for r in paths['paths'])
        facts[mode] = dict(sourceWorldSHA256=digest(tri.astype('<f8').tobytes()), allOriginalFaces=11866,
            rawStrictContacts=0, rawWallIntersections=4, rawRimWarnings=raw['support']['unresolved'], exactLowComponentDeckPaths=6,
            exactNativeDeckFace=3896, completePositiveDimensionalNativeContacts=2459, coplanarAreaContacts=0,
            actualEarthBuriedFaces=0, rawOrdinarySupportPassed=False, rawCompoundFoundation=raw['compoundFoundation'])
    inspected = take('government-xl-hkdi88343-source-recovery-checkpoint-v1-20261101')
    viewed = {r['path']: r['sha256'] for r in inspected['exactImagesActuallyViewed']}
    browser = P + 'unapproved-preview-v1-20261101'
    images, retained, reports = [], [], []
    for width in [390, 1280]:
        report = take(browser, str(width) + '/staged-browser.json')
        assert report['passed'] and not report['errors']
        reports.append(dict(path=str((BASE / browser / str(width) / 'staged-browser.json').relative_to(ROOT)), sha256=digest((BASE / browser / str(width) / 'staged-browser.json').read_bytes())))
        for field, target, expected_uid, expected_sha in [('views', images, UID, SHA), ('retainedNativeOwnViews', retained, PARENT, PSHA)]:
            rows = [r for r in report[field] if r.get('file')]
            assert len(rows) == 2
            for view in rows:
                f = BASE / browser / str(width) / view['file']
                item = dict(path=str(f.relative_to(ROOT)), sha256=digest(f.read_bytes()), uid=view['uid'], width=width, time=view['time'])
                assert viewed[item['path']] == item['sha256'] == pins[browser][item['path']]
                assert view['uid'] == expected_uid and view['sourceSHA256'] == expected_sha
                assert view['active'] and view['visible'] and view['fullyFramed'] and not view['fallbackFaces']
                if field == 'views': assert view['pick'] == view['collision'] == UID and view['solidAppearance']
                target.append(item)
                refs.append(f)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    start = digest(manifest.read_bytes())
    assert start == selection['manifestSHA256'] == scope['currentManifestSHA256'] == parent_review['currentManifestSHA256']
    installed = {r['uid']: r for url in read(manifest)['officialModelCatalogues'] for r in read(ROOT / '3d-viewer' / url)['models']}
    assert len(installed) == 7071 and UID not in installed and installed[PARENT] == parent
    pointer = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (read(pointer)['snapshotId'], PARENT)).fetchone() == ('installed-verified', PSHA)
    refs.extend([manifest, pointer])
    # Retain the intentionally stopped, unsuitable peer-envelope experiment.
    stopped = BASE / 'government-xl-hkdi88343-complete-peer-clearance-v1-20261101'
    stop = read(stopped / 'INTENTIONAL-STOP.json')
    assert digest((stopped / 'original.json.gz').read_bytes()) == stop['originalWorldOutputSHA256']
    assert digest((stopped / 'original-cap-paths.json.gz').read_bytes()) == stop['originalCapOutputSHA256']
    hypothesis = read(stopped / 'original-cap-paths.json.gz')
    assert not hypothesis['proof']['allAffectedHavePaths'] and len(hypothesis['proof']['negativeNonWallFaces']) == 1973
    refs.extend(f for f in stopped.rglob('*') if f.is_file())
    low = take('government-xl-hkdi88343-low-component-views-v2-20261101')
    assert len(low['sourceFaces']) == 28
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == start
    result = dict(uids=[UID], reviewer='ROOT', sourceSHA256ByUid={UID: SHA}, requiredOriginalAssembly={UID: SHA}, supportByUid={UID: PARENT}, nativeSupportByUid={UID: PARENT},
        identityAccepted=True, identityProof=proof, rawIdentityReasonsRetained=[], sourceSpecificPhysicalInterpretationAccepted=True,
        completeNeighbourInterpretationAccepted=True, completeFourWorldFoundations=True, completeFourWorldSourceClearance=True,
        completeCurrentNeighbourChecks=2, leaseResources=resources, retainedNativeEntries={PARENT: parent}, retainedNativeUids=[PARENT],
        retainedBasicSupportDependencies=[], retainedCurrentBasicSupportUids=[], unresolvedExternalBasicContacts=[],
        currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=start), currentManifestSHA256=start,
        parentComponentIdentityReview=dict(path=str((BASE / PARENT_REVIEW / 'ROOT-COMPONENT-IDENTITY-REVIEW.json').relative_to(ROOT)), sha256=digest((BASE / PARENT_REVIEW / 'ROOT-COMPONENT-IDENTITY-REVIEW.json').read_bytes())),
        acceptedInstalledSupportContacts=[dict(uid=UID, nativeUid=PARENT, physicalInterpretationAccepted=True, rawContactSummary=pair)],
        actualEarthGlobalClearanceLowerBoundM=margin, junctionFacts=facts, rawPolicyReasonsPreserved=raw_policy,
        rawCanonicalFailuresPreserved=True, ordinarySupportPredicateRemainsFalse=True, parentCatalogueFlagsUnchanged=True,
        stoppedPeerEnvelopeHypothesis=dict(completedModes=['original'], allFourWorldExperimentComplete=False, physicalApprovalTransferred=False, rawStop=stop),
        terrainEdits=False, sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True,
        imagesActuallyViewed=images, retainedImagesActuallyViewed=retained, browserReports=reports,
        visualAcceptance=True, installationApproved=False, publication=False,
        interpretation=[
            'Accept only this exact Block A source and original platform at unchanged fixed1x/HKPD placement. Every source face is covered by actual earth and all vertices remain above its complete maximum in each world. No actual-earth burial, missing ground, identity or runtime-budget exception is granted.',
            'The sole touching installed native is the unchanged reviewed platform of the same recorded campus; the two complete current forms are this source and that platform. All2459positive-dimensional source/platform crossings per world are retained as the authored campus-part interface; there are no coplanar area contacts or unexamined external native/BASIC intersections.',
            'The exact28face inclined folded lower component was inspected together with the complete source and platform. Each of the six original rim warnings reaches original horizontal deck3896 through a finite unchanged-source path inside the actual-earth coverage and existing residual/endpoint-height limits. Accept this specific inclined interface as part of the authored assembly; do not report ordinary0strict/4wall/6unresolved checks as passing or widen the0.5m wall allowance.',
            'The multi-level platform contains overhead floors/roof around the Block A opening. Its maximum-height compound envelope is not earth and falsely treats ordinary lower source floors as buried. Preserve the failed first-world1973nonwall clear-cap hypothesis and all four raw sampled compound foundations; this hypothesis supplies no physical approval and was intentionally stopped before redundant remaining-world work.',
            'Parent component identity is separately qualified by the current exact graph/route/cell and inspected projection review. Its legacy identity=false and whole-landmark=false flags remain unchanged; no complete-campus acceptance, new native geometry, ownership or engineering certification is asserted.',
            'Eight exact desktop/mobile source and retained exports were opened directly. Night views are dark and existing platform skin/aliasing remains; no measured FPS or complete-façade claim. Guarded typed stage, actual installed loading/failure/picking/collision, unchanged-old-assets and full521ledger readback remain mandatory.'])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    save(out / 'junction-facts.json', facts)
    refs.extend([HERE / 'acceptance-policy.py', HERE / 'exact_packed_world_geometry_20261009.py'])
    module('hkdi_campus_part_review_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-unchanged-original-campus-part-interface-review', list(dict.fromkeys(refs)), result)

if __name__ == '__main__': main()
