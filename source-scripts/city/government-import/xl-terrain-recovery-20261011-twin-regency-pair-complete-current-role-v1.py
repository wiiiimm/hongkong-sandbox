"""Draft independently fenced Twin original-pair typed current qualification.

All original faces remain unchanged. Only genuine actual P1091 grade seeds the
827 nonvisual paths; 155 boundary-associated and 138 situated original visual
parts remain terminal and provide no mount/root/bridge/host credit. Completed
exact arithmetic is reused only after its full source/world/ground/file tuple
and completed Neon receipt are verified. Staged/live browser gates are separate.
Root full review is required before this canonical producer is executed.
"""
from pathlib import Path
import importlib.util
import json
import time
import uuid
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations, NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
from twin_regency1120_complete_actual_fixture_v1_20261011 import actual_fixture
import twin_regency1120_complete_original_role_composition_v1_20261011 as composition

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261011-twin-regency-pair-complete-current-role-v1'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
CURRENT = 'df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e'
UIDS = ['landsd/222465:0', 'landsd/223206:0']
COUNTS = [13063, 456]
SOURCES = composition.SOURCE_SHA
PHYSICAL = BASE / 'government-xl-terrain-recovery-twin-regency-pair-authentic-current-v1-20261011'
INPUT = BASE / 'xl-terrain-recovery-20261011-twin-regency-pair-current-inputs-v1'
CAPTURE = BASE / 'xl-terrain-recovery-20261011-twin-regency-two-current-render-attribute-capture-v1'
PROPOSED = BASE / 'government-xl-terrain-recovery-twin-regency-pair-proposed-ground-capture-v1-20261011'
NATIVE = BASE / 'xl-terrain-recovery-20261011-twin-regency-whole-terrain-domain-current6645-native-census-v1'
VALIDATION = BASE / 'xl-terrain-recovery-20261011-twin-regency1120-composition-validation-v1'
TERRAIN_SHA = 'f00e0dc6e588168dbb3ff69827b170c2a6beca41908bc7e556ea79e6b713a43e'
EXPECTED_RAW = [UIDS[0] + ':ground-contact-unresolved', UIDS[0] + ':sampled-ground-gap-below-model-bottom']
EXECUTED_CODE = {
    'twin_regency1120_complete_original_role_composition_v1_20261011.py': '7c69965cb44af17d030556214c2d72185110e77eab21a9bc0b80969866e7e03f',
    'twin_regency1120_complete_actual_fixture_v1_20261011.py': 'f0aab327e15df83a769426efb4e2f7f0e0e7b9525600477e9de145dea787323a',
    'test_twin_regency1120_complete_original_role_composition_v1_20261011.py': 'cd5ef368af3eaf5cd403761648ab4d8dd6dea41de4eff9663c9eb51173972310'}
TEST_LOG_SHA = '3dfb305d44c8960cb89a7773541835769eae9fa41ef72cf07fe8b8d1246acc0a'
EXIT_RECEIPT_SHA = '8721ab4df18b672576baa53797552d182feab4760c05036925b09cae2ec6d04f'

def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result

def pins_exact(refs):
    # No historical mutable-path alias or metadata exception is introduced here.
    unique = {}
    for pin in refs:
        if pin['path'] in unique: assert unique[pin['path']] == pin
        unique[pin['path']] = pin
        assert ref(ROOT / pin['path']) == pin
    return list(unique.values())

def completed(folder, refs, receipts, names=()):
    receipt = read(folder / 'result.json')
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    for name in names: assert ref(folder / name) in receipt['evidenceRefs']
    receipts[folder.name] = receipt
    refs.extend([ref(folder / 'result.json'), *receipt['evidenceRefs']])
    return receipt

