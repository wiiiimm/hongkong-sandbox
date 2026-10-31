"""Checkpoint the four prioritized XXL engineering routes in Neon."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / 'shared-modelling'))
from db import connect
import jobs

BATCH = 'government-xxl-four-20260912'
STAGE = 'government-xxl-four-engineering-v1'


def sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = ROOT / 'docs/astra-city/government-import/government-xxl-20260911/second-pass'
    paths = [base / 'third-pass/special-terrain-context.json', base / 'third-pass/landsd-136832/result.json', base / 'third-pass/landsd-136832/native-overlap-evidence.json', base / 'third-pass/landsd-136832/neighbour-checks.json', base / 'terrain/result.json', base / 'terrain/terrain-resolution.json', base / 'terrain/neighbour-checks.json', base / 'elements/neighbour-support-triangles.json']
    evidence = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    rows = [
        {'uid': 'landsd/226033:0', 'name': 'Telford Plaza I', 'state': 'held-for-local-scripted-engineering', 'resolved': ['All but 69 of 1,090,338 native checks are covered.'], 'remaining': ['Fill a 3.9–15.0 mm original terrain-sheet seam and validate the full complex against neighbours.']},
        {'uid': 'landsd/273061:0', 'name': 'Elements', 'state': 'held-for-source-assembly', 'resolved': ['Source identity and below-grade surface checks pass.'], 'remaining': ['Resolve a development-wide assembly: 20 flagged forms share parent way/1047822829 and one separate form remains; Harbourside already uses native detail.']},
        {'uid': 'landsd/109467:0', 'name': 'Lei Yue Mun Park Block 10', 'state': 'held-for-source-assembly', 'resolved': ['Full native coverage, runtime validation and independent highest-source-surface overlap proof pass.'], 'remaining': ['Resolve seven neighbour regressions, including two additional Block 10 source parts.']},
        {'uid': 'landsd/136832:0', 'name': 'Hong Kong Ocean Park Marriott Hotel podium', 'state': 'held-for-source-assembly', 'resolved': ['Native coverage hole is safely filled outside the model projection; overlap and runtime validation pass.'], 'remaining': ['Import and validate the three exact government tower sources with the podium as one four-part assembly.']},
    ]
    report = {'batch': BATCH, 'stage': STAGE, 'models': 4, 'installed': 0, 'inProcess': 0, 'heldTechnical': 4, 'requiresAI': 0, 'requiresUserDecision': 0, 'rows': rows, 'evidenceHashes': evidence, 'aiCalls': 0, 'geometryChanges': 0, 'publication': False}
    job_id = jobs.enqueue(BATCH, STAGE, {'evidenceHashes': evidence})
    job = jobs.claim(BATCH, 'codex-xxl-four-checkpoint', [STAGE], lease_seconds=600)
    assert job and job['id'] == job_id and jobs.finish(job, result=report)
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        assert connection.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (job_id,)).fetchone()[0] == report
    out = base / 'third-pass/four-priority-checkpoint.json'
    out.write_text(json.dumps({**report, 'jobId': job_id}, sort_keys=True, separators=(',', ':')) + '\n')
    print(json.dumps({'jobId': job_id, 'rows': len(rows), 'aiCalls': 0}))


if __name__ == '__main__':
    main()
