"""Rational convex-polygon subtraction for finite positive-area coverage proofs."""
from fractions import Fraction


def rational(points):
    return [tuple(Fraction.from_float(float(v))for v in p)for p in points]


def cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def area2(p):
    return sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(p,p[1:]+p[:1]))


def clip(poly,a,b,inside=True):
    result=[]
    if not poly:return result
    for s,t in zip(poly,poly[1:]+poly[:1]):
        x,y=cross(a,b,s),cross(a,b,t);si=x>=0 if inside else x<=0;ti=y>=0 if inside else y<=0
        if si:result.append(s)
        if si!=ti:
            f=x/(x-y);result.append(tuple(u+f*(v-u)for u,v in zip(s,t)))
    return result


def intersection(poly,triangle):
    assert len(triangle)==3 and area2(triangle)!=0
    if area2(triangle)<0:triangle=triangle[::-1]
    for a,b in zip(triangle,triangle[1:]+triangle[:1]):poly=clip(poly,a,b)
    return poly


def difference(poly,triangle):
    """Partition the positive-area exterior; shared closed boundaries remain covered."""
    assert len(triangle)==3 and area2(triangle)!=0
    if area2(triangle)<0:triangle=triangle[::-1]
    pieces=[]
    for a,b in zip(triangle,triangle[1:]+triangle[:1]):
        outside=clip(poly,a,b,False)
        if outside and area2(outside):pieces.append(outside)
        poly=clip(poly,a,b)
        if not poly or not area2(poly):break
    return pieces


def uncovered(poly,triangles):
    pending=[poly]if poly and area2(poly)else[]
    for triangle in triangles:
        pending=[q for p in pending for q in difference(p,triangle)]
        if not pending:break
    return pending
