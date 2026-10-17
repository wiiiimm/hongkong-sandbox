"""Exact closed triangle/segment/point XY intersections, including degeneracies."""
from fractions import Fraction as F
from exact_original_projection_coverage_20261009 import point,signed_area,clip,cross
def on(p,a,b):return cross(a,b,p)==0 and all(min(a[k],b[k])<=p[k]<=max(a[k],b[k]) for k in range(2))
def endpoints(poly):return max([(a,b) for a in poly for b in poly],key=lambda p:sum((p[0][k]-p[1][k])**2 for k in range(2)))
def segment(a,b,c,d):
 if a==b:return [a] if on(a,c,d) else []
 if c==d:return [c] if on(c,a,b) else []
 u=(b[0]-a[0],b[1]-a[1]);v=(d[0]-c[0],d[1]-c[1]);w=(c[0]-a[0],c[1]-a[1]);den=u[0]*v[1]-u[1]*v[0]
 if den:
  t=(w[0]*v[1]-w[1]*v[0])/den;s=(w[0]*u[1]-w[1]*u[0])/den
  return [(a[0]+t*u[0],a[1]+t*u[1])] if 0<=t<=1 and 0<=s<=1 else []
 if cross(a,b,c)!=0:return []
 return sorted({p for p in [a,b,c,d] if on(p,a,b) and on(p,c,d)})
def intersection(first,second):
 a=[point(p) for p in first];b=[point(p) for p in second];assert a and b
 if signed_area(b)!=0:
  if signed_area(b)<0:b.reverse()
  result=a
  for p,q in zip(b,b[1:]+b[:1]):result=clip(result,p,q,True)
  return result
 if signed_area(a)!=0:return intersection(second,first)
 return segment(*endpoints(a),*endpoints(b))
