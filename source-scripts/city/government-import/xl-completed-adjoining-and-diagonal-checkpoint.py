"""Archive completed diagnostics and University Hall's physical holds in Neon.

This fences existing evidence only. It neither recomputes model geometry nor
changes a model review or grants installation credit.
"""
import uuid
from pathlib import Path
from run import ROOT, read, save, digest, reservations, jobs, connect, Jsonb, dict_row

DIR = ROOT / 'source-scripts/city/government-import'
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-completed-adjoining-and-diagonal-checkpoint-20261007'

def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

def main():
    doc = BASE / BATCH
    assert not doc.exists()
    refs = [ref(Path(__file__))]
    uids = set()
    summaries = []
    for name in ['government-xl-adjoining-current-tin-preview-20261007',
                 'government-xl-original-dtm-diagonal-preview-20261007']:
        path = BASE / name / 'result.json'
        result = read(path)
        assert result['diagnosticOnly'] and not result['publication']
        assert result['newlyInstalled'] == result['modelGeometryChanges'] == result['scriptExternalAICalls'] == 0
        for evidence in result.get('evidenceRefs', []):
            assert ref(ROOT / evidence['path']) == evidence
        for path_name, sha in result.get('inputHashes', {}).items():
            assert digest((ROOT / path_name).read_bytes()) == sha
        refs.append(ref(path))
        uids.update(row['uid'] for row in result['rows'])
        positive = [row['uid'] for row in result['rows'] if
                    row.get('highestOriginalTINPositive') or row.get('mixedOriginalPointwisePositive')
                    or row.get('coherentCellDiagonalPositive')]
        summaries.append({'batch': name, 'models': len(result['rows']), 'positive': positive,
                          'newOpportunities': 0, 'qualification': result['qualification']})
    sequence = BASE / 'government-xl-university-hall-original-followthrough-20261007' / 'commands.json'
    commands = read(sequence)
    assert commands['activeWorkers'] == commands['queuedFollowups'] == commands['newlyInstalled'] == 0
    refs.append(ref(sequence))
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for row in commands['rows']:
            uids.add(row['uid'])
            for step in row['steps']:
                result = step['result']; assert result is not None
                phase = BASE / step['batch']
                assert read(phase / 'result.json') == result
                assert read(phase / 'neon-sync.json')['resultVerified']
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                                   (result['jobId'],)).fetchone() == ('complete', result)
                for evidence in result['evidenceRefs']:
                    assert ref(ROOT / evidence['path']) == evidence
                refs.extend([ref(phase / 'result.json'), ref(phase / 'neon-sync.json')])
            summaries.append({'uid': row['uid'], 'name': row['name'], 'installed': False,
                              'reasons': row['steps'][-1]['result']['reasons']})
    claim = reservations.claim('codex-completed-diagnostics-' + str(uuid.uuid4()),
                               ['building:' + uid for uid in sorted(uids)], batch=BATCH)
    assert claim['ok']; lease = claim['reservation']
    try:
        stage = 'completed-adjoining-and-diagonal-evidence-v1'
        payload = {'uids': sorted(uids), 'evidenceRefs': refs}
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'jobId': jid, 'batch': BATCH, 'summaries': summaries,
                  'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0,
                  'scriptExternalAICalls': 0, 'activeWorkers': 0,
                  'qualification': 'Completed evidence archive only. Beverly Hill K was already a known DTM positive and retains its original support hold; no new installation opportunity or review credit.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for evidence in refs: assert ref(ROOT / evidence['path']) == evidence
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                               (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print({'jobId': jid, 'sources': len(uids), 'newlyInstalled': 0}, flush=True)
    finally:
        reservations.release(lease)

if __name__ == '__main__':
    main()
