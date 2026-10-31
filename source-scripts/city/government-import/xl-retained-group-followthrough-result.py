"""Bind terminal complete-group physical checks and exact original support holds."""
import json
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-ten-retained-group-followthrough-20261009'
DOC = BASE / BATCH


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def main():
    assert not DOC.exists(), 'Fresh result only'
    latest = {227380: 'native-parent', 228219: 'native-parent', 285509: 'source-local-v2',
              273672: 'source-local', 91827: 'source-local', 104302: 'source-local',
              264206: 'source-local', 280084: 'source-local', 235076: 'source-local'}
    names = [f'government-xl-retained-group-{route}-20261008-{uid}-0' for uid, route in latest.items()]
    names += ['government-xl-june-garden-t3-original-checked-20261008',
              'government-xl-june-garden-three-shared-osm-checked-20261008',
              'government-xl-june-garden-t3-original-seams-20261008',
              'government-xl-june-garden-four-original-shared-edges-20261009']
    refs = [ref(Path(__file__))]
    receipts = []
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for name in names:
            report = read(BASE / name / 'result.json')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                               (report['jobId'],)).fetchone() == ('complete', report)
            for item in report['evidenceRefs']:
                assert ref(ROOT / item['path']) == item
            receipts.append(report)
            refs.extend([ref(BASE / name / 'result.json'), *report['evidenceRefs']])
        pointer_path = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
        pointer = read(pointer_path)
        review = con.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews '
                             'WHERE snapshot_id=%s AND uid=%s',
                             (pointer['snapshotId'], 'landsd/134332:0')).fetchone()
        assert review and review[0] == 'held'
        assert review[2]['effort']['job_id'] == '832fcff4ff5b28677c4779a3561f6a263bda91d9e841eeb3e6ede7078e5a4d65'
    refs.append(ref(pointer_path))
    rows = []
    for (uid, route), report in zip(latest.items(), receipts):
        assert report['uids'] == [f'landsd/{uid}:0'] and not report['scriptChecksPassed']
        next_step = 'New source-specific terrain/support evidence is required; do not repeat this unchanged full physical route.'
        if uid == 227380:
            next_step = ('Own terrain/foundation/runtime and retained native147505 pass. Five basic neighbours fail. '
                         'Four actual tower originals recovered; T1/T2/T3/T4 retain4/1/14/1 unresolved contacts, '
                         'with zero seam/shared-edge corrections. The fifth ancillary component264492 is not '
                         'covered by the basic interface. Need actual source/component resolution; no same-parent assumption.')
        elif uid == 228219:
            next_step = ('Own terrain/foundation/runtime and retained native72357 pass. Four basic towers still regress; '
                         'earlier exact basic/native support diagnostics remain failed. Need new original component '
                         'support/identity evidence, not another unchanged terrain attempt.')
        elif uid == 264206:
            next_step = ('Handle the installed Central Pier terrain wrapper and its eight children with explicit '
                         'parent replacement, exact retained geometry and all retained-model checks; root-only '
                         'route stops before physical evaluation. This guard is not source corruption.')
        rows.append({'uid': f'landsd/{uid}:0', 'sourceSHA256': report['sourceSHA256s'][f'landsd/{uid}:0'],
                     'humanStatus': 'held-unknown', 'reasons': report['reasons'],
                     'physicalJobId': report['jobId'], 'nextStep': next_step,
                     'inProcess': False, 'retainCurrentModel': True, 'permanentRejection': False,
                     'needsAIProcessing': None, 'needsComputeProcessing': None, 'needsHumanDecision': False})
    rows.append({'uid': 'landsd/134332:0', 'sourceSHA256': review[1], 'humanStatus': 'held-unknown',
                 'reasons': ['existing-reviewed-Citywalk-Vision-City-support-hold'],
                 'existingReview': {'snapshotId': pointer['snapshotId'], 'state': review[0], 'result': review[2]},
                 'nextStep': 'Existing reviewed terrain/foundation and292 neighbours pass, but five installed '
                 'Vision City towers depend on the surveyed basic podium and294 original interface samples '
                 'remain unresolved. The no-review-only ten-source worker correctly refused this reviewed '
                 'source; preserve its existing review and use a dedicated dependency-resolution route.',
                 'inProcess': False, 'retainCurrentModel': True, 'permanentRejection': False,
                 'needsAIProcessing': None, 'needsComputeProcessing': None, 'needsHumanDecision': False})
    diagnostic_path = HERE / 'local/government-xl-june-garden-basic-interfaces-20261009/diagnostic.json'
    diagnostic = read(diagnostic_path)
    assert len(diagnostic['rows']) == 5 and not any(r['proof']['allSampledContactsPass'] for r in diagnostic['rows'])
    save(DOC / 'june-garden-basic-interfaces.json', diagnostic)
    refs.extend([ref(diagnostic_path), ref(DOC / 'june-garden-basic-interfaces.json')])
    refs.extend({'path': p, 'sha256': h} for p, h in diagnostic['inputHashes'].items())
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    refs.append(ref(manifest))
    refs = list({r['path']: r for r in refs}.values())
    payload = {'rows': rows, 'priorJobIds': [r['jobId'] for r in receipts], 'evidenceRefs': refs,
               'manifestSHA256': digest(manifest.read_bytes())}
    claim = reservations.claim('codex-retained-group-result-' + str(uuid.uuid4()),
                               ['source-context:' + BATCH], batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    job = None
    try:
        stage = 'terminal-retained-group-source-specific-followthrough-v1'
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'batch': BATCH, 'jobId': jid, 'newlyInstalled': 0, 'publication': False,
                  'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'aiGeometryModelling': False,
                  'qualification': 'Ten terminal source-specific results, no active worker or installation credit. '
                  'Cross-tile preparation fixed in a fresh checker; existing reviewed Citywalk is preserved. '
                  'Retained native parents are actually checked, not waived. Real source/component failures '
                  'remain resumable without inventing permanent noninstallability or requiring user/AI decisions.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for item in refs:
                assert ref(ROOT / item['path']) == item
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,"
                               "token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s "
                               "AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                               (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                               (jid,)).fetchone() == ('complete', result)
        save(DOC / 'result.json', result)
        save(DOC / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print(json.dumps({'jobId': jid, 'neonVerified': True, 'terminalSources': len(rows), 'newlyInstalled': 0}))
    except Exception as error:
        if job:
            jobs.finish(job, error=str(error))
        raise
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
