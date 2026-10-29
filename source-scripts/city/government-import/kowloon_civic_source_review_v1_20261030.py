"""Bind ROOT's exact original-source interpretation to completed current evidence."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-kowloon-city-civic-five-after-fuying-'
BATCH = P + 'source-review-v1-20261030'
BROWSER = P + 'unapproved-atomic-private-browser-v2-20261030'
SHEETS = BASE / (P + 'preview-review-sheets-v1-20261030')


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def ref(path):
        return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
    def take(batch, filename):
        path = BASE / batch / filename
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert ref(path)['sha256'] == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    def summary(suffix):
        return take(P + suffix, 'summary.json')
    selection = take(P + 'full-five-floor-runtime-v1-20261030', 'selection.json.gz')
    sources = {r['uid']: r['sourceSHA256'] for r in selection['rows']}
    assert sorted(sources) == ['landsd/159177:0', 'landsd/230911:0', 'landsd/82290:0', 'landsd/82291:0', 'landsd/82292:0']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert ref(manifest)['sha256'] == selection['manifestSHA256']
    refs.append(manifest)
    identities = {}
    for row in selection['rows']:
        uid = row['uid']
        identity = take(P + 'identity-v1-20261029', uid.split('/')[1] + '/identity.json')
        route, owner = identity['exactCurrentComponentRoute'], identity['originalOwnership']
        assert identity['sourceSHA256'] == sources[uid]
        assert owner['sourceGraphVerified'] and owner['originalRootName'] == row['modelId']
        assert route['qualified'] and not route['reasons']
        building, official = route['source']['building'], route['official']
        assert official['objectId'] == building['objectId'] and official['buildingCSUID'] == building['buildingCSUID']
        tile = ROOT / '3d-viewer' / route['source']['tile']
        assert digest(tile.read_bytes()) == route['source']['tileSHA256']
        assert [b for b in read(tile)['buildings'] if b.get('uid') == uid or b.get('buildingCSUID') == building['buildingCSUID']] == [building]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == sources[uid]
        refs += [tile, asset]
        identities[uid] = dict(modelId=row['modelId'], buildingCSUID=building['buildingCSUID'], rawReasons=identity['reasons'])
        foundation = summary(uid.split('/')[1].replace(':', '-') + '-floor-return-foundations-v1-20261030')
        assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
        assert all(r['completeTerrainTriangles'] == row['triangles'] and r['fullyBuriedUpwardTriangles'] == 0 and r['establishedFoundationPolicyPassed'] for r in foundation['rows'])
    for name, count in [('civic', 76), ('peninsula', 53)]:
        attachment = summary(name + '-finite-self-attachment-v1-20261030')
        assert len(attachment['rows']) == 4
        assert all(r['disconnected'] == 0 and r['witnesses'] == r['finiteAttachmentPaths'] == r['pathsWithinEndpointHeight'] == count for r in attachment['rows'])
    foreign = summary('full-five-foreign-contacts-v1-20261030')
    assert foreign['requiredCoRenderedOriginals'] == sorted(sources) and not foreign['independentlyMeasuredOverlappingNativePairs']
    assert len(foreign['rows']) == 1 and foreign['rows'][0]['foreignUid'] == 'landsd/262047:0'
    assert all(m['allFiniteContactPairs'] == 0 and m['projectedOverlapAreaM2'] == 0 for m in foreign['rows'][0]['modes'])
    for name, count in [('auxiliary', 61), ('podium-boundary', 0), ('upper-boundary', 0)]:
        roles = summary(name + '-contact-roles-v1-20261030')
        assert len(roles['rows']) == 4 and all(r['contactCount'] == count for r in roles['rows'])
        if count:
            assert all(r['roles'] == {'transverse-surface-crossing': 61} for r in roles['rows'])
    scope = take(P + 'floor-return-scope-v1-20261030', 'scope.json')
    assert not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps'] == 0
    forms = summary('full-five-form-checks-v1-20261030')
    assert forms['forms'] == 8 and not forms['flagged'] and forms['requiredCoRenderedOriginals'] == sorted(sources)
    fallback = summary('base-only-regression-v1-20261030')
    roof = summary('basic-roof-support-v3-20261030')
    assert fallback['allCurrentBasicsChecked'] and fallback['originalsAvailable'] is False
    assert {r['uid'] for r in fallback['flagged']} == {'landsd/82290:0', 'landsd/159177:0'}
    assert roof['actualBasicMeshes'] == 8 and roof['rawFlagsRetained']
    for row in roof['rows']:
        assert row['exactSourcePlanesEqual'] and row['actualFloat32PlanesEqual']
        assert not row['lowerRawRegressions'] and row['afterTerrainBelowUpperAtEveryGuardSample']
    # Preserve the exact pre-existing civic Float32 triangulation sliver, not a tolerance pass.
    assert roof['rows'][0]['uncoveredBottomAreaM2'] == 1.0290911199861696e-06
    assert roof['rows'][0]['exactActualMeshCoverage'] is False and roof['rows'][1]['exactActualMeshCoverage'] is True
    life = take(P + 'atomic-lifecycle-v1-20261030', 'browser/report.json')
    assert life['passed'] and not life['pageErrors'] and len(life['cases']) == 6
    assert {r['failedUid'] for r in life['cases']} == {None, *sources}
    for case in life['cases']:
        assert case['baseOnlyRestoredCompleteGroup'] and case['completeGroupEvicted'] and case['audit']['frames'] > 0 and not case['audit']['violations']
        assert {r['uid']: r['sha256'] for r in case['sources']} == sources
        assert [r['phase'] for r in case['basicLifecycle']] == (['failed-download'] if case['failedUid'] else []) + ['original-active', 'base-only', 'auto-restored', 'evicted-return-base-only']
        if case['failedUid']:
            assert case['failureKeptAllBasics']
    images, reports = [], []
    for width in [1280, 390]:
        path = BASE / BROWSER / str(width) / 'staged-browser.json'
        report = take(BROWSER, str(width) + '/staged-browser.json')
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 10
        for view in views:
            assert view['sourceSHA256'] == sources[view['uid']] and view['fullyFramed'] and view['solidAppearance'] and not view['fallbackFaces']
            assert view['pick'] == view['collision'] == view['uid']
            image = BASE / BROWSER / str(width) / view['file']
            assert ref(image)['sha256'] == pins[BROWSER][str(image.relative_to(ROOT))]
            refs.append(image)
            images.append(ref(image))
        reports.append(ref(path))
    sheet_inputs = read(SHEETS / 'inputs.json')
    assert {r['path']: r['sha256'] for r in sheet_inputs['images']} == {r['path']: r['sha256'] for r in images}
    refs += list(SHEETS.iterdir())
    interpretation = (
        'Exact government roots, current object/CSUID routes and unique viewer records identify all five unchanged original components. '
        'The two civic footprint-excess warnings remain verbatim; approximate BASIC footprints do not trim the originals. '
        'The 76 civic and53 Peninsula strict roof-ray warnings have exact finite endpoint-bounded original self/contact paths in every representation; '
        'these support the faithful opaque graphics assembly, not engineering certification or general roof-ray acceptance. '
        'The auxiliary ten-face component intersects its own source podium at61 transverse facet pairs; retain the original authored opaque junction, '
        'without inventing its architectural use or welding geometry. No civic/adjacent Peninsula boundary contact or genuine foreign surface contact exists. '
        'The unchanged BASIC upper bodies meet the unchanged lower roof planes exactly. The civic pre-existing Float32 triangulation sliver remains unfilled '
        'and explicitly nonzero; it is not introduced by the terrain. Both lower BASIC bodies have zero new regressions and the new ground stays below '
        'both upper bases at every original guard sample. Accept the raw upper-to-ground flags only as roof-supported compound context for this exact scene. '
        'ROOT viewed all20 wider desktop/mobile day/night exports through four labelled receipt-bound sheets, plus two full-resolution daytime source views. '
        'Full originals, blank source walls, roof equipment, lower steps and surrounding BASICs remain; no synthetic window skin or facade redesign. '
        'All five sources must activate atomically; every failed peer restores all five BASIC counterparts. Exact current private lifecycle, final guarded '
        'publication, actual installed HTTP lifecycle and independent whole-catalogue/all521 readback remain separate requirements.')
    common = dict(uids=sorted(sources), sourceSHA256ByUid=sources, currentManifest=ref(manifest),
                  identityAccepted=True, identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
                  sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
                  visualAcceptance=True, completeFourWorldFoundations=True, completeCurrentNeighbourChecks=8,
                  allFiveCurrentFoundationPoliciesPassed=True, requiredCoRenderedOriginals=sorted(sources), baseOnlyFallbackReviewed=True,
                  retainedBasicSupportDependencies=[], imagesActuallyViewed=images, browserReports=reports,
                  rawIdentityProofs=identities, rawBaseOnlyFlags=fallback['flagged'], rawBasicRoofMeasurement=roof['rows'],
                  sourceGeometryChanges=0, sourcePoseChanges=0, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                  installationApproved=False, qualification=interpretation)
    save(out / 'ROOT-SOURCE-REVIEW.json', common)
    save(out / 'ROOT-PHYSICAL-REVIEW.json', {**common, 'physicalAcceptance': True})
    module('civic_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'bounded-current-five-original-source-physical-visual-review', refs, common)


if __name__ == '__main__':
    main()
