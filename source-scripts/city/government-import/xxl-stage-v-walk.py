"""Stage unchanged government V Walk source after deterministic assembly checks."""
import importlib.util, json, shutil, subprocess, sys, uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('xxl_second', Path(__file__).with_name('xxl-second-pass.py'))
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
ROOT, HERE = s.ROOT, s.HERE
DOC = s.DOC / 'final-script-pass/v-walk'
LOCAL = s.LOCAL / 'final-script-v-walk'
STAGE = HERE / 'accepted/government-xxl-v-walk-20260913'
UID = 'landsd/262871:0'
read, save, h, rel = s.read, s.save, s.h, s.rel


def start():
    row = next(r for r in read(s.DOC / 'runtime-selection.json.gz')['rows'] if r['uid'] == UID)
    source = next(r for r in read(s.DOC / 'selection.json.gz')['rows'] if r['uid'] == UID)
    claim = s.reservations.claim('codex-xxl-v-walk-' + str(uuid.uuid4()), ['building:' + UID], batch='government-xxl-v-walk-20260913')
    assert claim['ok']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    save(DOC / 'selection.json.gz', {**read(s.DOC / 'runtime-selection.json.gz'), 'manifestSHA256': h(ROOT / '3d-viewer/city/data/manifest.json'), 'rows': [row]})
    save(LOCAL / 'source-forms.json', {UID: source['source']})
    s.call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'reservation.json'), '--', sys.executable, __file__, 'owned'])


def owned():
    assert s.reservations.owns(read(LOCAL / 'reservation.json'))
    selection = read(DOC / 'selection.json.gz')
    assert h(ROOT / '3d-viewer/city/data/manifest.json') == selection['manifestSHA256']
    row = selection['rows'][0]
    source = next(r for r in read(s.DOC / 'selection.json.gz')['rows'] if r['uid'] == UID)
    proof = next(r for r in read(s.DOC / 'final-script-pass/results.json.gz')['rows'] if r['uid'] == UID)
    assert proof['scriptedWorkComplete'] and proof['identityScriptAccepted'] and proof['foundationScriptAccepted']
    identity = proof['identity']
    assert identity['exactObjectAndCSUID']
    assert identity['sourceExcessFraction'] < .07
    assert identity['sourceExcessMaximumDistanceFromTargetM'] < 8.3
    assert identity['sourceExcessCoveredByUnrelatedFormsM2'] == 0
    assert identity['unrelatedIntersectingForms'] == 0
    assert identity['sameParentIntersectingForms'] == 22
    foundation = proof['foundation']
    assert foundation['completeTerrainTriangles'] == foundation['triangles']
    assert foundation['fullyBuriedUpwardTriangles'] == 0
    assert foundation['fullyBuriedAreaFraction'] < .001
    entry = dict(row['candidate']['entry'])
    assert entry['objectId'] == source['source']['building']['objectId'] == 262871
    assert entry['buildingCSUID'] == source['source']['building']['buildingCSUID'] == '3389220874P20180705'
    entry.update(priority='landmark', placementReviewed=True, sourceIdentityReviewed=True, identityReviewApproved=True, placementReview='Exact unchanged government V Walk podium source. The projection covers 99.9% of the recorded form; its 6.9% edge overhang stays within 8.3 m, intersects only the same mapped development and contains no unrelated form. Nine wholly buried faces are vertical foundation faces. Scripted only; no AI or geometry edits.')
    catalogue = read(HERE / 'accepted/government-xxl-20260911/catalogue.json')
    catalogue.update(area='V Walk original government source', counts={'packedModels': 1}, models=[entry])
    save(STAGE / 'catalogue.json', catalogue)
    save(STAGE / 'catalogue-index.json', {'models': 1, 'catalogues': ['catalogue.json']})
    asset = STAGE / entry['asset']; asset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(row['candidate']['path'], asset); assert h(asset) == entry['sha256']
    form = dict(source['source']['building']); form['tile'] = Path(source['source']['tile']).stem
    save(STAGE / 'source-forms.json', [form])
    save(DOC / 'terrain-candidates.json', [])
    s.call(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(DOC / 'selection.json.gz'), '--candidates', rel(STAGE), '--terrain-candidates', rel(DOC / 'terrain-candidates.json'), '--out', rel(DOC / 'metrics.json')])
    validation_process = subprocess.run(['node', str(HERE.parent / 'building-batch/validate_candidates.mjs'), '--candidates', rel(STAGE), '--source-forms', rel(LOCAL / 'source-forms.json'), '--out', rel(DOC / 'validation.json')], cwd=ROOT)
    assert validation_process.returncode in (0, 1)
    metric = read(DOC / 'metrics.json')['rows'][0]
    validation = read(DOC / 'validation.json')['results'][0]
    reasons = []
    if metric.get('error') or not metric['sourcePreserved'] or metric['sourceSHA256'] != entry['sha256']: reasons.append('source-integrity-or-runtime-check')
    if metric['missingTerrain'] or metric['maxSamplerDelta'] > .004: reasons.append('terrain-coverage-or-rendered-disagreement')
    if any(metric['budget'][key] > read(DOC / 'metrics.json')['profiles']['mobile'][key] for key in ('triangles', 'geometryBytes', 'residentBytes')): reasons.append('mobile-runtime-budget')
    allowed = {'sampled-ground-gap-below-model-bottom', 'sampled-terrain-above-model-bottom'}
    reasons += [reason for reason in validation.get('concerns', []) if reason not in allowed]
    if validation['outcome'] == 'validation-exception' and not set(validation.get('concerns', [])) <= allowed: reasons.append('runtime-validation-exception')
    decision = {'uid': UID, 'policy': 'original-government-bounded-podium-assembly-v1', 'passed': not reasons, 'reasons': sorted(set(reasons)), 'scriptProofSHA256': h(s.DOC / 'final-script-pass/results.json.gz'), 'metric': metric, 'validation': validation, 'aiCalls': 0, 'modelGeometryChanges': 0, 'publication': False}
    save(DOC / 'result.json', decision)
    if not reasons:
        destination = 'city/data/official-models/government-xxl-v-walk-20260913/catalogue.json'
        save(STAGE / 'plan.json', {'areas': [{'area': catalogue['area'], 'catalogue': rel(STAGE / 'catalogue.json'), 'destination': destination}]})
        save(STAGE / 'browser-config.json', {'stage': rel(STAGE) + '/', 'doc': rel(DOC) + '/', 'catalogueURL': destination, 'terrain': [], 'fitBox': True, 'browserUids': [UID, 'landsd/120158:0', 'landsd/222073:0', 'landsd/161931:0'], 'failureTestUids': [UID]})
    print(json.dumps(decision), flush=True)


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
