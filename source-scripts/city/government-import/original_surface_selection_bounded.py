"""Select lower unchanged rendered facets; compute regions without editing heights."""
import numpy as np
import shapely

def lower_original_surface_projection(patch, bounds, projection, sampler):
    """Select exact parent facets only where they lie below the source terrain.

    This computes a mask, not new elevations. Intersections of two planar source
    triangles are clipped at their equal-height line before parent preservation.
    """
    protected = projection.intersection(shapely.box(*bounds))
    if protected.is_empty:
        return protected, {'areaM2': 0.0, 'planePairs': 0}
    parents = np.asarray(sampler.surface_faces(protected))
    if parents.size == 0:
        return shapely.Polygon(), {'areaM2': 0.0, 'planePairs': 0}
    polygons = shapely.polygons(parents[:, :, [0, 2]])
    tree = shapely.STRtree(polygons)
    selected, pairs = [], 0

    def plane(face):
        normal = np.cross(face[1] - face[0], face[2] - face[0])
        assert abs(normal[1]) > 1e-10
        ax, az = -normal[0] / normal[1], -normal[2] / normal[1]
        return np.array([ax, az, face[0, 1] - ax * face[0, 0] - az * face[0, 2]])

    for face in np.asarray(patch['nativeMesh']['position']).reshape(-1,3)[np.asarray(patch['nativeMesh']['index']).reshape(-1,3)]:
        poly = shapely.Polygon(face[:, [0, 2]])
        if poly.area <= 1e-10 or not poly.intersects(protected):
            continue
        native_plane = plane(face)
        for i in tree.query(poly, predicate='intersects'):
            # Each grid facet was already clipped to protected; constrained
            # triangulation keeps these intersections convex.
            region = poly.intersection(polygons[i])
            if region.area <= 1e-10:
                continue
            diff = plane(parents[i]) - native_plane
            coords = list(region.exterior.coords)[:-1]
            clipped = []
            for a, b in zip(coords, coords[1:] + coords[:1]):
                da, db = np.dot(diff, [*a, 1]), np.dot(diff, [*b, 1])
                if da < -1e-8:
                    clipped.append(a)
                if (da < -1e-8) != (db < -1e-8):
                    t = (-1e-8 - da) / (db - da)
                    clipped.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            pairs += 1
            if len(clipped) >= 3:
                selected.append(shapely.Polygon(clipped))
    result = (shapely.union_all(selected) if selected else shapely.Polygon()).intersection(protected)
    return result, {'areaM2': float(result.area), 'planePairs': pairs,
                    'policy': 'Retain existing parent facets only below the original native terrain plane inside the supplied source-face mask; no invented or shifted heights.'}
