"""Clip by exact original-facet equations, retaining existing output-repair bounds.

Original coordinates stay untouched. Preserve rational coefficients until the
single output-coordinate rounding; do not refit clipped or tiny derived faces.
"""
from fractions import Fraction as F
import numpy as np
import shapely
from exact_finite_upper_surface_cells_20261011 import rational, plane


def from_original_facet(face):
    values = np.asarray(face, dtype=float)
    assert values.shape == (3, 3) and np.isfinite(values).all()
    return plane([rational(row) for row in values])


def convex_positive(region, difference):
    assert region.geom_type == 'Polygon' and not region.interiors
    coeff = tuple(v if isinstance(v, F) else F(float(v)) for v in difference)
    points = [tuple(F(float(v)) for v in p[:2]) for p in region.exterior.coords[:-1]]
    def value(p):
        return coeff[0] * p[0] + coeff[1] * p[1] + coeff[2]
    out = []
    for a, b in zip(points, points[1:] + points[:1]):
        va, vb = value(a), value(b)
        if va > 0:
            out.append(a)
        if (va > 0) != (vb > 0):
            ratio = va / (va - vb)
            out.append(tuple(a[j] + ratio * (b[j] - a[j]) for j in range(2)))
    result = shapely.Polygon([tuple(map(float, p)) for p in out]) if len(out) >= 3 else shapely.Polygon()
    if not result.is_valid:
        repaired = shapely.make_valid(result)
        assert abs(repaired.area - result.area) <= 1e-12
        assert shapely.hausdorff_distance(result, repaired) <= 1e-12
        result = repaired
    return result


def lower_region(region, difference):
    coefficients = np.asarray(difference, dtype=object)
    assert coefficients.shape == (3,) and np.isfinite(np.asarray(coefficients, dtype=float)).all()
    parts, polygons = list(shapely.get_parts(region)), []
    while parts:
        part = parts.pop()
        if part.geom_type == 'Polygon':
            polygons.append(part)
        elif part.geom_type in ('GeometryCollection', 'MultiPolygon'):
            parts.extend(shapely.get_parts(part))
        else:
            assert part.area == 0
    assert abs(sum(p.area for p in polygons) - region.area) < 1e-10
    return shapely.union_all([convex_positive(p, coefficients) for p in polygons])
