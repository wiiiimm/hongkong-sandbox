"""Apply existing rendered-Float32 coverage policy to captured parent terrain."""
import numpy as np
import shapely
from float32_coverage import approve_roundoff, geometry_sha
from native_patch_resolution import projected_context


def qualify(faces, bounds):
    faces = np.asarray(faces, dtype=float)
    assert faces.ndim == 3 and faces.shape[1:] == (3, 3) and len(faces)
    assert np.isfinite(faces).all()
    mesh = dict(position=faces.reshape(-1).tolist(), index=list(range(faces.size//3)), source={})
    patch = dict(nativeMesh=mesh)
    before = geometry_sha(patch)
    raw = shapely.union_all(shapely.polygons(faces[:, :, [0, 2]]))
    extent = shapely.box(*bounds)
    _, polygons, _, _ = projected_context(patch, bounds)
    rendered = shapely.union_all(polygons)
    area = float(rendered.symmetric_difference(extent).area)
    proof = approve_roundoff(patch, bounds) if area else None
    assert geometry_sha(patch) == before
    return dict(rawOverlayDifferenceM2=float(raw.symmetric_difference(extent).area),
        renderedFloat32DifferenceM2=area, existingNumericalCoverageProof=proof,
        geometrySHA256=before, geometryChanges=0,
        policy='Existing Float32 terrain coverage policy only; no new threshold, hole fill, source change or placement approval.')
