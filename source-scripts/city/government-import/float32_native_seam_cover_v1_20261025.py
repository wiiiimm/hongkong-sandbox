"""Add bounded Float32-representable terrain covers; never alter existing faces."""
import itertools
import numpy as np
import shapely
from native_patch_resolution import projected_context, _height_on_source_edge


def cover(patch, bounds):
    faces, polygons, missing, _ = projected_context(patch, bounds)
    union = shapely.union_all(polygons)
    assert 0 < missing.area <= .25
    assert missing.difference(union.buffer(.002)).area < 1e-8
    tree = shapely.STRtree(polygons)
    additions = []
    domains = []
    for part in shapely.get_parts(shapely.constrained_delaunay_triangles(missing)):
        if part.geom_type != 'Polygon' or part.area <= 1e-12:
            continue
        corners = []
        for x, z in list(part.exterior.coords)[:3]:
            # An outward enclosing cell at each vertex gives a convex cover of
            # the entire triangle, not just its centroid or sampled edges.
            x, z = np.float32(x), np.float32(z)
            xs = [np.nextafter(x, np.float32(-np.inf)), np.nextafter(x, np.float32(np.inf))]
            zs = [np.nextafter(z, np.float32(-np.inf)), np.nextafter(z, np.float32(np.inf))]
            corners.extend((float(a), float(b)) for a, b in itertools.product(xs, zs))
        hull = shapely.MultiPoint(corners).convex_hull
        assert hull.covers(part)
        domains.append(hull)
        for triangle in shapely.get_parts(shapely.constrained_delaunay_triangles(hull)):
            if triangle.geom_type != 'Polygon' or triangle.area <= 1e-12:
                continue
            coords = list(triangle.exterior.coords)[:3]
            additions.append([[x, _height_on_source_edge(shapely.Point(x, z), faces, polygons, tree), z] for x, z in coords])
    assert additions
    domain = shapely.union_all(domains)
    assert domain.area <= .25 and domain.difference(union.buffer(.002)).area < 1e-8
    assert domain.difference(shapely.box(*bounds)).area < 1e-8
    mesh = patch['nativeMesh']
    old_position, old_index = list(mesh['position']), list(mesh['index'])
    offset = len(mesh['position']) // 3
    data = np.asarray(additions, dtype=np.float32).astype(float)
    assert data[:, :, 1].min() >= 1.2
    mesh['position'].extend(data.reshape(-1).tolist())
    mesh['index'].extend(range(offset, offset + data.size // 3))
    assert mesh['position'][:len(old_position)] == old_position
    assert mesh['index'][:len(old_index)] == old_index
    _, _, after, excess = projected_context(patch, bounds)
    assert after.area < 1e-10
    return dict(beforeMissingAreaM2=float(missing.area), afterMissingAreaM2=float(after.area), addedTerrainTriangles=len(data), addedDomainAreaM2=float(domain.area), projectedExcessM2=float(excess), unchangedOriginalTerrainTriangles=len(old_index)//3, maximumSeamDistanceM=.002, sourceGeometryChanges=0, policy='Private additive terrain seam cover. Convex Float32 vertex-cell hulls enclose every missing triangle; nearest existing terrain edge heights used. All original terrain faces preserved. No building geometry or clearance policy edits; actual runtime and neighbours require fresh checks.')
