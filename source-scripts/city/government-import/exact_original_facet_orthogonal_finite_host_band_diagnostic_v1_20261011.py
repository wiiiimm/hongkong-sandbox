"""Conservative exact whole-facet finite orthogonal association, diagnostic only.

Host barycentric foot regions and an inward rational signed-distance band are
clipped in exact source barycentric coordinates. Complete finite union coverage
includes all interior slabs and closed source edges; proximity is no role/root.
"""
from fractions import Fraction as F
from math import isqrt
import numpy as np
from exact_original_surface_coordinate_band_20261010 import linear_clip,polygon_union_covers

LIMIT=F(.1)
def point(p):return tuple(F(float(v)) for v in p)
def sub(a,b):return tuple(a[i]-b[i] for i in range(3))
def dot(a,b):return sum(a[i]*b[i] for i in range(3))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def inward_sqrt(value,bits=128):
 assert value>=0 and type(bits)is int and bits>0
 scale=1<<bits;r=F(isqrt((value.numerator*scale*scale)//value.denominator),scale)
 assert r*r<=value
 return r
def verify(source,hosts):
 source=np.asarray(source,float);hosts=np.asarray(hosts,float)
 assert source.shape==(3,3) and hosts.ndim==3 and hosts.shape[1:]==(3,3) and np.isfinite(source).all() and np.isfinite(hosts).all()
 a,b,c=map(point,source);u,v=sub(b,a),sub(c,a);normal=cross(u,v)
 if not dot(normal,normal):return dict(wholeFacetAssociated=False,sourcePrimitiveDimensionLessThan2=True,visualRoleAccepted=False,structuralRootCredit=False)
 original=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))];polygons=[];records=[];degenerate=[]
 low=np.nextafter(source.min(0)-float(LIMIT),-np.inf);high=np.nextafter(source.max(0)+float(LIMIT),np.inf)
 selected=np.flatnonzero(((hosts.max(1)>=low)&(hosts.min(1)<=high)).all(1))
 for j in selected:
  p,q,r=map(point,hosts[int(j)]);hu,hv=sub(q,p),sub(r,p);hn=cross(hu,hv);n2=dot(hn,hn)
  if not n2:degenerate.append(int(j));continue
  aa,ab,bb=dot(hu,hu),dot(hu,hv),dot(hv,hv);det=aa*bb-ab*ab;assert det==n2 and det>0
  offset=sub(a,p)
  beta=tuple((dot(x,hu)*bb-dot(x,hv)*ab)/det for x in (u,v,offset))
  gamma=tuple((dot(x,hv)*aa-dot(x,hu)*ab)/det for x in (u,v,offset))
  poly=list(original)
  for coeff in (beta,gamma,tuple((F(1) if k==2 else F(0))-beta[k]-gamma[k] for k in range(3))):poly=linear_clip(poly,coeff)
  signed=tuple(dot(hn,x) for x in (u,v,offset));radius=inward_sqrt(n2*LIMIT*LIMIT)
  poly=linear_clip(poly,(-signed[0],-signed[1],radius-signed[2]));poly=linear_clip(poly,(signed[0],signed[1],radius+signed[2]))
  if len(poly)<3:continue
  from exact_original_projection_coverage_20261009 import signed_area
  if signed_area(poly)==0:continue
  squared=[(signed[0]*x+signed[1]*y+signed[2])**2/n2 for x,y in poly]
  assert max(squared)<=LIMIT*LIMIT
  polygons.append(poly);records.append(dict(originalHostFace=int(j),exactSourceBarycentricFootRegion=[[str(x),str(y)] for x,y in poly],exactInwardSignedBandRadius=str(radius),exactHostNormalSquared=str(n2),exactMaximumSquaredDistanceM2=str(max(squared)),completeFiniteOrthogonalFootOnOriginalHost=True))
 passed,coverage=polygon_union_covers(original,polygons)
 return dict(contract='exact-whole-original-facet-orthogonal-finite-host-fixed-band-diagnostic-v1',wholeFacetAssociated=passed,completeHostFaces=len(hosts),conservativeCandidateHostFaces=len(selected),exactDegenerateHostFaces=degenerate,completeExactFootRegionRecords=records,sourceBarycentricCoverage=coverage,strictBandM=.1,strictBandExact=str(LIMIT),inwardRationalBoundOnly=True,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,installationApproved=False,qualification='Exact finite orthogonal projection to unchanged host triangles and inward distance-band clipping; complete exact interior and closed-edge union coverage. Inward sqrt may reject marginal positives, never increases the fixed band. No authored function, attachment, grounded host or physical credit.')
