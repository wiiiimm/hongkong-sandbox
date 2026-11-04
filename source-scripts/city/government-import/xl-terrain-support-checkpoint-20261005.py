"""Freeze completed source-fenced terrain/support results; never create a queue."""
import json
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row

BATCH = 'government-xl-terrain-support-continuation-20261005'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
BASE = ROOT / 'docs/astra-city/government-import'
CASES = {
    '10664': ('coronation-circle', 'terrain-continuation', 'support-migration'),
    '270142': ('stonecutters-pumping', 'terrain-continuation-v2', 'source-identity'),
    '11093': ('royal-green-3', 'terrain-continuation-v2', 'source-identity'),
    '198440': ('south-hillcrest', 'terrain-continuation-v2', 'source-identity'),
    '118230': ('two-harbourfront', 'terrain-continuation-v3', 'source-clearance'),
    '26653': ('ching-hin-house', 'terrain-continuation-v3', 'source-clearance'),
    '276187': ('hanford-plaza', 'terrain-continuation-v5', 'source-clearance'),
    '265480': ('ssp-swimming-pool', 'terrain-continuation-v2', 'source-clearance'),
    '313033': ('market-in', 'native-terrain-group', 'source-clearance'),
    '258470': ('unnamed-258470', 'native-terrain-group', 'support-migration'),
    '255415': ('wk-bus-terminus', 'native-terrain-group', 'support-migration'),
    '227099': ('west9zone-227099', 'native-terrain-group', 'support-migration'),
}
SUPPORTS = ['government-xl-coronation-supports-20261005',
            'government-xl-bus-terminus-original-support-group-20261005',
            'government-xl-west9zone-original-support-group-20261005',
            'government-xl-imperial-podium-original-support-group-20261005']


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def run():
    selected = {r['uid']: r for r in read(BASE / 'government-xl-next-100-20261005/check-selection.json.gz')['rows']}
    cohort = {r['uid'] for r in read(BASE / 'government-xl-remaining-20260923/selection.json.gz')['rows']}
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    rows, auxiliary, refs, completed = [], [], [ref(DOC / 'indexed-preflight.json')], []
    for num, (case, phase, category) in CASES.items():
        uid = 'landsd/' + num + ':0'
        folder = BASE / ('government-xl-' + case + '-' + phase + '-20261005')
        result, sync = read(folder / 'result.json'), read(folder / 'neon-sync.json')
        assert sync['resultVerified'] and sync['jobId'] == result['jobId']
        assert result['uid'] == uid and result['sourceSHA256'] == selected[uid]['sourceSHA256']
        assert result['humanStatus'] == 'held-unknown' and result['reasons']
        refs.extend([ref(folder / 'result.json'), ref(folder / 'neon-sync.json')])
        completed.append((result['jobId'], result))
        rows.append({'uid': uid, 'name': selected[uid]['name'], 'sourceSHA256': result['sourceSHA256'],
                     'humanStatus': 'held-unknown', 'category': category, 'reasons': result['reasons'],
                     'latestJobId': result['jobId'], 'requiresAIEstablished': False,
                     'requiresHumanDecisionEstablished': False,
                     'nextStep': 'Inspect exact source identity/component coverage before further terrain work.' if category == 'source-identity'
                     else 'Resolve saved original support closure and complete unchanged acceptance gates.' if category == 'support-migration'
                     else 'Resolve exact drawn-terrain/source clearance and affected neighbours without source edits or increased limits.'})
    for batch in SUPPORTS:
        folder = BASE / batch
        result, sync = read(folder / 'result.json'), read(folder / 'neon-sync.json')
        assert sync['resultVerified'] and sync['jobId'] == result['jobId']
        completed.append((result['jobId'], result))
        refs.extend([ref(folder / 'result.json'), ref(folder / 'neon-sync.json')])
        for source in result['rows']:
            auxiliary.append({**source, 'inXL352': source['uid'] in cohort,
                              'latestJobId': result['jobId'], 'publication': False})
    assert len(rows) == 12 and len(auxiliary) == 15
    assert len({r['uid'] for r in auxiliary}) == 15
    for _, result in completed:
        for evidence in result['evidenceRefs']:
            assert digest((ROOT / evidence['path']).read_bytes()) == evidence['sha256']
    preflight = read(DOC / 'indexed-preflight.json')
    for path, pinned in preflight['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == pinned
    resources = ['building:' + u for u in sorted({r['uid'] for r in rows + auxiliary})]
    claim = reservations.claim('codex-xl-terrain-checkpoint-' + str(uuid.uuid4()), resources, batch=BATCH)
    assert claim['ok'], claim
    receipt = claim['reservation']
    try:
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            for jobid, expected in completed:
                actual = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()
                assert actual and actual[0] == 'complete' and actual[1] == expected
            reviews = dict(con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s', (pointer['snapshotId'],)).fetchall())
        installed = sum(reviews.get(u) == 'installed-verified' for u in cohort)
        assert len(cohort) == 352 and installed == 42
        assert not any(reviews.get(r['uid']) == 'installed-verified' for r in rows + auxiliary)
        payload = {'evidenceRefs': refs, 'sourceCommit': __import__('subprocess').check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                   'pipelineSHA256': digest(Path(__file__).read_bytes()), 'reviewSnapshot': pointer['snapshotId']}
        stage = 'completed-original-terrain-support-continuation-v1'
        jobid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, receipt['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jobid
        result = {**payload, 'jobId': jobid, 'rows': rows, 'supportingSources': auxiliary,
                  'newlyInstalled': 0, 'primaryHeld': 12, 'recoveredOriginalMeshes': 15,
                  'supportInterfacesPassed': sum(r['interfacePassed'] for r in auxiliary),
                  'supportInterfacesHeld': sum(not r['interfacePassed'] for r in auxiliary),
                  'primaryReasons': {'source-identity': 3, 'source-clearance': 5, 'support-migration': 4},
                  'activeWorkers': 0, 'queuedFollowups': 0, 'humanInProcess': 0,
                  'scriptExternalAICalls': 0, 'sourceGeometryChanges': 0, 'publication': False,
                  'widerXLCheckpoint': {'models': 352, 'installed': installed, 'held': 352-installed},
                  'qualification': 'Twelve fresh primary continuations and fifteen exact original supporting sources checked. Two passing interfaces grant no installation credit. All remaining technical holds are saved; no blanket AI/human requirement, queue or backlog-completion claim.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, receipt)
            assert read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json') == pointer
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
        save(DOC / 'result.json', result)
        save(DOC / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
        print(json.dumps({'jobId': jobid, 'neonVerified': True, 'primaryHeld': 12, 'recovered': 15,
                          'interfacesPassed': result['supportInterfacesPassed'], 'installed': 0}), flush=True)
    finally:
        reservations.release(receipt)


if __name__ == '__main__':
    run()
