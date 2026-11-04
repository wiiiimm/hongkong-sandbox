"""Stage unchanged Lui Seng Chun source after its bounded identity review."""
import gzip
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
BASE = s.DOC
DOC = BASE / 'lui-install'
LOCAL = s.LOCAL / 'lui-install'
STAGE = HERE / 'accepted/government-xxl-lui-20260912'
UID = 'landsd/160070:0'
BATCH = 'government-xxl-lui-20260912'
read, save, h, rel = s.read, s.save, s.h, s.rel


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def start():
    resources = ['building:' + UID, 'building:landsd/252763:0']
    claim = s.reservations.claim('codex-lui-stage-' + str(uuid.uuid4()), resources, batch=BATCH)
    assert claim['ok']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'reservation.json'), '--', sys.executable, __file__, 'owned'])


def owned():
    assert s.reservations.owns(read(LOCAL / 'reservation.json'))
    review_path = BASE / 'sol-review-proposal/review-result.json'
    review = read(review_path)
    assert review['uid'] == UID
    packet = read(BASE / 'sol-review-proposal/packet.json')
    assert review['decision'] == 'identity-supported-as-one-source-architectural-assembly'
    assert review['integrationApproval'] is False and review['geometryEdited'] is False
    rows = read(BASE / 'runtime-selection.json.gz')
    row = next(item for item in rows['rows'] if item['uid'] == UID)
    entry = dict(row['candidate']['entry'])
    assert entry['sha256'] == review['sourceSHA256']
    assert h(row['candidate']['path']) == entry['sha256']
    with s.connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        native = connection.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (row['native']['cacheKey'],)).fetchone()
    assert native and native[0] == row['native']['resultSha'] == packet['nativeSource']['resultSHA256']
    entry.update(
        priority='landmark',
        placementReviewed=True,
        sourceIdentityReviewed=True,
        identityReviewApproved=True,
        placementReview='Exact unchanged government source. Bounded identity/component review supports one compact Lui Seng Chun architectural assembly; complete native terrain sampling passes. Runtime/browser acceptance remains mandatory. No geometry edits.',
    )
    catalogue = {
        'schemaVersion': 1,
        'kind': 'staged-official-model-catalogue',
        'datasetId': 'landsd_rcd_1742809441342_98380',
        'area': 'Lui Seng Chun exact government source',
        'crs': 'EPSG:2326',
        'verticalDatum': 'Hong Kong Principal Datum',
        'coordinatePolicy': 'Unchanged native source nodes/float bits; one city translation',
        'loadingPolicy': 'Landmark range; exact original source retained',
        'rootTranslation': [-834500, 0, 816500],
        'counts': {'packedModels': 1},
        'models': [entry],
    }
    save(STAGE / 'catalogue.json', catalogue)
    save(STAGE / 'catalogue-index.json', {'models': 1, 'catalogues': ['catalogue.json']})
    asset = STAGE / entry['asset']
    asset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(row['candidate']['path'], asset)
    assert h(asset) == entry['sha256']
    building = dict(row['source']['building'])
    building['tile'] = Path(row['source']['tile']).stem
    save(STAGE / 'source-forms.json', [building])
    staged_row = {**row, 'candidate': {'path': str(asset), 'entry': entry}}
    selection = {**rows, 'rows': [staged_row], 'manifestSHA256': h(ROOT / '3d-viewer/city/data/manifest.json')}
    save(DOC / 'selection.json.gz', selection)
    save(LOCAL / 'source-forms.json', {UID: row['source']})
    call(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(DOC / 'selection.json.gz'), '--candidates', rel(STAGE), '--out', rel(DOC / 'metrics.json')])
    call(['node', str(HERE.parent / 'building-batch/validate_candidates.mjs'), '--candidates', rel(STAGE), '--source-forms', rel(LOCAL / 'source-forms.json'), '--out', rel(DOC / 'validation.json')], allowed=(0, 1))
    destination = 'city/data/official-models/government-xxl-lui-20260912/catalogue.json'
    save(STAGE / 'plan.json', {'areas': [{'area': catalogue['area'], 'catalogue': rel(STAGE / 'catalogue.json'), 'destination': destination}], 'topLevelTerrainPatches': []})
    save(STAGE / 'browser-config.json', {'stage': rel(STAGE) + '/', 'doc': rel(DOC) + '/', 'catalogueURL': destination, 'terrain': [], 'fitBox': True})
    call(['node', str(HERE / 'resolution-browser.mjs'), 'staged', rel(STAGE / 'browser-config.json')])
    metrics = read(DOC / 'metrics.json')['rows'][0]
    validation = read(DOC / 'validation.json')
    summary = {
        'uid': UID,
        'sourceSHA256': entry['sha256'],
        'identityReview': {'path': rel(review_path), 'sha256': h(review_path), 'decision': review['decision']},
        'sourcePreserved': metrics['sourcePreserved'],
        'budget': metrics['budget'],
        'mobileBudget': read(DOC / 'metrics.json')['profiles']['mobile'],
        'runtimeValidation': validation,
        'stagedBrowser': {'path': rel(DOC / 'staged-browser.json'), 'sha256': h(DOC / 'staged-browser.json')},
        'aiCallsThisStage': 0,
        'geometryChanges': 0,
        'publication': False,
    }
    save(DOC / 'summary.json', summary)
    print(json.dumps({'uid': UID, 'stagedBrowserPassed': read(DOC / 'staged-browser.json')['passed'], 'triangles': entry['triangles'], 'residentBytes': metrics['budget']['residentBytes'], 'aiCalls': 0}), flush=True)


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
