"""Bound a collapsed convex clip by exact area and Hausdorff budgets.

The ordinary V1 path stays first. Only an invalid rounded convex result whose
ordinary repair fails may use a represented line. Exact symmetric-difference
area is its full rational target area; both continuous Hausdorff directions
are bounded using convexity and exact point/segment distances. Existing 1e-12
square-metre and 1e-12 metre limits are unchanged. Original assets are untouched.
"""
from fractions import Fraction as F
from itertools import combinations, product
import math
import numpy as np
import shapely
from exact_affine_halfplane_clip_v1_20261024 import convex_positive as ordinary

# Bind the exact existing binary64 literals, including their last bits.
AREA_LIMIT = F(1e-12)
DISTANCE_SQUARED_LIMIT = F(1e-12)**2
REPAIRS = []


def signed_area(points):
    return sum(a[0]*b[1]-b[0]*a[1]
               for a, b in zip(points, points[1:]+points[:1])) / 2


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def convex(points):
    if len(points) < 3 or signed_area(points) == 0:
        return False
    sign = 1 if signed_area(points) > 0 else -1
    return all(sign*cross(a,b,p) >= 0 for a,b in zip(points,points[1:]+points[:1])
               for p in points)


def segment_distance_squared(p, a, b):
    delta = tuple(b[i]-a[i] for i in range(2))
    length = sum(v*v for v in delta)
    if not length:
        return sum((p[i]-a[i])**2 for i in range(2))
    t = max(F(0), min(F(1), sum((p[i]-a[i])*delta[i] for i in range(2))/length))
    return sum((p[i]-a[i]-t*delta[i])**2 for i in range(2))


def polygon_distance_squared(p, points):
    signs = [cross(a,b,p) for a,b in zip(points, points[1:]+points[:1])]
    if all(v >= 0 for v in signs) or all(v <= 0 for v in signs):
        return F(0)
    return min(segment_distance_squared(p,a,b) for a,b in zip(points,points[1:]+points[:1]))


def neighbours(point):
    choices = []
    for value in point:
        rounded = float(value)
        choices.append([rounded, math.nextafter(rounded,-math.inf),
                         math.nextafter(rounded,math.inf)])
    return [tuple(F(x) for x in pair) for pair in product(*choices)
            if all(math.isfinite(x) for x in pair)]


def bounded_line(points):
    assert len(points) >= 3 and convex(points)
    area = abs(signed_area(points))
    assert area <= AREA_LIMIT
    # Longest candidate spans first; stop after the first complete witness.
    pairs = sorted(combinations(range(len(points)),2), reverse=True,
                   key=lambda pair: sum((points[pair[0]][i]-points[pair[1]][i])**2 for i in range(2)))
    for first, second in pairs:
        for a,b in product(neighbours(points[first]), neighbours(points[second])):
            if a == b:
                continue
            forward = max(segment_distance_squared(p,a,b) for p in points)
            if forward > DISTANCE_SQUARED_LIMIT:
                continue
            backward = max(polygon_distance_squared(p,points) for p in [a,b])
            if backward > DISTANCE_SQUARED_LIMIT:
                continue
            return shapely.LineString([[float(x) for x in p] for p in [a,b]]), dict(
                exactTargetVertices=[[str(x) for x in p] for p in points],
                exactSymmetricDifferenceAreaM2=str(area), exactAreaLimitM2=str(AREA_LIMIT),
                exactForwardHausdorffSquaredM2=str(forward),
                exactBackwardHausdorffSquaredM2=str(backward),
                exactDistanceSquaredLimitM2=str(DISTANCE_SQUARED_LIMIT),
                continuousHausdorffDirectionsProvedByConvexity=True,
                sourceGeometryChanges=0, genericThresholdChanges=0)
    raise AssertionError('No represented line satisfies both unchanged exact repair limits')


def convex_positive(region, difference):
    assert region.geom_type == 'Polygon' and not region.interiors
    assert len(difference) == 3 and all(math.isfinite(float(v)) for v in difference)
    try:
        return ordinary(region,difference)
    except AssertionError:
        pass
    assert region.is_valid
    coefficients = tuple(F(float(v)) for v in difference)
    points = [tuple(F(float(v)) for v in p[:2]) for p in region.exterior.coords[:-1]]
    assert convex(points)
    def value(p):
        return coefficients[0]*p[0]+coefficients[1]*p[1]+coefficients[2]
    target = []
    for a,b in zip(points,points[1:]+points[:1]):
        va,vb = value(a),value(b)
        if va > 0:
            target.append(a)
        if (va > 0) != (vb > 0):
            ratio = va/(va-vb)
            target.append(tuple(a[i]+ratio*(b[i]-a[i]) for i in range(2)))
    assert len(target) >= 3
    rounded = shapely.Polygon([[float(v) for v in p] for p in target])
    assert not rounded.is_valid
    result, proof = bounded_line(target)
    REPAIRS.append(dict(operandWKB=region.wkb_hex,
        exactDifference=[str(c) for c in coefficients],
        rawRoundedWKB=rounded.wkb_hex, outputWKB=result.wkb_hex, **proof))
    return result


def lower_region(region, difference):
    difference = np.asarray(difference,float)
    assert difference.shape == (3,) and np.isfinite(difference).all()
    parts, polygons = list(shapely.get_parts(region)), []
    while parts:
        part = parts.pop()
        if part.geom_type == 'Polygon':
            polygons.append(part)
        elif part.geom_type in ('GeometryCollection','MultiPolygon'):
            parts.extend(shapely.get_parts(part))
        else:
            assert part.area == 0
    assert abs(sum(p.area for p in polygons)-region.area) < 1e-10
    return shapely.union_all([convex_positive(p,difference) for p in polygons])
