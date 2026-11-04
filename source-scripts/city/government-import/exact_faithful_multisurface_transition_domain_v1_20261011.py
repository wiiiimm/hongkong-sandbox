"""DRAFT scratch projected union for a faithful original multisurface terrain.
Scratch cells never replace/delete original3D source faces. No execution approval.
"""
from fractions import Fraction as F
from collections import defaultdict
from itertools import product
from exact_source_core_ten_metre_transition_domain_v1_20261011 import polygon,separated,hull,intersection
from exact_original_projection_coverage_v2_20261010 import subtract,signed_area
from exact_original_3d_directed_edge_atom_census_v1_20261011 import census
from exact_original_3d_boundary_cycles_core_point_locus_v1_20261011 import cycles
from exact_compute_transition_mesh_v1_20261011 import height,contains,edge_intersections
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on,at

def closed_pairs(a,b):
 """Exact rational buckets, no global LCM of clipped intersection denominators."""
 def box(p):return(min(v[0]for v in p),max(v[0]for v in p),min(v[1]for v in p),max(v[1]for v in p))
 def cells(q):return product(range(q[0]//5,q[1]//5+1),range(q[2]//5,q[3]//5+1))
 boxes=[box(p)for p in b];buckets=defaultdict(set)
 for j,q in enumerate(boxes):
  for k in cells(q):buckets[k].add(j)
 result=[]
 for i,p in enumerate(a):
  q=box(p);ids=set()
  for k in cells(q):ids.update(buckets[k])
  result.extend((i,j)for j in sorted(ids))
 return result

def mapped(checkpoints,name,items,compute):return checkpoints.map(name,items,compute)if checkpoints else compute(items)
def partition(polys,checkpoints=None,name='scratch-source-union'):
 polys=[polygon(p)for p in polys];pairs=closed_pairs(polys,polys);prior=defaultdict(list)
 for i,j in pairs:
  if j<i:prior[i].append(j)
 def compute(part):
  result=[]
  for i in part:
   remaining=[polys[i]]
   for j in sorted(prior[i]):
    remaining=[v for q in remaining for v in([q]if separated(q,polys[j])else subtract(q,polys[j]))]
    if not remaining:break
   result.append(dict(originalScratchPiece=i,completeEarlierClosedBucketPieces=sorted(prior[i]),allExactRemainingPositiveCells=remaining,exactRemainingAreaM2=sum(signed_area(p)for p in remaining)))
  return result
 rows=mapped(checkpoints,name,list(range(len(polys))),compute);assert [r['originalScratchPiece']for r in rows]==list(range(len(polys)))
 return [polygon(q)for r in rows for q in r['allExactRemainingPositiveCells']],rows

def planar_boundary(polys,checkpoints=None,label="scratch-planar-boundary"):
 triangles=[]
 for p in polys:
  p=polygon(p);c=tuple(sum(v[k]for v in p)/len(p)for k in range(2))
  for a,b in zip(p,p[1:]+p[:1]):
   t=[(c[0],F(0),c[1]),(a[0],F(0),a[1]),(b[0],F(0),b[1])];assert signed_area([(v[0],v[2])for v in t])>0;triangles.append(t)
 if checkpoints:
  from exact_resumable_projected_inventory_v1_20261011 import Checkpoints
  checkpoints=Checkpoints(checkpoints.folder/label,triangles,checkpoints.contract['inputBindings'],checkpoints.check_inputs)
 atom=census(triangles,checkpoints);assert not atom['allNonmanifoldAtomIds']and not atom['allTwoSameDirectionAtomIds'];cy=cycles(atom['allExact3DAtomicEdges'],len(triangles));assert all(c['completeBoundaryCyclePartitionQualified']for c in cy),'Scratch projected union boundary branches; no guessed cycle/point bridge'
 edges=[]
 for i in atom['allPositive3DBoundaryAtomIds']:
  e=atom['allExact3DAtomicEdges'][i]['allDirectedIncidences'][0];edges.append(dict(start=(e['start'][0],e['start'][2]),end=(e['end'][0],e['end'][2]),scratchAtomicEdge=i))
 return edges,dict(completeScratchPositiveTriangles=len(triangles),completeAtomicCensus=atom,completePositiveEdgeComponentCycles=cy)

def domain(polys,checkpoints=None):
 originals=[polygon(p)for p in polys];core,proof=partition(originals,checkpoints);inner,innerproof=planar_boundary(core,checkpoints,"complete-source-union-boundary");diamond=[(-F(10),F(0)),(F(0),-F(10)),(F(10),F(0)),(F(0),F(10))];strips=[hull([(p[0]+v[0],p[1]+v[1])for p in[e['start'],e['end']]for v in diamond])for e in inner]
 # Exactly strip_i minus complete source union and earlier original strips.
 # Earlier raw strips have the same union as earlier admitted band plus core.
 allpolys=originals+strips;pairs=closed_pairs(strips,allpolys);nominations=defaultdict(list)
 for i,j in pairs:
  if j<len(originals)or j-len(originals)<i:nominations[i].append(j)
 def compute(part):
  rows=[]
  for i in part:
   remaining=[strips[i]]
   for j in sorted(nominations[i]):
    remaining=[v for q in remaining for v in([q]if separated(q,allpolys[j])else subtract(q,allpolys[j]))]
    if not remaining:break
   rows.append(dict(sourceBoundary=i,exactOriginalBoundary=inner[i],exactInflatedL1Strip=strips[i],allCompleteClosedBucketSubtractedPieceIds=sorted(nominations[i]),allExactPositiveBandCells=remaining))
  return rows
 bandproof=mapped(checkpoints,'complete-ten-metre-source-union-band',list(range(len(strips))),compute);band=[polygon(p)for r in bandproof for p in r['allExactPositiveBandCells']];outer,outerproof=planar_boundary(core+band,checkpoints,"complete-source-plus-band-boundary");bounds=[min(p[k]for q in core+band for p in q)for k in[0,1]]+[max(p[k]for q in core+band for p in q)for k in[0,1]]
 return dict(scratchOriginalProjectionUnionCells=core,completeSourceUnionPartitionProof=proof,sourceUnionBoundarySegments=inner,sourceUnionBoundaryProof=innerproof,computeBandPolygons=band,allComputeBandSourceBoundaryProvenance=bandproof,completeOuterBoundarySegments=outer,completeOuterBoundaryProof=outerproof,exactWholeDomainXZBounds=bounds,explicitWidthM=F(10),metric='10mL1;Euclidean<=10m',scratchDoesNotReplaceAnyOriginal3DFace=True)

def upper_anchors(boundary,original_faces):
 """Exact full interval max-plane ownership, matching existing walking sampler."""
 from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
 import numpy as np
 ground=CompleteGround(np.asarray(original_faces,dtype='<f8'));polys=[polygon([(p[0],p[2])for p in f]if signed_area([(p[0],p[2])for p in f])>0 else list(reversed([(p[0],p[2])for p in f])))for f in original_faces];rows=[]
 for bi,e in enumerate(boundary):
  a,b=e['start'],e['end'];ids,proof=ground.select([(a[0],F(0),a[1]),(b[0],F(0),b[1])]);ids=list(map(int,ids));cuts={F(0),F(1)}
  for i in ids:
   q=polys[i]
   for c,d in zip(q,q[1:]+q[:1]):
    for p in edge_intersections(a,b,c,d):cuts.add(on(a,b,p))
  basic=sorted(cuts)
  for lo,hi in zip(basic,basic[1:]):
   mid=at(a,b,(lo+hi)/2);active=[i for i in ids if contains(polys[i],mid)];assert active
   u,v=at(a,b,lo),at(a,b,hi)
   for ai,i in enumerate(active):
    for j in active[:ai]:
     da=height(original_faces[i],u)-height(original_faces[j],u);db=height(original_faces[i],v)-height(original_faces[j],v)
     if da*db<0:cuts.add(lo+(hi-lo)*da/(da-db))
  cuts=sorted(cuts)
  for lo,hi in zip(cuts,cuts[1:]):
   u,v,mid=at(a,b,lo),at(a,b,hi),at(a,b,(lo+hi)/2);active=[i for i in ids if contains(polys[i],mid)];assert active;owner=min(active,key=lambda i:(-height(original_faces[i],mid),i));ys=[height(original_faces[owner],p)for p in[u,v]]
   assert all(all(ys[k]>=height(original_faces[i],p)for i in ids if contains(polys[i],p))for k,p in enumerate([u,v])),'Closed authentic upper boundary discontinuity; no snap'
   rows.append(dict(sourceUnionBoundary=bi,exactSourceParameterInterval=[lo,hi],start=u,end=v,exactEndpointY=ys,originalUpperPlane=owner,allOriginalClosedIntervalPlanes=active,completeSourceSelection=proof))
 return rows
