"""Exact rational projected polygon coverage by ground strictly above a source ceiling."""
from fractions import Fraction as F

def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def area(p):return abs(sum(cross(p[i],p[(i+1)%len(p)])for i in range(len(p))))/2 if len(p)>2 else F(0)
def clip(p,a,b,c):
    """Closed affine half-plane a*x+b*z+c >= 0; exact intersections."""
    if not p:return []
    result=[]
    for start,end in zip(p,p[1:]+p[:1]):
        ds=a*start[0]+b*start[1]+c;de=a*end[0]+b*end[1]+c
        if ds>=0:result.append(start)
        if (ds<0 and de>0)or(ds>0 and de<0):
            t=ds/(ds-de);result.append(tuple(start[i]+t*(end[i]-start[i])for i in range(2)))
    return result

def subtract(subject,convex):
    sign=1 if sum(cross(convex[i],convex[(i+1)%len(convex)])for i in range(len(convex)))>0 else -1
    inside=subject;outside=[]
    for start,end in zip(convex,convex[1:]+convex[:1]):
        dx,dz=end[0]-start[0],end[1]-start[1]
        a,b,c=-sign*dz,sign*dx,sign*(dz*start[0]-dx*start[1])
        piece=clip(inside,-a,-b,-c)
        if area(piece)>0:outside.append(piece)
        inside=clip(inside,a,b,c)
        if area(inside)==0:break
    return outside

def prove(projected_triangle,source_top,triangles,minimum_margin=F(1,10)):
    assert minimum_margin>0
    subject=[tuple(F(float(v))for v in p)for p in projected_triangle]
    assert len(subject)==3 and area(subject)>0
    ceiling=F(float(source_top))+minimum_margin
    remaining=[subject];used=[]
    for index,t in enumerate(triangles):
        v=[tuple(F(float(x))for x in p)for p in t];xz=[(p[0],p[2])for p in v]
        dx0,dz0=xz[1][0]-xz[0][0],xz[1][1]-xz[0][1];dx1,dz1=xz[2][0]-xz[0][0],xz[2][1]-xz[0][1];det=dx0*dz1-dz0*dx1
        if det==0:continue
        dy0,dy1=v[1][1]-v[0][1],v[2][1]-v[0][1]
        px=(dy0*dz1-dy1*dz0)/det;pz=(dx0*dy1-dx1*dy0)/det
        constant=v[0][1]-px*xz[0][0]-pz*xz[0][1]-ceiling
        qualified=clip(xz,px,pz,constant)
        if area(qualified)==0:continue
        before=sum(map(area,remaining));remaining=[part for poly in remaining for part in subtract(poly,qualified)]
        if sum(map(area,remaining))<before:used.append(index)
        if not remaining:break
    assert not remaining,'Positive-area source projection lacks exact ground cover above the conservative source ceiling'
    return dict(completeProjectedTriangleCovered=True,strictlyBelowGroundEverywhere=True,minimumMarginExact=str(minimum_margin),sourceProjectedAreaExact=str(area(subject)),groundFaces=used,coordinateArithmetic='Exact rational clipping/subtraction on finite IEEE coordinates; no epsilon or sampling; closed cover above a strictly positive conservative ceiling.')