def recheck(local=None, pulse=None):
    pulse = pulse or (lambda: None)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    start = ref(manifest); assert start['sha256'] == CURRENT
    current = read(manifest)
    refs = [start, ref(Path(__file__))]; receipts = {}
    for folder, names in [(PHYSICAL, ('selection.json.gz', 'metrics.json', 'foundation.json', 'validation.json', 'terrain-candidates.json', 'current-pair-physical-diagnostic.json')),
        (INPUT, ('check-selection.json.gz', 'context.json.gz')),
        (CAPTURE, ('actual-render-attributes.json.gz',)),
        (PROPOSED, ()), (NATIVE, ('diagnostic.json.gz',))]:
        completed(folder, refs, receipts, names)
    args, docs, fixture_refs, fixture_receipts = actual_fixture()
    refs.extend(fixture_refs)
    for name, receipt in fixture_receipts.items():
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
        receipts[name] = receipt; refs.extend(receipt['evidenceRefs'])
    validation = read(VALIDATION / 'validation.json')
    assert validation['passed'] is True and validation['actualAdverseTests'] == 16
    executed = {str((HERE / name).relative_to(ROOT)): sha for name, sha in EXECUTED_CODE.items()}
    assert validation['exactExecutedCodeSHA256'] == executed
    for path, sha in validation['exactExecutedCodeSHA256'].items(): assert ref(ROOT / path)['sha256'] == sha
    log_pin = ref(VALIDATION / 'actual-adverse-tests.log'); assert log_pin['sha256'] == TEST_LOG_SHA
    assert validation['evidenceRefs'] == [dict(path=path, sha256=sha) for path, sha in executed.items()] + [log_pin]
    log = (VALIDATION / 'actual-adverse-tests.log').read_text()
    assert log.count(' ... ok\n') == 16 and 'Ran 16 tests in 254.923s\n' in log and log.rstrip().endswith('\nOK')
    exit_pin = ref(VALIDATION / 'execution-exit-status.json'); assert exit_pin['sha256'] == EXIT_RECEIPT_SHA
    execution = read(VALIDATION / 'execution-exit-status.json')
    assert execution['observedFinalExecExitCode'] == 0 and execution['observedFinalExecCompletion'] is True
    assert execution['passed'] is True and execution['actualAdverseTests'] == 16
    assert execution['exactExecutedCodeSHA256'] == executed and execution['testLog'] == log_pin
    assert execution['command'] == ['/tmp/astra-city-venv/bin/python', '-m', 'unittest', 'test_twin_regency1120_complete_original_role_composition_v1_20261011', '-v']
    assert execution['workingDirectory'] == str(HERE.relative_to(ROOT)) and execution['execSessionId'] == 69164
    refs.extend([ref(VALIDATION / 'validation.json'), *validation['evidenceRefs']])
    refs.extend([exit_pin, *execution['evidenceRefs']])
    refs = pins_exact(refs); pulse()

    rows = read(PHYSICAL / 'selection.json.gz')['rows']
    assert read(PHYSICAL / 'selection.json.gz')['manifestSHA256'] == CURRENT
    contexts = {r['uid']: r for r in read(INPUT / 'context.json.gz')['rows']}
    runtime_path = HERE / 'local' / PROPOSED.name / 'runtime-geometry.json.gz'
    assert ref(runtime_path) in receipts[PROPOSED.name]['evidenceRefs']
    runtime_doc = read(runtime_path); runtime = runtime_doc['rows']
    attributes = read(CAPTURE / 'actual-render-attributes.json.gz')['rows']
    assert [r['uid'] for r in rows] == [r['uid'] for r in runtime] == [r['uid'] for r in attributes] == UIDS
    assert set(contexts) == set(UIDS)
    for path, sha in runtime_doc['inputHashes'].items(): assert ref(ROOT / path)['sha256'] == sha
    folder = Path(local) if local is not None else LOCAL / ('identity-recheck-' + str(uuid.uuid4()))
    assert folder.resolve().is_relative_to((HERE / 'local').resolve())
    worlds = {mode: [] for mode in composition.MODES}; grounds = {}; positions = []; streams = []; identities = []
    for number, (row, rt, actual, count) in enumerate(zip(rows, runtime, attributes, COUNTS)):
        uid = UIDS[number]
        assert row['uid'] == rt['uid'] == actual['uid'] == uid
        assert row['sourceSHA256'] == rt['sourceSHA256'] == actual['sourceSHA256'] == SOURCES[uid]
        asset = ROOT / row['candidate']['path']; raw = asset.read_bytes()
        assert digest(raw) == row['candidate']['entry']['sha256'] == SOURCES[uid]
        proof = packed_world_bounds(raw); assert proof == row['completeOriginalPOSITIONProof']
        assert proof['allOriginalPositionVerticesAccounted'] is True and proof['completeOriginalTriangles'] == count
        positions.append(proof); streams.append(source_stream_binding(raw)); refs.append(ref(asset))
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            assert connection.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchone() == (row['native']['resultSha'],)
        identity_folder = folder / ('exact-current-cell-' + uid.split('/')[1].replace(':', '-'))
        identity = verify_files(row, contexts[uid], identity_folder)
        assert identity['passed'] is True and identity['proof']['identityAccepted'] is True
        identities.append(identity)
        index = np.asarray(rt['index'], np.uint32).reshape(-1, 3)
        assert len(index) == count and rt['index'] == actual['completeOriginalIndex']
        assert np.array_equal(np.asarray(rt['position']), np.asarray(actual['completeLiteralWorldPosition']))
        worlds['providerOriginal'].append(decode_original_world_triangles(raw))
        for mode, field in zip(composition.MODES[1:], ['completeLiteralWorldPosition', 'completeExplicitLeftAssociatedFloat32WorldPosition', 'completeExplicitBalancedFloat32WorldPosition']):
            world_position = np.asarray(actual[field], float).reshape(-1, 3)
            assert len(world_position) == proof['completeOriginalPositionVertices'] and np.isfinite(world_position).all()
            worlds[mode].append(world_position[index])
        ground = np.asarray(rt['drawnGroundGeometry'], float).reshape(-1, 3, 3)
        assert np.isfinite(ground).all() and len(ground)
        grounds[uid] = composition.world_sha(ground)
        for mode in composition.MODES:
            finite = next(r for r in docs['finite']['rows'] if r['mode'] == mode and r['uid'] == uid)
            assert finite['completeActualDrawnGroundSHA256'] == grounds[uid]
        pulse()
    worlds = {mode: np.concatenate(parts) for mode, parts in worlds.items()}
    assert all(np.array_equal(worlds[mode], args['worlds'][mode]) for mode in composition.MODES)
    assert composition.binding(worlds, args['graph'], args['finite'], args['paths'], args['boundary155'], args['placement138']) == args['expected_binding']
    typed = composition.verify(**args); pulse()

    metrics_doc = read(PHYSICAL / 'metrics.json'); metrics = metrics_doc['rows']
    foundations = read(PHYSICAL / 'foundation.json')['rows']; checks = read(PHYSICAL / 'validation.json')
    assert [r['uid'] for r in metrics] == [r['uid'] for r in foundations] == UIDS
    assert [r['uid'] for r in checks['results']] == UIDS
    policy = module('twin_complete_current_ordinary_policy', 'acceptance-policy.py')
    actual_reasons = []
    for uid, count, metric, foundation, runtime_result, identity in zip(UIDS, COUNTS, metrics, foundations, checks['results'], identities):
        assert metric['sourceSHA256'] == foundation['sourceSHA256'] == SOURCES[uid]
        assert foundation['strictFoundationAccepted'] is True
        assert foundation['foundation']['completeTerrainTriangles'] == foundation['foundation']['triangles'] == count
        assert foundation['foundation']['fullyBuriedUpwardTriangles'] == 0
        assert metric['sourcePreserved'] is True and metric['missingTerrain'] == 0
        assert metric['missingDrawnTerrain']['count'] == metric['samplerDisagreement']['count'] == 0 and metric['maxSamplerDelta'] <= .004
        assert runtime_result['uid'] == uid and runtime_result['outcome'] == 'runtime-accepted-placement-unreviewed' and runtime_result['triangles'] == count
        actual_reasons.extend(uid + ':' + reason for reason in policy.reasons(dict(state='runtime-validated-awaiting-acceptance', sourceSHA256=SOURCES[uid], identityProof=identity['proof']), metric, metrics_doc['profiles']['mobile']))
        actual_reasons.extend(uid + ':' + reason for reason in runtime_result['concerns'])
    assert type(checks['models']) is int and checks['models'] == checks['loaderAccepted'] == checks['checksPassed'] == 2 and checks['exceptions'] == 0
    raw = read(PHYSICAL / 'current-pair-physical-diagnostic.json')
    assert sorted(set(actual_reasons)) == raw['rawReasons'] == EXPECTED_RAW
    assert typed['allFourStreamRows'] and all(18 in r['complete827NonvisualParents'] and r['genuineMainPodiumGradeSeed']['originalBody'] == 1091 for r in typed['allFourStreamRows'])
    neighbours = read(PHYSICAL / 'neighbour-checks.json'); neighbour_inputs = read(PHYSICAL / 'neighbour-inputs.json.gz')
    assert len(neighbours['rows']) == len(neighbour_inputs['rows']) == 107
    assert len({r['uid'] for r in neighbours['rows']}) == 107 and not any(r['reasons'] for r in neighbours['rows'])
    assert not any(r['existingNative'] for r in neighbour_inputs['rows'])
    assert {r['uid'] for r in neighbours['rows']} == {r['building']['uid'] for r in neighbour_inputs['rows']}
    assert 'landsd/223207:0' in {r['uid'] for r in neighbours['rows']}, 'Current original T1 BASIC foreign actor omitted'
    native_checks = read(PHYSICAL / 'native-neighbour-checks.json')
    assert native_checks['rows'] == native_checks['resolved'] == native_checks['blocked'] == []

    candidates = read(PHYSICAL / 'terrain-candidates.json')
    assert len(candidates) == 1 and candidates[0]['uids'] == UIDS and candidates[0]['sha256'] == TERRAIN_SHA and candidates[0]['triangles'] == 2513
    candidate = candidates[0]; assert 'replaces' not in candidate
    terrain_path = ROOT / candidate['path']; assert ref(terrain_path)['sha256'] == TERRAIN_SHA
    native = read(NATIVE / 'diagnostic.json.gz')
    assert native['currentManifest'] == start and native['completeCurrentNativeActors'] == 6645
    assert len(native['completeStrictlyDisjointActors']) == 6645 and native['fullFiniteRegressionNominations'] == []
    assert native['completeDeclaredTerrainBounds'] == candidate['bounds'] and native['nativeReacceptance'] is False
    tuples = {r['uid']: r for r in native['completeFreshCurrentEntrySourceFormModuleTuples']}
    assert len(tuples) == 6645
    entries = {}; catalogue_refs = []
    for url in current['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url; catalogue_refs.append(ref(path))
        for entry in read(path)['models']:
            assert entry['uid'] not in entries
            entries[entry['uid']] = (path, entry)
    assert set(entries) == set(tuples) and not set(UIDS) & set(entries)
    forms = {}
    for tile in current['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        for form in read(path)['buildings']:
            if form['uid'] in tuples:
                assert form['uid'] not in forms; forms[form['uid']] = form
    assert set(forms) == set(tuples)
    for uid, (path, entry) in entries.items():
        item = tuples[uid]
        assert composition.canonical(entry) == item['rawEntrySHA256']
        assert composition.canonical(forms[uid]) == item['viewerFormSHA256']
        assert ref(path.parent / entry['asset']) == item['source'] and item['source']['sha256'] == entry['sha256']
    # All full original/literal/F32 native geometry and separation arithmetic
    # remain bound by the completed whole-domain result and recursive receipts.
    assert len({r['uid'] for r in native['completeStrictlyDisjointActors']}) == 6645
    refs.extend(catalogue_refs)
    # Identity replay cache copies are outputs, never authorities: the exact
    # source, decoder/current modules and returned complete proof are bound.
    # Excluding only those newly generated cache paths keeps repeated identical
    # current rechecks byte-deterministic across distinct lease-owned folders.
    refs.extend(ref(HERE / name) for name in ['twin_regency1120_complete_original_role_composition_v1_20261011.py', 'twin_regency1120_complete_actual_fixture_v1_20261011.py', 'test_twin_regency1120_complete_original_role_composition_v1_20261011.py', 'exact_original_georef_cell_identity_20261009.py', 'routed_original_cell_identity.py', 'exact_packed_world_geometry_20261009.py', 'exact_packed_world_bounds_v3_20261010.py', 'xl_source_stream_binding_20261009.py', 'acceptance-policy.py', 'xl-popcorn-source-investigations-checkpoints-20261009.py'])
    refs = pins_exact(refs); assert ref(manifest) == start; pulse()
    return dict(contract='twin-regency-complete1120-current-four-stream-original-pair-typed-qualification-v1', uids=UIDS,
        currentManifest=start, sourceSHA256ByUID=SOURCES, completeOriginalFaces=13519, completeOriginalNonzeroBodies=1120,
        completeFourStreamRoleComposition=typed, currentOwnedIdentities=identities,
        completeWholeOriginalPOSITIONProofs=positions, completeProviderRootAndStreams=streams,
        completeActualDrawnGroundSHA256ByUID=grounds, completeCurrentNativeActors=6645,
        completeNativeWholeAlteredTerrainDomainProof=ref(NATIVE / 'diagnostic.json.gz'),
        completeCurrentForeignForms=107, originalT1RemainsCurrentBasicForeign=True,
        allRawPhysicalReasonsPreserved=EXPECTED_RAW, rawGroundOnlyReasonsResolvedBy827NonvisualPathsToGenuineP1091=True,
        complete155BoundaryVisualBodies=typed['complete155BoundaryVisualBodies'], complete138OriginalPlacementVisualBodies=typed['complete138SourcePlacementVisualBodies'],
        visualPartsNeverSupplyRootsBridgesOrHosts=True, sourcePlacementMountingNotCertified=True,
        nativeReacceptance=False, sourceGeometryChanges=0, terrainProposal=candidates,
        terrainProposalGeometryChanged=True, explicitArithmeticNotUniversalGPUCameraGuarantee=True,
        currentTypedPhysicalAccepted=True, reasons=[], scriptChecksPassed=True, readyForStagedBrowser=True,
        browserAcceptanceRequired=True, fullAcceptance=False, installationApproved=False, newlyInstalled=0,
        completedMathJobIds={name: r['jobId'] for name, r in receipts.items()}, evidenceRefs=refs)

def main():
    assert not DOC.exists() and not LOCAL.exists()
    neighbour_inputs = read(PHYSICAL / 'neighbour-inputs.json.gz')
    wanted = sorted({r['building']['uid'] for r in neighbour_inputs['rows']} | set(UIDS))
    claim = reservations.claim('twin-complete-current-role-' + str(uuid.uuid4()), ['building:' + uid for uid in wanted] + ['terrain-patch:' + uid for uid in UIDS], batch=BATCH, ttl=3600)
    assert claim['ok']; lease = claim['reservation']; last = time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic() - last >= 20:
            assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease); last = time.monotonic()
    try:
        result = json.loads(json.dumps(recheck(LOCAL / 'identity-recheck', pulse)))
        assert reservations.owns(lease)
        save(DOC / 'typed-role.json.gz', result)
        freezer = module('twin_complete_current_role_freezer', 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        freezer.freeze(BATCH, 'complete-current1120-original-pair827-nonvisual155-boundary138-source-placement-role-v1', [ROOT / p['path'] for p in result['evidenceRefs']] + [DOC / 'typed-role.json.gz'], dict(uids=UIDS, scriptChecksPassed=True, completeOriginalFaces=13519, completeOriginalNonzeroBodies=1120, sourceGeometryChanges=0, browserAcceptanceRequired=True, installationApproved=False, newlyInstalled=0))
    finally:
        assert reservations.release(lease)['ok']

if __name__ == '__main__': main()
