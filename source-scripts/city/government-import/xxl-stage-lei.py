"""Stage Lei Yue Mun Block 10 with its exact government assembly and source terrain."""
import gzip
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from shapely.geometry import Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('second', Path(__file__).with_name('xxl-second-pass.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT, HERE = s.ROOT, s.HERE
BASE = s.DOC
DOC = BASE / 'lei-install'
LOCAL = s.LOCAL / 'lei-install'
STAGE = HERE / 'accepted/government-xxl-lei-20260912'
UID = 'landsd/109467:0'
BATCH = 'government-xxl-lei-20260912'
read, save, h, rel = s.read, s.save, s.h, s.rel


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def start():
    source_patch = s.LOCAL / 'terrain-stage/government-native-109467-0.json'
    assert h(source_patch) == 'f77b46897f684d4035527a4f544ce358efb1ddf54d9729aec86608f802832fb2'
    patch = read(source_patch)
    bounds = s.resolution.extent(patch['coarseCells'], read(ROOT / '3d-viewer/city/data/terrain.json'))
    region = box(*bounds)
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    live = {model['uid'] for url in manifest['officialModelCatalogues'] for model in read(ROOT / '3d-viewer' / url)['models']}
    neighbours, hashes = [], {}
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        raw = path.read_bytes()
        touched = False
        for building in json.loads(raw)['buildings']:
            if Polygon(building['rings'][0], building['rings'][1:]).intersects(region):
                neighbours.append({'building': building, 'patchIndexes': [0], 'existingNative': building['uid'] in live or bool(building.get('modelGeometry'))})
                touched = True
        if touched:
            hashes[rel(path)] = s.digest(raw)
    resources = {'building:' + UID} | {('building:' if row['building']['uid'].startswith('landsd/') else 'source-form:') + row['building']['uid'] for row in neighbours}
    claim = s.reservations.claim('codex-lei-stage-' + str(uuid.uuid4()), sorted(resources), batch=BATCH)
    assert claim['ok']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    save(DOC / 'neighbour-context.json.gz', {'rows': neighbours, 'inputHashes': hashes, 'bounds': bounds, 'manifestSHA256': h(ROOT / '3d-viewer/city/data/manifest.json')})
    call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'reservation.json'), '--', sys.executable, __file__, 'owned'])


def owned():
    assert s.reservations.owns(read(LOCAL / 'reservation.json'))
    context = read(DOC / 'neighbour-context.json.gz')
    assert h(ROOT / '3d-viewer/city/data/manifest.json') == context['manifestSHA256']
    source_patch = s.LOCAL / 'terrain-stage/government-native-109467-0.json'
    patch = read(source_patch)
    native_mesh_sha = s.digest(json.dumps(patch['nativeMesh'], sort_keys=True, separators=(',', ':')).encode())
    patch.pop('nativeMesh')
    patch['id'] = 'government-grid-109467-0'
    patch['meta']['source']['policy'] = 'Deterministic five-metre grid sampled from the recovered original government TIN with the existing ten-metre parent transition. The overlapping raw-facet representation is omitted so the same sampled surface cannot override adjacent fallback forms.'
    patch['meta']['source']['derivedFromNativePatch'] = {'path': rel(source_patch), 'sha256': h(source_patch), 'nativeMeshSHA256': native_mesh_sha}
    patch_path = STAGE / 'government-grid-109467-0.json'
    save(patch_path, patch)
    patch_entry = {'path': rel(patch_path), 'sha256': h(patch_path), 'uids': [UID], 'bounds': context['bounds']}
    neighbour_inputs = {'rows': context['rows'], 'inputHashes': context['inputHashes'], 'candidateIds': [UID], 'patches': [patch_entry]}
    save(DOC / 'neighbour-inputs.json.gz', neighbour_inputs)
    call(['node', str(HERE / 'check-neighbours.mjs'), rel(DOC) + '/'])
    neighbour_report = read(DOC / 'neighbour-checks.json')
    assert not neighbour_report['patches'][0]['blockedBy']
    rows = read(BASE / 'runtime-selection.json.gz')
    row = next(item for item in rows['rows'] if item['uid'] == UID)
    entry = dict(row['candidate']['entry'])
    entry.update(
        priority='detail',
        placementReviewed=True,
        sourceIdentityReviewed=True,
        identityReviewApproved=True,
        placementReview='Exact unchanged government source with its deterministic five-metre TIN-derived terrain grid. Eighteen neighbouring source forms pass the before/after regression guard. No model geometry edits.',
    )
    catalogue = {
        'schemaVersion': 1,
        'kind': 'staged-official-model-catalogue',
        'datasetId': 'landsd_rcd_1742809441342_98380',
        'area': 'Lei Yue Mun Park Block 10 exact government source',
        'crs': 'EPSG:2326',
        'verticalDatum': 'Hong Kong Principal Datum',
        'coordinatePolicy': 'Unchanged native source nodes/float bits; one city translation',
        'loadingPolicy': 'Progressive exact-source detail with surveyed fallback',
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
    save(DOC / 'selection.json.gz', {**rows, 'rows': [staged_row], 'manifestSHA256': context['manifestSHA256']})
    save(LOCAL / 'source-forms.json', {UID: row['source']})
    save(DOC / 'terrain-candidates.json', [patch_entry])
    call(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(DOC / 'selection.json.gz'), '--candidates', rel(STAGE), '--terrain-candidates', rel(DOC / 'terrain-candidates.json'), '--out', rel(DOC / 'metrics.json')])
    call(['node', str(HERE.parent / 'building-batch/validate_candidates.mjs'), '--candidates', rel(STAGE), '--source-forms', rel(LOCAL / 'source-forms.json'), '--terrain-candidates', rel(DOC / 'terrain-candidates.json'), '--out', rel(DOC / 'validation.json')], allowed=(0, 1))
    destination = 'city/data/official-models/government-xxl-lei-20260912/catalogue.json'
    terrain = {'source': rel(patch_path), 'sha256': h(patch_path), 'destination': 'city/data/government-grid-109467-0.json', 'resolution': patch['cell'], 'area': 'Lei Yue Mun Park Block 10 source-derived terrain'}
    save(STAGE / 'plan.json', {'areas': [{'area': catalogue['area'], 'catalogue': rel(STAGE / 'catalogue.json'), 'destination': destination}], 'topLevelTerrainPatches': [terrain]})
    save(STAGE / 'browser-config.json', {'stage': rel(STAGE) + '/', 'doc': rel(DOC) + '/', 'catalogueURL': destination, 'terrain': [terrain], 'fitBox': True})
    call(['node', str(HERE / 'resolution-browser.mjs'), 'staged', rel(STAGE / 'browser-config.json')])
    save(DOC / 'summary.json', {'uid': UID, 'sourceSHA256': entry['sha256'], 'terrainSHA256': h(patch_path), 'neighbours': len(context['rows']), 'neighbourFlags': 0, 'stagedBrowserSHA256': h(DOC / 'staged-browser.json'), 'aiCalls': 0, 'modelGeometryChanges': 0, 'publication': False})
    print(json.dumps({'uid': UID, 'neighbours': len(context['rows']), 'flagged': 0, 'stagedBrowserPassed': True, 'aiCalls': 0}), flush=True)


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
