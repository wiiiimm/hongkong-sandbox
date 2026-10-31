"""Exact positive-dimensional 3D segment interval inventory; zero tolerance."""
from fractions import Fraction as F

def point(p):return tuple(v if isinstance(v,F)else F(float(v))for v in p)
def overlap(a,b,c,d):
 a,b,c,d=map(point,[a,b,c,d]);assert all(len(p)==3 for p in [a,b,c,d]);u=tuple(b[i]-a[i]for i in range(3));assert any(u),'Collapsed source segment'
 if c==d:return None
 for p in [c,d]:
  v=tuple(p[i]-a[i]for i in range(3))
  if any(u[i]*v[j]-u[j]*v[i]!=0 for i,j in [(0,1),(0,2),(1,2)]):return None
 k=next(i for i in range(3)if u[i]);t=[(p[k]-a[k])/u[k]for p in [c,d]];lo,hi=max(F(0),min(t)),min(F(1),max(t));return (lo,hi)if lo<hi else None

def covered(parts):
 cursor=F(0)
 for lo,hi in sorted(parts):
  assert F(0)<=lo<hi<=F(1),'Invalid complete interval'
  if lo>cursor:return False
  cursor=max(cursor,hi)
 return cursor==1
