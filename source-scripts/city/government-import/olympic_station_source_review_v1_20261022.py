"""Bind exact original source, contact, full neighbour and viewed browser evidence."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-olympic-station-qualified-source-review-v1-20261022'
UID = 'landsd/81242:0'


def main():
    doc = BASE / BATCH
    assert not doc.exists()
    refs, bound = [Path(__file__)], {}

    def take(batch, name):
        if batch not in bound:
            bound[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == bound[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    ref = lambda p: dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
    runtime = 'government-xl-olympic-station-band-runtime-v1-20261022'
    selection = take(runtime, 'selection.json.gz')
    row = selection['rows'][0]
    assert row['uid'] == UID
    sha = row['sourceSHA256']
    identity = take('government-xl-olympic-station-source-identity-review-v1-20261022', 'ROOT-IDENTITY-REVIEW.json')
    assert identity['identityOnlyApproved'] and identity['sourceSHA256'] == sha
    metrics = take(runtime, 'metrics.json')
    m = metrics['rows'][0]
    assert m['sourcePreserved'] and m['sourceSHA256'] == sha and m['missingTerrain'] == 0 and m['maxSamplerDelta'] <= .004
    assert all(m['budget'][k] <= metrics['profiles']['mobile'][k] for k in ['triangles', 'geometryBytes', 'residentBytes', 'drawCalls'])
    foundation = take(runtime, '81242:0.json')['foundation']
    assert foundation['completeTerrainTriangles'] == foundation['triangles'] == 14051
    assert foundation['fullyBuriedTriangles'] == foundation['fullyBuriedUpwardTriangles'] == 0
    ctx = take('government-xl-olympic-station-band-continuous-v1-20261022', '81242:0.json.gz')
    assert ctx['wholeSourceUncoveredFaces'] == 0 and ctx['affectedWallFaces'] == [5024]
    walls = take('government-xl-olympic-station-original-wall-paths-v2-20261022', 'paths.json.gz')
    assert walls['allAffectedWallsHaveRoles'] and len(walls['faces']) == 1
    assert walls['faces'][0]['sourceFace'] == 5024 and walls['faces'][0]['verifiedRoleNecessaryConditions']
    transfer = take('government-xl-olympic-four-stream-transport-v1-20261022', 'summary.json')
    assert len(transfer['rows']) == 4 and all(r['ordinaryContinuousClearanceLowerBoundM'] >= -.5 and r['wholeCoverageTransportedFromSameProjection'] for r in transfer['rows'])
    rim = take('government-xl-olympic-rim-four-stream-replay-v1-20261022', 'summary.json')
    assert rim['allPathsPassed'] and len(rim['rows']) == 4
    assert all(r['originalSamples'] == 49447 and r['raisedOrBuriedRimWarnings'] == r['verifiedPaths'] == 53 and not r['failedPaths'] for r in rim['rows'])
    nearbatch = 'government-xl-olympic-station-band-neighbours-v1-20261022'
    near = take(nearbatch, 'summary.json')
    unchanged = take('government-xl-olympic-hoi-yu-unchanged-terrain-v1-20261022', 'summary.json')
    assert not near['basicFlags'] and near['forms'] == 613
    assert unchanged['terrainFacetMultisetsIdentical'] and unchanged['identicalOrientedFloat32TerrainFacets'] == 1879
    assert set(near['nativeResolved']) | {unchanged['checkedNativeUid']} == set(near['requiredNativeUids'])
    assert len(near['requiredNativeUids']) == 47
    assert all(r['terrain']['newlyWhollyBuried'] == r['terrain']['newlyUpwardWhollyBuried'] == 0 for r in near['nativeRows'])
    take(nearbatch, 'native-neighbour-checks.json')
    foreign = take('government-xl-olympic-station-full-foreign-intersections-v1-20261022', 'summary.json')
    assert foreign['allNominatedNativeActorsAccounted']
    scope = foreign['completeCurrentActorScopePlan']
    assert scope['allCurrentNativeActors'] == 6841 and scope['touchingNativeUids'] == ['landsd/265848:0']
    assert all(r.get('exactIntersectionCount', 0) == 0 for r in foreign['reports'])
    # Check all nominated BASIC polygons directly, beyond their conservative boxes.
    attrs = take('government-xl-olympic-station-original-attributes-v1-20261022', 'attributes.json.gz')['rows'][0]
    tri = np.asarray(attrs['completeLiteralWorldPosition']).reshape(-1, 3)[np.asarray(attrs['completeOriginalIndex']).reshape(-1, 3)]
    projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
    forms = take('government-xl-olympic-station-foreign-scope-plan-v1-20261022', 'forms.json.gz')
    separation = []
    assert len(forms) == scope['candidateForeignForms'] == 4
    for item in forms:
        b = item['building']
        poly = shapely.Polygon(b['rings'][0], b['rings'][1:])
        distance = float(shapely.distance(projection, poly))
        assert distance > 1 and shapely.disjoint(projection, poly)
        separation.append(dict(uid=b['uid'], installedNative=item['isInstalledNative'], projectedSeparationM=distance))
    save(doc / 'current-form-separation.json', separation)
    images, reports = [], []
    for browser, width in [('government-xl-olympic-station-private-browser-v1-20261022', 1280),
                           ('government-xl-olympic-station-private-mobile-v1-20261022', 390)]:
        report = take(browser, 'staged-browser.json')
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 2
        assert all(v['pick'] == v['collision'] == UID and v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces'] and v['sourceSHA256'] == sha for v in views)
        assert report['localJointViews']
        if width == 390:
            assert any(v.get('phase') == 'failed-download' and v['fallbackRetained'] for v in report['views'])
        reports.append(ref(BASE / browser / 'staged-browser.json'))
        files = [f'staged-landsd-81242-0-{width}-{t}.png' for t in ['1500', '2200']]
        if width == 1280:
            files += ['staged-local-joint-olympic-north-neighbour-1280.png',
                      'staged-retained-own-landsd-265848-0-1280-1500.png',
                      'staged-retained-own-landsd-265851-0-1280-1500.png']
        for name in files:
            p = BASE / browser / name
            assert digest(p.read_bytes()) == bound[browser][str(p.relative_to(ROOT))]
            refs.append(p)
            images.append(ref(p))
    patch = take('government-xl-olympic-facet-band-return-v1-20261022', 'summary.json')
    precision = take('government-xl-olympic-band-anchor-precision-v1-20261022', 'summary.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    review = dict(uids=[UID], sourceSHA256ByUid={UID: sha}, currentManifest=ref(manifest), reviewer='Codex ROOT',
                  identityAccepted=True, identityProof=identity['identityProof'],
                  sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
                  foreignContactContextAccepted=True, visualAcceptance=True, completeFourWorldFoundations=True,
                  completeCurrentNeighbourChecks=613, checkedNativeUids=near['requiredNativeUids'],
                  imagesActuallyViewed=images, browserReports=reports, rawStrictFailuresRetained=True,
                  sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False,
                  physicalBasis=[
                      'All14051 original faces are terrain-covered, with zero wholly buried or upward wholly buried faces. Every ordinary source point retains the existing -.5m continuous clearance in all four source representations.',
                      'Only original face5024 crosses the continuous clearance threshold. Accept its explicit steep wall role: exposed original wall, unchanged exact shared-edge path to a clear upward roof, independently replayed in all four source representations. This is not a new wall or a whole-source clearance waiver.',
                      'All53 raised original rim warnings have actual same-source finite-face paths to independently sampled strict grade anchors. Every warning/sample lineage, finite path,1mm residual,own endpoint-height ceiling and strict -.1..+.1m anchor band passes in all four streams. Raw925rim/49447sample metrics remain unchanged.',
                      'All613 current base forms pass changed-terrain checks.46native actors pass directly; HoiYu177605 has exactly1879unchanged oriented actual terrain facets across its full four-world bounds. Its existing support warning is retained without reapproval.',
                      'The91913face private terrain replaces the existing retained23source patch. Its2moutside-building strip blends corresponding original facets and actual root-DEM gap facets, preserving layered original outer surfaces.3619boundary anchor occurrences are separately plane/Float32 precision checked. This is scripted terrain work, not building geometry editing.'
                  ], foreignContactBasis='Complete6841native four-world bounds and all current form tiles nominate one native265848 and four forms. Full exact native source pair tests have zero finite intersections in every distinct stream pairing. All four actual form polygons are separated from the source projection by32m or more. No new native support dependency, common ownership or general collision exemption is required.',
                  visualLimitations='ROOT inspected desktop/mobile day/night station exports, focused footbridge-area view and retained day views. Original station colours are retained; no invented windows or night lighting. Mobile/UI and neighbouring tower occlusion remain. Browser checks are local staged evidence, not measured mobile hardware FPS or publication.')
    save(doc / 'ROOT-SOURCE-REVIEW.json', review)
    save(doc / 'ROOT-PHYSICAL-REVIEW.json', review)
    replacement = patch['candidate']['replaces']
    candidate = read(ROOT / patch['candidate']['path'])
    native = dict(status='approved-for-integration', supersededURL=replacement['url'],
                  supersededSHA256=replacement['sha256'], replacementSHA256=patch['candidate']['sha256'],
                  sourceGeometryChanged=False, aiCalls=0, modelGeometryChanges=0,
                  retainedUids=replacement['retainedUids'], replacementTargetUids=candidate['meta']['targetUids'],
                  fullMeshCheck=ref(BASE / nearbatch / 'native-neighbour-checks.json'),
                  qualification='Complete613form/47native scope:46direct unchanged-guard passes plus exact1879facet HoiYu unchanged-terrain proof. Retains all23superseded source actors; no legacy flags reapproved. Source-specific contact and original wall review separately bound.')
    save(doc / 'native-replacement-review.json', native)
    module('olympic_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'qualified-unchanged-original-source-contact-and-current-neighbour-review', refs, review)


if __name__ == '__main__':
    main()
