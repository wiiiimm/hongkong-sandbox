"""Record verified runtime correction evidence; grants no model acceptance."""
import json
from pathlib import Path
import uuid
from run import ROOT, read, save, digest, connect, reservations, jobs, Jsonb, dict_row


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def main():
    batch = 'government-xl-coastal-sampler-correction-20261008'
    doc = ROOT / 'docs/astra-city/government-import' / batch
    assert not (doc / 'result.json').exists(), 'Completed evidence is immutable'
    checks_path = ROOT / 'docs/astra-city/government-import/government-xl-three-final-coastal-sampler-rechecks-20261008/result.json'
    checks = read(checks_path)
    unit = read(doc / 'final-unit-tests.json')
    browser = read(doc / 'browser-final/browser.json')
    assert unit['exitCode'] == 0
    assert unit['geoSHA256'] == digest((ROOT / '3d-viewer/city/geo.js').read_bytes())
    assert unit['outputSHA256'] == digest((doc / 'final-unit-tests.tap').read_bytes())
    assert len(browser['views']) == 2 and browser['errors'] == []
    assert {v['name'] for v in browser['views']} == {'desktop', 'mobile'}
    for view in browser['views']:
        assert view['ready'] and view['submergedWalkRejected']
        assert all(p['webglError'] == 0 for p in view['proofs'])
        assert view['imageSHA256'] == digest((doc / 'browser-final' / (view['name'] + '.png')).read_bytes())
    refs = [ref(p) for p in [Path(__file__), checks_path,
        ROOT / '3d-viewer/city/tests/terrain-coast.test.js',
        ROOT / '3d-viewer/city/tests/tai-o-models.test.js',
        doc / 'baseline.json', doc / 'baseline-tests.tap',
        doc / 'baseline-hydro-tests.tap', doc / 'baseline-tai-o-tests.tap',
        doc / 'intermediate-geo.js.txt', doc / 'final-unit-tests.json',
        doc / 'final-unit-tests.tap', doc / 'browser-final/browser.json',
        doc / 'browser-final/desktop.png', doc / 'browser-final/mobile.png']]
    refs += checks['evidenceRefs']
    refs += [{'path': p, 'sha256': sha} for p, sha in browser['inputHashes'].items()]
    refs = list({r['path']: r for r in refs}.values())
    for item in refs:
        assert ref(ROOT / item['path']) == item
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (checks['jobId'],)).fetchone() == ('complete', checks)
    claim = reservations.claim('codex-xl-coastal-runtime-' + str(uuid.uuid4()),
        ['building:' + uid for uid in checks['uids']], batch=batch)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        payload = {'evidenceRefs': refs, 'freshPhysicalJobId': checks['jobId']}
        stage = 'xl-coastal-runtime-correction-verification-v1'
        jid = jobs.enqueue(batch, stage, payload)
        job = jobs.claim(batch, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'jobId': jid, 'batch': batch,
            'fullXLCounts': checks['fullXLCounts'], 'newlyInstalled': 0,
            'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
            'unitTestFiles': unit['testFiles'], 'browserViews': ['desktop', 'mobile'],
            'freshPhysicalChecks': [{k: row[k] for k in ['uid', 'scriptChecksPassed', 'reasons']}
                                   | {'maxSamplerDeltaM': row['metric']['maxSamplerDelta']}
                                   for row in checks['rows']],
            'qualification': 'Production sampler now follows interpolated coastal faces and inherited mapped water cuts while preserving complete native overlays. Focused browser fixtures and full city unit suite pass. Three exact originals still fail independent identity/foundation/contact gates. No model acceptance, whole-city browser acceptance, geometry editing or tolerance waiver.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for item in refs:
                assert ref(ROOT / item['path']) == item
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                               (jid,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print(json.dumps({'jobId': jid, 'resultVerified': True, 'newlyInstalled': 0}))
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
