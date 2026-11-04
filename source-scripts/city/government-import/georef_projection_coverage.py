"""Certify whole-cell coverage despite sub-nanometre planar-union artifacts.

This never buffers or modifies runtime/source geometry. Raw measurements stay
authoritative for extent, unrelated overlap and contact checks. Only a vanishing
GEOS union residue may use a one-nanometre precision union as a second proof.
"""
import numpy as np
import shapely

GRID_METRES = 1e-9
MAXIMUM_RESIDUE_AREA_M2 = 1e-10

def whole_cell_coverage(triangles, cell, projection):
    raw_covers = bool(projection.covers(cell))
    result = {'policy': 'whole-georef-cell-double-precision-union-v1',
        'rawProjectionCoversWholeCell': raw_covers, 'coversWholeCell': raw_covers,
        'numericalCorrectionApplied': False, 'maximumResidueAreaM2': MAXIMUM_RESIDUE_AREA_M2,
        'precisionGridMetres': GRID_METRES, 'modelGeometryChanges': 0}
    if raw_covers: return result
    missing = cell.difference(projection)
    result['rawMissingAreaM2'] = float(missing.area)
    if (not projection.is_valid or projection.is_empty or missing.is_empty
            or not np.isfinite(missing.area) or missing.area > MAXIMUM_RESIDUE_AREA_M2):
        return result
    # Area alone must never allow a long thin real gap. The complete residue
    # must be within a nanometre of the unchanged raw projection as well.
    if not projection.buffer(GRID_METRES).covers(missing): return result
    tri = np.asarray(triangles, dtype=float)
    if tri.ndim != 3 or tri.shape[1:] != (3, 3) or not np.isfinite(tri).all(): return result
    robust = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]), grid_size=GRID_METRES)
    covers = bool(robust.is_valid and robust.covers(cell))
    result.update(coversWholeCell=covers, numericalCorrectionApplied=covers,
        robustProjectionCoversWholeCell=covers,
        rawAndRobustSymmetricDifferenceAreaM2=float(projection.symmetric_difference(robust).area),
        qualification='Whole one-metre cell at one-nanometre planar computation precision; raw residue also bounded by area and distance. Original model bytes, vertices, transforms and all physical/spatial gates unchanged.')
    return result
