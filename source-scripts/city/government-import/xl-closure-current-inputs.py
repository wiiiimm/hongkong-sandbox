"""Freeze current, never-reviewed originals from one exact support closure.

Identity qualification is diagnostic only. Preserve all cached matching failures;
do not alter native records, model geometry, reviews or publication flags.
"""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path

from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN
from government_georef_cell_identity import verify_files
from publication_lock import locked_publication


def reference(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def owned(args, doc, local):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    closure = ROOT / args.closure
    result = read(closure / 'result.json')
    assert result['publication'] is False and result['newlyInstalled'] == 0
    assert result['modelGeometryChanges'] == result['scriptExternalAICalls'] == 0
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (result['jobId'],)).fetchone() == ('complete', result)
    for evidence in result['evidenceRefs']:
        assert reference(ROOT / evidence['path']) == evidence
    originals = read(closure / 'selection.json.gz')['rows']
    contexts = {r['uid']: r for r in read(closure / 'context.json.gz')['rows']}
    assert originals and len({r['uid'] for r in originals}) == len(originals)
    assert set(contexts) == {r['uid'] for r in originals}
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_ref = reference(manifest_path)
    manifest = read(manifest_path)
    installed = {m['uid'] for url in manifest['officialModelCatalogues']
                 for m in read(ROOT / '3d-viewer' / url)['models']}
    rows, outcomes = [], []
    for row in originals:
        uid = row['uid']
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            native = row['native']
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
                'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                'WHERE m.run_id=%s AND r.cache_key=%s',
                (NATIVE_RUN, native['cacheKey'])).fetchone() == (native['resultSha'],)
            reviewed = bool(con.execute('SELECT 1 FROM astra_modelling.model_reviews '
                                       'WHERE uid=%s LIMIT 1', (uid,)).fetchone())
        if uid in installed or reviewed:
            outcomes.append({'uid': uid, 'sourceSHA256': row['sourceSHA256'],
                             'identityQualified': False,
                             'reasons': ['existing-review-requires-dedicated-continuation']})
            continue
        raw = (ROOT / row['candidate']['path']).read_bytes()
        assert digest(raw) == row['sourceSHA256'] == row['native']['model']['asset']['sha256']
        assert len(raw) == row['native']['model']['asset']['bytes']
        source_tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(source_tile.read_bytes()) == row['source']['tileSHA256']
        assert [b for b in read(source_tile)['buildings'] if b['uid'] == uid] == [row['source']['building']]
        for tile, sha in contexts[uid]['neighbourTileHashes'].items():
            assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
        destination = local / 'assets' / (row['sourceSHA256'] + '.glb.gz')
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        row['candidate']['path'] = str(destination.relative_to(ROOT))
        row['candidate']['entry']['asset'] = 'assets/' + destination.name
        row['currentReview'] = None
        positive = verify_files(row, contexts[uid], local / ('identity-' + uid.split('/')[1].replace(':', '-')))
        rows.append(row)
        outcomes.append({'uid': uid, 'sourceSHA256': row['sourceSHA256'],
                         'identityQualified': positive['passed'], 'reasons': positive['reasons'],
                         'positiveIdentity': positive})
        print(json.dumps({k: outcomes[-1][k] for k in ('uid', 'identityQualified', 'reasons')}), flush=True)
        assert reservations.owns(lease)
    save(doc / 'check-selection.json.gz', {'batch': args.batch, 'rows': rows,
        'manifestSHA256': manifest_ref['sha256']})
    save(doc / 'context.json.gz', {'rows': [contexts[r['uid']] for r in rows]})
    save(doc / 'identity-qualification.json', {'rows': outcomes})
    save(doc / 'input-proof.json', {'closure': reference(closure / 'result.json'),
        'originalSelection': reference(closure / 'selection.json.gz'),
        'originalContext': reference(closure / 'context.json.gz'), 'manifest': manifest_ref,
        'runner': reference(Path(__file__)), 'identityRunner': reference(HERE / 'government_georef_cell_identity.py'),
        'publication': False, 'newlyInstalled': 0, 'modelGeometryChanges': 0})
    assert reference(manifest_path) == manifest_ref
    refs = [reference(p) for p in sorted(doc.iterdir()) if p.is_file()]
    payload = {'evidenceRefs': refs, 'uids': [r['uid'] for r in originals],
               'sourceSHA256s': {r['uid']: r['sourceSHA256'] for r in originals},
               'runner': reference(Path(__file__))}
    stage = 'exact-closure-current-original-inputs-v1'
    jobid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jobid
    output = {**payload, 'jobId': jobid, 'batch': args.batch, 'rows': outcomes,
        'identityQualifiedUids': [r['uid'] for r in outcomes if r['identityQualified']],
        'publication': False, 'newlyInstalled': 0, 'modelGeometryChanges': 0,
        'scriptExternalAICalls': 0, 'requiresAI': False, 'requiresHumanDecision': False,
        'activeWorkers': 0, 'queuedFollowups': 0,
        'qualification': 'Fresh source identity only. Original matching failures remain; full terrain, foundation, neighbours, runtime and staged/live publication gates are mandatory.'}
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, lease)
        for row in rows:
            assert not con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=%s LIMIT 1', (row['uid'],)).fetchone()
            native = row['native']
            actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
                'JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                (NATIVE_RUN, native['cacheKey'])).fetchone()
            assert actual and actual['result_sha'] == native['resultSha']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
            (Jsonb(output), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone() == ('complete', output)
    save(doc / 'result.json', output)
    save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'jobId': jobid, 'neonVerified': True,
                     'identityQualifiedUids': output['identityQualifiedUids'], 'newlyInstalled': 0}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--closure', required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    closure = (ROOT / args.closure).resolve()
    assert closure.is_relative_to(ROOT / 'docs/astra-city/government-import')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        with locked_publication(ROOT):
            owned(args, doc, local)
        return
    assert not doc.exists(), 'Fresh exact source freeze only'
    scope = {r['uid'] for r in read(closure / 'selection.json.gz')['rows']}
    claim = reservations.claim('codex-xl-closure-inputs-' + str(uuid.uuid4()),
        ['building:' + uid for uid in sorted(scope)], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
        '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__,
        *sys.argv[1:], '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
