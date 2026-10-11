"""Exact positive-dimensional interfaces on the actual finite upper ground envelope.

Partitions contact segments at every ground coverage and equality breakpoint.
Geometric evidence only: no structural or installation credit.
"""
from fractions import Fraction
import numpy as np,shapely
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure

def exact_upper_ground_interfaces(triangles,face_ids,drawn_ground):
 tri=np.asarray(triangles,float);ground=np.asarray(drawn_ground,float)
 assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
 assert ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(ground).all()
 assert list(face_ids)==sorted(set(face_ids)) and all(type(i) is int and 0<=i<len(tri) for i in face_ids)
 valid=np.flatnonzero(shapely.area(shapely.polygons(ground[:,:,[0,2]]))>0);g=ground[valid];gp=shapely.polygons(g[:,:,[0,2]]);tree=shapely.STRtree(gp);rational={};witnesses=[]
 def face(k):
  if k not in rational:rational[k]=rational_face(g[k])
  return rational[k]
 def upper_height(p):
  x,y,z=p;values=[]
  for k in tree.query(shapely.Point(float(x),float(z))):
   a,b,c=face(int(k));den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
   if not den:continue
   u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den;v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den;w=1-u-v
   if min(u,v,w)>=0:values.append(u*a[1]+v*b[1]+w*c[1])
  return max(values) if values else None
 def active_intervals(a,b):
  # Partition the entire candidate segment at every finite ground-facet
  # coverage endpoint and source/ground equality. Endpoint-only equality
  # cannot certify the upper envelope across an interior ground island.
  cuts={Fraction(0),Fraction(1)};lo=np.minimum([float(a[0]),float(a[2])],[float(b[0]),float(b[2])]);hi=np.maximum([float(a[0]),float(a[2])],[float(b[0]),float(b[2])]);candidates=tree.query(shapely.box(*lo,*hi))
  for k in candidates:
   p,q,r=face(int(k));den=(q[2]-r[2])*(p[0]-r[0])+(r[0]-q[0])*(p[2]-r[2])
   if not den:continue
   def bary(v):
    u=((q[2]-r[2])*(v[0]-r[0])+(r[0]-q[0])*(v[2]-r[2]))/den;w=((r[2]-p[2])*(v[0]-r[0])+(p[0]-r[0])*(v[2]-r[2]))/den;return (u,w,1-u-w)
   aa,bb=bary(a),bary(b);left,right=Fraction(0),Fraction(1)
   for x,y in zip(aa,bb):
    slope=y-x
    if not slope:
     if x<0:left,right=Fraction(1),Fraction(0);break
    elif slope>0:left=max(left,-x/slope)
    else:right=min(right,-x/slope)
   if left>right:continue
   cuts.update([left,right]);h0=sum(v*f[1] for v,f in zip(aa,[p,q,r]));h1=sum(v*f[1] for v,f in zip(bb,[p,q,r]));gap0=a[1]-h0;gap1=b[1]-h1
   if gap0!=gap1:
    crossing=-gap0/(gap1-gap0)
    if left<=crossing<=right:cuts.add(crossing)
  ordered=sorted(cuts);accepted=[]
  def at(s):return tuple(a[i]+s*(b[i]-a[i]) for i in range(3))
  for left,right in zip(ordered,ordered[1:]):
   if left==right:continue
   midpoint=at((left+right)/2)
   if upper_height(midpoint)==midpoint[1]:accepted.append(dict(exactParameterOpenInterval=[str(left),str(right)],exactSegmentEndpoints=[[str(v) for v in at(s)] for s in [left,right]],allGroundCoverageAndHeightBreakpoints=[str(s) for s in ordered],candidateGroundFacets=[int(valid[int(k)]) for k in candidates],upperEnvelopeCertifiedOnOpenInterval=True))
  return accepted
 for i in sorted(face_ids):
  t=tri[i];lo=t[:,[0,2]].min(axis=0);hi=t[:,[0,2]].max(axis=0)
  for k in tree.query(shapely.box(lo[0],lo[1],hi[0],hi[1])):
   k=int(k);points=intersection_points(rational_face(t),face(k))
   if not points or contact_measure(points)['dimension']<=0:continue
   ordered=sorted(points)
   intervals=active_intervals(ordered[0],ordered[-1])
   if intervals:witnesses.append(dict(sourceFace=i,originalGroundFace=int(valid[k]),exactActiveUpperGroundIntervals=intervals))
 return witnesses
