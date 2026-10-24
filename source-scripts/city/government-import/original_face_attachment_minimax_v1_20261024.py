"""Diagnostic minimum-height attachment paths, without endpoint-height admission.

This cannot approve support: paths above their endpoints are explicitly failures
of the existing height gate. Exact shared edges and authenticated finite joins
are the only graph edges; source triangles are never edited.
"""
from collections import defaultdict
from fractions import Fraction as F
import heapq
import numpy as np
from pool_incident_wall_contacts_v1_20261017 import closest


def attachment_paths(triangles, report, joins):
    tri=np.asarray(triangles,float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3)and np.isfinite(tri).all()
    renderable=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0
    edges=defaultdict(list);adj=defaultdict(dict)
    def link(a,b,point,height,kind):
        assert 0<=a<len(tri)and 0<=b<len(tri)and renderable[a]and renderable[b]
        assert all(np.linalg.norm(closest(np.asarray(point),tri[i])-point)<=.001 for i in [a,b])
        if b not in adj[a]or height<adj[a][b][0]:adj[a][b]=(height,point,kind);adj[b][a]=(height,point,kind)
    for i,t in enumerate(tri):
        if not renderable[i]:continue
        for x,y in [(0,1),(1,2),(2,0)]:
            edge=tuple(sorted((tuple(t[x]),tuple(t[y]))))
            if edge[0]!=edge[1]:edges[edge].append(i)
    for edge,ids in edges.items():
        point=min(edge,key=lambda p:p[1]);height=F(float(point[1]))
        for a in ids:
            for b in ids:
                if a!=b:link(a,b,np.asarray(point),height,'exact-shared-original-edge')
    for c in joins:
        assert c['dimension']>0 and c['primitiveDimensions']==[2,2]
        point=min(c['exactPoints'],key=lambda p:F(p[1]));link(c['sourceFaceA'],c['sourceFaceB'],np.array([float(F(v))for v in point]),F(point[1]),'authenticated-positive-finite-source-join')
    contacts=[c for c in report['proof']['contacts']if c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
    distances={};next_face={};terminals={};queue=[]
    for c in contacts:
        i=c['sourceFaceA'];assert renderable[i]
        p=min(c['exactPoints'],key=lambda p:F(p[1]));height=F(p[1]);point=np.array([float(F(v))for v in p])
        assert np.linalg.norm(closest(point,tri[i])-point)<=.001
        if i not in distances or height<distances[i]:
            distances[i]=height;next_face[i]=None;terminals[i]=(point,c);heapq.heappush(queue,(height,i))
    while queue:
        height,i=heapq.heappop(queue)
        if distances[i]!=height:continue
        for j,(edge_height,point,kind)in adj[i].items():
            proposed=max(height,edge_height)
            if j not in distances or proposed<distances[j]:
                distances[j]=proposed;next_face[j]=i;heapq.heappush(queue,(proposed,j))
    rows=[]
    for target in report['targets']:
        start=np.asarray(target['witness']['position']);incident=target['incidentFaces'];assert incident
        assert all(renderable[i]and np.linalg.norm(closest(start,tri[i])-start)<=.001 for i in incident)
        reached=[i for i in incident if i in distances]
        row=dict(witness=target['witness'],incidentFaces=incident,hasUnrestrictedFiniteAttachment=bool(reached),supportApproved=False)
        if reached:
            i=min(reached,key=lambda i:max(F(float(start[1])),distances[i]));ceiling=max(F(float(start[1])),distances[i]);faces=[i];points=[start];kinds=[]
            while next_face[i]is not None:
                j=next_face[i];_,point,kind=adj[i][j];points.append(point);faces.append(j);kinds.append(kind);i=j
            end,contact=terminals[i];points.append(end)
            residuals=[float(np.linalg.norm(closest(q,tri[f])-q))for k,f in enumerate(faces)for q in points[k:k+2]]
            assert max(residuals)<=.001
            endpoint=max(F(float(start[1])),min(F(p[1])for p in contact['exactPoints']));rise=max(F(0),ceiling-endpoint)
            row.update(faces=faces,continuousPath=[q.tolist()for q in points],transitionKinds=kinds,exactMinimumAttachmentCeilingM=str(ceiling),minimumAttachmentCeilingM=float(ceiling),endpointHeightCeilingM=float(endpoint),riseAboveEndpointsM=float(rise),passesExistingEndpointHeight=(rise==0),maximumResidualM=max(residuals),contact=contact)
        rows.append(row)
    return rows
