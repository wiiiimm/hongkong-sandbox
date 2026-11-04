"""Write the 15-source XXL third-pass routing checkpoint to Neon; never AI."""
import importlib.util
import json
import sys
import uuid
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
spec = importlib.util.spec_from_file_location('xxl_second', Path(__file__).with_name('xxl-second-pass.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT, HERE, DOC, LOCAL = s.ROOT, s.HERE, s.DOC, s.LOCAL
BATCH = 'government-xxl-third-20260912'
STAGE = 'government-xxl-technical-routing-v1'
OUT = DOC / 'third-pass'
read, save, h, rel = s.read, s.save, s.h, s.rel


def start():
    previous = read(DOC / 'final-results.json.gz')
    rows = [r for r in previous['rows'] if r['humanStatus'] == 'held-unknown']
    assert len(rows) == 15
    diagnostics = {r['modelId']: r for r in read(DOC / 'diagnostics.json')['rows']}
    resources = set()
    for row in rows:
        uid = row['uid']
        if not uid:
            candidates = diagnostics[row['modelId']]['projectionCandidates']
            assert len(candidates) == 1
            uid = candidates[0]['uid']
        resources.add('building:' + uid)
    claim = s.reservations.claim('codex-xxl-third-final-' + str(uuid.uuid4()), sorted(resources), batch=BATCH)
    assert claim['ok']
    save(LOCAL / 'third-pass-final-reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    s.call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LOCAL / 'third-pass-final-reservation.json'), '--', sys.executable, __file__, 'owned'])


def owned():
    receipt = read(LOCAL / 'third-pass-final-reservation.json')
    assert s.reservations.owns(receipt)
    previous = read(DOC / 'final-results.json.gz')
    diagnostics = {r['modelId']: r for r in read(DOC / 'diagnostics.json')['rows']}
    surface = {r['modelId']: r for r in read(OUT / 'source-surface-context.json')['rows']}
    special = read(OUT / 'special-terrain-context.json')
    patches = {r['uid']: r for r in special['terrainPatches']}
    rows = []
    for old in previous['rows']:
        if old['humanStatus'] != 'held-unknown':
            continue
        row = {k: old.get(k) for k in ('modelId', 'uid', 'name', 'sourceSHA256')}
        row.update(humanStatus='held-unknown', actionableState='held-for-local-scripted-engineering', requiresAI=False, requiresUserDecision=False, needsMoreCompute=True, aiCalls=0, geometryChanges=0, publication=False)
        if row['uid'] == 'landsd/226033:0':
            row.update(reasons=['native-terrain-source-sheet-boundary-seam', 'source-component-identity-outside-conservative-script-contract'], technicalEvidence=special['telford'], nextStep='Resolve the 3.9–15.0 mm source-sheet boundary seam with a source-preserving tolerance rule, then run terrain, neighbour, runtime and browser gates.')
        elif row['uid'] == 'landsd/273061:0':
            row.update(reasons=['current-elements-neighbour-support-unresolved'], surfaceContext=surface[row['modelId']], supportDiagnostics=read(DOC / 'elements/neighbour-support-triangles.json'), nextStep='Resolve 21 incomplete neighbour/support forms and the existing-native Harbourside check before publication.')
        elif row['uid'] == 'landsd/109467:0':
            row.update(reasons=['native-terrain-overlapping-height-surfaces'], technicalEvidence=patches[row['uid']], nextStep='Produce and validate a highest-original-surface overlap proof for 367.492 m² of overlapping source TIN, then run neighbour and runtime checks.')
        else:
            evidence = surface[row['modelId']]
            reasons = list(evidence['reasons'])
            if row['uid'] == 'landsd/136832:0':
                reasons = ['native-terrain-patch-incomplete-source-coverage']
                row['technicalEvidence'] = patches[row['uid']]
                row['stageAttempt'] = read(OUT / 'landsd-136832/result.json')
                row['nextStep'] = 'Recover or bound the 3,360.123 m² missing original TIN area before repeating neighbour, runtime and browser gates.'
            else:
                row['nextStep'] = 'Keep the current fallback while a deterministic component/identity or below-grade surface rule is developed and validated.'
            row.update(reasons=reasons, surfaceContext=evidence)
        rows.append(row)
    assert len(rows) == 15 and all(r['humanStatus'] == 'held-unknown' for r in rows)
    evidence_paths = [OUT / 'source-surface-context.json', OUT / 'special-terrain-context.json', OUT / 'landsd-136832/result.json', HERE / 'xxl-third-pass.py', HERE / 'xxl-third-special.py', HERE / 'xxl-stage-third.py']
    evidence_hashes = {rel(path): h(path) for path in evidence_paths}
    counts = dict(Counter(reason for row in rows for reason in row['reasons']))
    report = {'batch': BATCH, 'stage': STAGE, 'models': 15, 'humanCounts': {'installed': 0, 'to-do': 0, 'held-human': 0, 'held-ai': 0, 'held-unknown': 15, 'in-process': 0}, 'technicalReasonCounts': counts, 'rows': rows, 'evidenceHashes': evidence_hashes, 'aiCalls': 0, 'geometryChanges': 0, 'publication': False, 'qualification': 'All 15 prior technical holds received another deterministic pass. No additional model passed all publication gates. Every item is stopped with a precise local engineering dependency; none requires a user decision or demonstrated AI modelling.'}
    payload = {'models': 15, 'previousJobId': previous['jobId'], 'evidenceHashes': evidence_hashes}
    job_id = s.jobs.enqueue(BATCH, STAGE, payload)
    job = s.jobs.claim(BATCH, receipt['owner'], [STAGE], lease_seconds=600)
    assert job and job['id'] == job_id
    report['jobId'] = job_id
    save(OUT / 'final-results.json.gz', report)
    report['evidence'] = {'path': rel(OUT / 'final-results.json.gz'), 'sha256': h(OUT / 'final-results.json.gz')}
    assert s.jobs.finish(job, result=report)
    with s.connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        stored = connection.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s AND status=\'complete\'', (job_id,)).fetchone()[0]
    assert stored == report
    save(OUT / 'neon-sync.json', {'jobId': job_id, 'rows': 15, 'exactResultMatch': True, 'sourceReservationFenced': True, 'humanCounts': report['humanCounts']})
    save(OUT / 'summary.json', {k: v for k, v in report.items() if k != 'rows'})
    print(json.dumps({'jobId': job_id, 'humanCounts': report['humanCounts'], 'technicalReasonCounts': counts, 'aiCalls': 0}), flush=True)


if __name__ == '__main__':
    owned() if len(sys.argv) > 1 else start()
