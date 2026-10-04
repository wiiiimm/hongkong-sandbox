"""Fresh bounded XL continuation after HKS-229; unchanged government sources only.

Freeze the next 100 from the original outside-Lantau inventory, excluding installed
forms and the completed ten-form pilot. Reuse hash-verified bytes and historical
recovery evidence, then measure current runtime, complete terrain contact and
projected neighbour context. This driver does not approve or publish models.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import uuid

from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row, NATIVE_RUN
from dependency_preflight import from_catalogues

BATCH = 'government-xl-next-100-20261005'
STAGE = 'xl-current-runtime-context-v1'
BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
PILOT = {'landsd/91827:0', 'landsd/104302:0', 'landsd/134332:0',
         'landsd/255917:0', 'landsd/255647:0', 'landsd/255539:0',
         'landsd/264206:0', 'landsd/336430:0', 'landsd/273672:0',
         'landsd/273839:0'}


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def candidate_entry(row):
    # Native-stage matching metadata lacks the compact catalogue's source sheet.
    # Use the existing deterministic entry builder, preserving every byte/transform.
    sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
    from shape_prepare import entry
    value = entry(row['native'], row['source']['building'])
    assert value['uid'] == row['uid'] and value['sha256'] == row['sourceSHA256']
    return value


def installed():
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    result = {}
    for url in manifest['officialModelCatalogues']:
        for entry in read(ROOT / '3d-viewer' / url)['models']:
            assert entry['uid'] not in result
            result[entry['uid']] = entry
    return result


def freeze():
    assert not (DOC / 'selection.json.gz').exists(), 'Resume frozen selection; never overwrite it'
    original = read(BASE / 'selection.json.gz')
    current = installed()
    rows = [r for r in original['rows'] if r['uid'] not in current and r['uid'] not in PILOT][:100]
    assert len(rows) == 100
    # Query all exact cached asset paths once, without any per-model AI or download.
    paths = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore',
                                   '-g', '*.glb.gz', 'source-scripts/city',
                                   '3d-viewer/city/data'], cwd=ROOT, text=True).splitlines()
    wanted = {r['sourceSHA256'] for r in rows}
    cache = {}
    for name in paths:
        path = ROOT / name
        key = path.name.removesuffix('.glb.gz')
        if key in wanted and key not in cache and sha(path) == key:
            cache[key] = rel(path)
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    sources = {}
    uids = {r['uid'] for r in rows}
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        for building in read(path)['buildings']:
            if building['uid'] in uids:
                sources[building['uid']] = {'building': building, 'tile': tile['url'], 'tileSHA256': sha(path)}
    assert set(sources) == uids
    previous = {r['uid']: r for r in read(BASE / 'reconciliation.json.gz')['rows']}
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        live = dict(connection.execute(
            'SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r '
            'JOIN astra_modelling.native_stage_members m USING(cache_key) '
            'WHERE m.run_id=%s AND r.cache_key=ANY(%s)',
            (NATIVE_RUN, sorted({r['native']['cacheKey'] for r in rows}))))
        reviews = dict(connection.execute(
            "SELECT DISTINCT ON(uid) uid,jsonb_build_object('state',review_state,'sha',source_sha256) "
            "FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC",
            (sorted(uids),)))
    frozen = []
    for row in rows:
        assert live[row['native']['cacheKey']] == row['native']['resultSha']
        frozen.append({**row, 'source': sources[row['uid']],
                       'currentReview': reviews.get(row['uid']), 'previousCheckpoint': previous[row['uid']],
                       'cachedAsset': cache.get(row['sourceSHA256'])})
    selection = {**original, 'batch': BATCH, 'rows': frozen,
                 'selectionLimit': 100, 'manifestSHA256': sha(ROOT / '3d-viewer/city/data/manifest.json'),
                 'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                 'selectionPolicy': 'Next 100 in frozen descending-triangle order; exclude installed and completed ten-form pilot',
                 'inputHashes': {rel(BASE / p): sha(BASE / p) for p in ('selection.json.gz', 'reconciliation.json.gz')},
                 'installedBefore': sum(r['uid'] in current for r in original['rows']),
                 'scriptExternalAICalls': 0}
    save(DOC / 'selection.json.gz', selection)
    print(json.dumps({'selected': len(frozen), 'exactCachedAssets': sum(bool(r['cachedAsset']) for r in frozen),
                      'priorHoldCounts': dict(Counter(r['previousCheckpoint']['primaryHold'] for r in frozen))}), flush=True)


def start():
    frozen = read(DOC / 'selection.json.gz')
    resources = ['building:' + r['uid'] for r in frozen['rows']]
    receipt = reservations.claim('codex-xl-next100-' + str(uuid.uuid4()), resources, batch=BATCH)
    assert receipt['ok'], receipt
    save(LOCAL / 'reservation.json', json.loads(json.dumps(receipt['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
                    'run', '--lease-file', str(LOCAL / 'reservation.json'), '--',
                    sys.executable, __file__, 'execute'], cwd=ROOT, check=True)


def context_one(row):
    context = module('next100_context', 'xl-final-script-pass.py')
    context.s.LOCAL = LOCAL
    triangles = context.s.glb_triangles(row)
    lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
    forms = context.load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
    identity = context.identity_context(row, triangles, forms)
    return {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'],
            'sourceFaceCount': len(triangles), 'identity': identity,
            'neighbourTileHashes': {tile: sha(ROOT / '3d-viewer' / tile) for _, _, tile in forms}}


def execute():
    receipt = read(LOCAL / 'reservation.json')
    frozen = read(DOC / 'selection.json.gz')
    assert reservations.owns(receipt)
    assert sha(ROOT / '3d-viewer/city/data/manifest.json') == frozen['manifestSHA256']
    chosen = []
    for row in frozen['rows']:
        assert sha(ROOT / '3d-viewer' / row['source']['tile']) == row['source']['tileSHA256']
        if not row['cachedAsset']:
            continue
        raw = (ROOT / row['cachedAsset']).read_bytes()
        assert digest(raw) == row['sourceSHA256']
        target = LOCAL / 'assets' / (row['sourceSHA256'] + '.glb.gz')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        entry = candidate_entry(row)
        assert entry['uid'] == row['uid'] and entry['sha256'] == row['sourceSHA256']
        assert len(raw) == entry['bytes']
        entry['asset'] = 'assets/' + target.name
        chosen.append({**row, 'candidate': {'entry': entry, 'path': rel(target)}})
    catalogue = {k: v for k, v in read(HERE.parent / 'kai-tak-port/staged/catalogue.json').items()
                 if k not in ('models', 'counts', 'area')}
    catalogue.update(area=BATCH, models=[r['candidate']['entry'] for r in chosen], counts={'packedModels': len(chosen)})
    save(LOCAL / 'catalogue.json', catalogue)
    save(LOCAL / 'catalogue-index.json', {'models': len(chosen), 'catalogues': ['catalogue.json']})
    save(LOCAL / 'source-forms.json', {r['uid']: r['source'] for r in chosen})
    save(DOC / 'check-selection.json.gz', {**frozen, 'rows': chosen})
    save(DOC / 'dependency-preflight.json', from_catalogues(ROOT / '3d-viewer/city/data/manifest.json', [LOCAL / 'catalogue.json']))
    payload = {'selectionSHA256': sha(DOC / 'selection.json.gz'), 'sourceCommit': frozen['sourceCommit'],
               'pipelineSHA256': sha(__file__), 'uids': [r['uid'] for r in frozen['rows']]}
    job_id = jobs.enqueue(BATCH, STAGE, payload)
    job = jobs.claim(BATCH, receipt['owner'], [STAGE], lease_seconds=1800)
    assert job and job['id'] == job_id
    save(LOCAL / 'job.json', json.loads(json.dumps(job, default=str)))
    def beat():
        assert jobs.heartbeat(job, lease_seconds=1800), 'Job lease lost'
        assert reservations.owns(receipt), 'Source lease lost'
    def command(args, allowed=(0,)):
        result = subprocess.run(args, cwd=ROOT)
        assert result.returncode in allowed
        beat()
    command(['node', str(HERE.parent / 'building-batch/validate_candidates.mjs'), '--candidates', rel(LOCAL),
             '--source-forms', rel(LOCAL / 'source-forms.json'), '--out', rel(DOC / 'validation.json')], (0, 1))
    command(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(DOC / 'check-selection.json.gz'),
             '--candidates', rel(LOCAL), '--out', rel(DOC / 'metrics.json')])
    output = {'rows': [], 'errors': {}, 'sourceCommit': frozen['sourceCommit'], 'scriptExternalAICalls': 0}
    with ProcessPoolExecutor(max_workers=4) as pool:
        work = {pool.submit(context_one, row): row['uid'] for row in chosen}
        for future in as_completed(work):
            uid = work[future]
            try:
                output['rows'].append(future.result())
            except Exception as error:
                output['errors'][uid] = type(error).__name__ + ': ' + str(error)
            output['rows'].sort(key=lambda r: r['uid'])
            save(DOC / 'context.json.gz', output)
            beat()
            if (len(output['rows']) + len(output['errors'])) % 10 == 0:
                print(json.dumps({'projectedContextFinished': len(output['rows']), 'contextErrors': len(output['errors'])}), flush=True)
    print(json.dumps({'checksComplete': len(chosen), 'jobId': job_id, 'publication': False}), flush=True)


def retry_runtime():
    """Repair compact staging metadata; preserve the failed attempt and context."""
    receipt = read(LOCAL / 'reservation.json')
    assert reservations.owns(receipt)
    job = read(LOCAL / 'job.json')
    assert jobs.heartbeat(job, lease_seconds=1800)
    selected = read(DOC / 'check-selection.json.gz')
    assert sha(ROOT / '3d-viewer/city/data/manifest.json') == selected['manifestSHA256']
    for row in selected['rows']:
        row['candidate']['entry'] = candidate_entry(row)
    (DOC / 'staging-metadata-retry').mkdir(exist_ok=True)
    # The first runtime output is invalid (all rows failed before preparation).
    for name in ('metrics.json', 'validation.json', 'check-selection.json.gz', 'dependency-preflight.json'):
        path = DOC / name
        if path.exists() and not (DOC / 'staging-metadata-retry' / name).exists():
            shutil.copyfile(path, DOC / 'staging-metadata-retry' / name)
    save(DOC / 'check-selection.json.gz', selected)
    catalogue = read(LOCAL / 'catalogue.json')
    catalogue['models'] = [row['candidate']['entry'] for row in selected['rows']]
    save(LOCAL / 'catalogue.json', catalogue)
    save(DOC / 'dependency-preflight.json', from_catalogues(ROOT / '3d-viewer/city/data/manifest.json', [LOCAL / 'catalogue.json']))
    for args in (
        ['node', str(HERE.parent / 'building-batch/validate_candidates.mjs'), '--candidates', rel(LOCAL),
         '--source-forms', rel(LOCAL / 'source-forms.json'), '--out', rel(DOC / 'validation.json')],
        ['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(DOC / 'check-selection.json.gz'),
         '--candidates', rel(LOCAL), '--out', rel(DOC / 'metrics.json')]):
        result = subprocess.run(args, cwd=ROOT)
        assert result.returncode in (0, 1)
        assert jobs.heartbeat(job, lease_seconds=1800)
    assert len(read(DOC / 'validation.json')['results']) == len(selected['rows'])
    save(DOC / 'staging-metadata-retry/retry.json', {'reason': 'native matching row lacks sourceTile; use existing shape_prepare.entry',
                                                 'geometryChanges': 0, 'sourceBytesChanged': False, 'pipelineSHA256': sha(__file__)})


def recover_missing():
    """One bounded exact R2 restore attempt; never replace a changed source revision."""
    frozen = read(DOC / 'selection.json.gz')
    missing = [r for r in frozen['rows'] if not r['cachedAsset']]
    assert len(missing) == 1
    row = missing[0]
    claim = reservations.claim('codex-xl-source-restore-' + str(uuid.uuid4()),
                               ['building:' + row['uid']], batch=BATCH + '-source-restore')
    assert claim['ok'], claim
    receipt = claim['reservation']
    try:
        sys.path.insert(0, str(HERE.parent / 'landmark-resume'))
        sys.path.insert(0, str(HERE.parent / 'citywide-native'))
        from r2_snapshot import R2Store, verify_object
        from source_cache import validate_artifact
        from dotenv import dotenv_values
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            result = connection.execute('SELECT result FROM astra_modelling.native_stage_results WHERE cache_key=%s',
                                        (row['native']['cacheKey'],)).fetchone()[0]
        artifacts = [validate_artifact(a) for a in result['artifacts'] if a['kind'] == 'original-and-prepared-sheet']
        assert len(artifacts) == 1
        artifact = artifacts[0]
        report = {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'artifact': artifact,
                  'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'sourceRevisionSubstituted': False}
        for key, value in dotenv_values(ROOT / '.env.modelling').items():
            if key.startswith('R2_') and value and value != '[SENSITIVE]':
                os.environ.setdefault(key, value)
        report['cacheAccessConfigured'] = all(os.environ.get(k) for k in
                                               ('R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY')) and bool(
                                                   os.environ.get('R2_ENDPOINT_URL') or os.environ.get('R2_ACCOUNT_ID'))
        try:
            store = R2Store('hk-sandbox-assets')
            bundle = LOCAL / 'restore' / (artifact['sha256'] + '.tar.gz')
            bundle.parent.mkdir(parents=True, exist_ok=True)
            verify_object(store, artifact['key'], artifact['sha256'], artifact['bytes'], bundle)
            with tarfile.open(bundle, 'r:gz') as archive:
                matches = [m for m in archive if Path(m.name).name == row['sourceSHA256'] + '.glb.gz']
                assert len(matches) == 1 and matches[0].isfile()
                raw = archive.extractfile(matches[0]).read()
                assert digest(raw) == row['sourceSHA256'] and len(raw) == row['native']['model']['asset']['bytes']
            target = LOCAL / 'assets' / (row['sourceSHA256'] + '.glb.gz')
            target.write_bytes(raw)
            report.update(state='exact-source-restored', path=rel(target))
        except Exception as error:
            details = getattr(error, 'response', {}).get('Error', {})
            report.update(state='pinned-source-cache-unavailable', errorType=type(error).__name__, errorCode=details.get('Code'))
        save(DOC / 'missing-source-restore.json', report)
        print(json.dumps(report), flush=True)
    finally:
        reservations.release(receipt)


def complete():
    frozen = read(DOC / 'selection.json.gz')
    supports = read(DOC / 'installed-support-inputs.json')['sources']
    resources = sorted({'building:' + r['uid'] for r in frozen['rows'] + supports})
    claim = reservations.claim('codex-xl-next100-final-' + str(uuid.uuid4()), resources, batch=BATCH)
    assert claim['ok'], claim
    save(LOCAL / 'final-reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
                    'run', '--lease-file', str(LOCAL / 'final-reservation.json'), '--',
                    sys.executable, __file__, 'complete-owned'], cwd=ROOT, check=True)


def complete_owned():
    receipt = read(LOCAL / 'final-reservation.json')
    job = read(LOCAL / 'job.json')
    assert reservations.owns(receipt) and jobs.heartbeat(job, lease_seconds=1800)
    frozen = read(DOC / 'selection.json.gz')
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert sha(manifest_path) == frozen['manifestSHA256']
    metrics = read(DOC / 'metrics.json')
    for path, expected in metrics['inputHashes'].items():
        assert sha(ROOT / path) == expected, path
    contexts = read(DOC / 'context.json.gz')
    assert not contexts['errors']
    for context in contexts['rows']:
        for tile, expected in context['neighbourTileHashes'].items():
            assert sha(ROOT / '3d-viewer' / tile) == expected, tile
    support = read(DOC / 'installed-support-checks.json.gz')
    for path, expected in support['inputHashes'].items():
        assert sha(ROOT / path) == expected, path
    assert all(not r['interface']['passed'] for r in support['rows'])
    by_support = {}
    for row in support['rows']:
        by_support.setdefault(row['uid'], []).append(row)
    by_context = {r['uid']: r for r in contexts['rows']}
    by_metric = {r['uid']: r for r in metrics['rows']}
    validation = read(DOC / 'validation.json')
    by_validation = {r['uid']: r for r in validation['results']}
    dependencies = {r['uid']: r for r in read(DOC / 'dependency-preflight.json')['rows']}
    assert set(by_metric) == set(by_validation) == set(by_context) == set(dependencies)
    assert len(by_metric) == 99 and not any(r.get('error') for r in by_metric.values())
    policy = module('next100_policy', 'acceptance-policy.py')
    direct = module('next100_direct', 'xl-remaining-direct.py')
    current = installed()
    restore = read(DOC / 'missing-source-restore.json')
    assert restore['state'] == 'pinned-source-cache-unavailable'
    rows = []
    eligible = []
    for original in frozen['rows']:
        uid = original['uid']
        assert uid not in current
        assert sha(ROOT / '3d-viewer' / original['source']['tile']) == original['source']['tileSHA256']
        reasons = []
        if uid not in by_metric:
            primary = 'source-cache-access'
            reasons = ['pinned-source-not-cached', 'r2-cache-access-unconfigured', 'government-source-revision-changed']
            next_step = 'Restore the exact recorded R2 bundle using configured credentials; verify the existing source SHA, then run contact/context checks. Do not substitute a changed government revision.'
        else:
            metric = by_metric[uid]
            identity = by_context[uid]['identity']
            reasons = policy.reasons({'state': 'runtime-validated-awaiting-acceptance',
                                     'sourceSHA256': original['sourceSHA256']}, metric, metrics['profiles']['mobile'])
            identity_clear = direct.identity_clear(identity)
            if not identity_clear:
                reasons.append('detailed-projected-source-identity-or-assembly')
            reasons.extend(by_validation[uid].get('concerns', []))
            if by_validation[uid]['outcome'] == 'validation-exception':
                reasons.append('runtime-terrain-sampler-conflict')
                primary = 'runtime-terrain-sampler-conflict'
                next_step = 'Resolve the overlapping drawn-terrain/sampler surfaces at the saved exact source roof position; retest source, seam and all affected native neighbours.'
            elif dependencies[uid]['blockers']:
                reasons.append('fallback-support-migration-required')
                primary = 'fallback-support-migration'
                next_step = 'Prove the exact native support interface for the recorded fallback-dependent UID before changing either dependency state or source installation.'
            elif uid in by_support:
                reasons.append('exact-native-support-interface-unresolved')
                primary = 'native-support-interface'
                next_step = 'Resolve the recorded original source faces and failed native podium interfaces under the existing 0.5m rule; no geometry/elevation edits or tolerance widening.'
            elif not identity_clear:
                primary = 'source-identity-or-assembly'
                next_step = 'Resolve detailed projection/component coverage against the saved exact object/CSUID and intersecting forms. Parent/name/nearby bounding overlap alone is not proof.'
            else:
                primary = 'terrain-contact-or-missing-support'
                next_step = ('Locate an exact source support and prove every native lower-rim contact; reuse original meshes and retain all terrain/neighbour/publication gates.'
                             if metric['minSurfaceGap'] >= -.5 else
                             'Evaluate source-backed terrain and full-face foundation evidence without moving source elevations; preserve installed native surfaces and retest affected neighbours.')
            if not reasons:
                eligible.append(uid)
        rows.append({'uid': uid, 'modelId': original['modelId'], 'name': original.get('name'),
                     'sectionId': original['sectionId'], 'sourceSHA256': original['sourceSHA256'],
                     'nativeCacheKey': original['native']['cacheKey'], 'nativeResultSHA256': original['native']['resultSha'],
                     'sourceSheet': original['native']['sheet'], 'humanStatus': 'held-unknown',
                     'state': 'technical-checkpoint-held', 'primaryHold': primary,
                     'reasons': sorted(set(reasons)), 'nextStep': next_step,
                     'previousCheckpoint': original['previousCheckpoint'],
                     'currentReview': original['currentReview'], 'exactSourceRecovered': uid in by_metric,
                     'metrics': by_metric.get(uid), 'validation': by_validation.get(uid),
                     'context': by_context.get(uid), 'dependencyPreflight': dependencies.get(uid),
                     'supportProbes': by_support.get(uid, []), 'sourceRestore': restore if uid == restore['uid'] else None,
                     'scriptedCheckpointComplete': True, 'queuedFollowup': False, 'activeWorker': False,
                     'requiresAI': False, 'requiresHumanDecision': False,
                     'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'installed': False})
    assert not eligible, ('Complete acceptance/publication for clear candidates before finalizing', eligible)
    counts = {key: sum(r['humanStatus'] == key for r in rows) for key in
              ('installed', 'to-do', 'held-human', 'held-ai', 'held-unknown', 'in-process')}
    assert sum(counts.values()) == 100 and counts['in-process'] == 0
    macro = read(BASE / 'selection.json.gz')['rows']
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        actual = dict(connection.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r '
                                         'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                                         'WHERE m.run_id=%s AND r.cache_key=ANY(%s)',
                                         (NATIVE_RUN, sorted({r['native']['cacheKey'] for r in frozen['rows']}))))
    assert all(actual[r['native']['cacheKey']] == r['native']['resultSha'] for r in frozen['rows'])
    refs = ['selection.json.gz', 'check-selection.json.gz', 'context.json.gz', 'metrics.json',
            'validation.json', 'dependency-preflight.json', 'installed-support-inputs.json',
            'installed-support-checks.json.gz', 'missing-source-restore.json',
            'staging-metadata-retry/retry.json']
    evidence = [{'path': rel(DOC / name), 'sha256': sha(DOC / name)} for name in refs]
    report = {'batch': BATCH, 'stage': STAGE, 'jobId': job['id'], 'models': len(rows), 'humanCounts': counts,
              'primaryHoldCounts': dict(Counter(r['primaryHold'] for r in rows)), 'rows': rows,
              'loaderSourceCommit': frozen['sourceCommit'], 'pipelineSHA256': sha(__file__),
              'detailedIdentityPolicySHA256': sha(HERE / 'xl-remaining-direct.py'),
              'numericalPolicySHA256': sha(HERE / 'acceptance-policy.py'),
              'checks': {'exactCachedSources': 99, 'loaderDecoded': validation['loaderAccepted'],
                         'runtimePassed': validation['checksPassed'], 'runtimeExceptions': validation['exceptions'],
                         'completeContactRows': len(by_metric), 'currentContextRows': len(by_context),
                         'sourceSamples': sum(r['checks'] for r in by_metric.values()),
                         'nativeSupportPairs': len(support['rows']), 'nativeSupportPairsPassed': 0},
              'widerXLCheckpoint': {'models': len(macro), 'installed': sum(r['uid'] in current for r in macro),
                                    'held': sum(r['uid'] not in current for r in macro)},
              'evidenceRefs': evidence, 'newlyInstalled': 0, 'activeWorkers': 0, 'queuedFollowups': 0,
              'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'viewerChanges': 0,
              'qualification': 'The bounded current-code CPU/context pass is complete; the sources are not installed and their technical blockers remain. No architectural AI judgement, geometry edits, tolerance waiver, browser acceptance or region completion is implied. Future technical investigation is saved, not queued as a running task.'}
    save(DOC / 'results.json.gz', report)
    result = {**report, 'evidence': {'path': rel(DOC / 'results.json.gz'), 'sha256': sha(DOC / 'results.json.gz')}}
    with connect() as connection:
        connection.row_factory = dict_row
        connection.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        group = reservations._current(connection, receipt)
        assert group and {'building:' + r['uid'] for r in frozen['rows']} <= set(group['resources'])
        assert connection.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() "
                                  "WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                                  (Jsonb(result), job['id'], job['owner'], job['token'])).rowcount == 1
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        assert connection.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s AND status=\'complete\'',
                                  (job['id'],)).fetchone()[0] == result
    save(DOC / 'summary.json', {k: v for k, v in report.items() if k not in ('rows', 'evidenceRefs')})
    save(DOC / 'neon-sync.json', {'jobId': job['id'], 'verifiedRows': len(rows), 'exactResultMatch': True,
                                'sourceAndJobFenced': True, 'evidenceRefsVerified': len(evidence), 'modelReviewWrites': 0})
    print(json.dumps({'humanCounts': counts, 'primaryHoldCounts': report['primaryHoldCounts'],
                      'checks': report['checks'], 'jobId': job['id']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['freeze', 'start', 'execute', 'retry-runtime', 'recover-missing', 'complete', 'complete-owned'])
    args = parser.parse_args()
    {'freeze': freeze, 'start': start, 'execute': execute, 'retry-runtime': retry_runtime,
     'recover-missing': recover_missing, 'complete': complete, 'complete-owned': complete_owned}[args.phase]()
