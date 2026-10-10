"""Four alternate Langham interfaces on independently exposed bounded paths.

Frozen baseline source-only diagnosis. Complete literal/explicit Float32 paths
are recomputed from actual coordinates, with exact positive-dimensional grade
and strictly exposed shared edges/facets. No complete native/body/root approval.
"""
from collections import defaultdict, deque
from fractions import Fraction as F
from pathlib import Path
import importlib.util, json, time, uuid
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_shell_intersections_20261009 import intersection_points, rational_face
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment_verify
from exact_original_face_conservative_clearance_v5_20261010 import verify as facet_verify
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261011-langham-four-alternate-current-native-exposed-paths-v1'
DOC = BASE / BATCH
PROBE = BASE / 'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011'
GRAPH = BASE / 'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
FINITE = BASE / 'xl-terrain-recovery-20261011-langham-original-literal-complete-current-finite-v1'
GRADE = BASE / 'xl-terrain-recovery-20261011-langham-native963-current-grade-diagnostic-v1'
PRIOR_PATHS = BASE / 'xl-terrain-recovery-20261011-langham-native963-bounded-exposed-paths-v1'
ACTUAL = BASE / 'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
CROSS = BASE / 'xl-terrain-recovery-20261011-langham-complete-original-cross-contacts-render-replay-v1'
OWN = 'landsd/79318:0'; NATIVE = 'landsd/224399:0'; TARGETS = (34, 781, 790, 947)
MODES = ('providerOriginal', 'actualLiteral', 'explicitLeftAssociatedF32ModelMatrix', 'explicitBalancedF32ModelMatrix')
def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
def exact_edge(edge):
    return [[str(F(float(v))) for v in point] for point in edge]
def strict(proof):
    return proof['groundProjectionCovered'] is True and F(proof['exactCertifiedLowerClearanceM']) > 0

