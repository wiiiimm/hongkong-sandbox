"""Measure attachment-path height barriers, never structural acceptance."""
from collections import defaultdict
import heapq
import numpy as np
from pool_incident_wall_contacts_v1_20261017 import closest


def adjacency(triangles,joins):
    t=np.asarray(triangles);valid=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>0;edges=defaultdict(list);adj=[{}for _ in t]
    for i in np.flatnonzero(valid):
        for a,b in [(0,1),(1,2),(2,0)]:
            edge=tuple(sorted([tuple(t[i,a]),tuple(t[i,b])]))
            if edge[0]!=edge[1]:edges[edge].append(int(i))
    def link(a,b,p):
        assert valid[a]and valid[b]
        assert max(np.linalg.norm(closest(np.asarray(p),t[i])-p)for i in [a,b])<=.001
        if b not in adj[a]or p[1]<adj[a][b][1]:adj[a][b]=adj[b][a]=tuple(p)
    for edge,ids in edges.items():
        p=min(edge,key=lambda q:q[1])
        for a in ids:
            for b in ids:
                if a!=b:link(a,b,p)
    for j in joins:
        assert j['dimension']>0 and j['primitiveDimensions']==[2,2]
        link(j['sourceFaceA'],j['sourceFaceB'],min(j['points'],key=lambda p:p[1]))
    return adj,valid


def minimum_barrier(t,adj,valid,start,incident,endpoints):
    start=np.asarray(start);cost={int(i):float(start[1])for i in incident if valid[i]};previous={i:None for i in cost};queue=[(c,i)for i,c in cost.items()];heapq.heapify(queue)
    while queue:
        c,a=heapq.heappop(queue)
        if c!=cost[a]:continue
        for b,p in adj[a].items():
            nextcost=max(c,p[1])
            if nextcost<cost.get(b,float('inf')):cost[b]=nextcost;previous[b]=a;heapq.heappush(queue,(nextcost,b))
    candidates=[]
    for end in endpoints:
        face=end['sourceFace'];p=np.asarray(end['point']);assert valid[face]
        if face not in cost:continue
        maximum=max(cost[face],float(p[1]));ceiling=max(float(start[1]),float(p[1]));candidates.append((maximum-ceiling,maximum,face,p,end))
    if not candidates:return None
    _,maximum,face,end,certificate=min(candidates,key=lambda x:(x[0],x[1],x[2]));ids=[];i=face
    while i is not None:ids.append(i);i=previous[i]
    ids.reverse();points=[start]+[np.asarray(adj[a][b])for a,b in zip(ids,ids[1:])]+[end]
    residual=max(float(np.linalg.norm(closest(p,t[f])-p))for k,f in enumerate(ids)for p in points[k:k+2]);assert residual<=.001
    ceiling=max(float(start[1]),float(end[1]));actual=max(float(p[1])for p in points);assert actual<=maximum+1e-9
    return dict(faces=ids,path=[p.tolist()for p in points],sourceContact=certificate,maximumPathHeightM=actual,ownEndpointHeightM=ceiling,minimumExcessOverOwnEndpointsM=maximum-ceiling,maximumSurfaceResidualM=residual,strictOwnEndpointHeightPassed=actual<=ceiling+1e-9,installationApproved=False)
