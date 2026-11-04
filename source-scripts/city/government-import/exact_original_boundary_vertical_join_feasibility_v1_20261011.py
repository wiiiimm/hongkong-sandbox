"""DRAFT exact finite3D ruled join nomination, no original edits/mesh acceptance."""
from fractions import Fraction as F
import math
from exact_original_shell_intersections_20261009 import cross,sub

def point(p):
 assert len(p)==3
 for v in p:
  if isinstance(v,float):assert math.isfinite(v)
 return tuple(F(v)for v in p)
def at(a,b,t):return tuple(a[i]+t*(b[i]-a[i])for i in range(3))
def nominate(old_a,old_b,new_a,new_b):
 a,b,c,d=map(point,[old_a,old_b,new_a,new_b]);assert (a[0],a[2])==(c[0],c[2])and(b[0],b[2])==(d[0],d[2]);assert(a[0],a[2])!=(b[0],b[2]),'Point cannot become join';g0,g1=c[1]-a[1],d[1]-b[1];cuts=[F(0),F(1)]
 if g0*g1<0:cuts.insert(1,-g0/(g1-g0))
 rows=[];zero=[]
 for lo,hi in zip(cuts,cuts[1:]):
  u,v,w,z=at(a,b,lo),at(a,b,hi),at(c,d,hi),at(c,d,lo)
  for tri in [(u,v,w),(u,w,z)]:
   n=cross(sub(tri[1],tri[0]),sub(tri[2],tri[0]));(rows if any(n)else zero).append(tri)
 return dict(exactOriginalOldEndpoints=[a,b],exactOriginalNewEndpoints=[c,d],allGapSignSplitParameters=cuts,allPositiveGeneratedJoinFaces=rows,allExactDegenerateGeneratedNominees=zero,exactEndpointHeightGaps=[g0,g1],noSourcePositionChanges=True,generatedFacesAreNotOriginalGovernmentGeometry=True,sourceBoundaryIncidenceAndFullCandidateAcceptanceUnproved=True)
