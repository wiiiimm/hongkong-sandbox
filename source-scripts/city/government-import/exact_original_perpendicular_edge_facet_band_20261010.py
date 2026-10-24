"""Conservative exact perpendicular finite-facet edge-band DIAGNOSIS.

Entire original edge, unchanged .1m Euclidean plane distance, exact original
orthogonal feet INSIDE finite facets. Every original facet is enumerated. A
facet interval contributes only if BOTH exact interval endpoints satisfy the
band; convexity then proves the entire interval. This may reject partially
useful intervals. It grants no mount, root, role, clearance or install credit.
"""
from fractions import Fraction as F
import numpy as np
def verify(segment,surfaces):
 line=np.asarray(segment,float);tri=np.asarray(surfaces,float);assert line.shape==(2,3) and tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(line).all() and np.isfinite(tri).all() and not np.array_equal(*line)
 a,b=[tuple(F(float(v)) for v in p) for p in line];limit=F(.1)**2;certified=[];records=[];degenerate=[]
 # Outward rounding is pruning only; exact distance still enforces .1m.
 lo=np.nextafter(line.min(axis=0)-.1,-np.inf);hi=np.nextafter(line.max(axis=0)+.1,np.inf)
 candidate=np.flatnonzero(np.all(tri.max(axis=1)>=lo,axis=1)&np.all(tri.min(axis=1)<=hi,axis=1))
 for i in candidate:
  p,q,r=[tuple(F(float(v)) for v in vtx) for vtx in tri[i]];u=tuple(q[j]-p[j] for j in range(3));v=tuple(r[j]-p[j] for j in range(3));n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);n2=sum(x*x for x in n)
  if not n2:degenerate.append(int(i));continue
  if n[1]*n[1]>n2/F(16):continue # Original vertical host, exact normal ratio.
  ev=lambda x:sum(n[j]*(x[j]-p[j]) for j in range(3));ea,eb=ev(a),ev(b)
  feet=[tuple(x[j]-e*n[j]/n2 for j in range(3)) for x,e in [(a,ea),(b,eb)]];drop=max(range(3),key=lambda j:abs(n[j]));dims=[j for j in range(3) if j!=drop];j,k=dims
  den=(q[k]-r[k])*(p[j]-r[j])+(r[j]-q[j])*(p[k]-r[k]);assert den
  def bary(x):
   aa=((q[k]-r[k])*(x[j]-r[j])+(r[j]-q[j])*(x[k]-r[k]))/den;bb=((r[k]-p[k])*(x[j]-r[j])+(p[j]-r[j])*(x[k]-r[k]))/den;return aa,bb,1-aa-bb
  ba,bb=map(bary,feet);left,right=F(0),F(1)
  for x,y in zip(ba,bb):
   slope=y-x
   if not slope:
    if x<0:left,right=F(1),F(0);break
   elif slope>0:left=max(left,-x/slope)
   else:right=min(right,-x/slope)
  if left>right:continue
  distances=[(ea+s*(eb-ea))**2/n2 for s in [left,right]];passed=all(x<=limit for x in distances)
  row=dict(originalSurfaceFace=int(i),exactProjectedFootCoverageInterval=[str(left),str(right)],exactEndpointPerpendicularSquaredDistancesM2=[str(x) for x in distances],entireIntervalWithinFixedBand=passed);records.append(row)
  if passed:certified.append((left,right))
 merged=[]
 for l,r in sorted(certified):
  if merged and l<=merged[-1][1]:merged[-1]=(merged[-1][0],max(r,merged[-1][1]))
  else:merged.append((l,r))
 passed=merged==[(F(0),F(1))]
 return dict(contract='exact-original-complete-edge-perpendicular-finite-host-band-diagnostic-v1',verifiedCompleteOriginalEdgePerpendicularBand=passed,strictBandM=.1,completeOriginalFacetCount=len(tri),broadphaseFacetCount=len(candidate),allFiniteOriginalFacetIntervals=records,exactCertifiedMergedIntervals=[[str(l),str(r)] for l,r in merged],exactZeroAreaOriginalHostFaces=degenerate,perpendicularPlaneDistanceNotCoordinateHeight=True,conservativeIntervalEndpointRequirement=True,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,installationApproved=False)
