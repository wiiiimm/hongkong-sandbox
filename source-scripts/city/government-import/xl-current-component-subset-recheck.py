"""Fresh physical checks after a demonstrated runtime correction; no acceptance.

Reuse exact originals and old selection metadata, but bind fresh runtime code,
manifest and complete metrics. Previous failed evidence stays historical.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row, NATIVE_RUN


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-selection', action='append', required=True)
    parser.add_argument('--count', required=True)
    parser.add_argument('--uid', action='append', required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and Path(args.batch).name == args.batch
    wanted = set(args.uid)
    assert len(wanted) == len(args.uid) and 1 <= len(wanted) <= 20
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    assert not (doc / 'result.json').exists(), 'Completed checks are immutable'
    count_path = ROOT / args.count
    count = read(count_path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == count['manifestSHA256']
    remaining = {r['uid']: r for r in count['rows'] if not r['installedVerified'] and r['uid']}
    assert wanted <= remaining.keys()
    selected, paths = {}, [count_path, manifest, Path(__file__)]
    for filename in args.source_selection:
        path = ROOT / filename
        paths.append(path)
        for row in read(path)['rows']:
            if row['uid'] not in wanted:
                continue
            if row['uid'] in selected:
                assert selected[row['uid']] == row
            selected[row['uid']] = row
    assert set(selected) == wanted
    lease_path = local / 'reservation.json'
    if not args.owned:
        assert not local.exists(), 'Fresh runtime-check cache required'
        claim = reservations.claim('codex-xl-runtime-correction-' + str(uuid.uuid4()),
            ['building:' + uid for uid in sorted(wanted)], batch=args.batch)
        assert claim['ok'], claim
        save(lease_path, json.loads(json.dumps(claim['reservation'], default=str)))
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
            'run', '--lease-file', str(lease_path), '--', sys.executable, __file__,
            *sys.argv[1:], '--owned'], cwd=ROOT, check=True)
        return
    lease = read(lease_path)
    assert reservations.owns(lease)
    rows = []
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert not con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=ANY(%s)',
                               (sorted(wanted),)).fetchall(), 'Reviewed source requires explicit continuation'
        for uid, earlier in sorted(selected.items()):
            row = json.loads(json.dumps(earlier))
            native = row['native']
            assert row['sourceKey'] == remaining[uid]['sourceKey']
            assert row['sourceSHA256'] == remaining[uid]['indexedSourceSHA256']
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
                'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                'WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, native['cacheKey'])).fetchone() == (native['resultSha'],)
            old = Path(row['candidate']['path'])
            old = old if old.is_absolute() else ROOT / old
            assert digest(old.read_bytes()) == row['sourceSHA256']
            assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
            asset = local / row['candidate']['entry']['asset']
            assert asset.is_relative_to(local)
            asset.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(old, asset)
            row['candidate']['path'] = str(asset.relative_to(ROOT))
            paths.append(asset)
            rows.append(row)
    selection = doc / 'physical-selection.json.gz'
    save(selection, {'batch': args.batch, 'nativeRun': NATIVE_RUN,
        'manifestSHA256': count['manifestSHA256'], 'rows': rows})
    save(doc / 'terrain-candidates.json', [])
    command = ['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', str(selection.relative_to(ROOT)),
        '--candidates', str(local.relative_to(ROOT)), '--terrain-candidates', str((doc / 'terrain-candidates.json').relative_to(ROOT)),
        '--out', str((doc / 'current-metrics.json').relative_to(ROOT)),
        '--geometry-out', str((local / 'current-runtime-geometry.json.gz').relative_to(ROOT))]
    save(doc / 'metrics-command.json', command)
    subprocess.run(command, cwd=ROOT, check=True)
    metrics = read(doc / 'current-metrics.json')
    geometry_path = local / 'current-runtime-geometry.json.gz'
    geometry = {r['uid']: r for r in read(geometry_path)['rows']}
    measured = {r['uid']: r for r in metrics['rows']}
    assert set(measured) == wanted
    for path, sha in metrics['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
    helper_path = HERE / 'xl-held-component-current-checks.py'
    spec = importlib.util.spec_from_file_location('fresh_component_physical', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    outcomes = []
    for row in rows:
        assert reservations.owns(lease)
        outcome = helper.check_one(row, measured[row['uid']], geometry.get(row['uid']), metrics['profiles']['mobile'])
        outcomes.append(outcome)
        print(json.dumps({'uid': row['uid'], 'passed': outcome['scriptChecksPassed'],
            'samplerDelta': outcome['metric'].get('maxSamplerDelta'), 'reasons': outcome['reasons']}), flush=True)
    save(doc / 'physical-results.json.gz', {'rows': outcomes})
    paths += [selection, doc / 'terrain-candidates.json', doc / 'metrics-command.json',
        doc / 'current-metrics.json', doc / 'physical-results.json.gz', geometry_path, helper_path,
        HERE / 'xl-final-script-pass.py', HERE / 'acceptance-policy.py',
        HERE / 'component_type_resolution.py', HERE / 'original_source_ownership.py',
        HERE / 'government_georef_cell_identity.py']
    refs = [ref(p) for p in paths]
    refs += [{'path': p, 'sha256': sha} for p, sha in metrics['inputHashes'].items()]
    payload = {'uids': sorted(wanted), 'evidenceRefs': refs}
    stage = 'fresh-xl-component-physical-checks-after-runtime-correction-v1'
    jid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    result = {**payload, 'jobId': jid, 'batch': args.batch, 'rows': outcomes,
        'checked': len(outcomes), 'passes': sum(r['scriptChecksPassed'] for r in outcomes),
        'fullXLCounts': count['counts'], 'newlyInstalled': 0, 'publication': False,
        'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
        'qualification': 'Fresh exact-original identity/contact/foundation/runtime measurements after code correction. Previous results stay historical. Passing does not grant installation, browser or publication acceptance.'}
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
    print(json.dumps({'jobId': jid, 'checked': len(outcomes), 'passes': result['passes'], 'newlyInstalled': 0}), flush=True)


if __name__ == '__main__':
    main()
