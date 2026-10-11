"""Open exterior v2: retain/account zero-area originals without using them as wall/roof bridges."""
import collections
import numpy as np


def original_open_paths(triangles,face_context,affected_faces,component_faces,*,expected_binding,current_binding):
    assert expected_binding and expected_binding==current_binding,'Source or physical context binding changed'
    for key in ['sourceSHA256','rootMatrix','positionTriangleStreamSHA256','normalTriangleStreamSHA256',
                'colourTriangleStreamSHA256','decodedWorldTrianglesSHA256','drawnGroundSHA256']:
        assert key in expected_binding,'Missing original/context binding '+key
    tri=np.asarray(triangles,dtype=float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
    import hashlib
    assert hashlib.sha256(tri.tobytes()).hexdigest()==current_binding['decodedWorldTrianglesSHA256']
    members=set(component_faces);affected=set(affected_faces)
    assert members and members.issubset(range(len(tri))) and affected.issubset(members)
    assert len(face_context)==len(tri)
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1)
    valid=length>0;ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=valid)
    # Collapsed original faces remain in the inventory but cannot bridge roles.
    members=members & set(np.flatnonzero(valid).tolist())
    assert affected.issubset(members),'Collapsed face cannot receive wall role'
    edges={}
    for i in sorted(members):
        for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
            aa,bb=tuple(a),tuple(b);key=tuple(sorted([aa,bb]))
            edges.setdefault(key,[]).append((i,aa==key[0]))
    adjacency={i:set() for i in members}
    conflicts=[]
    for key,items in edges.items():
        for i,_ in items:adjacency[i].update(j for j,_ in items if i!=j)
        if len(items)==2 and items[0][1]==items[1][1]:conflicts.append({'faces':[i for i,_ in items],'edge':list(key)})
    roofs={i for i in members if ratio[i]>.25 and face_context[i]['groundProjectionCovered']
           and face_context[i]['minimum'] and face_context[i]['minimum']['minimumGapM']>=-.5}
    previous={i:None for i in roofs};todo=collections.deque(sorted(roofs))
    while todo:
        i=todo.popleft()
        for j in sorted(adjacency[i]):
            if j not in previous and abs(ratio[j])<=.25:previous[j]=i;todo.append(j)
    results=[]
    for i in sorted(affected):
        context=face_context[i];path=[i]
        while path[-1] in previous and previous[path[-1]] is not None:path.append(previous[path[-1]])
        reasons=[]
        if abs(ratio[i])>.25:reasons.append('affected-face-is-not-wall')
        if not context['groundProjectionCovered']:reasons.append('ground-projection-incomplete')
        if not context['minimum'] or context['minimum']['minimumGapM']>=0:reasons.append('no-below-ground-witness')
        if context['maximumObservedGapM'] is None or context['maximumObservedGapM']<=0:reasons.append('no-exposed-wall-witness')
        if path[-1] not in roofs:reasons.append('no-original-geometric-edge-path-to-clear-upward-roof')
        results.append({'sourceFace':i,'wallToRoofPath':path,'reasons':reasons,'verifiedRoleNecessaryConditions':not reasons})
    return {'faces':results,'allAffectedWallsHaveRoles':all(not r['reasons'] for r in results),
            'originalOrientationConflicts':conflicts,'orientationConflictsPreserved':True,
            'sourceAndPhysicalBindings':current_binding,'roofFaces':sorted(roofs),
            'originalComponentFaces':sorted(component_faces),'collapsedOriginalFacesExcludedFromRolePaths':np.flatnonzero(~valid).tolist(),'closedSolidCertified':False,
            'geometryChanges':0,'installationApproved':False}
