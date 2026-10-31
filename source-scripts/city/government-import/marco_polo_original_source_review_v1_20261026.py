"""Bind Marco Polo's exact original, reviewed source roles and unchanged neighbours."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

P = 'government-xl-after-dragon-next-five-'
UID = 'landsd/215934:0'
SHA = '2bafbc4db86031469ade9828d8f7701f9c8caa0d4d0975f522650d4b34c6166f'
NATIVES = {'landsd/205767:0': 103, 'landsd/210032:0': 0, 'landsd/33396:0': 0, 'landsd/231484:0': 60}


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = P + 'marco-polo-source-review-v1-20261026'
    out = base / batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(suffix, name='summary.json', local=False):
        folder = P + suffix + '-20261026'
        if folder not in pins:
            pins[folder] = authenticate(base / folder)[1]
            refs.append(base / folder / 'result.json')
        path = (HERE / 'local' / folder if local else base / folder) / name
        assert digest(path.read_bytes()) == pins[folder][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take('ground-v1', 'selection.json.gz')
    source = next(r for r in selected['rows'] if r['uid'] == UID)
    assert source['sourceSHA256'] == SHA and source['triangles'] == 10432
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == SHA
    refs.append(asset)
    triangles = decode_original_world_triangles(asset.read_bytes())
    identity = take('identity-v1', '215934:0/identity.json')
    assert identity['sourceSHA256'] == SHA and identity['worldTrianglesSHA256'] == digest(triangles.astype('<f8').tobytes())
    assert identity['originalOwnership']['sourceGraphVerified'] and identity['originalOwnership']['originalRootName'] == 'B354441736701063C0'
    assert identity['exactCurrentComponentRoute']['qualified'] and identity['freshCurrentIdentity']['exactObjectAndCSUID']
    assert identity['exactWholeCellCoverage']['covered'] and identity['freshCurrentIdentity']['targetCoveredBySourceProjection'] > .998
    assert not identity['passed'] and set(identity['reasons']) == {
        'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2',
        'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM',
        'full-source-maximum-extent', 'full-source-unrelated-overlap'}
    form = source['source']['building']
    assert form['objectId'] == 215934 and form['buildingCSUID'] == '3544417367T20050430' and form['buildingId'] == 1108244278
    footprint = next(r['attributes'] for r in take('primary-v1', 'footprints.json')['features']
                     if r['attributes']['BuildingCSUID'] == form['buildingCSUID'])
    assert footprint['BuildingID'] == form['buildingId'] and footprint['BuildingNameEN'] == 'Marco Polo Hongkong Hotel'
    identity_proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True)
    metrics = take('ground-v1', 'metrics.json')
    metric = next(r for r in metrics['rows'] if r['uid'] == UID)
    policy_path = HERE / 'acceptance-policy.py'
    policy = module('marco_polo_policy', policy_path)
    reasons = policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=SHA, identityProof=identity_proof), metric, metrics['profiles']['mobile'])
    assert reasons == ['terrain-intersects-source-over-0.5m']
    refs.append(policy_path)
    foundation = take('215934-foundation-v1')
    assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
    assert all(r['triangles'] == r['completeTerrainTriangles'] == 10432 and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in foundation['rows'])
    low = take('215934-low-faces-v1')
    caps = take('215934-cap-paths-v1')
    assert caps['allFourCompleteGroundClearCapPaths'] and len(low['rows']) == len(caps['rows']) == 4
    for row in low['rows']:
        assert row['completeSourceFaces'] == 10432 and len(row['exactAffectedFaces']) == 38
        assert row['allAffectedWallLike'] and row['allAffectedHaveExposedHighestVertex']
    for row in caps['rows']:
        proof = row['completeGroundClearancePartition']
        assert proof['completeSourceFaces'] == 10432 and not proof['negativeNonWallFaces']
        assert proof['allAffectedHavePaths'] and len(proof['paths']) == 38
        assert all(p['hasExactSharedEdgeClearCapPath'] for p in proof['paths'])
    scope = take('scope-v1')
    own_scope = next(r for r in scope['rows'] if r['uid'] == UID)
    assert own_scope['currentNativeActorsChecked'] == 6965
    assert {r['uid'] for r in own_scope['nearbyNativeActors']} == set(NATIVES)
    forms = {r['building']['uid']: r for r in take('scope-v1', '215934:0-forms.json.gz')}
    fallback = take('marco-polo-native-fallback-v1')
    assert {r['nativeFallbackUid'] for r in fallback['rows']} == set(NATIVES)
    for row in fallback['rows']:
        assert row['uid'] == UID and row['sourceSHA256'] == SHA and len(row['modes']) == 5
        assert all(m['finiteContactPairs'] == m['positiveSurfaceContactPairs'] == 0 for m in row['modes'])
        f = row['exactCurrentFallbackForm']; uid = f['building']['uid']
        if uid in forms:
            assert forms[uid] == f
        else:
            forms[uid] = f
    assert len(forms) == 10
    native = take('native-contacts-v1')
    native_rows = [r for r in native['rows'] if r['uid'] == UID]
    assert {r['nativeUid'] for r in native_rows} == set(NATIVES)
    raw_native = []
    for row in native_rows:
        assert row['sourceSHA256'] == SHA and len(row['modes']) == 4
        for mode in row['modes']:
            count = NATIVES[row['nativeUid']]
            assert mode['finiteContactPairs'] == mode['positiveSurfaceContactPairs'] == count and mode['areaContactPairs'] == 0
            proof = take('native-contacts-v1', '215934:0--'+row['nativeUid'].split('/')[1]+'--'+mode['mode']+'.json.gz')
            assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0 and len(proof['contacts']) == count
        raw_native.append(row)
    foreign = take('foreign-v1')
    foreign_rows = [r for r in foreign['rows'] if r['uid'] == UID]
    assert {r['foreignUid'] for r in foreign_rows} == {'landsd/156599:0','landsd/211943:0','landsd/231469:0','landsd/234188:0','landsd/264744:0'}
    for row in foreign_rows:
        expected = {'landsd/231469:0': 76, 'landsd/264744:0': 49}.get(row['foreignUid'], 0)
        assert len(row['modes']) == 5
        assert all(m['allFiniteContactPairs'] == expected for m in row['modes'] if m['mode'] != 'before-basic')
    unrelated = next(r for r in identity['freshCurrentIdentity']['intersectingForms'] if r['uid'] == 'landsd/211943:0')
    assert unrelated['sourceYRange'][0] > 12.79 and unrelated['top'] == 8 and unrelated['sameParent'] is False
    native_views = take('marco-polo-native-views-v1')
    assert {r['nativeUid'] for r in native_views['rows']} == {'landsd/205767:0', 'landsd/231484:0'}
    for suffix in ['marco-polo-basic231469-views-v1', 'marco-polo-basic264744-views-v1']:
        take(suffix)
    browser = 'marco-polo-private-native-preview-v1'
    take(browser, 'catalogue.json', local=True)
    images, retained_images, reports = [], [], []
    for width in [1280, 390]:
        report = take(browser, str(width) + '/staged-browser.json')
        reportpath = base / (P+browser+'-20261026') / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(reportpath.relative_to(ROOT)), sha256=digest(reportpath.read_bytes())))
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 2 and len(report['retainedNativeOwnViews']) == 8
        for group, output in [(views, images), (report['retainedNativeOwnViews'], retained_images)]:
            for view in group:
                assert view['active'] and view['visible'] and view['fullyFramed'] and not view['fallbackFaces']
                path = reportpath.parent / view['file']
                assert digest(path.read_bytes()) == pins[P+browser+'-20261026'][str(path.relative_to(ROOT))]
                refs.append(path); output.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    assert len(images) == 4 and len(retained_images) == 16
    for uid, f in forms.items():
        tile = ROOT / '3d-viewer' / f['tile']
        assert digest(tile.read_bytes()) == f['tileSHA256']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == uid) == f['building']
        refs.append(tile)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256'] == scope['currentManifestSHA256']
    refs.append(manifest)
    result = dict(uids=[UID], sourceSHA256ByUid={UID:SHA}, sourceSpecificPhysicalInterpretationAccepted=True,
        identityAccepted=True, completeNeighbourInterpretationAccepted=True, qualifiedFourWorldSourceClearance=True,
        completeCurrentNeighbourChecks=10, identityProof=identity_proof, identityProofByUid={UID:identity_proof},
        rawIdentityVerbatim=identity, rawIdentityReasonsRetained=identity['reasons'], rawPolicyReasonsRetained=reasons,
        currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())),
        retainedCurrentBasicSupportUids=[], retainedBasicSupportDependencies=[], supportByUid={},
        retainedNativeEntries={r['nativeUid']:r['rawCurrentNativeEntry'] for r in native_rows},
        runtimeAvailabilityDependenciesByUid={}, leaseResources=sorted('building:'+u for u in forms),
        terrainEdits=False, sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False,
        visualAcceptance=True, originalSourceReviewAccepted=True, imagesActuallyViewed=images,
        retainedImagesActuallyViewed=retained_images, browserReports=reports,
        rawNativeContacts=raw_native, rawForeignContacts=foreign_rows,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        interpretation='Exact stable IDs, authored root/graph, full metre cell and99.8097percent footprint coverage identify the complete hotel original. The H-shaped roof, exterior fins and low authored attachments match the primary footprint/basemap and inspected source plan. The19.965m extent excess is retained; the only unrelated projected form211943 is below the intersecting source facets by more than4.79m and has no finite surface contact inanyworld. Two same-parent BASIC Ocean Terminal parts retain all76/49after contacts and their before contacts; diagrams show pre-existing podium/facade envelopes crossed by the original facade/low links, not a moved tower. Shared parent is context, not ownership proof. Original Ocean Terminal205767 and Star House podium231484 retain103/60transverse line contacts respectively inall4worlds,0area contacts, within their low adjoining source interfaces. Original-detail facade/connector joins are accepted only for this exact tuple; other natives have0contacts and no entry or publication flag is reapproved. All4native BASIC fallbacks have0finitecontacts beforeandafter. Ground negatives are38exposed authored facade/grade walls with exact clear-cap routes inall4worlds,0wholly buried or upward faces and no negative floor/nonwall surfaces. Ground/podium/support semantics and all numeric failures remain verbatim; no earth or source edit is justified. All20individual private source/retained desktop/mobile day/night exports were actually opened by ROOT. Source roofs/facades and retained native forms remain readable; low podiums are partly occluded by their existing upper buildings and foreground scene, disclosed rather than treated as fully visible. Original grey/day and dark/night appearance retained without new procedural windows. This bounded review grants no installation credit; guarded publication, fresh live browser checks and full current-state readback remain mandatory.')
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    refs.extend([HERE / 'exact_packed_world_geometry_20261009.py', out / 'ROOT-PHYSICAL-REVIEW.json'])
    module('marco_polo_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'bounded-complete-original-hotel-source-and-interface-review', refs, result)


if __name__ == '__main__':
    main()
