"""Narrow original column termination contract; never certifies a basement.

This checks complete source geometry and continuous ground evidence. Independent
identity, current neighbours, runtime, support and publication checks remain
mandatory. Raw strict clearance failures are returned unchanged alongside role
results. No source/root/ground modification or blanket clearance allowance.
"""
import hashlib
import json
from fractions import Fraction
import numpy as np
from original_shell_diagnostic_20261009 import shell_context
from exact_shell_context_accelerated_20261009 import shell_self_intersections
from exact_original_shell_intersections_20261009 import rational_face, intersection_points


def context_digest(contexts):
    return hashlib.sha256(json.dumps(contexts,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def column_role(triangles, ground, contexts, column_faces, *, expected_binding,
                current_binding, foreign_triangles=()):
    """Verify one complete outward source column and all its source interfaces.

    All other source faces must retain ordinary continuous clearance. This
    initial contract intentionally cannot approve multiple buried columns or
    the separately classified open wall body of Block 37.
    """
    tri=np.asarray(triangles,dtype=float);terrain=np.asarray(ground,dtype=float)
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
    assert terrain.ndim==3 and terrain.shape[1:]==(3,3) and len(terrain) and np.isfinite(terrain).all()
    assert expected_binding and current_binding==expected_binding,'Source/context binding changed'
    for k in ['sourceSHA256','rootMatrix','positionTriangleStreamSHA256','normalTriangleStreamSHA256',
              'colourTriangleStreamSHA256','decodedWorldTrianglesSHA256','decodedGroundTrianglesSHA256',
              'continuousFaceContextSHA256']:
        assert k in current_binding,'Missing immutable binding '+k
    assert hashlib.sha256(tri.tobytes()).hexdigest()==current_binding['decodedWorldTrianglesSHA256']
    assert hashlib.sha256(terrain.tobytes()).hexdigest()==current_binding['decodedGroundTrianglesSHA256']
    assert len(contexts)==len(tri) and context_digest(contexts)==current_binding['continuousFaceContextSHA256']
    assert [c['sourceFace'] for c in contexts]==list(range(len(tri))),'Incomplete original face inventory'
    ids=list(column_faces)
    assert ids and all(type(i) is int for i in ids) and len(ids)==len(set(ids))
    assert set(ids).issubset(range(len(tri)))
    shell=shell_context(tri,[ids[0]])
    assert shell['componentFaces']==sorted(ids),'Column selection omits or adds original component faces'
    reasons=[]
    if not shell['closedConsistentlyOriented'] or not shell['outwardPositiveVolume']:
        reasons.append('column-not-closed-outward-solid')
    certificate=shell_self_intersections(tri[sorted(ids)].tolist())
    if not certificate['selfIntersectionFree']:reasons.append('column-self-intersection')
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(n,axis=1)
    ratio=np.divide(n[:,1],length,out=np.zeros(len(tri)),where=length>0)
    members=set(ids);ordinary=set(range(len(tri)))-members
    raw=[i for i,c in enumerate(contexts) if c['minimum'] and c['minimum']['minimumGapM']<-.5]
    for i,c in enumerate(contexts):
        if not c['groundProjectionCovered'] or c['minimum'] is None:reasons.append('missing-ground-face:'+str(i));continue
        gap=c['minimum']['minimumGapM']
        if i in ordinary and gap<-.5:reasons.append('ordinary-clearance:'+str(i))
        if i in members:
            if ratio[i]>.25 and gap<-.5:reasons.append('buried-upward-column-face:'+str(i))
            if abs(ratio[i])<=.25 and gap<0 and (c['maximumObservedGapM'] is None or c['maximumObservedGapM']<=0):
                reasons.append('column-wall-without-exposed-termination:'+str(i))
    caps={i for i in ids if ratio[i]>.25 and contexts[i]['minimum'] and contexts[i]['minimum']['minimumGapM']>0}
    if not caps:reasons.append('no-clear-original-upward-cap')
    outside=sorted(ordinary);lo=tri[outside].min(axis=1);hi=tri[outside].max(axis=1)
    rational={};interfaces=[];cap_attachment=False
    for i in sorted(ids):
        a=rational_face(tri[i]);hits=np.flatnonzero(np.all(hi>=tri[i].min(axis=0),axis=1)&np.all(lo<=tri[i].max(axis=0),axis=1))
        for k in hits:
            j=outside[int(k)]
            if j not in rational:rational[j]=rational_face(tri[j])
            points=intersection_points(a,rational[j])
            if points:
                interfaces.append({'columnFace':i,'otherOriginalFace':j,'exactIntersectionPoints':[[str(v) for v in p] for p in sorted(points)]})
                if i in caps and len(points)>=2 and contexts[j]['minimum'] and contexts[j]['minimum']['minimumGapM']>=-.5:
                    cap_attachment=True
    if not cap_attachment:reasons.append('no-positive-length-original-cap-attachment-to-clear-exterior')
    # Foreign geometry receives no original-source role credit, even when clear.
    foreign=np.asarray(foreign_triangles,dtype=float)
    foreign_hits=[]
    if foreign.size:
        assert foreign.ndim==3 and foreign.shape[1:]==(3,3) and np.isfinite(foreign).all()
        flo=foreign.min(axis=1);fhi=foreign.max(axis=1)
        for i in sorted(ids):
            for j in np.flatnonzero(np.all(fhi>=tri[i].min(axis=0),axis=1)&np.all(flo<=tri[i].max(axis=0),axis=1)):
                if intersection_points(rational_face(tri[i]),rational_face(foreign[int(j)])):
                    foreign_hits.append([i,int(j)])
        if foreign_hits:reasons.append('foreign-column-intersection')
    return {'contract':'unchanged-closed-column-termination-v1','verifiedColumnRole':not reasons,
            'reasons':reasons,'wholeOriginalFaces':len(tri),'originalColumnFaces':sorted(ids),
            'ordinarySourceFaces':sorted(ordinary),'originalCapFaces':sorted(caps),'shell':shell,
            'selfIntersections':certificate,'allOriginalInterfaces':interfaces,'foreignIntersections':foreign_hits,
            'rawStrictBurialFaceFailures':raw,'sourceAndPhysicalBinding':current_binding,
            'sourceGeometryChanges':0,'basementCertified':False,'installationApproved':False,
            'independentPhysicalGatesStillRequired':True}
