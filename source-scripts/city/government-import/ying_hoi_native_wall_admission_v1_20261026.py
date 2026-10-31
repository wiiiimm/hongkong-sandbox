"""Exact Ying Hoi source/floor profile; no other source or native is admitted.

The ordinary terrain policy is unchanged. The fifteen vertical facets below the
owned podium envelope require actual native floor roots and finite source paths;
the failed roof-cap and direct-rim verdicts are retained as separate evidence.
"""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from pool_incident_wall_contacts_v1_20261017 import closest
from original_retained_own_views_contract_v1_20261025 import verify as verify_views
from primrose_compound_foundation_v2_20261015 import module

UID = 'landsd/207957:0'
PARENT = 'landsd/205663:0'
SOURCE_SHA = '82e6a654d9ac5451271f8fce1cf82c0a234dd9e67649a47f4e51bfffeb2088be'
PARENT_SHA = '97f824a1699c079e1d0e98962dd76175e384500340bbf22a732f5b92730ac502'
WALLS = [2, 3, 4, 5, 10, 12, 13, 24, 26, 27, 2842, 2843, 2851, 2852, 3035]
MODES = ['original', 'literal', 'leftF32', 'balancedF32']
BASE = ROOT / 'docs/astra-city/government-import'


def verify_paths(tri, podium, rim, wall):
    """Replay all raw warnings, exact root facets and every finite path."""
    assert tri.shape == (10682, 3, 3) and podium.shape == (908, 3, 3)
    assert rim['sourceWorldSHA256'] == wall['sourceWorldSHA256'] == digest(tri.tobytes())
    assert rim['supportWorldSHA256'] == wall['supportWorldSHA256'] == digest(podium.tobytes())
    anchors = rim['canonicalStrictRoots']
    assert len(anchors) == rim['canonicalStrictAnchorCount'] == 462
    assert rim['noIntercomponentJoins'] and rim['originalEndpointHeightGatePreserved']
    for root in anchors:
        assert root['strictAccepted'] is True and -.1 <= root['gap'] <= 1
        provider = root['provider']
        face = podium[provider['faceIndex']]
        assert np.array_equal(face, np.asarray(provider['vertices']))
        point = np.asarray(root['position'])
        floor_point = point.copy()
        floor_point[1] = root['supportHeight']
        assert root['gap'] == point[1] - root['supportHeight']
        assert provider['height'] == root['supportHeight']
        assert np.linalg.norm(closest(floor_point, face) - floor_point) <= .001
    assert len(rim['rows']) == 36 and len(wall['rows']) == 15
    assert wall['rawCapProof']['negativeSourceFaces'] == WALLS
    assert wall['rawCapProof']['negativeNonWallFaces'] == wall['excludedNonWallFaces'] == []
    assert wall['rawCapProof']['allAffectedHavePaths'] is False
    assert [r['witness']['sourceFace'] for r in wall['rows']] == WALLS
    normals = np.cross(tri[WALLS, 1] - tri[WALLS, 0], tri[WALLS, 2] - tri[WALLS, 0])
    assert np.all(np.linalg.norm(normals, axis=1) > 0) and np.all(normals[:, 1] == 0)
    for detail in [rim, wall]:
        rows = detail['rows']
        targets = [dict(witness=r['witness'], incidentFaces=r['incidentFaces']) for r in rows]
        reproduced = attachment_paths(tri, dict(targets=targets, proof=dict(contacts=[])), [], strict_anchors=anchors)
        assert reproduced == rows
        assert all(r['hasUnrestrictedFiniteAttachment'] and r['passesExistingEndpointHeight']
                   and r['riseAboveEndpointsM'] == 0 and r['maximumResidualM'] <= .001 for r in rows)
        assert all(r['terminal']['kind'] == 'canonical-strict-vertical-support-anchor' for r in rows)
    return dict(strictNativeFloorAnchors=462, replayedRimPaths=36, replayedVerticalWallPaths=15,
                sourceGeometryChanges=0, directRimVerdictRetained=False, roofCapVerdictRetained=False)


