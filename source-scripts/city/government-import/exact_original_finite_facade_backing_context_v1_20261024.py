"""Exact finite backing projection, without a distance/contact/mount admission rule."""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_projection_coverage_20261009 import signed_area,subtract


def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def point(v):return tuple(F(float(x))for x in v)
def bary(p,t):
    a,b,c=t;d=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);assert d
    u=((b[1]-c[1])*(p[0]-c[0])+(c[0]-b[0])*(p[1]-c[1]))/d;v=((c[1]-a[1])*(p[0]-c[0])+(a[0]-c[0])*(p[1]-c[1]))/d;return(u,v,1-u-v)
def segment_coverage(a,b,triangles):
    intervals=[]
    for t in triangles:
        aa,bb=bary(a,t),bary(b,t);left,right=F(0),F(1)
        for x,y in zip(aa,bb):
            delta=y-x
            if not delta:
                if x<0:left,right=F(1),F(0);break
            elif delta>0:left=max(left,-x/delta)
            else:right=min(right,-x/delta)
        if left<=right:intervals.append((left,right))
    merged=[]
    for left,right in sorted(intervals):
        if merged and left<=merged[-1][1]:merged[-1]=(merged[-1][0],max(right,merged[-1][1]))
        else:merged.append((left,right))
    return merged

def verify(source_face,host_faces):
    source=np.asarray(source_face,dtype='<f8');hosts=np.asarray(host_faces,dtype='<f8');assert source.shape==(3,3)and hosts.ndim==3 and hosts.shape[1:]==(3,3)and np.isfinite(source).all()and np.isfinite(hosts).all()
    points=[point(v)for v in source];ns=cross(tuple(points[1][j]-points[0][j]for j in range(3)),tuple(points[2][j]-points[0][j]for j in range(3)));assert any(ns),'Exactly nonrendering source cannot provide a backing facet'
    planes={};degenerate=[]
    for i,h in enumerate(hosts):
        t=[point(v)for v in h];n=cross(tuple(t[1][j]-t[0][j]for j in range(3)),tuple(t[2][j]-t[0][j]for j in range(3)));n2=sum(x*x for x in n)
        if not n2:degenerate.append(i);continue
        if n[1]*n[1]>n2/F(16):continue
        scale=next(x for x in n if x);normal=tuple(x/scale for x in n);d=-sum(normal[j]*t[0][j]for j in range(3));planes.setdefault((*normal,d),[]).append((i,t))
    witnesses=[];failures=[]
    for plane,entries in sorted(planes.items()):
        n=plane[:3];n2=sum(x*x for x in n);e=[sum(n[j]*p[j]for j in range(3))+plane[3]for p in points];feet=[tuple(p[j]-v*n[j]/n2 for j in range(3))for p,v in zip(points,e)];drop=max(range(3),key=lambda j:abs(n[j]));dims=[j for j in range(3)if j!=drop];projected=[tuple(p[j]for j in dims)for p in feet];host2d=[[tuple(p[j]for j in dims)for p in t]for _,t in entries];area=abs(signed_area(projected));intervals=[]
        if area:
            remaining=[projected]
            for h in host2d:
                remaining=[piece for polygon in remaining for piece in subtract(polygon,h)]
                if not remaining:break
            uncovered=sum(abs(signed_area(p))for p in remaining);covered=not remaining;dimension=2
        else:
            ends=sorted(set(projected));dimension=1 if len(ends)>1 else 0
            if dimension:intervals=segment_coverage(ends[0],ends[-1],host2d);covered=intervals==[(F(0),F(1))]
            else:covered=any(min(bary(ends[0],h))>=0 for h in host2d)
            uncovered=None
        record=dict(exactOriginalHostPlane=list(map(str,plane)),completeCoplanarHostFaceIndices=[i for i,_ in entries],exactOrthogonalFeet=[[str(v)for v in p]for p in feet],exactVertexSquaredPerpendicularDistancesM2=[str(v*v/n2)for v in e],projectedDimension=dimension,exactUncoveredProjectedArea=str(uncovered)if uncovered is not None else None,exactCoveredSegmentIntervals=[[str(v)for v in pair]for pair in intervals],completeFiniteProjectionCovered=covered)
        (witnesses if covered else failures).append(record)
    return dict(contract='exact-original-finite-facade-backing-projection-context-v1',completeOriginalFacetSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeHostSHA256=hashlib.sha256(hosts.tobytes()).hexdigest(),completeHostFaces=len(hosts),verifiedCompleteFiniteBackingProjection=bool(witnesses),allPassingFiniteBackingWitnesses=witnesses,uncoveredFiniteProjectionContexts=failures,exactNonrenderingHostFaceIndices=degenerate,originalSourceGeometryChanges=0,noDistanceAdmissionRule=True,existingPointOneMetreBandPassed=False,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,installationApproved=False,qualification='Actual finite coplanar source facets only; full rational orthogonal-foot area/segment/point coverage, preserving holes and non-dyadic feet. Distances are measured, never admitted as a contact or mounting tolerance. Complete projected backing does not prove attachment, architectural role, collision, support or publication.')
