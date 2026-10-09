"""Polynomial exact finite triangle-union coverage, without area tolerances.

All polygon clips, crossing events and slice intervals use Fractions. Candidate
lookup is conservative only; it changes no geometry or acceptance predicate.
Full edge/point closure uses the existing exact interval proof independently.
"""
from fractions import Fraction
import hashlib,numpy as np,shapely
from exact_original_projection_coverage_20261009 import point,cross,signed_area,clip,exact_coverage
def intersection_x(a,b,c,d):
    u=(b[0]-a[0],b[1]-a[1]);v=(d[0]-c[0],d[1]-c[1]);det=u[0]*v[1]-u[1]*v[0]
    if det==0:return None
    w=(c[0]-a[0],c[1]-a[1]);t=(w[0]*v[1]-w[1]*v[0])/det;s=(w[0]*u[1]-w[1]*u[0])/det
    return a[0]+t*u[0] if 0<=t<=1 and 0<=s<=1 else None
def interval(poly,x):
    hits=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if min(a[0],b[0])<x<max(a[0],b[0]):hits.append(a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]))
    return (min(hits),max(hits)) if len(hits)>=2 else None
def slab_coverage(source_face,ground_triangles):
    source=np.asarray(source_face,float);ground=np.asarray(ground_triangles,float);assert source.shape==(3,3) and ground.ndim==3 and ground.shape[1:]==(3,3) and np.isfinite(source).all() and np.isfinite(ground).all()
    original=[point(p) for p in source[:,[0,2]]]
    if signed_area(original)==0:return exact_coverage(source,ground)
    if signed_area(original)<0:original.reverse()
    gxz=ground[:,:,[0,2]];lo=source[:,[0,2]].min(axis=0);hi=source[:,[0,2]].max(axis=0);ids=np.flatnonzero(np.all(gxz.max(axis=1)>=lo,axis=1)&np.all(gxz.min(axis=1)<=hi,axis=1));polys=[]
    for i in ids:
        poly=[point(p) for p in gxz[i]]
        if signed_area(poly)==0:continue
        if signed_area(poly)<0:poly.reverse()
        for a,b in zip(original,original[1:]+original[:1]):poly=clip(poly,a,b,True)
        if signed_area(poly)!=0:polys.append(poly)
    edges=sorted({tuple(sorted((a,b))) for poly in polys for a,b in zip(poly,poly[1:]+poly[:1]) if a!=b});events={p[0] for poly in polys+[original] for p in poly}
    if edges:
        boxes=[]
        for a,b in edges:
            v=np.asarray([list(map(float,a)),list(map(float,b))]);low=np.nextafter(v.min(axis=0),-np.inf);high=np.nextafter(v.max(axis=0),np.inf);boxes.append(shapely.box(*low,*high))
        tree=shapely.STRtree(boxes)
        for i,box in enumerate(boxes):
            for j in tree.query(box):
                if j<=i:continue
                x=intersection_x(*edges[i],*edges[int(j)])
                if x is not None:events.add(x)
    sorted_events=sorted(events);witness=None;checked=0
    for a,b in zip(sorted_events,sorted_events[1:]):
        if a==b:continue
        x=(a+b)/2;target=interval(original,x)
        if target is None:continue
        reach=target[0];segments=sorted(v for poly in polys if (v:=interval(poly,x)) is not None);checked+=1
        for low,high in segments:
            if low>reach:
                witness=[str(x),str((reach+min(low,target[1]))/2)];break
            reach=max(reach,high)
            if reach>=target[1]:break
        if witness is None and reach<target[1]:witness=[str(x),str((reach+target[1])/2)]
        if witness is not None:break
    edges_proof=[]
    if witness is None:
        for a,b in zip(source,np.roll(source,-1,axis=0)):edges_proof.append(exact_coverage(np.asarray([a,b,b]),ground))
    covered=witness is None and all(p['exactProjectionCovered'] for p in edges_proof)
    return {'exactProjectionCovered':covered,'method':'exact-fraction-finite-facet-vertical-slab-arrangement-and-three-closed-edge-unions',
        'completeOriginalGroundTrianglesAccounted':len(ground),'conservativeAABBCandidateGroundFacets':len(ids),
        'nonzeroExactClippedPolygons':len(polys),'exactCrossingEventCount':len(events),'slabsChecked':checked,
        'exactUncoveredInteriorWitnessXZ':witness,'closedSourceEdgeProofs':edges_proof,
        'sourceFaceSHA256':hashlib.sha256(source.tobytes()).hexdigest(),'completeGroundSHA256':hashlib.sha256(ground.tobytes()).hexdigest(),
        'noToleranceOrBufferCredit':True,'qualification':'All edge crossing/vertex x-events partition slices into intervals with stable linear boundary order. Every open slab is fully covered and each source edge is covered by the existing exact closed interval proof. No geometry is changed; source ground heights and physical support remain independent.'}
