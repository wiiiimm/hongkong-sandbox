"""Partition faces by identical transformed vertices, without snapping geometry."""
import numpy as np


def face_components(triangles):
    triangles = np.asarray(triangles)
    if triangles.shape != (len(triangles), 3, 3) or not np.isfinite(triangles).all():
        raise ValueError('Finite N×3×3 world triangles required')
    parent = list(range(len(triangles)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    seen = {}
    for i, face in enumerate(triangles):
        for vertex in face:
            key = tuple(vertex)
            old = seen.setdefault(key, i)
            a, b = root(i), root(old)
            if a != b:
                parent[a] = b
    groups = {}
    for i in range(len(triangles)):
        groups.setdefault(root(i), []).append(i)
    return [np.asarray(ids, dtype=np.int64) for ids in
            sorted(groups.values(), key=lambda ids: (-len(ids), ids[0]))]
