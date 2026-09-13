"""Stage V City as one unchanged government source assembly; never AI."""
import gzip
import importlib.util
import json
import shutil
import struct
import subprocess
import sys
import uuid
from pathlib import Path

from shapely.geometry import Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('second', Path(__file__).with_name('xl-second-pass.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

ROOT, HERE = s.ROOT, s.HERE
read, save, h, rel = s.read, s.save, s.h, s.rel
DOC = s.DOC / 'third-pass/terrain-v-city'
LOCAL = s.LOCAL / 'third-pass-v-city-assembly'
RECOVERY = s.LOCAL / 'third-pass-v-city-supports/support-runtime.json.gz'
STAGE = HERE / 'accepted/government-xl-v-city-assembly-20260914'
BATCH = 'government-xl-v-city-assembly-20260914'
PODIUM = 'landsd/230643:0'
STATION = 'landsd/243886:0'
REPRESENTATIVE = [PODIUM, STATION, 'landsd/248373:0', 'landsd/308947:0']
MOBILE = {'count': 24, 'geometryBytes': 48 * 1024 * 1024, 'residentBytes': 128 * 1024 * 1024, 'triangles': 450000}


def call(args, allowed=(0,)):
    result = subprocess.run(args, cwd=ROOT)
    assert result.returncode in allowed, (args, result.returncode)


def assembly_rows():
    frozen = read(s.DOC / 'runtime-selection.json.gz')
    primary = next(row for row in frozen['rows'] if row['uid'] == PODIUM)
    supports = read(RECOVERY)
    assert supports['aiCalls'] == supports['modelGeometryChanges'] == 0
    rows = [primary, *supports['rows']]
    assert len(rows) == len({row['uid'] for row in rows}) == 11
    assert {row['candidate']['entry']['sourceTile'] for row in rows} == {'6-SW-6A'}
    return frozen, rows


def current_neighbours(bounds, candidate_ids):
    region = box(*bounds)
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    live = {model['uid'] for url in manifest['officialModelCatalogues'] for model in read(ROOT / '3d-viewer' / url)['models']}
    assert not candidate_ids & live
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
    return neighbours, hashes


def start():
    frozen, rows = assembly_rows()
    ids = {row['uid'] for row in rows}
    old_patch = read(DOC / 'terrain-candidates.json')[0]
    assert h(ROOT / old_patch['path']) == old_patch['sha256']
    neighbours, hashes = current_neighbours(old_patch['bounds'], ids)
    manifest_sha = h(ROOT / '3d-viewer/city/data/manifest.json')
    save(DOC / 'assembly-selection.json.gz', {**frozen, 'manifestSHA256': manifest_sha, 'rows': rows})
    save(DOC / 'assembly-neighbour-inputs.json.gz', {'rows': neighbours, 'inputHashes': hashes, 'candidateIds': sorted(ids), 'patches': [], 'manifestSHA256': manifest_sha})
    resources = {'building:' + uid for uid in ids} | {('building:' if row['building']['uid'].startswith('landsd/') else 'source-form:') + row['building']['uid'] for row in neighbours}
    claim = s.reservations.claim('codex-xl-v-city-' + str(uuid.uuid4()), sorted(resources), batch=BATCH)
    assert claim['ok'], claim
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    s.call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'reservation.json'), '--', sys.executable, __file__, 'owned'])


def budget(entries):
    result = {'count': len(entries), 'geometryBytes': 0, 'residentBytes': 0, 'triangles': 0}
    for entry in entries:
        collision = entry['indexedVertices'] * 24 + entry['triangles'] * (12 + 48 + 64)
        result['geometryBytes'] += entry['decodedGeometryBytes']
        result['residentBytes'] += entry['decodedGeometryBytes'] * 2 + collision + 65536
        result['triangles'] += entry['triangles']
    result['mobilePassed'] = all(result[key] <= MOBILE[key] for key in MOBILE)
    return result


