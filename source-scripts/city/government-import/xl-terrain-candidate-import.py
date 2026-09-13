"""Publish a script-verified XL source model with its bounded native terrain patch."""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('terrain_stage', Path(__file__).with_name('xl-stage-terrain-candidate.py'))
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)
s = stage.s
ROOT, HERE = s.ROOT, s.HERE
read, save, h, rel = s.read, s.save, s.h, s.rel

CONFIG = {
    'spectra-3': {
        'uid': 'landsd/265311:0',
        'batch': 'government-xl-spectra-3-20260914',
        'policy': 'original-government-xl-bounded-native-terrain-v1',
        'classification': 'script-verified-original-government-bounded-native-terrain',
        'review': (
            'Exact government source identity and placement verified by object ID, Building CSUID, '
            'full footprint overlap and a 0.97 m centroid offset. The unchanged model and bounded native '
            'terrain pass contact, neighbour and runtime checks.'
        ),
    },
}

sys.path.insert(0, str(HERE.parent / 'model-review-ledger'))
import ledger

direct_spec = importlib.util.spec_from_file_location('direct', HERE / 'integrate.py')
direct = importlib.util.module_from_spec(direct_spec)
direct_spec.loader.exec_module(direct)


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def paths(key):
    config = CONFIG[key]
    check = s.DOC / 'third-pass' / ('terrain-' + key)
    stage_local = s.LOCAL / ('third-pass-terrain-' + key)
    install_local = s.LOCAL / ('third-pass-terrain-' + key + '-install')
    accepted = HERE / 'accepted' / config['batch']
    doc = s.DOC / 'third-pass' / ('terrain-' + key + '-install')
    return config, check, stage_local, install_local, accepted, doc


def start(key):
    config, check, stage_local, install_local, _, _ = paths(key)
    result = read(check / 'result.json')
    assert result['passed'] and result['uid'] == config['uid'] and result['aiCalls'] == 0
    resources = read(stage_local / 'reservation.json')['resources']
    claim = s.reservations.claim(
        'codex-xl-terrain-import-' + key + '-' + str(uuid.uuid4()),
        resources,
        batch=config['batch'],
    )
    assert claim['ok']
    receipt = install_local / 'reservation.json'
    save(receipt, json.loads(json.dumps(claim['reservation'], default=str)))
    call([
        sys.executable,
        str(HERE.parent / 'shared-modelling/reservations.py'),
        'run',
        '--lease-file',
        str(receipt),
        '--',
        sys.executable,
        __file__,
        key,
        'owned',
    ])


