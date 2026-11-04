"""Independently replay the six low-component paths to the original exposed deck.

Preserve the failed ordinary rim/compound-envelope results. This is geometric
evidence only, without architectural, support, identity or publication approval.
"""
import sys, uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_four_world_contact_paths_v1_20261023 import paths

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hkdi88343-original-deck-paths-v2-20261101'
RUNTIME = 'government-xl-hkdi88343-after-one-peking-current-v1-20261101-runtime'
ATTRS = 'government-xl-hkdi88343-after-one-peking-attributes-v1-20261101'
NATIVE = 'government-xl-cohort19-installed-native-contacts-v1-20261101'
SUPPORT = 'government-xl-hkdi88343-after-one-peking-support-v1-20261101'
FOUNDATIONS = 'government-xl-hkdi88343-after-one-peking-foundations-v1-20261101'
LOW = 'government-xl-hkdi88343-low-component-views-v2-20261101'
UID, PARENT = 'landsd/88343:0', 'landsd/22089:0'

def main():
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not out.exists()
    if '--owned' not in sys.argv:
        assert not local.exists()
        c = reservations.claim('hkdi-original-deck-paths-' + str(uuid.uuid4()),
            ['building:' + UID, 'building:' + PARENT, 'terrain:city/data/terrain.json'], batch=BATCH, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], local / 'reservation.json', [sys.executable, __file__, '--owned'])
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}
    def take(batch, name, path=None):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        f = path if path is not None else BASE / batch / name
        assert digest(f.read_bytes()) == pins[batch][str(f.relative_to(ROOT))]
        refs.append(f)
        return read(f)
    selection = take(RUNTIME, 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == UID)
    geom = next(r for r in take(RUNTIME, '', HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')['rows'] if r['uid'] == UID)
    child = next(r for r in take(ATTRS, 'attributes.json.gz')['rows'] if r['uid'] == UID)
    native_input = take(NATIVE, 'native-input.json.gz')
    native = next(r for r in native_input['rows'] if r['uid'] == PARENT)
    parent = next(r for r in take(NATIVE, 'native-attributes.json.gz')['rows'] if r['uid'] == PARENT)
    low = take(LOW, 'summary.json')
    foundation = take(FOUNDATIONS, 'summary.json')
    assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
    assert all(r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 and r['completeTerrainTriangles'] == r['triangles'] == 11866 for r in foundation['rows'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    start = digest(manifest.read_bytes())
    assert start == selection['manifestSHA256']
    cat = ROOT / native['cataloguePath']
    assert str(cat.relative_to(ROOT / '3d-viewer')) in read(manifest)['officialModelCatalogues']
    assert next(r for r in read(cat)['models'] if r['uid'] == PARENT) == native['entry']
    refs.extend([manifest, cat])
    assets = [ROOT / source['candidate']['path'], ROOT / native['path']]
    attrs = [child, parent]
    expected = [source['sourceSHA256'], native['entry']['sha256']]
    worlds = {}
    for uid, asset, attr, sha in zip([UID, PARENT], assets, attrs, expected):
        assert digest(asset.read_bytes()) == attr['sourceSHA256'] == sha
        refs.append(asset)
        index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds[uid] = {'original': decode_original_world_triangles(asset.read_bytes())}
        for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
            worlds[uid][mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[index]
    ground = np.asarray(geom['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    domain = unary_union([Polygon(t[:, [0, 2]]) for t in ground if Polygon(t[:, [0, 2]]).area > 0])
    ground_max = float(ground[:, :, 1].max())
    assert np.array_equal(np.asarray(geom['position']).reshape(-1, 3)[np.asarray(geom['index']).reshape(-1, 3)], worlds[UID]['literal'])
    results = []
    for mode in ['original', 'literal', 'leftF32', 'balancedF32']:
        tri, deck = worlds[UID][mode], worlds[PARENT][mode]
        diag = take(SUPPORT, mode + '/diagnostic.json.gz')
        contacts = take(NATIVE, '88343:0--22089:0--' + mode + '.json.gz')
        assert diag['sourceWorldSHA256ByUid'] == {UID: digest(tri.astype('<f8').tobytes()), PARENT: digest(deck.astype('<f8').tobytes())}
        assert diag['unresolved'] == diag['finitePaths'] == 6 and not diag['support']['passed']
        assert diag['support']['strictContacts'] == 0 and diag['support']['wallIntersections'] == 4
        replay = paths(tri, dict(targets=[dict(witness=r['witness'], incidentFaces=r['incidentFaces']) for r in diag['paths']], proof=contacts))
        assert replay == diag['paths']
        rows = []
        for r in replay:
            path = r['verifiedPath']
            assert path and path['withinEndpointHeight'] and path['maximumResidualM'] <= .001
            c = path['contact']
            assert c in contacts['contacts'] and c['dimension'] == 1 and c['sourceFaceB'] == 3896
            assert set(path['faces']) <= set(low['sourceFaces']) and set(r['incidentFaces']) <= set(low['sourceFaces'])
            face = deck[c['sourceFaceB']]
            normal = np.cross(face[1] - face[0], face[2] - face[0])
            assert abs(float(normal[1])) > 0 and np.all(face[:, 1] == face[0, 1])
            points = np.asarray(path['continuousPath'])
            assert domain.covers(MultiPoint(points[:, [0, 2]]).convex_hull)
            gap = float(face[:, 1].min()) - ground_max
            assert gap > 0
            rows.append(dict(witness=r['witness'], path=path, originalDeckFace=3896,
                deckHeightHKPD=float(face[0, 1]), conservativeDeckMinusAllCapturedGroundMaximumM=gap,
                completeFinitePathProjectionCoveredByActualGround=True))
        results.append(dict(mode=mode, paths=rows, sourceWorldSHA256=digest(tri.astype('<f8').tobytes()), nativeWorldSHA256=digest(deck.astype('<f8').tobytes()), rawOrdinarySupport=diag['support'], rawCompoundFoundation=diag['compoundFoundation']))
        save(out / (mode + '.json.gz'), results[-1])
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == start
    result = dict(uids=[UID, PARENT], sourceSHA256=expected[0], nativeSHA256=expected[1], currentManifestSHA256=start,
        fourWorldPathCounts=[len(r['paths']) for r in results], exactNativeDeckFace=3896, lowComponentFaces=low['sourceFaces'],
        allCurrentEarthFoundationsPassed=True, deckStrictlyAboveAllCapturedEarth=True,
        sourceGeometryChanges=0, sourcePoseChanges=0, thresholdChanges=0, sourceRoleAccepted=False,
        physicalAcceptance=False, installationApproved=False, publication=False,
        qualification='Six existing finite paths independently replay in every coordinate stream to exact original horizontal native deck3896. Current earth foundation passes separately. Raw zero strict rim contacts, four wall intersections, negative rim samples and failed full-platform compound-envelope results retained. No automatic support or architectural approval.')
    save(out / 'summary.json', result)
    refs.extend(HERE / f for f in ['original_four_world_contact_paths_v1_20261023.py', 'exact_packed_world_geometry_20261009.py'])
    module('hkdi_deck_paths_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'current-exact-original-low-component-exposed-deck-paths', refs, result)

if __name__ == '__main__': main()
