"""Bounded exact rational triangle intersections in an unchanged source shell.

All decoded binary coordinates become exact rational numbers; no epsilon or
vertex repair is used. Shared source edges/vertices are legal contacts only.
"""
from fractions import Fraction
from itertools import combinations
import math


def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,t):return tuple(x*t for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]


def rational_face(face):
    assert len(face)==3 and all(len(p)==3 and all(math.isfinite(float(v)) for v in p) for p in face)
    return tuple(tuple(Fraction(float(x)) for x in p) for p in face)


def segment_has(a,b,p):
    d=sub(b,a)
    if not any(d):return p==a
    if any(cross(d,sub(p,a))):return False
    axis=max(range(3),key=lambda i:abs(d[i]))
    t=(p[axis]-a[axis])/d[axis]
    return 0<=t<=1


def plane_slice(face,distances):
    points={face[i] for i,d in enumerate(distances) if d==0}
    for i,j in [(0,1),(1,2),(2,0)]:
        a,b=distances[i],distances[j]
        if a*b<0:points.add(add(face[i],mul(sub(face[j],face[i]),a/(a-b))))
    return sorted(points)


def coplanar_intersections(a,b,normal):
    dropped=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=dropped]
    xy=lambda p:tuple(p[i] for i in axes)
    def inside(p,face):
        d=[cross2(sub(xy(y),xy(x)),sub(xy(p),xy(x))) for x,y in zip(face,face[1:]+face[:1])]
        return all(x>=0 for x in d) or all(x<=0 for x in d)
    points={p for p in a if inside(p,b)}|{p for p in b if inside(p,a)}
    for x,y in zip(a,a[1:]+a[:1]):
        r=sub(xy(y),xy(x))
        for u,v in zip(b,b[1:]+b[:1]):
            s=sub(xy(v),xy(u));den=cross2(r,s);offset=sub(xy(u),xy(x))
            if den:
                t,k=cross2(offset,s)/den,cross2(offset,r)/den
                if 0<=t<=1 and 0<=k<=1:points.add(add(x,mul(sub(y,x),t)))
            elif cross2(offset,r)==0:
                for p in [x,y,u,v]:
                    if segment_has(x,y,p) and segment_has(u,v,p):points.add(p)
    return points


def intersection_points(a,b):
    na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]))
    assert any(na) and any(nb),'Degenerate source triangle'
    da=[dot(nb,sub(p,b[0])) for p in a];db=[dot(na,sub(p,a[0])) for p in b]
    if any(all(d>0 for d in ds) or all(d<0 for d in ds) for ds in [da,db]):return set()
    if all(d==0 for d in da):return coplanar_intersections(a,b,na)
    direction=cross(na,nb)
    if not any(direction):return set()
    sa,sb=plane_slice(a,da),plane_slice(b,db)
    if not sa or not sb:return set()
    axis=max(range(3),key=lambda i:abs(direction[i]))
    sa=sorted(sa,key=lambda p:p[axis]);sb=sorted(sb,key=lambda p:p[axis])
    lo=max(sa[0][axis],sb[0][axis]);hi=min(sa[-1][axis],sb[-1][axis])
    if lo>hi:return set()
    if sa[0][axis]==sa[-1][axis]:return {sa[0]}
    return {add(sa[0],mul(sub(sa[-1],sa[0]),(n-sa[0][axis])/(sa[-1][axis]-sa[0][axis]))) for n in [lo,hi]}


def shell_self_intersections(triangles, *, maximum_faces=100):
    assert 1<=len(triangles)<=maximum_faces<=1000,'Explicit bounded component required'
    faces=[rational_face(f) for f in triangles]
    assert all(any(cross(sub(f[1],f[0]),sub(f[2],f[0]))) for f in faces),'Degenerate source triangle'
    failures=[];pairs=0;legal_contacts=0
    for i,j in combinations(range(len(faces)),2):
        a,b=faces[i],faces[j];pairs+=1
        points=intersection_points(a,b)
        if not points:continue
        shared=sorted(set(a)&set(b))
        legal=(len(shared)==1 and points==set(shared)) or (
            len(shared)==2 and all(segment_has(shared[0],shared[1],p) for p in points))
        if legal:legal_contacts+=1
        else:failures.append({'faces':[i,j],'sharedSourceVertices':len(shared),
                              'intersectionPoints':[[str(v) for v in p] for p in sorted(points)]})
    return {'sourceFaces':len(faces),'trianglePairsChecked':pairs,'legalSharedContacts':legal_contacts,
            'invalidIntersections':failures,'selfIntersectionFree':not failures,
            'coordinateArithmetic':'exact-rational-of-original-decoded-binary-coordinates',
            'geometryChanges':0,'toleranceWaivers':0,'placementAccepted':False}