def replay(config, review):
    refs = [Path(__file__), HERE / 'original_face_attachment_minimax_v2_20261024.py',
            HERE / 'pool_incident_wall_contacts_v1_20261017.py', HERE / 'exact_packed_world_geometry_20261009.py',
            HERE / 'original_retained_own_views_contract_v1_20261025.py']
    pins = {}

    def take(batch, name, local=False):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = (HERE / 'local' / batch if local else BASE / batch) / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    assert config['sources'] == review['sourceSHA256ByUid'] == {UID: SOURCE_SHA}
    assert config['retainedNativeUids'] == [PARENT]
    assert config['nativeAvailabilityDependenciesByUid'] == review['runtimeAvailabilityDependenciesByUid'] == {UID: PARENT}
    assert review['retainedBasicSupportDependencies'] == []
    assert review['sourceGeometryChanges'] == review['sourcePoseChanges'] == 0 and review['terrainEdits'] is False
    assert review['rawCanonicalSupportPassed'] is False and review['rawCompoundCapPassed'] is False
    assert review['acceptedOwnedNativeInteriorWallFaces'] == WALLS
    assert all(review[k] is True for k in ['sourceSpecificPhysicalInterpretationAccepted', 'completeNeighbourInterpretationAccepted', 'identityAccepted', 'visualAcceptance'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_hash = digest(manifest.read_bytes())
    assert review['currentManifest'] == dict(path=str(manifest.relative_to(ROOT)), sha256=manifest_hash)
    refs.append(manifest)
    selection = take(config['runtime'], 'selection.json.gz')
    assert selection['manifestSHA256'] == manifest_hash
    row = next(r for r in selection['rows'] if r['uid'] == UID)
    attrs = take(config['attributes'], 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attr = next(r for r in attrs['rows'] if r['uid'] == UID)
    native_attr = next(r for r in take(config['nativeContext'], 'native-attributes.json.gz')['rows'] if r['uid'] == PARENT)
    current = {}
    for url in read(manifest)['officialModelCatalogues']:
        cat = ROOT / '3d-viewer' / url
        for entry in read(cat)['models']:
            assert entry['uid'] not in current
            current[entry['uid']] = (entry, cat.parent / entry['asset'])
    assert len(current) == config['currentNativeActors'] == 6967 and UID not in current
    parent, parent_asset = current[PARENT]
    assert review['retainedNativeEntries'] == {PARENT: parent}
    assert parent['publicationApproved'] is True and parent['sha256'] == PARENT_SHA
    strict = take(config['supportBinding'], 'summary.json')
    assert strict['allFourModesPassed'] is False and strict['installedNativeEntry'] == parent
    assert strict['sourceSHA256ByUid'] == {UID: SOURCE_SHA, PARENT: PARENT_SHA}
    source_asset = ROOT / row['candidate']['path']
    assert digest(source_asset.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256'] == SOURCE_SHA
    assert digest(parent_asset.read_bytes()) == native_attr['sourceSHA256'] == PARENT_SHA
    refs.extend([source_asset, parent_asset])
    identity = take(config['identity'], '207957:0/identity.json')
    assert identity['passed'] and identity['sourceSHA256'] == SOURCE_SHA and all(identity['proof'].values())
    assert identity['proof'] == review['identityProof']
    metrics = take(config['runtime'], 'metrics.json')
    metric = next(r for r in metrics['rows'] if r['uid'] == UID)
    policy = module('ying_hoi_native_wall_ordinary_policy', HERE / 'acceptance-policy.py')
    assert policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=SOURCE_SHA,
                               identityProof=identity['proof']), metric, metrics['profiles']['mobile']) == ['ground-contact-unresolved']
    refs.append(HERE / 'acceptance-policy.py')
    scope = take(config['scope'], 'summary.json')
    assert scope['currentManifestSHA256'] == manifest_hash
    scoped = [r for r in scope['rows'] if r['uid'] == UID]
    assert len(scoped) == 1 and scoped[0]['currentNativeActorsChecked'] == 6967
    assert {r['uid'] for r in scoped[0]['nearbyNativeActors']} == {PARENT}
    forms = take(config['scope'], '207957:0-forms.json.gz')
    assert {r['building']['uid'] for r in forms} == {UID, PARENT}
    assert all(r['building']['name'] == 'Ying Hoi House' for r in forms)
    assert set(review['leaseResources']) == {'building:' + UID, 'building:' + PARENT}
    for form in forms:
        tile = ROOT / '3d-viewer' / form['tile']
        assert digest(tile.read_bytes()) == form['tileSHA256']
        assert next(f for f in read(tile)['buildings'] if f['uid'] == form['building']['uid']) == form['building']
        refs.append(tile)
    foundation = take(config['foundation'], 'summary.json')
    assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
    assert all(r['completeTerrainTriangles'] == r['triangles'] == 10682
               and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0
               and r['minimumGapM'] > 0 for r in foundation['rows'])
    compound = take(config['compound'], 'summary.json')
    assert len(compound['rows']) == 4
    assert all(r['completeSourceFaces'] == 10682 and r['exactAffectedFaces'] == WALLS
               and r['negativeNonWallFaces'] == [] and r['allAffectedWallLike']
               and r['compoundCapPathsPassed'] is False for r in compound['rows'])
    source_index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    native_index = np.asarray(native_attr['completeOriginalIndex']).reshape(-1, 3)
    source_worlds = dict(original=decode_original_world_triangles(source_asset.read_bytes()))
    native_worlds = dict(original=decode_original_world_triangles(parent_asset.read_bytes()))
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
        source_worlds[mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[source_index]
        native_worlds[mode] = np.asarray(native_attr[field], dtype='<f8').reshape(-1, 3)[native_index]
    for mode in MODES:
        rim = take(config['rimPaths'], mode + '.json.gz')
        wall = take(config['wallPaths'], mode + '.json.gz')
        verify_paths(source_worlds[mode], native_worlds[mode], rim, wall)
    foreign = take(config['foreign'], 'summary.json')
    assert UID in foreign['uids'] and not any(r['uid'] == UID for r in foreign['rows'])
    native = [r for r in take(config['nativeContext'], 'summary.json')['rows'] if r['uid'] == UID]
    assert len(native) == 1 and native[0]['nativeUid'] == PARENT and native[0]['rawCurrentNativeEntry'] == parent
    assert native[0]['sourceSHA256'] == SOURCE_SHA and native[0]['nativeSHA256'] == PARENT_SHA
    assert [m['finiteContactPairs'] for m in native[0]['modes']] == [636, 592, 636, 636]
    for mode in MODES:
        raw = take(config['nativeContext'], '207957:0--205663:0--' + mode + '.json.gz')
        assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0
        assert all(c['dimension'] < 2 for c in raw['contacts'])
    roles = take(config['nativeRoles'], 'summary.json')
    assert len([r for r in roles['rows'] if r['uid'] == UID and r['nativeUid'] == PARENT]) == 4
    fallback = take(config['nativeFallbackContext'], 'summary.json')
    fallback = [r for r in fallback['rows'] if r['uid'] == UID]
    assert len(fallback) == 1 and fallback[0]['rawCurrentNativeEntry'] == parent
    assert all(m['finiteContactPairs'] == 0 for m in fallback[0]['modes'] if m['mode'] != 'before-basic')
    fail = take(config['nativeDependencyFailure'], 'browser.json')
    assert fail['passed'] and not fail['errors'] and fail['uid'] == UID and fail['parentUid'] == PARENT
    assert fail['sourceSHA256'] == SOURCE_SHA and fail['parentSHA256'] == PARENT_SHA
    assert fail['deniedParentRequests'] > 0 and fail['successfulParentRequests'] > 0
    f = fail['failed']
    assert f['parentFailed'] and not f['active'] and not f['parentActive'] and f['basicLoaded']
    assert not f['basicHidden'] and not f['detailSuppressed'] and f['basicGroupVisible'] and f['ownFeaturePresent']
    expected = [dict(uid=PARENT, state='installed', buildingCSUID=parent['buildingCSUID'], sha256=PARENT_SHA)]
    assert f['dependencies'] == expected
    assert {r['uid']: r['sourceSHA256'] for r in fail['recovered'] if r['active'] and r['visible']} == {UID: SOURCE_SHA, PARENT: PARENT_SHA}
    cat = take(config['browser'], 'catalogue.json', local=True)
    browser = read(BASE / config['browser'] / 'result.json')
    assert browser['allBrowserDiagnosticsPassed'] and browser['proposedSupportByUid'] == {UID: PARENT}
    assert len(cat['models']) == 1 and cat['models'][0]['uid'] == UID and cat['models'][0]['sha256'] == SOURCE_SHA
    assert cat['models'][0]['supportDependencies'] == expected
    image_refs = review['imagesActuallyViewed'] + review['retainedImagesActuallyViewed']
    assert len(review['imagesActuallyViewed']) == len(review['retainedImagesActuallyViewed']) == 4
    assert len({r['path'] for r in image_refs}) == 8
    assert len(review['browserReports']) == 2
    for report in review['browserReports']:
        path = ROOT / report['path']
        assert digest(path.read_bytes()) == report['sha256']
        r = read(path)
        assert r['passed'] and not r['errors']
        views = r['retainedNativeOwnViews']
        assert verify_views(views, {PARENT: parent}, widths=(views[0]['width'],))
        for v in [v for v in r['views'] if 'time' in v] + views:
            image = path.parent / v['file']
            assert dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes())) in [dict(path=i['path'], sha256=i['sha256']) for i in image_refs]
            refs.append(image)
        refs.append(path)
    wall_view = take(config['wallViews'], 'summary.json')
    assert [r['faceIndex'] for r in wall_view['rows']] == WALLS
    image = BASE / config['wallViews'] / 'negative-wall-native-floor-roots.png'
    assert review['wallFloorImageActuallyViewed'] == dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes()))
    refs.append(image)
    assert digest(manifest.read_bytes()) == manifest_hash
    return list(dict.fromkeys(refs))
