"""Exact point/segment/triangle contacts, retaining all original source primitives."""
import numpy as np
from exact_original_shell_intersections_20261009 import (
    rational_face, intersection_points, segment_has, sub, add, mul, dot, cross, cross2,
)
from exact_original_component_contacts_20261009 import contact_measure


def primitive(face):
    normal = cross(sub(face[1], face[0]), sub(face[2], face[0]))
    if any(normal):
        return 2, face
    points = sorted(set(face))
    return (0, points) if len(points) == 1 else (1, [points[0], points[-1]])


def inside_triangle(point, triangle):
    normal = cross(sub(triangle[1], triangle[0]), sub(triangle[2], triangle[0]))
    assert any(normal)
    if dot(normal, sub(point, triangle[0])):
        return False
    axis = max(range(3), key=lambda i: abs(normal[i]))
    axes = [i for i in range(3) if i != axis]
    xy = lambda p: tuple(p[i] for i in axes)
    signs = [cross2(sub(xy(b), xy(a)), sub(xy(point), xy(a)))
             for a, b in zip(triangle, triangle[1:] + triangle[:1])]
    return all(s >= 0 for s in signs) or all(s <= 0 for s in signs)


def segment_intersection(a, b, u, v):
    direction, other, offset = sub(b, a), sub(v, u), sub(u, a)
    assert any(direction) and any(other)
    normal = cross(direction, other)
    if not any(normal):
        if any(cross(direction, offset)):
            return set()
        return {p for p in [a, b, u, v] if segment_has(a, b, p) and segment_has(u, v, p)}
    if dot(offset, normal):
        return set()
    axis = max(range(3), key=lambda i: abs(normal[i]))
    axes = [i for i in range(3) if i != axis]
    xy = lambda p: tuple(p[i] for i in axes)
    denominator = cross2(xy(direction), xy(other))
    t = cross2(xy(offset), xy(other)) / denominator
    k = cross2(xy(offset), xy(direction)) / denominator
    if 0 <= t <= 1 and 0 <= k <= 1:
        point = add(a, mul(direction, t))
        assert point == add(u, mul(other, k))
        return {point}
    return set()


def segment_triangle(a, b, triangle):
    normal = cross(sub(triangle[1], triangle[0]), sub(triangle[2], triangle[0]))
    da, db = dot(normal, sub(a, triangle[0])), dot(normal, sub(b, triangle[0]))
    if da == db == 0:
        points = {p for p in [a, b] if inside_triangle(p, triangle)}
        for u, v in zip(triangle, triangle[1:] + triangle[:1]):
            points |= segment_intersection(a, b, u, v)
        return points
    if da * db > 0 or da == db:
        return set()
    t = da / (da - db)
    point = add(a, mul(sub(b, a), t))
    return {point} if 0 <= t <= 1 and inside_triangle(point, triangle) else set()


def primitive_intersections(a, b):
    da, pa = primitive(a)
    db, pb = primitive(b)
    if da > db:
        da, db, pa, pb = db, da, pb, pa
    if da == 0:
        point = pa[0]
        contained = point == pb[0] if db == 0 else segment_has(*pb, point) if db == 1 else inside_triangle(point, pb)
        return {point} if contained else set()
    if da == 1:
        return segment_intersection(*pa, *pb) if db == 1 else segment_triangle(*pa, pb)
    return intersection_points(pa, pb)


def exact_component_contacts_with_primitives(triangles_a, face_ids_a, triangles_b, face_ids_b,
                                             *, first_only=False, maximum_pairs=1000000):
    a, b = np.asarray(triangles_a), np.asarray(triangles_b)
    ids_a, ids_b = list(map(int, face_ids_a)), np.asarray(face_ids_b, dtype=int)
    assert ids_a and len(ids_b)
    cache_a = {i: rational_face(a[i]) for i in ids_a}
    cache_b = {int(i): rational_face(b[i]) for i in ids_b}
    dimensions_a = {i: primitive(f)[0] for i, f in cache_a.items()}
    dimensions_b = {i: primitive(f)[0] for i, f in cache_b.items()}
    low, high = b[ids_b].min(axis=1), b[ids_b].max(axis=1)
    records, tested = [], 0
    for fi in ids_a:
        hits = np.flatnonzero(np.all(high >= a[fi].min(axis=0), axis=1) & np.all(low <= a[fi].max(axis=0), axis=1))
        for ix in hits:
            fj = int(ids_b[ix])
            tested += 1
            assert tested <= maximum_pairs, 'Explicit exact-pair resource bound exceeded'
            points = primitive_intersections(cache_a[fi], cache_b[fj])
            if points:
                records.append(dict(sourceFaceA=fi, sourceFaceB=fj,
                                    primitiveDimensions=[dimensions_a[fi], dimensions_b[fj]],
                                    surfacePair=dimensions_a[fi] == dimensions_b[fj] == 2,
                                    **contact_measure(points)))
                if first_only:
                    break
        if first_only and records:
            break
    return dict(contacts=records, trianglePairsTested=tested,
                allPairsExamined=not(first_only and records),
                originalFacePrimitiveDimensionsA=dimensions_a,
                originalFacePrimitiveDimensionsB=dimensions_b,
                geometryChanges=0, physicalSupportAccepted=False,
                qualification='Exact rational contacts for every original primitive. Zero-area point/line primitives remain explicit and receive no surface-support credit. No source geometry edits or identity/placement approval.')
