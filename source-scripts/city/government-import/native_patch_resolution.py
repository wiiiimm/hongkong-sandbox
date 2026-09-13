"""Deterministic repairs for incomplete/overlapping original terrain patches."""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.ops import nearest_points, triangulate


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


def _height_on_source_edge(point, faces, polygons, tree):
    nearest = tree.nearest(point)
    distance = polygons[nearest].distance(point)
    candidates = tree.query(point, predicate='dwithin', distance=distance + 1e-7)
    heights = []
    for index in candidates:
        sample = nearest_points(point, polygons[index])[1]
        face = faces[index]
        a, b, c = face
        normal = np.cross(b - a, c - a)
        assert abs(normal[1]) > 1e-10, 'vertical-source-terrain-face'
        height = a[1] - (normal[0] * (sample.x - a[0]) + normal[2] * (sample.y - a[2])) / normal[1]
        heights.append(float(height))
    assert heights, 'source-edge-height-unavailable'
    return max(heights)


def fill_narrow_source_seam(patch, bounds, protected_projection, sampler, tolerance=0.02):
    """Bridge a narrow source-sheet export seam without changing a model.

    Inside the protected model projection, every added point must be within the
    stated tolerance of a recovered source facet and receives the nearest source
    edge height. Other holes retain the established parent-only fill policy.
    """
    faces, polygons, missing, _ = projected_context(patch, bounds)
    source_union = shapely.union_all(polygons)
    seam = missing.intersection(protected_projection)
    assert seam.area > 0, 'no-protected-source-seam'
    outside_tolerance = seam.difference(source_union.buffer(tolerance))
    assert outside_tolerance.area < 1e-8, 'protected-gap-exceeds-source-seam-tolerance'
    tree = shapely.STRtree(polygons)
    additions = []
    counts = {'source-edge': 0, 'parent': 0}
    parts = [(seam, 'source-edge'), (missing.difference(protected_projection), 'parent')]
    for region, policy in parts:
        for candidate in triangulate(region):
            if candidate.area <= 1e-10 or not region.buffer(1e-8).covers(candidate):
                continue
            points = []
            for x, z in list(candidate.exterior.coords)[:3]:
                height = (_height_on_source_edge(shapely.Point(x, z), faces, polygons, tree)
                          if policy == 'source-edge' else sampler.ground(x, z))
                points.append([x, height, z])
            additions.append(points)
            counts[policy] += 1
    assert counts['source-edge'] > 0, 'no-source-seam-fill'
    position = patch['nativeMesh']['position']
    index = patch['nativeMesh']['index']
    offset = len(position) // 3
    flat = np.asarray(additions).reshape(-1, 3).tolist()
    position.extend(value for point in flat for value in point)
    index.extend(range(offset, offset + len(flat)))
    proof = {
        'protectedAreaM2': float(seam.area),
        'totalMissingAreaM2': float(missing.area),
        'toleranceM': tolerance,
        'sourceEdgeTriangles': counts['source-edge'],
        'parentTriangles': counts['parent'],
        'policy': 'Protected source-sheet seam vertices use the nearest recovered government TIN edge height; holes outside the model projection use current parent terrain.',
    }
    patch['nativeMesh']['source']['sourceBoundaryToleranceFill'] = proof
    return proof



def preserve_parent_under_projection(patch, bounds, projection, sampler):
    """Keep current rendered terrain under one unresolved neighbouring form."""
    faces = _faces(patch)
    extent = shapely.box(*bounds)
    protected = projection.intersection(extent)
    assert protected.area > 0, 'protected-parent-projection-empty'
    output = []
    removed = 0.0
    for face in faces:
        polygon = shapely.Polygon(face[:, [0, 2]])
        overlap = polygon.intersection(protected)
        if overlap.area <= 1e-10:
            output.append(face.tolist())
            continue
        removed += overlap.area
        remainder = polygon.difference(protected)
        normal = np.cross(face[1] - face[0], face[2] - face[0])
        assert abs(normal[1]) > 1e-10, 'vertical-source-terrain-face'
        parts = [part for part in shapely.get_parts(remainder) if part.geom_type == 'Polygon']
        for part in parts:
            for candidate in triangulate(part):
                if candidate.area <= 1e-10 or not part.buffer(1e-8).covers(candidate):
                    continue
                points = []
                for x, z in list(candidate.exterior.coords)[:3]:
                    y = face[0, 1] - (normal[0] * (x - face[0, 0]) + normal[2] * (z - face[0, 2])) / normal[1]
                    points.append([x, float(y), z])
                output.append(points)
    parent_faces = []
    for candidate in triangulate(protected):
        if candidate.area <= 1e-10 or not protected.buffer(1e-8).covers(candidate):
            continue
        parent_faces.append([[x, sampler.ground(x, z), z] for x, z in list(candidate.exterior.coords)[:3]])
    assert removed > 0 and parent_faces, 'no-protected-parent-preservation'
    output.extend(parent_faces)
    flat = np.asarray(output).reshape(-1, 3)
    patch['nativeMesh']['position'] = flat.reshape(-1).tolist()
    patch['nativeMesh']['index'] = list(range(len(flat)))
    proof = {
        'areaM2': float(protected.area),
        'removedNativeProjectedAreaM2': float(removed),
        'parentTriangles': len(parent_faces),
        'policy': 'Current rendered parent terrain is retained only beneath the unresolved neighbouring source form; no building geometry or elevation changes.',
    }
    patch['nativeMesh']['source']['protectedParentProjection'] = proof
    return proof

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
