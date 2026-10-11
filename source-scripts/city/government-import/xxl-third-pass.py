"""Classify remaining XXL source holds with exact geometry and native TINs; never AI."""
from collections import defaultdict
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('xxl_second', Path(__file__).with_name('xxl-second-pass.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT, DOC, LOCAL = s.ROOT, s.DOC, s.LOCAL
OUT = DOC / 'third-pass'


def surface_context(triangles, native):
    polygons = shapely.polygons(native[:, :, [0, 2]])
    valid = shapely.area(polygons) > 1e-10
    terrain = native[valid]
    tree = shapely.STRtree(polygons[valid])
    area = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]), axis=1) / 2
    normal_y = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])[:, 1]
    points = np.concatenate([triangles, triangles.mean(axis=1)[:, None, :]], axis=1)
    heights = s.context.shared.samples(points[:, :, [0, 2]].reshape(-1, 2), terrain, tree).reshape(-1, 4)
    gaps = points[:, :, 1] - heights
    complete = np.isfinite(heights).all(axis=1)
    fully_buried = complete & (gaps < -.5).all(axis=1)
    partly_buried = complete & (gaps < -.5).any(axis=1)
    upward = normal_y > .25 * np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]), axis=1)
    total = float(area.sum())
    buried = float(area[fully_buried].sum())
    upward_buried = fully_buried & upward
    return {
        'triangles': len(triangles),
        'completeTerrainTriangles': int(complete.sum()),
        'fullyBuriedTriangles': int(fully_buried.sum()),
        'partlyBuriedTriangles': int(partly_buried.sum()),
        'fullyBuriedUpwardTriangles': int(upward_buried.sum()),
        'surfaceAreaM2': total,
        'fullyBuriedAreaM2': buried,
        'fullyBuriedAreaRatio': buried / total if total else None,
        'fullyBuriedUpwardAreaM2': float(area[upward_buried].sum()),
        'minimumCompleteGapM': float(gaps[complete].min()) if complete.any() else None,
    }


def route(row, context):
    candidates = row['projectionCandidates']
    identity = len(candidates) == 1 and candidates[0]['metrics']['overlapOfSmaller'] >= .98 and candidates[0]['metrics']['footprintCovered'] >= .98 and candidates[0]['metrics']['projectionInsideFootprint'] >= .98 and candidates[0]['metrics']['centroidDistance'] <= 1
    foundation = context['completeTerrainTriangles'] == context['triangles'] and context['fullyBuriedUpwardTriangles'] == 0 and context['fullyBuriedAreaRatio'] <= .001
    reasons = []
    if not identity:
        reasons.append('source-component-identity-outside-conservative-script-contract')
    if not foundation:
        reasons.append('below-grade-surfaces-outside-conservative-foundation-contract')
    return {
        'identityScriptAccepted': identity,
        'foundationScriptAccepted': foundation,
        'actionableState': 'scripted-acceptance-candidate' if not reasons else 'held-unknown',
        'reasons': reasons,
    }


def main():
    diagnostics = s.read(DOC / 'diagnostics.json')
    final = s.read(DOC / 'final-results.json.gz')
    held = {r['modelId'] for r in final['rows'] if r['humanStatus'] == 'held-unknown'}
    rows = [r for r in diagnostics['rows'] if r['modelId'] in held and 'native-source-below-grade' in r['native'].get('reasons', [])]
    assert len(rows) == 13
    sources = s.read(DOC / 'recovery.json')['sheets'] + s.read(DOC / 'adjacent-terrain-results.json')['sources']
    by_sheet = defaultdict(list)
    for source in sources:
        for path in source['terrainPaths']:
            by_sheet[source['sheet']].append(s.context.triangles(ROOT / path))
    all_native = np.concatenate([part for pieces in by_sheet.values() for part in pieces])
    results = []
    for row in rows:
        tri = s.glb_triangles(next(r for r in s.read(DOC / 'selection.json.gz')['rows'] if r['modelId'] == row['modelId']))
        lo, hi = tri.min(axis=(0, 1)), tri.max(axis=(0, 1))
        native = all_native[(all_native[:, :, 0].max(axis=1) >= lo[0] - 1) & (all_native[:, :, 0].min(axis=1) <= hi[0] + 1) & (all_native[:, :, 2].max(axis=1) >= lo[2] - 1) & (all_native[:, :, 2].min(axis=1) <= hi[2] + 1)]
        context = surface_context(tri, native)
        decision = route(row, context)
        results.append({k: row.get(k) for k in ('modelId', 'uid', 'name', 'sourceSheet')} | {'sourceSHA256': row['sha256'], 'surfaceContext': context, **decision, 'aiCalls': 0, 'geometryChanges': 0, 'publication': False})
        print(json.dumps({'modelId': row['modelId'], 'uid': row['uid'], **context, **decision}), flush=True)
    report = {'batch': 'government-xxl-third-20260912', 'stage': 'below-grade-source-context-v1', 'models': len(results), 'rows': results, 'aiCalls': 0, 'geometryChanges': 0, 'publication': False, 'qualification': 'Exact original source triangles against recovered original government terrain. The conservative scripted foundation route requires complete triangle coverage, no fully buried upward face, and at most 0.1% fully buried source area. It does not modify or remodel geometry.'}
    s.save(OUT / 'source-surface-context.json', report)


if __name__ == '__main__':
    main()
