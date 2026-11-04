"""Clip actual finite host branches to prior exact uncovered intervals.

The old full-branch endpoint test can reject a useful subinterval. This new
DIAGNOSTIC certifies only closed subintervals whose TWO exact squared distances
stay inside the unchanged .1m band. Convexity covers the whole interval. No
irrational root approximation, coordinate epsilon, mount or support credit.
"""
from fractions import Fraction as F
import numpy as np
from exact_original_edge_finite_facade_distance_band_20261010 import verify as old_verify

def merge(intervals):
 out=[]
 for l,r in sorted(intervals):
  if out and l<=out[-1][1]:out[-1]=(out[-1][0],max(r,out[-1][1]))
  else:out.append((l,r))
 return out
def gaps(intervals):
 out=[];reach=F(0)
 for l,r in intervals:
  if l>reach:out.append((reach,l))
  reach=max(reach,r)
 if reach<1:out.append((reach,F(1)))
 return out
def verify(segment,surfaces):
 prior=old_verify(segment,surfaces);a,b=[tuple(F(float(v)) for v in p) for p in np.asarray(segment,float)];delta=tuple(b[j]-a[j] for j in range(3));tri=np.asarray(surfaces,float);limit=F(.1)**2;certified=[tuple(F(v) for v in pair) for pair in prior['exactFacetAndEdgeCertifiedMergedIntervals']];remaining=gaps(merge(certified));records=[]
 for r in prior['allFiniteOriginalFacetIntervals']:
  face=[[F(float(v)) for v in p] for p in tri[r['originalSurfaceFace']]];p,q,z=face;u=[q[j]-p[j] for j in range(3)];v=[z[j]-p[j] for j in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];n2=sum(v*v for v in n);assert n2;ea=sum(n[j]*(a[j]-p[j]) for j in range(3));ed=sum(n[j]*delta[j] for j in range(3));left,right=map(F,r['exactProjectedFootCoverageInterval'])
  for lo,hi in remaining:
   l,h=max(left,lo),min(right,hi)
   if l>h:continue
   ds=[(ea+ed*t)**2/n2 for t in [l,h]];passed=all(d<=limit for d in ds);records.append(dict(kind='original-finite-facet-orthogonal-foot',originalSurfaceFace=r['originalSurfaceFace'],exactClippedInterval=[str(l),str(h)],exactEndpointSquaredDistancesM2=list(map(str,ds)),entireClosedClippedIntervalWithinFixedBand=passed))
   if passed:certified.append((l,h))
 for r in prior['exactFiniteOriginalEdgeIntervals']:
  p,q=[tuple(F(v) for v in vertex) for vertex in r['exactOriginalEdgeVertices']];e=[q[j]-p[j] for j in range(3)];e2=sum(v*v for v in e);s0=sum((a[j]-p[j])*e[j] for j in range(3))/e2;sd=sum(delta[j]*e[j] for j in range(3))/e2;left,right=map(F,r['exactCoverageInterval'])
  for lo,hi in remaining:
   l,h=max(left,lo),min(right,hi)
   if l>h:continue
   ds=[]
   for t in [l,h]:
    s=max(F(0),min(F(1),s0+sd*t));ds.append(sum((a[j]+delta[j]*t-p[j]-s*e[j])**2 for j in range(3)))
   passed=all(d<=limit for d in ds);records.append(dict(kind='original-finite-triangle-edge-or-vertex',originalSurfaceFace=r['originalSurfaceFace'],originalTriangleEdge=r['originalTriangleEdge'],exactClippedInterval=[str(l),str(h)],exactEndpointSquaredDistancesM2=list(map(str,ds)),entireClosedClippedIntervalWithinFixedBand=passed))
   if passed:certified.append((l,h))
 merged=merge(certified);return{**prior,'contract':'exact-original-complete-edge-finite-facade-distance-band-clipped-existing-gaps-diagnostic-v2','priorWholeBranchResultVerbatim':prior,'priorWholeFiniteBranchBandPassed':prior['verifiedCompleteOriginalEdgeFiniteFacadeBand'],'verifiedCompleteOriginalEdgeFiniteFacadeBand':merged==[(F(0),F(1))],'exactFacetAndEdgeCertifiedMergedIntervals':[[str(l),str(h)] for l,h in merged],'allExactClippedUncoveredBranchRecords':records,'everyClippedIntervalRetainsActualFiniteFootOrClosestPoint':True,'strictBandM':.1,'visualRoleAccepted':False,'structuralRootCredit':False,'installationApproved':False}
