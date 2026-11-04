"""Bind unchanged rendered low parent facets outside a new land-only edit."""
from collections import Counter
import numpy as np
import shapely


def face_key(face):
    return np.asarray(face, dtype='<f4').tobytes()


def bind(faces, edit):
    values = np.asarray(faces, dtype=np.float32).astype(float)
    assert values.ndim == 3 and values.shape[1:] == (3, 3) and np.isfinite(values).all()
    ids = np.flatnonzero(values[:, :, 1].min(1) < 1.2).tolist()
    for i in ids:
        assert shapely.MultiPoint(values[i][:, [0, 2]]).convex_hull.disjoint(edit), 'Existing below-clamp face touches the proposed edit region'
    return dict(faceIds=ids, keys=Counter(face_key(values[i]) for i in ids))


def verify(output, binding):
    values = np.asarray(output, dtype=np.float32).astype(float)
    assert values.ndim == 3 and values.shape[1:] == (3, 3) and np.isfinite(values).all()
    after = Counter(face_key(f) for f in values if f[:, 1].min() < 1.2)
    assert after == binding['keys'], 'A below-clamp rendered parent facet was changed, removed, duplicated or introduced'
    return dict(unchangedLowParentFaces=len(binding['faceIds']), exactFloat32FaceMultiplicityPreserved=True, everyLowFaceOutsideEdit=True, newLandSurfaceMinimumM=1.2, installationApproved=False)
