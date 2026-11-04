"""Clip represented polygon coordinates by an affine half-plane using Fractions.

Coordinates round once at output; numerical gates and source planes are unchanged.
"""
from fractions import Fraction
import numpy as np
import shapely


def convex_positive(region, difference):
    assert region.geom_type == 'Polygon' and not region.interiors
    coeff = tuple(Fraction(float(v)) for v in difference)
    points = [tuple(Fraction(float(v)) for v in p[:2]) for p in region.exterior.coords[:-1]]
    def value(p):
        return coeff[0]*p[0]+coeff[1]*p[1]+coeff[2]
    out = []
    for a, b in zip(points, points[1:]+points[:1]):
        va, vb = value(a), value(b)
        if va > 0:
            out.append(a)
        if (va > 0) != (vb > 0):
            ratio = va/(va-vb)
            out.append(tuple(a[j]+ratio*(b[j]-a[j]) for j in range(2)))
    result = shapely.Polygon([(float(x), float(z)) for x, z in out]) if len(out) >= 3 else shapely.Polygon()
    if not result.is_valid:
        repaired = shapely.make_valid(result)
        assert abs(repaired.area-result.area) <= 1e-12
        assert shapely.hausdorff_distance(result, repaired) <= 1e-12
        result = repaired
    return result


def lower_region(region, difference):
    difference = np.asarray(difference, float)
    assert difference.shape == (3,) and np.isfinite(difference).all()
    parts = list(shapely.get_parts(region))
    polygons = []
    while parts:
        p = parts.pop()
        if p.geom_type == 'Polygon':
            polygons.append(p)
        elif p.geom_type in ('GeometryCollection', 'MultiPolygon'):
            parts.extend(shapely.get_parts(p))
        else:
            assert p.area == 0
    assert abs(sum(p.area for p in polygons)-region.area) < 1e-10
    return shapely.union_all([convex_positive(p, difference) for p in polygons])
