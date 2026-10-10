"""Complete the three unchanged Langham interfaces on bounded exposed paths.

Source-only frozen baseline. Reuse is limited to exact Neon-fenced grade,
first-edge and whole-facet proofs matching every world/ground/kernel SHA.
Every selected shared edge and upper interface is independently reconstructed.
No structural/native/current acceptance or source/terrain modifications.
"""
from collections import defaultdict, deque
from fractions import Fraction as F
from pathlib import Path
import importlib.util, time, uuid
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_shell_intersections_20261009 import intersection_points, rational_face
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_face_conservative_clearance_v5_20261010 import verify as facet_verify
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261011-langham-three-remaining-four-stream-exposed-paths-v1'
DOC = BASE / BATCH
PROBE = BASE / 'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011'
GRAPH = BASE / 'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
FINITE = BASE / 'xl-terrain-recovery-20261011-langham-original-literal-complete-current-finite-v1'
PRIOR = BASE / 'xl-terrain-recovery-20261011-langham-native963-bounded-exposed-paths-v1'
ACTUAL = BASE / 'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
ALT = BASE / 'xl-terrain-recovery-20261011-langham-four-alternate-current-native-exposed-paths-v2'
OWN = 'landsd/79318:0'; NATIVE = 'landsd/224399:0'; TARGETS = (33, 787, 788)
MODES = ('providerOriginal', 'actualLiteral', 'explicitLeftAssociatedF32ModelMatrix', 'explicitBalancedF32ModelMatrix')
def ref(p): return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
def strict(p): return p['groundProjectionCovered'] is True and F(p['exactCertifiedLowerClearanceM']) > 0

