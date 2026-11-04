"""Link four completed investigations to source-specific resumable Neon holds.

Historical filings and model reviews stay unchanged. These new dispositions
record changed failure evidence, never installation or permanent rejection.
"""
import json
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row, NATIVE_RUN

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-four-current-hold-followups-20261008'
PRIOR = BASE / 'government-xl-held-second-pass-dispositions-20261008'
PAIR_CHECKPOINT = BASE / 'government-xl-three-original-pair-checkpoint-20261008'
LANGHAM = BASE / 'government-xl-langham-retained-grid-recovered-20261008'
SUPPORT = BASE / 'government-xl-five-provisional-installed-supports-20261007'
UIDS = {'landsd/259803:0', 'landsd/9778:0', 'landsd/232089:0', 'landsd/79318:0'}


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def verified(con, folder, historical_support=False):
    result = read(folder / 'result.json')
    assert read(folder / 'neon-sync.json') == {'jobId': result['jobId'], 'resultVerified': True}
    assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
        (result['jobId'],)).fetchone() == ('complete', result)
    changes = []
    for evidence in result['evidenceRefs']:
        current = ref(ROOT / evidence['path'])
        if current != evidence:
            assert historical_support and evidence['path'] in {
                '3d-viewer/city/data/manifest.json',
                'docs/astra-city/model-integration-20260909/current-source-review.json'}
            changes.append({'historical': evidence, 'current': current,
                'qualification': 'Historical publication context only; no current acceptance inferred.'})
    if historical_support:
        # The two publication pointers have advanced; the actual interface is
        # independent of terrain and remains bound to these exact source bytes.
        inputs = read(folder / 'support-inputs.json')
        rows = [r for r in inputs['sources'] if r['uid'] in {'landsd/79318:0', 'landsd/224399:0'}]
        assert len(rows) == 2
        for row in rows:
            assert digest((ROOT / row['candidate']['path']).read_bytes()) == row['sourceSHA256']
        source = read(LANGHAM / 'selection.json.gz')['rows'][0]
        assert source['sourceSHA256'] == next(r['sourceSHA256'] for r in rows if r['uid'] == 'landsd/79318:0')
        manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
        current = [m for url in manifest['officialModelCatalogues']
            for m in read(ROOT / '3d-viewer' / url)['models'] if m['uid'] == 'landsd/224399:0']
        assert len(current) == 1 and current[0]['sha256'] == next(
            r['sourceSHA256'] for r in rows if r['uid'] == 'landsd/224399:0')
        return result, changes
    return result


def main():
    doc = BASE / BATCH
    assert not doc.exists(), 'Completed source followups are immutable'
    prior = {r['uid']: r for r in read(PRIOR / 'dispositions.json.gz')['rows'] if r['uid'] in UIDS}
    assert set(prior) == UIDS
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        verified(con, PAIR_CHECKPOINT)
        langham = verified(con, LANGHAM)
        support, support_context_changes = verified(con, SUPPORT, historical_support=True)
    interface = next(r for r in support['rows'] if r['uid'] == 'landsd/79318:0')
    assert len(interface['interface']['unresolved']) == 4
    reasons = {
        'landsd/259803:0': ['isolated-source-coverage-below-95-percent',
            'exact-original-support-interface', 'paired-original-tower-terrain-penetration'],
        'landsd/9778:0': ['original-source-does-not-cover-whole-georef-cell',
            'exact-original-support-interface'],
        'landsd/232089:0': ['compound-spatial-bound:targetCoveredBySourceProjection',
            'exact-original-support-interface'],
        'landsd/79318:0': langham['reasons'] + ['four-original-shopping-mall-interface-failures'],
    }
    refs = [ref(Path(__file__)), ref(PRIOR / 'dispositions.json.gz'),
        ref(ROOT / '3d-viewer/city/data/manifest.json'),
        ref(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')]
    for folder in [PAIR_CHECKPOINT, LANGHAM, SUPPORT]:
        refs += [ref(folder / 'result.json'), ref(folder / 'neon-sync.json')]
    claim = reservations.claim('codex-four-source-followups-' + str(uuid.uuid4()),
        ['building:' + uid for uid in sorted(UIDS)], batch=BATCH)
    assert claim['ok'], claim
    lease, rows = claim['reservation'], []
    try:
        save(doc / 'historical-support-context.json', {'changes': support_context_changes,
            'exactCurrentSourceBytesVerified': True, 'currentInstallationApproval': False,
            'qualification': 'Original failed interface preserved on unchanged source bytes. '
                'Historical manifest/review pointers are not current acceptance proof.'})
        refs.append(ref(doc / 'historical-support-context.json'))
        for uid in sorted(UIDS):
            old = prior[uid]
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
            evidence = refs + [{'jobId': old['jobId'], 'resultSHA256': digest(json.dumps(
                old_result, sort_keys=True, separators=(',', ':')).encode())}]
            payload = {'uid': uid, 'sourceKey': old['sourceKey'], 'sourceSHA256': old['sourceSHA256'],
                'evidenceRefs': refs, 'previousDispositionJobId': old['jobId']}
            stage = 'xl-original-source-new-failure-followup-v1'
            jid = jobs.enqueue(BATCH, stage, payload)
            job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
            assert job and job['id'] == jid
            result = {**payload, 'jobId': jid, 'batch': BATCH,
                'nativeCacheKey': old['nativeCacheKey'], 'nativeResultSHA256': old['nativeResultSHA256'],
                'reasons': sorted(set(reasons[uid])), 'previousReasons': old['reasons'],
                'reasonGroup': 'component-support' if uid == 'landsd/79318:0' else 'source-identity-or-component-coverage',
                'humanStatus': 'held-unknown', 'state': 'held-for-second-pass',
                'activeWorkers': 0, 'queuedFollowups': 0, 'needsAIProcessing': None,
                'needsComputeProcessing': None, 'needsHumanDecision': False,
                'retainCurrentModel': True, 'revisitLater': True, 'permanentRejection': False,
                'evidence': evidence, 'newlyInstalled': 0, 'publication': False,
                'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
                'completedWork': 'Exact original source recovery and completed source-bound physical/identity diagnostics. '
                    'Langham additionally retains published hotel grid and original mall support evidence.',
                'nextStep': 'Changed exact component/source evidence or a demonstrated correction to the failed gate. '
                    'Reuse these completed checks; full fresh acceptance is required before installation.',
                'qualification': 'Technical hold with updated evidence, not corruption, permanent impossibility, '
                    'AI necessity, installation credit or a request for human decision.'}
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
            rows.append({'uid': uid, 'jobId': jid, 'resultVerified': True, 'reasons': result['reasons']})
            print({'uid': uid, 'jobId': jid, 'neonVerified': True}, flush=True)
        save(doc / 'neon-sync.json', {'rows': rows, 'allResultsVerified': True})
        save(doc / 'result.json', {'batch': BATCH, 'rows': rows, 'newlyInstalled': 0,
            'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
            'activeWorkers': 0, 'queuedFollowups': 0,
            'qualification': 'All four new per-source dispositions are verified in Neon. '
                'Aggregate is a local index of those authoritative leaf receipts.'})
    finally:
        reservations.release(lease)


if __name__ == '__main__':
    main()
