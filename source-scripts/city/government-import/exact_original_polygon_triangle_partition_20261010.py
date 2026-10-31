"""Exact literal polygon/triangle partition certificate; no asset geometry changes.

All arithmetic uses Fractions of the supplied finite coordinate values. Each
positive triangle contributes winding +1. Equality of its complete oriented
boundary chain to a simple exterior (+1) and disjoint interior rings (-1)
therefore proves exactly one covering triangle in the domain and none outside.
Collinear boundary segmentation is atomized exactly, without a distance epsilon.
"""
from collections import Counter
from fractions import Fraction
import math


def point(v):
 assert len(v)==2
 assert all(math.isfinite(float(x)) for x in v), 'Nonfinite literal coordinate'
 return tuple(Fraction(x.item() if hasattr(x,'item') else x) for x in v)


def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def twice_area(r):return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(r,r[1:]+r[:1]))
def on_segment(a,b,p):return cross(a,b,p)==0 and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1])
def intersects(a,b,c,d):
 x,y,z,w=cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
 return (x*y<0 and z*w<0) or any((t==0 and on_segment(u,v,p)) for t,u,v,p in [(x,a,b,c),(y,a,b,d),(z,c,d,a),(w,c,d,b)])
def edges(r):return list(zip(r,r[1:]+r[:1]))
def inside(p,r):
 assert not any(on_segment(a,b,p) for a,b in edges(r)), 'Ring boundaries touch'
 winding=0
 for a,b in edges(r):
  if a[1]<=p[1]<b[1] and cross(a,b,p)>0:winding+=1
  elif b[1]<=p[1]<a[1] and cross(a,b,p)<0:winding-=1
 return winding!=0

def ring(values):
 r=[point(v) for v in values]
 if len(r)>1 and r[0]==r[-1]:r.pop()
 assert len(r)>=3 and len(set(r))==len(r) and twice_area(r)!=0, 'Degenerate/repeated polygon boundary'
 e=edges(r)
 for i,(a,b) in enumerate(e):
  for j,(c,d) in enumerate(e[i+1:],i+1):
   if j==i+1 or (i==0 and j==len(e)-1):
    # Adjacent edges may share just their endpoint, never retrace.
    shared=set((a,b))&set((c,d));assert len(shared)==1
    assert not any(on_segment(a,b,p) for p in (c,d) if p not in shared) and not any(on_segment(c,d,p) for p in (a,b) if p not in shared), 'Retraced polygon boundary'
   else:assert not intersects(a,b,c,d), 'Self-intersecting polygon boundary'
 return r

def chain(all_edges,vertices):
 result=Counter()
 for a,b in all_edges:
  assert a!=b
  axis=0 if a[0]!=b[0] else 1
  pieces=sorted((p for p in vertices if on_segment(a,b,p)),key=lambda p:(p[axis]-a[axis])/(b[axis]-a[axis]))
  assert pieces[0]==a and pieces[-1]==b
  for u,v in zip(pieces,pieces[1:]):
   key=(u,v) if u<v else (v,u);result[key]+=1 if u<v else -1
 return {k:v for k,v in result.items() if v}

def exact_partition(rings,triangles):
 assert rings and triangles, 'Missing polygon or triangulation'
 rs=[ring(r) for r in rings]
 for i,r in enumerate(rs):
  for s in rs[i+1:]:assert not any(intersects(a,b,c,d) for a,b in edges(r) for c,d in edges(s)), 'Polygon rings cross/touch'
 for i,h in enumerate(rs[1:],1):
  assert inside(h[0],rs[0]), 'Hole outside exterior'
  assert not any(inside(h[0],other) or inside(other[0],h) for j,other in enumerate(rs[1:],1) if j!=i), 'Nested/overlapping holes'
 target=[]
 for i,r in enumerate(rs):
  if (twice_area(r)>0)!=(i==0):r=list(reversed(r))
  target.extend(edges(r))
 tri=[];area=Fraction(0)
 for values in triangles:
  t=[point(v) for v in values];assert len(t)==3 and len(set(t))==3
  signed=cross(*t);assert signed!=0, 'Zero-area proof facet'
  if signed<0:t[1],t[2]=t[2],t[1];signed=-signed
  area+=signed/2;tri.extend(edges(t))
 vertices=set(p for e in target+tri for p in e)
 target_chain=chain(target,vertices);actual_chain=chain(tri,vertices)
 assert actual_chain==target_chain, 'Exact oriented facet boundary differs from complete polygon/hole boundary'
 target_area=abs(twice_area(rs[0]))/2-sum(abs(twice_area(h))/2 for h in rs[1:])
 assert target_area>0 and area==target_area, 'Exact facet area census differs from polygon domain'
 return {'exactPartitionPassed':True,'exactAreaFraction':str(area),'literalTriangleCount':len(tri)//3,'literalRingCount':len(rs),'exactBoundaryAtomicEdgeCount':len(target_chain),'qualification':'Positive literal rational triangle winding sum equals the complete simple exterior-minus-hole oriented boundary. Every domain interior has exactly one triangle; complete boundaries are retained. No asset edits or tolerance.'}
