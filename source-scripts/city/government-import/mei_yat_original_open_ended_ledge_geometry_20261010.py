"""Eight original faces and a complete back U mount; no physical/root credit."""
import hashlib
from collections import defaultdict
import numpy as np
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as band
from exact_shell_context_accelerated_20261009 import shell_self_intersections
def verify(triangles,faces,rooted_host_faces,*,expected_world_sha256):
 t=np.asarray(triangles,float);assert t.ndim==3 and t.shape[1:]==(3,3) and np.isfinite(t).all();assert hashlib.sha256(t.tobytes()).hexdigest()==expected_world_sha256
 ids=list(faces);hosts=list(rooted_host_faces);assert len(ids)==8 and len(set(ids))==8 and hosts and len(set(hosts))==len(hosts) and not set(ids)&set(hosts);assert all(type(i)is int and 0<=i<len(t) for i in ids+hosts)
 vertices=set(map(tuple,t[ids].reshape(-1,3)));levels=sorted({v[1] for v in vertices});plans={(v[0],v[2]) for v in vertices};assert len(vertices)==8 and len(levels)==2 and len(plans)==4 and levels[0]<levels[1];assert {(x,y,z) for x,z in plans for y in levels}==vertices
 edges=defaultdict(list);adj=defaultdict(set);horizontal=[];vertical=[]
 for i in ids:
  vs=list(map(tuple,t[i]));n=np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]);assert np.linalg.norm(n)>0
  if len({v[1] for v in vs})==1:horizontal.append(i);assert n[1]!=0 and n[0]==n[2]==0
  else:vertical.append(i);assert n[1]==0
  for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
 assert len(horizontal)==len(vertical)==4 and all(sum(t[i,0,1]==y for i in horizontal)==2 for y in levels)
 boundary=[]
 for edge,inc in edges.items():
  assert len(inc)<=2
  if len(inc)==1:boundary.append(inc[0])
  else:
   assert inc[0][1:]==inc[1][1:][::-1]
   a,b=inc[0][0],inc[1][0];adj[a].add(b);adj[b].add(a)
 reached={ids[0]};todo=[ids[0]]
 while todo:
  for j in adj[todo.pop()]-reached:reached.add(j);todo.append(j)
 assert reached==set(ids) and len(boundary)==6
 directed={a:b for i,a,b in boundary};assert len(directed)==6 and set(directed)=={b for i,a,b in boundary};a=min(directed);start=a;seen=[]
 while a not in seen:seen.append(a);a=directed[a]
 assert a==start and len(seen)==6
 proofs=[dict(sourceFace=i,originalEdge=[list(a),list(b)],finiteHostBand=band(np.array([a,b]),t[hosts])) for i,a,b in boundary];mounted=[p for p in proofs if p['finiteHostBand']['verifiedCompleteOriginalEdgeFiniteFacadeBand']];assert len(mounted)==3
 h=[p for p in mounted if p['originalEdge'][0][1]==p['originalEdge'][1][1]];v=[p for p in mounted if p not in h];assert len(h)==2 and len(v)==1 and {p['originalEdge'][0][1] for p in h}==set(levels)
 hp=[{(q[0],q[2]) for q in p['originalEdge']} for p in h];assert len(hp[0])==2 and hp[0]==hp[1];a,b=v[0]['originalEdge'];assert (a[0],a[2])==(b[0],b[2]) and (a[0],a[2]) in hp[0] and {a[1],b[1]}==set(levels)
 selfcheck=shell_self_intersections(t[ids]);assert selfcheck['selfIntersectionFree']
 return dict(contract='named-original-eight-face-open-ended-facade-ledge-geometry-v1',verifiedOriginalLedgeGeometry=True,completeOriginalFaces=ids,completeRootedHostFaces=hosts,originalOpeningEdges=proofs,completeMountedBackUEdges=mounted,actualOriginalFreeEndEdges=[p for p in proofs if p not in mounted],actualPlanCorners=[list(p) for p in sorted(plans)],actualOriginalHeightLevels=levels,originalSelfIntersection=selfcheck,syntheticBackOrEndCapCreated=False,closedSolidCertified=False,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,installationApproved=False,mandatoryIndependentOriginalAndRenderedWholeFacetClearance=True,mandatoryIndependentRootedHostAndProviderBinding=True)
