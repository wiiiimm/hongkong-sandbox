"""Explain existing loader rejections using pinned bounds; never bypass the loader."""
import argparse
import math
import uuid
from pathlib import Path
from run import ROOT, read, save, digest, connect, reservations, jobs, Jsonb, dict_row, NATIVE_RUN


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', required=True); parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    previous = ROOT / args.previous
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    assert not doc.exists(), 'Fresh evidence only'
    old_path, selection_path = previous / 'current-checks.json', previous / 'physical-selection.json.gz'
    old, selection = read(old_path), read(selection_path)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    current_manifest_sha = digest(manifest_path.read_bytes())
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (old['jobId'],)).fetchone() == ('complete', old)
    selected = {r['uid']: r for r in selection['rows']}
    failures = [r for r in old['rows'] if r.get('metric', {}).get('error') == 'Official model does not fit its matched footprint']
    assert failures
    refs = [ref(p) for p in [old_path, selection_path, manifest_path, Path(__file__),
                            ROOT / '3d-viewer/city/building-geometry.js', ROOT / '3d-viewer/city/official-model-assets.js']]
    rows = []
    for failure in failures:
        r = selected[failure['uid']]
        assert r['sourceSHA256'] == failure['sourceSHA256']
        source_path, tile_path = ROOT / r['candidate']['path'], ROOT / '3d-viewer' / r['source']['tile']
        assert digest(source_path.read_bytes()) == r['sourceSHA256']
        assert digest(tile_path.read_bytes()) == r['source']['tileSHA256']
        b = r['source']['building']
        assert next(f for f in read(tile_path)['buildings'] if f['uid'] == r['uid']) == b
        e = r['candidate']['entry']; lo, hi = e['worldBounds']
        x, z = zip(*b['rings'][0]); footprint = [min(x), min(z), max(x), max(z)]
        margin = max(20, math.hypot(max(x)-min(x), max(z)-min(z)))
        excess = {'west': max(0, min(x)-margin-lo[0]), 'east': max(0, hi[0]-max(x)-margin),
                  'north': max(0, min(z)-margin-lo[2]), 'south': max(0, hi[2]-max(z)-margin)}
        assert max(excess.values()) > .02, 'Bounds alone do not explain this loader rejection'
        rows.append({'uid': r['uid'], 'name': b.get('name'), 'sourceKey': r['sourceKey'],
            'sourceSHA256': r['sourceSHA256'], 'nativeCacheKey': r['native']['cacheKey'],
            'nativeResultSHA256': r['native']['resultSha'], 'modelId': r['modelId'],
            'footprintBounds': footprint, 'nativeModelBounds': [lo, hi], 'existingLoaderMarginM': margin,
            'sourceBoundsBeyondLoaderAllowanceM': excess, 'indexedVertices': e['indexedVertices'],
            'positionLength': 3*e['indexedVertices'], 'withinExistingPositionLengthCap': 3*e['indexedVertices'] <= 3000000,
            'recordedRawError': failure['metric']['error'], 'previousReasons': failure['reasons'],
            'classification': 'original-source-exceeds-current-matched-footprint-bounds',
            'nextStep': 'Resolve exact authoritative source/component coverage or a demonstrated metadata/loader defect. Retain full identity and physical gates; do not enlarge footprint margins to suppress the error.'})
        refs += [ref(source_path), ref(tile_path)]
    refs = list({r['path']: r for r in refs}.values())
    claim = reservations.claim('codex-xl-loader-footprint-' + str(uuid.uuid4()), ['building:' + r['uid'] for r in rows], batch=args.batch)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        payload = {'previousJobId': old['jobId'], 'evidenceRefs': refs, 'sourceSHA256s': {r['uid']: r['sourceSHA256'] for r in rows},
                   'previousManifestSHA256': selection['manifestSHA256'], 'currentManifestSHA256': current_manifest_sha,
                   'unchangedCurrentSourceFormsVerified': True, 'currentPhysicalAcceptanceClaimed': False}
        stage = 'original-source-loader-footprint-hold-classification-v1'
        jid = jobs.enqueue(args.batch, stage, payload)
        job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'jobId': jid, 'batch': args.batch, 'rows': rows, 'classified': len(rows),
                  'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
                  'activeWorkers': 0, 'queuedFollowups': 0,
                  'qualification': 'Current unchanged exact source forms and pinned original bounds explain the recorded loader rejection. The historical physical selection is retained with its old manifest hash; terrain and installation checks are not rebound or claimed current. Other validity checks may also fail. No corruption, permanent impossibility, AI requirement or installation credit is inferred.'}
        with connect() as con:
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            for r in rows:
                assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, r['nativeCacheKey'])).fetchone() == (r['nativeResultSHA256'],)
            con.row_factory = dict_row
            assert reservations._current(con, lease)
            for item in refs:
                assert ref(ROOT / item['path']) == item
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone()[0] == result
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print({'classified': len(rows), 'jobId': jid, 'neonVerified': True, 'newlyInstalled': 0}, flush=True)
        print([{'uid': r['uid'], 'name': r['name'], 'maxBeyondMarginM': max(r['sourceBoundsBeyondLoaderAllowanceM'].values())} for r in rows], flush=True)
    finally:
        reservations.release(lease)


if __name__ == '__main__':
    main()
