"""Unexecuted historical original-source attribution recipe, never acceptance.

Only --preflight-only may run while original worker restart approval is pending.
--execute uses the existing reservation supervisor; --owned is its private child.
"""
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import struct
import sys
import uuid

import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from foundation_source_face_attribution_adapter_v2_20261013 import attribute, canonical_pin

UID = 'landsd/264206:0'
SOURCE = '0ff5adae4dae90e856af6fb6f40112a24198668ca9dfc66e9570b058739b50fb'
EXPECTED = dict(uid=UID, sourceSHA256=SOURCE, modelId='B336901655802063C1',
                csuid='3369016558P20060312', faces=19551, bodies=144)
BATCH = 'government-xl-china-merchants264206-saved-face-attribution-v1-20261013'
STAGE = 'historical-original-source-face-attribution-no-acceptance-v1'
RESOURCES = ['building:' + UID, 'source-context:' + BATCH]
BASE = ROOT / 'docs/astra-city/government-import'
PROPOSAL = BASE / 'government-xl-china-merchants-foundation-source-face-attribution-code-proposal-v1-20261013'
PREPARATION = BASE / 'government-xl-china-merchants264206-saved-face-attribution-runner-preparation-v1-20261013'
WRAPPER = BASE / 'government-xl-retained-group-central-wrapper-20261009-264206-0'
FOUNDATION = BASE / 'government-xl-china-merchants-wrapper-foundation-result-20261009'
CENSUS = BASE / 'government-xl-remaining-20260923/sol-continuation-20261003/components/264206-0.json.gz'
RUNTIME = HERE / 'local/government-xl-retained-group-central-wrapper-20261009-264206-0/runtime-geometry.json.gz'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
RECOVERY_LOCAL = HERE / 'local' / (BATCH + '-receipt-recovery-v1')
MANIFEST_SHA = 'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'


def ref(path):
    path = path.resolve()
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def payload_for(launch):
    return dict(uids=[UID], sourceSHA256=SOURCE, canonicalPin=launch['canonicalPin'], evidenceRefs=launch['evidenceRefs'])


def verify_launch(launch):
    approved_path = PREPARATION / 'runner-input-pins.json'
    approved = read(approved_path)
    expected = {**approved['inputHashes'], ref(approved_path)['path']: ref(approved_path)['sha256']}
    assert len(launch['evidenceRefs']) == len(expected)
    assert {p['path']: p['sha256'] for p in launch['evidenceRefs']} == expected
    for pin in launch['evidenceRefs']:
        assert ref(ROOT / pin['path']) == pin


def claim_exact_job(payload, owner):
    jid = jobs.enqueue(BATCH, STAGE, payload)
    job = jobs.claim(BATCH, owner, [STAGE], lease_seconds=3600)
    assert job, 'No claimable exact diagnostic job; recover its completed receipt instead of recomputing'
    if job['id'] != jid:
        assert jobs.finish(job, error='Unexpected diagnostic job identity; source calculation refused', retry=True)
        raise AssertionError('Unexpected pending job returned to retry handling; no source calculation')
    return jid, job


def recover_completed_result(payload, fetch_completed, verify_ref, write_receipt):
    """Exact completed receipt only; callbacks never decode or recalculate geometry."""
    jid = digest(jobs.encode([BATCH, STAGE, payload]).encode())
    status, completed = fetch_completed(jid)
    assert status == 'complete' and completed['jobId'] == jid
    assert completed['batch'] == BATCH and completed['stage'] == STAGE
    for key, value in payload.items():
        if key != 'evidenceRefs':
            assert completed[key] == value
    assert completed['newlyInstalled'] == 0 and completed['publication'] is False
    assert completed['currentAcceptance'] is False and completed['physicalAccepted'] is False and completed['sourceRoleApproved'] is False
    refs = {r['path']: r['sha256'] for r in completed['evidenceRefs']}
    assert len(refs) == len(completed['evidenceRefs'])
    assert all(refs.get(r['path']) == r['sha256'] for r in payload['evidenceRefs'])
    assert str((DOC / 'source-face-attribution.json.gz').relative_to(ROOT)) in refs
    for pin in completed['evidenceRefs']:
        verify_ref(pin)
    write_receipt(completed, dict(jobId=jid, resultVerified=True, receiptRecoveredWithoutNumericalReplay=True))
    return completed