def main():
    assert not DOC.exists()
    refs = [ref(Path(__file__))]
    receipts = {}
    for folder in (PROBE, GRAPH, FINITE, PRIOR, ACTUAL, ALT):
        receipt = read(folder / 'result.json')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
        bound = {r['path']: r for r in receipt['evidenceRefs']}
        for name in ('diagnostic.json.gz',):
            p = folder / name
            if p.is_file():
                assert bound[str(p.relative_to(ROOT))] == ref(p)
        receipts[folder] = bound
        refs.extend(ref(folder / name) for name in ('result.json', 'diagnostic.json.gz') if (folder / name).is_file())
    geometry = HERE / 'local' / PROBE.name / 'runtime-geometry.json.gz'
    captured = ACTUAL / 'actual-render-attributes.json.gz'
    assert receipts[PROBE][str(geometry.relative_to(ROOT))] == ref(geometry)
    assert receipts[ACTUAL][str(captured.relative_to(ROOT))] == ref(captured)
    runtime = {r['uid']: r for r in read(geometry)['rows']}
    selection = {r['uid']: r for r in read(PROBE / 'selection.json.gz')['rows']}
    actual = {r['uid']: r for r in read(captured)['rows']}
    worlds = {m: {} for m in MODES}
    for uid, count in ((OWN, 18086), (NATIVE, 20260)):
        row = selection[uid]; r = runtime[uid]; a = actual[uid]
        assert row['uid'] == r['uid'] == a['uid'] == uid
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == r['sourceSHA256'] == a['sourceSHA256']
        assert receipts[PROBE][str(asset.relative_to(ROOT))] == ref(asset)
        index = np.asarray(r['index'], int).reshape(-1, 3)
        literal = np.asarray(r['position'], float).reshape(-1, 3)
        assert r['index'] == a['completeOriginalIndex'] and np.array_equal(literal, np.asarray(a['completeLiteralWorldPosition'], float).reshape(-1, 3))
        worlds[MODES[0]][uid] = decode_original_world_triangles(asset.read_bytes())
        worlds[MODES[1]][uid] = literal[index]
        worlds[MODES[2]][uid] = np.asarray(a['completeExplicitLeftAssociatedFloat32WorldPosition'], float).reshape(-1, 3)[index]
        worlds[MODES[3]][uid] = np.asarray(a['completeExplicitBalancedFloat32WorldPosition'], float).reshape(-1, 3)[index]
        assert all(worlds[m][uid].shape == (count, 3, 3) and np.isfinite(worlds[m][uid]).all() for m in MODES)
        refs.append(ref(asset))
    ground = np.asarray(runtime[NATIVE]['drawnGroundGeometry'], float).reshape(-1, 3, 3)
    graph = read(GRAPH / 'diagnostic.json.gz')
    body = [i - 18086 for i in graph['components'][963]['globalOriginalFaces']]
    assert len(body) == 2385 and graph['components'][963]['actorUID'] == NATIVE
    finite = next(r for r in read(FINITE / 'diagnostic.json.gz')['rows'] if r['uid'] == NATIVE)
    assert finite['completeGroundSHA256'] == digest(ground.tobytes())
    old = {r['sourceFace']: r for r in finite['allFaces']}
    eligible = {i for i in body if strict(old[i]['completeOriginal']) and strict(old[i]['actualRendered'])}
    assert len(eligible) == 2373
    previous = read(PRIOR / 'diagnostic.json.gz')
    target_rows = next(r for r in previous['rows'] if r['mode'] == MODES[0])['boundedParticipatingPaths']
    targets = [{k: p[k] for k in ('ownedBody', 'ownedFace', 'nativeFace', 'originalWitness')} for p in target_rows if p['ownedBody'] in TARGETS]
    assert len(targets) == 3 and {p['ownedBody'] for p in targets} == set(TARGETS)
    assert all(p['nativeFace'] in eligible and p['ownedFace'] in graph['components'][p['ownedBody']]['globalOriginalFaces'] for p in targets)
    prior = read(ALT / 'diagnostic.json.gz'); alt_rows = {r['mode']: r for r in prior['rows']}
    assert set(alt_rows) == set(MODES) and prior['allFourAlternativesAllFourStreamsPositive'] is True
    helpers = ('exact_packed_world_geometry_20261009.py', 'exact_original_shared_edge_component_census_v2_20261011.py', 'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py', 'exact_original_rational_interface_segment_clearance_20261011.py', 'exact_original_face_conservative_clearance_v5_20261010.py', 'exact_original_projection_coverage_v2_20261010.py', 'exact_original_projection_coverage_20261009.py', 'exact_original_closed_projection_intersection_20261010.py', 'exact_original_upper_ground_interfaces_20261009.py', 'original_bound_facet_wall_context_v3_20261010.py', 'original_bound_facet_wall_context_v2_20261010.py', 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    for name in helpers:
        r = ref(HERE / name)
        assert receipts[ALT][r['path']] == r
        refs.append(r)
    refs.extend(ref(p) for p in (geometry, captured, PROBE / 'selection.json.gz', PROBE / 'historical-current-manifest.json'))
    assert receipts[PROBE][str((PROBE / 'selection.json.gz').relative_to(ROOT))] == ref(PROBE / 'selection.json.gz')
    claim = reservations.claim('langham-three-remaining-paths-' + str(uuid.uuid4()), ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok']; lease = claim['reservation']; last = time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic() - last >= 20:
            assert reservations.heartbeat(lease)['ok']; last = time.monotonic()
            print(dict(heartbeat=BATCH), flush=True)
    try:
        rows = []
        for mode in MODES:
            owned = worlds[mode][OWN]; world = worlds[mode][NATIVE]; cached = alt_rows[mode]
            assert (cached['completeOwnedWorldSHA256'], cached['completeNativeWorldSHA256'], cached['completeGroundSHA256']) == (digest(owned.tobytes()), digest(world.tobytes()), digest(ground.tobytes()))
            field = 'completeOriginal' if mode == MODES[0] else 'actualRendered' if mode == MODES[1] else None
            proofs = {r['nativeFace']: r['proof'] for r in cached['actualRecomputedBoundedFacetProofs']}
            reused = set(proofs); new_ids = set()
            def proof(i):
                if i not in proofs:
                    proofs[i] = old[i][field] if field else facet_verify(world[i], ground)
                    new_ids.add(i); pulse()
                p = proofs[i]
                assert p['sourceFaceSHA256'] == digest(world[i].tobytes()) and p['completeCurrentGroundSHA256'] == digest(ground.tobytes())
                return p
            roots = {}
            for g in cached['actualGradeCandidates']:
                i = g['nativeFace']
                assert i in body and np.array_equal(np.asarray(g['completeOriginalGradeFacet'], float), world[i])
                if g['exactUpperGroundInterfaces']:
                    roots[i] = g
            assert len(roots) == 11
            edge_faces = defaultdict(set)
            for i in body:
                if exact_nonrendering(world[i]): continue
                for a, b in zip(world[i], np.roll(world[i], -1, axis=0)):
                    if tuple(a) != tuple(b): edge_faces[tuple(sorted((tuple(a), tuple(b))))].add(i)
            neighbours = defaultdict(list)
            for edge, ids in sorted(edge_faces.items()):
                for i in sorted(ids):
                    for j in sorted(ids):
                        if i != j and i in eligible and j in eligible: neighbours[i].append((j, edge))
            parents = {}; first_rows = []
            for p in cached['selectedFirstExposedEdges']:
                i, j = p['gradeFace'], p['strictFace']
                edge = tuple(tuple(float(F(v)) for v in point) for point in p['exactSharedEdge'])
                assert i in roots and j in eligible and {i, j} <= edge_faces[tuple(sorted(edge))]
                assert p['completeInterfaceExposure']['strictlyExposedWholePositiveInterface'] is True and strict(proof(j))
                assert proof(j) == p['completeStrictFacetProof']
                assert j not in parents
                parents[j] = (i, tuple(sorted(edge))); first_rows.append(p)
            assert first_rows
            q = deque(sorted(parents))
            while q:
                i = q.popleft()
                for j, edge in sorted(neighbours[i]):
                    if j not in parents: parents[j] = (i, edge); q.append(j)
            selected = []
            for target in targets:
                cur = target['nativeFace']; path = []; seen = set()
                while cur in parents:
                    assert cur not in seen; seen.add(cur)
                    prev, edge = parents[cur]; path.append((prev, cur, edge)); cur = prev
                path.reverse(); positive_path = bool(path) and cur in roots
                p_rows = []
                for prev, i, edge in path:
                    assert {prev, i} <= edge_faces[edge]
                    p = proof(i); positive_path = positive_path and strict(p)
                    p_rows.append(dict(fromFace=prev, toFace=i, exactSharedEdge=[[str(F(v)) for v in point] for point in edge], completeStrictFacetProof=p))
                a, n = target['ownedFace'], target['nativeFace']
                pts = intersection_points(rational_face(owned[a]), rational_face(world[n]))
                contact = contact_measure(pts) if pts else dict(dimension=-1, exactPoints=[], maximumSpanM=0, bounds=None)
                result = dict(**target, boundedGradeFace=cur if path else None, completeGradeFacetProof=roots.get(cur), completeStrictSharedEdgePath=p_rows, recomputedExactOwnedContact=contact, allActualPathFacetsStrictlyExposed=positive_path, actualContactPositiveDimensional=contact['dimension'] > 0)
                selected.append(result)
                print(dict(mode=mode, body=target['ownedBody'], pathLength=len(path), allExposed=positive_path, contactDimension=contact['dimension']), flush=True); pulse()
            rows.append(dict(mode=mode, completeOwnedWorldSHA256=digest(owned.tobytes()), completeNativeWorldSHA256=digest(world.tobytes()), completeGroundSHA256=digest(ground.tobytes()), nativeOriginalBodyFaceInventory=body, exactFencedGradeAndFirstEdgeReuse=ref(ALT / 'diagnostic.json.gz'), selectedFirstExposedEdges=first_rows, threeRemainingBoundedParticipatingPaths=selected, allThreePathsAndContactsStrictPositive=all(p['allActualPathFacetsStrictlyExposed'] and p['actualContactPositiveDimensional'] for p in selected), exactReusedBoundedFacetIds=sorted(reused), newlyRequiredBoundedFacetProofs=[dict(nativeFace=i, proof=proofs[i]) for i in sorted(new_ids)])); pulse(True)
        assert all(ref(ROOT / r['path']) == r for r in refs)
        out = dict(uids=[OWN,NATIVE], rows=rows, allThreeRemainingPathsAllFourStreamsPositive=all(r['allThreePathsAndContactsStrictPositive'] for r in rows), allFourAlternatePathProof=ref(ALT / 'diagnostic.json.gz'), allOtherNative2859FailuresPreserved=ref(FINITE / 'diagnostic.json.gz'), literal565ExactNegativePreserved=True, frozenBaselineManifest=ref(PROBE / 'historical-current-manifest.json'), sourceOnlyFrozenCurrentBaseline=True, noFreshCurrentReacceptance=True, diagnosticOnly=True, nativeReacceptance=False, currentAcceptance=False, structuralRootCredit=False, sourceGeometryChanges=0, newlyInstalled=0, evidenceRefs=refs)
        save(DOC / 'diagnostic.json.gz', out); pulse(True)
        spec = importlib.util.spec_from_file_location('freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.freeze(BATCH, 'bounded-langham-three-remaining-original-literal-two-explicit-f32-strict-exposed-native-grade-path-diagnostic-v1', [ROOT / r['path'] for r in refs] + [DOC / 'diagnostic.json.gz'], dict(uids=[OWN,NATIVE], allThreeRemainingPathsAllFourStreamsPositive=out['allThreeRemainingPathsAllFourStreamsPositive'], diagnosticOnly=True, nativeReacceptance=False, currentAcceptance=False, newlyInstalled=0))
    finally:
        assert reservations.release(lease)['ok']
if __name__ == '__main__': main()
