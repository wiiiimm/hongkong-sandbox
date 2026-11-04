"""Reuse the established original-TIN upper envelope and bounded return math.

No building geometry input is edited. Output is a terrain diagnostic until
separate surface, source, current-neighbour and publication checks pass.
"""
import numpy as np
import shapely
from ronsdale_local_inset_v2_20261022 import plane,lift,lower_region,parent_fragment_lift


def inset_faces(baseline,terrain,projection):
    baseline=np.asarray(baseline,dtype=float)
    assert baseline.ndim==3 and baseline.shape[1:]==(3,3)and np.isfinite(baseline).all()
    core=projection.buffer(1,join_style='mitre');outer=core.buffer(3,join_style='mitre')
    a,b,c,d=outer.bounds;values=np.asarray(terrain,dtype=float)
    assert values.ndim==3 and values.shape[1:]==(3,3)and np.isfinite(values).all()
    source=[]
    for face in values[(values[:,:,0].max(1)>=a)&(values[:,:,0].min(1)<=c)&(values[:,:,2].max(1)>=b)&(values[:,:,2].min(1)<=d)]:
        polygon=shapely.Polygon(face[:,[0,2]])
        if polygon.area>1e-10:source.extend(lift(polygon.intersection(outer),plane(face)))
    assert source,'No finite original terrain in the proposed inset'
    source = np.asarray(source)
    polygons = shapely.polygons(source[:, :, [0, 2]])
    union = shapely.union_all(polygons)
    assert projection.difference(union).area < 1e-6, 'Original terrain does not cover the complete model projection'
    planes = [plane(face) for face in source]
    tree = shapely.STRtree(polygons)
    upper, upperlineage = [], []
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
        for face in lift(kept, planes[i]):
            upper.append(face)
            upperlineage.append(i)
    source = np.asarray(upper)
    polygons = shapely.polygons(source[:, :, [0, 2]])
    assert abs(float(shapely.area(polygons).sum()-shapely.union_all(polygons).area)) < 1e-6
    assert shapely.union_all(polygons).symmetric_difference(union).area < 1e-6
    planes = [planes[i] for i in upperlineage]
    tree = shapely.STRtree(polygons)
    sectors = [(core, None)]
    for polygon in shapely.get_parts(shapely.constrained_delaunay_triangles(outer.difference(core))):
        if polygon.geom_type != 'Polygon' or polygon.area <= 0:
            continue
        xz = np.asarray(polygon.exterior.coords[:3])
        weights = []
        for x, z in xz:
            point = shapely.Point(x, z)
            inside, outside = point.distance(core.boundary) < 1e-8, point.distance(outer.boundary) < 1e-8
            assert inside != outside
            weights.append(0. if inside else 1.)
        sectors.append((polygon, plane(np.column_stack([xz[:, 0], weights, xz[:, 1]]))))
    output, lineage, changed = [], [], []
    removed = inserted = 0.
    for i, face in enumerate(baseline):
        polygon = shapely.Polygon(face[:, [0, 2]])
        if polygon.area <= 1e-10 or not polygon.intersects(outer):
            output.append(face)
            lineage.append(dict(kind='unchanged', parentFace=i))
            continue
        parentplane, cuts, added = plane(face), [], []
        for j in tree.query(polygon, predicate='intersects'):
            intersection = polygon.intersection(polygons[j])
            if intersection.area <= 1e-10:
                continue
            # Replace with the exact original terrain in the core whether
            # it is higher or lower than current ground. All unchanged
            # clamp, seam, coverage and whole-neighbour gates still apply.
            lower = intersection
            if lower.area <= 1e-10:
                continue
            cuts.append(lower)
            for region, weightplane in sectors:
                for part in lift(lower.intersection(region), planes[j]):
                    if weightplane is not None:
                        weights = np.clip(part[:, [0, 2]] @ weightplane[:2]+weightplane[2], 0, 1)
                        oldheight = part[:, [0, 2]] @ parentplane[:2]+parentplane[2]
                        part[:, 1] = part[:, 1]*(1-weights)+oldheight*weights
                    assert part[:, 1].min() >= 1.2, 'new-inset-surface-below-existing-clamp'
                    added.append((part, int(j)))
        if not cuts:
            output.append(face)
            lineage.append(dict(kind='unchanged', parentFace=i))
            continue
        cut = shapely.union_all(cuts)
        removed += cut.area
        changed.append(i)
        for part in parent_fragment_lift(polygon.difference(cut), parentplane):
            output.append(part)
            lineage.append(dict(kind='parent-fragment', parentFace=i))
        for part, j in added:
            output.append(part)
            lineage.append(dict(kind='original-inset-or-return', parentFace=i, sourceFace=j))
            inserted += shapely.Polygon(part[:, [0, 2]]).area
    assert abs(removed-inserted) < 1e-6
    output = np.asarray(output)
    return dict(output=output,lineage=lineage,changedParentFaces=changed,highestOriginalFaces=source,
        core=core,outer=outer,removedAreaM2=removed,insertedAreaM2=inserted)
