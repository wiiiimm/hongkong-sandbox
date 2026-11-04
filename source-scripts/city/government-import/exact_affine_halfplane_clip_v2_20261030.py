"""Existing exact clip plus a conservative representation repair within its old bounds.

Only invalid rounded clips of valid triangles are eligible. The repair must be
inside BOTH exact source triangle and exact half-plane, retain an original edge,
and pass the unchanged1e-12area/Hausdorff limits plus exact rational area loss.
No source plane, input coordinate, model geometry or tolerance is changed.
"""
from fractions import Fraction as F
import math
import numpy as np
import shapely
from exact_affine_halfplane_clip_v1_20261024 import convex_positive as original_positive
EPS=F(1e-12)
REPAIR_AUDIT=[]

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def signed_area(points):return sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(points,points[1:]+points[:1]))/2

def bounded_triangle_repair(region,difference):
 assert region.is_valid and not region.interiors
 points=[tuple(F(float(v))for v in p[:2])for p in region.exterior.coords[:-1]]
 assert len(points)==3 and len(set(points))==3
 coeff=tuple(F(float(v))for v in difference)
 value=lambda p:coeff[0]*p[0]+coeff[1]*p[1]+coeff[2]
 out=[]
 for a,b in zip(points,points[1:]+points[:1]):
  va,vb=value(a),value(b)
  if va>0:out.append(a)
  if (va>0)!=(vb>0):
   t=va/(va-vb);out.append(tuple(a[j]+t*(b[j]-a[j])for j in range(2)))
 assert len(out)==4 and sum(value(p)>0 for p in points)==2
 rounded=shapely.Polygon([tuple(map(float,p))for p in out]);assert not rounded.is_valid
 target=abs(signed_area(out));oldarea=F(float(rounded.area));lower=max(F(0),target-EPS,oldarea-EPS);upper=min(target,oldarea+EPS)
 assert 0<target and lower<=upper
 orientation=1 if signed_area(points)>0 else -1
 constraints=[]
 for a,b in zip(points,points[1:]+points[:1]):
  dx,dz=b[0]-a[0],b[1]-a[1]
  constraints.append((-orientation*dz,orientation*dx,orientation*(dz*a[0]-dx*a[1])))
 constraints.append(coeff)
 base=next((a,b)for a,b in zip(points,points[1:]+points[:1])if value(a)>0 and value(b)>0)
 a,b=base;dx,dz=b[0]-a[0],b[1]-a[1]
 area=(-orientation*dz/2,orientation*dx/2,orientation*(dz*a[0]-dx*a[1])/2)
 constraints.extend([(area[0],area[1],area[2]-lower),(-area[0],-area[1],upper-area[2])])
 midpoint=float((a[1]+b[1])/2);zs={midpoint}
 lo=hi=midpoint
 for _ in range(4):
  lo=math.nextafter(lo,-math.inf);hi=math.nextafter(hi,math.inf);zs.update([lo,hi])
 for z in sorted(zs,key=lambda z:abs(z-midpoint)):
  zq=F(z);left=right=None;feasible=True
  for ca,cb,cc in constraints:
   d=cb*zq+cc
   if ca==0:
    if d<0:feasible=False;break
   elif ca>0:left=max(left,-d/ca)if left is not None else -d/ca
   else:right=min(right,-d/ca)if right is not None else -d/ca
  if not feasible or left is None or right is None or left>right:continue
  candidates=[float((left+right)/2),float(left),float(right)]
  for x in candidates:
   if F(x)<left:x=math.nextafter(x,math.inf)
   if F(x)>right:x=math.nextafter(x,-math.inf)
   q=(F(x),zq)
   if not left<=q[0]<=right or any(ca*q[0]+cb*q[1]+cc<0 for ca,cb,cc in constraints):continue
   vertices=[a,b,q];exact=abs(signed_area(vertices));answer=shapely.Polygon([tuple(map(float,p))for p in vertices])
   if not answer.is_valid or answer.area<=0:continue
   # Both old output-repair gates remain; additionally prove exact loss and
   # containment, rather than trusting invalid signed-area cancellation.
   if abs(answer.area-rounded.area)>float(EPS)or abs(exact-target)>EPS:continue
   if shapely.hausdorff_distance(rounded,answer)>float(EPS):continue
   assert all(value(p)>=0 for p in vertices)
   assert all(orientation*cross(u,v,p)>=0 for p in vertices for u,v in zip(points,points[1:]+points[:1]))
   REPAIR_AUDIT.append(dict(regionWKB=region.wkb_hex,difference=list(map(float,difference)),exactTargetAreaM2=str(target),exactRepairedAreaM2=str(exact),exactAreaLossM2=str(target-exact),oldRoundedAreaM2=float(rounded.area),repairedAreaM2=float(answer.area),oldAreaChangeM2=abs(answer.area-rounded.area),boundaryHausdorffM=float(shapely.hausdorff_distance(rounded,answer)),areaToleranceM2=1e-12,boundaryToleranceM=1e-12,exactContainmentVerified=True,repairedVertices=[list(map(float,p))for p in vertices]))
   return answer
 raise AssertionError('No conservative triangle satisfies original clip-repair bounds')

def convex_positive(region,difference):
 assert region.geom_type=='Polygon'and not region.interiors
 try:return original_positive(region,difference)
 except AssertionError:return bounded_triangle_repair(region,difference)

def lower_region(region,difference):
 difference=np.asarray(difference,float);assert difference.shape==(3,)and np.isfinite(difference).all()
 parts=list(shapely.get_parts(region));polygons=[]
 while parts:
  p=parts.pop()
  if p.geom_type=='Polygon':polygons.append(p)
  elif p.geom_type in ('GeometryCollection','MultiPolygon'):parts.extend(shapely.get_parts(p))
  else:assert p.area==0
 assert abs(sum(p.area for p in polygons)-region.area)<1e-10
 return shapely.union_all([convex_positive(p,difference)for p in polygons])
