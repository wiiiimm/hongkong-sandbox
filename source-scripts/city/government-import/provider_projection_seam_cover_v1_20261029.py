"""Add provider-edge-height terrain faces for bounded source projection seams.

The existing 0.25 m² and 2 mm nearest-edge bounds are unchanged. This helper
never edits existing provider faces or building geometry and grants no approval.
"""
import numpy as np
import shapely
from native_patch_resolution import _height_on_source_edge
from china_merchants_finite_inset_v4_20261021 import plane


def cover(source, projection):
    source = np.asarray(source, dtype='<f8')
    assert source.ndim == 3 and source.shape[1:] == (3, 3) and np.isfinite(source).all()
    polygons = shapely.polygons(source[:, :, [0, 2]])
    assert np.all(shapely.area(polygons) > 0)
    union = shapely.union_all(polygons)
    missing = projection.difference(union)
    proof = dict(beforeMissingAreaM2=float(missing.area), maximumSeamDistanceM=.002,
                 maximumSeamAreaM2=.25, retainedProviderFaces=len(source),
                 addedTerrainFaces=0, afterMissingAreaM2=float(missing.area),
                 buildingGeometryChanges=0, installationApproved=False)
    if missing.is_empty:
        return source.copy(), [], proof
    assert 0 < missing.area <= .25, 'provider-seam-area-exceeds-existing-bound'
    assert missing.difference(union.buffer(.002)).area < 1e-8, 'provider-seam-distance-exceeds-existing-bound'
    tree = shapely.STRtree(polygons)
    additions, planes, added_domains = [], [], []
    for triangle in shapely.get_parts(shapely.constrained_delaunay_triangles(missing)):
        if triangle.geom_type != 'Polygon':
            assert triangle.area == 0
            continue
        assert triangle.area > 0
        coords = list(triangle.exterior.coords)[:3]
        face = np.asarray([[x, _height_on_source_edge(shapely.Point(x, z), source, polygons, tree), z]
                           for x, z in coords], dtype='<f8')
        assert face[:, 1].min() >= 1.2, 'derived-provider-seam-below-existing-clamp'
        coefficients = plane(face)
        assert np.isfinite(coefficients).all()
        additions.append(face)
        planes.append(coefficients)
        added_domains.append(triangle)
    assert additions
    assert shapely.union_all(added_domains).symmetric_difference(missing).area < 1e-10
    result = np.concatenate([source, np.asarray(additions)])
    assert np.array_equal(result[:len(source)], source)
    after = projection.difference(shapely.union_all(shapely.polygons(result[:, :, [0, 2]])))
    assert after.area < 1e-6  # Same complete-projection gate as the inset builder.
    proof.update(addedTerrainFaces=len(additions), afterMissingAreaM2=float(after.area),
        addedDomainAreaM2=float(shapely.union_all(added_domains).area),
        policy='Additive terrain only: constrained triangulation of the exact missing projection, using existing nearest-provider-edge heights. Existing provider faces, source models and final terrain/runtime gates remain unchanged.')
    return result, planes, proof
