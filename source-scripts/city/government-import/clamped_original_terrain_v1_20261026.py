"""Partition affine terrain at the existing height floor; never edit source files."""
import hashlib
import numpy as np
import shapely
from ronsdale_local_inset_v2_20261022 import plane, lift, lower_region


def clamp_surface(triangles, *, floor):
    raw = np.asarray(triangles, dtype=float)
    assert raw.ndim == 3 and raw.shape[1:] == (3, 3) and len(raw)
    assert np.isfinite(raw).all() and floor == 1.2
    output, cut_faces, floor_area = [], [], 0.
    level = np.array([0., 0., floor])
    for index, face in enumerate(raw):
        polygon = shapely.Polygon(face[:, [0, 2]])
        assert polygon.area > 1e-10
        affine = plane(face)
        if face[:, 1].min() >= floor:
            output.append(face.copy())
            continue
        cut_faces.append(index)
        if face[:, 1].max() <= floor:
            low, high = polygon, shapely.Polygon()
        else:
            low = lower_region(polygon, level-affine)
            high = polygon.difference(low)
        assert low.intersection(high).area < 1e-10
        assert polygon.symmetric_difference(low.union(high)).area < 1e-8
        floor_area += low.area
        for region, coefficients in [(low, level), (high, affine)]:
            for piece in lift(region, coefficients):
                # Level-set intersection arithmetic may round a boundary below
                # the floor. Bound that correction; no clearance limit changes.
                assert piece[:, 1].min() >= floor-1e-10
                piece[:, 1] = np.maximum(piece[:, 1], floor)
                output.append(piece)
    result = np.asarray(output)
    before = shapely.union_all(shapely.polygons(raw[:, :, [0, 2]]))
    polygons = shapely.polygons(result[:, :, [0, 2]])
    assert before.symmetric_difference(shapely.union_all(polygons)).area < 1e-6
    assert abs(shapely.area(polygons).sum()-before.area) < 1e-6
    assert result[:, :, 1].min() >= floor
    return result, dict(policy='max-original-affine-terrain-and-existing-1.2m-floor',
        sourceSurfaceSHA256=hashlib.sha256(raw.astype('<f8').tobytes()).hexdigest(),
        outputSurfaceSHA256=hashlib.sha256(result.astype('<f8').tobytes()).hexdigest(),
        sourceFaces=len(raw), outputFaces=len(result), partitionedSourceFaceIds=cut_faces,
        floorHeightM=floor, flooredProjectionAreaM2=floor_area,
        originalBuildingGeometryChanges=0, sourceFileChanges=0,
        installationApproved=False, globalClearanceLimitsChanged=False)
