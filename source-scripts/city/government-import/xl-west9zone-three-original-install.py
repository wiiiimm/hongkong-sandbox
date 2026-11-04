"""Publish three unchanged WEST9ZONE originals after current full checks.

The physical receipt is independently revalidated, publication is serialized,
and both sources require staged/live mobile/desktop acceptance before credit.
AI interpreted existing source/component ownership; no model geometry edits.
"""
import argparse, importlib.util, json, os, shutil, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN
from dependency_preflight import from_catalogues
from government_georef_cell_identity import verify_files as individual_verify
from retained_component_geographic_identity import verify_files as group_verify
PRIMARY="landsd/227099:0"
UIDS={PRIMARY,"landsd/81972:0","landsd/83691:0"}
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
    assert len(uids) == len(set(uids)) == 3 and result['scriptChecksPassed'] and not result['reasons']
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
    validated = read(source / 'validation.json'); assert validated['checksPassed'] == validated['loaderAccepted'] == 3 and validated['exceptions'] == 0
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
        positive = (group_verify if uid==PRIMARY else individual_verify)(row, context, HERE/'local'/args.batch/'identity-recheck'/uid.split('/')[1])
        assert positive['passed'] and positive == identities[uid]
        fresh_identity.append({'uid': uid, 'positive': positive})
        metric = next(r for r in metrics['rows'] if r['uid'] == uid)
        foundation = foundations[uid]; assert foundation['sourceSHA256'] == row['sourceSHA256'] and foundation['strictFoundationAccepted']
        f = foundation['foundation']; assert f['completeTerrainTriangles'] == f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction'] == 0
        diagnostic = resolve_global_bottom_warning(next(r for r in validated['results'] if r['uid'] == uid), metric, foundation)
        raw = numeric.reasons({'state': 'runtime-validated-awaiting-acceptance', 'sourceSHA256': row['sourceSHA256'], 'identityProof': positive['proof']}, metric, metrics['profiles']['mobile'])
        decision=decisions[uid];assert decision['rawNumericReasons']==raw and decision['diagnosticResolution']==diagnostic
        remaining=list(raw);remaining_diagnostics=list(diagnostic['remaining'])
        if uid!=PRIMARY:
            checks=read(source/'support-checks.json');check=next(r for r in checks['rows'] if r['uid']==uid)
            assert check['sourceSHA256']==row['sourceSHA256'] and check['supportUid']==PRIMARY and check['supportSHA256']==result['sourceSHA256s'][PRIMARY]
            p=check['interface'];assert p['policy']=='exact-original-contact-seams-v1' and p['passed'] and not p['unresolved'] and p['strictContacts']>0
            assert p['strictContacts']+p['wallIntersections']+p['seamCorrections']==p['samples']
            assert p['maximumEmbeddingM']==.5 and p['exactSeamToleranceM']==.001
            for path,sha in checks['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha
            # Full physical receipt proves the original support + drawn terrain
            # foundation; only terrain-only ground-gap diagnostics resolve.
            assert decision['originalSupportContactAccepted'] and foundation['supportUid']==PRIMARY
            resolved={'ground-contact-unresolved','sampled-ground-gap-below-model-bottom'}
            remaining=[r for r in remaining if r not in resolved];remaining_diagnostics=[r for r in remaining_diagnostics if r not in resolved]
        assert decision['remainingNumericReasons']==remaining==[] and decision['remainingDiagnosticReasons']==remaining_diagnostics==[]
    native = read(source / 'native-neighbour-checks.json'); resolved = set(native['resolved'])
    assert not set(native['blocked']) - resolved
    assert not any(r['reasons'] for r in read(source / 'neighbour-checks.json')['rows'] if r['uid'] not in resolved)
    save(doc / 'positive-identity-publication-recheck.json', {'rows': fresh_identity})
    catalogue = read(HERE / 'local' / source.name / 'catalogue.json'); models = []
    for row in rows:
        entry = dict(row['candidate']['entry']); assert entry['sha256'] == row['sourceSHA256']
        entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,suppressesBuildingUids=[],placementReview='Unchanged original government WEST9ZONE assembly; exact original GeoRef/type/CSUID, SHA and native pose. Whole original-source identity; podium full source/terrain contact and complete tower/podium foundations pass. Exact original wall upper-edge seams and higher zero-area deck corners resolve ray omissions while preserving raw failures and strict limits. All other basic/native neighbours, including existing229310, pass. Staged/live desktop/mobile day/night, picking/collision and fallback/retry required. AI interpreted unchanged sources only; zero generated or edited model geometry.')
        entry['supportDependencies']=[] if row['uid']==PRIMARY else [{'uid':PRIMARY,'state':'candidate','csuid':next(r for r in rows if r['uid']==PRIMARY)['candidate']['entry']['buildingCSUID'],'sha256':result['sourceSHA256s'][PRIMARY]}]
        asset = stage / entry['asset']; asset.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / row['candidate']['path'], asset)
        assert ref(asset)['sha256'] == entry['sha256']; models.append(entry)
    catalogue.update(models=models, counts={'packedModels': 3}, area='WEST9ZONE and Florient Rise original government assembly')
    save(stage / 'catalogue.json', catalogue); save(stage / 'catalogue-index.json', {'models': 2, 'catalogues': ['catalogue.json']})
    save(stage/'source-forms.json',[r['source']['building'] for r in rows])
    candidates = read(source / 'terrain-candidates.json'); assert len(candidates) == 1
    candidate = candidates[0]; assert candidate.get('replaces') and not candidate.get('replacesMany') and ref(ROOT / candidate['path'])['sha256'] == candidate['sha256']
    old_ref=read(source/'terrain.json')['originalRetainedTerrainEvidence'];assert ref(ROOT/old_ref['path'])==old_ref
    patch = stage / Path(candidate['path']).name; shutil.copyfile(ROOT / candidate['path'], patch)
    terrain = {'source': ref(patch)['path'], 'sha256': ref(patch)['sha256'], 'destination': 'city/data/' + patch.name, 'resolution': read(patch)['cell'], 'area': catalogue['area'] + ' indexed government terrain'}
    replacement=candidate['replaces'];original=read(patch)
    assert ref(ROOT/'3d-viewer'/replacement['url'])['sha256']==replacement['sha256']
    assert set(replacement['retainedUids']) <= {r['uid'] for r in native['rows'] if r['passed']}
    replacement_review={'status':'approved-for-integration','supersededURL':replacement['url'],'supersededSHA256':replacement['sha256'],'replacementSHA256':terrain['sha256'],'sourceGeometryChanged':False,'aiCalls':0,'modelGeometryChanges':0,'retainedUids':replacement['retainedUids'],'replacementTargetUids':original['meta']['targetUids'],'fullMeshCheck':ref(source/'native-neighbour-checks.json')}
    save(doc/'native-replacement-review.json',replacement_review);terrain.update(replaces=replacement,nativeReview=ref(doc/'native-replacement-review.json'))
    destination = 'city/data/official-models/' + args.batch + '/catalogue.json'
    save(stage / 'plan.json', {'areas': [{'area': catalogue['area'], 'catalogue': ref(stage / 'catalogue.json')['path'], 'destination': destination}], 'topLevelTerrainPatches': [terrain]})
    dependencies = from_catalogues(manifest, [stage / 'catalogue.json']); assert not any(r['blockers'] for r in dependencies['rows']); save(doc / 'dependencies.json', dependencies)
    current_models=[m for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid'] in replacement['retainedUids']]
    bounds = [[min(m['worldBounds'][0][axis] for m in models+current_models) for axis in range(3)], [max(m['worldBounds'][1][axis] for m in models+current_models) for axis in range(3)]]
    models.sort(key=lambda m:(m['uid']!=PRIMARY,m['uid']));uids=[m['uid'] for m in models]
    save(stage / 'browser-config.json', {'stage': str(stage.relative_to(ROOT)) + '/', 'doc': str(doc.relative_to(ROOT)) + '/', 'catalogueURL': destination, 'terrain': [terrain], 'fitBox': True, 'captureBoundsByModel': {uid: bounds for uid in uids}, 'browserUids': uids, 'failureTestUids': uids, 'nativeSupportUidsByModel': {uid:[*replacement['retainedUids'],*([PRIMARY] if uid!=PRIMARY else [])] for uid in uids}})
    evidence = {'physical-result': ref(source / 'result.json'), 'physical-neon': ref(source / 'neon-sync.json'), 'fresh-identity': ref(doc / 'positive-identity-publication-recheck.json'), 'dependencies': ref(doc / 'dependencies.json'), 'catalogue': ref(stage / 'catalogue.json'), 'plan': ref(stage / 'plan.json'), 'browser-config': ref(stage / 'browser-config.json'), 'runner': ref(Path(__file__)), 'browser-runner': ref(HERE / 'resolution-assembly-browser.mjs')}
    evidence['identity-runner']=ref(HERE/'retained_component_geographic_identity.py')
    evidence['native-replacement-review']=ref(doc/'native-replacement-review.json')
    evidence['contact-seams']=ref(HERE/'original-contact-seams.mjs')
    evidence['contact-seam-tests']=ref(HERE/'test-original-contact-seams.mjs')
    evidence['source-review']=ref(ROOT/'docs/astra-city/government-import/government-xl-22-original-component-capture-review-20261008/reviews.json')
    evidence['official-group-context']=ref(ROOT/'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/official-context.json')
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
        previous = parts.get(model['uid'], {}); parts[model['uid']] = {'uid': model['uid'], 'name': model['label'], 'landmarkIds': previous.get('landmarkIds', []), 'objectId': model['objectId'], 'csuid': model['buildingCSUID'], 'candidate': {'sha256': model['sha256']}, 'sourceProgress': 'prepared-for-review', 'classification': 'verified-original-government-native-assembly', 'knownHold': False}
    ordered = sorted(parts.values(), key=lambda p: p['uid']); snapshot = digest(jobs.encode([ordered, decision]).encode())[:16]; inventory_path = pointer_path.parent / ('source-review-inventory-' + snapshot + '.json')
    save(inventory_path, {**inventory, 'snapshotId': snapshot, 'derivedFrom': pointer['snapshotId'], 'parts': ordered, 'qualification': 'Unchanged original complete WEST9ZONE assembly pass whole-source identity, terrain, foundation, neighbour and staged/live runtime checks. AI source interpretation only; no geometry modelling.'}); ledger.seed(inventory_path, inherit=pointer['snapshotId'])
    effort = {'method': 'unknown', 'ai_model': None, 'reasoning_effort': 'unknown', 'issue': 'HKS-203', 'run_id': snapshot, 'output_ref': ref(doc / 'acceptance.json')['path']}
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    ledger.record_many(snapshot, lease, [(uid, 'approved-for-integration', doc / 'acceptance.json', 'Full original WEST9ZONE assembly and staged browser pass; live publication pending. AI source interpretation recorded separately; model geometry unchanged.', commit) for uid in uids], effort=effort, request_id=args.batch + '-approved-' + snapshot)
    call(publication); before = manifest.read_bytes(); (lease.parent / 'manifest-before-installation.json').write_bytes(before); call(publication + ['--apply'])
    try:
        call(['node', str(HERE / 'resolution-assembly-browser.mjs'), 'live', ref(stage / 'browser-config.json')['path']]); direct.browser_verified(doc / 'live-browser.json', set(uids))
    except BaseException:
        manifest.write_bytes(before); raise
    installed = {**decision, 'snapshotId': snapshot, 'publication': True, 'manifest': ref(manifest), 'liveBrowser': ref(doc / 'live-browser.json')}; save(doc / 'installed-acceptance.json', installed)
    ledger.record_many(snapshot, lease, [(uid, 'installed-verified', doc / 'installed-acceptance.json', 'All three unchanged WEST9ZONE originals pass staged/live desktop/mobile day/night, picking/collision, suppression and failed-load/retry checks. Complete source foundation and unchanged neighbours pass. AI source interpretation only; zero geometry modelling.', commit) for uid in uids], effort=effort, request_id=args.batch + '-installed-' + snapshot)
    assert read(pointer_path) == pointer; save(pointer_path, {**pointer, 'snapshotId': snapshot, 'inventory': ref(inventory_path)['path'], 'previousSnapshots': [*pointer.get('previousSnapshots', []), pointer['snapshotId']]})
    call([sys.executable, str(HERE.parent / 'building-progress/export.py'), '--refresh']); call(['node', str(ROOT / '3d-viewer/scripts/build_progress.mjs')])
    payload = {'acceptance': ref(doc / 'acceptance.json'), 'snapshot': snapshot}; jobid = jobs.enqueue(args.batch, 'west9zone-three-original-seams-install-v1', payload); receipt = read(lease); job = jobs.claim(args.batch, receipt['owner'], ['west9zone-three-original-seams-install-v1'], lease_seconds=1800); assert job and job['id'] == jobid
    final = {**installed, 'installedUids': uids, 'evidenceRefs': [ref(doc / name) for name in ['acceptance.json', 'installed-acceptance.json', 'staged-browser.json', 'live-browser.json']], 'jobId': jobid, 'newlyInstalled': 3, 'activeWorkers': 0, 'queuedFollowups': 0, 'progress': read(ROOT / '3d-viewer/city/data/building-progress.json')}
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
    scope = {r['building']['uid'] for r in read(source/'neighbour-inputs.json.gz')['rows']} | set(result['uids']) | {b['uid'] for r in read(source/'owned-source-identity.json')['rows'] for b in r.get('completeGroupForms',[])}
    claim = reservations.claim('codex-xl-joint-original-install-' + str(uuid.uuid4()), [('building:' if uid.startswith('landsd/') else 'source-form:') + uid for uid in sorted(scope)] + ['terrain-patch:' + uid for uid in result['uids']], batch=args.batch); assert claim['ok'], claim
    save(lease, json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(lease), '--', sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)

if __name__ == '__main__': main()
