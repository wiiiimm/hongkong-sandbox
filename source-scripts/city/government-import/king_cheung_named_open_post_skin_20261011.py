"""Named eight-face original post skin: exact lateral/grade rings, exposed upper rim.

Open authored ends are preserved. This certifies a bounded interpreted visual
post skin, never a closed volume, structural capacity or a canopy support edge.
The caller must bind whole source/current identity and actual four-stream bytes.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite

IDS = list(range(2803, 2811))
def point(p): return tuple(F.from_float(float(v)) for v in p)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def cycle(edges, *, nodes):
    adjacency=defaultdict(set)
    assert len(edges)==len(set(edges))==nodes
    for a,b in edges:
        assert a!=b; adjacency[a].add(b);adjacency[b].add(a)
    assert len(adjacency)==nodes and all(len(v)==2 for v in adjacency.values())
    start=min(adjacency);order=[start];prev=None;cur=start
    while True:
        nxt=min(x for x in adjacency[cur] if x!=prev)
        if nxt==start:break
        assert nxt not in order;order.append(nxt);prev,cur=cur,nxt
    assert len(order)==nodes
    assert len({p[1] for p in order})==1
    area=sum(a[0]*b[2]-b[0]*a[2] for a,b in zip(order,order[1:]+order[:1]))
    assert area!=0
    # All non-neighbour closed edges must be strictly disjoint in XZ.
    def orient(a,b,p):return (b[0]-a[0])*(p[2]-a[2])-(b[2]-a[2])*(p[0]-a[0])
    for i,(a,b) in enumerate(zip(order,order[1:]+order[:1])):
        for j,(c,d) in enumerate(zip(order,order[1:]+order[:1])):
            if j<=i or j in {(i-1)%nodes,(i+1)%nodes}:continue
            ab=[orient(a,b,c),orient(a,b,d)];cd=[orient(c,d,a),orient(c,d,b)]
            assert (ab[0]*ab[1]>0) or (cd[0]*cd[1]>0)
    return order

def verify(part, ground, *, source_face_ids, interpreted_role, expected_binding, current_binding):
    assert expected_binding==current_binding
    assert source_face_ids==IDS and interpreted_role=='King Cheung original ancillary isolated post43 lateral skin'
    t=np.asarray(part,dtype='<f8');g=np.asarray(ground,dtype='<f8')
    assert t.shape==(8,3,3) and g.ndim==3 and g.shape[1:]==(3,3) and len(g)>0 and np.isfinite(t).all() and np.isfinite(g).all()
    assert expected_binding==dict(completePartSHA256=hashlib.sha256(t.tobytes()).hexdigest(),completeGroundSHA256=hashlib.sha256(g.tobytes()).hexdigest())
    faces=[[point(p) for p in f] for f in t];edge_counts=Counter();face_edges=[]
    for f in faces:
        n=cross(tuple(f[1][k]-f[0][k] for k in range(3)),tuple(f[2][k]-f[0][k] for k in range(3)))
        assert any(n) and 16*n[1]*n[1]<=sum(v*v for v in n)
        edges={tuple(sorted((a,b))) for a,b in zip(f,f[1:]+f[:1])};assert len(edges)==3
        edge_counts.update(edges);face_edges.append(edges)
    assert Counter(edge_counts.values())=={1:8,2:8}
    heights=sorted({p[1] for f in faces for p in f});assert len(heights)==2
    lower,upper=heights
    boundaries=[e for e,count in edge_counts.items() if count==1]
    bottom=cycle([e for e in boundaries if e[0][1]==e[1][1]==lower],nodes=4)
    top=cycle([e for e in boundaries if e[0][1]==e[1][1]==upper],nodes=4)
    # All eight real facets belong to this one lateral shell, without point glue.
    seen={0};queue=[0]
    while queue:
        i=queue.pop()
        for j in range(8):
            if j not in seen and face_edges[i]&face_edges[j]:seen.add(j);queue.append(j)
    assert len(seen)==8
    grade=exact_finite_contacts(t,range(8),g,range(len(g)))
    assert grade['allPairsExamined'] and grade['sourceFacesOmitted']==0
    contacts=grade['contacts'];assert {c['sourceFaceA'] for c in contacts if c['dimension']==1}==set(range(8))
    assert all(c['dimension']==1 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and len(c['exactPoints'])==2 for c in contacts)
    grade_edges=sorted({tuple(sorted(tuple(tuple(F(v) for v in p) for p in c['exactPoints']))) for c in contacts})
    ring=cycle(grade_edges,nodes=8)
    assert lower<ring[0][1]<upper
    top_proofs=[]
    for a,b in zip(top,top[1:]+top[:1]):
        line=np.asarray([[float(v) for v in p] for p in [a,b,b]],dtype='<f8')
        proof=finite(line,g)
        assert proof['groundProjectionCovered'] and F(proof['exactCertifiedLowerClearanceM'])>0
        top_proofs.append(dict(completeUpperEdge=[list(map(str,a)),list(map(str,b))],completeFiniteClearance=proof))
    return dict(contract='King-Cheung-named-original-post43-open-lateral-skin-grade-ring-v1',completeOriginalFaceIds=IDS,
                completePartSHA256=expected_binding['completePartSHA256'],completeGroundSHA256=expected_binding['completeGroundSHA256'],
                completeOriginalFacets=8,completeOriginalUpperRing=[[str(v) for v in p] for p in top],completeOriginalLowerRing=[[str(v) for v in p] for p in bottom],
                genuineCompleteFiniteGradeContacts=grade,completeExactGradeRing=[[str(v) for v in p] for p in ring],completeUpperPerimeterProofs=top_proofs,
                everyLateralFaceCrossesActualGrade=True,wholeUpperPerimeterStrictlyExposed=True,openEndsPreserved=True,
                namedVisualSkinRoleProposed=True,closedSolidCertified=False,loadBearingClaim=False,canopySupportCredit=False,
                geometryChanges=0,fullCurrentAcceptance=False,installationApproved=False)
