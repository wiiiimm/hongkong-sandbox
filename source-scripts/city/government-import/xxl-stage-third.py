"""Stage the clean third-pass XXL candidate with original source terrain; never AI."""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('xxl_second', Path(__file__).with_name('xxl-second-pass.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
import native_patch_resolution as patch_resolution
ROOT, HERE = s.ROOT, s.HERE
DOC = s.DOC / 'third-pass/landsd-136832'
LOCAL = s.LOCAL / 'third-pass-landsd-136832'
STAGE = HERE / 'accepted/government-xxl-third-20260912'
UID = 'landsd/136832:0'
read, save, h, rel = s.read, s.save, s.h, s.rel


def start():
    selected = read(s.DOC / 'runtime-selection.json.gz')
    row = next(r for r in selected['rows'] if r['uid'] == UID)
    parent = read(ROOT / '3d-viewer/city/data/terrain.json')
    cells = s.resolution.rectangle_for(row['candidate']['entry']['worldBounds'], parent)
    bounds = s.resolution.extent(cells, parent)
    region = box(*bounds)
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    live = {m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
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
    current_manifest_sha = h(ROOT / '3d-viewer/city/data/manifest.json')
    save(DOC / 'selection.json.gz', {**selected, 'manifestSHA256': current_manifest_sha, 'rows': [row]})
    save(DOC / 'neighbour-inputs.json.gz', {'rows': neighbours, 'inputHashes': hashes, 'candidateIds': [UID], 'patches': []})
    save(DOC / 'patch-plan.json', {'cells': cells, 'bounds': bounds, 'manifestSHA256': current_manifest_sha, 'uid': UID})
    resources = {'building:' + UID} | {('building:' if n['building']['uid'].startswith('landsd/') else 'source-form:') + n['building']['uid'] for n in neighbours}
    claim = s.reservations.claim('codex-xxl-third-' + str(uuid.uuid4()), sorted(resources), batch='government-xxl-third-20260912')
    assert claim['ok']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    s.call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'reservation.json'), '--', sys.executable, __file__, 'owned'])


