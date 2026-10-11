"""Publish two unchanged complete original market halls after current full checks.

The physical receipt is independently revalidated, publication is serialized,
and both sources require staged/live mobile/desktop acceptance before credit.
AI interpreted existing source/component ownership; no model geometry edits.
"""
import argparse, importlib.util, json, os, shutil, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN
from dependency_preflight import from_catalogues
from market_complete_source_identity import verify_files, POLICY, UIDS
from terrain_diagnostic_resolution import resolve_global_bottom_warning


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


def ref(path):
    path = Path(path); return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def owned(args, doc, stage, lease):
    source = ROOT / args.source; base = ROOT / args.base
    def owns(): assert reservations.owns(read(lease)), 'Live original source ownership required'
    def call(command):
        subprocess.run(command, cwd=ROOT, check=True, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}); owns()
    owns()
    result = read(source / 'result.json'); uids = result['uids']
    assert len(uids) == len(set(uids)) == 2 and result['scriptChecksPassed'] and not result['reasons']
    assert result['publication'] is False and result['newlyInstalled'] == result['modelGeometryChanges'] == result['scriptExternalAICalls'] == 0
    assert read(source / 'neon-sync.json') == {'jobId': result['jobId'], 'resultVerified': True}
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
        assert not con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=ANY(%s)', (uids,)).fetchall(), 'Existing approvals require dedicated recovery'
    for evidence in result['evidenceRefs']: assert ref(ROOT / evidence['path']) == evidence
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    selection = read(source / 'selection.json.gz'); rows = sorted(selection['rows'],key=lambda r:r['uid'])
    assert [r['uid'] for r in rows] == uids and ref(manifest)['sha256'] == selection['manifestSHA256']
    assert {r['uid']: r['sourceSHA256'] for r in rows} == result['sourceSHA256s']
    contexts = {r['uid']: r for r in read(base / 'context.json.gz')['rows']}
    metrics = read(source / 'metrics.json'); neighbours = read(source / 'neighbour-inputs.json.gz')
    assert set(uids)==UIDS
    for report in [metrics, neighbours]:
        for path, sha in report['inputHashes'].items(): assert ref(ROOT / path)['sha256'] == sha, path
    foundations = {r['uid']: r for r in read(source / 'foundation.json')['rows']}
    validated = read(source / 'validation.json'); assert validated['checksPassed'] == validated['loaderAccepted'] == 2 and validated['exceptions'] == 0
    numeric = module('joint_publish_numeric', 'acceptance-policy.py')
    identities = {r['uid']:r for r in read(source/'owned-source-identity.json')['rows']}
    decisions = {r['uid']:r for r in read(source/'physical-decisions.json')['rows']}
    fresh_identity = []
    for row in rows:
        uid = row['uid']; context = contexts[uid]
        assert context['sourceSHA256'] == row['sourceSHA256']
        for path, sha in context['neighbourTileHashes'].items(): assert ref(ROOT / '3d-viewer' / path)['sha256'] == sha
        assert ref(ROOT / row['candidate']['path'])['sha256'] == row['sourceSHA256']
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchone() == (row['native']['resultSha'],)
        positive = verify_files(row, context, HERE/'local'/args.batch/'identity-recheck'/uid.split('/')[1])
        assert positive['policy'] == POLICY and positive['passed'] and positive == identities[uid]
        fresh_identity.append({'uid': uid, 'positive': positive})
        metric = next(r for r in metrics['rows'] if r['uid'] == uid)
        foundation = foundations[uid]; assert foundation['sourceSHA256'] == row['sourceSHA256'] and foundation['strictFoundationAccepted']
        f = foundation['foundation']; assert f['completeTerrainTriangles'] == f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction'] == 0
        diagnostic = resolve_global_bottom_warning(next(r for r in validated['results'] if r['uid'] == uid), metric, foundation)
        raw = numeric.reasons({'state': 'runtime-validated-awaiting-acceptance', 'sourceSHA256': row['sourceSHA256'], 'identityProof': positive['proof']}, metric, metrics['profiles']['mobile'])
        decision=decisions[uid];assert decision['numericReasons']==raw and decision['diagnosticResolution']==diagnostic
        assert not raw and not diagnostic['remaining']
    native = read(source / 'native-neighbour-checks.json'); resolved = set(native['resolved'])
    assert not set(native['blocked']) - resolved
    assert not any(r['reasons'] for r in read(source / 'neighbour-checks.json')['rows'] if r['uid'] not in resolved)
    save(doc / 'positive-identity-publication-recheck.json', {'rows': fresh_identity})
    catalogue = read(HERE / 'local' / source.name / 'catalogue.json'); models = []
    for row in rows:
        entry = dict(row['candidate']['entry']); assert entry['sha256'] == row['sourceSHA256']
        group=identities[row['uid']]['completeGroupForms']
        assert entry['footprintScope']==row['uid']
        assert sorted(entry['suppressesBuildingUids'])==sorted(b['uid'] for b in group if b['uid']!=row['uid'])
        entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,placementReview='Unchanged complete government market hall; exact unique original GeoRef/type/CSUID and full cell; fresh official component ownership; full-group 95% coverage, 10m extent, 1m2 unrelated overlap limits; original terrain confined to source projection plus 1m with current neighbour ground preserved. Full source/foundation/runtime/neighbour and staged/live browser gates. AI interpreted source identity only; zero generated or edited model geometry.')
        entry['supportDependencies']=[]
        asset = stage / entry['asset']; asset.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / row['candidate']['path'], asset)
        assert ref(asset)['sha256'] == entry['sha256']; models.append(entry)
    catalogue.update(models=models, counts={'packedModels': 2}, area='Cheung Sha Wan Wholesale Vegetable Market complete original halls')
    save(stage / 'catalogue.json', catalogue); save(stage / 'catalogue-index.json', {'models': 2, 'catalogues': ['catalogue.json']})
    save(stage/'source-forms.json',list({b['uid']:b for proof in identities.values() for b in proof['completeGroupForms']}.values()))
    candidates = read(source / 'terrain-candidates.json'); assert len(candidates) == 1
    candidate = candidates[0]; assert not candidate.get('replaces') and not candidate.get('replacesMany') and ref(ROOT / candidate['path'])['sha256'] == candidate['sha256']
    for item in read(source / 'terrain.json')['sourceFiles']: assert ref(ROOT / item['path']) == item
    patch = stage / Path(candidate['path']).name; shutil.copyfile(ROOT / candidate['path'], patch)
    terrain = {'source': ref(patch)['path'], 'sha256': ref(patch)['sha256'], 'destination': 'city/data/' + patch.name, 'resolution': read(patch)['cell'], 'area': catalogue['area'] + ' indexed government terrain'}
    destination = 'city/data/official-models/' + args.batch + '/catalogue.json'
    save(stage / 'plan.json', {'areas': [{'area': catalogue['area'], 'catalogue': ref(stage / 'catalogue.json')['path'], 'destination': destination}], 'topLevelTerrainPatches': [terrain]})
    dependencies = from_catalogues(manifest, [stage / 'catalogue.json']); assert not any(r['blockers'] for r in dependencies['rows']); save(doc / 'dependencies.json', dependencies)
    bounds = [[min(m['worldBounds'][0][axis] for m in models) for axis in range(3)], [max(m['worldBounds'][1][axis] for m in models) for axis in range(3)]]
    save(stage / 'browser-config.json', {'stage': str(stage.relative_to(ROOT)) + '/', 'doc': str(doc.relative_to(ROOT)) + '/', 'catalogueURL': destination, 'terrain': [terrain], 'fitBox': True, 'captureBoundsByModel': {uid: bounds for uid in uids}, 'browserUids': uids, 'failureTestUids': uids, 'nativeSupportUidsByModel': {}})
    evidence = {'physical-result': ref(source / 'result.json'), 'physical-neon': ref(source / 'neon-sync.json'), 'fresh-identity': ref(doc / 'positive-identity-publication-recheck.json'), 'dependencies': ref(doc / 'dependencies.json'), 'catalogue': ref(stage / 'catalogue.json'), 'plan': ref(stage / 'plan.json'), 'browser-config': ref(stage / 'browser-config.json'), 'runner': ref(Path(__file__)), 'browser-runner': ref(HERE / 'resolution-assembly-browser.mjs')}
    evidence['identity-runner']=ref(HERE/'market_complete_source_identity.py')
    evidence['source-review']=ref(ROOT/'docs/astra-city/government-import/government-xl-six-source-identity-review-20261008/review.json')
    evidence['official-group-context']=ref(ROOT/'docs/astra-city/government-import/government-xl-market-official-group-context-20261008/context.json')
    decision = {'batch': args.batch, 'uids': uids, 'sourceSHA256s': result['sourceSHA256s'], 'evidence': evidence, 'checksPassed': True, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'sourceIdentityReviewUsedAI': True, 'aiGeometryModelling': False}
    save(doc / 'stage.json', decision)
    publication = [sys.executable, str(HERE.parent / 'model-integration-20260909/publish.py'), ref(stage / 'plan.json')['path'], '--receipt', str(lease), '--phase', args.batch]
    call(publication)
    direct = module('joint_browser_validator', 'integrate.py')
    call(['node', str(HERE / 'resolution-assembly-browser.mjs'), 'staged', ref(stage / 'browser-config.json')['path']]); direct.browser_verified(doc / 'staged-browser.json', set(uids))
    for item in evidence.values(): assert ref(ROOT / item['path']) == item
    decision.update(stagedBrowser=ref(doc / 'staged-browser.json'), passed=True, failures=[]); save(doc / 'acceptance.json', decision)
    sys.path.insert(0, str(HERE.parent / 'model-review-ledger')); import ledger
    pointer_path = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'; pointer = read(pointer_path); inventory = read(ROOT / pointer['inventory']); parts = {p['uid']: p for p in inventory['parts']}
    for model in models:
        previous = parts.get(model['uid'], {}); parts[model['uid']] = {'uid': model['uid'], 'name': model['label'], 'landmarkIds': previous.get('landmarkIds', []), 'objectId': model['objectId'], 'csuid': model['buildingCSUID'], 'candidate': {'sha256': model['sha256']}, 'sourceProgress': 'prepared-for-review', 'classification': 'verified-complete-original-government-market-hall', 'knownHold': False}
    ordered = sorted(parts.values(), key=lambda p: p['uid']); snapshot = digest(jobs.encode([ordered, decision]).encode())[:16]; inventory_path = pointer_path.parent / ('source-review-inventory-' + snapshot + '.json')
    save(inventory_path, {**inventory, 'snapshotId': snapshot, 'derivedFrom': pointer['snapshotId'], 'parts': ordered, 'qualification': 'Unchanged original complete market halls pass whole-source identity, terrain, foundation, neighbour and staged/live runtime checks. AI source interpretation only; no geometry modelling.'}); ledger.seed(inventory_path, inherit=pointer['snapshotId'])
    effort = {'method': 'unknown', 'ai_model': None, 'reasoning_effort': 'unknown', 'issue': 'HKS-203', 'run_id': snapshot, 'output_ref': ref(doc / 'acceptance.json')['path']}
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    ledger.record_many(snapshot, lease, [(uid, 'approved-for-integration', doc / 'acceptance.json', 'Full original market halls and staged browser pass; live publication pending. AI source interpretation recorded separately; model geometry unchanged.', commit) for uid in uids], effort=effort, request_id=args.batch + '-approved-' + snapshot)
    call(publication); before = manifest.read_bytes(); (lease.parent / 'manifest-before-installation.json').write_bytes(before); call(publication + ['--apply'])
    try:
        call(['node', str(HERE / 'resolution-assembly-browser.mjs'), 'live', ref(stage / 'browser-config.json')['path']]); direct.browser_verified(doc / 'live-browser.json', set(uids))
    except BaseException:
        manifest.write_bytes(before); raise
    installed = {**decision, 'snapshotId': snapshot, 'publication': True, 'manifest': ref(manifest), 'liveBrowser': ref(doc / 'live-browser.json')}; save(doc / 'installed-acceptance.json', installed)
    ledger.record_many(snapshot, lease, [(uid, 'installed-verified', doc / 'installed-acceptance.json', 'Both unchanged market originals pass staged/live desktop/mobile day/night, picking/collision, suppression and failed-load/retry checks. Complete source foundation and unchanged neighbours pass. AI source interpretation only; zero geometry modelling.', commit) for uid in uids], effort=effort, request_id=args.batch + '-installed-' + snapshot)
    assert read(pointer_path) == pointer; save(pointer_path, {**pointer, 'snapshotId': snapshot, 'inventory': ref(inventory_path)['path'], 'previousSnapshots': [*pointer.get('previousSnapshots', []), pointer['snapshotId']]})
    call([sys.executable, str(HERE.parent / 'building-progress/export.py'), '--refresh']); call(['node', str(ROOT / '3d-viewer/scripts/build_progress.mjs')])
    payload = {'acceptance': ref(doc / 'acceptance.json'), 'snapshot': snapshot}; jobid = jobs.enqueue(args.batch, 'complete-original-government-market-install-v1', payload); receipt = read(lease); job = jobs.claim(args.batch, receipt['owner'], ['complete-original-government-market-install-v1'], lease_seconds=1800); assert job and job['id'] == jobid
    final = {**installed, 'installedUids': uids, 'evidenceRefs': [ref(doc / name) for name in ['acceptance.json', 'installed-acceptance.json', 'staged-browser.json', 'live-browser.json']], 'jobId': jobid, 'newlyInstalled': 2, 'activeWorkers': 0, 'queuedFollowups': 0, 'progress': read(ROOT / '3d-viewer/city/data/building-progress.json')}
    with connect() as con:
        con.row_factory = dict_row; con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,)); assert reservations._current(con, receipt)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(final), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY'); assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone() == ('complete', final)
        reviews = con.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)', (snapshot, uids)).fetchall(); assert {u: sha for u, state, sha in reviews if state == 'installed-verified'} == result['sourceSHA256s']
    save(doc / 'result.json', final); save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True, 'snapshotId': snapshot, 'installedUids': uids})
    print(json.dumps({'installed': uids, 'snapshotId': snapshot, 'jobId': jobid, 'neonVerified': True}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'source', 'base']: parser.add_argument('--' + name, required=True)
    parser.add_argument('--owned', action='store_true'); args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    for value in [args.source, args.base]: assert (ROOT / value).resolve().is_relative_to(ROOT)
    doc = ROOT / 'docs/astra-city/government-import' / args.batch; stage = HERE / 'accepted' / args.batch; lease = HERE / 'local' / args.batch / 'install-reservation.json'
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT): return owned(args, doc, stage, lease)
    assert not doc.exists(), 'Fresh immutable acceptance batch required'
    source = ROOT / args.source; result = read(source / 'result.json')
    scope = {r['building']['uid'] for r in read(source/'neighbour-inputs.json.gz')['rows']} | set(result['uids']) | {b['uid'] for r in read(source/'owned-source-identity.json')['rows'] for b in r['completeGroupForms']}
    claim = reservations.claim('codex-xl-joint-original-install-' + str(uuid.uuid4()), [('building:' if uid.startswith('landsd/') else 'source-form:') + uid for uid in sorted(scope)] + ['terrain-patch:' + uid for uid in result['uids']], batch=args.batch); assert claim['ok'], claim
    save(lease, json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(lease), '--', sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)

if __name__ == '__main__': main()
