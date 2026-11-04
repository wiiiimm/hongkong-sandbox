"""Bounded saved-terrain packing context; diagnostics never decide acceptance.
Rational target coordinates are preserved. Closed finite packed triangles use
exact dyadic coordinates. Projection coverage is independent of height/layer.
"""
from fractions import Fraction as F
from exact_original_projection_coverage_v2_20261010 import subtract, signed_area, clip, cross

def points(t): return [tuple(F(v) for v in p) for p in t]
def projection(t): return [(p[0], p[2]) for p in points(t)]
def normal(t):
 a,b,c=points(t);u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
 return (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
def positive(t):
 p=projection(t);area=signed_area(p)
 return p if area>0 else list(reversed(p)) if area<0 else None

def interval(a,b,t):
 lo,hi=F(0),F(1)
 for p,q in zip(t,t[1:]+t[:1]):
  first,last=cross(p,q,a),cross(p,q,b);delta=last-first
  if delta==0:
   if first<0:return None
  elif delta>0:lo=max(lo,-first/delta)
  else:hi=min(hi,-first/delta)
 return (lo,hi) if lo<=hi else None

def edge_account(a,b,triangles):
 intervals=[v for t in triangles if (v:=interval(a,b,t)) is not None]
 reach=F(0);gaps=[]
 for lo,hi in sorted(intervals):
  if lo>reach:gaps.append([str(reach),str(lo)])
  reach=max(reach,hi)
 if reach<1:gaps.append([str(reach),'1'])
 return dict(exactClosedEdgeCovered=not gaps,exactParameterGaps=gaps,
             completeClosedIntervals=[[str(v)for v in pair]for pair in sorted(intervals)])

def coverage(target,records):
 """No tolerance, buffering, highest-layer inference or acceptance predicate."""
 original=projection(target);assert signed_area(original)!=0
 ids=[r['outputFacet']for r in records];assert len(ids)==len(set(ids))
 triangles=[t for r in records if (t:=positive(r['packedPoints']))is not None]
 remaining=[original]
 for t in triangles:
  remaining=[p for piece in remaining for p in subtract(piece,t)]
  if not remaining:break
 gaps=sum((abs(signed_area(p))for p in remaining),F(0))
 edges=[dict(edge=i,**edge_account(a,b,triangles))for i,(a,b)in enumerate(zip(original,original[1:]+original[:1]))]
 return dict(completeCandidateOutputIDs=ids,nonzeroPackedProjectedFacets=len(triangles),
  exactUncoveredProjectedAreaM2=str(gaps),remainingPositiveAreaPolygons=[[[str(v)for v in p]for p in polygon]for polygon in remaining],
  completeTargetEdgeAccounts=edges,wholeClosedProjectionCovered=gaps==0 and all(e['exactClosedEdgeCovered']for e in edges),
  heightOrLayerAgreementClaim=False,physicalAccepted=False)

def height(t,p):
 t=points(t);n=normal(t);assert n[1]!=0
 return t[0][1]-(n[0]*(p[0]-t[0][0])+n[2]*(p[1]-t[0][2]))/n[1]

def plane_context(target,record):
 a,b=positive(target),positive(record['packedPoints'])
 if a is None or b is None:return dict(outputFacet=record['outputFacet'],uniqueProjectedHeightPlane=False)
 part=a
 for p,q in zip(b,b[1:]+b[:1]):part=clip(part,p,q,True)
 if not part:return dict(outputFacet=record['outputFacet'],closedProjectedIntersection=False)
 delta=[height(record['packedPoints'],p)-height(target,p)for p in part]
 return dict(outputFacet=record['outputFacet'],closedProjectedIntersection=True,
  completeExactClosedIntersection=[[str(v)for v in p]for p in part],
  exactNeighbourMinusProposedHeightAtEveryIntersectionVertexM=[str(v)for v in delta],
  exactHeightDifferenceRangeM=[str(min(delta)),str(max(delta))],
  agreesOnWholeClosedIntersection=all(v==0 for v in delta),
  noSeamToleranceOrAcceptanceDecision=True)
