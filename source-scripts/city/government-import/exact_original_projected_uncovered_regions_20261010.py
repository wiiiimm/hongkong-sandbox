"""Every exact positive-area, interval or point gap against the complete ground.

Uses the existing unchanged closed-facet subtraction semantics, returning full
rational geometric witnesses for a bounded new terrain proposal. No gap area,
length or coordinate tolerance. A missing interval retains both closed endpoints
as a conservative proposal envelope. Diagnostic only, no acceptance credit.
"""
from fractions import Fraction as F
import hashlib,numpy as np
from exact_original_projection_coverage_v2_20261010 import point,cross,signed_area,subtract
def diagnose(source_face,ground_triangles):
 source=np.asarray(source_face,float);ground=np.asarray(ground_triangles,float);assert source.shape==(3,3) and ground.ndim==3 and ground.shape[1:]==(3,3) and np.isfinite(source).all() and np.isfinite(ground).all()
 xz=source[:,[0,2]];lo=xz.min(0);hi=xz.max(0);gxz=ground[:,:,[0,2]];ids=np.flatnonzero(np.all(gxz.max(1)>=lo,1)&np.all(gxz.min(1)<=hi,1));original=[point(p) for p in xz];triangles=[]
 for j in ids:
  t=[point(p) for p in gxz[j]];area=signed_area(t)
  if area:triangles.append(t if area>0 else t[::-1])
 area=abs(signed_area(original));regions=[]
 if area:
  regions=[original]
  for t in triangles:
   regions=[p for piece in regions for p in subtract(piece,t)]
   if not regions:break
  kind='exact-positive-area-polygons';amount=sum(abs(signed_area(p)) for p in regions)
 else:
  a,b=max([(p,q) for p in original for q in original],key=lambda pq:sum((pq[0][k]-pq[1][k])**2 for k in range(2)))
  if a==b:
   inside=any(all(cross(p,q,a)>=0 for p,q in zip(t,t[1:]+t[:1])) for t in triangles);regions=[] if inside else [[a]];kind='exact-point-gap';amount=F(0)
  else:
   intervals=[]
   for t in triangles:
    lower,upper=F(0),F(1)
    for p,q in zip(t,t[1:]+t[:1]):
     start,end=cross(p,q,a),cross(p,q,b);delta=end-start
     if not delta:
      if start<0:lower,upper=F(1),F(0);break
     elif delta>0:lower=max(lower,-start/delta)
     else:upper=min(upper,-start/delta)
    if lower<=upper:intervals.append((lower,upper))
   reach=F(0);gaps=[]
   for lower,upper in sorted(intervals):
    if lower>reach:gaps.append((reach,lower))
    reach=max(reach,upper)
   if reach<1:gaps.append((reach,F(1)))
   regions=[[tuple(a[k]+t*(b[k]-a[k]) for k in range(2)) for t in pair] for pair in gaps];kind='exact-open-interval-gaps-closed-envelopes';amount=sum(end-start for start,end in gaps)
 return dict(contract='complete-original-finite-ground-exact-uncovered-region-diagnostic-v1',sourceFaceSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeGroundSHA256=hashlib.sha256(ground.tobytes()).hexdigest(),completeOriginalGroundTrianglesAccounted=len(ground),allClosedBoundingCandidateOriginalGroundFaces=list(map(int,ids)),method=kind,allExactUncoveredRegions=[[[str(v) for v in p] for p in poly] for poly in regions],exactUncoveredAreaOrParameterAmount=str(amount),exactProjectionCovered=not regions,toleranceOrBufferCredit=False,terrainProposalGeometryChanged=False,sourceGeometryChanges=0,installationApproved=False)
