"""Exact finite MAX-height equivalence across differing Float32 triangulations.

Pure diagnostic kernel. No tolerance, geometry edits, role or installation credit.
Uses the production nonvertical determinant cutoff; omitted primitives receive
no height/root credit. A strict domain expansion accounts for closed boundaries.
"""
from fractions import Fraction as F
import numpy as np


def area(poly):
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))/2 if len(poly)>2 else F(0)


def clip(poly, condition):
    if not poly:return []
    a,b,c=condition
    def value(p):return a*p[0]+b*p[1]+c
    out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        vp,vq=value(p),value(q)
        if vp>=0:out.append(p)
        if (vp<0)!=(vq<0):
            t=vp/(vp-vq);out.append(tuple(p[i]+t*(q[i]-p[i]) for i in range(2)))
    clean=[]
    for p in out:
        if not clean or p!=clean[-1]:clean.append(p)
    if len(clean)>1 and clean[0]==clean[-1]:clean.pop()
    return clean


def subtract(poly, conditions):
    """Disjoint convex interior pieces outside a closed convex intersection."""
    pieces=[];inside=poly
    for condition in conditions:
        if not any(condition):continue
        outside=clip(inside,tuple(-x for x in condition))
        if area(outside)>0:pieces.append(outside)
        inside=clip(inside,condition)
        if area(inside)<=0:break
    return pieces


def indexed_faces(triangles, domain):
    tri=np.asarray(triangles,dtype='<f4').astype('<f8')
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
    lo,hi=np.asarray(domain[:2],float),np.asarray(domain[2:],float)
    selected=np.flatnonzero(np.all(tri[:,:,[0,2]].max(1)>=lo,axis=1)&np.all(tri[:,:,[0,2]].min(1)<=hi,axis=1))
    rows=[];excluded=[]
    for i in selected:
        t=tri[i];ax,az=t[0,[0,2]];bx,bz=t[1,[0,2]];cx,cz=t[2,[0,2]]
        determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz)
        if abs(determinant)<1e-10:excluded.append(int(i));continue
        p,q,r=[tuple(F(float(v))for v in point)for point in t]
        ux,uz,uy=q[0]-p[0],q[2]-p[2],q[1]-p[1]
        vx,vz,vy=r[0]-p[0],r[2]-p[2],r[1]-p[1];d=ux*vz-uz*vx;assert d
        a,b=(uy*vz-uz*vy)/d,(ux*vy-uy*vx)/d
        plane=(a,b,p[1]-a*p[0]-b*p[2])
        polygon=[(v[0],v[2])for v in [p,q,r]]
        if area(polygon)<0:polygon.reverse()
        conditions=[]
        for x,y in zip(polygon,polygon[1:]+polygon[:1]):
            dx,dz=y[0]-x[0],y[1]-x[1];conditions.append((-dz,dx,dz*x[0]-dx*x[1]))
        rows.append(dict(face=int(i),polygon=polygon,plane=plane,conditions=conditions))
    return rows,excluded


def direction(source, target, domain):
    x0,z0,x1,z1=domain
    boundary=[(F(1),F(0),-x0),(-F(1),F(0),x1),(F(0),F(1),-z0),(F(0),-F(1),z1)]
    tested=0
    for row in source:
        polygon=row['polygon']
        for condition in boundary:polygon=clip(polygon,condition)
        if area(polygon)<=0:continue
        remaining=[polygon];tested+=1
        for other in target:
            delta=tuple(b-a for a,b in zip(row['plane'],other['plane']))
            remaining=[piece for pending in remaining for piece in subtract(pending,[*other['conditions'],delta])]
            if not remaining:break
        if remaining:
            polygon=remaining[0];point=tuple(sum(p[i]for p in polygon)/len(polygon)for i in range(2))
            heights=[]
            for other in target:
                if all(a*point[0]+b*point[1]+c>=0 for a,b,c in other['conditions']):
                    a,b,c=other['plane'];heights.append(a*point[0]+b*point[1]+c)
            a,b,c=row['plane'];height=a*point[0]+b*point[1]+c
            return dict(passed=False,facetsTested=tested,sourceFace=row['face'],exactWitnessXZ=list(map(str,point)),exactSourceHeight=str(height),exactTargetMaximumHeight=str(max(heights))if heights else None,exactUncoveredArea=str(sum(area(p)for p in remaining)))
    return dict(passed=True,facetsTested=tested)


def verify(before, after, bounds):
    assert len(bounds)==4 and bounds[0]<bounds[2]and bounds[1]<bounds[3]
    margin=F(1,1024);box=tuple(F(float(v))for v in bounds)
    expanded=(box[0]-margin,box[1]-margin,box[2]+margin,box[3]+margin)
    old,old_excluded=indexed_faces(before,expanded);new,new_excluded=indexed_faces(after,expanded)
    forward=direction(old,new,expanded);reverse=direction(new,old,expanded)
    return dict(exactHighestHeightEquivalent=forward['passed']and reverse['passed'],beforeBelowAfter=forward,afterBelowBefore=reverse,closedSourceBounds=list(bounds),exactConservativeDomainMarginM=str(margin),beforeIndexedFacets=len(old),afterIndexedFacets=len(new),beforeExcludedFacetIds=old_excluded,afterExcludedFacetIds=new_excluded,excludedPrimitivesReceiveNoHeightCredit=True,geometryChanges=0,physicalAcceptance=False,installationApproved=False,qualification=__doc__)
