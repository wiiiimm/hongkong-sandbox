"""Complete exact original body edge incidence; no hole or role certificate.

Every supplied facet ID is retained. Exact zero-area facets are separately
inventoried and provide no boundary or structural support credit. Point-shared
branches, duplicate incidences and open groups are recorded rather than joined
into an invented opening loop.
"""
from collections import defaultdict
import hashlib,json
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering

def canonical(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def census(world,source_faces,*,expected_binding=None):
 w=np.asarray(world,float);assert w.ndim==3 and w.shape[1:]==(3,3)and np.isfinite(w).all()
 ids=list(map(int,source_faces));assert ids==sorted(set(ids))and ids and min(ids)>=0 and max(ids)<len(w)
 binding=dict(completeWorldSHA256=hashlib.sha256(w.tobytes()).hexdigest(),completeOriginalFaceIdsSHA256=canonical(ids))
 if expected_binding is not None:assert binding==expected_binding,'Complete body/source world changed'
 edgefaces=defaultdict(list);zeros=[]
 for face in ids:
  if exact_nonrendering(w[face]):zeros.append(face);continue
  vertices=list(map(tuple,w[face]))
  for corner,(a,b)in enumerate(zip(vertices,vertices[1:]+vertices[:1])):
   assert a!=b
   edgefaces[tuple(sorted((a,b)))].append(dict(globalOriginalFace=face,originalCorner=corner,directedActualEdge=[a,b]))
 boundary={e:rows for e,rows in edgefaces.items()if len(rows)==1};adj=defaultdict(set)
 for a,b in boundary:adj[a].add(b);adj[b].add(a)
 remaining=set(adj);groups=[]
 while remaining:
  start=min(remaining);seen={start};todo=[start]
  while todo:
   for v in adj[todo.pop()]:
    if v not in seen:seen.add(v);todo.append(v)
  remaining-=seen;edges=sorted(e for e in boundary if e[0]in seen)
  groups.append(dict(completeActualEdges=edges,completeActualEdgeIncidences=[boundary[e]for e in edges],completeVertexDegrees=[dict(actualVertex=v,degree=len(adj[v]))for v in sorted(seen)],closedConnectedDegreeTwoLoop=len(edges)>=3 and all(len(adj[v])==2 for v in seen),simpleHoleOrCavityCertified=False))
 return dict(binding=binding,completeOriginalFaceIds=ids,exactZeroAreaOriginalFaces=zeros,allNonzeroEdgeIncidences=[dict(completeActualEdge=e,completeOriginalIncidences=edgefaces[e])for e in sorted(edgefaces)],nonmanifoldOriginalEdges=[dict(completeActualEdge=e,completeOriginalIncidences=edgefaces[e])for e in sorted(edgefaces)if len(edgefaces[e])>2],completeIncidenceOneBoundaryGroups=groups,completeIncidenceOneBoundaryEdges=len(boundary),zeroAreaFacesReceiveNoSupportCredit=True,originalHoleCertified=False,visualRoleAccepted=False,structuralRootOrBridgeCredit=False)
