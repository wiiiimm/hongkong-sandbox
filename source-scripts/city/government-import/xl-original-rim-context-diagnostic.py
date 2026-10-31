"""Bind exact failed rim positions, original TIN and basic-support probes in Neon.

Read-only geometry diagnostics. No acceptance, source edits or publication.
"""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row, NATIVE_RUN
from original_tin_point_diagnostic import indexed_surface, point_heights
import importlib.util


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def owned(args, doc, local):
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    previous = ROOT / args.previous
    reuse = module('verified_completed_terrain', 'xl-reuse-terrain-retain-basic-neighbours.py')
    prior, selection, row = reuse.verify_previous(previous)
    old_local = HERE / 'local' / prior['batch']
    geometry = old_local / 'runtime-geometry.json.gz'
    helpers = [Path(__file__), HERE / 'xl-reuse-terrain-retain-basic-neighbours.py',
               HERE / 'diagnose-low-rim-current-ground.mjs', HERE / 'diagnose-rim-neighbour-locations.py',
               HERE / 'basic-neighbour-source-support-diagnostic.mjs', HERE / 'original_tin_point_diagnostic.py',
               HERE / 'xl-second-pass.py']
    helper_hashes = {rel(p): sha(p) for p in helpers}

    def call(command):
        subprocess.run(command, cwd=ROOT, check=True)
        assert reservations.owns(lease)

    call(['node', str(HERE / 'diagnose-low-rim-current-ground.mjs'), '--doc', args.previous,
          '--geometry', rel(geometry), '--out', rel(doc / 'low-rim.json')])
    call([sys.executable, str(HERE / 'diagnose-rim-neighbour-locations.py'), '--rim', rel(doc / 'low-rim.json'),
          '--neighbours', rel(previous / 'neighbour-inputs.json.gz'), '--out', rel(doc / 'neighbour-locations.json'),
          *[part for uid in args.protect for part in ('--uid', uid)]])
    support_path = local / 'basic-support-samples.json'
    call(['node', str(HERE / 'basic-neighbour-source-support-diagnostic.mjs'), rel(previous) + '/', rel(geometry), rel(support_path)])
    support = read(support_path)
    assert support['uid'] == row['uid'] and support['sourceSHA256'] == row['sourceSHA256']
    assert set(args.protect).issubset({r['uid'] for r in support['rows']})
    for path, pinned in support['inputHashes'].items():
        assert sha(ROOT / path) == pinned
    save(doc / 'basic-support-samples.json.gz', support)
    source_files, pieces = [], []
    terrain = module('exact_original_terrain_reader', 'xl-second-pass.py')
    for sheet in read(previous / 'source-recovery.json')['sheets']:
        folder = ROOT / sheet['cache']
        receipt = read(folder / 'original/download.json')
        directory = read(folder / 'directory/result.json')
        assert sheet['directorySHA256'] == receipt['directorySHA256'] == directory['directorySHA256']
        assert receipt['terrainGeometryIncluded'] and receipt['sheet'] == sheet['sheet']
        for entry in sheet['terrainFiles']:
            p = folder / 'terrain' / entry['name']
            assert sha(p) == entry['sha256']
            source_files.append({'path': rel(p), 'sha256': sha(p)})
            if p.suffix == '.gltf':
                pieces.append(terrain.terrain_triangles(p))
    native = np.concatenate(pieces)
    rim = read(doc / 'low-rim.json')['rows'][0]
    points = np.asarray([p['point'] for p in rim['points']])
    sample_indexes, heights, highest = point_heights(points, indexed_surface(native))
    assert np.isfinite(highest).all(), 'Original source coverage missing at rim'
    per_point = []
    for i, p in enumerate(rim['points']):
        originals = heights[sample_indexes == i]
        per_point.append({**p, 'originalTINHeights': originals.tolist(), 'originalTINGround': float(highest[i]),
                          'originalTINGap': float(points[i, 1] - highest[i]),
                          'candidateOriginalTINDelta': float(p['candidateGround'] - highest[i])})
    summary = {'samples': len(points), 'originalTerrainTriangles': len(native),
               'maxCandidateOriginalTINDeltaM': max(abs(p['candidateOriginalTINDelta']) for p in per_point),
               'maxOriginalTINGapM': max(p['originalTINGap'] for p in per_point),
               'samplesOverUnchanged1mLimit': sum(p['originalTINGap'] > 1 for p in per_point)}
    save(doc / 'original-tin-rim.json', {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'summary': summary,
         'points': per_point, 'sourceFiles': source_files, 'modelGeometryChanges': 0, 'publication': False,
         'qualification': 'All original covering terrain planes at the unchanged acceptance rim samples. Numeric diagnostic only; no contact or source-identity acceptance.'})
    save(doc / 'inputs.json', {'previousJobId': prior['jobId'], 'previousResultPath': rel(previous / 'result.json'),
         'previousResultSHA256': sha(previous / 'result.json'), 'inputHashes': helper_hashes,
         'sourceFiles': source_files, 'originalModelPath': row['candidate']['path'],
         'originalModelSHA256': row['sourceSHA256'], 'modelGeometryChanges': 0, 'publication': False})
    refs = [{'path': rel(p), 'sha256': sha(p)} for p in sorted(doc.iterdir()) if p.is_file()]
    refs += [{'path': rel(previous / 'result.json'), 'sha256': sha(previous / 'result.json')}]
    payload = {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'evidenceRefs': refs,
               'previousJobId': prior['jobId'], 'runnerSHA256': sha(__file__)}
    stage = 'exact-original-rim-tin-and-basic-support-context-v1'
    jobid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jobid
    result = {**payload, 'jobId': jobid, 'batch': args.batch, 'rimTIN': summary,
              'basicSupportChecks': [{'uid': r['uid'], **{k: r['proof'][k] for k in ['samples', 'contacts', 'missing', 'minGap', 'maxGap', 'allSampledContactsPass']}}
                                     for r in support['rows']],
              'previousReasons': prior['reasons'], 'humanStatus': 'held-unknown', 'state': 'held-for-second-pass',
              'retainCurrentModel': True, 'revisitLater': True, 'permanentRejection': False,
              'requiresAI': False, 'requiresHumanDecision': False, 'activeWorkers': 0, 'queuedFollowups': 0,
              'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
              'nextStep': 'Reuse these completed failures. Require changed authoritative source/terrain/component evidence or a demonstrated code correction, then all physical/runtime/browser/publication gates.',
              'qualification': 'Exact point/plane and support probes only. These establish neither permanent impossibility nor a need for AI modelling.'}
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, lease)
        actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchone()
        assert actual and actual['result_sha'] == row['native']['resultSha']
        for ref in refs + source_files:
            assert sha(ROOT / ref['path']) == ref['sha256']
        for path, pinned in helper_hashes.items():
            assert sha(ROOT / path) == pinned
        assert sha(ROOT / row['candidate']['path']) == row['sourceSHA256']
        assert sha(ROOT / '3d-viewer/city/data/manifest.json') == selection['manifestSHA256']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'jobId': jobid, 'neonVerified': True, 'rimTIN': summary, 'newlyInstalled': 0}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous', required=True); p.add_argument('--batch', required=True)
    p.add_argument('--protect', action='append', required=True); p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        owned(args, doc, local)
        return
    assert not doc.exists() and not local.exists(), 'Fresh diagnostic only'
    row = read(ROOT / args.previous / 'selection.json.gz')['rows'][0]
    claim = reservations.claim('codex-xl-original-rim-context-' + str(uuid.uuid4()),
        ['building:' + uid for uid in sorted({row['uid'], *args.protect})], batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file',
        str(local / 'reservation.json'), '--', sys.executable, __file__, '--previous', args.previous, '--batch', args.batch,
        *[part for uid in args.protect for part in ('--protect', uid)], '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
