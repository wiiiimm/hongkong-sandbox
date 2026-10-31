"""Vectorized original TIN point heights; diagnostics never grant acceptance."""
import numpy as np
import shapely


def indexed_surface(triangles):
    tri = np.asarray(triangles, dtype=float).reshape(-1, 3, 3)
    polygons = shapely.polygons(tri[:, :, [0, 2]])
    keep = shapely.area(polygons) > 1e-10
    return tri[keep], shapely.STRtree(polygons[keep])


def point_heights(points, indexed):
    """Return all covering original facets and the highest original surface.

    Empty and uncovered points yield -inf. Boundary tolerance is numeric only;
    heights are interpolated on the unchanged original triangle planes.
    """
    points = np.asarray(points, dtype=float).reshape(-1, 3)
    tri, tree = indexed
    si, fi = tree.query(shapely.points(points[:, [0, 2]]), predicate='dwithin', distance=1e-7)
    faces = tri[fi]
    a, b, c = faces[:, 0], faces[:, 1], faces[:, 2]
    v = points[si][:, [0, 2]] - c[:, [0, 2]]
    u0, u1 = a[:, [0, 2]]-c[:, [0, 2]], b[:, [0, 2]]-c[:, [0, 2]]
    det = u0[:, 0]*u1[:, 1]-u1[:, 0]*u0[:, 1]
    u = (v[:, 0]*u1[:, 1]-u1[:, 0]*v[:, 1])/det
    w = (u0[:, 0]*v[:, 1]-v[:, 0]*u0[:, 1])/det
    keep = np.minimum(np.minimum(u, w), 1-u-w) >= -1e-7
    si = si[keep]
    heights = (u*a[:, 1]+w*b[:, 1]+(1-u-w)*c[:, 1])[keep]
    highest = np.full(len(points), -np.inf)
    np.maximum.at(highest, si, heights)
    return si, heights, highest
