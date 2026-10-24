"""Finish acquired but interrupted component checks, preserving per-pair failures.

Only exact unchanged recovered originals are used. Runtime rejection stays a
hold and does not bypass decoding or identity guards. No installation credit.
"""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def inputs(prior):
    assert not (prior / 'result.json').exists(), 'Use completed evidence instead of repeating it'
    data = read(prior / 'support-inputs.json')
    context = read(prior / 'context.json.gz')
    contexts = {r['uid']: r for r in context['rows']}
    sources = {r['uid']: r for r in data['sources']}
    assert len(sources) == len(data['sources']) and set(sources) == set(contexts)
    assert {u for p in data['pairs'] for u in (p['uid'], p['supportUid'])} == set(sources)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for uid, row in sources.items():
            assert digest((ROOT / row['candidate']['path']).read_bytes()) == row['sourceSHA256']
            assert contexts[uid]['sourceSHA256'] == row['sourceSHA256']
            assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
            for tile, sha in contexts[uid]['neighbourTileHashes'].items():
                assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
            native = row['native']
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
                'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                'WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, native['cacheKey'])).fetchone() == (native['resultSha'],)
    return data, context


def owned(a, doc, local, prior):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    data, context = inputs(prior)
    save(doc / 'support-inputs.json', data)
    save(doc / 'context.json.gz', context)
    save(doc / 'recovery.json', read(prior / 'recovery.json'))
    save(doc / 'continuation.json', {'interruptedInputRefs': [ref(prior / name) for name in
        ['support-inputs.json', 'context.json.gz', 'selection.json.gz', 'recovery.json']],
        'modelGeometryChanges': 0, 'transferredBytes': 0,
        'qualification': 'Original source acquisition is complete; earlier end-only interface writer failed before saving results. Incremental evidence now isolates runtime rejections.'})
    subprocess.run(['node', str(HERE / 'original-support-closure-interfaces-incremental.mjs'),
                    str(doc.relative_to(ROOT)) + '/'], cwd=ROOT, check=True)
    checks = read(doc / 'support-checks.json.gz')
    assert len(checks['rows']) == len(data['pairs'])
    assert {(r['uid'], r['supportUid']) for r in checks['rows']} == {(r['uid'], r['supportUid']) for r in data['pairs']}
    for path, sha in checks['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
    sources = {r['uid']: r for r in data['sources']}
    outcomes = []
    for row in checks['rows']:
        assert row['sourceSHA256'] == sources[row['uid']]['sourceSHA256']
        assert row['supportSHA256'] == sources[row['supportUid']]['sourceSHA256']
        interface = row['interface']
        reasons = ['support-terrain-foundation-runtime-publication-not-complete']
        if interface is None:
            assert row['loadFailure']['reason'] == 'runtime-source-footprint-fit'
            assert row['loadFailure']['uid'] in (row['uid'], row['supportUid'])
            reasons.append('runtime-source-footprint-fit:' + row['loadFailure']['uid'])
        elif not interface['passed']:
            reasons.append('original-support-interface-unresolved')
        outcomes.append({k: row[k] for k in ('uid', 'supportUid', 'sourceSHA256', 'supportSHA256')} | {
            'humanStatus': 'held-unknown', 'reasons': reasons,
            'interfaceChecked': interface is not None,
            'interfacePassed': interface['passed'] if interface else False,
            'samples': interface['samples'] if interface else None,
            'strictContacts': interface['strictContacts'] if interface else None,
            'unresolvedSamples': len(interface['unresolved']) if interface else None,
            'loadFailure': row.get('loadFailure'),
            'nextStep': 'Reuse original acquisition and exact completed contact evidence. Resolve recorded runtime/component failures; full source identity, physical, neighbour, browser and publication acceptance remain.',
            'requiresAI': False, 'requiresHumanDecision': False})
    refs = [ref(p) for p in sorted(doc.iterdir()) if p.is_file()] + [ref(Path(__file__))]
    refs += [{'path': path, 'sha256': sha} for path, sha in checks['inputHashes'].items()]
    payload = {'evidenceRefs': refs, 'runnerSHA256': digest(Path(__file__).read_bytes())}
    stage = 'recovered-original-component-closure-incremental-v1'
    jid = jobs.enqueue(a.batch, stage, payload)
    job = jobs.claim(a.batch, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    result = {**payload, 'jobId': jid, 'batch': a.batch, 'rows': outcomes,
        'recoveredOriginalMeshes': len(sources), 'interfacesChecked': sum(r['interfaceChecked'] for r in outcomes),
        'interfacesPassed': sum(r['interfacePassed'] for r in outcomes),
        'runtimeRejectedPairs': sum(not r['interfaceChecked'] for r in outcomes),
        'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
        'activeWorkers': 0, 'queuedFollowups': 0,
        'qualification': 'Interrupted diagnostic recovery only; native identities, full physical and publication gates remain separate. Runtime-rejected interfaces are explicitly untested.'}
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
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
    print({'jobId': jid, 'neonVerified': True, 'interfacesPassed': result['interfacesPassed'],
           'runtimeRejectedPairs': result['runtimeRejectedPairs']}, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prior', required=True)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert Path(a.batch).name == a.batch and a.batch.startswith('government-xl-')
    prior = (ROOT / a.prior).resolve()
    assert prior.parent == ROOT / 'docs/astra-city/government-import'
    doc, local = prior.parent / a.batch, HERE / 'local' / a.batch
    if a.owned:
        return owned(a, doc, local, prior)
    assert not doc.exists(), 'Fresh immutable recovery only'
    data, _ = inputs(prior)
    claim = reservations.claim('codex-xl-recovered-components-' + str(uuid.uuid4()),
        ['building:' + r['uid'] for r in data['sources']], batch=a.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
        '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
