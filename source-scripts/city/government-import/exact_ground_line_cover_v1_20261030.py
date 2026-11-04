"""Exact rational upper-height-field cover of a finite projected source line."""
from fractions import Fraction as F

def q(value):return F(float(value))
def cross(a,b):return a[0]*b[1]-a[1]*b[0]

def prove(start,end,source_top,triangles):
    a=tuple(map(q,start));b=tuple(map(q,end));direction=tuple(b[i]-a[i]for i in range(2));top=q(source_top)
    assert any(direction)
    segments=[]
    for index,t in enumerate(triangles):
        v=[tuple(map(q,p))for p in t]
        xz=[(p[0],p[2])for p in v]
        d0=(xz[1][0]-xz[0][0],xz[1][1]-xz[0][1]);d1=(xz[2][0]-xz[0][0],xz[2][1]-xz[0][1]);det=cross(d0,d1)
        if det==0:continue
        lo,hi=F(0),F(1);sign=1 if det>0 else -1
        for i in range(3):
            x,y=xz[i],xz[(i+1)%3];edge=(y[0]-x[0],y[1]-x[1]);origin=(a[0]-x[0],a[1]-x[1])
            constant=sign*cross(edge,origin);slope=sign*cross(edge,direction)
            if slope>0:lo=max(lo,-constant/slope)
            elif slope<0:hi=min(hi,-constant/slope)
            elif constant<0:lo,hi=F(1),F(0);break
        if lo>hi:continue
        dy0=v[1][1]-v[0][1];dy1=v[2][1]-v[0][1]
        px=(dy0*d1[1]-dy1*d0[1])/det;pz=(d0[0]*dy1-d1[0]*dy0)/det
        intercept=v[0][1]+px*(a[0]-xz[0][0])+pz*(a[1]-xz[0][1]);slope=px*direction[0]+pz*direction[1]
        segments.append((lo,hi,slope,intercept,index))
    cuts={F(0),F(1)}
    for lo,hi,*_ in segments:cuts.update([lo,hi])
    for i,left in enumerate(segments):
        for right in segments[i+1:]:
            lo=max(left[0],right[0]);hi=min(left[1],right[1]);slope=left[2]-right[2]
            if lo>hi or slope==0:continue
            where=(right[3]-left[3])/slope
            if lo<where<hi:cuts.add(where)
    cuts=sorted(cuts);proof=[];minimum=None
    for lo,hi in zip(cuts,cuts[1:]):
        if lo==hi:continue
        midpoint=(lo+hi)/2;active=[s for s in segments if s[0]<=midpoint<=s[1]]
        assert active,'Finite source line has an uncovered ground interval'
        owner=max(active,key=lambda s:(s[2]*midpoint+s[3],-s[4]))
        gap=min(owner[2]*lo+owner[3]-top,owner[2]*hi+owner[3]-top)
        assert gap>0,'Source closure is not strictly below the continuous upper ground field'
        minimum=gap if minimum is None else min(minimum,gap)
        proof.append(dict(start=str(lo),end=str(hi),groundFace=owner[4],minimumMarginExact=str(gap)))
    assert proof and cuts[0]==0 and cuts[-1]==1 and minimum is not None
    return dict(completeFiniteLineCovered=True,strictlyBelowGroundEverywhere=True,minimumMarginM=float(minimum),minimumMarginExact=str(minimum),pieces=proof,coordinateArithmetic='Exact rational arithmetic on supplied finite IEEE vertex values; no epsilon, sampling or gap fill.')
