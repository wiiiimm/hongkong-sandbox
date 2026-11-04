"""Unchanged V14 original-TIN inset construction, without patch approval.

Extracted from selected_original_local_inset_v14_20261029.py. This pure
construction step retains its area conservation and 1.2m new-land guards.
Final patch, renderer, neighbour and publication checks remain separate.
"""
import numpy as np
import shapely
from pathlib import Path
from run import ROOT,HERE,save,digest
from primrose_compound_foundation_v2_20261015 import module
from ronsdale_local_inset_v2_20261022 import plane,lift,parent_fragment_lift
from exact_affine_halfplane_clip_v1_20261024 import lower_region
from affine_terrain_blend_v1 import sector as blend_sector,evaluate as blend_evaluate
from provider_projection_seam_cover_v1_20261029 import cover as cover_provider_seam


def construct(baseline,projection,core,outer,checked,take,pins,refs,doc,local):
    a,b,c,d=outer.bounds
    decoder = module('selected_inset_source', HERE / 'xl-second-pass.py')
    decoder.LOCAL = local
    source, source_refs, source_planes = [], [], []
    for name in checked['sourceTerrainPaths']:
        path = ROOT / name
        metadata = take(path)
        for buffer in metadata.get('buffers', []):
            member = path.parent / buffer['uri']
            assert digest(member.read_bytes()) == pins[str(member.relative_to(ROOT))]
            refs.append(member)
        source_refs.append(dict(path=name, sha256=pins[name]))
        values = decoder.terrain_triangles(path)
        for face in values[(values[:, :, 0].max(1) >= a) & (values[:, :, 0].min(1) <= c) & (values[:, :, 2].max(1) >= b) & (values[:, :, 2].min(1) <= d)]:
            polygon = shapely.Polygon(face[:, [0, 2]])
            if polygon.area > 1e-10:
                # Keep the authored source plane through clipping. Tiny derived
                # triangles can be ill-conditioned for a second plane fit;
                # no clipped primitive or source facet is discarded here.
                coefficients = plane(face)
                parts = lift(polygon.intersection(outer), coefficients)
                source.extend(parts)
                source_planes.extend(coefficients.copy() for _ in parts)
    source = np.asarray(source)
    source, seam_planes, seam_proof = cover_provider_seam(source, projection)
    source_planes.extend(seam_planes)
    save(doc / 'provider-projection-seam-proof.json', seam_proof)
    refs.append(HERE / 'provider_projection_seam_cover_v1_20261029.py')
    polygons = shapely.polygons(source[:, :, [0, 2]])
    union = shapely.union_all(polygons)
    assert projection.difference(union).area < 1e-6, 'Original terrain does not cover the complete model projection'
    assert len(source_planes) == len(source)
    planes = source_planes
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
        sectors.append((polygon, blend_sector(xz, weights)))
    output, lineage, changed = [], [], []
    removed = inserted = 0.
    area_cases = []
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
            lower = lower_region(intersection, parentplane-planes[j])
            if lower.area <= 1e-10:
                continue
            cuts.append(lower)
            for region, weightplane in sectors:
                for part in lift(lower.intersection(region), planes[j]):
                    if weightplane is not None:
                        weights = blend_evaluate(part[:, [0, 2]], weightplane)
                        oldheight = part[:, [0, 2]] @ parentplane[:2]+parentplane[2]
                        part[:, 1] = part[:, 1]*(1-weights)+oldheight*weights
                    assert part[:, 1].min() >= 1.2, 'new-inset-surface-below-existing-clamp'
                    added.append((part, int(j)))
        if not cuts:
            output.append(face)
            lineage.append(dict(kind='unchanged', parentFace=i))
            continue
        cut = shapely.union_all(cuts)
        local_inserted = sum(shapely.Polygon(part[:, [0, 2]]).area for part, _ in added)
        if abs(cut.area-local_inserted) > 1e-9:
            area_cases.append(dict(parentFace=i, removedAreaM2=cut.area, insertedAreaM2=local_inserted, signedDifferenceM2=cut.area-local_inserted, parentTriangle=face.tolist(), cutWKT=cut.wkt, insertedTriangles=[part.tolist() for part, _ in added], sourceFaceIds=[j for _, j in added]))
        removed += cut.area
        changed.append(i)
        for part in parent_fragment_lift(polygon.difference(cut), parentplane):
            output.append(part)
            lineage.append(dict(kind='parent-fragment', parentFace=i))
        for part, j in added:
            output.append(part)
            lineage.append(dict(kind='original-inset-or-return', parentFace=i, sourceFace=j))
            inserted += shapely.Polygon(part[:, [0, 2]]).area
    save(doc / 'area-conservation-diagnostic.json.gz', dict(removedAreaM2=removed, insertedAreaM2=inserted, signedDifferenceM2=removed-inserted, existingLimitM2=1e-6, allLocalDiscrepanciesAboveOneBillionthM2=area_cases, toleranceChanged=False, installationApproved=False))
    assert abs(removed-inserted) < 1e-6
    output = np.asarray(output)
    return output, dict(changedParentFaces=changed,outputLineage=lineage,
        sourceFaces=source.tolist(),coreWKT=core.wkt,outerWKT=outer.wkt,
        removedAreaM2=removed,insertedAreaM2=inserted,sourceRefs=source_refs,
        providerProjectionSeam=seam_proof)
