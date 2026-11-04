"""Exact complete source surface association; never an attachment/support decision."""
from fractions import Fraction
import numpy as np,shapely
from exact_original_projection_coverage_20261009 import point,cross,signed_area,clip,clean
from exact_original_slab_projection_coverage_20261010 import intersection_x,interval
def linear_clip(poly,coeff):
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a=coeff[0]*p[0]+coeff[1]*p[1]+coeff[2];b=coeff[0]*q[0]+coeff[1]*q[1]+coeff[2]
  if a>=0:out.append(p)
  if (a>=0)!=(b>=0):
   t=a/(a-b);out.append(tuple(p[k]+t*(q[k]-p[k]) for k in range(2)))
 return clean(out)
def plane(face,axes,drop):
 p=[tuple(Fraction.from_float(float(v)) for v in q) for q in face];a,b,c=p;u,v=tuple(b[k]-a[k] for k in axes),tuple(c[k]-a[k] for k in axes);det=u[0]*v[1]-u[1]*v[0]
 if not det:return None
 h,j=b[drop]-a[drop],c[drop]-a[drop];x=(h*v[1]-j*u[1])/det;y=(u[0]*j-v[0]*h)/det
 return x,y,a[drop]-x*a[axes[0]]-y*a[axes[1]]
def edge_covered(a,b,polys):
 segments=[]
 for poly in polys:
  low,high=Fraction(0),Fraction(1)
  for p,q in zip(poly,poly[1:]+poly[:1]):
   start,end=cross(p,q,a),cross(p,q,b);delta=end-start
   if not delta:
    if start<0:low,high=Fraction(1),Fraction(0);break
   elif delta>0:low=max(low,-start/delta)
   else:high=min(high,-start/delta)
  if low<=high:segments.append((low,high))
 reach=Fraction(0)
 for low,high in sorted(segments):
  if low>reach:return False
  reach=max(reach,high)
 return reach>=1
def polygon_union_covers(original,polys):
 edges=sorted({tuple(sorted((a,b))) for poly in polys for a,b in zip(poly,poly[1:]+poly[:1]) if a!=b});events={p[0] for poly in polys+[original] for p in poly}
 if edges:
  boxes=[]
  for a,b in edges:
   coords=np.asarray([list(map(float,a)),list(map(float,b))]);lo=np.nextafter(coords.min(0),-np.inf);hi=np.nextafter(coords.max(0),np.inf);boxes.append(shapely.box(*lo,*hi))
  tree=shapely.STRtree(boxes)
  for i,box in enumerate(boxes):
   for j in tree.query(box):
    if j>i:
     x=intersection_x(*edges[i],*edges[int(j)])
     if x is not None:events.add(x)
 count=0
 for a,b in zip(sorted(events),sorted(events)[1:]):
  if a==b:continue
  x=(a+b)/2;target=interval(original,x)
  if target is None:continue
  count+=1;reach=target[0]
  for lo,hi in sorted(v for poly in polys if (v:=interval(poly,x)) is not None):
   if lo>reach:return False,{'slabsChecked':count,'uncoveredInteriorWitness':[str(x),str((reach+min(lo,target[1]))/2)]}
   reach=max(reach,hi)
   if reach>=target[1]:break
  if reach<target[1]:return False,{'slabsChecked':count,'uncoveredInteriorWitness':[str(x),str((reach+target[1])/2)]}
 edges_ok=[edge_covered(a,b,polys) for a,b in zip(original,original[1:]+original[:1])]
 return all(edges_ok),{'slabsChecked':count,'closedSourceEdgesCovered':edges_ok,'exactCrossingEvents':len(events)}
def surface_band(face,counterparts,limit):
 face=np.asarray(face,float);counterparts=np.asarray(counterparts,float);assert face.shape==(3,3) and counterparts.ndim==3 and counterparts.shape[1:]==(3,3) and np.isfinite(face).all() and np.isfinite(counterparts).all();limit=Fraction(str(limit));assert limit>=0
 normal=np.cross(face[1]-face[0],face[2]-face[0]);drop=int(np.argmax(np.abs(normal)));axes=[i for i in range(3) if i!=drop];source_plane=plane(face,axes,drop)
 if source_plane is None:return {'wholeFaceAssociated':False,'reason':'original-degenerate-role-unresolved','supportAccepted':False}
 original=[point(p) for p in face[:,axes]]
 if signed_area(original)<0:original.reverse()
 lo,hi=face[:,axes].min(0),face[:,axes].max(0);aabb=(counterparts[:,:,axes].max(1)>=lo).all(1)&(counterparts[:,:,axes].min(1)<=hi).all(1);polys=[];ids=[]
 for j in np.flatnonzero(aabb):
  other=counterparts[j];coeff=plane(other,axes,drop)
  if coeff is None:continue
  poly=[point(p) for p in other[:,axes]]
  if signed_area(poly)<0:poly.reverse()
  for a,b in zip(original,original[1:]+original[:1]):poly=clip(poly,a,b,True)
  gap=tuple(source_plane[i]-coeff[i] for i in range(3));poly=linear_clip(poly,(-gap[0],-gap[1],limit-gap[2]));poly=linear_clip(poly,(gap[0],gap[1],limit+gap[2]))
  if signed_area(poly)!=0:polys.append(poly);ids.append(int(j))
 covered,details=polygon_union_covers(original,polys)
 return {'wholeFaceAssociated':covered,'coordinateAxis':drop,'coordinateSeparationLimitM':str(limit),'completeCounterpartFaces':len(counterparts),'candidateCounterpartFaces':int(aabb.sum()),'associatedCounterpartFaceIds':ids,'exactFinitePolygons':[[list(map(str,p)) for p in poly] for poly in polys],**details,'sourceGeometryChanges':0,'supportAccepted':False,'qualification':'Exact finite source/counterpart plane interpolation and coordinate-band clips followed by complete Fraction slab arrangement plus closed-edge interval coverage. Every associated point lies on an actual unchanged counterpart triangle within the diagnostic coordinate separation. This is not zero-distance contact, role, load-bearing support or physical acceptance.'}
