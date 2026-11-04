"""Exact rational squared distance for binary-float points and finite triangles."""
from fractions import Fraction as F

def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def squared_distance(point,triangle):
 p=tuple(F(float(x))for x in point);a,b,c=[tuple(F(float(x))for x in v)for v in triangle];n=cross(sub(b,a),sub(c,a));nn=dot(n,n);ds=[]
 if nn:
  delta=dot(sub(p,a),n);q=tuple(p[i]-delta*n[i]/nn for i in range(3))
  if all(dot(cross(sub(y,x),sub(q,x)),n)>=0 for x,y in [(a,b),(b,c),(c,a)]):ds.append(delta*delta/nn)
 for x,y in [(a,b),(b,c),(c,a)]:
  e=sub(y,x);den=dot(e,e);t=max(F(0),min(F(1),dot(sub(p,x),e)/den))if den else F(0);q=tuple(x[i]+t*e[i]for i in range(3));v=sub(p,q);ds.append(dot(v,v))
 return min(ds)
if __name__=='__main__':
 assert squared_distance([.25,2,.25],[[0,0,0],[1,0,0],[0,0,1]])==4
 assert squared_distance([2,0,0],[[0,0,0],[1,0,0],[0,0,1]])==1
 assert squared_distance([.5,0,0],[[0,0,0],[1,0,0],[1,0,0]])==0
 assert squared_distance([.5,0,2**-31],[[0,0,0],[1,0,0],[1,0,2**-30]])==0
 print('Exact rational interior, exterior, degenerate and thin-triangle checks pass')