def detailed_primary_identity():
    final_path = s.DOC / 'final-script-pass/results.json.gz'
    diagnostic_path = s.DOC / 'diagnostics.json'
    final = next(row for row in read(final_path)['rows'] if row['uid'] == PODIUM)
    diagnostic = next(row for row in read(diagnostic_path)['rows'] if row['uid'] == PODIUM)
    projection = next(row for row in diagnostic['projectionCandidates'] if row['uid'] == PODIUM)['metrics']
    identity = final['identity']
    passed = final['identityScriptAccepted'] and identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection'] > .999 and identity['sourceProjectionInsideTarget'] > .99 and identity['sourceExcessFraction'] < .01 and identity['sourceExcessMaximumDistanceFromTargetM'] < 3.5 and identity['unrelatedIntersectingForms'] == 0 and projection['centroidDistance'] < .2
    return {'passed': bool(passed), 'identity': identity, 'projectionMetrics': projection, 'inputHashes': {rel(final_path): h(final_path), rel(diagnostic_path): h(diagnostic_path)}}


def station_source_foundation(row):
    spec = importlib.util.spec_from_file_location('final_pass', HERE / 'xl-final-script-pass.py')
    final_pass = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(final_pass)
    raw = gzip.decompress(Path(row['candidate']['path']).read_bytes())
    json_size, json_kind = struct.unpack_from('<II', raw, 12)
    assert json_kind == 0x4E4F534A
    data = json.loads(raw[20:20 + json_size])
    at = 20 + json_size
    binary_size, binary_kind = struct.unpack_from('<II', raw, at)
    assert binary_kind == 0x004E4942 and at + 8 + binary_size == len(raw)
    unpacked = LOCAL / 'station-unpacked'
    unpacked.mkdir(parents=True, exist_ok=True)
    (unpacked / 'buffer.bin').write_bytes(raw[at + 8:])
    data['buffers'][0]['uri'] = 'buffer.bin'
    save(unpacked / 'model.gltf', data)
    triangles = s.context.triangles(unpacked / 'model.gltf')
    entry, building = row['candidate']['entry'], row['source']['building']
    assert len(triangles) == entry['triangles']
    result = final_pass.foundation_context(triangles, final_pass.native_terrain(), Polygon(building['rings'][0], building['rings'][1:]))
    source = next(item for item in read(s.DOC / 'recovery.json')['sheets'] if item['sheet'] == entry['sourceTile'])
    result.update(uid=STATION, sourceSHA256=entry['sha256'], sourceDirectorySHA256=source['source']['directorySHA256'], sourceTerrainHashes={path: h(ROOT / path) for path in source['terrainPaths']}, policy='Every unchanged source triangle and its centre checked against original terrain from the same pinned government sheet. The published 2.5D terrain selects an upper transport surface, so this same-archive proof distinguishes intentional multi-level station geometry from a placement error.', passed=result['completeTerrainTriangles'] == result['triangles'] and result['fullyBuriedTriangles'] == 0 and result['minimumGapM'] > -.01, aiCalls=0, modelGeometryChanges=0)
    save(DOC / 'station-source-terrain.json', result)
    return result


