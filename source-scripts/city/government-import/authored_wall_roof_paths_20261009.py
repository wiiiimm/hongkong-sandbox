"""Necessary authored exterior wall role check, not installation acceptance."""
import collections
import numpy as np


def authored_paths(triangles, face_context, affected_faces, component_faces):
    tri=np.asarray(triangles,dtype=float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
    members=set(component_faces);affected=set(affected_faces)
    assert members and members.issubset(range(len(tri))) and affected.issubset(members)
    assert len(face_context)==len(tri)
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1)
    assert (length>0).all()
    ratio=normal[:,1]/length;edges={}
    for i in sorted(members):
        for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
            aa,bb=tuple(a),tuple(b);key=tuple(sorted([aa,bb]))
            edges.setdefault(key,[]).append((i,aa==key[0]))
    adjacency={i:set() for i in members}
    for items in edges.values():
        for i,direction in items:
            adjacency[i].update(j for j,other_direction in items if i!=j and direction!=other_direction)
    roofs={i for i in members if ratio[i]>.25 and face_context[i]['groundProjectionCovered']
           and face_context[i]['minimum'] and face_context[i]['minimum']['minimumGapM']>=-.5}
    predecessor={i:None for i in roofs};todo=collections.deque(sorted(roofs))
    while todo:
        i=todo.popleft()
        for j in sorted(adjacency[i]):
            if j not in predecessor and abs(ratio[j])<=.25:
                predecessor[j]=i;todo.append(j)
    results=[]
    for i in sorted(affected):
        context=face_context[i];path=[i]
        while path[-1] in predecessor and predecessor[path[-1]] is not None:
            path.append(predecessor[path[-1]])
        reasons=[]
        if abs(ratio[i])>.25:reasons.append('affected-face-is-not-wall')
        if not context['groundProjectionCovered']:reasons.append('ground-projection-incomplete')
        if not context['minimum'] or context['minimum']['minimumGapM']>=0:reasons.append('no-below-ground-witness')
        if context['maximumObservedGapM'] is None or context['maximumObservedGapM']<=0:reasons.append('no-exposed-wall-witness')
        if path[-1] not in roofs:reasons.append('no-opposed-original-edge-path-to-clear-upward-roof')
        results.append({'sourceFace':i,'wallToRoofPath':path,'reasons':reasons,'verifiedRoleNecessaryConditions':not reasons})
    return {'faces':results,'allAffectedWallsHaveRoles':all(not r['reasons'] for r in results),
            'roofFaces':sorted(roofs),'originalComponentFaces':sorted(members),
            'geometryChanges':0,'installationApproved':False,
            'qualification':'Necessary role evidence only. Source provenance/current context, complete component inventory, other original interfaces, independent support, neighbours and runtime remain mandatory.'}
