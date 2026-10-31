"""DRAFT exact planar terrain union boundary/T-junction inventory and one genuine edge ring.
Geometry-only topology; no triangulation, terrain generation or actor/root approval.
"""
from fractions import Fraction as F
from collections import defaultdict
import numpy as np
from exact_source_planar_domain_recovery_seams_v1_20261011 import projected,oriented,source_height,overlap_interval,interval_covered
from exact_original_projection_coverage_v2_20261010 import clip,signed_area,cross
def arrays(faces):
 a=np.asarray(faces,dtype='<f8');assert a.ndim==3 and a.shape[1:]==(3,3)and len(a)>0 and np.isfinite(a).all();assert all(signed_area(projected(f))!=0 for f in a),'Zero projected terrain facet';return a
def at(a,b,t):return tuple(a[k]+t*(b[k]-a[k])for k in range(2))
def on(a,b,p):
 if cross(a,b,p)!=0:return None
 k=0 if b[0]!=a[0]else 1;t=(p[k]-a[k])/(b[k]-a[k]);return t if 0<=t<=1 else None
def atomic_boundary(faces):
 faces=arrays(faces);polys=[oriented(projected(f))for f in faces];overlaps=[]
 for i,a in enumerate(polys):
  for j in range(i+1,len(polys)):
   p=a
   for u,v in zip(polys[j],polys[j][1:]+polys[j][:1]):p=clip(p,u,v,True)
   area=abs(signed_area(p))
   if area:overlaps.append(dict(faces=[i,j],exactPositiveOverlapM2=area))
 edges=[(i,a,b)for i,p in enumerate(polys)for a,b in zip(p,p[1:]+p[:1])];vertices={p for _,a,b in edges for p in [a,b]};atoms=defaultdict(list)
 for i,a,b in edges:
  cuts={F(0),F(1)}
  for p in vertices:
   t=on(a,b,p)
   if t is not None:cuts.add(t)
  ordered=sorted(cuts)
  for lo,hi in zip(ordered,ordered[1:]):
   u,v=at(a,b,lo),at(a,b,hi);assert u!=v;key=tuple(sorted((u,v)));atoms[key].append(dict(face=i,start=u,end=v,exactEndpointY=[source_height(faces[i],p)for p in [u,v]]))
 boundary=[];internal=[];invalid=[];adj=defaultdict(set)
 for key,inc in sorted(atoms.items()):
  r=dict(canonicalEndpoints=key,allOriginalIncidences=inc)
  if len(inc)==1:boundary.append(r)
  elif len(inc)==2:
   a,b=inc;opposite=a['start']==b['end']and a['end']==b['start'];heights=a['exactEndpointY']==list(reversed(b['exactEndpointY']));r.update(oppositeDirectedIncidence=opposite,exactShared3DHeightCompatible=heights);internal.append(r)
   if opposite and heights:adj[a['face']].add(b['face']);adj[b['face']].add(a['face'])
   else:invalid.append(r)
  else:invalid.append(r)
 outgoing=defaultdict(list);incoming=defaultdict(list)
 for i,r in enumerate(boundary):
  e=r['allOriginalIncidences'][0];outgoing[e['start']].append(i);incoming[e['end']].append(i)
 nodes=set(outgoing)|set(incoming);branch=[dict(point=p,outgoingAtoms=outgoing[p],incomingAtoms=incoming[p])for p in sorted(nodes)if len(outgoing[p])!=1 or len(incoming[p])!=1];loops=[]
 if not branch:
  remaining=set(range(len(boundary)))
  while remaining:
   first=min(remaining);now=first;loop=[]
   while now in remaining:
    remaining.remove(now);loop.append(now);end=boundary[now]['allOriginalIncidences'][0]['end'];now=outgoing[end][0]
   assert now==first,'Boundary cycle entered another completed cycle';points=[boundary[i]['allOriginalIncidences'][0]['start']for i in loop];loops.append(dict(boundaryAtoms=loop,exactDirectedPoints=points,exactSignedProjectedAreaM2=signed_area(points)))
 components=[];unseen=set(range(len(faces)))
 while unseen:
  todo=[min(unseen)];component=[]
  while todo:
   i=todo.pop()
   if i not in unseen:continue
   unseen.remove(i);component.append(i);todo.extend(adj[i]&unseen)
  components.append(sorted(component))
 return dict(completeFaces=len(faces),allAtomicEdges=[dict(canonicalEndpoints=k,allOriginalIncidences=v)for k,v in sorted(atoms.items())],completePositiveProjectedOverlapPairs=overlaps,allInternalAtomicEdges=internal,allBoundaryAtomicEdges=boundary,invalidAtomicIncidences=invalid,boundaryBranchPoints=branch,completeSimpleDirectedBoundaryCycles=loops,genuineNonzero3DSharedEdgeFaceComponents=components,topologyQualified=not overlaps and not invalid and not branch and all(r['exactSignedProjectedAreaM2']!=0 for r in loops),oneGenuine3DSharedEdgeComponent=len(components)==1,terrainCandidateApproved=False)
def one_edge_ring(domains,retained):
 domains=arrays(domains);retained=arrays(retained);union=atomic_boundary(domains);rows=[];selected=set();coverage=[]
 for bi,boundary in enumerate(union['allBoundaryAtomicEdges']):
  edge=boundary['allOriginalIncidences'][0];a,b=edge['start'],edge['end'];parts=[]
  for ri,f in enumerate(retained):
   p=oriented(projected(f))
   for c,d in zip(p,p[1:]+p[:1]):
    iv=overlap_interval(a,b,c,d)
    if iv is None:continue
    pts=[at(a,b,t)for t in iv];gaps=[source_height(domains[edge['face']],p)-source_height(f,p)for p in pts];opposite=(b[0]-a[0])*(d[0]-c[0])+(b[1]-a[1])*(d[1]-c[1])<0;compatible=all(v==0 for v in gaps)
    if opposite:selected.add(ri)
    rows.append(dict(boundaryAtom=bi,domainFace=edge['face'],retainedFace=ri,exactPositiveParameterInterval=iv,oppositeDirectedBoundaryEdge=opposite,exactEndpointCurrentHeightGapsM=gaps,exactCurrent3DCompatible=compatible))
    if opposite and compatible:parts.append(iv)
  coverage.append(dict(boundaryAtom=bi,completeOriginalCurrent3DEdgeNeighbourCoverage=interval_covered(parts)))
 return dict(domainAtomicBoundary=union,completeOnePositiveEdgeAdjacentRetainedFaceIds=sorted(selected),allExactPositiveAdjacentIntervals=rows,allDomainBoundary3DNeighbourCoverage=coverage,pointOnlyNeighboursReceiveNoRingCredit=True,oneLayerOnlyNoRecursiveExpansion=True,terrainCandidateApproved=False)
