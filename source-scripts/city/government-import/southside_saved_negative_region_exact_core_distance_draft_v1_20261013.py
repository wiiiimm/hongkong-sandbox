"""UNEXECUTED saved-region distance draft. No terrain/source geometry generated.
Closed negative-region closure is used for infimum, never an impossibility claim.
"""
from fractions import Fraction as F

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(points):
 p=sorted(set(tuple(F(v)for v in q)for q in points));assert p and all(len(q)==2 for q in p)
 if len(p)==1:return p
 lo=[];hi=[]
 for q in p:
  while len(lo)>1 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 for q in reversed(p):
  while len(hi)>1 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return lo[:-1]+hi[:-1]
def closed_negative_region(points,gaps):
 p=[tuple(F(v)for v in q)for q in points];g=list(map(F,gaps));assert p and len(p)==len(g)and all(len(q)==3 for q in p)
 out=[];out_g=[];threshold=F(-1,2)
 for i,(a,ga)in enumerate(zip(p,g)):
  b,gb=p[(i+1)%len(p)],g[(i+1)%len(p)];ia,ib=ga<=threshold,gb<=threshold
  if ia:out.append(a);out_g.append(ga)
  if ia!=ib:
   t=(threshold-ga)/(gb-ga);assert 0<=t<=1;out.append(tuple(a[k]+t*(b[k]-a[k])for k in range(3)));out_g.append(threshold)
 if not out:return dict(completeClosedNegativeSourcePoints=[],exactGapM=[],hasStrictNegativePoint=False)
 assert all(v<=threshold for v in out_g)
 return dict(completeClosedNegativeSourcePoints=out,exactGapM=out_g,hasStrictNegativePoint=any(v<threshold for v in out_g),closureForDistanceInfimumOnly=True,noAcceptanceOrImpossibilityInference=True)
def closed_bounds(poly):return tuple((min(q[k]for q in poly),max(q[k]for q in poly))for k in range(2))
def bounds_distance(a,b):return max([F(0)]+[max(a[k][0]-b[k][1],b[k][0]-a[k][1])for k in range(2)])
def convex_linf_distance(p,q):
 """Finite exact Minkowski-difference hull; every edge knot retained."""
 p=hull(p);q=hull(q);lookup={}
 for a in p:
  for b in q:lookup.setdefault((a[0]-b[0],a[1]-b[1]),(a,b))
 difference=hull(lookup)
 def witness(vertices,weights):
  pa=tuple(sum(w*lookup[v][0][k]for v,w in zip(vertices,weights))for k in range(2));qb=tuple(sum(w*lookup[v][1][k]for v,w in zip(vertices,weights))for k in range(2));d=max(abs(pa[k]-qb[k])for k in range(2));return dict(exactDistanceM=d,exactNegativeProjectionWitness=pa,exactCoreProjectionWitness=qb,exactDifferenceHullVertices=vertices,exactConvexWeights=weights)
 if len(difference)>2 and all(cross(a,b,(F(0),F(0)))>=0 for a,b in zip(difference,difference[1:]+difference[:1])):
  for i in range(1,len(difference)-1):
   a,b,c=difference[0],difference[i],difference[i+1];den=cross(a,b,c);assert den>0
   wa=cross((F(0),F(0)),b,c)/den;wb=cross(a,(F(0),F(0)),c)/den;wc=cross(a,b,(F(0),F(0)))/den
   if min(wa,wb,wc)>=0:
    result=witness([a,b,c],[wa,wb,wc]);assert result['exactDistanceM']==0;return result
  raise AssertionError('origin-in-difference-without-exact-barycentric-witness')
 if len(difference)==1:return witness(difference,[F(1)])
 best=None
 for a,b in zip(difference,difference[1:]+difference[:1]):
  dx,dz=b[0]-a[0],b[1]-a[1];knots={F(0),F(1)}
  for numerator,denominator in [(-a[0],dx),(-a[1],dz),(a[1]-a[0],dx-dz),(-a[1]-a[0],dx+dz)]:
   if denominator:
    t=numerator/denominator
    if 0<=t<=1:knots.add(t)
  for t in sorted(knots):
   candidate=witness([a,b],[1-t,t])
   if best is None or candidate['exactDistanceM']<best['exactDistanceM']:best=candidate
 assert best is not None;return best
def prepare_complete_core(records):
 groups={}
 for r in records:
  p=tuple(hull(r['completeXZPoints']));row=groups.setdefault(p,dict(completeCoreHull=p,completeOriginalCoreDomainLineage=[]));row['completeOriginalCoreDomainLineage'].append(r)
 for row in groups.values():row['exactClosedBounds']=closed_bounds(row['completeCoreHull'])
 return list(groups.values())
def distance_to_complete_core(negative_projection,core):
 p=hull(negative_projection);bounds=closed_bounds(p);scheduled=sorted([(bounds_distance(bounds,r['exactClosedBounds']),i)for i,r in enumerate(core)]);best=None;ties=[];excluded=[];examined=0;examined_proofs=[]
 for lower,i in scheduled:
  if best is not None and lower>best:excluded.append(dict(corePrimitive=i,exactClosedBoundsLowerDistanceM=lower));continue
  proof=convex_linf_distance(p,core[i]['completeCoreHull']);examined+=1;d=proof['exactDistanceM'];assert d>=lower;examined_proofs.append(dict(corePrimitive=i,exactClosedBoundsLowerDistanceM=lower,completeExactDistanceProof=proof))
  if best is None or d<best:best=d;ties=[]
  if d==best:ties.append(dict(corePrimitive=i,completeOriginalCoreDomainLineage=core[i]['completeOriginalCoreDomainLineage'],proof=proof))
 assert best is not None and examined+len(excluded)==len(core)
 return dict(exactMinimumDistanceM=best,completeNearestCoreTies=ties,completeStrictDistanceExclusions=excluded,completeExaminedCoreProofs=examined_proofs,completeCorePrimitiveCount=len(core),exactExaminedCorePrimitives=examined,closedEdgesPointsAndTiesRetained=True,noFiniteSupportOrRoleCredit=True,noImpossibilityInference=True)

def authentic_positive_faces(authentic_row,current_row):
 """Saved full-record gate, not inference from absence in a failure list."""
 records=authentic_row['completeOriginalFaceComparisons'];current=current_row['completeOriginalFaceComparisons'];assert len(records)==len(current)==current_row['completeOriginalFaceCount']
 assert authentic_row['completeWorldSHA256']==current_row['completeWholeWorldSHA256']
 assert [r['sourceFace']for r in records]==list(range(len(records)))
 positive=[];failed=[]
 for i,r in enumerate(records):
  assert r['sourceFace']==current[i]['sourceFace']and r['completeOriginalFacetSHA256']==current[i]['completeOriginalFacetSHA256']
  result=r['unfilteredAuthenticatedOriginalGroundComparison'];a,b=result['coarse'],result['paired'];assert type(a['existingOrdinaryClearanceBoundProved'])is bool
  if a['existingOrdinaryClearanceBoundProved']:assert b is None
  else:assert b is not None and type(b['existingOrdinaryClearanceBoundProved'])is bool
  actual=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved']));assert result['completeFiniteOrdinaryBoundProved']is actual
  (positive if actual else failed).append(i)
 assert failed==authentic_row['allAuthenticatedGroundFailuresRetained']
 return set(positive)
