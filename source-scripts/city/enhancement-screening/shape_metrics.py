"""Deterministic CPU multi-view comparison. Metrics are evidence, not source approval."""
import math
import numpy as np
from numba import njit

VERSION = 'shape-comparison-v1'
# Several compass directions prevent one facade from hiding a different roof/wing.
VIEWS = [(a, e) for e in (15, 40) for a in range(0, 360, 45)] + [(0, 90)]
RESOLUTIONS = (96, 192)
POLICY = {'version': VERSION, 'views': VIEWS, 'resolutions': RESOLUTIONS,
          'maxSilhouetteDifference': .01, 'maxChangedSurfaceFraction': .01,
          'maxDepthErrorMetres': .20, 'pixelDepthTolerance': .5,
          'maxBoundsDifferenceMetres': .20,
          'usefulSilhouetteDifference': .04, 'usefulChangedSurfaceFraction': .05,
          'usefulDepthErrorMetres': .5}


def mesh(value):
    p = np.asarray(value, dtype=np.float64)
    if p.size == 0 or p.size % 9 or not np.isfinite(p).all():
        raise ValueError('Non-finite, empty or incomplete triangle geometry')
    return p.reshape(-1, 3, 3)


@njit(cache=True)
def raster(projected, size):
    """Orthographic two-sided z-buffer; closest depth wins, independent of winding."""
    z = np.full((size, size), -np.inf)
    for t in projected:
        ax, ay, az = t[0]; bx, by, bz = t[1]; cx, cy, cz = t[2]
        den = (by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(den) < 1e-12:
            continue
        lo_x=max(0,int(math.ceil(min(ax,bx,cx)-.5)));hi_x=min(size-1,int(math.floor(max(ax,bx,cx)-.5)))
        lo_y=max(0,int(math.ceil(min(ay,by,cy)-.5)));hi_y=min(size-1,int(math.floor(max(ay,by,cy)-.5)))
        for y in range(lo_y, hi_y+1):
            for x in range(lo_x, hi_x+1):
                u=((by-cy)*(x+.5-cx)+(cx-bx)*(y+.5-cy))/den
                v=((cy-ay)*(x+.5-cx)+(ax-cx)*(y+.5-cy))/den
                w=1-u-v
                if min(u,v,w) >= -1e-9:
                    depth=u*az+v*bz+w*cz
                    if depth>z[y,x]:z[y,x]=depth
    return z


def frame(a, b, azimuth, elevation, size):
    """Both meshes use one world frame. Never recenter/rescale them independently."""
    az, el = np.radians([azimuth,elevation])
    eye=np.array([np.sin(az)*np.cos(el),np.sin(el),np.cos(az)*np.cos(el)])
    right=np.array([np.cos(az),0,-np.sin(az)]);up=np.cross(eye,right)
    basis=np.array([right,up,eye]).T
    bounds=np.concatenate([a.reshape(-1,3),b.reshape(-1,3)])
    origin=(bounds.min(axis=0)+bounds.max(axis=0))/2
    x=(a-origin)@basis;y=(b-origin)@basis
    points=np.concatenate([x.reshape(-1,3),y.reshape(-1,3)])
    low=points[:,:2].min(axis=0);high=points[:,:2].max(axis=0)
    extent=float(max(high-low))
    if extent<=1e-6:raise ValueError('Degenerate comparison extent')
    scale=(size-8)/extent;center=(low+high)/2
    x[:,:,:2]=(x[:,:,:2]-center)*scale+size/2
    y[:,:,:2]=(y[:,:,:2]-center)*scale+size/2
    return raster(x,size),raster(y,size),1/scale


def view_metrics(a,b,pixel_metres):
    ma=np.isfinite(a);mb=np.isfinite(b);union=ma|mb;overlap=ma&mb
    if min(ma.sum(),mb.sum()) < 16:
        raise ValueError('Insufficient raster coverage')
    delta=np.abs(a[overlap]-b[overlap]);tolerance=max(.10,pixel_metres*POLICY['pixelDepthTolerance'])
    return {'silhouetteDifference':float(np.count_nonzero(ma^mb)/union.sum()),
            'changedSurfaceFraction':float(np.count_nonzero(delta>tolerance)/max(1,overlap.sum())),
            'depthP95Metres':float(np.quantile(delta,.95)) if delta.size else None,
            'depthMaxMetres':float(delta.max()) if delta.size else None,
            'overlapPixels':int(overlap.sum()),'metresPerPixel':pixel_metres}


def classify_metrics(result):
    v=result['views']
    negligible=(result['boundsDifferenceMetres']<=POLICY['maxBoundsDifferenceMetres'] and
        all(r['silhouetteDifference']<=POLICY['maxSilhouetteDifference'] and
            r['changedSurfaceFraction']<=POLICY['maxChangedSurfaceFraction'] and
            r['depthP95Metres'] is not None and r['depthP95Metres']<=POLICY['maxDepthErrorMetres'] for r in v))
    if negligible:return 'negligible-difference'
    # Require evidence at both resolutions; tiny one-view raster artefacts stay uncertain.
    useful=all(any(r['size']==s and (r['silhouetteDifference']>=POLICY['usefulSilhouetteDifference'] or
                 (r['changedSurfaceFraction']>=POLICY['usefulChangedSurfaceFraction'] and
                  r['depthP95Metres'] is not None and r['depthP95Metres']>=POLICY['usefulDepthErrorMetres'])) for r in v) for s in RESOLUTIONS)
    return 'material-difference' if useful else 'uncertain-difference'


def compare(current,candidate,diagnose_offset=True):
    a=mesh(current);b=mesh(candidate);rows=[]
    for size in RESOLUTIONS:
        for az,el in VIEWS:
            x,y,pixel=frame(a,b,az,el,size)
            rows.append({'size':size,'azimuth':az,'elevation':el,**view_metrics(x,y,pixel)})
    bounds=lambda m:np.r_[m.reshape(-1,3).min(axis=0),m.reshape(-1,3).max(axis=0)]
    result={'views':rows,'boundsDifferenceMetres':float(np.max(np.abs(bounds(a)-bounds(b)))),
            'currentTriangles':len(a),'candidateTriangles':len(b)}
    result['comparison']=classify_metrics(result)
    result['roof']=next(r for r in rows if r['size']==max(RESOLUTIONS) and r['elevation']==90)
    # Diagnose a rigid positional discrepancy without moving either actual source.
    # It is not evidence that the candidate adds architectural detail.
    if diagnose_offset and result['comparison']=='material-difference':
        delta=(bounds(b)-bounds(a)).reshape(2,3)
        if np.max(np.abs(delta[0]-delta[1]))<=.20:
            offset=delta.mean(axis=0)
            if np.max(np.abs(offset))>.20:
                aligned=compare(a,b-offset,diagnose_offset=False)
                result['offsetDiagnostic']={'translationMetres':offset.tolist(),'alignedComparison':aligned['comparison']}
                if aligned['comparison']=='negligible-difference':result['comparison']='placement-only-difference'
    return result