def load_canonical():
    spec = importlib.util.spec_from_file_location('china_saved_face_canonical', HERE / 'xl-final-script-pass.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.foundation_context


def original_index_order(raw):
    """Exact integer topology in scene/node/primitive order, with unused slots.

    This is the same traversal order as the pinned original census decoder.
    The pinned runtime loader concatenates mesh indices with POSITION offsets.
    No coordinate-distance match establishes or substitutes for this binding.
    """
    data = gzip.decompress(raw)
    magic, version, total = struct.unpack_from('<III', data)
    assert (magic, version, total) == (0x46546c67, 2, len(data))
    size, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4e4f534a
    doc = json.loads(data[20:20 + size])
    size2, kind2 = struct.unpack_from('<II', data, 20 + size)
    assert kind2 == 0x004e4942 and 28 + size + size2 == len(data)
    binary = data[28 + size:]
    assert len(doc['buffers']) == 1 and not doc['buffers'][0].get('uri')
    indices, primitives, vertices, face_offset = [], [], 0, 0

    def visit(node_id, ancestors, occurrence):
        nonlocal vertices, face_offset
        assert node_id not in ancestors, 'Cyclic hierarchy'
        node = doc['nodes'][node_id]
        if 'mesh' in node:
            for ordinal, primitive in enumerate(doc['meshes'][node['mesh']]['primitives']):
                assert primitive.get('mode', 4) == 4 and 'indices' in primitive
                position = doc['accessors'][primitive['attributes']['POSITION']]
                accessor = doc['accessors'][primitive['indices']]
                view = doc['bufferViews'][accessor['bufferView']]
                assert accessor['type'] == 'SCALAR' and not accessor.get('normalized') and not accessor.get('sparse')
                assert view['buffer'] == 0 and position['type'] == 'VEC3'
                dtype = np.dtype({5123: '<u2', 5125: '<u4'}[accessor['componentType']])
                stride = view.get('byteStride', dtype.itemsize)
                assert stride >= dtype.itemsize
                offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
                count = accessor['count']
                assert count > 0 and count % 3 == 0
                assert accessor.get('byteOffset', 0) + (count - 1) * stride + dtype.itemsize <= view['byteLength']
                ids = np.ndarray((count,), dtype=dtype, buffer=binary, offset=offset, strides=(stride,)).astype(np.int64)
                assert ids.max() < position['count']
                indices.append(ids + vertices)
                primitives.append(dict(nodeIndex=node_id, nodeOccurrencePath=occurrence, primitiveOrdinal=ordinal,
                    positionAccessor=primitive['attributes']['POSITION'], indexAccessor=primitive['indices'],
                    vertexOffset=vertices, positionSlotCount=position['count'], sourceFaceOffset=face_offset,
                    sourceFaceCount=count // 3, primitiveIndexValuesSHA256=digest(ids.astype('<i8').tobytes())))
                vertices += position['count']
                face_offset += count // 3
        for ordinal, child in enumerate(node.get('children', [])):
            visit(child, ancestors | {node_id}, [*occurrence, ordinal])

    for ordinal, root in enumerate(doc['scenes'][doc.get('scene', 0)]['nodes']):
        visit(root, set(), [ordinal])
    return np.concatenate(indices), vertices, primitives


def bound_attribution(function, runtime_row, selection_row, census, raw_source, prior_metrics,
                      *, expected, expected_pin):
    """Pure calculation; fixtures may inject a smaller exact source binding.

    Production supplies EXPECTED, the pinned source decoder and saved inputs.
    Face ordinals require the exact original/runtime integer-index comparison;
    complete census partition alone cannot establish that correspondence.
    """
    for item in (runtime_row, selection_row, census):
        assert item['uid'] == expected['uid'] and item['sourceSHA256'] == expected['sourceSHA256']
    assert selection_row['modelId'] == expected['modelId']
    building = selection_row['source']['building']
    assert building['uid'] == expected['uid'] and building['buildingCSUID'] == expected['csuid']
    assert selection_row['triangles'] == expected['faces']
    assert digest(raw_source) == expected['sourceSHA256']
    position = np.asarray(runtime_row['position'], dtype=float)
    index = np.asarray(runtime_row['index'])
    assert position.ndim == index.ndim == 1 and position.size % 3 == index.size % 3 == 0
    assert index.dtype.kind in 'iu' and index.size == expected['faces'] * 3
    position = position.reshape(-1, 3)
    assert np.isfinite(position).all() and index.min() >= 0 and index.max() < len(position)
    original_index, original_position_count, primitive_order = original_index_order(raw_source)
    assert len(position) == original_position_count and np.array_equal(index, original_index), 'Exact source/runtime index-slot order changed'
    triangles = position[index.reshape(-1, 3)]
    original = decode_original_world_triangles(raw_source)
    assert isinstance(original, np.ndarray) and original.shape == triangles.shape and np.isfinite(original).all()
    # Preserve the completed producer's existing exact face-order / 2 mm check.
    delta = float(np.max(np.abs(original - triangles)))
    assert delta < .002, 'Original/runtime indexed face order or coordinate binding changed'
    ground = np.asarray(runtime_row['drawnGroundGeometry'], dtype=float)
    assert ground.ndim == 1 and ground.size % 9 == 0 and np.isfinite(ground).all()
    ground = ground.reshape(-1, 3, 3)
    assert len(census['components']) == expected['bodies']
    bodies = []
    for ordinal, body in enumerate(census['components']):
        assert body['triangles'] == len(body['sourceFaceIndices'])
        bodies.append(dict(bodyId=ordinal, sourceFaceIndices=body['sourceFaceIndices']))
    original_arithmetic_zero = np.flatnonzero(np.linalg.norm(np.cross(original[:, 1]-original[:, 0], original[:, 2]-original[:, 0]), axis=1) == 0).tolist()
    runtime_arithmetic_zero = np.flatnonzero(np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0]), axis=1) == 0).tolist()
    result = attribute(function, triangles, ground, Polygon(building['rings'][0], building['rings'][1:]),
                       bodies, expected_canonical_pin=expected_pin)
    assert result['canonicalFoundationMetrics'] == prior_metrics, 'Saved canonical foundation was not reproduced exactly'
    for group in result['failureGroupsInCanonicalDelegateOrder']:
        ids = group['sourceFaceIndices']
        group['originalSourceFaceVerticesInJournalOrder'] = original[ids].tolist()
        group['savedRuntimeFaceVerticesInJournalOrder'] = triangles[ids].tolist()
    result.update(uid=expected['uid'], sourceSHA256=expected['sourceSHA256'],
                  originalRuntimeMaximumCoordinateDeltaM=delta,
                  originalFloat64CrossNormArithmeticZeroFaceIndices=original_arithmetic_zero,
                  runtimeFloat64CrossNormArithmeticZeroFaceIndices=runtime_arithmetic_zero,
                  arithmeticZeroObservationsAreNotExactNonrenderingCertificates=True,
                  exactSourceRuntimeIndexStreamEqual=True, sourcePrimitiveFaceOrder=primitive_order,
                  completeSavedCensusConnectivity='all-source shared vertices rounded to four decimals, diagnostic only',
                  completeOriginalSourceFaceVerticesInOrdinalOrder=original.tolist(),
                  completeCensusVerbatim=census, savedFoundationReproducedExactly=True,
                  historicalSavedWrapperOnly=True, currentAcceptance=False, physicalAccepted=False,
                  sourceRoleApproved=False, installationApproved=False)
    return result


