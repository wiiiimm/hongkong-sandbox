"""Persist completed exact component checks and boundary-coverage measurements.

No acceptance, source mutation, model edit or installation credit. Verify all
prior Neon results and their evidence before reserving the explicit six sources.
"""
import importlib.util
import shutil
import uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-three-original-pair-checkpoint-20261008'
CLOSURE = 'government-xl-three-untried-podium-original-closures-20261008'
PHASES = [CLOSURE, 'government-xl-new-desh-assembly-identity-20261008',
    'government-xl-new-tvb-assembly-identity-20261008',
    'government-xl-new-tower1-assembly-identity-20261008',
    'government-xl-259803-independent-current-ground-20261008',
    'government-xl-259803-independent-original-ground-20261008']


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def polygon_parts(geometry):
    if geometry.geom_type == 'Polygon':
        return [geometry]
    return [p for part in getattr(geometry, 'geoms', []) for p in polygon_parts(part)]


def main():
    doc, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not doc.exists(), 'Completed checkpoints are immutable'
    phase_rows, refs = [], []
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for name in PHASES:
            folder = BASE / name
            result = read(folder / 'result.json')
            assert read(folder / 'neon-sync.json') == {'jobId': result['jobId'], 'resultVerified': True}
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                (result['jobId'],)).fetchone() == ('complete', result)
            assert not result['publication'] and result['newlyInstalled'] == result['modelGeometryChanges'] == 0
            for evidence in result['evidenceRefs']:
                assert ref(ROOT / evidence['path']) == evidence
            refs.extend([ref(folder / 'result.json'), ref(folder / 'neon-sync.json')])
            phase_rows.append({'batch': name, 'jobId': result['jobId'],
                'reasons': result.get('reasons'), 'identityPassed': result.get('identityPassed'),
                'allIndependentGroundChecksPassed': result.get('allIndependentGroundChecksPassed')})
    inputs = read(BASE / CLOSURE / 'support-inputs.json')
    uids = sorted(r['uid'] for r in inputs['sources'])
    assert len(uids) == 6
    claim = reservations.claim('codex-three-pair-checkpoint-' + str(uuid.uuid4()),
        ['building:' + uid for uid in uids], batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        spec = importlib.util.spec_from_file_location('checkpoint_triangles', HERE / 'xl-second-pass.py')
        second = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(second)
        second.LOCAL = local
        rows = []
        for row in inputs['sources']:
            if row['uid'] not in {'landsd/259803:0', 'landsd/9778:0', 'landsd/232089:0'}:
                continue
            raw = ROOT / row['candidate']['path']
            assert digest(raw.read_bytes()) == row['sourceSHA256']
            asset = local / 'assets' / raw.name
            asset.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(raw, asset)
            triangles = second.glb_triangles(row)
            assert np.isfinite(triangles).all()
            projection = shapely.union_all(shapely.polygons(triangles[:, :, [0, 2]]))
            filled = shapely.union_all([Polygon(part.exterior) for part in polygon_parts(projection)])
            b = row['source']['building']
            target = Polygon(b['rings'][0], b['rings'][1:])
            missing = target.difference(projection)
            void = filled.difference(projection).intersection(target)
            boundary = target.difference(filled)
            assert abs(missing.area - void.area - boundary.area) < 1e-6
            rows.append({'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'],
                'worldTrianglesSHA256': digest(np.asarray(triangles, dtype=np.float64).tobytes()),
                'sourceRef': ref(raw), 'sourceFormSHA256': digest(__import__('json').dumps(
                    b, sort_keys=True, separators=(',', ':')).encode()),
                'rawCoverage': float(target.intersection(projection).area / target.area),
                'enclosedVoidWithinTargetM2': float(void.area), 'boundaryMissingM2': float(boundary.area),
                'coverageWithAllVoidsFilled': float(target.intersection(filled).area / target.area),
                'passesUnchangedCoverageEvenWithVoidsFilled': target.intersection(filled).area / target.area >= .95,
                'installationApproved': False})
        save(doc / 'boundary-coverage.json', {'rows': rows, 'diagnosticOnly': True,
            'publication': False, 'modelGeometryChanges': 0,
            'qualification': 'Enclosed-void hypothesis does not recover 95% coverage. '
                'No filled geometry is emitted or accepted.'})
        refs += [ref(doc / 'boundary-coverage.json'), ref(Path(__file__)),
            ref(BASE / CLOSURE / 'support-inputs.json'), ref(HERE / 'xl-second-pass.py')]
        save(doc / 'phases.json', {'rows': phase_rows, 'uids': uids,
            'humanStatus': 'held-unknown', 'activeWorkers': 0, 'queuedFollowups': 0,
            'requiresAI': None, 'requiresHumanDecision': False,
            'nextStep': 'New exact component/source evidence or a demonstrated correction to a failed gate. '
                'Do not repeat unchanged support, current-ground or original-TIN checks.'})
        refs.append(ref(doc / 'phases.json'))
        payload = {'uids': uids, 'evidenceRefs': refs}
        stage = 'three-exact-original-component-pair-checkpoint-v1'
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'jobId': jid, 'batch': BATCH, 'phases': phase_rows,
            'indexedXLSourcesInvestigated': ['landsd/259803:0', 'landsd/9778:0', 'landsd/232089:0'],
            'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0,
            'scriptExternalAICalls': 0, 'activeWorkers': 0, 'queuedFollowups': 0,
            'qualification': 'Verified completed investigations only. Exact original TIN clears podium '
                '259803 contact/foundation, while its tower still penetrates terrain. No pair is approved.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for evidence in refs:
                assert ref(ROOT / evidence['path']) == evidence
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                (jid,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print({'jobId': jid, 'neonVerified': True, 'newlyInstalled': 0,
            'boundaryResults': [{k: r[k] for k in ['uid', 'rawCoverage', 'enclosedVoidWithinTargetM2',
                'boundaryMissingM2']} for r in rows]}, flush=True)
    finally:
        reservations.release(lease)


if __name__ == '__main__':
    main()
