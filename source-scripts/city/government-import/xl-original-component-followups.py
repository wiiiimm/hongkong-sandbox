"""Persist completed exact component checks as resumable source-specific holds.

This does not approve, publish, mutate model reviews or grant installation credit.
Every requested source must match an existing XL disposition and a verified
complete closure on identical source bytes. Historical reasons stay available.
"""
import argparse
import json
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row, NATIVE_RUN

BASE = ROOT / 'docs/astra-city/government-import'
PRIOR = BASE / 'government-xl-held-second-pass-dispositions-20261008'


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def verified(con, folder):
    result = read(folder / 'result.json')
    assert read(folder / 'neon-sync.json') == {'jobId': result['jobId'], 'resultVerified': True}
    assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                       (result['jobId'],)).fetchone() == ('complete', result)
    assert not result['publication'] and result['newlyInstalled'] == 0
    assert result['modelGeometryChanges'] == result['scriptExternalAICalls'] == 0
    for item in result['evidenceRefs']:
        assert ref(ROOT / item['path']) == item
    return result


def source_interfaces(uid, original, sources, interfaces):
    """Reject cross-source receipts and never turn support probes into acceptance."""
    assert uid in sources and sources[uid]['sourceSHA256'] == original['sourceSHA256']
    rows = [row for row in interfaces if row['uid'] == uid]
    assert rows, 'No complete component interface for requested source'
    for row in rows:
        assert row['sourceSHA256'] == original['sourceSHA256']
        assert row['supportSHA256'] == sources[row['supportUid']]['sourceSHA256']
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--closure', required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--uid', action='append', required=True)
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    closure = (ROOT / args.closure).resolve()
    assert closure.parent == BASE
    doc = BASE / args.batch
    assert not doc.exists(), 'Completed source followups are immutable'
    wanted = set(args.uid)
    assert len(wanted) == len(args.uid)
    old_rows = {r['uid']: r for r in read(PRIOR / 'dispositions.json.gz')['rows'] if r['uid'] in wanted}
    assert set(old_rows) == wanted
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        prior = verified(con, closure)
    sources = {r['uid']: r for r in read(closure / 'support-inputs.json')['sources']}
    checks = read(closure / 'support-checks.json.gz')['rows']
    # All bindings are validated before any reservation or job is created.
    selected = {uid: source_interfaces(uid, old, sources, checks) for uid, old in old_rows.items()}
    refs = [ref(Path(__file__)), ref(PRIOR / 'dispositions.json.gz'),
            ref(closure / 'result.json'), ref(closure / 'neon-sync.json')]
    refs += prior['evidenceRefs']
    claim = reservations.claim('codex-xl-component-followups-' + str(uuid.uuid4()),
        ['building:' + uid for uid in sorted(wanted)], batch=args.batch)
    assert claim['ok'], claim
    lease, rows = claim['reservation'], []
    try:
        for uid in sorted(wanted):
            old, components = old_rows[uid], selected[uid]
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                status, old_result = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                                                (old['jobId'],)).fetchone()
                assert status == 'complete'
                for key in ['uid', 'sourceKey', 'sourceSHA256', 'nativeCacheKey', 'nativeResultSHA256']:
                    assert old_result[key] == old[key]
                assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
                    'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                    'WHERE m.run_id=%s AND r.cache_key=%s',
                    (NATIVE_RUN, old['nativeCacheKey'])).fetchone() == (old['nativeResultSHA256'],)
            failed = [r for r in components if not r['interface']['passed']]
            reasons = sorted(set(old['reasons'] + [
                'exact-original-component-interface:' + r['supportUid'] for r in failed]))
            payload = {'uid': uid, 'sourceKey': old['sourceKey'], 'sourceSHA256': old['sourceSHA256'],
                'evidenceRefs': refs, 'previousDispositionJobId': old['jobId'], 'closureJobId': prior['jobId']}
            stage = 'xl-original-source-component-followup-v1'
            jid = jobs.enqueue(args.batch, stage, payload)
            job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
            assert job and job['id'] == jid
            result = {**payload, 'jobId': jid, 'batch': args.batch,
                'nativeCacheKey': old['nativeCacheKey'], 'nativeResultSHA256': old['nativeResultSHA256'],
                'reasons': reasons, 'previousReasons': old['reasons'],
                'componentChecks': [{'supportUid': r['supportUid'], 'supportSHA256': r['supportSHA256'],
                    'passed': r['interface']['passed'], 'samples': r['interface']['samples'],
                    'strictContacts': r['interface']['strictContacts'],
                    'wallIntersections': r['interface']['wallIntersections'],
                    'unresolvedSamples': len(r['interface']['unresolved'])} for r in components],
                'humanStatus': 'held-unknown', 'state': 'held-for-second-pass',
                'activeWorkers': 0, 'queuedFollowups': 0, 'needsAIProcessing': None,
                'needsComputeProcessing': None, 'needsHumanDecision': False,
                'retainCurrentModel': True, 'revisitLater': True, 'permanentRejection': False,
                'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
                'completedWork': 'Recovered unchanged exact government components and measured complete original support interfaces. Previous independent holds remain.',
                'nextStep': 'Changed exact component evidence or demonstrated correction to a failed gate; reuse completed checks and require full fresh acceptance before installation.',
                'qualification': 'Evidence followup only. No corruption, permanent impossibility, AI necessity or installation credit is inferred.'}
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
            save(doc / (uid.split('/')[1].replace(':', '-') + '.json'), result)
            rows.append({'uid': uid, 'jobId': jid, 'resultVerified': True, 'componentChecks': result['componentChecks']})
            print({'uid': uid, 'jobId': jid, 'neonVerified': True}, flush=True)
        save(doc / 'neon-sync.json', {'rows': rows, 'allResultsVerified': True})
        save(doc / 'result.json', {'batch': args.batch, 'rows': rows, 'newlyInstalled': 0,
            'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
            'activeWorkers': 0, 'queuedFollowups': 0,
            'qualification': 'Local index of verified source-specific Neon followups; no installation credit.'})
    finally:
        reservations.release(lease)


if __name__ == '__main__':
    main()