def preflight():
    """Literal hashes and census/form metadata only; no runtime mesh decoding/math."""
    assert not DOC.exists() and not LOCAL.exists(), 'Use the existing handle/receipt; never silently restart'
    pins = {r['path']: r['sha256'] for r in read(PROPOSAL / 'draft-pins.json')['evidenceRefs']}
    primary_review = BASE / 'government-xl-china-merchants264206-bounded-basement-primary-research-v1-20261013/root-independent-primary-and-dependency-review.json'
    for path, sha in read(primary_review)['allInputHashes'].items():
        assert path not in pins or pins[path] == sha
        pins[path] = sha
    for path, sha in pins.items():
        assert ref(ROOT / path)['sha256'] == sha, path
    rows = read(WRAPPER / 'selection.json.gz')['rows']
    assert len(rows) == 1
    row = rows[0]
    assert (row['uid'], row['sourceSHA256'], row['modelId'], row['triangles']) == (UID, SOURCE, EXPECTED['modelId'], EXPECTED['faces'])
    assert row['source']['building']['buildingCSUID'] == EXPECTED['csuid']
    assert ref(ROOT / row['candidate']['path'])['sha256'] == SOURCE
    forms = read(ROOT / '3d-viewer' / row['source']['tile'])['buildings']
    assert [f for f in forms if f['uid'] == UID] == [row['source']['building']]
    census = read(CENSUS)
    assert census['uid'] == UID and census['sourceSHA256'] == SOURCE and len(census['components']) == 144
    ids = [i for body in census['components'] for i in body['sourceFaceIndices']]
    assert len(ids) == 19551 and sorted(ids) == list(range(19551))
    assert ref(ROOT / '3d-viewer/city/data/manifest.json')['sha256'] == MANIFEST_SHA
    function = load_canonical()
    expected_pin = read(PROPOSAL / 'synthetic-validation.json')['canonicalPin']
    assert canonical_pin(function) == expected_pin
    paths = {ROOT / p for p in pins} | {Path(__file__).resolve(), PROPOSAL / 'draft-pins.json',
        HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'run.py',
        HERE.parent / 'shared-modelling/jobs.py', HERE.parent / 'shared-modelling/reservations.py',
        HERE.parent / 'shared-modelling/reservation_runner.py', HERE.parent / 'shared-modelling/db.py',
        ROOT / row['candidate']['path'], ROOT / '3d-viewer' / row['source']['tile'],
        ROOT / '3d-viewer/city/data/manifest.json', FOUNDATION / 'result.json', primary_review}
    contract_path = PREPARATION / 'historical-runtime-order-contract.json'
    contract = read(contract_path)
    for item in [contract['historicalLoaderArchiveRef'], *contract['orderContractRefs']]:
        assert ref(ROOT / item['path']) == {k: item[k] for k in ['path', 'sha256']}
        paths.add(ROOT / item['path'])
    paths.add(contract_path)
    priors = [read(WRAPPER / 'result.json'), read(FOUNDATION / 'result.json')]
    for module in [*list(sys.modules.values())]:
        name = getattr(module, '__file__', None)
        if name:
            p = Path(name).resolve()
            if p.is_relative_to(ROOT) and p.is_file():
                paths.add(p)
    return function, expected_pin, row, census, priors, [ref(p) for p in sorted(paths)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight-only', action='store_true')
    mode.add_argument('--execute', action='store_true')
    mode.add_argument('--owned', action='store_true')
    mode.add_argument('--recover-receipt', action='store_true')
    mode.add_argument('--owned-recover', action='store_true')
    args = parser.parse_args()
    if args.owned or args.owned_recover:
        lease = read((RECOVERY_LOCAL if args.owned_recover else LOCAL) / 'reservation.json')
        assert lease['batch'] == BATCH and set(lease['resources']) == set(RESOURCES)
        assert reservations.owns(lease)
        assert (DOC / 'source-face-attribution.json.gz').exists() if args.owned_recover else not DOC.exists()
        # preflight rejects LOCAL to prevent accidental new launch; owned inputs
        # are pinned separately below using the launch receipt.
        launch = read(LOCAL / 'launch-inputs.json')
        verify_launch(launch)
        payload = payload_for(launch)
        if args.owned_recover:
            def fetch_completed(jid):
                with connect() as connection:
                    connection.execute('SET TRANSACTION READ ONLY')
                    return connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone()
            def verify_recovery_ref(pin):
                assert ref(ROOT / pin['path']) == pin
            def write_recovery_receipt(result, receipt):
                assert reservations.owns(lease)
                if (DOC / 'result.json').exists():
                    assert read(DOC / 'result.json') == result
                else:
                    save(DOC / 'result.json', result)
                if (DOC / 'neon-sync.json').exists():
                    old = read(DOC / 'neon-sync.json')
                    assert old['jobId'] == receipt['jobId'] and old['resultVerified'] is True
                else:
                    save(DOC / 'neon-sync.json', receipt)
            completed = recover_completed_result(payload, fetch_completed, verify_recovery_ref, write_recovery_receipt)
            print(json.dumps(dict(jobId=completed['jobId'], receiptRecovered=True, numericalReplay=False)), flush=True)
            return
        function = load_canonical()
        expected_pin = launch['canonicalPin']
        row = read(WRAPPER / 'selection.json.gz')['rows'][0]
        census = read(CENSUS)
        priors = [read(WRAPPER / 'result.json'), read(FOUNDATION / 'result.json')]
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            for prior in priors:
                assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (prior['jobId'],)).fetchone() == ('complete', prior)
        jid, job = claim_exact_job(payload, lease['owner'])
        durable_complete = False
        try:
            assert reservations.heartbeat(lease)['ok'] and jobs.heartbeat(job, lease_seconds=3600)
            runtime = read(RUNTIME)
            assert len(runtime['rows']) == 1
            contract = read(PREPARATION / 'historical-runtime-order-contract.json')
            assert runtime['inputHashes']['3d-viewer/city/official-model-assets.js'] == contract['savedRuntimeAssetLoaderSHA256']
            provenance = {p['path']: p['sha256'] for p in priors[0]['evidenceRefs']}
            assert all(provenance.get(p) == h for p, h in runtime['inputHashes'].items())
            raw_source = (ROOT / row['candidate']['path']).read_bytes()
            result = bound_attribution(function, runtime['rows'][0], row, census, raw_source,
                                      read(FOUNDATION / 'foundation.json')['foundation'],
                                      expected=EXPECTED, expected_pin=expected_pin)
            assert reservations.heartbeat(lease)['ok'] and jobs.heartbeat(job, lease_seconds=3600)
            for pin in launch['evidenceRefs']:
                assert ref(ROOT / pin['path']) == pin
            save(DOC / 'source-face-attribution.json.gz', result)
            refs = [*launch['evidenceRefs'], ref(DOC / 'source-face-attribution.json.gz'), ref(LOCAL / 'launch-inputs.json')]
            completed = dict(**payload, batch=BATCH, stage=STAGE, jobId=jid, newlyInstalled=0,
                             publication=False, modelGeometryChanges=0, terrainGeometryChanges=0,
                             scriptExternalAICalls=0, aiGeometryModelling=False, currentAcceptance=False,
                             physicalAccepted=False, sourceRoleApproved=False, permanentRejection=False)
            completed['evidenceRefs'] = refs
            with connect() as connection:
                connection.row_factory = dict_row
                connection.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
                assert reservations._current(connection, lease)
                for pin in refs:
                    assert ref(ROOT / pin['path']) == pin
                assert connection.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(completed), jid, job['owner'], job['token'])).rowcount == 1
            durable_complete = True
            with connect() as connection:
                connection.execute('SET TRANSACTION READ ONLY')
                assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', completed)
            save(DOC / 'result.json', completed)
            save(DOC / 'neon-sync.json', dict(jobId=jid, resultVerified=True))
            print(json.dumps(dict(jobId=jid, sourceFaceAttributionComplete=True, currentAcceptance=False)), flush=True)
        except Exception as error:
            if not durable_complete:
                assert jobs.finish(job, error=str(error))
            raise
        return
    if args.recover_receipt:
        assert not RECOVERY_LOCAL.exists() and (DOC / 'source-face-attribution.json.gz').is_file()
        verify_launch(read(LOCAL / 'launch-inputs.json'))
        claim = reservations.claim('china-saved-face-receipt-recovery-' + str(uuid.uuid4()), RESOURCES, batch=BATCH, ttl=1800)
        assert claim['ok'], claim
        lease_file = RECOVERY_LOCAL / 'reservation.json'
        try:
            save(lease_file, json.loads(json.dumps(claim['reservation'], default=str)))
        except Exception:
            assert reservations.release(claim['reservation'])['ok']
            raise
        try:
            status = subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
                                     'run', '--lease-file', str(lease_file), '--ttl', '1800', '--',
                                     sys.executable, __file__, '--owned-recover'], cwd=ROOT).returncode
        except OSError:
            assert reservations.release(claim['reservation'])['ok']
            raise
        assert status == 0, status
        return
    function, expected_pin, row, census, priors, refs = preflight()
    if args.preflight_only:
        print(json.dumps(dict(evidenceRefs=len(refs), completeSourceSlots=19551, completeBodies=144,
                             noDatabaseCalls=True, noReservations=True, noModelDecode=True, noNumericalModelCall=True,
                             inputRefs=refs)))
        return
    approved_path = PREPARATION / 'runner-input-pins.json'
    approved = read(approved_path)
    assert {p['path']: p['sha256'] for p in refs} == approved['inputHashes'], 'Reviewed recipe/input tuple changed'
    refs.append(ref(approved_path))
    claim = reservations.claim('china-saved-face-attribution-' + str(uuid.uuid4()),
                               RESOURCES, batch=BATCH, ttl=1800)
    assert claim['ok'], claim
    lease_file = LOCAL / 'reservation.json'
    try:
        save(lease_file, json.loads(json.dumps(claim['reservation'], default=str)))
        save(LOCAL / 'launch-inputs.json', dict(canonicalPin=expected_pin, evidenceRefs=refs))
    except Exception:
        assert reservations.release(claim['reservation'])['ok']
        raise
    try:
        status = subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
                                 'run', '--lease-file', str(lease_file), '--ttl', '1800', '--',
                                 sys.executable, __file__, '--owned'], cwd=ROOT).returncode
    except OSError:
        assert reservations.release(claim['reservation'])['ok']
        raise
    assert status == 0, status


if __name__ == '__main__':
    main()
