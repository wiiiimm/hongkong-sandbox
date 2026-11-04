"""Conditional source-authored opening-panel geometry; zero support credit.

A complete original triangle may span an authentic triangular boundary loop
without interior proximity to solid host facets. This kernel certifies only
unchanged source geometry, exact parallel planes and fixed-band reciprocal
perimeters. Independently grounded actual hosts and full current physical
checks remain mandatory before any visual-role acceptance.
"""
from collections import defaultdict
from fractions import Fraction as F
import hashlib,json
import numpy as np
from exact_original_shell_intersections_20261009 import cross,sub
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
from exact_original_closed_boundary_loop_band_diagnostic_v1_20261011 import verify as boundary_verify

LIMIT=F(.1)
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def vertices(v):return [tuple(F(float(x))for x in p)for p in v]
def edge(a,b):return tuple(sorted([tuple(a),tuple(b)]))

def source_inventory(world):
 w=np.asarray(world,float);assert w.ndim==3 and w.shape[1:]==(3,3)and np.isfinite(w).all()
 inc=defaultdict(list)
 for i,t in enumerate(w):
  if exact_nonrendering(t):continue
  for a,b in zip(t,np.roll(t,-1,axis=0)):inc[edge(a,b)].append(i)
 c=census(w,list(range(len(w))))
 return dict(completeWorldSHA256=hashlib.sha256(w.tobytes()).hexdigest(),
  completeOriginalFaces=len(w),edgeIncidences=inc,census=c)

def verify(world,*,source_face,host_loop_edges,expected_source_binding):
 w=np.asarray(world,float);inventory=source_inventory(w)
 assert type(source_face)is int and 0<=source_face<len(w)
 binding=dict(completeOriginalWorldSHA256=inventory['completeWorldSHA256'],
  completeOriginalFaces=inventory['completeOriginalFaces'],sourceFace=source_face,
  completeOriginalSourceFacetSHA256=hashlib.sha256(w[source_face].tobytes()).hexdigest(),
  completeClaimedHostLoopSHA256=canonical(host_loop_edges))
 assert binding==expected_source_binding,'Complete source/facet/loop binding changed'
 panel=w[source_face];assert not exact_nonrendering(panel),'Renderable noncollinear panel required'
 keys=[edge(*e)for e in host_loop_edges];assert len(keys)==3 and len(set(keys))==3
 loop_vertices=set(v for e in keys for v in e);assert len(loop_vertices)==3
 adj=defaultdict(set)
 for a,b in keys:adj[a].add(b);adj[b].add(a)
 assert all(len(v)==2 for v in adj.values())
 boundary={e:r for e,r in inventory['edgeIncidences'].items()if len(r)==1}
 assert all(e in boundary for e in keys),'Every complete host edge must have exactly one original incidence'
 hostfaces=sorted(set(boundary[e][0]for e in keys));assert source_face not in hostfaces
 # No partial sub-loop selected from a larger or branched boundary component.
 all_adj=defaultdict(set)
 for a,b in boundary:all_adj[a].add(b);all_adj[b].add(a)
 assert all(all_adj[v]==adj[v]for v in loop_vertices),'Complete original boundary loop required'
 members=[i for i,body in enumerate(inventory['census']['sharedEdgeConnectedComponents'])if any(f in body for f in hostfaces)]
 assert len(members)==1,'All loop incidences must belong to one complete genuine shared-edge host body'
 hostbody=inventory['census']['sharedEdgeConnectedComponents'][members[0]]
 assert source_face not in hostbody,'Panel must be separately authored, not an existing host triangle'
 pv=vertices(panel);hv=vertices(sorted(loop_vertices));n=cross(sub(pv[1],pv[0]),sub(pv[2],pv[0]));m=cross(sub(hv[1],hv[0]),sub(hv[2],hv[0]))
 assert any(n)and any(m)and not any(cross(n,m)),'Exact original parallel noncollinear planes required'
 squared_offsets=[sum(n[i]*(p[i]-pv[0][i])for i in range(3))**2/sum(x*x for x in n)for p in hv]
 assert max(squared_offsets)<=LIMIT*LIMIT,'Unchanged fixed plane band exceeded'
 panel_edges=list(zip(panel.tolist(),np.roll(panel,-1,axis=0).tolist()))
 band=boundary_verify(panel_edges,host_loop_edges)
 assert band['completeReciprocalBoundaryBandProved'],'Whole reciprocal finite perimeter required'
 return dict(contract='conditional-original-triangular-opening-panel-source-role-v1',
  binding=binding,sourceFace=source_face,hostOriginalBody=members[0],
  completeHostOriginalBodyFaces=hostbody,completeOriginalHostBoundaryIncidences=hostfaces,
  exactParallelPlanes=True,exactPlaneOffsetsSquaredM2=list(map(str,squared_offsets)),
  completeReciprocalPerimeterProof=band,sourceRoleProposal='original nonstructural opening panel',
  wholeFacetInteriorProximityCertified=False,functionOrWindowClaim=False,
  independentlyGroundedActualHostRequired=True,completeCurrentPhysicalChecksRequired=True,
  visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,
  nativeReacceptance=False,geometryChanges=0)
