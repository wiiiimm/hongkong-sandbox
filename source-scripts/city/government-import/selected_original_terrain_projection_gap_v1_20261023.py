"""Measure and exactly check missing original-TIN projections; discovery only."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projection_coverage_v2_20261010 import exact_coverage


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'terrain-check', 'uid']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, cache = [Path(__file__)], {}
    def take(batch, path):
        if batch not in cache:
            cache[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == cache[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(a.capture, base / a.capture / 'selection.json.gz')
    row = next(r for r in selected['rows'] if r['uid'] == a.uid)
    donor = next(r for r in take(a.terrain_check, base / a.terrain_check / 'summary.json')['rows'] if r['uid'] == a.uid)
    assert donor['sourceSHA256'] == row['sourceSHA256'] and donor['nativeResultSHA256'] == row['native']['resultSha']
    path = ROOT / row['candidate']['path']
    assert digest(path.read_bytes()) == row['sourceSHA256']
    refs.append(path)
    tri = decode_original_world_triangles(path.read_bytes())
    assert len(tri) == row['triangles']
    decoder = module('projection_gap_terrain_decoder', HERE / 'xl-second-pass.py')
    parts = []
    for name in donor['sourceTerrainPaths']:
        path = ROOT / name
        gltf = take(a.terrain_check, path)
        for b in gltf.get('buffers', []):
            buffer = path.parent / b['uri']
            assert digest(buffer.read_bytes()) == cache[a.terrain_check][str(buffer.relative_to(ROOT))]
            refs.append(buffer)
        parts.append(decoder.terrain_triangles(path))
    ground = np.concatenate(parts)
    lo, hi = tri.min((0, 1)), tri.max((0, 1))
    keep = (ground[:, :, 0].max(1) >= lo[0]-1) & (ground[:, :, 0].min(1) <= hi[0]+1) & (ground[:, :, 2].max(1) >= lo[2]-1) & (ground[:, :, 2].min(1) <= hi[2]+1)
    ground = ground[keep]
    sourcepolys = shapely.polygons(tri[:, :, [0, 2]])
    terrainpolys = shapely.polygons(ground[:, :, [0, 2]])
    sourceunion = shapely.union_all(sourcepolys)
    terrainunion = shapely.union_all(terrainpolys)
    missing = sourceunion.difference(terrainunion)
    # GEOS nominates every positive missing-area face; exact arithmetic below
    # distinguishes real gaps from floating overlay residues. No gap is filled.
    indices = [i for i, poly in enumerate(sourcepolys) if poly.difference(terrainunion).area > 0]
    proofs = []
    for i in indices:
        proof = exact_coverage(tri[i], ground)
        proofs.append(dict(sourceFace=i, **proof))
    result = dict(uids=[a.uid], sourceSHA256=row['sourceSHA256'], sourceWorldSHA256=digest(tri.astype('<f8').tobytes()), completeSourceFaces=len(tri), sourceTerrainPaths=donor['sourceTerrainPaths'], terrainFaces=len(ground), missingProjectionAreaM2=missing.area, missingProjectionWKT=missing.wkt, sourceProjectionAreaM2=sourceunion.area, geosNominatedSourceFaces=indices, exactTestedFaces=len(proofs), exactStillUncoveredFaces=[p['sourceFace'] for p in proofs if not p['exactProjectionCovered']], zeroXZSourceFaces=int((shapely.area(sourcepolys) == 0).sum()), zeroXZTerrainFaces=int((shapely.area(terrainpolys) == 0).sum()), status='original-terrain-projection-gap-discovery', installationApproved=False, sourceGeometryChanges=0, qualification='Original source and original TIN bytes only. All GEOS positive-area missing-face nominations checked with exact arithmetic. Zero-XZ faces are counted, not granted clearance or ignored in future whole-source checks. No current-scene, support, clearance, terrain construction, geometry edits or admission approval.')
    save(out / 'exact-face-proofs.json.gz', proofs)
    save(out / 'summary.json', result)
    refs.extend(HERE / name for name in ['xl-second-pass.py', 'exact_packed_world_geometry_20261009.py', 'exact_original_projection_coverage_v2_20261010.py'])
    module('original_terrain_projection_gap_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-original-tin-projection-gap-discovery', refs, result)
    print({k:result[k] for k in ['completeSourceFaces', 'terrainFaces', 'missingProjectionAreaM2', 'exactTestedFaces', 'exactStillUncoveredFaces']}, flush=True)


if __name__ == '__main__':
    main()
