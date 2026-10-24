"""Fenced real-source benchmark of the heavy incident-face lookup, without modelling."""
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row

BATCH = 'workflow-contact-index-20261005'
BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'
PRIOR = BASE / 'workflow-optimisation-20261005'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'


def ref(path):
    return {'path': str(Path(path).relative_to(ROOT)), 'sha256': digest(Path(path).read_bytes())}


def start():
    assert not LEASE.exists() and not (DOC / 'result.json').exists(), 'Reuse the existing attempt.'
    inputs = read(PRIOR / 'support-inputs.json')
    claim = reservations.claim('codex-contact-index-' + str(uuid.uuid4()),
                               ['building:' + u for u in inputs['sources']], batch=BATCH)
    assert claim['ok'], claim
    receipt = json.loads(json.dumps(claim['reservation'], default=str))
    save(LEASE, receipt)
    payload = {'priorResult': ref(PRIOR / 'result.json'), 'priorChecks': ref(PRIOR / 'support-checks.json'),
               'inputs': ref(PRIOR / 'support-inputs.json'), 'scripts': [ref(HERE / p) for p in (
                   'workflow-contact-index-20261005.py', 'workflow-face-benchmark.mjs',
                   'source-face-query.mjs', 'triangle-point-index.mjs')]}
    stage = 'exact-source-face-lookup-v1'
    jid = jobs.enqueue(BATCH, stage, payload)
    job = jobs.claim(BATCH, receipt['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    save(LOCAL / 'job.json', json.loads(json.dumps(job, default=str)))
    save(DOC / 'checkpoint.json', {'batch': BATCH, 'jobId': jid, 'humanStatus': 'in-process',
                                  'selectedHeld': 9, 'priorResult': payload['priorResult']})
    return subprocess.call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
        'run', '--lease-file', str(LEASE), '--', sys.executable, str(Path(__file__)), 'execute'], cwd=ROOT)


def execute():
    receipt, job = read(LEASE), read(LOCAL / 'job.json')
    assert reservations.owns(receipt) and jobs.heartbeat(job, lease_seconds=1800)
    payload = job['payload']
    inputs = read(PRIOR / 'support-inputs.json')
    def verify_inputs():
        for evidence in [payload['priorResult'], payload['priorChecks'], payload['inputs'],
                         *payload['scripts'], inputs['manifest'], *inputs['tileRefs'], *inputs['catalogueRefs']]:
            assert digest((ROOT / evidence['path']).read_bytes()) == evidence['sha256'], 'Input changed'
    try:
        verify_inputs()
        subprocess.run(['node', str(HERE / 'workflow-face-benchmark.mjs'),
                        str(PRIOR / 'support-checks.json'), str(PRIOR / 'support-inputs.json'),
                        str(DOC / 'source-face-checks.json.gz')], cwd=ROOT, check=True)
        verify_inputs()
        checks = read(DOC / 'source-face-checks.json.gz')
        assert all(r['completeBaselineEvidenceEqual'] for r in checks['rows'])
        rows = read(PRIOR / 'result.json')['rows']
        for row in rows:
            relevant = [r for r in checks['rows'] if r['uid'] == row['uid'] or r['supportUid'] == row['uid']]
            if relevant:
                row['freshSourceFaceLookup'] = {'evidence': ref(DOC / 'source-face-checks.json.gz'),
                    'rows': [{'uid': r['uid'], 'unresolvedSamples': r['unresolvedSamples'],
                              'sourceFacesLocated': r['sourceFacesLocated']} for r in relevant]}
        baseline = sum(r['benchmark']['baselineFullMs'] for r in checks['rows'])
        indexed = sum(r['benchmark']['indexedFullMs'] for r in checks['rows'])
        report = {'batch': BATCH, 'rows': rows, 'counts': {'installedInPilot': 1, 'heldUnknown': 9,
            'newlyInstalled': 0, 'heldAI': 0, 'heldHuman': 0, 'inProcess': 0},
            'remainingXLBatch': read(PRIOR / 'result.json')['remainingXLBatch'],
            'sourceFaceSamples': sum(r['unresolvedSamples'] for r in checks['rows']),
            'timing': {'baselineFullMs': baseline, 'indexedFullMs': indexed, 'speedup': baseline / indexed,
                       'qualification': 'Local CPU incident-face lookup only, including index build; not total model processing or viewer FPS.'},
            'priorResult': payload['priorResult'], 'evidenceRefs': [ref(DOC / 'source-face-checks.json.gz'),
                payload['priorChecks'], payload['inputs'], *payload['scripts']],
            'executor': 'Codex root; AI for reusable code/workflow only', 'scriptExternalAICalls': 0,
            'modelGeometryChanges': 0, 'publication': False,
            'qualification': 'Exact original source-face lookup accelerated; all pass/fail and held reasons remain. No architectural AI review, model edits, acceptance or installation.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, receipt)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                               (Jsonb(report), job['id'], job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (job['id'],)).fetchone()[0] == report
        save(DOC / 'result.json', report)
        save(DOC / 'neon-sync.json', {'jobId': job['id'], 'exactResultMatch': True,
            'sourceReservationFenced': True, 'reviewStatesUnchanged': True, 'result': ref(DOC / 'result.json')})
        checkpoint = read(DOC / 'checkpoint.json')
        checkpoint.update(humanStatus='complete', inProcess=0, result=ref(DOC / 'result.json'))
        save(DOC / 'checkpoint.json', checkpoint)
        print(json.dumps({'sourceFaceSamples': report['sourceFaceSamples'], 'timing': report['timing'], **report['counts']}), flush=True)
    except BaseException as error:
        jobs.finish(job, error=type(error).__name__ + ': ' + str(error), retry=False)
        raise


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'execute':
        execute()
    else:
        sys.exit(start())
