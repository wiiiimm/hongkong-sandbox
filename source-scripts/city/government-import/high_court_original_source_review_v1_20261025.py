"""Bind exact High Court source/placement evidence and individually inspected previews."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-government-court-caribbean-after-airport-'
BATCH = 'government-xl-high-court-after-airport-final-source-review-v1-20261025'
UID = 'landsd/263644:0'
SHA = '62285a058cf89dba5808eebd7a21c8236b61b28d1e7bf971138bc7103ed99e67'
RETAINED = 'landsd/181141:0'


def main():
    out = BASE / BATCH; assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(tag, filename='summary.json'):
        batch = P + tag + '-20261025'
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selected = take('runtime-v1', 'selection.json.gz')
    row = next(r for r in selected['rows'] if r['uid'] == UID)
    assert row['sourceSHA256'] == SHA and row['triangles'] == 15813
    asset = ROOT / row['candidate']['path']; assert digest(asset.read_bytes()) == SHA; refs.append(asset)
    assert row['candidate']['entry']['rootTranslation'] == [-834500, 0, 816500]
    assert row['candidate']['entry'].get('verticalPlacementOffsetHKPD', 0) == 0
    identity = take('identity-v1', '263644:0/identity.json')
    assert identity['originalOwnership']['sourceGraphVerified']
    assert identity['originalOwnership']['originalRootName'] == 'B348861552501063C0'
    assert identity['exactCurrentComponentRoute']['qualified']
    assert identity['exactWholeCellCoverage']['covered']
    assert identity['exactWholeCellCoverage']['wholeOriginalFacesAccounted'] == 15813
    spatial = identity['freshCurrentIdentity']
    assert spatial['exactObjectAndCSUID'] and spatial['targetCoveredBySourceProjection'] >= .995
    assert 12.27 < spatial['sourceExcessMaximumDistanceFromTargetM'] < 12.29
    assert 199.5 < spatial['sourceExcessCoveredByUnrelatedFormsM2'] < 199.6
    footprints = take('primary-records-v1', 'footprints.json')['features']
    official = next(f['attributes'] for f in footprints if f['attributes']['BuildingCSUID'] == '3488615525T20050430')
    assert official['BuildingNameEN'] == 'The High Court' and official['BaseHeight'] == 14
    # Batch structure records all belong to Caribbean Square, not this source.
    relations = take('primary-records-v1', 'relations.json')['features']
    assert not any(f['attributes']['BuildingCSUID'] == official['BuildingCSUID'] for f in relations)
    foundation = take('263644-foundations-v1'); assert foundation['establishedFoundationPolicyPassed']
    assert len(foundation['rows']) == 4
    for r in foundation['rows']:
        assert r['completeTerrainTriangles'] == r['triangles'] == 15813
        assert r['fullyBuriedTriangles'] == 2 and r['fullyBuriedUpwardTriangles'] == 0
        assert r['fullyBuriedAreaFraction'] <= .001
    ground = take('263644-complete-ground-v1'); assert len(ground['rows']) == 4
    for r in ground['rows']:
        assert r['negativeNonWallFaces'] == [8404, 8405, 8407, 8413, 8414]
        proof = take('263644-complete-ground-v1', r['mode'] + '-cap-paths.json.gz')['proof']
        assert len(proof['paths']) == 165
        assert [x['sourceFace'] for x in proof['paths'] if not x['hasExactSharedEdgeClearCapPath']] == list(range(8565, 8581))
    tri = decode_original_world_triangles(asset.read_bytes())
    for i in [8404, 8405, 8407, 8413, 8414]:
        n = np.cross(tri[i, 1] - tri[i, 0], tri[i, 2] - tri[i, 0]); assert n[1] / np.linalg.norm(n) < -.87
    walls = tri[list(range(8565, 8581))]
    normals = np.cross(walls[:, 1] - walls[:, 0], walls[:, 2] - walls[:, 0])
    assert np.max(np.abs(normals[:, 1]) / np.linalg.norm(normals, axis=1)) < .01
    assert walls[:, :, 1].max() <= official['BaseHeight']
    for tag in ['263644-lower-face-views-v1', '263644-wall-face-views-v1']:
        for r in take(tag)['regions']:
            path = ROOT / r['image']; assert digest(path.read_bytes()) == r['imageSHA256']; refs.append(path)
    take('263644-identity-views-v1')
    for name in ['whole-source-plan.png', 'whole-source-perspectives.png']:
        path = BASE / (P + '263644-identity-views-v1-20261025') / name
        assert digest(path.read_bytes()) == pins[P + '263644-identity-views-v1-20261025'][str(path.relative_to(ROOT))]; refs.append(path)
    continuous = next(r for r in take('continuous-v1')['rows'] if r['uid'] == UID)
    assert continuous['wholeSourceUncoveredFaces'] == 0 and continuous['upwardContinuousMinimumGapM'] >= -.5
    scope = take('complete-native-form-scope-v2')
    own = next(r for r in scope['rows'] if r['uid'] == UID)
    assert own['currentNativeActorsChecked'] == 6946
    forms = take('complete-native-form-scope-v2', '263644:0-forms.json.gz')
    byuid = {r['building']['uid']: r['building'] for r in forms}
    assert len(byuid) == len(forms) == 7 and RETAINED in byuid
    for u, f in byuid.items():
        if u != RETAINED: assert 'HIGH COURT' in f['name'].upper()
    natives = take('complete-scope-native-contacts-v2')
    pair = next(r for r in natives['rows'] if r['uid'] == UID and r['nativeUid'] == RETAINED)
    assert len(pair['modes']) == 4
    assert all(r['finiteContactPairs'] == r['positiveSurfaceContactPairs'] == r['areaContactPairs'] == 0 for r in pair['modes'])
    retained_entry = pair['rawCurrentNativeEntry']
    foreign = [r for r in take('foreign-contacts-v1')['rows'] if r['uid'] == UID]
    assert {r['foreignUid'] for r in foreign if any(m.get('positiveContactPairs', 0) for m in r['modes'] if m['mode'] != 'before-basic')} == {'landsd/90809:0', 'landsd/181146:0'}
    images, retained_images, reports = [], [], []
    for width in [390, 1280]:
        tag = '263644-unapproved-browser-v3'; report = take(tag, str(width) + '/staged-browser.json')
        assert report['passed'] and not report['errors']
        for records, target in [(report['views'], images), (report['retainedNativeOwnViews'], retained_images)]:
            for v in records:
                if 'time' not in v: continue
                assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
                if target is images:
                    assert v['uid'] == UID and v['sourceSHA256'] == SHA and v['solidAppearance']
                    assert v['pick'] == v['collision'] == UID
                else:
                    assert v['uid'] == RETAINED and v['sourceSHA256'] == retained_entry['sha256']
                    assert v['originalTriangles'] == retained_entry['triangles'] and not v['overflow']
                    assert all(v['meshVisibility']) and not any(v['wireframeFlags'])
                path = BASE / (P + tag + '-20261025') / str(width) / v['file']; refs.append(path)
                target.append(dict(uid=v['uid'], width=width, time=v['time'], path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
        path = BASE / (P + tag + '-20261025') / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    assert len(images) == len(retained_images) == 4
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; assert digest(manifest.read_bytes()) == selected['manifestSHA256']; refs.append(manifest)
    result = dict(uids=[UID], sourceSHA256ByUid={UID: SHA}, requiredOriginalAssembly={UID: SHA}, supportByUid={},
                  retainedNativeUids=[RETAINED], retainedNativeEntries={RETAINED: retained_entry},
                  retainedImagesActuallyViewed=retained_images, reviewer='ROOT', identityAccepted=True,
                  identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
                  currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())),
                  sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
                  completeFourWorldFoundations=True, completeCurrentNeighbourChecks=7, totalNeighbourForms=7,
                  leaseResources=sorted('building:' + u for u in byuid), terrainEdits=False, terrainGeometryChanges=0,
                  visualAcceptance=True, imagesActuallyViewed=images, browserReports=reports, originalSourceReviewAccepted=True,
                  rawIdentityReasonsRetained=identity['reasons'], rawSixteenWallPathFailuresRetained=True,
                  sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True,
                  installationApproved=False, observations=[
                      'Accept only the exact complete government High Court original. Source graph/root, unique ObjectID/CSUID route, whole GeoRef cell and exact primary footprint name establish identity. Own target coverage99.5503percent. Preserve raw12.2789mextent/199.5528m2foreign-footprint flags: original facade and lower access/annex interfaces extend into other retained HIGH COURT BUILDING footprints. ROOT inspected full source diagrams and actual previews. No blanket name-based ownership/suppression or generic threshold change.',
                      'Existing foundation policy passes all4worlds: complete15813faces,2buriedfaces,zero upward burial,0.000459091buried-area fraction (limit0.001). Continuous upward clearance-.369289m passes unchanged-.5mlimit; full source terrain coverage. Five negative nonwall facets are downward lower closures. All149otherwall cap paths pass;16raw failures form two eight-face vertical lower columns below recorded14mbase. ROOT inspected allfive lower diagrams. These authored below-grade column walls remain; no per-component engineering watertightness requirement or excavation solely to expose foundations.',
                      'All7current forms are bound, including Queensway181141 outside the earlier2mfootprint nomination. All four exact source/native contact modes have zero contacts and preserve raw existing native catalogue entry. Only positive BASICpairs90809/181146are retained High Court parts; source and BASIC contact diagnostics retained, no source suppression/base/height changes. Terrain is unchanged, so no neighbour terrain regression or invented patch.',
                      'ROOT actually opened all4new source and4retained-own desktop/mobile day/night exports. Source facade/roof/access readable; original material dark at night with legacy BASIC lit strips retained. V1retained views obscured by foreground BASIC;V2desktop improved butmobile wasfullyoccluded and rejected. V3retains opposite desktop angle andusesa highermobile retained camera, with every actor present. Existing Queensway native remains unchanged. Fresh live source ANDretained exports plus full6946oldasset/full521/globalBASIC/unchangedterrain readback remain mandatory.'
                  ])
    save(out / 'ROOT-SOURCE-REVIEW.json', result); save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    module('high_court_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'bounded-original-high-court-source-role-and-retained-neighbour-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__': main()
