"""Prepare original mesh/footprint captures for a separately authorised identity review.

No architectural judgement, source edits, acceptance or publication.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row, NATIVE_RUN


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def inputs(previous):
    prior = read(previous / 'result.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (prior['jobId'],)).fetchone() == ('complete', prior)
    for item in prior['evidenceRefs']:
        assert ref(ROOT / item['path']) == item
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == prior['currentManifestSHA256']
    paths = [ROOT / r['path'] for r in prior['evidenceRefs'] if r['path'].endswith('/physical-selection.json.gz')]
    assert len(paths) == 1
    selection = read(paths[0]); selected = {r['uid']: r for r in selection['rows']}
    spec = importlib.util.spec_from_file_location('current_overlay_context', HERE / 'xl-final-script-pass.py')
    final = importlib.util.module_from_spec(spec); spec.loader.exec_module(final)
    hashes = {item['path']: item['sha256'] for item in prior['evidenceRefs']}
    for path in [Path(__file__), HERE / 'render-source-footprint-evidence.mjs', HERE / 'xl-final-script-pass.py', previous / 'result.json']:
        hashes[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    models, scope = [], set()
    for classified in prior['rows']:
        row = selected[classified['uid']]
        assert row['sourceSHA256'] == classified['sourceSHA256']
        lo, hi = row['candidate']['entry']['worldBounds']
        forms = final.load_forms([lo[0]-2, lo[2]-2, hi[0]+2, hi[2]+2])
        assert row['source']['building'] in [b for b, _, _ in forms]
        for b, _, url in forms:
            scope.add(b['uid'])
            path = ROOT / '3d-viewer' / url
            hashes[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        scope.add(row['uid'])
        models.append({'uid': row['uid'], 'name': row['source']['building'].get('name'), 'modelId': row['modelId'],
            'sourceSHA256': row['sourceSHA256'], 'assetPath': row['candidate']['path'],
            'worldBounds': [lo, hi], 'triangles': row['triangles'],
            'nativeCacheKey': row['native']['cacheKey'], 'nativeResultSHA256': row['native']['resultSha'],
            'forms': [b for b, _, _ in forms]})
    return {'previousJobId': prior['jobId'], 'models': models, 'inputHashes': hashes,
            'publication': False, 'architectureReview': False, 'installationApproved': False}, scope


def owned(args, doc, local):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    frozen = read(doc / 'inputs.json')
    current, _ = inputs(ROOT / args.previous)
    assert current == frozen, 'Capture inputs changed'
    subprocess.run(['node', str(HERE / 'render-source-footprint-evidence.mjs'), '--inputs', str((doc / 'inputs.json').relative_to(ROOT)),
                    '--out', str(doc.relative_to(ROOT))], cwd=ROOT, check=True)
    assert reservations.owns(lease)
    render = read(doc / 'render.json')
    assert not render['errors'] and len(render['views']) == len(frozen['models'])
    for path, pinned in render['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == pinned
    refs = [ref(p) for p in sorted(doc.iterdir()) if p.is_file()]
    payload = {'previousJobId': frozen['previousJobId'], 'evidenceRefs': refs,
               'sourceSHA256s': {r['uid']: r['sourceSHA256'] for r in frozen['models']}}
    stage = 'original-source-current-footprint-render-evidence-v1'
    jid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    result = {**payload, 'jobId': jid, 'batch': args.batch, 'sourcesCaptured': len(render['views']),
              'views': render['views'], 'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0,
              'scriptExternalAICalls': 0, 'architectureReview': False, 'installationApproved': False,
              'activeWorkers': 0, 'queuedFollowups': 0,
              'nextStep': 'Inspect exported capture framing. Architectural/source identity review requires its separate applicable authorisation; all physical and publication checks still apply.',
              'qualification': render['qualification']}
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        for model in frozen['models']:
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, model['nativeCacheKey'])).fetchone() == (model['nativeResultSHA256'],)
        con.row_factory = dict_row
        assert reservations._current(con, lease)
        for item in refs:
            assert ref(ROOT / item['path']) == item
        for path, pinned in render['inputHashes'].items():
            assert digest((ROOT / path).read_bytes()) == pinned
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone()[0] == result
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
    print({'sourcesCaptured': len(render['views']), 'jobId': jid, 'neonVerified': True, 'newlyInstalled': 0}, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous', required=True); p.add_argument('--batch', required=True); p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        owned(args, doc, local)
        return
    assert not doc.exists() and not local.exists(), 'Fresh evidence only'
    frozen, scope = inputs(ROOT / args.previous)
    claim = reservations.claim('codex-xl-original-footprint-capture-' + str(uuid.uuid4()),
        [('building:' if uid.startswith('landsd/') else 'source-form:') + uid for uid in sorted(scope)], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    save(doc / 'inputs.json', frozen)
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(local / 'reservation.json'),
        '--', sys.executable, __file__, '--previous', args.previous, '--batch', args.batch, '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
