"""Exact unchanged open vertical envelope census; never grants acceptance.

Recognizes only the complete, consistently wound triangulation of a simple
closed plan ring at two original heights. No inferred cap, weld or tolerance.
Ground/support/identity/current actors remain separate proofs.
"""
from collections import defaultdict
from fractions import Fraction
import numpy as np


def orient(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def intersects(a, b, c, d):
    o = [orient(a,b,c), orient(a,b,d), orient(c,d,a), orient(c,d,b)]
    if o[0]*o[1] < 0 and o[2]*o[3] < 0:
        return True
    def on(p, q, v):
        return (orient(p,q,v)==0 and all(min(p[k],q[k])<=v[k]<=max(p[k],q[k]) for k in range(2)))
    return on(a,b,c) or on(a,b,d) or on(c,d,a) or on(c,d,b)


def diagnose(triangles, face_ids):
    tri = np.asarray(triangles, dtype='<f8')
    assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
    assert face_ids and all(type(i) is int and 0<=i<len(tri) for i in face_ids)
    assert len(set(face_ids))==len(face_ids), 'Repeated original source face'
    faces=[tuple(tuple(Fraction(float(x)) for x in v) for v in tri[i]) for i in face_ids]
    heights=sorted({v[1] for f in faces for v in f})
    assert len(heights)==2 and heights[0]<heights[1], 'Not two exact original height levels'
    strips=defaultdict(list)
    directed=defaultdict(list)
    for i,face in zip(face_ids,faces):
        assert len(set(face))==3, 'Collapsed original face'
        xz=sorted({(v[0],v[2]) for v in face})
        assert len(xz)==2, 'Nonvertical original face or cap'
        strips[tuple(xz)].append((i,face))
        for a,b in zip(face,face[1:]+face[:1]):
            directed[tuple(sorted((a,b)))].append((a,b))
    adjacency=defaultdict(set)
    records=[]
    for (a,b),part in sorted(strips.items()):
        assert a!=b and len(part)==2, 'Missing or overlapping original strip faces'
        first,second=part[0][1],part[1][1]
        assert len(set(first)|set(second))==4 and len(set(first)&set(second))==2
        diagonal=list(set(first)&set(second))
        assert diagonal[0][1]!=diagonal[1][1] and (diagonal[0][0],diagonal[0][2])!=(diagonal[1][0],diagonal[1][2]), 'Shared edge is not rectangle diagonal'
        assert set(first)|set(second)=={(v[0],y,v[1]) for v in (a,b) for y in heights}
        adjacency[a].add(b);adjacency[b].add(a)
        records.append({'originalFaces':[p[0] for p in part], 'planEndpoints':[[str(x) for x in v] for v in (a,b)]})
    assert len(adjacency)>=3 and all(len(v)==2 for v in adjacency.values()), 'Open or branched plan ring'
    start=min(adjacency);ring=[start];previous=None;current=start
    while True:
        nxt=next(v for v in sorted(adjacency[current]) if v!=previous)
        if nxt==start:break
        assert nxt not in ring, 'Repeated plan ring vertex'
        ring.append(nxt);previous,current=current,nxt
    assert len(ring)==len(adjacency), 'Multiple disconnected original rings'
    edges=list(zip(ring,ring[1:]+ring[:1]))
    for i,(a,b) in enumerate(edges):
        for j,(c,d) in enumerate(edges[i+1:],i+1):
            if j==i+1 or (i==0 and j==len(edges)-1):continue
            assert not intersects(a,b,c,d), 'Self-intersecting original plan ring'
    signed=sum(a[0]*b[1]-a[1]*b[0] for a,b in edges)
    assert signed!=0, 'Zero enclosed plan area'
    boundaries=[]
    for edge,uses in directed.items():
        if len(uses)==2:
            assert uses[0]==tuple(reversed(uses[1])), 'Original winding conflicts'
        else:
            assert len(uses)==1 and edge[0][1]==edge[1][1], 'Unaccounted vertical/open/overlapping edge'
            boundaries.append(edge)
    assert len(boundaries)==2*len(ring)
    return {'contract':'exact-original-open-vertical-envelope-census-v1',
            'originalFaces':face_ids,'wholeComponentOriginalFacesAccounted':len(face_ids),
            'exactSimpleClosedPlan':[[str(x) for x in v] for v in ring],
            'exactOriginalHeightLevels':[str(v) for v in heights],
            'enclosedPlanAreaM2':float(abs(signed)/2),'completeOriginalStrips':records,
            'originalTopAndBottomOpenEdges':len(boundaries),
            'closedSolidCertified':False,'installationApproved':False,
            'sourceGeometryChanges':0,'diagnosticOnly':True,
            'qualification':'Uncapped original vertical envelope only; no architectural-purpose, ground/support, foreign-actor or runtime acceptance.'}
