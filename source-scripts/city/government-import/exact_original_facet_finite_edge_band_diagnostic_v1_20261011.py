"""Whole original facet within fixed .1m of one genuine finite host edge.

Exact squared vertex distances suffice by convexity of distance to a convex
finite segment. Different host edges cannot be combined into a certificate.
Diagnostic proximity only: no visual role, contact, root or geometry changes.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
LIMIT=F(.1)
def point(p):return tuple(F(float(v))for v in p)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def verify(source,hosts,*,expected_input_binding=None):
 source=np.asarray(source,float);hosts=np.asarray(hosts,float)
 assert source.shape==(3,3)and hosts.ndim==3 and hosts.shape[1:]==(3,3)and np.isfinite(source).all()and np.isfinite(hosts).all()
 assert not exact_nonrendering(source),'Exact nonrendering source cannot receive a surface association'
 binding=dict(completeSourceFacetSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeHostWorldSHA256=hashlib.sha256(hosts.tobytes()).hexdigest())
 if expected_input_binding is not None:assert binding==expected_input_binding,'Pinned source/host input changed'
 src=list(map(point,source));lo=np.nextafter(source.min(0)-float(LIMIT),-np.inf);hi=np.nextafter(source.max(0)+float(LIMIT),np.inf);ids=np.flatnonzero(((hosts.max(1)>=lo)&(hosts.min(1)<=hi)).all(1));witnesses=[];degenerate=[]
 for i in ids:
  host=hosts[int(i)]
  if exact_nonrendering(host):degenerate.append(int(i));continue
  vertices=list(map(point,host))
  for edge,(a,b)in enumerate(zip(vertices,vertices[1:]+vertices[:1])):
   delta=sub(b,a);length2=dot(delta,delta);assert length2>0;records=[]
   for p in src:
    raw=dot(sub(p,a),delta)/length2;t=max(F(0),min(F(1),raw));foot=tuple(a[k]+t*delta[k]for k in range(3));error=sub(p,foot);records.append(dict(exactUnclampedFootParameter=str(raw),exactClampedFiniteFootParameter=str(t),exactOriginalHostEdgeFoot=[str(v)for v in foot],exactSquaredDistanceM2=str(dot(error,error))))
   if all(F(r['exactSquaredDistanceM2'])<=LIMIT*LIMIT for r in records):witnesses.append(dict(originalHostFace=int(i),originalHostTriangleEdge=edge,exactOriginalHostEdgeVertices=[[str(v)for v in p]for p in [a,b]],allThreeOriginalSourceVertexFiniteEdgeDistances=records,exactMaximumSquaredDistanceM2=str(max(F(r['exactSquaredDistanceM2'])for r in records)),completeFacetConvexFiniteSegmentDistanceBound=True))
 return dict(contract='exact-whole-original-facet-one-finite-host-edge-fixed-band-diagnostic-v1',wholeFacetFiniteEdgeAssociated=bool(witnesses),completeSourceFacetSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeHostWorldSHA256=hashlib.sha256(hosts.tobytes()).hexdigest(),completeHostFaces=len(hosts),conservativeCandidateHostFaces=len(ids),exactDegenerateHostFacesExcludedFromHostCredit=degenerate,allCompleteFacetFiniteEdgeCertificates=witnesses,strictBandM=.1,strictBandExact=str(LIMIT),noDifferentEdgeCombinationCredit=True,sourceGeometryChanges=0,visualRoleAccepted=False,physicalContactCredit=False,structuralRootCredit=False,structuralBridgeCredit=False,installationApproved=False,qualification='All3 source vertices have exact finite closest points on the SAME genuine original host edge under fixed squared band. Distance squared to that convex segment is convex, so every source barycentric interior point stays in band. An exact source-host intersection, authored function or grounded host is not inferred.')
