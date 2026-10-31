"""DRAFT exact source-facet core plus bounded compute terrain domain.
The 10m L1 diamond has Euclidean radius <=10m; it is not a guessed rectangle.
No height interpolation, mesh nomination or acceptance in this domain kernel.
"""
from fractions import Fraction as F
from collections import defaultdict
from exact_original_projection_coverage_v2_20261010 import cross,signed_area,clip,subtract
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on,at
def polygon(p):
 assert all(len(q)==2 for q in p);p=[tuple(F(v)for v in q)for q in p];assert len(p)>=3 and signed_area(p)>0
 assert all(cross(a,b,c)>=0 for a,b,c in zip(p,p[1:]+p[:1],p[2:]+p[:2])),'Nonconvex piece'
 return p
def separated(a,b):return any(max(p[k]for p in a)<min(p[k]for p in b)or max(p[k]for p in b)<min(p[k]for p in a)for k in [0,1])
def intersection(a,b):
 if separated(a,b):return []
 p=a
 for u,v in zip(b,b[1:]+b[:1]):p=clip(p,u,v,True)
 return p
def hull(points):
 points=sorted(set(points));assert len(points)>=3
 def half(ps):
  out=[]
  for p in ps:
   while len(out)>1 and cross(out[-2],out[-1],p)<=0:out.pop()
   out.append(p)
  return out
 return polygon(half(points)[:-1]+half(list(reversed(points)))[:-1])
def atomic(polygons):
 polygons=[polygon(p)for p in polygons];points={p for poly in polygons for p in poly};atoms=defaultdict(list);overlaps=[]
 for i,p in enumerate(polygons):
  for j in range(i):
   q=intersection(p,polygons[j]);area=signed_area(q)
   if area:overlaps.append(dict(pieces=[j,i],exactPositiveOverlapM2=area))
  for a,b in zip(p,p[1:]+p[:1]):
   cuts={F(0),F(1)}
   for q in points:
    t=on(a,b,q)
    if t is not None:cuts.add(t)
   cuts=sorted(cuts)
   for lo,hi in zip(cuts,cuts[1:]):
    u,v=at(a,b,lo),at(a,b,hi);assert u!=v;atoms[tuple(sorted((u,v)))].append(dict(piece=i,start=u,end=v))
 boundary=[];invalid=[]
 for key,inc in sorted(atoms.items()):
  row=dict(endpoints=key,incidences=inc)
  if len(inc)==1:boundary.append(row)
  elif len(inc)!=2 or inc[0]['start']!=inc[1]['end']or inc[0]['end']!=inc[1]['start']:invalid.append(row)
 outgoing=defaultdict(list);incoming=defaultdict(list)
 for i,r in enumerate(boundary):e=r['incidences'][0];outgoing[e['start']].append(i);incoming[e['end']].append(i)
 branches=[dict(point=p,outgoing=outgoing[p],incoming=incoming[p])for p in sorted(set(outgoing)|set(incoming))if len(outgoing[p])!=1 or len(incoming[p])!=1];cycles=[]
 if not branches:
  remaining=set(range(len(boundary)))
  while remaining:
   first=min(remaining);now=first;ids=[]
   while now in remaining:remaining.remove(now);ids.append(now);now=outgoing[boundary[now]['incidences'][0]['end']][0]
   assert now==first;pts=[boundary[i]['incidences'][0]['start']for i in ids];cycles.append(dict(atoms=ids,points=pts,exactSignedAreaM2=signed_area(pts)))
 return dict(completePieces=len(polygons),allAtomicEdges=[dict(endpoints=k,incidences=v)for k,v in sorted(atoms.items())],allBoundaryAtoms=boundary,allInvalidIncidences=invalid,allPositiveOverlaps=overlaps,allBranchPoints=branches,allDirectedCycles=cycles,projectedTopologyQualified=not overlaps and not invalid and not branches and bool(cycles)and all(c['exactSignedAreaM2']!=0 for c in cycles))
def domain(core,width=F(10)):
 width=F(width);assert width==10,'This version permits exactly the explicit10mL1 band'
 core=[polygon(p)for p in core];initial=atomic(core);assert initial['projectedTopologyQualified'],'Invalid authentic projected core union'
 diamond=[(-width,F(0)),(F(0),-width),(width,F(0)),(F(0),width)];band=[];provenance=[]
 # For a closed finite polygon union, adding a convex diamond consists of the
 # original union plus every genuine union-boundary segment Minkowski diamond.
 for bi,row in enumerate(initial['allBoundaryAtoms']):
  e=row['incidences'][0];strip=hull([(p[0]+d[0],p[1]+d[1])for p in [e['start'],e['end']]for d in diamond]);remaining=[strip]
  for other in core+band:
   remaining=[p for old in remaining for p in subtract(old,other)]
   if not remaining:break
  for p in remaining:
   p=polygon(p);band.append(p);provenance.append(dict(sourceBoundaryAtom=bi,exactInflatedBoundarySegmentPolygon=strip))
 combined=core+band;outer=atomic(combined);assert outer['projectedTopologyQualified'],'Invalid generated band union'
 area=sum(signed_area(p)for p in combined);bounds=[min(p[k]for poly in combined for p in poly)for k in [0,1]]+[max(p[k]for poly in combined for p in poly)for k in [0,1]]
 return dict(originalCorePolygons=core,sourceCoreAtomicBoundary=initial,computeBandPolygons=band,allComputeBandSourceBoundaryProvenance=provenance,combinedAtomicBoundary=outer,exactWholeDomainAreaM2=area,exactWholeDomainXZBounds=bounds,explicitWidthM=width,metric='L1 diamond; every band point Euclidean-distance<=10m from genuine source core',terrainCandidateApproved=False)