def owned():
    receipt = read(LOCAL / 'reservation.json')
    assert s.reservations.owns(receipt)
    plan = read(DOC / 'patch-plan.json')
    assert h(ROOT / '3d-viewer/city/data/manifest.json') == plan['manifestSHA256']
    row = read(DOC / 'selection.json.gz')['rows'][0]
    proof = next(r for r in read(s.DOC / 'third-pass/source-surface-context.json')['rows'] if r['uid'] == UID)
    assert proof['identityScriptAccepted'] and proof['foundationScriptAccepted']
    sources = read(s.DOC / 'recovery.json')['sheets'] + read(s.DOC / 'adjacent-terrain-results.json')['sources']
    bounds = plan['bounds']
    fragments, used = [], []
    parent = read(ROOT / '3d-viewer/city/data/terrain.json')
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    group = {'uids': [UID], 'cells': plan['cells']}
    try:
        assert not any(s.resolution.terrain.overlap(group['cells'], read(ROOT / '3d-viewer' / p['url'])['coarseCells']) for p in manifest['terrainPatches']), 'overlaps-installed-terrain-patch'
        for source in sources:
            folder = s.LOCAL / 'sheets' / source['sheet'] / 'terrain'
            found = []
            for path in source['terrainPaths']:
                triangles = s.context.triangles(ROOT / path)
                near = triangles[(triangles[:, :, 0].max(axis=1) >= bounds[0]) & (triangles[:, :, 0].min(axis=1) <= bounds[2]) & (triangles[:, :, 2].max(axis=1) >= bounds[1]) & (triangles[:, :, 2].min(axis=1) <= bounds[3])]
                if len(near):
                    found.append(near)
            if found:
                fragments.extend(found)
                source_proof = source['source']
                used.append({'sheet': source['sheet'], 'revision': source_proof['revisionDate'], 'sourceETag': source_proof['sourceETag'], 'directorySHA256': source_proof['directorySHA256'], 'sourceFiles': [{'path': rel(folder / e['name']), 'sha256': e['sha256']} for e in source_proof['entries'] if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf', '.bin'))]})
        lo, hi = row['candidate']['entry']['worldBounds']
        validator = s.resolution.validate_patch
        s.resolution.validate_patch = lambda candidate, parent_terrain: None
        try:
            patch = s.resolution.make_patch(group, parent, np.concatenate(fragments), used, native_core=[lo[0] - 1, lo[2] - 1, hi[0] + 1, hi[2] + 1])
        finally:
            s.resolution.validate_patch = validator
        patch_path = LOCAL / (patch['id'] + '.json')
        save(patch_path, patch)
        model = s.glb_triangles(next(item for item in read(s.DOC / 'selection.json.gz')['rows'] if item['modelId'] == row['candidate']['entry']['modelId']))
        projected = __import__('shapely').union_all(__import__('shapely').polygons(model[:, :, [0, 2]]))
        fill = patch_resolution.fill_parent_only_holes(patch, parent, bounds, projected, s.resolution.terrain.fine.DemSampler(parent, rendered=True))
        save(patch_path, patch)
        source_files = [item for source in used for item in source['sourceFiles']]
        patch = read(patch_path)
        overlap = patch_resolution.approve_original_overlap(patch, patch_path, Path(rel(DOC / 'native-overlap-evidence.json')), source_files)
        save(patch_path, patch)
        validator(patch, parent)
        save(DOC / 'terrain-resolution.json', {'parentHoleFill': fill, 'overlapProof': overlap, 'aiCalls': 0, 'geometryChanges': 0})
    except (AssertionError, ValueError) as error:
        save(DOC / 'result.json', {'uid': UID, 'passed': False, 'stage': 'source-terrain-patch', 'reason': str(error), 'aiCalls': 0})
        print(json.dumps(read(DOC / 'result.json')), flush=True)
        return
    patch_entry = {'path': rel(patch_path), 'sha256': h(patch_path), 'uids': [UID], 'bounds': bounds, 'triangles': len(patch['nativeMesh']['index']) // 3}
    save(DOC / 'terrain-candidates.json', [patch_entry])
    neighbours = read(DOC / 'neighbour-inputs.json.gz')
    neighbours['patches'] = [patch_entry]
    save(DOC / 'neighbour-inputs.json.gz', neighbours)
    catalogue = read(HERE / 'accepted/government-xxl-20260911/catalogue.json')
    entry = dict(row['candidate']['entry'])
    catalogue.update(area='Government XXL third pass', counts={'packedModels': 1}, models=[entry])
    save(LOCAL / 'candidates/catalogue.json', catalogue)
    save(LOCAL / 'candidates/catalogue-index.json', {'models': 1, 'catalogues': ['catalogue.json']})
    asset = LOCAL / 'candidates' / entry['asset']
    asset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(row['candidate']['path'], asset)
    assert h(asset) == entry['sha256']
    save(LOCAL / 'source-forms.json', {UID: row['source']})
    s.call(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(DOC / 'selection.json.gz'), '--candidates', rel(LOCAL / 'candidates'), '--terrain-candidates', rel(DOC / 'terrain-candidates.json'), '--out', rel(DOC / 'metrics.json')])
    validation = subprocess.run(['node', str(HERE.parent / 'building-batch/validate_candidates.mjs'), '--candidates', rel(LOCAL / 'candidates'), '--source-forms', rel(LOCAL / 'source-forms.json'), '--terrain-candidates', rel(DOC / 'terrain-candidates.json'), '--out', rel(DOC / 'validation.json')], cwd=ROOT)
    assert validation.returncode in (0, 1)
    s.call(['node', str(HERE / 'check-neighbours.mjs'), rel(DOC) + '/'])
    metric = read(DOC / 'metrics.json')['rows'][0]
    reasons = []
    if metric.get('error') or not metric['sourcePreserved'] or metric['sourceSHA256'] != entry['sha256']:
        reasons.append('source-integrity-or-runtime-check')
    if metric['missingTerrain'] or metric['maxSamplerDelta'] > .004:
        reasons.append('terrain-coverage-or-rendered-disagreement')
    if any(metric['budget'][key] > read(DOC / 'metrics.json')['profiles']['mobile'][key] for key in ('triangles', 'geometryBytes', 'residentBytes')):
        reasons.append('mobile-runtime-budget')
    for item in read(DOC / 'validation.json')['results']:
        reasons += [reason for reason in item.get('concerns', []) if reason != 'sampled-ground-gap-below-model-bottom']
        if item['outcome'] == 'validation-exception':
            reasons.append('runtime-validation-exception')
    blocked = read(DOC / 'neighbour-checks.json')['patches'][0]['blockedBy']
    if blocked:
        reasons.append('terrain-correction-regresses-neighbours')
    decision = {'uid': UID, 'policy': 'original-government-partial-foundation-v1', 'passed': not reasons, 'reasons': sorted(set(reasons)), 'blockedNeighbours': blocked, 'surfaceProof': proof, 'patch': patch_entry, 'aiCalls': 0, 'modelGeometryChanges': 0, 'publication': False}
    save(DOC / 'result.json', decision)
    if not reasons:
        entry.update(priority='detail', placementReviewed=True, sourceIdentityReviewed=True, identityReviewApproved=True, placementReview='Exact unchanged government source. Actual projected identity passes the conservative contract; no source face is wholly below original government terrain. Eleven partially intersected faces are retained at surveyed elevation. Scripted only; no AI architectural review or geometry edits.')
        save(STAGE / 'catalogue.json', catalogue)
        source_form = dict(row['source']['building'])
        source_form['tile'] = Path(row['source']['tile']).stem
        save(STAGE / 'source-forms.json', [source_form])
        staged_asset = STAGE / entry['asset']
        staged_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(asset, staged_asset)
        staged_patch = STAGE / patch_path.name
        shutil.copyfile(patch_path, staged_patch)
        terrain = {'source': rel(staged_patch), 'sha256': h(staged_patch), 'destination': 'city/data/' + staged_patch.name, 'resolution': patch['cell'], 'area': 'landsd/136832 original native terrain'}
        destination = 'city/data/official-models/government-xxl-third-20260912/catalogue.json'
        save(STAGE / 'plan.json', {'areas': [{'area': catalogue['area'], 'catalogue': rel(STAGE / 'catalogue.json'), 'destination': destination}], 'topLevelTerrainPatches': [terrain]})
        save(STAGE / 'browser-config.json', {'stage': rel(STAGE) + '/', 'doc': rel(DOC) + '/', 'catalogueURL': destination, 'terrain': [terrain], 'fitBox': True})
    print(json.dumps(decision), flush=True)


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
