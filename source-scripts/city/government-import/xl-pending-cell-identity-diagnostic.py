"""Verify original identity for four pinned empty pending reviews; no review decisions."""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
from collections import Counter
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, dict_row, Jsonb, NATIVE_RUN
from government_georef_cell_identity import verify_files, POLICY


def verify_native(con, sources):
    for row in sources:
        n = row['native']
        actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, n['cacheKey'])).fetchone()
        assert actual and actual[0] == n['resultSha']


def owned(args, doc, local):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    base = ROOT / args.base
    selection = read(base / 'check-selection.json.gz')
    sources = selection['rows']
    assert 1 <= len(sources) <= 100 and len({r['uid'] for r in sources}) == len(sources)
    contexts = {r['uid']: r for r in read(base / 'context.json.gz')['rows']}
    paths = [base / 'check-selection.json.gz', base / 'context.json.gz', base / 'preflight.json',
             Path(__file__), HERE / 'pending_original_review.py', HERE / 'test_pending_original_review.py', HERE / 'original_source_ownership.py', HERE / 'government_georef_cell_identity.py',
             HERE / 'test_government_georef_cell_identity.py', HERE / 'xl-second-pass.py', HERE / 'xl-final-script-pass.py']
    refs = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())} for p in paths]
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        verify_native(con, sources)
        from pending_original_review import verify
        for row in sources: verify(con, row['uid'], row['sourceSHA256'], row['currentReview'])
    rows = []
    for row in sources:
        assert reservations.owns(lease)
        result = verify_files(row, contexts[row['uid']], local / 'identity' / row['uid'].split('/')[1].replace(':', '-'))
        result.update(nativeCacheKey=row['native']['cacheKey'], nativeResultSHA256=row['native']['resultSha'],
                      modelGeometryChanges=0, scriptExternalAICalls=0, requiresAI=False, requiresHumanDecision=False)
        path = doc / (row['uid'].split('/')[1].replace(':', '-') + '.json.gz')
        save(path, result)
        refs.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())})
        rows.append(result)
        print(json.dumps({'uid': row['uid'], 'positiveIdentityPassed': result['passed'], 'reasons': result['reasons']}), flush=True)
    payload = {'evidenceRefs': refs, 'identityPolicy': POLICY, 'runnerSHA256': digest(Path(__file__).read_bytes())}
    stage = 'explicit-fresh-full-georef-cell-original-identity-v1'
    jobid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jobid
    result = {**payload, 'jobId': jobid, 'batch': args.batch, 'rows': rows, 'sourcesChecked': len(rows),
              'positiveIdentityPassed': sum(r['passed'] for r in rows),
              'reasonCounts': dict(Counter(reason for r in rows for reason in r['reasons'])),
              'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0,
              'scriptExternalAICalls': 0, 'activeWorkers': 0, 'queuedFollowups': 0,
              'qualification': 'Original full-cell identity diagnostics only. All existing current coverage/extent/unrelated-form and physical/runtime/publication gates stay mandatory; no installation credit.'}
    for ref in refs:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        verify_native(con, sources)
        for row in sources: verify(con, row['uid'], row['sourceSHA256'], row['currentReview'])
        con.row_factory = dict_row
        assert reservations._current(con, lease)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'jobId': jobid, 'sourcesChecked': len(rows), 'positiveIdentityPassed': result['positiveIdentityPassed'], 'newlyInstalled': 0, 'neonVerified': True}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', required=True)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        owned(args, doc, local)
        return
    assert not doc.exists(), 'Fresh explicit diagnostic only'
    rows = read(ROOT / args.base / 'check-selection.json.gz')['rows']
    claim = reservations.claim('codex-xl-explicit-cell-' + str(uuid.uuid4()), ['building:' + r['uid'] for r in rows], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
