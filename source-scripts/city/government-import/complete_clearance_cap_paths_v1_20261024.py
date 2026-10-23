"""Exact shared-edge wall paths using a complete externally proven clearance partition.

No numerical minimum is invented for clear faces. This is source connectivity
and cap-clearance evidence only, never a ground root or physical-role approval.
"""
from collections import defaultdict,deque
import numpy as np


def verify(triangles, negative_faces):
    tri=np.asarray(triangles,dtype=np.float64);assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
    negative=list(negative_faces);assert negative==sorted(set(negative)) and all(type(i)is int and 0<=i<len(tri)for i in negative)
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(normal,axis=1);real=set(map(int,np.flatnonzero(size>0)));walls={i for i in real if abs(normal[i,1])<=.25*size[i]};bad=set(negative)
    eligible=walls|(real-bad);caps={i for i in eligible if normal[i,1]>.25*size[i]};edges=defaultdict(list);adj={i:set()for i in eligible}
    for i in sorted(eligible):
        vertices=[tuple(p)for p in tri[i]]
        for a,b in zip(vertices,vertices[1:]+vertices[:1]):
            if a!=b:edges[tuple(sorted((a,b)))].append(i)
    for faces in edges.values():
        for i in faces:adj[i].update(j for j in faces if j!=i)
    parents={i:None for i in sorted(caps)};queue=deque(sorted(caps))
    while queue:
        i=queue.popleft()
        for j in sorted(adj[i]):
            if j not in parents:parents[j]=i;queue.append(j)
    paths=[]
    for i in sorted(bad&walls):
        path=[i]
        while path[-1]in parents and parents[path[-1]]is not None:path.append(parents[path[-1]])
        paths.append(dict(sourceFace=i,originalPath=path,hasExactSharedEdgeClearCapPath=path[-1]in caps))
    return dict(contract='complete-clearance-partition-original-shared-edge-cap-paths-v1',completeSourceFaces=len(tri),negativeSourceFaces=negative,negativeNonWallFaces=sorted(bad-walls),nonrenderingSourceFaces=sorted(set(range(len(tri)))-real),paths=paths,allAffectedHavePaths=bool(paths) and not(bad-walls)and all(p['hasExactSharedEdgeClearCapPath']for p in paths),groundRootCredit=False,physicalAcceptance=False,installationApproved=False,sourceGeometryChanges=0,qualification='Every actual nonzero exact shared edge is matched by full represented endpoint coordinates. Point-only/zero-length/collapsed facets never bridge. Only upward facets outside the externally proven negative partition are caps; no false scalar minimum, closed-solid assumption or architectural-role approval.')
