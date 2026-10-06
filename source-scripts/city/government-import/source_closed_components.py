"""Exact original-source topology diagnostics; no support or import approval.

Only bit-identical world vertices are shared. No welding tolerance, snapping,
convex hulls, removed geometry or modified faces. Closed, consistently wound edge
components can be examined with solid-angle winding; self-intersection and filled
architectural volume are not certified by this diagnostic.
"""
import hashlib
from collections import defaultdict

import numpy as np


def components(triangles):
    tri = np.asarray(triangles, dtype=float)
    if tri.ndim != 3 or tri.shape[1:] != (3, 3) or not np.isfinite(tri).all():
        raise ValueError('Finite original N×3×3 triangles required')
    _, inverse = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    parent = list(range(len(faces)))
    def root(i):
        while i != parent[i]:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def join(a, b):
        ra, rb = root(a), root(b)
        if ra != rb: parent[rb] = ra
    edges = defaultdict(list)
    degenerate = set()
    for i, face in enumerate(faces):
        if len(set(face)) != 3 or np.linalg.norm(np.cross(tri[i, 1]-tri[i, 0], tri[i, 2]-tri[i, 0])) == 0:
            degenerate.add(i)
        for a, b in zip(face, np.roll(face, -1)):
            edges[tuple(sorted((int(a), int(b))))].append((i, 1 if a < b else -1))
    for owners in edges.values():
        for i, _ in owners[1:]: join(owners[0][0], i)
    groups = defaultdict(list)
    for i in range(len(faces)): groups[root(i)].append(i)
    issues = defaultdict(lambda: {'boundaryEdges': 0, 'nonManifoldEdges': 0, 'inconsistentWindingEdges': 0})
    for owners in edges.values():
        key = root(owners[0][0])
        if len(owners) == 1: issues[key]['boundaryEdges'] += 1
        elif len(owners) != 2: issues[key]['nonManifoldEdges'] += 1
        elif sum(direction for _, direction in owners) != 0: issues[key]['inconsistentWindingEdges'] += 1
    result = []
    for key, indices in groups.items():
        values = tri[indices]; stats = dict(issues[key])
        stats['degenerateTriangles'] = len(degenerate.intersection(indices))
        shifted = values - values[0, 0]
        volume = float(np.einsum('ij,ij->i', shifted[:, 0], np.cross(shifted[:, 1], shifted[:, 2])).sum() / 6)
        result.append({'faceIndices': indices, 'triangles': len(indices), **stats,
                       'signedVolumeM3': volume,
                       'closedConsistentlyWound': not any(stats.values()) and volume != 0,
                       'selfIntersectionCertified': False})
    assert sum(r['triangles'] for r in result) == len(tri)
    return {'worldTrianglesSHA256': hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest(),
            'triangles': len(tri), 'components': result,
            'originalGeometryChanged': False, 'supportApproved': False,
            'qualification': 'Exact edge topology and signed volume only. Closedness does not prove no self-intersection, source component identity, filled architectural volume or support acceptance.'}


def winding(triangles, points):
    """Original solid-angle winding; boundary-coincident points stay undefined."""
    tri = np.asarray(triangles, dtype=float); result = []
    if not np.isfinite(tri).all(): raise ValueError('Nonfinite triangles')
    for point in np.asarray(points, dtype=float):
        if not np.isfinite(point).all(): raise ValueError('Nonfinite point')
        vectors = tri - point
        lengths = np.linalg.norm(vectors, axis=2)
        numerator = np.einsum('ij,ij->i', vectors[:, 0], np.cross(vectors[:, 1], vectors[:, 2]))
        denominator = np.prod(lengths, axis=1)
        denominator += np.einsum('ij,ij->i', vectors[:, 0], vectors[:, 1]) * lengths[:, 2]
        denominator += np.einsum('ij,ij->i', vectors[:, 1], vectors[:, 2]) * lengths[:, 0]
        denominator += np.einsum('ij,ij->i', vectors[:, 2], vectors[:, 0]) * lengths[:, 1]
        if (lengths == 0).any() or ((numerator == 0) & (denominator <= 0)).any():
            result.append(None)
        else: result.append(float((2*np.arctan2(numerator, denominator)).sum() / (4*np.pi)))
    return result
