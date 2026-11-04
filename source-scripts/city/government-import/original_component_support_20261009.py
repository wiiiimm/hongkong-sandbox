"""Typed unchanged-original component support graph, not full acceptance.

The caller must independently re-decode/pin the source and support bytes, verify
current identity, and supply fresh strict anchor-interface measurements. Complete
terrain, neighbour, budget, browser and guarded publication gates are unchanged.
"""
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points

POLICY='original-source-complete-attached-component-support-v1'

def verify(triangles,components,interfaces,attachments):
    tri=np.asarray(triangles,dtype=float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
    assert len(components)==len(interfaces)>0
    membership={}
    for component,faces in enumerate(components):
        assert faces and all(type(i) is int and 0<=i<len(tri) for i in faces)
        assert len(set(faces))==len(faces)
        for i in faces:
            assert i not in membership,'Duplicate original face ownership'
            membership[i]=component
        # Explicit components must be connected by exact authored edges.
        remaining=set(faces);edges={};adjacency={i:set() for i in faces}
        for i in faces:
            f=[tuple(v) for v in tri[i]]
            for a,b in zip(f,f[1:]+f[:1]):
                key=tuple(sorted((a,b)))
                for j in edges.get(key,[]):adjacency[i].add(j);adjacency[j].add(i)
                edges.setdefault(key,[]).append(i)
        pending=[remaining.pop()]
        while pending:
            for j in adjacency[pending.pop()]&remaining:remaining.remove(j);pending.append(j)
        assert not remaining,'Declared component is disconnected'
    assert set(membership)==set(range(len(tri))),'Incomplete original face ownership'
    anchors=[];reasons=[]
    for i,proof in enumerate(interfaces):
        # A favourable boolean cannot hide failed samples or embedding resolutions.
        if proof.get('passed'):
            low=proof['strictLowRim']
            assert proof['samples']>0 and proof['strictContacts']==proof['samples']
            assert low['samples']==proof['samples']==low['contacts']
            assert not low['failed'] and low['missing']==0 and not proof['unresolved']
            assert low['minimumGap']==-.1 and low['maximumGap']==1
            assert np.isfinite([low['minGap'],low['maxGap']]).all()
            assert -.1<=low['minGap']<=low['maxGap']<=1
            assert proof['wallIntersections']==0
            if low['minGap']<=.1:anchors.append(i)
    if not anchors:reasons.append('no-complete-strict-original-anchor')
    resolved=set(anchors);verified=[]
    for row in attachments:
        i=row['component'];j=row['anchorComponent']
        assert type(i) is int and type(j) is int and 0<=i<len(components) and j in anchors and i!=j
        a,b=row['sourceFace'],row['anchorFace']
        assert type(a) is int and type(b) is int and membership[a]==i and membership[b]==j
        points=intersection_points(rational_face(tri[a]),rational_face(tri[b]))
        # A single corner kiss cannot establish an attached original appendage.
        if len(points)<2:
            reasons.append('no-positive-length-original-contact:'+str(i));continue
        resolved.add(i);verified.append({'component':i,'anchorComponent':j,'sourceFace':a,'anchorFace':b,
            'exactContactPoints':[[str(v) for v in p] for p in sorted(points)]})
    reasons += ['unresolved-original-component:'+str(i) for i in sorted(set(range(len(components)))-resolved)]
    return {'policy':POLICY,'supportInterfaceAccepted':not reasons,'reasons':sorted(set(reasons)),
        'sourceFaces':len(tri),'completeFaceAccounting':True,'anchorComponents':anchors,
        'componentCount':len(components),'verifiedAttachments':verified,'geometryChanges':0,
        'fullAcceptance':False,'publication':False,
        'qualification':'Every original component either has complete strict podium contact or positive-length exact authored surface contact with such an anchor. Original source/root/identity and all-surface terrain, independent foundation semantics, neighbours, runtime and publication are separate mandatory gates. No component is removed or called decorative; this is visual source assembly support, not structural engineering certification.'}
