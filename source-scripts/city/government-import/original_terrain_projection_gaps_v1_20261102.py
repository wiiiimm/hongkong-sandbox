"""Measure original terrain gaps without filling them or granting approval."""
import argparse
import json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'terrain-check']:
        parser.add_argument('--' + key, required=True)
    a = parser.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n
               for n in [a.batch, a.runtime, a.terrain_check])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs = [Path(__file__)]
    pins = {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(a.runtime, base / a.runtime / 'selection.json.gz')
    terrain = take(a.terrain_check, base / a.terrain_check / 'summary.json')
    assert set(terrain['uids']) == {r['uid'] for r in selection['rows']}
    paths = terrain['rows'][0]['sourceTerrainPaths']
    assert paths and all(r['sourceTerrainPaths'] == paths for r in terrain['rows'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    decoder = module('original_projection_gap_decoder', HERE / 'xl-second-pass.py')
    decoder.LOCAL = HERE / 'local' / a.batch
    pieces = []
    for name in paths:
        path = ROOT / name
        meta = take(a.terrain_check, path)
        for buffer in meta.get('buffers', []):
            member = path.parent / buffer['uri']
            assert digest(member.read_bytes()) == pins[a.terrain_check][str(member.relative_to(ROOT))]
            refs.append(member)
        pieces.append(decoder.terrain_triangles(path))
    ground = np.concatenate(pieces)
    source = {}
    terrain_rows = {r['uid']: r for r in terrain['rows']}
    for row in selection['rows']:
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == terrain_rows[row['uid']]['sourceSHA256']
        refs.append(asset)
        source[row['uid']] = decode_original_world_triangles(asset.read_bytes())
    all_source = np.concatenate(list(source.values()))
    lo, hi = all_source.min((0, 1)), all_source.max((0, 1))
    keep = ((ground[:, :, 0].max(1) >= lo[0] - 1) & (ground[:, :, 0].min(1) <= hi[0] + 1)
            & (ground[:, :, 2].max(1) >= lo[2] - 1) & (ground[:, :, 2].min(1) <= hi[2] + 1))
    local_ground = ground[keep]
    polygons = shapely.polygons(local_ground[:, :, [0, 2]])
    union = shapely.union_all(polygons[shapely.area(polygons) > 1e-10])
    projections = {u: shapely.union_all(shapely.polygons(t[:, :, [0, 2]])) for u, t in source.items()}
    projection = shapely.union_all(list(projections.values()))
    missing = projection.difference(union)
    rows = []
    for uid, polygon in projections.items():
        gap = polygon.difference(union)
        rows.append(dict(uid=uid, missingAreaM2=float(gap.area),
                         outsideExistingTwoMillimetreBufferM2=float(gap.difference(union.buffer(.002)).area),
                         missingBounds=list(gap.bounds) if not gap.is_empty else None))
    save(out / 'missing-geometry.json', json.loads(shapely.to_geojson(missing)))
    save(out / 'gap-context.json', dict(rows=rows, completeOriginalTerrainFaces=len(ground),
         localTerrainFaces=len(local_ground), completeOriginalSourceFaces=len(all_source),
         missingAreaM2=float(missing.area), missingBounds=list(missing.bounds) if not missing.is_empty else None,
         outsideExistingTwoMillimetreBufferM2=float(missing.difference(union.buffer(.002)).area)))
    result = dict(uids=sorted(source), sourceSHA256ByUid={r['uid']: r['sourceSHA256'] for r in selection['rows']},
                  rows=rows, missingAreaM2=float(missing.area), sourceGeometryChanges=0,
                  terrainGeometryChanges=0, installationApproved=False, publication=False,
                  qualification='Raw original-terrain projection and per-source missing domains only. Uses the existing builder terrain positive-area filter and 2mm seam buffer unchanged. Does not fill holes, alter surfaces, certify support or declare a source unavailable.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'xl-second-pass.py', HERE / 'exact_packed_world_geometry_20261009.py'])
    module('original_projection_gaps_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-original-terrain-projection-gap-context-no-repair', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
