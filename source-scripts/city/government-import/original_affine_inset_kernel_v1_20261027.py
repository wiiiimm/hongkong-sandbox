"""Private original-TIN lower inset with the existing affine return algorithm.

Extracts the V13 numerical method for partitioned parent domains. No source
model edits, publication, coverage exceptions, or acceptance decisions.
"""
import numpy as np
import shapely
from ronsdale_local_inset_v2_20261022 import plane, lift, parent_fragment_lift
from exact_affine_halfplane_clip_v1_20261024 import lower_region
from affine_terrain_blend_v1 import sector, evaluate


def source_upper_surface(original, projection, core, outer):
    assert outer.covers(core) and core.covers(projection)
    source, planes = [], []
    for face in np.asarray(original, dtype=float):
        polygon = shapely.Polygon(face[:, [0, 2]])
        if polygon.area <= 1e-10 or not polygon.intersects(outer):
            continue
        coefficients = plane(face)
        fragments = lift(polygon.intersection(outer), coefficients)
        source.extend(fragments)
        planes.extend(coefficients.copy() for _ in fragments)
    assert source, 'Original TIN must cover the complete source model'
    polygons = shapely.polygons(np.asarray(source)[:, :, [0, 2]])
    union = shapely.union_all(polygons)
    assert projection.difference(union).area < 1e-6, 'Original TIN must cover the complete source model'
    tree = shapely.STRtree(polygons)
    upper, upper_planes = [], []
    for i, polygon in enumerate(polygons):
        cuts = []
        for j in tree.query(polygon, predicate='intersects'):
            if i == j:
                continue
            overlap = polygon.intersection(polygons[j])
            if overlap.area <= 1e-10:
                continue
            if np.array_equal(planes[i], planes[j]):
                if j < i:
                    cuts.append(overlap)
            else:
                cuts.append(lower_region(overlap, planes[j]-planes[i]))
        kept = polygon.difference(shapely.union_all(cuts)) if cuts else polygon
        fragments = lift(kept, planes[i])
        upper.extend(fragments)
        upper_planes.extend(planes[i].copy() for _ in fragments)
    upper = np.asarray(upper)
    polygons = shapely.polygons(upper[:, :, [0, 2]])
    assert abs(float(shapely.area(polygons).sum()-shapely.union_all(polygons).area)) < 1e-6
    assert shapely.union_all(polygons).symmetric_difference(union).area < 1e-6
    return upper, upper_planes


def inset_parent(baseline, source, planes, core, outer):
    baseline, source = np.asarray(baseline, float), np.asarray(source, float)
    assert np.isfinite(baseline).all() and np.isfinite(source).all()
    assert baseline.shape[1:] == source.shape[1:] == (3, 3)
    assert len(planes) == len(source)
    polygons = shapely.polygons(source[:, :, [0, 2]])
    tree = shapely.STRtree(polygons)
    sectors = [(core, None)]
    for polygon in shapely.get_parts(shapely.constrained_delaunay_triangles(outer.difference(core))):
        if polygon.geom_type != 'Polygon' or polygon.area <= 0:
            continue
        xz = np.asarray(polygon.exterior.coords[:3])
        weights = []
        for x, z in xz:
            point = shapely.Point(x, z)
            inside = point.distance(core.boundary) < 1e-8
            outside = point.distance(outer.boundary) < 1e-8
            assert inside != outside
            weights.append(0. if inside else 1.)
        sectors.append((polygon, sector(xz, weights)))
    output, lineage, changed = [], [], []
    removed = inserted = 0.
    for i, face in enumerate(baseline):
        polygon = shapely.Polygon(face[:, [0, 2]])
        if polygon.area <= 1e-10 or not polygon.intersects(outer):
            output.append(face.copy())
            lineage.append(dict(kind='unchanged', parentFace=i))
            continue
        coefficients, cuts, added = plane(face), [], []
        for j in tree.query(polygon, predicate='intersects'):
            intersection = polygon.intersection(polygons[j])
            if intersection.area <= 1e-10:
                continue
            lower = lower_region(intersection, coefficients-planes[j])
            if lower.area <= 1e-10:
                continue
            cuts.append(lower)
            for region, weightplane in sectors:
                for part in lift(lower.intersection(region), planes[j]):
                    if weightplane is not None:
                        weights = evaluate(part[:, [0, 2]], weightplane)
                        oldheight = part[:, [0, 2]] @ coefficients[:2]+coefficients[2]
                        part[:, 1] = part[:, 1]*(1-weights)+oldheight*weights
                    assert part[:, 1].min() >= 1.2, 'new-inset-surface-below-existing-clamp'
                    added.append((part, int(j)))
        if not cuts:
            output.append(face.copy())
            lineage.append(dict(kind='unchanged', parentFace=i))
            continue
        cut = shapely.union_all(cuts)
        removed += cut.area
        changed.append(i)
        for part in parent_fragment_lift(polygon.difference(cut), coefficients):
            output.append(part)
            lineage.append(dict(kind='parent-fragment', parentFace=i))
        for part, j in added:
            output.append(part)
            inserted += shapely.Polygon(part[:, [0, 2]]).area
            lineage.append(dict(kind='original-inset-or-return', parentFace=i, sourceFace=j))
    assert abs(removed-inserted) < 1e-6, 'Replacement area conservation failed'
    return np.asarray(output), dict(changedParentFaces=changed, outputLineage=lineage,
                                   removedAreaM2=removed, insertedAreaM2=inserted)
