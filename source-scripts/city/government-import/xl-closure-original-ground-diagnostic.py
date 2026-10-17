"""Measure complete original components against an original government TIN candidate independently.

A failed stacked tower/podium interface need not describe two ground-standing
parts. This diagnostic tests that alternative without identity approval, ground
edits, source edits, waived limits, or publication.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row, NATIVE_RUN
from publication_lock import locked_publication


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def verified(closure, tower):
    prior = read(closure / 'result.json')
    assert read(closure / 'neon-sync.json') == {'jobId': prior['jobId'], 'resultVerified': True}
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
            (prior['jobId'],)).fetchone() == ('complete', prior)
    for evidence in prior['evidenceRefs']:
        assert ref(ROOT / evidence['path']) == evidence
    inputs = read(closure / 'support-inputs.json')
    pair = next(p for p in inputs['pairs'] if p['uid'] == tower)
    wanted = {pair['uid'], pair['supportUid']}
    rows = [r for r in inputs['sources'] if r['uid'] in wanted]
    assert len(rows) == 2 and {r['uid'] for r in rows} == wanted
    return prior, pair, rows


def owned(args, doc, local, closure):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    with locked_publication(ROOT):
        prior, pair, rows = verified(closure, args.tower)
        manifest = ROOT / '3d-viewer/city/data/manifest.json'
        manifest_ref = ref(manifest)
        for row in rows:
            raw = (ROOT / row['candidate']['path']).read_bytes()
            assert digest(raw) == row['sourceSHA256']
            assert len(raw) == row['native']['model']['asset']['bytes']
            asset = local / 'assets' / (row['sourceSHA256'] + '.glb.gz')
            asset.parent.mkdir(parents=True, exist_ok=True)
            asset.write_bytes(raw)
        save(doc / 'selection.json.gz', {'rows': rows, 'manifestSHA256': manifest_ref['sha256']})
        from original_pair_terrain_diagnostic import build
        build(rows, doc, local)
        rel = lambda p: str(p.relative_to(ROOT))
        subprocess.run(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(doc / 'selection.json.gz'),
            '--candidates', rel(local), '--terrain-candidates', rel(doc / 'terrain-candidates.json'),
            '--out', rel(doc / 'metrics.json'), '--geometry-out', rel(local / 'runtime-geometry.json.gz')], cwd=ROOT, check=True)
        metrics = read(doc / 'metrics.json')
        geometries = {r['uid']: r for r in read(local / 'runtime-geometry.json.gz')['rows']}
        by_uid = {r['uid']: r for r in metrics['rows']}
        final = module('independent_ground_foundation', 'xl-final-script-pass.py')
        policy = module('independent_ground_policy', 'acceptance-policy.py')
        outcomes = []
        for row in rows:
            uid = row['uid']
            metric = by_uid[uid]
            assert not metric.get('error'), metric
            geometry = geometries[uid]
            triangles = np.asarray(geometry['position']).reshape(-1, 3)[np.asarray(geometry['index']).reshape(-1, 3)]
            ground = np.asarray(geometry['drawnGroundGeometry']).reshape(-1, 3, 3)
            assert triangles.shape == (row['triangles'], 3, 3) and np.isfinite(triangles).all()
            bounds = np.array([triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))])
            assert np.max(np.abs(bounds - row['native']['model']['worldBounds'])) < .002
            b = row['source']['building']
            foundation = final.foundation_context(triangles, ground, Polygon(b['rings'][0], b['rings'][1:]))
            foundation_pass = foundation['completeTerrainTriangles'] == foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction'] == 0
            # Identity remains explicitly unapproved. Separate its policy failure
            # only to describe physical measurements; never expose this as acceptance.
            raw_reasons = policy.reasons({'state': 'runtime-validated-awaiting-acceptance',
                'sourceSHA256': row['sourceSHA256'], 'identityProof': {'identityAccepted': False}},
                metric, metrics['profiles']['mobile'])
            physical = [r for r in raw_reasons if r != 'strict-identity-fit']
            if not foundation_pass:
                physical.append('whole-source-foundation')
            outcomes.append({'uid': uid, 'sourceSHA256': row['sourceSHA256'], 'metric': metric,
                'foundation': foundation, 'physicalReasons': sorted(set(physical)),
                'rawAcceptanceReasons': raw_reasons, 'independentGroundChecksPassed': not physical,
                'identityAccepted': False, 'installationApproved': False})
            print(json.dumps({'uid': uid, 'independentGroundChecksPassed': not physical,
                'physicalReasons': sorted(set(physical)), 'minSurfaceGap': metric['minSurfaceGap'],
                'minLowGap': metric['minLowGap'], 'maxLowGap': metric['maxLowGap']}), flush=True)
        save(doc / 'physical-results.json.gz', {'rows': outcomes})
        refs = [ref(p) for p in sorted(doc.iterdir()) if p.is_file()]
        refs += [ref(Path(__file__)), ref(closure / 'result.json'), ref(closure / 'support-inputs.json'),
            ref(HERE / 'acceptance-policy.py'), ref(HERE / 'xl-final-script-pass.py'),
            ref(HERE / 'original_pair_terrain_diagnostic.py')]
        for path, sha in metrics['inputHashes'].items():
            assert digest((ROOT / path).read_bytes()) == sha
        assert ref(manifest) == manifest_ref
        payload = {'pair': pair, 'sourceSHA256s': {r['uid']: r['sourceSHA256'] for r in rows}, 'evidenceRefs': refs}
        stage = 'original-closure-independent-original-tin-ground-diagnostic-v1'
        job_id = jobs.enqueue(args.batch, stage, payload)
        job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == job_id
        result = {**payload, 'jobId': job_id, 'batch': args.batch, 'rows': outcomes,
            'allIndependentGroundChecksPassed': all(r['independentGroundChecksPassed'] for r in outcomes),
            'publication': False, 'newlyInstalled': 0, 'modelGeometryChanges': 0,
            'terrainCandidateOnly': True, 'scriptExternalAICalls': 0, 'activeWorkers': 0,
            'qualification': 'Complete source/contact/foundation measurements against a source-backed original TIN candidate only. '
                'No identity, stacked-support exception, runtime/browser or publication acceptance.'}
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, lease)
            for row in rows:
                native = row['native']
                assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
                    'JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                    (NATIVE_RUN, native['cacheKey'])).fetchone()['result_sha'] == native['resultSha']
            for evidence in refs:
                assert ref(ROOT / evidence['path']) == evidence
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                (Jsonb(result), job_id, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                (job_id,)).fetchone() == ('complete', result)
        save(doc / 'result.json', result)
        save(doc / 'neon-sync.json', {'jobId': job_id, 'resultVerified': True})
        print(json.dumps({'jobId': job_id, 'neonVerified': True,
            'allIndependentGroundChecksPassed': result['allIndependentGroundChecksPassed']}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ('batch', 'closure', 'tower'):
        p.add_argument('--' + key, required=True)
    p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    closure = (ROOT / args.closure).resolve()
    assert closure.parent == ROOT / 'docs/astra-city/government-import'
    doc = closure.parent / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        return owned(args, doc, local, closure)
    assert not doc.exists(), 'Fresh diagnostic only'
    _, _, rows = verified(closure, args.tower)
    claim = reservations.claim('codex-independent-ground-' + str(uuid.uuid4()),
        ['building:' + r['uid'] for r in rows], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
        '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__,
        *sys.argv[1:], '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
