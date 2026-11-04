"""Exact contact classifications; no collision, identity or support acceptance."""
from exact_original_shell_intersections_20261009 import cross, cross2, dot, sub


def strictly_inside_triangle(point, face):
    normal = cross(sub(face[1], face[0]), sub(face[2], face[0]))
    assert any(normal)
    if dot(normal, sub(point, face[0])):
        return False
    drop = max(range(3), key=lambda i: abs(normal[i]))
    xy = lambda p: tuple(p[i] for i in range(3) if i != drop)
    signs = [cross2(sub(xy(b), xy(a)), sub(xy(point), xy(a))) for a, b in zip(face, face[1:] + face[:1])]
    return all(s > 0 for s in signs) or all(s < 0 for s in signs)


def contact_role(face_a, face_b, points, dimension, primitive_dimensions):
    assert points
    if primitive_dimensions != [2, 2]:
        return 'original-degenerate-primitive-contact'
    if dimension == 2:
        return 'shared-plane-area-contact'
    if dimension == 0:
        return 'surface-point-contact'
    assert dimension == 1
    normal_a = cross(sub(face_a[1], face_a[0]), sub(face_a[2], face_a[0]))
    normal_b = cross(sub(face_b[1], face_b[0]), sub(face_b[2], face_b[0]))
    if not any(cross(normal_a, normal_b)):
        return 'coplanar-edge-contact'
    midpoint = tuple(sum(p[i] for p in points) / len(points) for i in range(3))
    return 'transverse-surface-crossing' if strictly_inside_triangle(midpoint, face_a) and strictly_inside_triangle(midpoint, face_b) else 'source-edge-surface-contact'
