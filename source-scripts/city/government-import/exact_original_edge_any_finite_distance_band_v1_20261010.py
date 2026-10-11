"""Exact complete segment-to-finite-original-facade distance DIAGNOSIS.

Adds original triangle edges/vertices to the unchanged orthogonal-foot route.
No geometry is welded. Each finite-edge closest-point branch is affine over an
exact rational interval; squared distance is convex, so both endpoints certify
the WHOLE interval under the fixed .1m band. Incomplete unions fail. This earns
no visual role, root, structural bridge, clearance or installation credit.
"""
from fractions import Fraction as F
import numpy as np
from exact_original_perpendicular_any_facet_band_v1_20261010 import verify as facet_foot

def verify(segment,surfaces):
 result=facet_foot(segment,surfaces)
 line=np.asarray(segment,float);tri=np.asarray(surfaces,float)
 a,b=[tuple(F(float(x)) for x in p) for p in line];delta=tuple(b[j]-a[j] for j in range(3));limit=F(.1)**2
 certified=[tuple(F(x) for x in interval) for interval in result['exactCertifiedMergedIntervals']];records=[]
 lo=np.nextafter(line.min(axis=0)-.1,-np.inf);hi=np.nextafter(line.max(axis=0)+.1,np.inf)
 candidates=np.flatnonzero(np.all(tri.max(axis=1)>=lo,axis=1)&np.all(tri.min(axis=1)<=hi,axis=1))
 for i in candidates:
  vertices=[tuple(F(float(x)) for x in p) for p in tri[i]];u=tuple(vertices[1][j]-vertices[0][j] for j in range(3));v=tuple(vertices[2][j]-vertices[0][j] for j in range(3));n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);n2=sum(x*x for x in n)
  if not n2:continue
  for edge_index,(p,q) in enumerate(zip(vertices,vertices[1:]+vertices[:1])):
   e=tuple(q[j]-p[j] for j in range(3));e2=sum(x*x for x in e);assert e2
   s0=sum((a[j]-p[j])*e[j] for j in range(3))/e2;sd=sum(delta[j]*e[j] for j in range(3))/e2
   knots={F(0),F(1)}
   if sd:
    for boundary in [F(0),F(1)]:
     t=(boundary-s0)/sd
     if 0<t<1:knots.add(t)
   ordered=sorted(knots)
   for left,right in zip(ordered,ordered[1:]):
    sm=s0+sd*(left+right)/2
    branch='edge-interior' if 0<=sm<=1 else ('first-vertex' if sm<0 else 'second-vertex')
    distances=[]
    for t in [left,right]:
     s=max(F(0),min(F(1),s0+sd*t));distances.append(sum((a[j]+delta[j]*t-p[j]-s*e[j])**2 for j in range(3)))
    passed=all(d<=limit for d in distances)
    records.append(dict(originalSurfaceFace=int(i),originalTriangleEdge=edge_index,exactOriginalEdgeVertices=[[str(x) for x in p],[str(x) for x in q]],closestFiniteEdgeBranch=branch,exactCoverageInterval=[str(left),str(right)],exactEndpointSquaredDistancesM2=[str(x) for x in distances],entireIntervalWithinFixedBand=passed))
    if passed:certified.append((left,right))
 merged=[]
 for left,right in sorted(certified):
  if merged and left<=merged[-1][1]:merged[-1]=(merged[-1][0],max(right,merged[-1][1]))
  else:merged.append((left,right))
 result.update(contract='exact-original-complete-edge-all-orientation-finite-distance-band-diagnostic-v1',verifiedCompleteOriginalEdgeFiniteFacadeBand=merged==[(F(0),F(1))],exactFiniteOriginalEdgeIntervals=records,exactFacetAndEdgeCertifiedMergedIntervals=[[str(l),str(r)] for l,r in merged],originalPerpendicularFootRoutePassed=result['verifiedCompleteOriginalEdgePerpendicularBand'],finiteTriangleEdgesAreOriginalGeometry=True,closestPointDistanceNotSupportContact=True)
 return result
