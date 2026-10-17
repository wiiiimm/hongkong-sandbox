"""Reciprocal complete finite-edge association of two original closed loops.

A topological degree-two loop is not a simple hole or an authored mount. Exact
fixed-band proximity certifies perimeters only, never either loop's interior.
"""
from fractions import Fraction as F
import hashlib,json,numpy as np
LIMIT=F(.1)
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def loop(raw):
 a=np.asarray(raw,float);assert a.ndim==3 and a.shape[1:]==(2,3)and len(a)>=3 and np.isfinite(a).all();edges=[tuple(map(tuple,e))for e in a];assert all(x!=y for x,y in edges);keys=[tuple(sorted(e))for e in edges];assert len(set(keys))==len(keys);adj={}
 for x,y in edges:adj.setdefault(x,set()).add(y);adj.setdefault(y,set()).add(x)
 assert all(len(n)==2 for n in adj.values());seen={min(adj)};todo=list(seen)
 while todo:
  for n in adj[todo.pop()]:
   if n not in seen:seen.add(n);todo.append(n)
 assert len(seen)==len(adj),'One complete connected degree-two loop required'
 return edges

def verify(source_edges,host_edges,*,expected_binding=None):
 source=loop(source_edges);host=loop(host_edges);binding=dict(completeSourceLoopSHA256=canonical(source),completeHostLoopSHA256=canonical(host))
 if expected_binding is not None:assert binding==expected_binding,'Complete original boundary input changed'
 def point(v):return tuple(F(float(x))for x in v)
 def squared(p,a,b):
  d=tuple(y-x for x,y in zip(a,b));length=sum(x*x for x in d);assert length>0;t=max(F(0),min(F(1),sum((p[i]-a[i])*d[i]for i in range(3))/length));return sum((p[i]-a[i]-t*d[i])**2 for i in range(3))
 def direction(first,second):
  result=[]
  for i,e in enumerate(first):
   p,q=map(point,e);witness=[]
   for j,f in enumerate(second):
    a,b=map(point,f);values=[squared(v,a,b)for v in [p,q]]
    if max(values)<=LIMIT*LIMIT:witness.append(dict(otherCompleteOriginalEdge=j,exactEndpointSquaredDistancesM2=list(map(str,values)),wholeEdgeConvexFiniteSegmentBound=True))
   result.append(dict(completeOriginalEdge=i,allSameFiniteEdgeCertificates=witness,wholeEdgeAssociated=bool(witness)))
  return result
 forward=direction(source,host);back=direction(host,source)
 return dict(contract='exact-reciprocal-original-closed-boundary-loop-fixed-band-diagnostic-v1',binding=binding,completeSourceEdges=len(source),completeHostEdges=len(host),sourceToHost=forward,hostToSource=back,completeReciprocalBoundaryBandProved=all(r['wholeEdgeAssociated']for r in forward+back),strictBandM=.1,strictBandExact=str(LIMIT),closedTopologicalLoopOnly=True,simpleGeometricHoleCertified=False,wholeInteriorProximityCertified=False,authoredMountCertified=False,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,geometryChanges=0)
