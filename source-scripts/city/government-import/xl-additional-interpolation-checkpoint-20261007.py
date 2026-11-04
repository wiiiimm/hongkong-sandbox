"""Archive completed interpolation evidence and a read-only XL backlog snapshot.

Latest individual jobs are historical evidence, not current acceptance. Rows
outside these diagnostic sets are not automatically ready or unprocessed.
"""
import uuid
import json
from pathlib import Path
from run import ROOT, read, save, digest, reservations, jobs, connect, Jsonb, dict_row

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-additional-interpolation-checkpoint-20261007'

def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

def main():
    doc = BASE / BATCH
    assert not doc.exists()
    preview_path = BASE / 'government-xl-additional-original-interpolation-preview-20261007/result.json'
    preview = read(preview_path)
    assert preview['diagnosticOnly'] and not preview['publication']
    assert preview['newlyInstalled'] == preview['modelGeometryChanges'] == preview['scriptExternalAICalls'] == 0
    assert len(preview['rows']) == 109 and not preview['skipped']
    assert not any(r['newlyPositiveByAdditionalInterpolation'] for r in preview['rows'])
    refs = [ref(Path(__file__)), ref(preview_path)]
    for path, sha in preview['inputHashes'].items():
        evidence = ref(ROOT / path)
        assert evidence['sha256'] == sha
        refs.append(evidence)
    selection_path = BASE / 'government-xl-remaining-20260923/selection.json.gz'
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    refs.extend([ref(selection_path), ref(manifest_path)])
    selection = {r['uid']: r for r in read(selection_path)['rows']}
    installed = set()
    for url in read(manifest_path)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(ref(path))
        installed.update(r['uid'] for r in read(path)['models'])
    remaining = set(selection) - installed
    assert len(selection) == 352 and len(remaining) == 261
    negative = {r['uid'] for r in preview['rows'] if not r['mixedOriginalPointwisePositive']}
    assert negative <= remaining
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        latest = con.execute("SELECT DISTINCT ON(result->>'uid') result->>'uid',id,batch,result FROM astra_modelling.jobs WHERE status='complete' AND result->>'uid'=ANY(%s) ORDER BY result->>'uid',updated_at DESC,id DESC", (sorted(remaining),)).fetchall()
    latest_by_uid = {u: (jid, batch, result) for u, jid, batch, result in latest}
    identity = {u for u, (_, _, r) in latest_by_uid.items() if any(any(s in reason for s in ['identity', 'spatial', 'unrelated']) for reason in r.get('reasons', []))}
    coverage = []
    for uid in sorted(remaining):
        jid, batch, result = latest_by_uid.get(uid, (None, None, None))
        coverage.append({'uid': uid, 'name': selection[uid].get('name'), 'originalSurfaceBankNegative': uid in negative,
                         'latestIndividualJobHasIdentityReason': uid in identity,
                         'latestIndividualJobId': jid, 'latestIndividualBatch': batch,
                         'latestIndividualSourceSHA256': result.get('sourceSHA256') if result else None,
                         'historicalReasons': result.get('reasons') if result else None,
                         'latestJobResultSHA256': digest(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()) if result else None,
                         'qualification': 'Historical job reason; absence of a reason or individual job does not imply readiness.'})
    save(doc / 'backlog.json', {'rows': coverage, 'xlInstalled': 91, 'xlNotInstalled': 261,
                             'originalSurfaceBankNegative': len(negative), 'latestIdentityReasons': len(identity),
                             'intersection': len(negative & identity), 'outsideTheseSets': sorted(remaining - negative - identity),
                             'qualification': 'Evidence coverage only, not a global impossibility bound. Latest job source/current identity may differ; original-surface tests are necessary conditions for the tested bank, not acceptance.'})
    refs.append(ref(doc / 'backlog.json'))
    failure_path = BASE / 'government-xl-silvercord-complete-regional-original-tin-20261007-prepared/construction-failure.json'
    refs.append(ref(failure_path))
    claim = reservations.claim('codex-interpolation-archive-' + str(uuid.uuid4()),
                               ['building:' + u for u in sorted(remaining)], batch=BATCH)
    assert claim['ok']
    lease = claim['reservation']
    try:
        stage = 'completed-additional-interpolation-evidence-v1'
        payload = {'uids': sorted(remaining), 'evidenceRefs': refs}
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'jobId': jid, 'batch': BATCH, 'testedMeshes': 109,
                  'newInterpolationPositives': 0, 'xlInstalled': 91, 'xlNotInstalled': 261,
                  'newXLFromBaseline': 47, 'furtherInstallationsRequired': 53,
                  'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0,
                  'scriptExternalAICalls': 0, 'activeWorkers': 0,
                  'qualification': 'Completed diagnostic and historical backlog archive only. No review, geometry, terrain or installation changes.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for evidence in refs:
                assert ref(ROOT / evidence['path']) == evidence
            for _, old_jid, _, old_result in latest:
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (old_jid,)).fetchone() == {'status': 'complete', 'result': old_result}
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print({'jobId': jid, 'meshes': 109, 'newlyInstalled': 0, 'outsideDiagnosticSets': len(remaining - negative - identity)}, flush=True)
    finally:
        reservations.release(lease)

if __name__ == '__main__':
    main()
