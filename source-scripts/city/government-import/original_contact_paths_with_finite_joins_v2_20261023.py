"""Finite original-component joins; preserves source path height/residual gates."""
from collections import defaultdict,deque
from fractions import Fraction
import numpy as np
from pool_incident_wall_contacts_v1_20261017 import closest

def paths(t,report,joins):
 targets=report['targets'];assert len(targets)<=1000
 contacts=[c for c in report['proof']['contacts']if c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
 edges=defaultdict(list);adj=defaultdict(dict)
 for i,face in enumerate(t):
  if np.linalg.norm(np.cross(face[1]-face[0],face[2]-face[0]))==0:continue
  for x,y in [(0,1),(1,2),(2,0)]:
   edge=tuple(sorted((tuple(face[x]),tuple(face[y]))))
   if edge[0]!=edge[1]:edges[edge].append(i)
 for edge,ids in edges.items():
  for x in ids:
   for y in ids:
    if x!=y:adj[x][y]=edge
 # Only exact positive-dimensional contacts between nondegenerate source
 # faces may bridge components. Every contact point is replayed on both faces.
 for c in joins:
  assert c['dimension']>0 and c['primitiveDimensions']==[2,2]
  a,b=c['sourceFaceA'],c['sourceFaceB'];points=[tuple(float(Fraction(v))for v in p)for p in c['exactPoints']];low=min(points,key=lambda p:p[1])
  assert all(np.linalg.norm(closest(np.asarray(low),t[i])-low)<=.001 for i in [a,b])
  if b not in adj[a]or min(q[1]for q in adj[a][b])>low[1]:adj[a][b]=adj[b][a]=(low,low)
 endpoints=[(c,np.array([[float(Fraction(v))for v in q]for q in c['exactPoints']]).mean(0))for c in sorted(contacts,key=lambda c:-c['maximumSpanM'])]
 rows=[]
 for target in targets:
  start=np.asarray(target['witness']['position']);found=None
  for contact,end in sorted(endpoints,key=lambda pair: pair[0]['sourceFaceA'] not in target['incidentFaces']):
   ceiling=max(start[1],end[1]);terminal=contact['sourceFaceA'];queue=deque(target['incidentFaces']);previous={i:None for i in queue}
   while queue and terminal not in previous:
    x=queue.popleft()
    for y,edge in adj[x].items():
     if y not in previous and min(q[1]for q in edge)<=ceiling:previous[y]=x;queue.append(y)
   if terminal not in previous:continue
   ids=[];at=terminal
   while at is not None:ids.append(at);at=previous[at]
   ids.reverse();points=[start]
   for x,y in zip(ids,ids[1:]):
    low,high=map(np.asarray,adj[x][y]);assert min(low[1],high[1])<=ceiling
    if max(low[1],high[1])>ceiling:
     cut=low+(high-low)*((ceiling-low[1])/(high[1]-low[1]))
     if low[1]>ceiling:low=cut
     else:high=cut
    points.append((low+high)/2)
   points.append(end);errors=[float(np.linalg.norm(closest(q,t[f])-q))for i,f in enumerate(ids)for q in points[i:i+2]]
   if max(errors)>.001:continue
   maximum=float(max(q[1]for q in points));assert maximum<=ceiling+1e-9
   found=dict(faces=ids,continuousPath=[q.tolist()for q in points],maximumResidualM=max(errors),endpointHeightCeilingM=float(ceiling),maximumPathHeightM=maximum,withinEndpointHeight=True,contact=contact);break
  rows.append(dict(witness=target['witness'],incidentFaces=target['incidentFaces'],verifiedPath=found))
 return rows
