"""Named actual P0 grade -> exposed source path -> original T4 interface.

Geometric source continuity only. No engineering, volume, point-root or legacy
podium reapproval. Uses already bound whole-facet clearance and the existing
exact rational segment kernel; source triangles and actual ground stay literal.
"""
from collections import defaultdict, deque
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment

T, P = 'landsd/184286:0', 'landsd/184285:0'

def positive(c):
    return c['dimension'] > 0 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2

def exact_point(p):
    return tuple(F(float(v)) for v in p)

def endpoints(c):
    points = [tuple(F(v) for v in p) for p in c['exactPoints']]
    assert c['dimension'] == 1 and len(points) >= 2
    return [min(points), max(points)]

def open_ascent(proof):
    """Every positive parameter is strictly exposed; t=0 is actual grade."""
    if not proof['closedWholeSegmentProjectionCovered']:
        return False
    touched_origin = False
    for piece in proof['allFinitePieces']:
        lo, hi = map(F, piece['exactParameterInterval'])
        if piece.get('collapsedProjectionConservative'):
            gap = F(piece['exactMinimumGapM'])
            if gap < 0 or (gap == 0 and hi > 0):
                return False
            continue
        values = [F(p[1]) - F(h) for p, h in zip(
            piece['exactEndpointSourcePoints'], piece['exactEndpointGroundHeights'])]
        for parameter, gap in zip([lo, hi], values):
            if gap < 0 or (parameter > 0 and gap <= 0):
                return False
            if parameter == 0 and gap == 0:
                touched_origin = True
    return touched_origin

def verify(*, world, ground, parts, grade_records, cross_records, finite_row):
    w = np.asarray(world, dtype='<f8'); g = np.asarray(ground, dtype='<f8')
    sha = lambda a: hashlib.sha256(a.tobytes()).hexdigest()
    assert w.shape == (3844, 3, 3) and g.shape == (517, 3, 3)
    assert np.isfinite(w).all() and np.isfinite(g).all()
    assert len(parts) == 34 and sorted(i for p in parts for i in p) == list(range(3844))
    assert finite_row['uid'] == P and finite_row['completeWholeWorldSHA256'] == sha(w)
    assert finite_row['completeCurrentGroundSHA256'] == sha(g)
    assert finite_row['completeOriginalFaceCount'] == 3844 and finite_row['failedFacesRetained'] == []
    records = finite_row['completeOriginalFaceComparisons']
    assert [r['sourceFace'] for r in records] == list(range(3844))
    for i, r in enumerate(records):
        assert r['completeOriginalFacetSHA256'] == sha(w[i])
        assert r['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']
    own = set(parts[0]); assert len(own) == 2510
    grade = [c for c in grade_records if c['podiumComponent'] == 0 and positive(c)]
    cross = [c for c in cross_records if c['podiumComponent'] == 0 and c['towerComponent'] == 4 and positive(c)]
    assert len(grade) == 113 and len(cross) == 74
    assert all(c['sourceFaceA'] in own for c in grade)
    assert all(c['sourceFaceB'] in own for c in cross)
    edges = defaultdict(list)
    for face in sorted(own):
        vertices = [exact_point(p) for p in w[face]]
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            if a != b:
                edges[tuple(sorted([a, b]))].append(face)
    graph = defaultdict(list); edge_proofs = {}; cache = {}
    def clear_edge(edge, faces):
        key = tuple(edge)
        if key not in cache:
            strict_face = next((i for i in faces if
                records[i]['currentDrawnGroundComparison']['coarse']['groundProjectionCovered'] and
                F(records[i]['currentDrawnGroundComparison']['coarse']['exactCertifiedLowerClearanceM']) > 0), None)
            if strict_face is not None:
                cache[key] = dict(strictlyExposedWholePositiveInterface=True,
                    proof='exact shared edge of complete strictly clear finite source facet',
                    sourceFace=strict_face, completeSourceFacetSHA256=sha(w[strict_face]),
                    completeFiniteFacetProof=records[strict_face]['currentDrawnGroundComparison'])
            else:
                cache[key] = segment([[str(v) for v in p] for p in edge], g)
        return cache[key]
    for edge, faces in sorted(edges.items()):
        if len(faces) < 2:
            continue
        proof = clear_edge(edge, faces)
        if not proof['strictlyExposedWholePositiveInterface']:
            continue
        for a in faces:
            for b in faces:
                if a != b:
                    graph[a].append((b, edge)); edge_proofs[(a, b)] = proof
    starts = {}; by_face = defaultdict(list)
    for c in grade:
        by_face[c['sourceFaceA']].append(c)
    # Certify a literal positive ascent within the same authored triangle,
    # from a genuine rational ground intersection to an exposed shared edge.
    for face, contacts in sorted(by_face.items()):
        for neighbour, edge in graph[face]:
            midpoint = tuple((a + b) / 2 for a, b in zip(*edge))
            for contact in contacts:
                a, b = endpoints(contact); origin = tuple((x + y) / 2 for x, y in zip(a, b))
                if origin == midpoint:
                    continue
                proof = segment([[str(v) for v in p] for p in [origin, midpoint]], g)
                if open_ascent(proof):
                    starts[face] = dict(genuineGradeContact=contact,
                        completeOpenAscentProof=proof, exposedFirstSharedEdge=[[str(v) for v in p] for p in edge])
                    break
            if face in starts:
                break
    assert starts, 'No actual finite grade-to-exposed-source ascent'
    parent = {i: None for i in starts}; queue = deque(sorted(starts)); links = {}
    while queue:
        a = queue.popleft()
        for b, edge in graph[a]:
            if b not in parent:
                parent[b] = a; links[b] = edge; queue.append(b)
    candidates = [c for c in cross if c['sourceFaceB'] in parent]
    chosen = None
    for c in candidates:
        proof = segment([[str(v) for v in p] for p in endpoints(c)], g)
        if proof['strictlyExposedWholePositiveInterface']:
            chosen = (c, proof); break
    assert chosen, 'No reachable complete exposed original T4/P0 interface'
    contact, final = chosen; path = [contact['sourceFaceB']]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return dict(contract='heya-actual-P0-grade-exposed-source-to-T4-path-v1',
        completePodiumWorldSHA256=sha(w), completeDrawnGroundSHA256=sha(g),
        originalPodiumComponent=0, originalTowerComponent=4,
        completeGroundGradeInterfaces=113, completeT4P0Interfaces=74,
        genuineGradeToExposedAscent=starts[path[0]], podiumOriginalFacePath=path,
        completeStrictSharedEdges=[dict(sourceFaces=[a,b], exactEndpoints=[[str(v) for v in p] for p in links[b]],
            completeExposureProof=edge_proofs[(a,b)]) for a,b in zip(path,path[1:])],
        wholePositiveTowerPodiumContact=contact, completeTerminalInterfaceExposure=final,
        sourceGeometryChanges=0, terrainGeometryChanges=0,
        engineeringSupportCertified=False, loadBearingClaim=False,
        pointRootCredit=False, installedPodiumReapproved=False,
        currentAcceptance=False, installationApproved=False)
