"""Exact wall-skin connectivity to independently clear original wall facets.

This asks no horizontal-cap or closed-solid question. It supplies geometric
context only, not ground roots, strict foundation acceptance or publication.
"""
from collections import defaultdict,deque
import numpy as np

def wall_escape(triangles,component_ids,negative_ids,target_ids):
    tri=np.asarray(triangles,dtype='<f8');assert tri.ndim==3 and tri.shape[1:]==(3,3)and np.isfinite(tri).all()
    component=set(component_ids);negative=set(negative_ids);targets=set(target_ids)
    assert component and targets<=component&negative and all(type(i)is int and 0<=i<len(tri)for i in component|negative|targets)
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(normals,axis=1)
    assert all(size[i]>0 and abs(normals[i,1])<=.25*size[i]for i in component),'Every traversed original component facet must be wall-like'
    edges=defaultdict(list);graph={i:set()for i in component}
    for i in component:
        vertices=list(map(tuple,tri[i]))
        for a,b in zip(vertices,vertices[1:]+vertices[:1]):
            if a!=b:edges[tuple(sorted((a,b)))].append(i)
    for faces in edges.values():
        for i in faces:graph[i].update(j for j in faces if j!=i)
    terminals=component-negative;parents={i:None for i in sorted(terminals)};queue=deque(sorted(terminals))
    while queue:
        i=queue.popleft()
        for j in sorted(graph[i]):
            if j not in parents:parents[j]=i;queue.append(j)
    paths=[]
    for i in sorted(targets):
        path=[i]
        while path[-1]in parents and parents[path[-1]]is not None:path.append(parents[path[-1]])
        paths.append(dict(sourceFace=i,originalWallPath=path,reachesIndependentlyClearWall=path[-1]in terminals))
    return dict(componentFaceIds=sorted(component),clearOriginalWallFaces=sorted(terminals),paths=paths,allTargetsReachClearOriginalWalls=all(p['reachesIndependentlyClearWall']for p in paths),groundRootCredit=False,strictFoundationAccepted=False,physicalAcceptance=False,sourceGeometryChanges=0)
