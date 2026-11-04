"""Read-only exact source-domain/retained-actor preflight for a private inset.

No terrain candidate, publication or acceptance is produced. Root-native coverage
is closed over complete existing coarse extents before reserving later processing.
"""
import math
from pathlib import Path
import uuid
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint

BATCH = 'government-xl-elegant-garden-inset-scope-v1-20261027'
CAPTURE = 'government-xl-elegant-garden-existing-ground-runtime-v2-20261027'
INVENTORY = 'government-xl-after-ocean-four-current-inventory-v1-20261027'
UIDS = ['landsd/173532:0', 'landsd/173768:0', 'landsd/236170:0']


def main():
    base = ROOT / 'docs/astra-city/government-import'
    out = base / BATCH
    assert not out.exists()
    claimed = reservations.claim('elegant-inset-preflight-' + str(uuid.uuid4()),
                                 ['building:' + u for u in UIDS], batch=BATCH, ttl=1800)
    assert claimed['ok']
    lease = claimed['reservation']
    try:
        refs, pins = [Path(__file__)], {}

        def take(batch, path):
            if batch not in pins:
                _, pins[batch] = authenticate(base / batch)
                refs.append(base / batch / 'result.json')
            assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
            refs.append(path)
            return read(path)

        selection = take(CAPTURE, base / CAPTURE / 'selection.json.gz')
        geometries = take(CAPTURE, HERE / 'local' / CAPTURE / 'runtime-geometry.json.gz')
        inventory = take(INVENTORY, base / INVENTORY / 'complete-bounds.json.gz')
        manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
        manifest = take(INVENTORY, manifest_path)
        assert digest(manifest_path.read_bytes()) == selection['manifestSHA256']
        assert sorted(r['uid'] for r in selection['rows']) == UIDS
        triangles = []
        for row in selection['rows']:
            geometry = next(g for g in geometries['rows'] if g['uid'] == row['uid'])
            asset = ROOT / row['candidate']['path']
            assert digest(asset.read_bytes()) == geometry['sourceSHA256'] == row['sourceSHA256']
            refs.append(asset)
            tri = np.asarray(geometry['position']).reshape(-1, 3)[np.asarray(geometry['index']).reshape(-1, 3)]
            assert len(tri) == row['triangles']
            triangles.append(tri)
        projection = shapely.union_all([shapely.MultiPoint(f[:, [0, 2]]).convex_hull
                                       for f in np.concatenate(triangles)])
        core = projection.buffer(1, join_style='mitre')
        outer = core.buffer(3, join_style='mitre')
        root_path = ROOT / '3d-viewer/city/data/terrain.json'
        # The bounds inventory authenticates models/forms. Actual terrain bytes
        # are authenticated by the completed current drawn-ground capture.
        root = take(CAPTURE, root_path)
        g, size = root['meta']['georef'], root['cell']
        a, b, c, d = outer.bounds
        cells = [math.floor((a-.001+834500-g['bE'])/size), math.floor((b-.001-816500+g['bN'])/size),
                 math.ceil((c+.001+834500-g['bE'])/size), math.ceil((d+.001-816500+g['bN'])/size)]
        initial = cells.copy()
        natives = {}
        for entry in manifest['terrainPatches']:
            url = entry['url']
            path = ROOT / '3d-viewer' / url
            node = take(CAPTURE, path)
            if node.get('nativeMesh') and node['meta'].get('parentTerrain') == 'city/data/terrain.json':
                assert node['meta']['parentSha256'] == digest(root_path.read_bytes())
                natives[url] = node
        covered = set()
        while True:
            found = {url for url, node in natives.items()
                     if min(cells[2], node['coarseCells'][2]) > max(cells[0], node['coarseCells'][0])
                     and min(cells[3], node['coarseCells'][3]) > max(cells[1], node['coarseCells'][1])}
            if found <= covered:
                break
            covered |= found
            for url in sorted(found):
                old = natives[url]['coarseCells']
                cells = [min(cells[0], old[0]), min(cells[1], old[1]), max(cells[2], old[2]), max(cells[3], old[3])]
        builder = module('elegant_inset_extent', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
        bounds = builder.extent(cells, root)
        assert shapely.box(*bounds).covers(outer)
        touching = [r['uid'] for r in inventory['rows'] if not closed_disjoint(r['completeFourWorldBounds'], bounds)]
        retained_targets = {u for url in covered for u in natives[url]['meta']['targetUids']}
        coordinated = sorted(url for url in covered if natives[url]['nativeMesh'].get('source', {}).get('coordinatedBoundary'))
        resources = sorted({'terrain:city/data/terrain.json', *['terrain:' + url for url in covered],
                            *['building:' + u for u in set(UIDS) | set(touching) | retained_targets]})
        assert reservations.owns(lease)
        assert digest(manifest_path.read_bytes()) == selection['manifestSHA256']
        result = dict(uids=UIDS, initialCells=initial, cells=cells, bounds=bounds,
                      coreBounds=list(core.bounds), outerBounds=list(outer.bounds),
                      currentManifestSHA256=selection['manifestSHA256'], currentNativeActors=len(inventory['rows']),
                      touchingNativeUids=sorted(touching), coverNative=sorted(covered),
                      retainedTargets=sorted(retained_targets), coordinatedMembers=coordinated, resources=resources,
                      standaloneInsetEligible=not coordinated, sourceGeometryChanges=0, terrainGeometryChanges=0,
                      installationApproved=False, physicalAcceptance=False, publication=False,
                      qualification='Same represented source projection and buffers as existing insetV9. '
                      'Closed four-world original bounds nominate retained actors, not physical contact. '
                      'Every intersected root-native coarse domain is included whole, recursively. '
                      'A coordinated member requires its own complete-mate proof; no standalone waiver. '
                      'Nested/non-native current surfaces still require parent capture and later full scope checks.')
        save(out / 'summary.json', result)
        refs.extend([HERE / 'selected_original_local_inset_v9_20261024.py',
                     HERE / 'heritage_saved_native_bounds_binding_v1_20261014.py'])
        module('elegant_inset_scope_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'read-only-original-inset-domain-and-retained-actor-reservation-preflight', refs, result)
        print(dict(cells=cells, retainedActors=len(touching), coverNative=sorted(covered),
                   coordinatedMembers=coordinated, resources=len(resources)), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
