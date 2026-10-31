"""Capture a rejected private candidate and measure its complete projected overlaps.

No live writes or acceptance: neighbours, original support and runtime remain separate.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--terrain-check', required=True)
    parser.add_argument('--capture', required=True)
    parser.add_argument('--core-halo', type=float, default=1.0)
    args = parser.parse_args()
    assert 0 <= args.core_halo <= 10
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs, pins = [Path(__file__)], {}
    for name in [args.terrain_check, args.capture]:
        folder = base / name
        _, bound = authenticate(folder)
        refs.append(folder / 'result.json')
        for key, value in bound.items():
            assert key not in pins or pins[key] == value
            pins[key] = value

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    checked = take(base / args.terrain_check / 'summary.json')['rows']
    assert checked and all(r['status'] == 'original-terrain-checked' for r in checked)
    wanted = {r['uid']: r['sourceSHA256'] for r in checked}
    rows = [r for r in take(base / args.capture / 'selection.json.gz')['rows'] if r['uid'] in wanted]
    assert len(rows) == len(wanted)
    for row in rows:
        assert row['sourceSHA256'] == wanted[row['uid']]
    second = module('selected_patch_geometry', HERE / 'xl-second-pass.py')
    parentpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(parentpath)
    refs.append(parentpath)
    rects = [second.resolution.rectangle_for(r['native']['model']['worldBounds'], parent) for r in rows]
    cells = [min(r[0] for r in rects), min(r[1] for r in rects), max(r[2] for r in rects), max(r[3] for r in rects)]
    bounds = second.resolution.extent(cells, parent)
    lows = np.min([r['native']['model']['worldBounds'][0] for r in rows], axis=0)
    highs = np.max([r['native']['model']['worldBounds'][1] for r in rows], axis=0)
    core = [float(lows[0]-args.core_halo), float(lows[2]-args.core_halo), float(highs[0]+args.core_halo), float(highs[2]+args.core_halo)]
    sources, parts = [], []
    for name in sorted({p for r in checked for p in r['sourceTerrainPaths']}):
        path = ROOT / name
        gltf = take(path)
        for buffer in gltf.get('buffers', []):
            member = path.parent / buffer['uri']
            assert digest(member.read_bytes()) == pins[str(member.relative_to(ROOT))]
            refs.append(member)
        sources.append(dict(path=name, sha256=pins[name]))
        parts.append(second.terrain_triangles(path))
    terrain = np.concatenate(parts)
    terrain = terrain[(terrain[:, :, 0].max(1) >= bounds[0]) & (terrain[:, :, 0].min(1) <= bounds[2]) & (terrain[:, :, 2].max(1) >= bounds[1]) & (terrain[:, :, 2].min(1) <= bounds[3])]
    builder = module('selected_patch_builder', HERE / 'resolve-pass-indexed-parent-clipping.py')
    save(doc / 'scope.json', dict(uids=sorted(wanted), cells=cells, bounds=bounds, sourceTerrainFaces=len(terrain), nativeCore=core, coreHalo=args.core_halo, installationApproved=False))
    result = dict(uids=sorted(wanted), installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0)
    captured = []
    validator = builder.validate_patch
    def capture_then_validate(patch, parent):
        captured.append(patch)
        return validator(patch, parent)
    builder.validate_patch = capture_then_validate
    try:
        patch = builder.make_patch(dict(cells=cells, uids=sorted(wanted)), parent, terrain, sources, native_core=core, parent_sha256=digest(parentpath.read_bytes()))
    except AssertionError as error:
        assert str(error) == 'Native terrain contains overlapping height surfaces'
        assert len(captured) == 1
        patch = captured[0]
        candidate = local / 'unvalidated-terrain.json.gz'
        save(candidate, patch)
        refs.append(candidate)
        import shapely
        from shapely.geometry import Polygon
        mesh = patch['nativeMesh']
        tri = np.asarray(mesh['position'], dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
        polygons = shapely.polygons(tri[:,:,[0,2]])
        valid = np.flatnonzero(shapely.area(polygons) > 1e-10)
        poly = polygons[valid]
        union = shapely.union_all(poly)
        excess = float(shapely.area(poly).sum() - union.area)
        tree = shapely.STRtree(poly)
        pairs = tree.query(poly, predicate='intersects')
        pairs = pairs[:,pairs[0] < pairs[1]]
        overlaps = shapely.intersection(poly[pairs[0]], poly[pairs[1]])
        areas = shapely.area(overlaps)
        keep = np.flatnonzero(areas > 1e-10)
        records = []
        for k in keep:
            ia, ib = int(valid[pairs[0,k]]), int(valid[pairs[1,k]])
            points = shapely.get_coordinates(overlaps[k])
            assert len(points)
            def heights(face):
                t = tri[face]
                normal = np.cross(t[1]-t[0], t[2]-t[0])
                assert normal[1] != 0
                return t[0,1] - ((points[:,0]-t[0,0])*normal[0] + (points[:,1]-t[0,2])*normal[2])/normal[1]
            delta = heights(ia)-heights(ib)
            j = int(np.argmax(np.abs(delta)))
            records.append(dict(faceA=ia, faceB=ib, projectedAreaM2=float(areas[k]), maximumAbsoluteHeightDifferenceM=float(abs(delta[j])), heightDifferenceRangeM=[float(delta.min()),float(delta.max())], witnessXZ=points[j].tolist()))
        save(doc / 'positive-area-overlaps.json.gz', dict(rows=records, completeCandidateFaces=len(tri), arithmetic='Float64 plane evaluation of exact float32 runtime vertices; diagnostic measurements, not rational clearance or approval'))
        refs.append(doc / 'positive-area-overlaps.json.gz')
        result.update(status='unapproved-terrain-overlap-diagnosed', reason=str(error), permanentRejection=False, candidate=dict(path=str(candidate.relative_to(ROOT)), sha256=digest(candidate.read_bytes())), candidateFaces=len(tri), completePositiveAreaPairs=len(records), projectedExcessM2=excess, maximumMeasuredHeightDifferenceM=max((r['maximumAbsoluteHeightDifferenceM'] for r in records), default=0), pairsOverOneCentimetre=sum(r['maximumAbsoluteHeightDifferenceM'] > .01 for r in records), worstPairs=sorted(records,key=lambda r:r['maximumAbsoluteHeightDifferenceM'],reverse=True)[:10], numericalMeasurementsOnly=True, terrainValidationPassed=False)
    else:
        path = local / 'candidate-terrain.json'
        save(path, patch)
        refs.append(path)
        result.update(status='private-terrain-validator-passed', terrainTriangles=len(patch['nativeMesh']['index']) // 3, candidate=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    save(doc / 'summary.json', result)
    refs.extend([HERE / 'xl-second-pass.py', HERE / 'resolve-pass-indexed-parent-clipping.py', HERE.parent / 'island-detail-integration/native_terrain_validation.py'])
    module('selected_patch_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-private-original-terrain-candidate', list(dict.fromkeys(refs)), result)
    print({k: v for k, v in result.items() if k != 'candidate'}, flush=True)


if __name__ == '__main__':
    main()
