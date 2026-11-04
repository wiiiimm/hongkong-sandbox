"""Recover a bounded explicit XL list without changing model geometry or reviews."""
import argparse, importlib.util, json, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
import shape_prepare


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--revision-of', help='Exact completed recovery with container revision errors'); p.add_argument('--uids-file', required=True); p.add_argument('--batch', required=True); p.add_argument('--owned', action='store_true')
    args = p.parse_args(); assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    uids = read(ROOT / args.uids_file)['uids']; assert 1 <= len(uids) <= 100 and len(set(uids)) == len(uids)
    doc = ROOT / 'docs/astra-city/government-import' / args.batch; local = HERE / 'local' / args.batch; lease = local / 'reservation.json'
    if not args.owned:
        assert not doc.exists(), 'Fresh immutable recovery only'
        claim = reservations.claim('codex-xl-original-recovery-' + str(uuid.uuid4()), ['building:' + uid for uid in uids], batch=args.batch); assert claim['ok'], claim
        save(lease, json.loads(json.dumps(claim['reservation'], default=str)))
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(lease), '--', sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True); return
    receipt = read(lease); assert reservations.owns(receipt)
    macro = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923/selection.json.gz'
    selected = {r['uid']: r for r in read(macro)['rows']}; assert set(uids) <= set(selected)
    rows = [selected[u] for u in uids]
    for row in rows:
        assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
    def native_verified(con):
        for row in rows:
            n = row['native']; assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, n['cacheKey'])).fetchone() == (n['resultSha'],)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY'); native_verified(con)
        assert not con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=ANY(%s)', (uids,)).fetchall(), 'Reviewed source needs separate explicit continuation'
    evidence = {'nativeRun': read(macro)['nativeRun'], 'rows': uids, 'sources': {r['uid']: r['source'] for r in rows}, 'native': [r['native'] for r in rows]}
    save(local / 'recovery-inputs.json.gz', evidence)
    revision_refs = []
    if args.revision_of:
        previous = (ROOT / args.revision_of).resolve(); assert previous.is_relative_to(doc.parent)
        earlier = read(previous / 'result.json'); assert set(earlier['uids']) == set(uids) and not earlier['publication']
        assert all(earlier['errors'].get(uid) == 'ValueError: Source revision changed' for uid in uids)
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY'); assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (earlier['jobId'],)).fetchone() == ('complete', earlier)
        for evidence_ref in earlier['evidenceRefs']: assert digest((ROOT / evidence_ref['path']).read_bytes()) == evidence_ref['sha256']
        old_local = HERE / 'local' / previous.name / 'recovered'; metadata = read(old_local / 'source-metadata.json')
        spec = importlib.util.spec_from_file_location('explicit_same_member_recovery', HERE / 'xl-source-revision-recover.py'); recovery = importlib.util.module_from_spec(spec); spec.loader.exec_module(recovery); recovery.LOCAL = local
        outcomes = []
        for sheet in sorted({r['native']['sheet'] for r in rows}):
            directory = old_local / 'sheets' / sheet / 'directory'; current = read(directory / 'result.json')
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY'); prior = con.execute('SELECT result FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1', (sheet,)).fetchone()[0]
            assert all(prior[k] == metadata['directories'][sheet][k] for k in ('etag', 'directorySHA256'))
            group = [{'uid': r['uid'], 'modelId': r['modelId'], 'sourceSHA256': r['sourceSHA256'], 'sourceEntry': r['native']['model']['sourceEntry'], 'sourceBytes': r['native']['model']['asset']['bytes'], 'directoryFile': directory / 'zip-directory.bin'} for r in rows if r['native']['sheet'] == sheet]
            outcomes.extend(recovery.work(sheet, group, current, prior))
            revision_refs += [directory / 'result.json', directory / 'zip-directory.bin']
        save(doc / 'member-revision-proof.json', {'rows': outcomes, 'priorResult': str((previous / 'result.json').relative_to(ROOT)), 'modelGeometryChanges': 0})
        revision_refs += [previous / 'result.json', old_local / 'source-metadata.json', HERE / 'xl-source-revision-recover.py', doc / 'member-revision-proof.json']
        exact = {r['uid'] for r in outcomes if r['state'] == 'exact-source-recovered'}
        prepared = {'rows': [{'uid': u} for u in sorted(exact)], 'errors': {r['uid']: r['state'] for r in outcomes if r['uid'] not in exact}, 'methods': {'verified-same-member-revision': len(exact)}}
        save(local / 'recovered/geometry-inputs.json', prepared)
    else:
        prepared = shape_prepare.prepare(local / 'recovery-inputs.json.gz', local / 'recovered', allow_source=True, workers=2, env_file=ROOT / '.env.modelling', reservation_receipt=receipt)
    assert reservations.owns(receipt)
    recovered = []
    by_uid = {r['uid']: r for r in prepared['rows']}
    for row in rows:
        if row['uid'] not in by_uid: continue
        asset = local / 'recovered/assets' / (row['sourceSHA256'] + '.glb.gz')
        assert asset.exists() and digest(asset.read_bytes()) == row['sourceSHA256']
        recovered.append({'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'sourcePath': str(asset.relative_to(ROOT))})
    save(doc / 'recovery.json', {'rows': recovered, 'errors': prepared['errors'], 'methods': prepared['methods']})
    paths = [macro, ROOT / args.uids_file, Path(__file__), Path(shape_prepare.__file__), local / 'recovery-inputs.json.gz', local / 'recovered/geometry-inputs.json', doc / 'recovery.json']
    paths += revision_refs
    refs = [{'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())} for path in paths]
    payload = {'uids': uids, 'evidenceRefs': refs}; stage = 'explicit-unchanged-original-source-recovery-v1'
    jobid = jobs.enqueue(args.batch, stage, payload); job = jobs.claim(args.batch, receipt['owner'], [stage], lease_seconds=1800); assert job and job['id'] == jobid
    result = {**payload, 'jobId': jobid, 'batch': args.batch, 'rows': recovered, 'errors': prepared['errors'], 'recovered': len(recovered), 'publication': False, 'newlyInstalled': 0, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'activeWorkers': 0, 'queuedFollowups': 0, 'qualification': 'Exact pinned source bytes only; no source identity, physical acceptance or installed credit.'}
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,)); native_verified(con); con.row_factory = dict_row; assert reservations._current(con, receipt)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY'); assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone() == ('complete', result)
    save(doc / 'result.json', result); save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'recovered': len(recovered), 'errors': prepared['errors'], 'jobId': jobid, 'neonVerified': True, 'newlyInstalled': 0}), flush=True)

if __name__ == '__main__': main()
