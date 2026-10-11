"""Finite vertical ray census of a complete two-level closed actual mesh.

Mixed winding/zero-area primitives are retained. A unique nonboundary upper and
lower crossing proves odd closed-surface ray parity; it grants no source role,
support, surveyed height, geometry modification or positive installation credit.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,sub,cross

def projected_hit(point,triangle):
    x,z=point[0],point[2];a,b,c=triangle
    den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
    if den:
        u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
        v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den
        w=1-u-v
        return 'strict' if min(u,v,w)>0 else 'boundary' if min(u,v,w)>=0 else 'none'
    for p,q in zip(triangle,triangle[1:]+triangle[:1]):
        dx,dz=q[0]-p[0],q[2]-p[2]
        if dx*(z-p[2])!=dz*(x-p[0]):continue
        if min(p[0],q[0])<=x<=max(p[0],q[0]) and min(p[2],q[2])<=z<=max(p[2],q[2]):return 'boundary'
    return 'none'

def verify(triangles,point):
    a=np.asarray(triangles,dtype='<f8');assert a.ndim==3 and a.shape[1:]==(3,3) and len(a) and np.isfinite(a).all()
    assert len(point)==3 and all(isinstance(v,F) for v in point)
    low=F(float(a[:,:,1].min()));high=F(float(a[:,:,1].max()));assert low<high
    counts=Counter();directions=defaultdict(list);top=[];bottom=[];sides=[];zero=[];fractions=[]
    for i,f in enumerate(a):
        q=rational_face(f);fractions.append(q);ys={p[1] for p in q}
        n=cross(sub(q[1],q[0]),sub(q[2],q[0]))
        if n==(F(0),F(0),F(0)):zero.append(i)
        for p,r in zip(q,q[1:]+q[:1]):
            key=tuple(sorted((p,r)));counts[key]+=1;directions[key].append((p,r))
        if ys=={high}:top.append(i)
        elif ys=={low}:bottom.append(i)
        else:assert ys=={low,high} and n[1]==0,'Not an actual two-level vertical side';sides.append(i)
    assert set(counts.values())=={2} and all(v[0]==tuple(reversed(v[1])) for v in directions.values()),'Complete finite mesh is not closed with opposite edge pairs'
    keys=lambda ids:sorted(tuple(sorted((p[0],p[2]) for p in fractions[i])) for i in ids)
    assert keys(top)==keys(bottom),'Upper/lower actual cap projections differ'
    hits={kind:dict(strict=[],boundary=[]) for kind in ['upper','lower','vertical']}
    for kind,ids in [('upper',top),('lower',bottom),('vertical',sides)]:
        for i in ids:
            hit=projected_hit(point,fractions[i])
            if hit!='none':hits[kind][hit].append(i)
    interior=low<point[1]<high and len(hits['upper']['strict'])==len(hits['lower']['strict'])==1 and not any(v['boundary'] for v in hits.values()) and not hits['vertical']['strict']
    return dict(contract='complete-two-level-closed-mesh-finite-vertical-ray-census-v1',completeFaces=len(a),completeOppositeClosedEdgePairs=len(counts),completeUpperCapFaces=top,completeLowerCapFaces=bottom,completeVerticalFaces=sides,completeZeroAreaPrimitiveFaceIDs=zero,completeAllFacesAccounted=len(top)+len(bottom)+len(sides)==len(a),exactPoint=[str(v) for v in point],exactLowerHKPD=str(low),exactUpperHKPD=str(high),completeFiniteProjectedRayHits=hits,strictOddParityInterior=bool(interior),capWindingAssumed=False,zeroAreaFaceOmissions=0,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False)
