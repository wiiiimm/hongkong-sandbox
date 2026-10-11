"""Bounded actual-viewer geometry diagnostic; never changes model acceptance."""
import json
import subprocess
import uuid
from pathlib import Path
from run import ROOT, read, save, digest, connect, reservations, jobs, Jsonb, dict_row

DIR = ROOT / 'source-scripts/city/government-import'
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-open-sided-neighbour-diagnostic-20261007'

def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

def main():
    doc = BASE / BATCH
    assert not (doc / 'result.json').exists(), 'Reuse completed evidence'
    backlog = BASE / 'government-xl-additional-interpolation-checkpoint-20261007/backlog.json'
    held = {r['uid'] for r in read(backlog)['rows']}
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    installed = {r['uid'] for url in manifest['officialModelCatalogues']
                 for r in read(ROOT / '3d-viewer' / url)['models']}
    assert not held.intersection(installed)
    rows = []
    for path in sorted(BASE.glob('government-xl-*-20261007*/neighbour-checks.json')):
        source = path.parent / 'neighbour-inputs.json.gz'
        if not source.exists():
            continue
        selection = read(source)
        if not set(selection.get('candidateIds', [])).intersection(held):
            continue
        failures = {r['uid'] for r in read(path)['rows'] if r['reasons']
                    and not r.get('existingNative') and not r.get('candidate')}
        neighbours = [r['building']['uid'] for r in selection['rows']
                      if r['building']['uid'] in failures
                      and r['building'].get('structureType') == 'Open-sided Structure']
        if neighbours:
            rows.append({'document': str(path.parent.relative_to(ROOT)), 'neighbours': neighbours,
                         'candidateIds': selection['candidateIds']})
    assert rows
    save(doc / 'selection.json', {'rows': rows, 'publication': False})
    subprocess.run(['node', str(DIR / 'xl-open-sided-neighbour-diagnostic.mjs'),
                    str(doc.relative_to(ROOT))], cwd=ROOT, check=True)
    diagnostic = read(doc / 'geometry-checks.json')
    refs = [ref(Path(__file__)), ref(backlog), ref(doc / 'geometry-checks.json')]
    refs.extend({'path': path, 'sha256': sha} for path, sha in diagnostic['inputHashes'].items())
    scope = sorted({uid for row in rows for uid in [*row['candidateIds'], *row['neighbours']]})
    claim = reservations.claim('codex-xl-rendered-roofs-' + str(uuid.uuid4()),
                               ['building:' + uid for uid in scope], batch=BATCH)
    assert claim['ok']
    lease = claim['reservation']
    try:
        for evidence in refs:
            assert ref(ROOT / evidence['path']) == evidence
        payload = {'uids': scope, 'evidenceRefs': refs}
        stage = 'actual-rendered-open-sided-neighbour-diagnostic-v1'
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'batch': BATCH, 'jobId': jid,
                  'pairs': len(diagnostic['rows']),
                  'actualPartRegressionPassed': sum(r['actualPartRegressionPassed'] for r in diagnostic['rows']),
                  'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0,
                  'scriptExternalAICalls': 0, 'activeWorkers': 0, 'queuedFollowups': 0,
                  'qualification': diagnostic['qualification']}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for evidence in refs:
                assert ref(ROOT / evidence['path']) == evidence
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print(json.dumps({k: result[k] for k in ['jobId', 'pairs', 'actualPartRegressionPassed', 'newlyInstalled']}), flush=True)
    finally:
        reservations.release(lease)

if __name__ == '__main__':
    main()
