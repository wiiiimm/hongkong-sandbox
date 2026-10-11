"""Record a terminated stale-input attempt as a technical result, never acceptance."""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN


def owned(args, doc, local):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    previous = (ROOT / args.previous).resolve()
    assert previous.is_relative_to(ROOT / 'docs/astra-city/government-import')
    prior = read(HERE / 'local' / previous.name / 'reservation.json')
    assert not reservations.owns(prior), 'Previous source worker still owns this source'
    assert not (previous / 'result.json').exists(), 'Completed outcomes are immutable'
    row = next(r for r in read(ROOT / args.base / 'check-selection.json.gz')['rows'] if r['uid'] == args.uid)
    assert digest((ROOT / row['candidate']['path']).read_bytes()) == row['sourceSHA256']
    metrics = read(previous / 'metrics.json')
    assert len(metrics['rows']) == 1 and metrics['rows'][0]['uid'] == args.uid
    assert read(previous / 'owned-source-identity.json')['passed']
    changes = []
    current = {}
    for path, pinned in metrics['inputHashes'].items():
        actual = digest((ROOT / path).read_bytes())
        current[path] = actual
        if actual != pinned:
            changes.append({'path': path, 'pinnedSHA256': pinned, 'currentSHA256': actual})
    assert changes, 'A stale attempt must have an explicit changed input'
    # Do not promote any old numeric checks, native resolutions or identity proof.
    # The entire attempt stays unusable for installation after any input change.
    save(doc / 'stale-attempt.json', {
        'uid': args.uid, 'sourceSHA256': row['sourceSHA256'], 'changedInputs': changes,
        'previousReservationReleased': True, 'previousBatch': previous.name,
        'installationEvidenceUsable': False, 'fullFreshRecheckRequired': True,
        'qualification': 'Preserved completed computation from a terminated stale-input attempt. No check is current acceptance; original outputs remain immutable.'})
    refs = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
            for p in sorted(previous.iterdir()) if p.is_file()]
    refs += [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
             for p in [Path(__file__), doc / 'stale-attempt.json', ROOT / args.base / 'check-selection.json.gz']]
    payload = {'uid': args.uid, 'sourceSHA256': row['sourceSHA256'], 'evidenceRefs': refs,
               'runnerSHA256': digest(Path(__file__).read_bytes()), 'changedInputs': changes}
    stage = 'terminated-stale-original-terrain-evidence-v1'
    jobid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jobid
    result = {**payload, 'jobId': jobid, 'batch': args.batch, 'humanStatus': 'in-process',
              'reasons': ['stale-inputs-require-full-fresh-recheck'], 'scriptChecksPassed': False,
              'publication': False, 'newlyInstalled': 0, 'modelGeometryChanges': 0,
              'scriptExternalAICalls': 0, 'activeWorkers': 0, 'queuedFollowups': 1,
              'requiresAI': False, 'requiresHumanDecision': False,
              'nextStep': 'Use exact recorded original support evidence, then rerun all source/terrain/neighbour/runtime gates against a fresh pinned manifest before any installation.'}
    for ref in refs:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    for path, sha in current.items():
        assert digest((ROOT / path).read_bytes()) == sha, 'Inputs changed during stale-result sync'
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, lease)
        actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchone()
        assert actual and actual['result_sha'] == row['native']['resultSha']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'jobId': jobid, 'neonVerified': True, 'changedInputs': changes, 'newlyInstalled': 0}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['previous', 'base', 'uid', 'batch']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        owned(args, doc, local)
        return
    assert not doc.exists(), 'Fresh diagnostic sync only'
    claim = reservations.claim('codex-xl-stale-sync-' + str(uuid.uuid4()), ['building:' + args.uid], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
