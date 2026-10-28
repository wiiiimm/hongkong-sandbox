"""Locate exact per-source projection gaps in authenticated provider terrain.

Diagnostic only: original and actual-renderer projections are reported apart.
No extrapolation, terrain/model edit, tolerance change or acceptance follows.
"""
import argparse
from pathlib import Path
import sys
import uuid
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'terrain-check', 'terrain-uid']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert all(x.startswith('government-xl-') and '/' not in x
               for x in [a.batch, a.capture, a.terrain_check])
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / a.batch, HERE / 'local' / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__), HERE / 'exact_packed_world_geometry_20261009.py'], {}
    for name in [a.capture, a.terrain_check]:
        _, bound = authenticate(base / name)
        refs.append(base / name / 'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(base / a.capture / 'selection.json.gz')['rows']
    uids = sorted(r['uid'] for r in selection)
    assert len(uids) == len(set(uids)) and a.terrain_uid in uids
    leasepath = local / 'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('original-terrain-projection-' + str(uuid.uuid4()),
            ['building:' + u for u in uids], batch=a.batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath,
            [sys.executable, __file__, '--batch', a.batch, '--capture', a.capture,
             '--terrain-check', a.terrain_check, '--terrain-uid', a.terrain_uid, '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease)
    geometries = {r['uid']: r for r in take(HERE / 'local' / a.capture / 'runtime-geometry.json.gz')['rows']}
    context = next(r for r in take(base / a.terrain_check / 'summary.json')['rows']
                   if r['uid'] == a.terrain_uid)
    assert context['sourceSHA256'] == next(r['sourceSHA256'] for r in selection if r['uid'] == a.terrain_uid)
    decoder = module('original_projection_terrain_decoder', HERE / 'xl-second-pass.py')
    refs.append(HERE / 'xl-second-pass.py')
    terrain = []
    for name in context['sourceTerrainPaths']:
        path = ROOT / name
        meta = take(path)
        for buffer in meta.get('buffers', []):
            member = path.parent / buffer['uri']
            assert digest(member.read_bytes()) == pins[str(member.relative_to(ROOT))]
            refs.append(member)
        terrain.append(decoder.terrain_triangles(path))
    ground = np.concatenate(terrain)
    ground_projection = shapely.union_all(shapely.polygons(ground[:, :, [0, 2]]))
    results = []
    for row in selection:
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == geometries[row['uid']]['sourceSHA256']
        refs.append(asset)
        g = geometries[row['uid']]
        modes = dict(original=decode_original_world_triangles(asset.read_bytes()),
            literal=np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)])
        for mode, tri in modes.items():
            assert len(tri) == row['triangles']
            projection = shapely.union_all([shapely.MultiPoint(f[:, [0, 2]]).convex_hull for f in tri])
            missing = projection.difference(ground_projection)
            results.append(dict(uid=row['uid'], mode=mode, completeSourceFaces=len(tri),
                sourceSHA256=row['sourceSHA256'], uncoveredAreaM2=missing.area,
                uncoveredBounds=list(missing.bounds) if not missing.is_empty else [],
                geometry=shapely.to_geojson(missing)))
            print(row['uid'], mode, 'uncoveredAreaM2', missing.area, flush=True)
    result = dict(uids=uids, rows=results, providerTerrainFaces=len(ground),
        installationApproved=False, publication=False, sourceGeometryChanges=0,
        qualification='Per-source complete original versus literal projection coverage only. Empty-area results do not establish foundation, support or acceptance; all line/point gaps retained in GeoJSON.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('original_projection_coverage_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'per-source-exact-provider-projection-gap-diagnostic', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
