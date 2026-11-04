"""Exact unchanged source component contacts; geometric evidence, never support approval.

Broad-phase bounds are inclusive and unpadded. Narrow phase uses the exact
rational value of every decoded binary coordinate. Point contacts, line
contacts and coplanar area contacts remain distinct; none implies load bearing.
"""
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face, intersection_points, cross, sub


def contact_measure(points):
    pts = sorted(points)
    dimension = 0
    if len(pts) > 1:
        direction = sub(pts[1], pts[0])
        dimension = 2 if any(any(cross(direction, sub(p, pts[0]))) for p in pts[2:]) else 1
    arr = np.asarray([[float(v) for v in p] for p in pts])
    length = max((float(np.linalg.norm(a-b)) for a in arr for b in arr), default=0)
    return {'dimension': dimension, 'maximumSpanM': length,
            'bounds': [arr.min(axis=0).tolist(), arr.max(axis=0).tolist()],
            'exactPoints': [[str(v) for v in p] for p in pts]}


def exact_component_contacts(triangles_a, face_ids_a, triangles_b, face_ids_b,
                             *, first_only=False, maximum_pairs=1000000):
    a, b = np.asarray(triangles_a), np.asarray(triangles_b)
    ids_b = np.asarray(face_ids_b, dtype=int)
    assert len(face_ids_a) and len(ids_b)
    low, high = b[ids_b].min(axis=1), b[ids_b].max(axis=1)
    cached_a, cached_b, records, tested = {}, {}, [], 0
    for fi in face_ids_a:
        fi = int(fi)
        hits = np.flatnonzero(np.all(high >= a[fi].min(axis=0), axis=1) &
                              np.all(low <= a[fi].max(axis=0), axis=1))
        if not len(hits):
            continue
        if fi not in cached_a:
            cached_a[fi] = rational_face(a[fi])
        for ix in hits:
            fj = int(ids_b[ix]); tested += 1
            assert tested <= maximum_pairs, 'Explicit exact-pair resource bound exceeded'
            if fj not in cached_b:
                cached_b[fj] = rational_face(b[fj])
            points = intersection_points(cached_a[fi], cached_b[fj])
            if points:
                records.append({'sourceFaceA': fi, 'sourceFaceB': fj,
                                **contact_measure(points)})
                if first_only:
                    return {'contacts': records, 'trianglePairsTested': tested,
                            'allPairsExamined': False, 'geometryChanges': 0,
                            'physicalSupportAccepted': False}
    return {'contacts': records, 'trianglePairsTested': tested,
            'allPairsExamined': True, 'geometryChanges': 0,
            'physicalSupportAccepted': False}