def owned():
    assert s.reservations.owns(read(LOCAL / 'reservation.json'))
    selection = read(DOC / 'assembly-selection.json.gz')
    neighbour_inputs = read(DOC / 'assembly-neighbour-inputs.json.gz')
    assert h(ROOT / '3d-viewer/city/data/manifest.json') == selection['manifestSHA256'] == neighbour_inputs['manifestSHA256']
    rows = selection['rows']
    ids = {row['uid'] for row in rows}

    old_patch_entry = read(DOC / 'terrain-candidates.json')[0]
    old_patch_path = ROOT / old_patch_entry['path']
    assert h(old_patch_path) == old_patch_entry['sha256']
    patch = read(old_patch_path)
    assert patch['meta']['source']['nativeSources'][0]['directorySHA256'] == 'f99a5f97551f696b4f05470e1dd803b7d1e1a6ff10a23217c7b2ec497bb2b3bc'
    patch['id'] = 'government-native-v-city-assembly'
    patch['meta']['targetUids'] = sorted(ids)
    patch_path = LOCAL / (patch['id'] + '.json')
    save(patch_path, patch)
    patch_entry = {'path': rel(patch_path), 'sha256': h(patch_path), 'uids': sorted(ids), 'bounds': old_patch_entry['bounds'], 'triangles': len(patch['nativeMesh']['index']) // 3}
    save(DOC / 'assembly-terrain-candidates.json', [patch_entry])
    neighbour_inputs['patches'] = [patch_entry]
    save(DOC / 'neighbour-inputs.json.gz', neighbour_inputs)

    template = read(HERE / 'accepted/government-xxl-20260911/catalogue.json')
    entries, forms, browser_forms = [], {}, []
    identity_rows = []
    for row in rows:
        entry = dict(row['candidate']['entry'])
        building = row['source']['building']
        exact_ids = entry['objectId'] == building['objectId'] and entry['buildingCSUID'] == building['buildingCSUID']
        embedded_id = entry['modelId'][1:11] == entry['buildingCSUID'][:10]
        coarse_passed = entry['overlapOfSmallerFootprint'] >= .99 and entry['footprintCentroidDistanceMetres'] <= 7
        identity_rows.append({'uid': row['uid'], 'modelId': entry['modelId'], 'exactObjectId': entry['objectId'] == building['objectId'], 'exactBuildingCSUID': entry['buildingCSUID'] == building['buildingCSUID'], 'modelIdEmbedsCSUID': embedded_id, 'overlapOfSmallerFootprint': entry['overlapOfSmallerFootprint'], 'centroidDistanceMetres': entry['footprintCentroidDistanceMetres'], 'passed': bool(exact_ids and embedded_id and (coarse_passed or row['uid'] == PODIUM))})
        entry.update(label=building.get('name') or entry['modelId'], priority='landmark', placementReviewed=True, sourceIdentityReviewed=True, identityReviewApproved=True, placementReview='Exact UID/CSUID-matched unchanged government source in the V City/Century Gateway/Tuen Mun Station assembly. Native terrain and podium dependencies are validated as one atomic source-sheet group; no AI modelling, review, simplification or geometry edits.')
        if row['uid'] not in (PODIUM, STATION):
            entry['supportDependencies'] = [{'uid': PODIUM, 'state': 'candidate', 'csuid': next(item['candidate']['entry']['buildingCSUID'] for item in rows if item['uid'] == PODIUM)}]
        source_asset = Path(row['candidate']['path'])
        assert h(source_asset) == entry['sha256']
        target = STAGE / entry['asset']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_asset, target)
        entries.append(entry)
        forms[row['uid']] = row['source']
        form = dict(building)
        form['tile'] = Path(row['source']['tile']).stem
        browser_forms.append(form)
    primary_identity = detailed_primary_identity()
    assert primary_identity['passed']
    assert all(row['passed'] for row in identity_rows)
    save(DOC / 'assembly-identity.json', {'rows': identity_rows, 'primaryDetailedProof': primary_identity, 'sourceSheet': '6-SW-6A', 'samePinnedDirectory': True, 'aiCalls': 0, 'modelGeometryChanges': 0})
    station_foundation = station_source_foundation(next(row for row in rows if row['uid'] == STATION))
    assert station_foundation['passed']

    group_budget = budget(entries)
    assert group_budget['mobilePassed'], group_budget
    save(DOC / 'assembly-budget.json', {'measured': group_budget, 'mobileLimits': MOBILE, 'policy': 'Production modelBudget formula applied to the complete dependency closure.', 'aiCalls': 0})
    template.update(area='V City and Century Gateway original government source assembly', counts={'packedModels': len(entries)}, models=entries)
    save(STAGE / 'catalogue.json', template)
    save(STAGE / 'catalogue-index.json', {'models': len(entries), 'catalogues': ['catalogue.json']})
    save(STAGE / 'source-forms.json', browser_forms)
    save(LOCAL / 'source-forms.json', forms)
    call(['node', str(HERE / 'xl-v-city-support.mjs')])

    contact = read(DOC / 'native-support-contact.json')
    assert contact['supportUid'] == PODIUM and len(contact['rows']) == 9
    assert {row['uid'] for row in contact['rows']} == ids - {PODIUM, STATION}
    assert all(row['rimSamples'] > 0 and row['minDistance'] <= .5 for row in contact['rows'])

    save(DOC / 'terrain-candidates.json', [patch_entry])
    call(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(DOC / 'assembly-selection.json.gz'), '--candidates', rel(STAGE), '--terrain-candidates', rel(DOC / 'terrain-candidates.json'), '--out', rel(DOC / 'assembly-metrics.json')])
    validation = subprocess.run(['node', str(HERE.parent / 'building-batch/validate_candidates.mjs'), '--candidates', rel(STAGE), '--source-forms', rel(LOCAL / 'source-forms.json'), '--terrain-candidates', rel(DOC / 'terrain-candidates.json'), '--out', rel(DOC / 'assembly-validation.json')], cwd=ROOT)
    assert validation.returncode in (0, 1)
    call(['node', str(HERE / 'check-neighbours.mjs'), rel(DOC) + '/'])

    metrics = read(DOC / 'assembly-metrics.json')
    reasons = []
    for metric in metrics['rows']:
        if metric.get('error') or not metric.get('sourcePreserved') or metric.get('missingTerrain'):
            reasons.append(metric['uid'] + ':source-integrity-or-terrain-coverage')
        if metric.get('maxSamplerDelta', 0) > .004:
            reasons.append(metric['uid'] + ':rendered-terrain-disagreement')
        if metric.get('budget') and any(metric['budget'][key] > metrics['profiles']['mobile'][key] for key in ('triangles', 'geometryBytes', 'residentBytes')):
            reasons.append(metric['uid'] + ':mobile-runtime-budget')
    allowed_supported = {'sampled-ground-gap-below-model-bottom', 'sampled-terrain-above-model-bottom'}
    for result in read(DOC / 'assembly-validation.json')['results']:
        if result['outcome'] == 'validation-exception':
            reasons.append(result['uid'] + ':runtime-validation-exception')
        allowed = allowed_supported if result['uid'] != PODIUM else set()
        reasons.extend(result['uid'] + ':' + concern for concern in result.get('concerns', []) if concern not in allowed)
    blocked = read(DOC / 'neighbour-checks.json')['patches'][0]['blockedBy']
    if blocked:
        reasons.append('terrain-correction-regresses-unrelated-neighbours')
    result = {'uid': PODIUM, 'models': len(entries), 'policy': 'original-government-v-city-assembly-v1', 'passed': not reasons, 'reasons': sorted(set(reasons)), 'blockedNeighbours': blocked, 'patch': patch_entry, 'groupBudget': group_budget, 'identitySHA256': h(DOC / 'assembly-identity.json'), 'supportContactSHA256': h(DOC / 'native-support-contact.json'), 'stationSourceTerrainSHA256': h(DOC / 'station-source-terrain.json'), 'sourceRecoverySHA256': h(DOC / 'support-source-recovery.json'), 'aiCalls': 0, 'modelGeometryChanges': 0, 'publication': False}
    save(DOC / 'assembly-result.json', result)
    if not reasons:
        staged_patch = STAGE / patch_path.name
        shutil.copyfile(patch_path, staged_patch)
        terrain = {'source': rel(staged_patch), 'sha256': h(staged_patch), 'destination': 'city/data/' + staged_patch.name, 'resolution': patch['cell'], 'area': 'V City original native terrain'}
        destination = 'city/data/official-models/' + BATCH + '/catalogue.json'
        save(STAGE / 'plan.json', {'areas': [{'area': template['area'], 'catalogue': rel(STAGE / 'catalogue.json'), 'destination': destination}], 'topLevelTerrainPatches': [terrain]})
        save(STAGE / 'browser-config.json', {'stage': rel(STAGE) + '/', 'doc': rel(DOC) + '/', 'catalogueURL': destination, 'terrain': [terrain], 'fitBox': True, 'browserUids': REPRESENTATIVE, 'failureTestUids': [PODIUM]})
    print(json.dumps(result))


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
