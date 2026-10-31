"""Exact excluded-terrain checks and complete current wall foreign separation.

Necessary wall-role evidence only; no changed tolerance or installation approval.
"""
from fractions import Fraction
from pathlib import Path
import uuid
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify

BATCH = 'government-xl-nam-cheong-complete-vertical-ground-and-wall-scope-v1-20261023'
RUNTIME = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
ATTR = 'government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023'
REUSE = 'government-xl-nam-cheong-current-exact-context-reuse-v1-20261023'
SCOPE = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-scope'
INVENTORY = 'government-xl-after-island-current-inventory-v1-20261023'
GRADE = 'government-xl-nam-cheong-wall-grade-path-v2-20261023'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / BATCH
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for name in [RUNTIME, ATTR, REUSE, SCOPE, INVENTORY, GRADE]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    def take(name, path):
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(RUNTIME, base / RUNTIME / 'selection.json.gz')
    geometry = {r['uid']: r for r in take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')['rows']}
    attributes = take(ATTR, base / ATTR / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attributes['rows']}
    reuse = take(REUSE, base / REUSE / 'summary.json')
    assert reuse['currentManifestSHA256'] == selection['manifestSHA256']
    inventory = take(INVENTORY, base / INVENTORY / 'complete-bounds.json.gz')
    assert len(inventory['rows']) == len({r['uid'] for r in inventory['rows']}) == 6860
    forms = take(SCOPE, base / SCOPE / 'form-obligations.json.gz')
    region = take(SCOPE, base / SCOPE / 'scope.json')
    assert len(forms) == region['intersectingForms'] == 47
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == selection['manifestSHA256']
    manifest = read(manifestpath)
    refs.append(manifestpath)
    catalogues = {}
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == pins[INVENTORY][str(path.relative_to(ROOT))]
        catalogues[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        refs.append(path)
    for path, sha in inventory['currentFormTileHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    lease = reservations.claim('nam-complete-ground-' + str(uuid.uuid4()), ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert lease['ok']
    lease = lease['reservation']
    results, wallrows = [], []
    try:
        for selected in selection['rows']:
            uid = selected['uid']; attr = attrs[uid]; g = geometry[uid]
            asset = ROOT / selected['candidate']['path']
            assert digest(asset.read_bytes()) == selected['sourceSHA256'] == attr['sourceSHA256'] == g['sourceSHA256']
            refs.append(asset)
            ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
            modes = dict(original=decode_original_world_triangles(asset.read_bytes()),
                         literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1, 3)[ix],
                         left=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1, 3)[ix],
                         balanced=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1, 3)[ix])
            ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
            projected = shapely.area(shapely.polygons(ground[:, :, [0, 2]]))
            excluded = np.flatnonzero(projected <= 1e-10)
            assert np.all(projected[excluded] == 0)
            for modeindex, (mode, triangles) in enumerate(modes.items()):
                assert len(triangles) == selected['triangles']
                tmin, tmax = triangles[:, :, [0, 2]].min(1), triangles[:, :, [0, 2]].max(1)
                proofs, negatives = [], []
                for groundface in excluded:
                    face = ground[groundface]; xz = face[:, [0, 2]]
                    ids = np.flatnonzero(np.all(tmax >= xz.min(0), axis=1) & np.all(tmin <= xz.max(0), axis=1))
                    for sourceface in ids:
                        proof = verify(triangles[sourceface], face)
                        record = dict(sourceFace=int(sourceface), groundFace=int(groundface), proof=proof)
                        proofs.append(record)
                        if proof['exactClosedHorizontalProjectionsMeet'] and Fraction(proof['exactMinimumFiniteColumnGapM']) < Fraction(-1, 2):
                            negatives.append(dict(sourceFace=int(sourceface), groundFace=int(groundface), exactMinimumGapM=proof['exactMinimumFiniteColumnGapM']))
                        if len(proofs) % 100 == 0:
                            assert reservations.heartbeat(lease)['ok']
                save(doc / (uid.split('/')[1] + '-' + mode + '-exact.json.gz'), dict(excludedGroundFaceIds=list(map(int, excluded)), proofs=proofs))
                results.append(dict(uid=uid, mode=mode, completeSourceFaces=len(triangles), completeGroundFaces=len(ground), excludedGroundFaces=len(excluded), exactInclusivePairs=len(proofs), rawAdditionalClearanceFailures=negatives, additionalFacesNeedingReview=sorted({x['sourceFace'] for x in negatives} - ({11390} if uid == 'landsd/268867:0' else set()))))
                if uid == 'landsd/268867:0':
                    grade = take(GRADE, base / GRADE / (mode + '.json.gz'))
                    assert grade['sourceWorldSHA256'] == digest(triangles.tobytes())
                    assert grade['groundSHA256'] == digest(ground.tobytes())
                    assert grade['allChosenCapsOrdinaryClear'] and grade['positiveUpperGradeInterface']
                    wall = triangles[11390]
                    separated = []
                    for native in inventory['rows']:
                        bounds = np.asarray(native['completeFourWorldBounds'][modeindex])
                        assert np.any(bounds[0] > wall.max(0)) or np.any(bounds[1] < wall.min(0)), native['uid']
                        separated.append(dict(uid=native['uid'], sourceSHA256=native['sourceSHA256'], completeWorldBounds=bounds.tolist()))
                    projection = Polygon(wall[:, [0, 2]])
                    basicseparation = []
                    for form in forms:
                        if form['uid'] in {r['uid'] for r in inventory['rows']} or form['uid'] == uid:
                            continue
                        polygon = Polygon(form['rings'][0], form['rings'][1:])
                        assert polygon.is_valid and polygon.disjoint(projection), form['uid']
                        basicseparation.append(dict(uid=form['uid'], exactCurrentRings=form['rings'], floatingProjectionDistanceM=polygon.distance(projection)))
                    x0, z0, x1, z1 = region['regionalParentExtent']
                    assert np.all(wall[:, 0] > x0) and np.all(wall[:, 0] < x1) and np.all(wall[:, 2] > z0) and np.all(wall[:, 2] < z1)
                    save(doc / (mode + '-wall-foreign-scope.json.gz'), dict(currentManifestSHA256=selection['manifestSHA256'], nativeSeparations=separated, basicFootprintSeparations=basicseparation, completeCurrentNativeCount=len(separated), currentRegionalFormCount=len(forms), originalWall=wall.tolist(), currentFormTileHashes=inventory['currentFormTileHashes'], nativeCatalogueHashes=catalogues))
                    wallrows.append(dict(mode=mode, completeNativeBoundsSeparated=len(separated), basicFootprintsSeparated=len(basicseparation), entireWallStrictlyWithinCompleteRegionalScope=True, originalWallSHA256=digest(wall.tobytes()), rawClearanceFailurePreserved=True, sourceRoleAccepted=False))
                assert reservations.heartbeat(lease)['ok']
                print(results[-1], flush=True)
        assert digest(manifestpath.read_bytes()) == selection['manifestSHA256']
        summary = dict(uids=sorted(geometry), rows=results, wallForeignScope=wallrows,
                       currentManifestSHA256=selection['manifestSHA256'], additionalUnclassifiedFaces=sorted({(r['uid'], i) for r in results for i in r['additionalFacesNeedingReview']}),
                       sourceRoleAccepted=False, physicalAccepted=False, installationApproved=False,
                       qualification='Exact all-source checks against every terrain facet omitted by the positive-XZ context filter; all91Nam/10FuYunvertical/collapsed facets retained. Every installed native is strictly separated from wall11390 using complete corresponding four-world bounds. Every remaining regional basic footprint is disjoint and the whole wall is inside the complete scanned region. This does not approve exterior provenance, basic overhang extent, source role, root, support, other source contacts or publication. Existing finite cap/upper-grade evidence is rebound to matching full current arrays.')
        save(doc / 'summary.json', summary)
        refs.extend([HERE / 'exact_original_triangle_pair_column_gap_20261010.py', HERE / 'exact_packed_world_geometry_20261009.py'])
        module('nam_complete_vertical_ground_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-current-excluded-ground-and-four-world-wall-foreign-evidence', refs, summary)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
