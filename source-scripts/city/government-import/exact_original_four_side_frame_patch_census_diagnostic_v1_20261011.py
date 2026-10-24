"""Enumerate complete original side patches without using host proximity.

This narrow 12-vertex/16-facet annular topology has two four-corner boundaries.
Unique exact nearest-corner matching and unique shortest original corner rails
identify four complete side patches. These are source geometry diagnostics,
never a function, visual role, simple opening, solid or support certificate.
"""
from fractions import Fraction as F
from collections import defaultdict
import hashlib,heapq
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_closed_boundary_loop_band_diagnostic_v1_20261011 import loop
def squared(a,b):return sum((F(float(x))-F(float(y)))**2 for x,y in zip(a,b))
def verify(world,face_ids):
 world=np.asarray(world,float);ids=list(face_ids)
 assert world.ndim==3 and world.shape[1:]==(3,3)and np.isfinite(world).all()and ids==sorted(set(ids))and all(type(i)is int and 0<=i<len(world)for i in ids)
 inv=census(world,ids);out=dict(contract='exact-original-four-side-frame-patch-census-diagnostic-v1',completeWorldSHA256=hashlib.sha256(world.tobytes()).hexdigest(),completeOriginalFaceIds=ids,completeActualEdgeCensus=inv,verifiedCompleteFourSidePatchPartition=False,hostProximityNeverUsedForPartition=True,sourceGeometryChanges=0,authoredRoleAccepted=False,structuralRootOrBridgeCredit=False)
 def fail(reason):return dict(**out,reason=reason)
 if len(ids)!=16 or inv['exactNonrenderingOriginalFaces']or len(inv['sharedEdgeConnectedComponents'])!=1:return fail('not-the-complete16-nonzero-facet-edge-body')
 edges=defaultdict(list);vertex_adj=defaultdict(set)
 for f in ids:
  for a,b in zip(world[f],np.roll(world[f],-1,axis=0)):
   a,b=tuple(a),tuple(b)
   if a==b:continue
   edge=tuple(sorted([a,b]));edges[edge].append(f);vertex_adj[a].add(b);vertex_adj[b].add(a)
 if len(vertex_adj)!=12 or any(len(r)>2 for r in edges.values()):return fail('not-twelve-vertices-with-at-most-two-edge-incidences')
 boundary={e:r for e,r in edges.items()if len(r)==1};adj=defaultdict(set)
 for a,b in boundary:adj[a].add(b);adj[b].add(a)
 if len(boundary)!=8 or any(len(r)!=2 for r in adj.values()):return fail('not-two-complete-degree-two-four-corner-boundaries')
 remaining=set(adj);groups=[]
 while remaining:
  seen={min(remaining)};todo=list(seen)
  while todo:
   for n in adj[todo.pop()]:
    if n not in seen:seen.add(n);todo.append(n)
  remaining-=seen;group=sorted(e for e in boundary if e[0]in seen)
  if len(group)!=4 or len(seen)!=4:return fail('boundary-is-not-an-authentic-four-edge-loop')
  assert loop(np.asarray(group,float))==group;groups.append(group)
 if len(groups)!=2:return fail('not-two-boundary-loops')
 corners=[sorted({v for e in g for v in e})for g in groups];match={}
 for a in corners[0]:
  values=[(squared(a,b),b)for b in corners[1]];distance=min(v[0]for v in values);nearest=[v[1]for v in values if v[0]==distance]
  if len(nearest)!=1:return fail('corner-counterpart-is-not-unique')
  match[a]=nearest[0]
 if len(set(match.values()))!=4:return fail('nearest-corner-counterparts-are-not-bijective')
 if any(tuple(sorted([match[a],match[b]]))not in groups[1]for a,b in groups[0]):return fail('corner-matching-does-not-preserve-authored-boundary-adjacency')
 rail_records=[];rail_edges=set();internal=set();boundary_vertices=set(adj)
 for a,b in sorted(match.items()):
  allowed=set(vertex_adj)-(boundary_vertices-{a,b});dist={a:F(0)};ways={a:1};paths={a:[a]};queue=[(F(0),a)]
  while queue:
   cost,v=heapq.heappop(queue)
   if cost!=dist[v]:continue
   for n in sorted(vertex_adj[v]&allowed):
    proposal=cost+squared(v,n)
    if n not in dist or proposal<dist[n]:dist[n]=proposal;ways[n]=ways[v];paths[n]=paths[v]+[n];heapq.heappush(queue,(proposal,n))
    elif proposal==dist[n]:ways[n]=min(2,ways[n]+ways[v])
  if b not in paths or ways[b]!=1 or len(paths[b])!=3:return fail('not-unique-two-edge-original-corner-rail')
  path=paths[b]
  if path[1]in internal:return fail('original-corner-rails-share-an-interior-vertex')
  internal.add(path[1]);selected=[tuple(sorted(e))for e in zip(path,path[1:])]
  if any(len(edges[e])!=2 for e in selected):return fail('corner-rail-is-not-an-original-two-face-edge')
  rail_edges.update(selected);rail_records.append(dict(completeOriginalRailVertices=[list(v)for v in path],completeOriginalRailEdges=[[list(v)for v in e]for e in selected],exactShortestSumSquaredEdgeLengths=str(dist[b]),allAllowedOriginalVertexDistances=[dict(vertex=list(v),exactDistance=str(c))for v,c in sorted(dist.items())]))
 if internal!=set(vertex_adj)-boundary_vertices:return fail('corner-rails-do-not-account-every-interior-vertex')
 face_adj=defaultdict(set)
 for edge,faces in edges.items():
  if len(faces)==2 and edge not in rail_edges:face_adj[faces[0]].add(faces[1]);face_adj[faces[1]].add(faces[0])
 remaining=set(ids);patches=[]
 while remaining:
  seen={min(remaining)};todo=list(seen)
  while todo:
   for n in face_adj[todo.pop()]:
    if n not in seen:seen.add(n);todo.append(n)
  remaining-=seen;patch=sorted(seen)
  if len(patch)!=4:return fail('source-rail-cut-does-not-produce-four-complete-four-facet-patches')
  cut_boundary=[edge for edge,faces in edges.items()if sum(f in seen for f in faces)==1]
  first=[edge for edge in groups[0]if edge in cut_boundary];second=[edge for edge in groups[1]if edge in cut_boundary]
  if len(first)!=1 or len(second)!=1 or tuple(sorted(match[v]for v in first[0]))!=second[0]:return fail('patch-does-not-span-corresponding-complete-boundary-edges')
  patches.append(dict(completeOriginalPatchFacetIds=patch,completePatchCensus=census(world,patch),completePatchBoundaryEdges=[[list(v)for v in e]for e in sorted(cut_boundary)],firstOriginalBoundaryEdge=[list(v)for v in first[0]],secondOriginalBoundaryEdge=[list(v)for v in second[0]]))
 if len(patches)!=4 or sorted(f for p in patches for f in p['completeOriginalPatchFacetIds'])!=ids:return fail('incomplete-original-side-facet-partition')
 opposite=[]
 for i in range(4):
  for j in range(i+1,4):
   if set(map(tuple,patches[i]['firstOriginalBoundaryEdge'])).isdisjoint(map(tuple,patches[j]['firstOriginalBoundaryEdge'])):opposite.append([i,j])
 if len(opposite)!=2:return fail('not-two-complete-opposite-side-pairs')
 return dict(**{k:v for k,v in out.items()if k!='verifiedCompleteFourSidePatchPartition'},verifiedCompleteFourSidePatchPartition=True,completeOriginalBoundaryLoops=[[[list(v)for v in e]for e in g]for g in groups],completeOriginalCornerRails=rail_records,allFourCompleteOriginalSidePatches=patches,completeOppositePatchPairs=opposite,noClosingFaceFabricated=True)
