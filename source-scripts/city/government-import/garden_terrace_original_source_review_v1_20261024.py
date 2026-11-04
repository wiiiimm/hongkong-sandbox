"""Bounded source-role and actual-export review; no publication or geometry edits."""
from pathlib import Path
from fractions import Fraction
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from garden_terrace_original_catalogue_scope_v1_20261024 import SOURCES, SUPPORTS, RETAINED, verify_metadata, verify_native_scope
BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-next-repairs-garden-terrace2-'
BATCH = P + 'three-original-source-review-v1-20261024'
RUNTIME = P + 'three-current-runtime-v1-20261024'
BROWSER = P + 'three-unapproved-preview-v2-20261024'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs = [Path(__file__), HERE / 'garden_terrace_original_catalogue_scope_v1_20261024.py']
    pins = {}

    def ref(path):
        return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

    def take(batch, file='summary.json'):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / file
        assert ref(path)['sha256'] == pins[batch][ref(path)['path']]
        refs.append(path)
        return read(path)

    def summary(suffix):
        return take(P + suffix + '-20261024')

    selection = take(RUNTIME, 'selection.json.gz')
    assert {r['uid']: r['sourceSHA256'] for r in selection['rows']} == SOURCES
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert ref(manifest)['sha256'] == selection['manifestSHA256']
    refs.append(manifest)
    for row in selection['rows']:
        asset = ROOT / row['candidate']['path']
        assert ref(asset)['sha256'] == SOURCES[row['uid']]
        refs.append(asset)
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert ref(tile)['sha256'] == row['source']['tileSHA256']
        assert next(f for f in read(tile)['buildings'] if f['uid'] == row['uid']) == row['source']['building']
        refs.append(tile)
        f = summary(row['uid'].split('/')[1].split(':')[0] + '-four-world-foundations-v1')
        assert len(f['rows']) == 4
        assert all(r['completeTerrainTriangles'] == r['triangles'] == row['triangles'] and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in f['rows'])
        if row['uid'] == 'landsd/109491:0':
            assert all(r['minimumGapM'] > -0.001 for r in f['rows'])
    raw_supports = []
    for uid, count in [('109491', 328), ('21894', 371)]:
        raw_supports.append(summary(uid + '-original-podium-support-v1'))
        paths = summary(uid + '-original-podium-paths-v1')
        assert paths['allUnresolvedHaveFinitePaths'] and len(paths['rows']) == 4
        assert all(r['targets'] == r['verifiedPaths'] == count and not r['remaining'] for r in paths['rows'])
    low = summary('162285-low-faces-v1')
    assert all(r['allAffectedWallLike'] and r['allAffectedHaveExposedHighestVertex'] for r in low['rows'])
    cap = summary('162285-complete-ground-cap-paths-v1')
    assert cap['allFourCompleteGroundClearCapPaths']
    assert all(len(r['completeGroundClearancePartition']['paths']) == 67 for r in cap['rows'])
    cap = summary('21894-complete-ground-cap-paths-v1')
    assert not cap['allFourCompleteGroundClearCapPaths']
    for row in cap['rows']:
        partition = row['completeGroundClearancePartition']
        assert len(partition['paths']) == 5 and all(p['hasExactSharedEdgeClearCapPath'] for p in partition['paths'])
        assert partition['negativeNonWallFaces'] == [7628, 7629, 7630, 7631]
    basal = summary('21894-basal-ground-context-v1')
    assert basal['allFourWorldBottomFacesBelowRecordedBaseWithGradeBelowBase']
    assert len(basal['rows']) == 4
    assert all(r['allDownwardAtGlobalSourceMinimum'] and r['groundBelowRecordedBase'] and r['faces'] == [7628, 7629, 7630, 7631] and Fraction(r['maximumGroundUnderBottomHKPD']) < Fraction(r['recordedBaseHKPD']) for r in basal['rows'])
    identity = take(P + 'three-compound-identity-v1-20261024', 'identity.json')
    assert identity['identityAccepted'] and identity['requiredUnchangedAssembly'] == SOURCES
    assert all(all(r['proof'][k] for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted']) for r in identity['rows'])
    scope_name = P + 'three-current-model-scope-v1-20261024'
    scope = take(scope_name)
    native = summary('three-current-native-contacts-v1')
    current = {m['uid']: m for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    assert verify_native_scope(scope, native, current)
    forms = {}
    for row in scope['rows']:
        for item in take(scope_name, row['uid'].split('/')[1] + '-forms.json.gz'):
            forms[item['building']['uid']] = item['building']
    assert len(forms) == 6
    foreign = summary('three-current-basic-contacts-v1')
    assert foreign['foreignPairs'] == 9
    for pair in foreign['rows']:
        if pair['foreignUid'] not in SOURCES:
            assert all(r['positiveContactPairs'] == 0 for r in pair['modes'] if r['mode'] != 'before-basic')
    pairs = summary('three-original-pair-context-v1')
    assert pairs['sourceSHA256ByUid'] == SOURCES and pairs['completeUnorderedPairs'] == 3 and len(pairs['rows']) == 12
    assert all(r['contactDimensions'] == {'1': r['positiveSurfaceContacts']} for r in pairs['rows'])
    inspection_name = P + 'three-original-progress-checkpoint-v2-20261024'
    inspection = take(inspection_name, 'ROOT-V2-EXPORT-INSPECTION.json')
    assert inspection['visualInspectionComplete'] and inspection['visualAcceptance']
    assert len(inspection['imagesActuallyViewed']) == 16
    source_images = [r for r in inspection['imagesActuallyViewed'] if r['uid'] in SOURCES]
    retained_images = [r for r in inspection['imagesActuallyViewed'] if r['uid'] in RETAINED]
    assert len(source_images) == 12 and len(retained_images) == 4
    if BROWSER not in pins:
        _, pins[BROWSER] = authenticate(BASE / BROWSER)
        refs.append(BASE / BROWSER / 'result.json')
    for image in source_images + retained_images:
        path = ROOT / image['path']
        assert ref(path)['sha256'] == image['sha256'] == pins[BROWSER][image['path']]
        refs.append(path)
    for report in inspection['browserReports']:
        r = take(BROWSER, str((ROOT / report['path']).relative_to(BASE / BROWSER)))
        assert r['passed'] and not r['errors']
    catpath = HERE / 'local' / BROWSER / 'catalogue.json'
    assert ref(catpath)['sha256'] == pins[BROWSER][ref(catpath)['path']]
    assert verify_metadata(read(catpath)['models'])
    refs.append(catpath)
    plot = BASE / (P + '21894-basal-ground-context-v1-20261024') / 'basal-ground-context.png'
    assert ref(plot)['sha256'] == pins[P + '21894-basal-ground-context-v1-20261024'][ref(plot)['path']]
    refs.append(plot)
    observations = [
        'Exact source-owned Blocks2/3 and common podium form the named compound. Unique current component routes, complete source graphs/cells and the bounded compound identity review bind all3 unchanged hashes together. Raw Block2individual-footprint extent failures remain archived.',
        'All22814 original faces have complete actual-ground coverage in four coordinate representations, with no whole-face or upward-whole-face burial. Block2minimum actual-ground gap is within existing1mm numeric precision. Podium67 affected surfaces and Block3five affected wall surfaces are exposed lower facade walls with complete exact clear-cap paths.',
        'Block3four nonwall faces7628..7631 are downward-facing horizontal global-minimum closures of the original lower facade. Their Y134.9730072 lies below recorded government base135.9. Every actual ground facet under the exact finite columns remains below that recorded base. ROOT inspected their original/ground two-angle plot: the grade crosses the lower closure while the facade continues above. Accept this exact below-grade source closure, not a public upward floor or arbitrary buried horizontal surface. Raw negative gaps and capaggregateFALSE remain; no basement use or engineering foundation dimensions are asserted.',
        'Strict vertical support reports remain33/361 and18/389. All328+371 unresolved rims reach the original common podium through complete exact original-surface paths in all4worlds. The podium and tower interfaces are authored construction joints: all3 original pairs have line contacts only, including the towers touching along their original adjoining lower volumes. Both new towers retain the browser-tested dependency on original162285; no source moves or triangulation changes.',
        'All6881 installed actors were screened for complete four-world bounds. Retained No1GardenTerrace304714 keeps its exact821face asset and metadata, with no new support dependency. Its62 line-only contacts with the new podium are an adjoining original site interface; Block2has no exact surface contact with it. All9 basic pairs are measured, and all external non-peer contacts are zero. Co-import BASIC contacts are replaced together; no other actor is hidden or suppressed.',
        inspection['visualFinding'],
        'Approve the bounded exact originals for guarded integration only. Terrain, existing catalogue entries/assets, source pose, scale and all raw negatives stay unchanged. Global retained-BASIC checks, current leases, atomic publication, live desktop/mobile source+retained exports and full521ledger readback still gate installation credit.'
    ]
    common = dict(uids=sorted(SOURCES), reviewer='ROOT', sourceSHA256ByUid=SOURCES,
        requiredOriginalAssembly=SOURCES, sourceSpecificPhysicalInterpretationAccepted=True,
        originalSourceReviewAccepted=True, identityAccepted=True, completeNeighbourInterpretationAccepted=True,
        identityProof={k: True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},
        completeFourWorldFoundations=True, qualifiedFourWorldSourceClearance=True,
        completeFourWorldSourceClearance=True, completeFourWorldCanonicalRetainedBasicSupport=True,
        rawClearancePassed=False, completeCurrentNeighbourChecks=6, currentManifest=ref(manifest),
        leaseResources=sorted({'building:' + uid for uid in set(forms) | set(SOURCES) | RETAINED}),
        supportByUid=SUPPORTS, nativeSupportByUid=SUPPORTS, retainedBasicSupportDependencies=[],
        retainedCurrentBasicSupportUids=[], terrainEdits=False, sourceGeometryChanges=0, sourcePoseChanges=0,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, visualAcceptance=True,
        browserReports=inspection['browserReports'], imagesActuallyViewed=source_images,
        retainedImagesActuallyViewed=retained_images, inspectionPreviewsActuallyViewed=inspection['inspectionSheetsActuallyViewed'],
        actualGroundContextPlot=ref(plot), observations=observations, publication=False, installationApproved=False)
    save(out / 'ROOT-PHYSICAL-REVIEW.json', common)
    save(out / 'ROOT-SOURCE-REVIEW.json', common)
    save(out / 'raw-support-negatives.json', raw_supports)
    module('garden_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'bounded-garden-terrace-three-original-source-physical-and-inspected-preview-review',
        list(dict.fromkeys(refs)), dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES,
        originalSourceReviewAccepted=True, sourceSpecificPhysicalInterpretationAccepted=True,
        identityAccepted=True, visualAcceptance=True, installationApproved=False, sourceGeometryChanges=0))


if __name__ == '__main__':
    main()
