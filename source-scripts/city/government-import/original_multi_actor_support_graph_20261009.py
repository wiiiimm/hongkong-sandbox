"""Complete unchanged original assembly contact graph rooted in actual ground.

This certifies visual assembly support, not structural engineering or any other
identity/foundation/terrain/foreign/runtime/publication gate.
"""
import hashlib, json, numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points

def verify(triangles,actors,components,ground_interfaces,contacts,*,expected_binding,current_binding):
    tri=np.asarray(triangles,float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
    assert expected_binding==current_binding and current_binding
    assert current_binding['completeOriginalWorldTrianglesSHA256']==hashlib.sha256(tri.tobytes()).hexdigest()
    assert current_binding['currentDrawnGroundSHA256'] and current_binding['groundInterfacesInputSHA256']
    assert current_binding['groundInterfacesSHA256']==hashlib.sha256(json.dumps(ground_interfaces,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    assert current_binding['supportScope']=='complete-current-drawn-ground-only'
    assert len(components)==len(ground_interfaces)>0
    actor_by_uid={a['uid']:a for a in actors};assert len(actor_by_uid)==len(actors)
    owner={};membership={};component_actor={}
    for actor in actors:
        start,end=actor['globalFaceRange'];assert type(start)is int and type(end)is int and 0<=start<end<=len(tri)
        assert actor['sourceSHA256'] and actor['originalStreamBindingSHA256']
        assert end-start==actor['completeOriginalFaceCount']
        assert hashlib.sha256(tri[start:end].tobytes()).hexdigest()==actor['originalWorldTrianglesSHA256']
        for i in range(start,end):assert i not in owner;owner[i]=actor['uid']
    assert set(owner)==set(range(len(tri))),'Omitted or repeated original actor faces'
    for k,component in enumerate(components):
        faces=component['globalOriginalFaces'];uid=component['actorUID'];assert uid in actor_by_uid and faces
        assert len(set(faces))==len(faces) and all(type(i)is int and owner.get(i)==uid for i in faces)
        edges={};adj={i:set() for i in faces}
        for i in faces:
            assert i not in membership;membership[i]=k
            f=[tuple(p) for p in tri[i]]
            for a,b in zip(f,f[1:]+f[:1]):
                edge=tuple(sorted((a,b)))
                for j in edges.get(edge,[]):adj[i].add(j);adj[j].add(i)
                edges.setdefault(edge,[]).append(i)
        remaining=set(faces);todo=[remaining.pop()]
        while todo:
            for j in adj[todo.pop()]&remaining:remaining.remove(j);todo.append(j)
        assert not remaining,'Original component contains detached faces'
        component_actor[k]=uid
    assert set(membership)==set(range(len(tri))),'Incomplete original component ownership'
    anchors=[]
    for k,proof in enumerate(ground_interfaces):
        if proof.get('passed'):
            low=proof['strictLowRim']
            assert proof['samples']>0 and proof['samples']==proof['strictContacts']==low['samples']==low['contacts']
            assert low['failed']==[] and low['missing']==0 and proof['unresolved']==[] and proof['wallIntersections']==0
            assert low['minimumGap']==-.1 and low['maximumGap']==1
            assert np.isfinite([low['minGap'],low['maxGap']]).all() and -.1<=low['minGap']<=low['maxGap']<=1
            if low['minGap']<=.1:anchors.append(k)
    adjacency={i:set() for i in range(len(components))};verified=[];seen=set()
    for contact in contacts:
        a,b=contact['components'];fa,fb=contact['globalOriginalFaces']
        assert type(a)is int and type(b)is int and a!=b and membership.get(fa)==a and membership.get(fb)==b
        pair=tuple(sorted((a,b)));assert pair not in seen;seen.add(pair)
        points=intersection_points(rational_face(tri[fa]),rational_face(tri[fb]))
        assert len(points)>=2,'No positive-dimensional original contact'
        adjacency[a].add(b);adjacency[b].add(a)
        verified.append({'components':[a,b],'actorUIDs':[component_actor[a],component_actor[b]],'globalOriginalFaces':[fa,fb],
            'exactContactPoints':[[str(v) for v in p] for p in sorted(points)]})
    reached=set(anchors);todo=list(anchors);parent={i:None for i in anchors}
    while todo:
        a=todo.pop()
        for b in sorted(adjacency[a]):
            if b not in reached:reached.add(b);parent[b]=a;todo.append(b)
    reasons=[] if anchors else ['no-genuine-complete-current-ground-anchor']
    reasons+=['unresolved-original-component:'+str(i) for i in sorted(set(adjacency)-reached)]
    return {'contract':'complete-unchanged-original-multi-actor-ground-anchored-support-v1',
        'supportInterfaceAccepted':not reasons,'reasons':reasons,'completeOriginalFaces':len(tri),
        'completeOriginalActorUIDs':sorted(actor_by_uid),'completeOriginalComponentCount':len(components),
        'genuineGroundAnchorComponents':anchors,'exactOriginalContacts':verified,
        'resolvedOriginalComponents':sorted(reached),'groundRootedComponentParents':parent,
        'sourceGeometryChanges':0,'fullAcceptance':False,'publication':False,
        'qualification':'Every exact original component is independently anchored to complete current drawn ground under unchanged strict rim/contact rules or reaches such an anchor by recomputed positive-dimensional original surface contacts. Every original actor and face retained; raw individual support/embedding failures stay separate. No closed-solid, decorative omission, structural engineering, identity, foundation, foreign actor, runtime or publication certification.'}
