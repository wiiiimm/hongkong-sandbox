"""Whole original wall/clear-roof graph using exact positive-dimensional contacts.

This is source connectivity evidence only. Clearance, exposure, provider role,
whole foreign scope and independent physical acceptance remain separate gates.
"""
import collections,hashlib
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points

def contact_paths(triangles,contexts,affected_faces,*,expected_source_binding,current_source_binding,heartbeat=None):
 tri=np.asarray(triangles,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
 assert expected_source_binding==current_source_binding and current_source_binding
 for key in ['sourceSHA256','positionTriangleStreamSHA256','normalTriangleStreamSHA256','colourTriangleStreamSHA256','rootMatrix','drawnGroundSHA256']:
  assert key in current_source_binding,'Missing original source/context binding '+key
 assert current_source_binding['decodedWorldTrianglesSHA256']==hashlib.sha256(tri.tobytes()).hexdigest()
 assert len(contexts)==len(tri) and [c['sourceFace'] for c in contexts]==list(range(len(tri)))
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);valid=length>0
 ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=valid)
 roofs={i for i,c in enumerate(contexts) if valid[i] and ratio[i]>.25 and c['groundProjectionCovered'] and c['minimum'] and c['minimum']['minimumGapM']>=-.5}
 walls=set(np.flatnonzero(valid&(np.abs(ratio)<=.25)).tolist());nodes=sorted(walls|roofs);affected=set(affected_faces);assert affected.issubset(walls)
 # Every original component remains inventoried; only eligible original wall /
 # clear upward roof faces can act as graph nodes. Collapsed faces never bridge.
 edges={};adj={i:set() for i in nodes}
 for i in nodes:
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
   key=tuple(sorted([tuple(a),tuple(b)]));edges.setdefault(key,[]).append(i)
 for faces in edges.values():
  for i in faces:adj[i].update(j for j in faces if j!=i)
 lo=tri.min(axis=1);hi=tri.max(axis=1);isnode=np.zeros(len(tri),bool);isnode[nodes]=True;contacts=[];rational={};pair_count=0;vertex_only=0;shared_pairs=0
 def face(i):
  if i not in rational:rational[i]=rational_face(tri[i])
  return rational[i]
 for count,i in enumerate(nodes):
  if heartbeat and count%100==0:heartbeat(count,len(nodes))
  candidates=np.flatnonzero(isnode&np.all(hi>=lo[i],axis=1)&np.all(lo<=hi[i],axis=1));candidates=candidates[candidates>i]
  for value in candidates:
   j=int(value);pair_count+=1
   if j in adj[i]:shared_pairs+=1;continue
   points=intersection_points(face(i),face(j))
   if len(points)<=1:
    vertex_only+=bool(points);continue
   adj[i].add(j);adj[j].add(i)
   contacts.append({'originalFaces':[i,j],'exactIntersectionPoints':[[float(v) for v in p] for p in sorted(points)],'positiveDimension':True,'originalExactSharedFullEdge':False})
 previous={i:None for i in roofs};todo=collections.deque(sorted(roofs))
 while todo:
  i=todo.popleft()
  for j in sorted(adj[i]):
   if j not in previous and j in walls:previous[j]=i;todo.append(j)
 paths=[]
 for i in sorted(affected):
  path=[i]
  while path[-1] in previous and previous[path[-1]] is not None:path.append(previous[path[-1]])
  paths.append({'sourceFace':i,'originalWallContactRoofPath':path,'hasExactPositiveDimensionPathToClearRoof':path[-1] in roofs})
 return {'sourceBinding':current_source_binding,'completeOriginalFaceInventory':list(range(len(tri))),'collapsedOriginalFacesExcludedFromPaths':np.flatnonzero(~valid).tolist(),'eligibleWallFaces':sorted(walls),'clearOriginalRoofFaces':sorted(roofs),'completeEligibleAABBCandidatePairs':pair_count,'originalSharedFullEdgePairs':shared_pairs,'vertexOnlyContactsExcluded':vertex_only,'additionalExactOriginalContacts':contacts,'paths':paths,'allAffectedHaveExactContactRoofPaths':all(p['hasExactPositiveDimensionPathToClearRoof'] for p in paths),'sourceGeometryChanges':0,'installationApproved':False,'qualification':'Exact unchanged authored connectivity evidence only; no tolerance welding. Positive-length/area contacts bridge original walls to clear original roofs, never vertex-only contacts or downward/collapsed surfaces. Exposure/provider/current-ground/foreign/foundation/runtime/neighbour/browser gates remain separate.'}
