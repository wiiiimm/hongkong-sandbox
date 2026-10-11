"""Whole original face ground intersections, diagnostic only.

The minimum is continuous on each source/ground pair, including vertical
walls. Maximum is an observed witness, not an upper-envelope certificate.
Shapely intersection coordinates use floating point, without geometry edits.
"""
import numpy as np
import shapely
from exact_terrain_contact_20261009 import _height


def _vertical_heights(face, x, z):
    """All authored triangle edge intersections with this projected point."""
    values = []
    point = np.array([x, z])
    for a, b in zip(face, np.roll(face, -1, axis=0)):
        delta = b[[0, 2]]-a[[0, 2]]
        axis = int(np.argmax(np.abs(delta)))
        if delta[axis] == 0:
            if np.array_equal(point, a[[0, 2]]):
                values.extend([float(a[1]), float(b[1])])
            continue
        t = (point[axis]-a[[0, 2]][axis])/delta[axis]
        # Intersection coordinates have bounded floating arithmetic error.
        if -1e-10 <= t <= 1+1e-10:
            values.append(float(a[1]+np.clip(t, 0, 1)*(b[1]-a[1])))
    assert values, 'Projected point has no authored source edge intersection'
    return min(values), max(values)


def face_ground_context(face, ground, polygons=None, tree=None):
    face, ground = np.asarray(face, dtype=float), np.asarray(ground, dtype=float)
    assert face.shape == (3, 3) and ground.ndim == 3 and ground.shape[1:] == (3, 3)
    assert ground.size and np.isfinite(face).all() and np.isfinite(ground).all()
    normal = np.cross(face[1]-face[0], face[2]-face[0])
    assert np.linalg.norm(normal) > 0, 'Degenerate authored face'
    if polygons is None:
        polygons = shapely.polygons(ground[:, :, [0, 2]])
        assert np.all(shapely.area(polygons) > 1e-10), 'Invalid ground projection'
    if tree is None:
        tree = shapely.STRtree(polygons)
    projection = shapely.MultiPoint(face[:, [0, 2]]).convex_hull
    vertical = normal[1] == 0
    assert vertical == (projection.geom_type != 'Polygon'), 'Projection rank mismatch'
    hits = tree.query(projection, predicate='intersects')
    overlaps = []; witnesses = []
    for ground_id in hits:
        overlap = projection.intersection(polygons[ground_id])
        if overlap.is_empty:
            continue
        overlaps.append(overlap)
        coords = list(shapely.get_coordinates(overlap))
        if vertical:
            # Lower/upper authored edge envelopes can change at a projected
            # original vertex inside a ground interval. Include all breakpoints.
            coords += [v[[0, 2]] for v in face if overlap.covers(shapely.Point(v[[0, 2]]))]
        for x, z in coords:
            low, high = (_vertical_heights(face, x, z) if vertical
                         else (_height(face, x, z),)*2)
            gy = _height(ground[ground_id], x, z)
            # Pair minima remain valid against the highest ground envelope:
            # min(S-max(G)) = min over all intersecting ground facet pairs.
            witnesses.append({'minimumGapM':low-gy, 'position':[float(x), low, float(z)],
                              'terrainHeight':gy, 'terrainFace':int(ground_id)})
            point_hits = tree.query(shapely.Point(x, z), predicate='intersects')
            highest = max([gy, *(_height(ground[j], x, z) for j in point_hits)])
            witnesses[-1]['upperObservedGapM'] = high-highest
    covered = shapely.union_all(overlaps).covers(projection) if overlaps else False
    return {'verticalFace':bool(vertical), 'groundProjectionCovered':bool(covered),
            'minimum':min(witnesses, key=lambda r:r['minimumGapM']) if witnesses else None,
            'maximumObservedGapM':max((r['upperObservedGapM'] for r in witnesses), default=None),
            'groundFacetPairs':len(overlaps), 'continuousMaximumCertified':False,
            'floatingIntersectionArithmetic':True, 'diagnosticOnly':True,
            'geometryChanges':0, 'installationApproved':False}
