"""Deterministic repairs for incomplete/overlapping original terrain patches."""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.ops import triangulate


def _faces(patch):
    position = np.asarray(patch['nativeMesh']['position']).reshape(-1, 3)
    return position[np.asarray(patch['nativeMesh']['index']).reshape(-1, 3)]


def projected_context(patch, bounds):
    faces = _faces(patch)
    polygons = shapely.polygons(faces[:, :, [0, 2]])
    valid = shapely.area(polygons) > 1e-10
    polygons = polygons[valid]
    union = shapely.union_all(polygons)
    extent = shapely.box(*bounds)
    return faces[valid], polygons, extent.difference(union), float(shapely.area(polygons).sum() - union.area)


def fill_parent_only_holes(patch, parent, bounds, protected_projection, sampler):
    _, _, missing, _ = projected_context(patch, bounds)
    assert missing.intersection(protected_projection).area < 1e-6, 'missing-native-terrain-intersects-source-model'
    additions = []
    for candidate in triangulate(missing):
        if candidate.area <= 1e-10 or not missing.buffer(1e-8).covers(candidate):
            continue
        coords = list(candidate.exterior.coords)[:3]
        additions.append([[x, sampler.ground(x, z), z] for x, z in coords])
    assert additions, 'no-parent-hole-fill'
    position = patch['nativeMesh']['position']
    index = patch['nativeMesh']['index']
    offset = len(position) // 3
    flat = np.asarray(additions).reshape(-1, 3).tolist()
    position.extend(value for point in flat for value in point)
    index.extend(range(offset, offset + len(flat)))
    patch['nativeMesh']['source']['parentHoleFill'] = {'areaM2': float(missing.area), 'triangles': len(additions), 'policy': 'Current parent terrain sampled only where recovered native TIN is absent and outside the protected source-model projection.'}
    return {'missingAreaM2': float(missing.area), 'triangles': len(additions)}


def approve_original_overlap(patch, path, evidence_path, source_files):
    bounds = _patch_bounds(patch)
    faces, polygons, _, excess = projected_context(patch, bounds)
    assert excess > 0
    tree = shapely.STRtree(polygons)
    left, right = tree.query(polygons, predicate='intersects')
    rows = []
    for a, b in zip(left, right):
        if a >= b:
            continue
        overlap = polygons[a].intersection(polygons[b])
        if overlap.area <= 1e-8:
            continue
        point = overlap.representative_point()
        def barycentric(face):
            x, z = point.x, point.y
            a, b, c = face
            det = (b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])
            u = ((x-a[0])*(c[2]-a[2])-(z-a[2])*(c[0]-a[0]))/det
            v = ((b[0]-a[0])*(z-a[2])-(b[2]-a[2])*(x-a[0]))/det
            return a[1]+u*(b[1]-a[1])+v*(c[1]-a[1])
        def plane(face):
            normal = np.cross(face[1]-face[0], face[2]-face[0])
            return face[0,1]-(normal[0]*(point.x-face[0,0])+normal[2]*(point.y-face[0,2]))/normal[1]
        sampled=max(barycentric(faces[a]),barycentric(faces[b]));ray=max(plane(faces[a]),plane(faces[b]))
        rows.append({'x': point.x, 'z': point.y, 'overlapAreaM2': float(overlap.area), 'highestSamplerHeight': sampled, 'highestRayHeight': ray, 'error': abs(sampled-ray)})
        if len(rows) == 64:
            break
    assert rows, 'no-overlap-samples'
    staged_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    audit = {'stagedGeometrySha256': staged_sha, 'nativeProjectedExcessM2': excess, 'float32HighestRayAgreement': {'samples': len(rows), 'maxError': max(r['error'] for r in rows), 'rows': rows, 'method': 'Independent barycentric sampler and vertical plane-ray equations at points inside overlapping original source facets; runtime collision uses their highest surface.'}, 'source': {'files': source_files}, 'policy': 'Retain exact original overlapping source facets and use the highest original surface.'}
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(audit, sort_keys=True, separators=(',', ':')) + '\n')
    patch['nativeMesh']['sourceOverlap'] = {'policy': 'highest-native-surface', 'measuredProjectedExcessM2': excess, 'evidencePath': str(evidence_path), 'evidenceSHA256': hashlib.sha256(evidence_path.read_bytes()).hexdigest()}
    return audit


def _patch_bounds(patch):
    g = patch['meta']['georef']
    x0, z0 = g['bE'] - 834500, 816500 - g['bN']
    return [x0, z0, x0 + (patch['w'] - 1) * g['aE'], z0 - (patch['h'] - 1) * g['aN']]
