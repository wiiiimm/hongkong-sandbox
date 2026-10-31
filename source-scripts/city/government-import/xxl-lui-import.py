"""Publish unchanged Lui Seng Chun after identity and runtime acceptance."""
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('second', Path(__file__).with_name('xxl-second-pass.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT, HERE = s.ROOT, s.HERE
BASE = s.DOC
DOC = BASE / 'lui-install'
LOCAL = s.LOCAL / 'lui-install'
STAGE = HERE / 'accepted/government-xxl-lui-20260912'
UID = 'landsd/160070:0'
BATCH = 'government-xxl-lui-20260912'
read, save, h, rel = s.read, s.save, s.h, s.rel
sys.path.insert(0, str(HERE.parent / 'model-review-ledger'))
import ledger
spec = importlib.util.spec_from_file_location('direct', HERE / 'integrate.py')
direct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct)


def call(args):
    subprocess.run(args, cwd=ROOT, check=True)


def start():
    claim = s.reservations.claim('codex-lui-import-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH)
    assert claim['ok']
    save(LOCAL / 'import-reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'import-reservation.json'), '--', sys.executable, __file__, 'owned'])


def owned():
    receipt = LOCAL / 'import-reservation.json'
    assert s.reservations.owns(read(receipt))
    catalogue = read(STAGE / 'catalogue.json')
    assert [model['uid'] for model in catalogue['models']] == [UID]
    model = catalogue['models'][0]
    assert h(STAGE / model['asset']) == model['sha256']
    direct.browser_verified(DOC / 'staged-browser.json', {UID})
    validation = read(DOC / 'validation.json')
    assert validation['loaderAccepted'] == validation['checksPassed'] == 1
    assert validation['exceptions'] == 0 and validation['concerns'] == {}
    metrics = read(DOC / 'metrics.json')
    metric = metrics['rows'][0]
    assert metric['uid'] == UID and metric['sourcePreserved'] and not metric['missingTerrain']
    assert metric['budget']['residentBytes'] <= metrics['profiles']['mobile']['selectedResidentBytes']
    review_path = BASE / 'sol-review-proposal/review-result.json'
    review = read(review_path)
    assert review['decision'] == 'identity-supported-as-one-source-architectural-assembly'
    assert review['sourceSHA256'] == model['sha256'] and not review['geometryEdited']
    source = next(row for row in read(BASE / 'runtime-selection.json.gz')['rows'] if row['uid'] == UID)
    with s.connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        native = connection.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (source['native']['cacheKey'],)).fetchone()
        state = connection.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1', (UID,)).fetchone()
    assert native and native[0] == source['native']['resultSha']
    assert not state or state[0] != 'installed-verified'
    decision = {
        'policy': 'approved-identity-selected-xxl-runtime-v1',
        'uid': UID,
        'sourceSHA256': model['sha256'],
        'catalogueSHA256': h(STAGE / 'catalogue.json'),
        'planSHA256': h(STAGE / 'plan.json'),
        'identityReview': {'path': rel(review_path), 'sha256': h(review_path), 'model': review['reviewer']['model']},
        'metricsSHA256': h(DOC / 'metrics.json'),
        'validationSHA256': h(DOC / 'validation.json'),
        'stagedBrowserSHA256': h(DOC / 'staged-browser.json'),
        'aiCallsThisImport': 0,
        'priorApprovedIdentityReviewCalls': 1,
        'geometryChanges': 0,
    }
    save(DOC / 'decision.json', decision)
    pointer_path = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer = read(pointer_path)
    inventory = read(ROOT / pointer['inventory'])
    parts = {part['uid']: part for part in inventory['parts']}
    parts[UID] = {
        'uid': UID,
        'name': model['label'],
        'landmarkIds': parts.get(UID, {}).get('landmarkIds', []),
        'objectId': model['objectId'],
        'csuid': model['buildingCSUID'],
        'candidate': {'sha256': model['sha256']},
        'sourceProgress': 'prepared-for-review',
        'classification': 'identity-reviewed-original-government-source',
        'knownHold': False,
    }
    ordered = sorted(parts.values(), key=lambda row: row['uid'])
    snapshot = s.digest(s.jobs.encode([ordered, decision]).encode())[:16]
    inventory_path = pointer_path.parent / f'source-review-inventory-{snapshot}.json'
    save(inventory_path, {**inventory, 'snapshotId': snapshot, 'derivedFrom': pointer['snapshotId'], 'parts': ordered})
    ledger.seed(inventory_path, inherit=pointer['snapshotId'])
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    effort = {'method': 'unknown', 'ai_model': 'gpt-5.6-sol', 'reasoning_effort': 'medium', 'issue': 'HKS-203', 'run_id': snapshot, 'output_ref': rel(DOC / 'decision.json')}
    observation = 'Exact unchanged Lui Seng Chun government source. Prior bounded Sol review supports source identity/component scope; current source hash, terrain, selected-mobile budget, staged/live browser, picking, collision and fallback/retry checks pass. No AI modelling or geometry edits.'
    ledger.record_many(snapshot, receipt, [(UID, 'approved-for-integration', DOC / 'decision.json', observation, commit)], effort=effort, request_id=BATCH + '-approved-' + snapshot)
    publish = [sys.executable, str(HERE.parent / 'model-integration-20260909/publish.py'), rel(STAGE / 'plan.json'), '--receipt', str(receipt), '--phase', BATCH]
    call(publish)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    before = manifest.read_bytes()
    (LOCAL / 'manifest-before.json').write_bytes(before)
    call(publish + ['--apply'])
    try:
        call(['node', str(HERE / 'resolution-browser.mjs'), 'live', rel(STAGE / 'browser-config.json')])
        direct.browser_verified(DOC / 'live-browser.json', {UID})
    except BaseException:
        manifest.write_bytes(before)
        raise
    acceptance = {**decision, 'snapshot': snapshot, 'liveBrowserSHA256': h(DOC / 'live-browser.json'), 'manifestSHA256': h(manifest)}
    save(DOC / 'installed-acceptance.json', acceptance)
    ledger.record_many(snapshot, receipt, [(UID, 'installed-verified', DOC / 'installed-acceptance.json', observation, commit)], effort=effort, request_id=BATCH + '-installed-' + snapshot)
    assert read(pointer_path) == pointer
    save(pointer_path, {**pointer, 'snapshotId': snapshot, 'inventory': rel(inventory_path), 'previousSnapshots': [*pointer.get('previousSnapshots', []), pointer['snapshotId']]})
    call([sys.executable, str(HERE.parent / 'building-progress/export.py'), '--refresh'])
    call(['node', str(ROOT / '3d-viewer/scripts/build_progress.mjs')])
    save(DOC / 'summary.json', {'installedUids': [UID], 'snapshot': snapshot, 'aiCallsThisImport': 0, 'priorApprovedIdentityReviewCalls': 1, 'geometryChanges': 0, 'progress': read(ROOT / '3d-viewer/city/data/building-progress.json')})
    print(json.dumps({'installed': UID, 'snapshot': snapshot, 'aiCallsThisImport': 0}), flush=True)


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
