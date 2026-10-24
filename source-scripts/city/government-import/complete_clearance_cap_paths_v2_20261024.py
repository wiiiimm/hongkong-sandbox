"""Exact shared-edge wall paths using a complete externally proven clearance partition.

No numerical minimum is invented for clear faces. This is source connectivity
and cap-clearance evidence only, never a ground root or physical-role approval.
"""
from collections import defaultdict,deque
import numpy as np
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points
from exact_original_shell_intersections_20261009 import rational_face
from exact_original_component_contacts_20261009 import contact_measure


def verify(triangles, negative_faces, contacts=()):
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
    verified_contacts=[];seen=set()
    for pair in contacts:
        assert len(pair)==2 and all(type(i)is int and 0<=i<len(tri)for i in pair)
        i,j=pair;assert i!=j and i in real and j in real;key=tuple(sorted(pair));assert key not in seen;seen.add(key)
        points=finite_intersection_points(rational_face(tri[i]),rational_face(tri[j]));measured=contact_measure(points);assert measured['dimension']>0,'Point-only or detached contact cannot bridge'
        credited=i in eligible and j in eligible
        if credited:adj[i].add(j);adj[j].add(i)
        verified_contacts.append(dict(sourceFaces=[i,j],credited=credited,**measured))
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
    return dict(contract='complete-clearance-partition-original-positive-contact-cap-paths-v2',completeSourceFaces=len(tri),recomputedPositiveFiniteContacts=verified_contacts,negativeSourceFaces=negative,negativeNonWallFaces=sorted(bad-walls),nonrenderingSourceFaces=sorted(set(range(len(tri)))-real),paths=paths,allAffectedHavePaths=bool(paths) and not(bad-walls)and all(p['hasExactSharedEdgeClearCapPath']for p in paths),groundRootCredit=False,physicalAcceptance=False,installationApproved=False,sourceGeometryChanges=0,qualification='Every actual nonzero exact shared edge is matched by full represented endpoint coordinates; supplied additional real-surface contacts are independently recomputed and require positive finite dimension. Point-only/zero-length/collapsed facets never bridge. Only upward facets outside the externally proven negative partition are caps; no false scalar minimum, closed-solid assumption or architectural-role approval.')
