"""Publish the exact Horizon Cove government assembly after deterministic acceptance."""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('second', Path(__file__).with_name('xxl-second-pass.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT, HERE = s.ROOT, s.HERE
DOC = s.DOC / 'fourth-pass/horizon-cove'
LOCAL = s.LOCAL / 'horizon-cove-install'
STAGE = HERE / 'accepted/government-xxl-horizon-cove-20260913'
UID = 'landsd/283473:0'
TOWER = 'landsd/282761:0'
BATCH = 'government-xxl-horizon-cove-20260913'
read, save, h, rel = s.read, s.save, s.h, s.rel
sys.path.insert(0, str(HERE.parent / 'model-review-ledger'))
import ledger
spec = importlib.util.spec_from_file_location('direct', HERE / 'integrate.py')
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def verified_report(name, uids):
    report = read(DOC / name)
    assert report.get('passed') and not report['errors']
    expected = {(uid, width, time) for uid in uids for width in (1280, 390) for time in ('15:00', '22:00')}
    actual = {(view['uid'], view['width'], view['time']) for view in report['views'] if 'time' in view}
    assert actual == expected
    assert {view['uid'] for view in report['views'] if view.get('fallbackRetained')} == {UID}
    assert report['aiCalls'] == 0 and not report['architectureReview']
    for view in report['views']:
        if 'file' in view:
            assert view['fullyFramed'] and view['visible'] and not view['overflow']
            assert abs(view['ground'] - view['groundSampler']) <= .004
    return report


def start():
    catalogue = read(STAGE / 'catalogue.json')
    ids = {entry['uid'] for entry in catalogue['models']}
    assert ids == {UID, TOWER}
    resources = ['building:' + uid for uid in ids]
    claim = s.reservations.claim('codex-horizon-cove-import-' + str(uuid.uuid4()), resources, batch=BATCH)
    assert claim['ok']
    save(LOCAL / 'import-reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'import-reservation.json'), '--', sys.executable, __file__, 'owned'])


def owned():
    receipt = LOCAL / 'import-reservation.json'
    assert s.reservations.owns(read(receipt))
    catalogue = read(STAGE / 'catalogue.json')
    ids = {entry['uid'] for entry in catalogue['models']}
    assert ids == {UID, TOWER} and len(catalogue['models']) == 2
    for entry in catalogue['models']:
        assert h(STAGE / entry['asset']) == entry['sha256']
        assert entry['placementReviewed'] and entry['sourceIdentityReviewed'] and entry['identityReviewApproved']
    sampled = {UID, TOWER}
    verified_report('staged-browser.json', sampled)
    result = read(DOC / 'result.json')
    assert result['passed'] and result['policy'] == 'original-government-horizon-cove-assembly-v1'
    assert result['uids'] == [UID, TOWER] and not result['reasons']
    assert result['aiCalls'] == 0 and result['modelGeometryChanges'] == 0
    validation = read(DOC / 'validation.json')
    assert validation['loaderAccepted'] == validation['checksPassed'] == 2
    assert validation['exceptions'] == 0
    assert validation['concerns'] == {'sampled-terrain-above-model-bottom': 2, 'sampled-ground-gap-below-model-bottom': 1}
    metrics = read(DOC / 'metrics.json')
    assert len(metrics['rows']) == 2 and metrics['aiCalls'] == metrics['geometryChanges'] == 0
    assert all(row.get('sourcePreserved') and not row.get('missingTerrain') for row in metrics['rows'])
    assert not read(DOC / 'neighbour-checks.json')['patches'][0]['blockedBy']
    recovery = read(DOC / 'support-source-recovery.json')
    assert recovery['uid'] == TOWER and recovery['sourceSHA256'] == next(e['sha256'] for e in catalogue['models'] if e['uid'] == TOWER)
    assert recovery['aiCalls'] == recovery['geometryChanges'] == 0
    support = read(DOC / 'native-support.json')
    assert support['towerUid'] == TOWER and support['supportUid'] == UID and support['contactsWithinHalfMetre'] == support['rimSamples'] == 16 and support['maxDistance'] < .00001
    terrain = read(DOC / 'terrain-result.json')
    assert terrain['aiCalls'] == terrain['modelGeometryChanges'] == 0 and not terrain['blockedBy']
    decision = {
        'policy': result['policy'],
        'primaryUid': UID,
        'modelCount': 2,
        'sourceModels': [{'uid': entry['uid'], 'sha256': entry['sha256']} for entry in catalogue['models']],
        'catalogueSHA256': h(STAGE / 'catalogue.json'),
        'planSHA256': h(STAGE / 'plan.json'),
        'resultSHA256': h(DOC / 'result.json'),
        'metricsSHA256': h(DOC / 'metrics.json'),
        'validationSHA256': h(DOC / 'validation.json'),
        'neighbourChecksSHA256': h(DOC / 'neighbour-checks.json'),
        'supportRecoverySHA256': h(DOC / 'support-source-recovery.json'),
        'supportContactSHA256': h(DOC / 'native-support.json'),
        'terrainResolutionSHA256': h(DOC / 'terrain-result.json'),
        'stagedBrowserSHA256': h(DOC / 'staged-browser.json'),
        'aiCallsThisImport': 0,
        'geometryChanges': 0,
    }
    save(DOC / 'decision.json', decision)
    pointer_path = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer = read(pointer_path)
    inventory = read(ROOT / pointer['inventory'])
    parts = {part['uid']: part for part in inventory['parts']}
    source_forms = {form['uid']: form for form in read(STAGE / 'source-forms.json')}
    for entry in catalogue['models']:
        previous = parts.get(entry['uid'], {})
        source = source_forms[entry['uid']]
        parts[entry['uid']] = {
            'uid': entry['uid'],
            'name': entry['label'],
            'landmarkIds': previous.get('landmarkIds', []),
            'objectId': entry['objectId'],
            'csuid': entry['buildingCSUID'],
            'candidate': {'sha256': entry['sha256']},
            'sourceProgress': 'prepared-for-review',
            'classification': 'script-verified-original-government-assembly',
            'knownHold': False,
        }
        assert source['uid'] == entry['uid']
    ordered = sorted(parts.values(), key=lambda row: row['uid'])
    snapshot = s.digest(s.jobs.encode([ordered, decision]).encode())[:16]
    inventory_path = pointer_path.parent / f'source-review-inventory-{snapshot}.json'
    save(inventory_path, {**inventory, 'snapshotId': snapshot, 'derivedFrom': pointer['snapshotId'], 'parts': ordered})
    ledger.seed(inventory_path, inherit=pointer['snapshotId'])
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    effort = {'method': 'scripted', 'ai_model': None, 'reasoning_effort': 'not-applicable', 'issue': 'HKS-203', 'run_id': snapshot, 'output_ref': rel(DOC / 'decision.json')}
    observation = 'Exact unchanged Horizon Cove government podium and tower with a deterministic five-metre source-terrain grid and exact tower-to-podium contact passed source, neighbour, stage/live runtime, picking, collision, terrain-ray and fallback/retry checks. No AI modelling, review or model geometry edits.'
    ledger.record_many(snapshot, receipt, [(uid, 'approved-for-integration', DOC / 'decision.json', observation, commit) for uid in sorted(ids)], effort=effort, request_id=BATCH + '-approved-' + snapshot)
    publish = [sys.executable, str(HERE.parent / 'model-integration-20260909/publish.py'), rel(STAGE / 'plan.json'), '--receipt', str(receipt), '--phase', BATCH]
    call(publish)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    before = manifest.read_bytes()
    (LOCAL / 'manifest-before.json').write_bytes(before)
    call(publish + ['--apply'])
    try:
        call(['node', str(HERE / 'resolution-browser.mjs'), 'live', rel(STAGE / 'browser-config.json')])
        verified_report('live-browser.json', sampled)
    except BaseException:
        manifest.write_bytes(before)
        raise
    acceptance = {**decision, 'snapshot': snapshot, 'liveBrowserSHA256': h(DOC / 'live-browser.json'), 'manifestSHA256': h(manifest)}
    save(DOC / 'installed-acceptance.json', acceptance)
    ledger.record_many(snapshot, receipt, [(uid, 'installed-verified', DOC / 'installed-acceptance.json', observation, commit) for uid in sorted(ids)], effort=effort, request_id=BATCH + '-installed-' + snapshot)
    assert read(pointer_path) == pointer
    save(pointer_path, {**pointer, 'snapshotId': snapshot, 'inventory': rel(inventory_path), 'previousSnapshots': [*pointer.get('previousSnapshots', []), pointer['snapshotId']]})
    call([sys.executable, str(HERE.parent / 'building-progress/export.py'), '--refresh'])
    call(['node', str(ROOT / '3d-viewer/scripts/build_progress.mjs')])
    save(DOC / 'summary.json', {'installedUids': sorted(ids), 'primaryUid': UID, 'supportingModels': 1, 'snapshot': snapshot, 'aiCalls': 0, 'geometryChanges': 0, 'progress': read(ROOT / '3d-viewer/city/data/building-progress.json')})
    print(json.dumps({'installed': len(ids), 'primary': UID, 'snapshot': snapshot, 'aiCalls': 0}), flush=True)


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
