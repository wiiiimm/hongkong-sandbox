"""Exact convex finite upper-envelope cells; no packing or acceptance.
Zero XZ-area source faces stay inventoried without height/root credit.
Closed-boundary upper values are separate: genuine jumps cannot be smoothed.
"""
from fractions import Fraction as F
import math
from actual_native_parent_transition_v3_20261010 import clip,cross
from exact_original_polygon_triangle_partition_20261010 import exact_partition

def rational(values):
 assert len(values)==3 and all(math.isfinite(float(v))for v in values),'Nonfinite source/clip point'
 return tuple(v if isinstance(v,F)else F(float(v))for v in values)
def area(poly):return sum(a[0]*b[2]-a[2]*b[0]for a,b in zip(poly,poly[1:]+poly[:1]))/2 if len(poly)>=3 else F(0)
def positive(poly):
 if area(poly)<0:poly=list(reversed(poly))
 return poly if area(poly)>0 else []
def plane(t):
 a,b,c=t;d=cross(a,b,c);assert d
 px=((b[1]-a[1])*(c[2]-a[2])-(c[1]-a[1])*(b[2]-a[2]))/d
 pz=((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]))/d
 return px,pz,a[1]-px*a[0]-pz*a[2]
def height(p,h):return h[0]*p[0]+h[1]*p[2]+h[2]
def box(poly):return min(p[0]for p in poly),min(p[2]for p in poly),max(p[0]for p in poly),max(p[2]for p in poly)
def meets(a,b):return a[0]<=b[2]and b[0]<=a[2]and a[1]<=b[3]and b[1]<=a[3]
def inside(p,t):return all(cross(a,b,p)>=0 for a,b in zip(t,t[1:]+t[:1]))

def partition(poly,triangles,*,max_cells=100000,max_operations=1000000):
 assert isinstance(max_cells,int)and max_cells>0 and isinstance(max_operations,int)and max_operations>0
 poly=positive([rational(p)for p in poly]);assert poly,'Positive convex clip domain required'
 assert all(cross(a,b,p)>=0 for a,b in zip(poly,poly[1:]+poly[:1])for p in poly),'Convex input required'
 full=[tuple(rational(p)for p in t)for t in triangles];assert all(len(t)==3 for t in full)
 zero=[i for i,t in enumerate(full)if cross(*t)==0];pb=box(poly);eligible=[]
 for i,t in enumerate(full):
  if i in zero or not meets(pb,box(t)):continue
  tt=list(t)if cross(*t)>0 else list(reversed(t));eligible.append((i,tt,plane(tt)))
 cells=[];operations=0;discarded=0
 def cut(p,fn):
  nonlocal operations,discarded
  operations+=1;assert operations<=max_operations,'Exact clipping operation cap exceeded'
  result=clip(p,fn)
  if result and area(result)==0:discarded+=1
  return positive(result)
 for i,t,h in eligible:
  start=poly
  for a,b in zip(t,t[1:]+t[:1]):start=cut(start,lambda p,a=a,b=b:cross(a,b,p))
  groups=[start]if start else []
  for j,other,hh in eligible:
   if j==i:continue
   next_groups=[]
   for group in groups:
    remaining=group;outside=[]
    for a,b in zip(other,other[1:]+other[:1]):
     q=cut(remaining,lambda p,a=a,b=b:-cross(a,b,p))
     if q:outside.append(q)
     remaining=cut(remaining,lambda p,a=a,b=b:cross(a,b,p))
     if not remaining:break
    next_groups.extend(outside)
    if remaining:
     if h==hh:
      if i<j:next_groups.append(remaining)
     else:
      q=cut(remaining,lambda p:height(p,h)-height(p,hh))
      if q:next_groups.append(q)
    assert len(cells)+len(next_groups)<=max_cells,'Exact upper-cell resource cap exceeded'
   groups=next_groups
   if not groups:break
  for group in groups:
   assert len(cells)<max_cells,'Exact upper-cell resource cap exceeded'
   middle=tuple(sum(p[k]for p in group)/len(group)for k in range(3));assert inside(middle,t)
   competitors=[height(middle,hh)for j,tt,hh in eligible if inside(middle,tt)]
   assert height(middle,h)==max(competitors)
   cells.append(dict(faceIndex=i,polygon=group,plane=h))
 triangles2=[]
 for cell in cells:
  p=cell['polygon']
  for k in range(1,len(p)-1):
   if cross(p[0],p[k],p[k+1])!=0:triangles2.append([(q[0],q[2])for q in [p[0],p[k],p[k+1]]])
 certificate=exact_partition([[(p[0],p[2])for p in poly]],triangles2)
 boundary=[]
 for p in sorted(set(p for c in cells for p in c['polygon'])):
  candidates=[(i,height(p,h))for i,t,h in eligible if inside(p,t)];assert candidates
  boundary.append(dict(point=p,closedUpperY=max(v for _,v in candidates),finiteHostFaceIndices=[i for i,_ in candidates]))
 return cells,dict(completeSourceFaceCount=len(full),completeZeroProjectedAreaFaceIds=zero,exactEligibleFiniteHeightFaceIds=[i for i,_,_ in eligible],completeCellCount=len(cells),clippingOperations=operations,discardedExactZeroAreaClipRecords=discarded,exactInteriorPartition=certificate,completeBoundaryVertices=boundary,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Exact convex interior envelope partition; finite CLOSED boundary values retained independently including jumps. No packing, seam, root or acceptance credit.')
