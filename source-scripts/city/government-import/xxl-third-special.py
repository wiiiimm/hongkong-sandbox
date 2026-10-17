"""Measure XXL terrain seam/overlap blockers without changing source data."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('xxl_second', Path(__file__).with_name('xxl-second-pass.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT, DOC, LOCAL = s.ROOT, s.DOC, s.LOCAL
OUT = DOC / 'third-pass/special-terrain-context.json'


def all_native():
    sources = s.read(DOC / 'recovery.json')['sheets'] + s.read(DOC / 'adjacent-terrain-results.json')['sources']
    triangles = []
    for source in sources:
        triangles.extend(s.context.triangles(ROOT / path) for path in source['terrainPaths'])
    return np.concatenate(triangles), sources


def near(triangles, bounds, margin=0):
    return triangles[(triangles[:, :, 0].max(axis=1) >= bounds[0] - margin) & (triangles[:, :, 0].min(axis=1) <= bounds[2] + margin) & (triangles[:, :, 2].max(axis=1) >= bounds[1] - margin) & (triangles[:, :, 2].min(axis=1) <= bounds[3] + margin)]


def telford(triangles):
    row = next(r for r in s.read(DOC / 'selection.json.gz')['rows'] if r['modelId'] == 'B399652048902063C0')
    model = s.glb_triangles(row)
    lo, hi = model.min(axis=(0, 1)), model.max(axis=(0, 1))
    terrain = near(triangles, [lo[0], lo[2], hi[0], hi[2]], 1)
    polygons = shapely.polygons(terrain[:, :, [0, 2]])
    valid = shapely.area(polygons) > 1e-10
    terrain, polygons = terrain[valid], polygons[valid]
    points, bottom = s.resolution.sample_points({'position': model.reshape(-1).tolist(), 'index': list(range(len(model) * 3))})
    heights = s.context.shared.samples(points[:, [0, 2]], terrain, shapely.STRtree(polygons))
    missing = points[~np.isfinite(heights)]
    union = shapely.union_all(polygons)
    distances = shapely.distance(shapely.points(missing[:, [0, 2]]), union)
    return {'uid': 'landsd/226033:0', 'checks': len(points), 'uncoveredSamples': len(missing), 'uncoveredBounds': [missing[:, 0].min().item(), missing[:, 2].min().item(), missing[:, 0].max().item(), missing[:, 2].max().item()], 'distanceToRecoveredTerrainRangeM': [distances.min().item(), distances.max().item()], 'within1mm': int((distances <= .001).sum()), 'within1cm': int((distances <= .01).sum()), 'within10cm': int((distances <= .1).sum()), 'samplePoints': missing[:, [0, 1, 2]].tolist(), 'aiCalls': 0}


def patch_context(uid, triangles, sources, plan_path, row_path):
    plan = s.read(plan_path)
    row = next(r for r in s.read(row_path)['rows'] if r['uid'] == uid)
    parent = s.read(ROOT / '3d-viewer/city/data/terrain.json')
    bounds = plan['bounds']
    fragments, used = [], []
    for source in sources:
        pieces = []
        for path in source['terrainPaths']:
            hit = near(s.context.triangles(ROOT / path), bounds)
            if len(hit): pieces.append(hit)
        if pieces:
            fragments.extend(pieces)
            used.append({'sheet': source['sheet'], 'revision': source['source']['revisionDate'], 'sourceETag': source['source']['sourceETag'], 'directorySHA256': source['source']['directorySHA256'], 'sourceFiles': []})
    lo, hi = row['candidate']['entry']['worldBounds']
    original_validator = s.resolution.validate_patch
    s.resolution.validate_patch = lambda patch, parent: None
    try:
        patch = s.resolution.make_patch({'uids': [uid], 'cells': plan['cells']}, parent, np.concatenate(fragments), used, native_core=[lo[0] - 1, lo[2] - 1, hi[0] + 1, hi[2] + 1])
    finally:
        s.resolution.validate_patch = original_validator
    position = np.asarray(patch['nativeMesh']['position']).reshape(-1, 3)
    faces = position[np.asarray(patch['nativeMesh']['index']).reshape(-1, 3)]
    polygons = shapely.polygons(faces[:, :, [0, 2]])
    valid = shapely.area(polygons) > 1e-10
    polygons = polygons[valid]
    extent = box(*bounds)
    union = shapely.union_all(polygons)
    area_sum = float(shapely.area(polygons).sum())
    union_area = float(union.area)
    return {'uid': uid, 'sourceSheets': sorted({u['sheet'] for u in used}), 'patchTriangles': len(faces), 'verticalTriangles': int((~valid).sum()), 'extentAreaM2': float(extent.area), 'unionAreaM2': union_area, 'missingProjectedAreaM2': float(extent.difference(union).area), 'excessProjectedAreaM2': area_sum - union_area, 'symmetricDifferenceAreaM2': float(extent.symmetric_difference(union).area), 'aiCalls': 0, 'publication': False}


def main():
    triangles, sources = all_native()
    report = {
        'batch': 'government-xxl-third-20260912',
        'telford': telford(triangles),
        'terrainPatches': [
            patch_context('landsd/109467:0', triangles, sources, DOC / 'terrain/patch-plan.json', DOC / 'terrain/selection.json.gz'),
            patch_context('landsd/136832:0', triangles, sources, DOC / 'third-pass/landsd-136832/patch-plan.json', DOC / 'third-pass/landsd-136832/selection.json.gz'),
        ],
        'aiCalls': 0,
        'geometryChanges': 0,
        'publication': False,
        'qualification': 'Read-only measurement of exact recovered source TIN coverage and projected overlap. No interpolation, deduplication, geometry changes or acceptance decisions.',
    }
    s.save(OUT, report)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
