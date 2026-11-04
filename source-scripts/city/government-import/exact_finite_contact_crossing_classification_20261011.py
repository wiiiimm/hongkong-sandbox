"""Exact relative-interior finite contact diagnostics; no solid or support credit."""
from fractions import Fraction as Q

def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def triangle(v):return [tuple(Q(float(x)) for x in p)for p in v]
def normal(t):return cross(sub(t[1],t[0]),sub(t[2],t[0]))
def interior(t,p):
 n=normal(t)
 if n==(0,0,0)or dot(n,sub(p,t[0]))!=0:return False
 return all(dot(cross(sub(t[(i+1)%3],t[i]),sub(p,t[i])),n)>0 for i in range(3))
def classify(a,b,contact):
 a,b=triangle(a),triangle(b);na,nb=normal(a),normal(b)
 points=[tuple(Q(x)for x in p)for p in contact['exactPoints']]
 assert points and contact['dimension']in [0,1,2]
 centroid=tuple(sum(p[k]for p in points)/len(points)for k in range(3))
 real=na!=(0,0,0)and nb!=(0,0,0)
 coplanar=real and cross(na,nb)==(0,0,0)and dot(na,sub(b[0],a[0]))==0
 ia,ib=interior(a,centroid),interior(b,centroid)
 proper=real and not coplanar and contact['dimension']==1 and ia and ib
 role=('proper-noncoplanar-triangle-relative-interior-crossing'if proper else
       'coplanar-positive-area-overlap'if coplanar and contact['dimension']==2 else
       'coplanar-line-or-point-contact'if coplanar else
       'noncoplanar-boundary-contact'if real else 'degenerate-primitive-contact-no-structural-credit')
 return dict(classification=role,coplanarExact=coplanar,relativeInteriorA=ia,relativeInteriorB=ib,
  exactIntersectionCentroid=[str(x)for x in centroid],properTriangleInteriorCrossing=proper,
  volumetricCollisionProved=False,structuralSupportCredit=False)