def main():
    assert not DOC.exists()
    refs = [ref(Path(__file__))]
    for folder in (PROBE, GRAPH, FINITE, GRADE, PRIOR_PATHS, ACTUAL, CROSS):
        receipt = read(folder / 'result.json')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
        refs.extend(ref(folder / name) for name in ('result.json', 'diagnostic.json.gz') if (folder / name).is_file())
    geometry = HERE / 'local' / PROBE.name / 'runtime-geometry.json.gz'
    runtime = {r['uid']: r for r in read(geometry)['rows']}
    selection = {r['uid']: r for r in read(PROBE / 'selection.json.gz')['rows']}
    actual = {r['uid']: r for r in read(ACTUAL / 'actual-render-attributes.json.gz')['rows']}
    worlds = {mode: {} for mode in MODES}
    for uid, count in ((OWN, 18086), (NATIVE, 20260)):
        row = selection[uid]; r = runtime[uid]; a = actual[uid]
        assert row['uid'] == r['uid'] == a['uid'] == uid
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == r['sourceSHA256'] == a['sourceSHA256']
        index = np.asarray(r['index'], int).reshape(-1, 3)
        assert r['index'] == a['completeOriginalIndex']
        literal = np.asarray(r['position'], float).reshape(-1, 3)
        assert np.array_equal(literal, np.asarray(a['completeLiteralWorldPosition'], float).reshape(-1, 3))
        worlds['providerOriginal'][uid] = decode_original_world_triangles(asset.read_bytes())
        worlds['actualLiteral'][uid] = literal[index]
        worlds[MODES[2]][uid] = np.asarray(a['completeExplicitLeftAssociatedFloat32WorldPosition'], float).reshape(-1, 3)[index]
        worlds[MODES[3]][uid] = np.asarray(a['completeExplicitBalancedFloat32WorldPosition'], float).reshape(-1, 3)[index]
        assert all(worlds[mode][uid].shape == (count, 3, 3) and np.isfinite(worlds[mode][uid]).all() for mode in MODES)
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
    grades = read(GRADE / 'diagnostic.json.gz')
    grade_candidates = sorted(set(i for row in grades['rows'] for i in row['positiveDimensionalGradeFaces']))
    assert len(grade_candidates) == 11
    cross = read(CROSS / 'diagnostic.json.gz')
    candidates = {b: [] for b in TARGETS}
    for record in cross['completeOriginalContactInventoryReplayed']:
        b = record['ownedOriginalBody']
        if b in candidates and record['nativeOriginalBody'] == 963 and all(p['positiveDimensionalContact'] for p in record['independentRenderContacts']):
            n = record['nativeSourceFace']; a = record['ownedSourceFace']
            assert a in graph['components'][b]['globalOriginalFaces'] and n in body
            if n in eligible:
                candidates[b].append(dict(ownedBody=b, ownedFace=a, nativeFace=n, completeOriginalContactWitness=record))
    assert all(candidates[b] for b in TARGETS)
    helper_names = ('exact_packed_world_geometry_20261009.py', 'exact_original_shared_edge_component_census_v2_20261011.py', 'exact_original_shell_intersections_20261009.py', 'exact_original_component_contacts_20261009.py', 'exact_original_rational_interface_segment_clearance_20261011.py', 'exact_original_face_conservative_clearance_v5_20261010.py', 'exact_original_projection_coverage_v2_20261010.py', 'exact_original_projection_coverage_20261009.py', 'exact_original_closed_projection_intersection_20261010.py', 'exact_original_upper_ground_interfaces_20261009.py', 'original_bound_facet_wall_context_v3_20261010.py', 'original_bound_facet_wall_context_v2_20261010.py', 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    refs.extend(ref(p) for p in (geometry, PROBE / 'selection.json.gz', PROBE / 'historical-current-manifest.json', ACTUAL / 'actual-render-attributes.json.gz'))
    refs.extend(ref(HERE / name) for name in helper_names)
    claim = reservations.claim('langham-four-alternate-paths-' + str(uuid.uuid4()), ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok']; lease = claim['reservation']; last = time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic() - last >= 20:
            assert reservations.heartbeat(lease)['ok']; last = time.monotonic()
            print(json.dumps(dict(heartbeat=BATCH)), flush=True)
    try:
        rows = []
        for mode in MODES:
            world = worlds[mode][NATIVE]; owned = worlds[mode][OWN]
            cached_field = 'completeOriginal' if mode == MODES[0] else 'actualRendered' if mode == MODES[1] else None
            if cached_field:
                key = 'completeOriginalWorldSHA256' if cached_field == 'completeOriginal' else 'completeActualRenderedWorldSHA256'
                assert digest(world.tobytes()) == finite[key]
            proofs = {}
            def proof(i):
                if i not in proofs:
                    proofs[i] = old[i][cached_field] if cached_field else facet_verify(world[i], ground)
                    assert proofs[i]['sourceFaceSHA256'] == digest(world[i].tobytes())
                    assert proofs[i]['completeCurrentGroundSHA256'] == digest(ground.tobytes())
                    pulse()
                return proofs[i]
            roots = {}; grade_rows = []
            for i in grade_candidates:
                interfaces = exact_upper_ground_interfaces(world, [i], ground)
                exposure = best_original_vertex_exposure(world[i], ground)
                grade_rows.append(dict(nativeFace=i, completeOriginalGradeFacet=world[i].tolist(), exactUpperGroundInterfaces=interfaces, completeVertexExposure=exposure))
                if interfaces:
                    roots[i] = grade_rows[-1]
                pulse()
            edges = defaultdict(list)
            for i in body:
                if exact_nonrendering(world[i]):
                    continue
                for a, b in zip(world[i], np.roll(world[i], -1, axis=0)):
                    if tuple(a) != tuple(b):
                        edges[tuple(sorted((tuple(a), tuple(b))))].append(i)
            neighbours = defaultdict(list); first = []
            for edge, ids in sorted(edges.items()):
                for i in ids:
                    for j in ids:
                        if i == j:
                            continue
                        if i in eligible and j in eligible:
                            neighbours[i].append((j, edge))
                        elif i in roots and j in eligible:
                            first.append((i, j, edge))
            seeds = {}; parents = {}; first_proofs = []
            for i, j, edge in first:
                if j in parents:
                    continue
                p = segment_verify(exact_edge(edge), ground)
                if p['strictlyExposedWholePositiveInterface'] and strict(proof(j)):
                    parents[j] = (i, edge); seeds[j] = i
                    first_proofs.append(dict(gradeFace=i, strictFace=j, exactSharedEdge=exact_edge(edge), completeInterfaceExposure=p, completeStrictFacetProof=proof(j)))
                pulse()
            q = deque(sorted(parents))
            while q:
                i = q.popleft()
                for j, edge in sorted(neighbours[i]):
                    if j not in parents:
                        parents[j] = (i, edge); q.append(j)
            def path_to(n):
                path = []; seen = set(); cur = n
                while cur in parents:
                    assert cur not in seen; seen.add(cur)
                    prev, edge = parents[cur]
                    path.append((prev, cur, edge)); cur = prev
                return (cur, list(reversed(path))) if cur in roots and path else (None, [])
            selected = []
            for body_id in TARGETS:
                ranked = []
                for target in candidates[body_id]:
                    root, path = path_to(target['nativeFace'])
                    if path:
                        ranked.append((len(path), target['ownedFace'], target['nativeFace'], root, path, target))
                negatives = []; found = None
                for _, a, n, root, path, target in sorted(ranked, key=lambda p: p[:3]):
                    bad = [cur for _, cur, _ in path if not strict(proof(cur))]
                    contact = contact_measure(intersection_points(rational_face(owned[a]), rational_face(world[n])))
                    if bad or contact['dimension'] <= 0:
                        negatives.append(dict(ownedFace=a, nativeFace=n, unexposedPathFacets=bad, recomputedExactContact=contact)); continue
                    records = [dict(fromFace=prev, toFace=cur, exactSharedEdge=exact_edge(edge), completeStrictFacetProof=proof(cur)) for prev, cur, edge in path]
                    found = dict(**target, independentCurrentContact=contact, boundedGradeFace=root, completeGradeFacetProof=roots[root], completeStrictSharedEdgePath=records, allActualPathFacetsStrictlyExposed=True, allCurrentInterfacesPositiveDimensional=True, failedCandidatePathsPreserved=negatives)
                    break
                selected.append(found if found else dict(ownedBody=body_id, unresolved=True, failedCandidatePathsPreserved=negatives))
                print(json.dumps(dict(mode=mode, body=body_id, positive=found is not None, nativeFace=None if found is None else found['nativeFace'], pathLength=0 if found is None else len(found['completeStrictSharedEdgePath']))), flush=True)
            rows.append(dict(mode=mode, completeOwnedWorldSHA256=digest(owned.tobytes()), completeNativeWorldSHA256=digest(world.tobytes()), completeGroundSHA256=digest(ground.tobytes()), nativeOriginalBodyFaceInventory=body, actualGradeCandidates=grade_rows, selectedFirstExposedEdges=first_proofs, selectedBoundedAlternatePaths=selected, allFourAlternativesHaveStrictBoundedNativePaths=all(not p.get('unresolved', False) for p in selected), actualRecomputedBoundedFacetProofs=[dict(nativeFace=i, proof=p) for i, p in sorted(proofs.items())]))
            pulse(True)
        assert all(ref(ROOT[r['path']]) == r for r in refs)
        out = dict(uids=[OWN, NATIVE], rows=rows, completeAuthenticAllFourPositiveAlternativeCounts={b: len(candidates[b]) for b in TARGETS}, allFourAlternativesAllFourStreamsPositive=all(r['allFourAlternativesHaveStrictBoundedNativePaths'] for r in rows), originalSelectedFloat32FailuresPreserved=True, allOtherNative2859FailuresPreserved=ref(FINITE / 'diagnostic.json.gz'), literal565ExactNegativePreserved=True, frozenBaselineManifest=ref(PROBE / 'historical-current-manifest.json'), sourceOnlyFrozenCurrentBaseline=True, noFreshCurrentReacceptance=True, diagnosticOnly=True, nativeReacceptance=False, currentAcceptance=False, structuralRootCredit=False, sourceGeometryChanges=0, newlyInstalled=0, evidenceRefs=refs)
        save(DOC / 'diagnostic.json.gz', out); pulse(True)
        spec = importlib.util.spec_from_file_location('freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.freeze(BATCH, 'bounded-langham-four-alternate-original-literal-two-explicit-f32-strict-exposed-native-grade-path-diagnostic-v1', [ROOT[r['path']] for r in refs] + [DOC / 'diagnostic.json.gz'], dict(uids=[OWN, NATIVE], allFourAlternativesAllFourStreamsPositive=out['allFourAlternativesAllFourStreamsPositive'], diagnosticOnly=True, nativeReacceptance=False, currentAcceptance=False, newlyInstalled=0))
    finally:
        assert reservations.release(lease)['ok']
if __name__ == '__main__':
    main()
