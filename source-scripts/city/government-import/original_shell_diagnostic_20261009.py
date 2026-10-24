"""Exact original-shell topology context; never grants placement acceptance.

Vertices are welded only by exact decoded coordinates. No rounding, geometry
repairs or acceptance-threshold exceptions are made.
"""
from collections import defaultdict, Counter
import numpy as np


def shell_context(triangles, seed_faces):
    tri = np.asarray(triangles, dtype=float)
    assert tri.ndim == 3 and tri.shape[1:] == (3, 3) and tri.size and np.isfinite(tri).all()
    assert all(isinstance(i, (int, np.integer)) and not isinstance(i, bool) for i in seed_faces)
    seeds = {int(i) for i in seed_faces}
    assert seeds and all(0 <= i < len(tri) for i in seeds)
    edges = defaultdict(list)
    face_edges = []
    for i, face in enumerate(tri):
        keys = []
        for a, b in zip(face, np.roll(face, -1, axis=0)):
            av, bv = tuple(a), tuple(b)
            key = tuple(sorted((av, bv)))
            edges[key].append((i, av == key[0]))
            keys.append(key)
        face_edges.append(keys)
    start = min(seeds)
    component, pending = {start}, [start]
    while pending:
        i = pending.pop()
        for key in face_edges[i]:
            for j, _ in edges[key]:
                if j not in component:
                    component.add(j)
                    pending.append(j)
    if not seeds.issubset(component):
        raise ValueError('Seed faces span disconnected original components')
    chosen = tri[sorted(component)]
    component_edges = {key:rows for key, rows in edges.items()
                       if any(i in component for i, _ in rows)}
    cross = np.cross(chosen[:, 1]-chosen[:, 0], chosen[:, 2]-chosen[:, 0])
    area = np.linalg.norm(cross, axis=1)/2
    lo, hi = chosen.min(axis=(0, 1)), chosen.max(axis=(0, 1))
    local = chosen-lo
    volume = float(np.einsum('ij,ij->i', local[:, 0],
                             np.cross(local[:, 1], local[:, 2])).sum()/6)
    edge_histogram = dict(sorted(Counter(len(v) for v in component_edges.values()).items()))
    inconsistent = sum(len(v) == 2 and v[0][1] == v[1][1] for v in component_edges.values())
    degenerate = int((area <= 1e-12).sum())
    closed_oriented = (set(edge_histogram) == {2} and not inconsistent and not degenerate)
    return {'seedFaces':sorted(seeds), 'componentFaces':sorted(component),
            'triangles':len(component), 'edgeIncidenceHistogram':edge_histogram,
            'inconsistentOrientedEdges':inconsistent, 'degenerateFaces':degenerate,
            'closedConsistentlyOriented':closed_oriented,
            'signedVolumeM3':volume, 'outwardPositiveVolume':closed_oriented and volume > 0,
            'bounds':[lo.tolist(), hi.tolist()], 'surfaceAreaM2':float(area.sum()),
            'exactCoordinateWelding':True, 'sourceGeometryChanges':0,
            'selfIntersectionCertified':False, 'placementAccepted':False,
            'qualification':'Closed oriented original shell is below-grade context only. It does not prove an authorised basement, absence of self-intersection, source clearance, visible detail, support, neighbourhood compatibility or installation acceptance.'}
