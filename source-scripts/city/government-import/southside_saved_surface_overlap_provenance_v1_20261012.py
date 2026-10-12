"""Draft only: exact finite projected overlap classification of saved facets."""
from fractions import Fraction as F

def tri(value):
 assert len(value)==3 and all(len(p)==3 for p in value)
 return tuple(tuple(F(v)for v in p)for p in value)

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def area(poly):
 return abs(sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(poly,poly[1:]+poly[:1])))/2 if len(poly)>2 else F(0)

def intersection(a,b):
 a=[(p[0],p[2])for p in tri(a)];b=[(p[0],p[2])for p in tri(b)]
 orientation=cross(*b)
 if not orientation or not cross(*a):return []
 sign=1 if orientation>0 else -1;out=a
 for u,v in zip(b,b[1:]+b[:1]):
  old=out;out=[]
  if not old:break
  previous=old[-1];dp=sign*cross(u,v,previous)
  for current in old:
   dc=sign*cross(u,v,current)
   if (dp>=0)!=(dc>=0):
    k=dp/(dp-dc);out.append(tuple(previous[i]+k*(current[i]-previous[i])for i in range(2)))
   if dc>=0:out.append(current)
   previous=current;dp=dc
  compact=[]
  for p in out:
   if not compact or p!=compact[-1]:compact.append(p)
  if len(compact)>1 and compact[0]==compact[-1]:compact.pop()
  out=compact
 return out

def height(t,p):
 a,b,c=tri(t);u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
 n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 assert n[1]!=0
 return a[1]-(n[0]*(p[0]-a[0])+n[2]*(p[1]-a[2]))/n[1]

def classify(a,b):
 polygon=intersection(a,b);common=area(polygon)
 if not common:return dict(positiveProjectedArea=False,exactProjectedArea=str(common),classification='no-positive-projected-area')
 gaps=[height(a,p)-height(b,p)for p in polygon]
 kind='coincident-plane'if all(g==0 for g in gaps)else'crossing-height-planes'if min(gaps)<0<max(gaps)else'first-at-or-above-second'if min(gaps)>=0 else'second-at-or-above-first'
 return dict(positiveProjectedArea=True,exactProjectedArea=str(common),classification=kind,exactOverlapXZ=[[str(v)for v in p]for p in polygon],exactFirstMinusSecondHeightAtVertices=[str(v)for v in gaps])
