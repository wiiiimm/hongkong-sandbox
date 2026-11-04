"""DRAFT finite unchanged F32 source-edge atoms and source-bound band nomination."""
from fractions import Fraction as F
from exact_faithful_source_step_junction_feasibility_v2_20261011 import project,native_query_inventory
from exact_compute_transition_mesh_v1_20261011 import contains,height,edge_intersections
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on,at
from exact_original_projection_coverage_v2_20261010 import cross,signed_area

def infinitesimal_sides(poly,p,a,b):
 """Exact one-sided ownership at an edge midpoint, not an epsilon sample."""
 if not contains(poly,p):return False,False
 normal=(-(b[1]-a[1]),b[0]-a[0]);left=right=True
 for u,v in zip(poly,poly[1:]+poly[:1]):
  if cross(u,v,p)==0:
   derivative=(v[0]-u[0])*normal[1]-(v[1]-u[1])*normal[0]
   if derivative<0:left=False
   if derivative>0:right=False
 return left,right

def complete_actual_edge_atoms(native,face,edge):
 t=native['tri'][face];aa,bb=t[edge],t[(edge+1)%3];a,b=(aa[0],aa[2]),(bb[0],bb[2]);assert aa!=bb
 if a==b:return dict(sourceFace=face,sourceEdge=edge,actualOriginalEndpoints=[aa,bb],projectedPointOnly=True,noProjectedBoundaryCredit=True)
 ids,proof=native['ground'].segment([aa,bb]);ids=list(map(int,ids));cuts={F(0),F(1)}
 for i in ids:
  poly=native['polys'][i]
  for u,v in zip(poly,poly[1:]+poly[:1]):
   if u==v:
    x=on(a,b,u)
    if x is not None:cuts.add(x)
   else:
    for x in edge_intersections(a,b,u,v):cuts.add(on(a,b,x))
 atoms=[]
 for lo,hi in zip(sorted(cuts),sorted(cuts)[1:]):
  p=at(a,b,(lo+hi)/2);owners=[]
  for i in ids:
   poly=native['polys'][i]
   if not signed_area(poly)or not contains(poly,p):continue
   left,right=infinitesimal_sides(poly,p,a,b);owners.append(dict(sourceFace=i,heightIndexed=native['indexed'][i],coversPositiveLeftNeighbourhood=left,coversPositiveRightNeighbourhood=right,wholeAtomEndpointPlaneHeights=[height(native['tri'][i],at(a,b,x))for x in [lo,hi]]))
  left=[r['sourceFace']for r in owners if r['coversPositiveLeftNeighbourhood']];right=[r['sourceFace']for r in owners if r['coversPositiveRightNeighbourhood']];atoms.append(dict(parameters=[lo,hi],exactXZEndpoints=[at(a,b,x)for x in[lo,hi]],allCompleteClosedSourceOwners=owners,leftDrawnOwners=left,rightDrawnOwners=right,actualDrawnProjectedExteriorBoundary=bool(left)!=bool(right),bothDrawnSidesCovered=bool(left)and bool(right),noHeightOrSeamCredit=True))
 return dict(sourceFace=face,sourceEdge=edge,actualOriginalEndpoints=[aa,bb],allExactOrderedParameters=sorted(cuts),allCompletePositiveEdgeAtoms=atoms,completeActualSourceClosedAABBProof=proof,completeActualSourceNominations=ids,unchangedActualEdge=True)

def complete_outer_edge_candidates(p,edges):
 """Every finite outer edge; exact L1 minimum and finite breakpoint nominations."""
 p=tuple(map(F,p));rows=[]
 for i,e in enumerate(edges):
  a,b=tuple(e['start']),tuple(e['end']);d=tuple(b[k]-a[k]for k in[0,1]);assert a!=b;parameters={F(0),F(1)}
  for k in[0,1]:
   if d[k]:
    t=(p[k]-a[k])/d[k]
    if 0<=t<=1:parameters.add(t)
  euclidean=sum((p[k]-a[k])*d[k]for k in[0,1])/sum(v*v for v in d);parameters.add(max(F(0),min(F(1),euclidean)));nodes=[dict(parameter=t,exactPointXZ=at(a,b,t),exactL1Distance=sum(abs(at(a,b,t)[k]-p[k])for k in[0,1]))for t in sorted(parameters)];minimum=min(n['exactL1Distance']for n in nodes);rows.append(dict(outerEdge=i,exactEndpoints=[a,b],exactMinimumL1Distance=minimum,allFiniteBreakpointNominations=[n for n in nodes if 0<n['exactL1Distance']<=10],withinTenMetresSomewhere=minimum<=10))
 return rows

def directed_boundary_cycles(edges):
 outgoing={};incoming={}
 for i,e in enumerate(edges):
  a,b=tuple(e['start']),tuple(e['end']);assert a!=b;outgoing.setdefault(a,[]).append(i);incoming.setdefault(b,[]).append(i)
 failures=[dict(point=p,outgoing=outgoing.get(p,[]),incoming=incoming.get(p,[]))for p in sorted(set(outgoing)|set(incoming))if len(outgoing.get(p,[]))!=1 or len(incoming.get(p,[]))!=1];cycles=[]
 if not failures:
  remaining=set(range(len(edges)))
  while remaining:
   first=min(remaining);now=first;cycle=[]
   while now in remaining:
    remaining.remove(now);cycle.append(now);now=outgoing[tuple(edges[now]['end'])][0]
   assert now==first;points=[tuple(edges[i]['start'])for i in cycle];area=signed_area(points);cycles.append(dict(edgeIDs=cycle,exactDirectedPoints=points,exactSignedArea=area,orientedPositiveUnionExterior=area>0,orientedPositiveUnionHole=area<0))
 return dict(completeEdges=len(edges),degreeFailures=failures,completeDirectedCycles=cycles,nonzeroCycles=all(c['exactSignedArea']!=0 for c in cycles),orientationClassificationRequiresInheritedPositiveUnionBoundaryContract=True,noPocketFillOrRouteCredit=True)

def complete_edge_band_coverage(a,b,polys):
 from exact_faithful_multisurface_transition_domain_v1_20261011 import closed_pairs
 a,b=tuple(a),tuple(b);assert a!=b;ids=[j for i,j in closed_pairs([[a,b]],polys)];cuts={F(0),F(1)}
 for i in ids:
  poly=polys[i]
  for u,v in zip(poly,poly[1:]+poly[:1]):
   for x in edge_intersections(a,b,u,v):cuts.add(on(a,b,x))
 rows=[dict(parameters=[lo,hi],allBandOwners=[i for i in ids if contains(polys[i],at(a,b,(lo+hi)/2))])for lo,hi in zip(sorted(cuts),sorted(cuts)[1:])]
 return dict(completePositiveIntervals=rows,completeBandClosedBucketCandidates=ids,wholeProjectedEdgeBandCovered=all(r['allBandOwners']for r in rows),notTwoSidedOrPocketAreaCoverage=True)
