"""Publish the exact Telford government assembly after deterministic acceptance."""
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
DOC = s.DOC / 'third-pass/telford'
LOCAL = s.LOCAL / 'telford-install'
STAGE = HERE / 'accepted/government-xxl-telford-20260912'
UID = 'landsd/226033:0'
PODIUM = 'landsd/263578:0'
BATCH = 'government-xxl-telford-20260912'
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
    assert len(ids) == 61 and UID in ids and PODIUM in ids
    resources = ['building:' + uid for uid in ids]
    claim = s.reservations.claim('codex-telford-import-' + str(uuid.uuid4()), resources, batch=BATCH)
    assert claim['ok']
    save(LOCAL / 'import-reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'import-reservation.json'), '--', sys.executable, __file__, 'owned'])


def owned():
    receipt = LOCAL / 'import-reservation.json'
    assert s.reservations.owns(read(receipt))
    catalogue = read(STAGE / 'catalogue.json')
    ids = {entry['uid'] for entry in catalogue['models']}
    assert len(ids) == len(catalogue['models']) == 61 and UID in ids and PODIUM in ids
    for entry in catalogue['models']:
        assert h(STAGE / entry['asset']) == entry['sha256']
        assert entry['placementReviewed'] and entry['sourceIdentityReviewed'] and entry['identityReviewApproved']
    sampled = {UID, PODIUM, 'landsd/85820:0', 'landsd/209819:0'}
    verified_report('staged-browser.json', sampled)
    result = read(DOC / 'result.json')
    assert result['passed'] and result['policy'] == 'original-government-telford-assembly-v1'
    assert result['models'] == 61 and not result['reasons'] and not result['blockedNeighbours']
    assert result['aiCalls'] == 0 and result['modelGeometryChanges'] == 0
    validation = read(DOC / 'validation.json')
    assert validation['loaderAccepted'] == validation['checksPassed'] == 61
    assert validation['exceptions'] == 0
    assert validation['concerns'] == {'sampled-ground-gap-below-model-bottom': 59}
    metrics = read(DOC / 'metrics.json')
    assert len(metrics['rows']) == 61 and metrics['aiCalls'] == metrics['geometryChanges'] == 0
    assert all(row.get('sourcePreserved') and not row.get('missingTerrain') for row in metrics['rows'])
    assert not read(DOC / 'neighbour-checks.json')['patches'][0]['blockedBy']
    recovery = read(DOC / 'support-source-recovery.json')
    assert recovery['exactSourceMatches'] == recovery['recovered'] == 60
    assert recovery['missingUids'] == ['landsd/107325:0'] and recovery['aiCalls'] == recovery['geometryChanges'] == 0
    terrain = read(DOC / 'terrain-resolution.json')
    assert terrain['aiCalls'] == terrain['modelGeometryChanges'] == 0
    decision = {
        'policy': result['policy'],
        'primaryUid': UID,
        'modelCount': 61,
        'sourceModels': [{'uid': entry['uid'], 'sha256': entry['sha256']} for entry in catalogue['models']],
        'catalogueSHA256': h(STAGE / 'catalogue.json'),
        'planSHA256': h(STAGE / 'plan.json'),
        'resultSHA256': h(DOC / 'result.json'),
        'metricsSHA256': h(DOC / 'metrics.json'),
        'validationSHA256': h(DOC / 'validation.json'),
        'neighbourChecksSHA256': h(DOC / 'neighbour-checks.json'),
        'supportRecoverySHA256': h(DOC / 'support-source-recovery.json'),
        'supportContactSHA256': h(DOC / 'native-support-contact.json'),
        'terrainResolutionSHA256': h(DOC / 'terrain-resolution.json'),
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
    observation = 'Exact unchanged government Telford estate assembly with 61 source models, bounded native terrain seam repair and explicit podium dependencies passed source, neighbour, stage/live runtime, picking, collision, terrain-ray and fallback/retry checks. No AI modelling, review or geometry edits.'
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
    save(DOC / 'summary.json', {'installedUids': sorted(ids), 'primaryUid': UID, 'supportingModels': 60, 'snapshot': snapshot, 'aiCalls': 0, 'geometryChanges': 0, 'progress': read(ROOT / '3d-viewer/city/data/building-progress.json')})
    print(json.dumps({'installed': len(ids), 'primary': UID, 'snapshot': snapshot, 'aiCalls': 0}), flush=True)


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
