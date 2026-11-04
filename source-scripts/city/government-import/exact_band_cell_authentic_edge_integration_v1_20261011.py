"""DRAFT complete finite band-cell adjacency; graph context is never a terrain candidate."""
from fractions import Fraction as F
from collections import defaultdict,deque
from exact_faithful_multisurface_transition_domain_v1_20261011 import closed_pairs
from exact_source_core_ten_metre_transition_domain_v1_20261011 import intersection
from exact_source_planar_domain_recovery_seams_v1_20261011 import overlap_interval,interval_covered
from exact_original_projection_coverage_v2_20261010 import signed_area,cross
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import at,on

def checked_cells(cells):
 out=[]
 for p in cells:
  p=[tuple(F(v)for v in q)for q in p];assert len(p)>=3 and all(len(q)==2 for q in p)and signed_area(p)>0;assert all(a!=b for a,b in zip(p,p[1:]+p[:1]));assert all(cross(a,b,q)>=0 for a,b in zip(p,p[1:]+p[:1])for q in p),'Nonconvex band cell';out.append(p)
 return out

def complete_graph(cells,outer_edges,checkpoints=None):
 cells=checked_cells(cells);pairs=sorted({(min(i,j),max(i,j))for i,j in closed_pairs(cells,cells)if i!=j});adj=defaultdict(set);links=[];overlaps=[];same=[]
 def compute(part):
  rows=[]
  for i,j in part:
   area=signed_area(intersection(cells[i],cells[j]));pairlinks=[]
   for ei,(a,b)in enumerate(zip(cells[i],cells[i][1:]+cells[i][:1])):
    for ej,(c,d)in enumerate(zip(cells[j],cells[j][1:]+cells[j][:1])):
     iv=overlap_interval(a,b,c,d)
     if iv is None:continue
     opposite=sum((b[k]-a[k])*(d[k]-c[k])for k in[0,1])<0;pairlinks.append(dict(cells=[i,j],cellEdges=[ei,ej],exactPositiveFirstEdgeInterval=iv,exactSharedEndpoints=[at(a,b,t)for t in iv],oppositeDirected=opposite))
   rows.append(dict(cells=[i,j],exactPositiveOverlapArea=area,allFiniteSharedEdges=pairlinks))
  return rows
 pairrows=checkpoints.map('complete-existing-band-cell-finite-pairs',pairs,compute)if checkpoints else compute(pairs)
 assert [r['cells']for r in pairrows]==[list(p)for p in pairs],'Incomplete or changed exact band pair census'
 for row in pairrows:
  i,j=row['cells']
  if row['exactPositiveOverlapArea']:overlaps.append(dict(cells=[i,j],exactPositiveOverlapArea=row['exactPositiveOverlapArea']))
  for r in row['allFiniteSharedEdges']:
   links.append(r)
   if r['oppositeDirected']:adj[i].add(j);adj[j].add(i)
   else:same.append(r)
 outer=[];targets=set() # Exact finite edges, never bounding rectangles.
 nominations=closed_pairs([[tuple(e['start']),tuple(e['end'])]for e in outer_edges],cells)
 for oi,ci in nominations:
  a,b=tuple(outer_edges[oi]['start']),tuple(outer_edges[oi]['end']);assert a!=b
  for ei,(u,v)in enumerate(zip(cells[ci],cells[ci][1:]+cells[ci][:1])):
   iv=overlap_interval(a,b,u,v)
   if iv is not None:outer.append(dict(outerEdge=oi,cell=ci,cellEdge=ei,exactWholeOuterParameters=iv,exactProjectedEndpoints=[at(a,b,t)for t in iv],heightAndF32SeamUnqualified=True));targets.add(ci)
 coverage=[dict(outerEdge=i,wholeProjectedBandEdgeCoverage=interval_covered([r['exactWholeOuterParameters']for r in outer if r['outerEdge']==i]))for i in range(len(outer_edges))];components=[];unseen=set(range(len(cells)))
 while unseen:
  q=[min(unseen)];component=[]
  while q:
   i=q.pop()
   if i not in unseen:continue
   unseen.remove(i);component.append(i);q.extend(adj[i]&unseen)
  components.append(sorted(component))
 return dict(completeCells=len(cells),completeClosedAABBNominatedCellPairs=pairs,completePositiveInteriorOverlapPairs=overlaps,allPositiveSharedProjectedIntervals=links,sameDirectedPositiveSharedIntervals=same,positiveEdgeAdjacency={str(i):sorted(adj[i])for i in range(len(cells))},allFinitePositiveOuterEdgeLinks=outer,allWholeOuterProjectedCoverage=coverage,outerLinkedCells=sorted(targets),completePositiveEdgeComponents=components,projectedPartitionGraphQualified=not overlaps and not same,canonicalSharedProjectedNodes=sorted({tuple(p)for r in links for p in r['exactSharedEndpoints']}|{tuple(p)for r in outer for p in r['exactProjectedEndpoints']}),noHeightOrF32SeamCredit=True,noCandidate=True)

def source_boundary_integration(cells,graph,atom,positive_band_membership):
 cells=checked_cells(cells);a,b=map(tuple,atom['exactXZEndpoints']);assert a!=b;seeds=sorted({i for row in positive_band_membership['completePositiveIntervals']for i in row['allBandOwners']});assert all(0<=i<len(cells)for i in seeds);direct=[]
 for i in seeds:
  for ei,(u,v)in enumerate(zip(cells[i],cells[i][1:]+cells[i][:1])):
   iv=overlap_interval(a,b,u,v)
   if iv is not None:direct.append(dict(cell=i,cellEdge=ei,exactPositiveSourceParameters=iv,exactEndpoints=[at(a,b,t)for t in iv],heightAndRenderedSeamUnqualified=True))
 target=set(graph['outerLinkedCells']);queue=deque((i,[i])for i in seeds);visited=set(seeds);path=None
 while queue:
  i,p=queue.popleft()
  if i in target:path=p;break
  for j in graph['positiveEdgeAdjacency'][str(i)]:
   if j not in visited:visited.add(j);queue.append((j,p+[j]))
 return dict(completePositiveIntervalSeedCells=seeds,allDirectFiniteCollinearBandBoundaryIntervals=direct,wholeProjectedDirectBoundaryCovered=interval_covered([r['exactPositiveSourceParameters']for r in direct]),deterministicPositiveEdgeBandPathToOuter=path,allVisitedCells=sorted(visited),bandPathDoesNotImplySourceOrOuterHeightSeam=True,coreMAXPreservationUnqualified=True,underlayOverlapNotWaived=True,noCandidate=True,noRouteCredit=True)
