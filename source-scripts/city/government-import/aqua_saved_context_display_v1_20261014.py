"""Display-only saved-coordinate helpers; no role/topology/acceptance proof."""
import numpy as np

def plot_xyz(xyz):
    """Matplotlib standard Z-up: horizontal world X/Z, vertical HKPD Y."""
    a=np.asarray(xyz)
    assert a.shape[-1]==3
    return a[..., [0,2,1]]

def exact_coordinate_context(tri, face_ids):
    """Exact coordinate incidences across duplicate indices, not connectivity credit."""
    a=np.asarray(tri); assert a.ndim==3 and a.shape[1:]==(3,3)
    assert np.isfinite(a).all()
    vertex={}; edge={}
    for i,t in enumerate(a):
        keys=[tuple(float(x) for x in p) for p in t]
        for p in set(keys): vertex.setdefault(p,[]).append(i)
        for j in range(3):
            k=tuple(sorted((keys[j],keys[(j+1)%3])))
            edge.setdefault(k,[]).append(i)
    rows=[]
    for i in face_ids:
        keys=[tuple(float(x) for x in p) for p in a[i]]
        v=sorted({j for p in keys for j in vertex[p]})
        e=sorted({j for k in range(3) for j in edge[tuple(sorted((keys[k],keys[(k+1)%3]))) ]})
        rows.append(dict(originalFaceID=int(i),exactXYZSharedVertexFaceIDs=v,exactXYZWholeEdgeFaceIDs=e,coordinateIncidenceOnlyNotAuthoredRoleOrTopology=True))
    return rows

def closed_display_crop(tri, lower, upper):
    a=np.asarray(tri)
    return np.flatnonzero((a.max(axis=1)>=lower).all(axis=1)&(a.min(axis=1)<=upper).all(axis=1))
