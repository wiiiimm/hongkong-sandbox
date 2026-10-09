"""Exact Fraction coverage by finite closed original ground facets, without buffer.

Version 2 skips only strictly disjoint exact rational polygon/facet bounds.
Diagnostics may call this for GEOS seam residues. No metre/area tolerance is used:
any genuine positive-area or interval gap remains uncovered, however small.
"""
from fractions import Fraction
import hashlib,numpy as np

def point(p):return tuple(Fraction.from_float(float(v)) for v in p)
def cross(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def signed_area(poly):return sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1]))/2 if len(poly)>2 else Fraction(0)
def clean(poly):
 out=[]
 for p in poly:
  if not out or out[-1]!=p:out.append(p)
 if len(out)>1 and out[0]==out[-1]:out.pop()
 return out
def clip(poly,a,b,positive):
 if not poly:return []
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  vp,vq=cross(a,b,p),cross(a,b,q);ip=vp>=0 if positive else vp<=0;iq=vq>=0 if positive else vq<=0
  if ip:out.append(p)
  if ip!=iq:
   t=vp/(vp-vq);out.append(tuple(p[k]+t*(q[k]-p[k]) for k in range(2)))
 return clean(out)
def subtract(poly,triangle):
 # Exact comparisons only. Strictly separated closed bounds cannot intersect;
 # touching bounds always retain the original complete clipping path.
 if any(max(p[k] for p in poly)<min(p[k] for p in triangle) or max(p[k] for p in triangle)<min(p[k] for p in poly) for k in range(2)):
  return [poly]
 if signed_area(triangle)<0:triangle=list(reversed(triangle))
 inside=poly;outside=[]
 for a,b in zip(triangle,triangle[1:]+triangle[:1]):
  part=clip(inside,a,b,False)
  if signed_area(part)!=0:outside.append(part)
  inside=clip(inside,a,b,True)
  if not inside:break
 return outside

def exact_coverage(source_face,ground_triangles):
 source=np.asarray(source_face,float);ground=np.asarray(ground_triangles,float)
 assert source.shape==(3,3) and ground.ndim==3 and ground.shape[1:]==(3,3) and np.isfinite(source).all() and np.isfinite(ground).all()
 xz=source[:,[0,2]];low=xz.min(axis=0);high=xz.max(axis=0);gxz=ground[:,:,[0,2]]
 candidates=np.flatnonzero(np.all(gxz.max(axis=1)>=low,axis=1)&np.all(gxz.min(axis=1)<=high,axis=1))
 original=[point(p) for p in xz];triangles=[]
 for j in candidates:
  t=[point(p) for p in gxz[j]];area=signed_area(t)
  if area!=0:triangles.append(t if area>0 else list(reversed(t)))
 area=abs(signed_area(original));gaps=[]
 if area:
  remaining=[original]
  for t in triangles:
   remaining=[p for piece in remaining for p in subtract(piece,t)]
   if not remaining:break
  uncovered=sum(abs(signed_area(p)) for p in remaining);covered=uncovered==0;kind='closed-facet-area-union';detail={'exactUncoveredAreaM2':str(uncovered),'exactSourceProjectedAreaM2':str(area),'remainingPositiveAreaPieces':len(remaining)}
 else:
  pairs=[(p,q) for p in original for q in original];a,b=max(pairs,key=lambda pq:sum((pq[0][k]-pq[1][k])**2 for k in range(2)))
  if a==b:
   covered=any(all(cross(p,q,a)>=0 for p,q in zip(t,t[1:]+t[:1])) for t in triangles);kind='closed-facet-point-union';detail={}
  else:
   intervals=[]
   for t in triangles:
    lower,upper=Fraction(0),Fraction(1)
    for p,q in zip(t,t[1:]+t[:1]):
     start,end=cross(p,q,a),cross(p,q,b);delta=end-start
     if delta==0:
      if start<0:lower,upper=Fraction(1),Fraction(0);break
     elif delta>0:lower=max(lower,-start/delta)
     else:upper=min(upper,-start/delta)
    if lower<=upper:intervals.append((lower,upper))
   reach=Fraction(0);covered=False
   for lower,upper in sorted(intervals):
    if lower>reach:gaps.append([str(reach),str(lower)]);break
    reach=max(reach,upper)
   covered=reach>=1 and not gaps;kind='closed-facet-interval-union';detail={'exactCoveredParameterThrough':str(reach),'firstExactParameterGaps':gaps,'intervals':len(intervals)}
 return {'exactProjectionCovered':covered,'method':kind,'completeOriginalGroundTrianglesAccounted':len(ground),'conservativeAABBCandidateGroundFacets':len(candidates),'nonzeroExactProjectedCandidateFacets':len(triangles),'sourceFaceSHA256':hashlib.sha256(source.tobytes()).hexdigest(),'completeGroundSHA256':hashlib.sha256(ground.tobytes()).hexdigest(),'noToleranceOrBufferCredit':True,**detail}