def owned(key):
    config, check, stage_local, install_local, accepted, doc = paths(key)
    uid, batch = config['uid'], config['batch']
    receipt = install_local / 'reservation.json'
    assert s.reservations.owns(read(receipt))

    result = read(check / 'result.json')
    assert result['passed'] and result['uid'] == uid and not result['reasons'] and result['aiCalls'] == 0
    selection = read(check / 'selection.json.gz')
    assert len(selection['rows']) == 1 and selection['rows'][0]['uid'] == uid
    source = selection['rows'][0]
    metrics = read(check / 'metrics.json')
    metric = metrics['rows'][0]
    assert metric['uid'] == uid and metric['sourcePreserved'] and not metric['missingTerrain']
    assert metrics['aiCalls'] == metrics['geometryChanges'] == 0
    validation = read(check / 'validation.json')
    assert validation['loaderAccepted'] == validation['checksPassed'] == 1
    assert validation['exceptions'] == 0 and not validation['results'][0]['concerns']
    neighbours = read(check / 'neighbour-checks.json')
    assert neighbours['aiCalls'] == 0 and neighbours['patches'][0]['blockedBy'] == []

    source_catalogue = read(stage_local / 'candidates/catalogue.json')
    assert [model['uid'] for model in source_catalogue['models']] == [uid]
    entry = source_catalogue['models'][0]
    entry.update(
        priority='detail',
        placementReviewed=True,
        sourceIdentityReviewed=True,
        identityReviewApproved=True,
        publicationApproved=True,
        placementReview=config['review'],
    )
    asset = accepted / entry['asset']
    asset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(stage_local / 'candidates' / entry['asset'], asset)
    assert h(asset) == entry['sha256']
    catalogue = {
        **source_catalogue,
        'area': entry['label'] + ' original government model',
        'loadingPolicy': 'Published after deterministic source, terrain, neighbour, runtime and browser checks',
        'models': [entry],
    }
    save(accepted / 'catalogue.json', catalogue)
    save(accepted / 'catalogue-index.json', {'models': 1, 'catalogues': ['catalogue.json']})

    form = dict(source['source']['building'])
    form['tile'] = Path(source['source']['tile']).stem
    save(accepted / 'source-forms.json', [form])
    patch = result['patch']
    patch_source = ROOT / patch['path']
    assert h(patch_source) == patch['sha256']
    patch_destination = accepted / patch_source.name
    shutil.copyfile(patch_source, patch_destination)
    terrain = {
        'source': rel(patch_destination),
        'sha256': h(patch_destination),
        'destination': 'city/data/' + patch_destination.name,
        'resolution': read(patch_destination)['cell'],
        'area': entry['label'] + ' bounded original government terrain',
    }
    catalogue_url = 'city/data/official-models/' + batch + '/catalogue.json'
    plan = {
        'areas': [{
            'area': catalogue['area'],
            'catalogue': rel(accepted / 'catalogue.json'),
            'destination': catalogue_url,
        }],
        'topLevelTerrainPatches': [terrain],
    }
    save(accepted / 'plan.json', plan)
    browser_config = {
        'stage': rel(accepted) + '/',
        'doc': rel(doc) + '/',
        'catalogueURL': catalogue_url,
        'terrain': [terrain],
        'fitBox': True,
        'browserUids': [uid],
        'failureTestUids': [uid],
    }
    save(accepted / 'browser-config.json', browser_config)

    evidence_paths = [
        check / 'result.json',
        check / 'metrics.json',
        check / 'validation.json',
        check / 'neighbour-checks.json',
        check / 'terrain-resolution.json',
        check / 'native-overlap-evidence.json',
        HERE / 'xl-stage-terrain-candidate.py',
        HERE / 'xl-stage-west9zone.py',
        HERE / 'native_patch_resolution.py',
        HERE / 'xl-terrain-candidate-import.py',
        HERE / 'resolution-browser.mjs',
    ]
    evidence = {rel(path): h(path) for path in evidence_paths if path.exists()}
    inputs = {**metrics['inputHashes'], **neighbours['sourceInputHashes']}
    for path, sha in inputs.items():
        assert h(ROOT / path) == sha
    decision = {
        'policy': config['policy'],
        'uid': uid,
        'sourceSHA256': entry['sha256'],
        'catalogueSHA256': h(accepted / 'catalogue.json'),
        'planSHA256': h(accepted / 'plan.json'),
        'inputHashes': inputs,
        'evidenceHashes': evidence,
        'aiCalls': 0,
        'modelGeometryChanges': 0,
    }
    save(doc / 'decision.json', decision)
    call(['node', str(HERE / 'resolution-browser.mjs'), 'staged', rel(accepted / 'browser-config.json')])
    direct.browser_verified(doc / 'staged-browser.json', {uid})
    for path, sha in {**inputs, **evidence}.items():
        assert h(ROOT / path) == sha, 'Input changed during staged browser checks: ' + path

    with s.connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        native = dict(connection.execute(
            'SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',
            (source['native']['cacheKey'],),
        ))
    assert native[source['native']['cacheKey']] == source['native']['resultSha']

    pointer_path = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer = read(pointer_path)
    inventory = read(ROOT / pointer['inventory'])
    parts = {part['uid']: part for part in inventory['parts']}
    previous = parts.get(uid, {})
    parts[uid] = {
        'uid': uid,
        'name': entry['label'],
        'landmarkIds': previous.get('landmarkIds', []),
        'objectId': entry['objectId'],
        'csuid': entry['buildingCSUID'],
        'candidate': {'sha256': entry['sha256']},
        'sourceProgress': 'prepared-for-review',
        'classification': config['classification'],
        'knownHold': False,
    }
    ordered = sorted(parts.values(), key=lambda row: row['uid'])
    snapshot = s.digest(s.jobs.encode([ordered, decision]).encode())[:16]
    inventory_path = pointer_path.parent / ('source-review-inventory-' + snapshot + '.json')
    save(inventory_path, {**inventory, 'snapshotId': snapshot, 'derivedFrom': pointer['snapshotId'], 'parts': ordered})
    ledger.seed(inventory_path, inherit=pointer['snapshotId'])
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    effort = {
        'method': 'scripted',
        'ai_model': None,
        'reasoning_effort': 'not-applicable',
        'issue': 'HKS-203',
        'run_id': snapshot,
        'output_ref': rel(doc / 'decision.json'),
    }
    observation = config['review'] + ' No AI modelling, review or model geometry edits.'
    ledger.record_many(
        snapshot,
        receipt,
        [(uid, 'approved-for-integration', doc / 'decision.json', observation, commit)],
        effort=effort,
        request_id=batch + '-approved-' + snapshot,
    )

    publish = [
        sys.executable,
        str(HERE.parent / 'model-integration-20260909/publish.py'),
        rel(accepted / 'plan.json'),
        '--receipt',
        str(receipt),
        '--phase',
        batch,
    ]
    call(publish)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    before = manifest.read_bytes()
    (install_local / 'manifest-before.json').write_bytes(before)
    call(publish + ['--apply'])
    try:
        call(['node', str(HERE / 'resolution-browser.mjs'), 'live', rel(accepted / 'browser-config.json')])
        direct.browser_verified(doc / 'live-browser.json', {uid})
    except BaseException:
        manifest.write_bytes(before)
        shutil.rmtree(ROOT / '3d-viewer/city/data/official-models' / batch, ignore_errors=True)
        shutil.rmtree(ROOT / 'docs/astra-city/model-integration-20260909' / batch, ignore_errors=True)
        raise

    acceptance = {
        **decision,
        'snapshot': snapshot,
        'stagedBrowserSHA256': h(doc / 'staged-browser.json'),
        'liveBrowserSHA256': h(doc / 'live-browser.json'),
        'manifestSHA256': h(manifest),
    }
    save(doc / 'installed-acceptance.json', acceptance)
    ledger.record_many(
        snapshot,
        receipt,
        [(uid, 'installed-verified', doc / 'installed-acceptance.json', observation, commit)],
        effort=effort,
        request_id=batch + '-installed-' + snapshot,
    )
    assert read(pointer_path) == pointer
    save(pointer_path, {
        **pointer,
        'snapshotId': snapshot,
        'inventory': rel(inventory_path),
        'previousSnapshots': [*pointer.get('previousSnapshots', []), pointer['snapshotId']],
    })
    call([sys.executable, str(HERE.parent / 'building-progress/export.py'), '--refresh'])
    call(['node', str(ROOT / '3d-viewer/scripts/build_progress.mjs')])
    save(doc / 'summary.json', {
        'installedUids': [uid],
        'snapshot': snapshot,
        'aiCalls': 0,
        'modelGeometryChanges': 0,
        'progress': read(ROOT / '3d-viewer/city/data/building-progress.json'),
    })
    print(json.dumps({'installed': uid, 'snapshot': snapshot, 'aiCalls': 0}), flush=True)


if __name__ == '__main__':
    key = sys.argv[1]
    assert key in CONFIG
    owned(key) if len(sys.argv) > 2 else start(key)
