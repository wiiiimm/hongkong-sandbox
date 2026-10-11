"""Exact fixed-band finite edge certificates on unproved facet regions.

The prior complete orthogonal-foot union remains verbatim. Its exact unproved
parameter polygons are intersected with genuine finite-edge closest-point
branches. Squared distances at every clipped polygon vertex bound the whole
convex polygon. Complete closed source coverage is still required, without
buffer, subdivision epsilon, role, attachment or structural credit.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as prior_verify
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_surface_coordinate_band_20261010 import linear_clip,polygon_union_covers
from exact_original_projection_coverage_20261009 import subtract,signed_area
LIMIT=F(.1)
def point(p):return tuple(F(float(x))for x in p)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def verify(source,hosts,*,expected_input_binding=None):
 source=np.asarray(source,float);hosts=np.asarray(hosts,float)
 assert source.shape==(3,3)and hosts.ndim==3 and hosts.shape[1:]==(3,3)and np.isfinite(source).all()and np.isfinite(hosts).all()
 assert not exact_nonrendering(source),'Nonrendering facets provide no surface or mount'
 binding=dict(completeSourceFacetSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeHostWorldSHA256=hashlib.sha256(hosts.tobytes()).hexdigest())
 if expected_input_binding is not None:assert binding==expected_input_binding,'Actual complete source/host input changed'
 prior=prior_verify(source,hosts);original=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))]
 polygons=[[tuple(map(F,p))for p in r['exactSourceBarycentricFootRegion']]for r in prior['completeExactFootRegionRecords']]
 # An independent exact squared-distance certificate also retains equality
 # at the fixed band boundary, which the prior inward sqrt may conservatively
 # reject. Each complete finite foot polygon is accepted only when ALL of its
 # exact vertices pass; convexity then bounds every point of that polygon.
 a,b,c=map(point,source);u,v=sub(b,a),sub(c,a)
 lo=np.nextafter(source.min(0)-float(LIMIT),-np.inf);hi=np.nextafter(source.max(0)+float(LIMIT),np.inf)
 candidate=np.flatnonzero(((hosts.max(1)>=lo)&(hosts.min(1)<=hi)).all(1));foot_records=[]
 for i in candidate:
  host=hosts[int(i)]
  if exact_nonrendering(host):continue
  p,q,r=map(point,host);hu,hv=sub(q,p),sub(r,p);n=cross(hu,hv);n2=dot(n,n);assert n2>0
  aa,ab,bb=dot(hu,hu),dot(hu,hv),dot(hv,hv);det=aa*bb-ab*ab;assert det==n2
  offset=sub(a,p)
  beta=tuple((dot(x,hu)*bb-dot(x,hv)*ab)/det for x in (u,v,offset))
  gamma=tuple((dot(x,hv)*aa-dot(x,hu)*ab)/det for x in (u,v,offset))
  poly=list(original)
  for coeff in (beta,gamma,tuple((F(1)if k==2 else F(0))-beta[k]-gamma[k]for k in range(3))):poly=linear_clip(poly,coeff)
  if len(poly)<3 or signed_area(poly)==0:continue
  signed=tuple(dot(n,x)for x in (u,v,offset));squared=[(signed[0]*x+signed[1]*y+signed[2])**2/n2 for x,y in poly]
  if not all(value<=LIMIT*LIMIT for value in squared):continue
  polygons.append(poly);foot_records.append(dict(actualHostFace=int(i),completeFiniteFootSourceParameterPolygon=[[str(x),str(y)]for x,y in poly],allExactPolygonVertexSquaredDistancesM2=list(map(str,squared)),completeConvexSquaredPlaneDistanceCertificate=True))
 residual=[original]
 for polygon in polygons:
  for j in range(1,len(polygon)-1):
   fan=[polygon[0],polygon[j],polygon[j+1]]
   if signed_area(fan):residual=[piece for p in residual for piece in subtract(p,fan)]
 a,b,c=map(point,source);u,v=sub(b,a),sub(c,a)
 lo=np.nextafter(source.min(0)-float(LIMIT),-np.inf);hi=np.nextafter(source.max(0)+float(LIMIT),np.inf)
 candidate=np.flatnonzero(((hosts.max(1)>=lo)&(hosts.min(1)<=hi)).all(1));records=[];degenerate=[]
 for i in candidate:
  host=hosts[int(i)]
  if exact_nonrendering(host):degenerate.append(int(i));continue
  vertices=list(map(point,host))
  for edge,(p,q)in enumerate(zip(vertices,vertices[1:]+vertices[:1])):
   delta=sub(q,p);length2=dot(delta,delta);assert length2>0
   coeff=(dot(u,delta)/length2,dot(v,delta)/length2,dot(sub(a,p),delta)/length2)
   for ri,region in enumerate(residual):
    for kind in ('interior','clamped-start','clamped-end'):
     poly=list(region)
     if kind=='interior':poly=linear_clip(linear_clip(poly,coeff),(-coeff[0],-coeff[1],1-coeff[2]))
     elif kind=='clamped-start':poly=linear_clip(poly,tuple(-x for x in coeff))
     else:poly=linear_clip(poly,(coeff[0],coeff[1],coeff[2]-1))
     if len(poly)<3 or signed_area(poly)==0:continue
     checks=[]
     for x,y in poly:
      src=tuple(a[k]+x*u[k]+y*v[k]for k in range(3));parameter=coeff[0]*x+coeff[1]*y+coeff[2]
      t=parameter if kind=='interior'else F(0)if kind=='clamped-start'else F(1);assert 0<=t<=1
      foot=tuple(p[k]+t*delta[k]for k in range(3));error=sub(src,foot)
      checks.append(dict(exactSourceParameter=[str(x),str(y)],exactUnclampedFootParameter=str(parameter),exactClampedFiniteFootParameter=str(t),actualFiniteEdgeFoot=list(map(str,foot)),exactSquaredDistanceM2=str(dot(error,error))))
     if not all(F(r['exactSquaredDistanceM2'])<=LIMIT*LIMIT for r in checks):continue
     polygons.append(poly);records.append(dict(actualHostFace=int(i),actualHostTriangleEdge=edge,actualFiniteEdgeVertices=[list(map(str,p)),list(map(str,q))],priorUnprovedParameterPolygon=ri,closestFootBranch=kind,completeCertifiedSourceParameterPolygon=[[str(x),str(y)]for x,y in poly],allExactPolygonVertexDistances=checks,completeConvexSquaredDistanceCertificate=True))
 covered,coverage=polygon_union_covers(original,polygons)
 return dict(contract='exact-whole-original-facet-residual-finite-host-edge-fixed-band-diagnostic-v2',**binding,priorCompleteOrthogonalProofVerbatim=prior,allExactWholeFiniteFootSquaredBandPieces=foot_records,completePriorUnprovedParameterPolygons=[[[str(x),str(y)]for x,y in p]for p in residual],allExactCertifiedResidualFiniteEdgePieces=records,completeMixedClosedParameterCoverage=coverage,wholeFacetWithinExistingFiniteHostBand=covered,completeActualHostFaces=len(hosts),strictBandM=.1,strictBandExact=str(LIMIT),exactDegenerateHostFacesExcluded=degenerate,conservativeCandidateHostFaces=len(candidate),sourceGeometryChanges=0,visualRoleAccepted=False,physicalAttachmentCredit=False,structuralRootOrBridgeCredit=False,installationApproved=False)
