"""Conservative complete facet fixed-band union of finite closest-host-edge regions.
Every polygon vertex bounds that SAME affine closest-point map by convexity.
Whole exact interior/closed-boundary union required. No contact/role/root credit.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_surface_coordinate_band_20261010 import linear_clip,polygon_union_covers
from exact_original_projection_coverage_20261009 import signed_area
LIMIT=F(.1)
def point(p):return tuple(F(float(v))for v in p)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def verify(source,hosts,*,expected_input_binding=None):
 source=np.asarray(source,float);hosts=np.asarray(hosts,float)
 assert source.shape==(3,3)and hosts.ndim==3 and hosts.shape[1:]==(3,3)and np.isfinite(source).all()and np.isfinite(hosts).all()
 assert not exact_nonrendering(source),'Nonrendering source cannot receive proximity credit'
 binding=dict(completeSourceFacetSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeHostWorldSHA256=hashlib.sha256(hosts.tobytes()).hexdigest())
 if expected_input_binding is not None:assert binding==expected_input_binding,'Source/host input changed'
 a,b,c=map(point,source);su,sv=sub(b,a),sub(c,a);original=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))]
 lo=np.nextafter(source.min(0)-float(LIMIT),-np.inf);hi=np.nextafter(source.max(0)+float(LIMIT),np.inf);ids=np.flatnonzero(((hosts.max(1)>=lo)&(hosts.min(1)<=hi)).all(1));polys=[];records=[];degenerate=[]
 for i in ids:
  host=hosts[int(i)]
  if exact_nonrendering(host):degenerate.append(int(i));continue
  vertices=list(map(point,host))
  for edge,(p,q)in enumerate(zip(vertices,vertices[1:]+vertices[:1])):
   delta=sub(q,p);length2=dot(delta,delta);assert length2>0
   coeff=(dot(su,delta)/length2,dot(sv,delta)/length2,dot(sub(a,p),delta)/length2)
   for kind in ('interior','clamped-start','clamped-end'):
    poly=list(original)
    if kind=='interior':poly=linear_clip(linear_clip(poly,coeff),(-coeff[0],-coeff[1],1-coeff[2]))
    elif kind=='clamped-start':poly=linear_clip(poly,tuple(-v for v in coeff))
    else:poly=linear_clip(poly,(coeff[0],coeff[1],coeff[2]-1))
    if len(poly)<3 or signed_area(poly)==0:continue
    checks=[]
    for u,v in poly:
     src=tuple(a[k]+u*su[k]+v*sv[k]for k in range(3));parameter=coeff[0]*u+coeff[1]*v+coeff[2]
     t=parameter if kind=='interior'else F(0)if kind=='clamped-start'else F(1);assert 0<=t<=1
     foot=tuple(p[k]+t*delta[k]for k in range(3));error=sub(src,foot);checks.append(dict(exactSourceBarycentric=[str(u),str(v)],exactUnclampedParameter=str(parameter),exactClampedParameter=str(t),exactFiniteHostEdgeFoot=list(map(str,foot)),exactSquaredDistanceM2=str(dot(error,error))))
    if not all(F(r['exactSquaredDistanceM2'])<=LIMIT*LIMIT for r in checks):continue
    polys.append(poly);records.append(dict(originalHostFace=int(i),originalHostTriangleEdge=edge,closestFootBranch=kind,exactOriginalHostEdgeVertices=[list(map(str,pt))for pt in (p,q)],exactSourceBarycentricRegion=[[str(u),str(v)]for u,v in poly],allRegionVertexExactDistances=checks,completeRegionCertifiedByConvexity=True))
 covered,coverage=polygon_union_covers(original,polys)
 return dict(contract='exact-whole-original-facet-piecewise-finite-host-edge-fixed-band-diagnostic-v1',wholeFacetFiniteEdgeUnionAssociated=covered,**binding,completeHostFaces=len(hosts),conservativeCandidateHostFaces=len(ids),exactDegenerateHostFacesExcludedFromHostCredit=degenerate,allCompleteRegionCertificates=records,sourceBarycentricCoverage=coverage,strictBandM=.1,strictBandExact=str(LIMIT),sourceGeometryChanges=0,visualRoleAccepted=False,physicalContactCredit=False,structuralRootCredit=False,structuralBridgeCredit=False,installationApproved=False,qualification='Complete exact interior and closed-boundary union of individually certified finite closest-point regions. Each polygon uses one same affine original host edge/endpoint. Every polygon vertex stays within the unchanged squared band, conservatively bounding every interior point. No geometry or attachment inference.')
