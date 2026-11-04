"""Fresh physical continuation retaining exact current ground under named basic forms.

Reuse a complete, Neon-verified terrain candidate rather than rebuilding its TIN.
Never publish here. Original model bytes/pose and every acceptance limit remain.
"""
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import traceback
import uuid
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon, box
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row, NATIVE_RUN
import native_patch_resolution as patches
from routed_original_cell_identity import verify_files, POLICY


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    return digest(Path(path).read_bytes())


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def verify_previous(previous):
    result = read(previous / 'result.json')
    assert result['activeWorkers'] == 0 and result['publication'] is False
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        actual = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone()
    assert actual and actual[0] == 'complete' and actual[1] == result, 'Previous result not complete and verified'
    for ref in result['evidenceRefs']:
        assert sha(ROOT / ref['path']) == ref['sha256'], ref['path']
    selection = read(previous / 'selection.json.gz')
    assert len(selection['rows']) == 1
    assert sha(ROOT / '3d-viewer/city/data/manifest.json') == selection['manifestSHA256']
    row = selection['rows'][0]
    assert row['uid'] == result['uid'] and row['sourceSHA256'] == result['sourceSHA256']
    assert sha(ROOT / row['candidate']['path']) == row['sourceSHA256']
    for path, pinned in read(previous / 'metrics.json')['inputHashes'].items():
        assert sha(ROOT / path) == pinned, path
    return result, selection, row


def finish(args, row, doc, local, reasons):
    receipt = read(local / 'reservation.json')
    assert reservations.owns(receipt)
    refs = [{'path': rel(p), 'sha256': sha(p)} for p in sorted(doc.iterdir())
            if p.is_file() and p.name not in ('result.json', 'neon-sync.json', 'README.md')]
    payload = {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'evidenceRefs': refs,
               'runnerSHA256': sha(__file__), 'identityPolicy': POLICY}
    stage = 'verified-terrain-basic-neighbour-retention-v1'
    jobid = jobs.enqueue(args.batch, stage, payload)
    job = jobs.claim(args.batch, receipt['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jobid
    result = {**payload, 'jobId': jobid, 'batch': args.batch, 'reasons': sorted(set(reasons)),
              'humanStatus': 'held-unknown' if reasons else 'in-process',
              'scriptChecksPassed': not reasons, 'newlyInstalled': 0, 'publication': False,
              'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'activeWorkers': 0,
              'queuedFollowups': 0, 'requiresAI': False, 'requiresHumanDecision': False,
              'nextStep': 'Resolve recorded original terrain/source/support blockers without changing physical limits.' if reasons
              else 'Complete staged/live browsers, guarded publication and installed ledger.'}
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, receipt)
        actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, row['native']['cacheKey'])).fetchone()
        assert actual and actual['result_sha'] == row['native']['resultSha']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                           (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
    save(doc / 'result.json', result)
    save(doc / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'uid': row['uid'], 'checksPassed': not reasons, 'reasons': result['reasons'], 'jobId': jobid, 'neonVerified': True}), flush=True)


def owned(args, previous, doc, local):
    assert reservations.owns(read(local / 'reservation.json'))
    old_result, selection, row = verify_previous(previous)
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    live = {m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    assert row['uid'] not in live
    old_candidate = read(previous / 'terrain-candidates.json')
    assert len(old_candidate) == 1
    original = old_candidate[0]
    assert sha(ROOT / original['path']) == original['sha256']
    old_local = HERE / 'local' / old_result['batch']
    context = next(c for c in read(old_local / 'frozen-inputs/context.json.gz')['rows'] if c['uid'] == row['uid'])
    identity = verify_files(row, context, local / 'identity-recheck')
    assert identity['passed'] and identity['policy'] == POLICY
    save(doc / 'owned-source-identity.json', identity)
    save(doc / 'selection.json.gz', selection)
    for name in ['catalogue.json', 'catalogue-index.json', 'source-forms.json']:
        shutil.copyfile(old_local / name, local / name)
    shutil.copytree(old_local / 'assets', local / 'assets')
    source = local / 'assets' / (row['sourceSHA256'] + '.glb.gz')
    assert sha(source) == row['sourceSHA256']
    for path, pinned in context['neighbourTileHashes'].items():
        assert sha(ROOT / '3d-viewer' / path) == pinned
    inputs = read(previous / 'neighbour-inputs.json.gz')
    forms = {r['building']['uid']: r for r in inputs['rows']}
    assert len(set(args.protect)) == len(args.protect)
    assert all(uid in forms and uid != row['uid'] and uid not in live
               and not forms[uid]['existingNative'] and not forms[uid]['building'].get('modelGeometry') for uid in args.protect), 'Basic neighbour required'
    parent_path = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(parent_path)
    terrain = module('reuse_exact_terrain', 'xl-second-pass.py')
    terrain.LOCAL = local
    sampler = terrain.resolution.terrain.fine.DemSampler(parent, rendered=True)
    patch = read(ROOT / original['path'])
    bounds = original['bounds']
    model = terrain.glb_triangles(row)
    projection = shapely.union_all(shapely.polygons(model[:, :, [0, 2]]))
    protected_parts = [Polygon(forms[uid]['building']['rings'][0], forms[uid]['building']['rings'][1:])
                       .buffer(.01, join_style='mitre') for uid in args.protect]
    protected = shapely.union_all(protected_parts).intersection(box(*bounds))
    # This route retains ROOT planes only. An installed patch requires its exact
    # facet sampler and a separate explicitly verified continuation.
    for p in manifest['terrainPatches']:
        assert box(*patches._patch_bounds(read(ROOT / '3d-viewer' / p['url']))).intersection(protected).area < 1e-8, 'Protected basic form intersects installed terrain'
    proof = patches.preserve_parent_under_projection(patch, bounds, protected, sampler)
    proof.update(protectedUids=args.protect, sourceProjectionIntersectionM2=float(protected.intersection(projection).area),
                 rootURL='city/data/terrain.json', rootSHA256=sha(parent_path),
                 policy='Exact current root planes beneath named basic neighbour footprints plus 0.01m; candidate only, including overlaps with new source. Complete source and neighbour gates remain mandatory.')
    patch['nativeMesh']['source']['protectedBasicNeighbours'] = proof
    # Carry the earlier broad root-retention provenance into the candidate itself.
    prior_root = read(previous / 'source-local-parent-preservation.json')
    patch['nativeMesh']['source']['sourceLocalParentPreservation'] = {
        'proof': prior_root, 'evidencePath': rel(previous / 'source-local-parent-preservation.json'),
        'evidenceSHA256': sha(previous / 'source-local-parent-preservation.json')}
    patch['nativeMesh']['source']['finalBoundarySnap'] = patches.snap_boundary_to_parent(patch, bounds, sampler)
    patch['nativeMesh'].pop('sourceOverlap', None)
    target = local / Path(original['path']).name
    save(target, patch)
    source_files = read(previous / 'terrain.json')['sourceFiles']
    for ref in source_files:
        assert sha(ROOT / ref['path']) == ref['sha256']
    if patches.projected_context(patch, bounds)[3] > 1e-8:
        patches.approve_original_overlap(patch, target, doc / 'native-overlap.json', source_files)
        patches.finalize_overlap_evidence(patch, doc / 'native-overlap.json')
    triangles = len(patch['nativeMesh']['index']) // 3
    assert triangles <= 100000, 'final-terrain-runtime-budget'
    terrain.resolution.validate_patch(patch, parent)
    save(target, patch)
    revised = {**original, 'path': rel(target), 'sha256': sha(target), 'triangles': triangles}
    save(doc / 'neighbour-preservation.json', {'originalPatch': original, 'finalPatch': revised, 'proof': proof,
          'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'publication': False})
    save(doc / 'final-terrain-budget.json', {'finalTriangles': triangles, 'maximumTriangles': 100000, 'passed': True, 'runtimeBudgetChanged': False})
    save(doc / 'terrain-candidates.json', [revised])
    save(doc / 'terrain.json', {'patch': revised, 'sourceFiles': source_files, 'reusedFrom': old_result['jobId'], 'modelGeometryChanges': 0})
    inputs['patches'] = [revised]
    save(doc / 'neighbour-inputs.json.gz', inputs)
    save(doc / 'continuation-inputs.json', {'previousJobId': old_result['jobId'], 'previousResult': rel(previous / 'result.json'),
        'previousResultSHA256': sha(previous / 'result.json'), 'inputHashes': {
            rel(p): sha(p) for p in [Path(__file__), HERE / 'native_patch_resolution.py',
            HERE / 'routed_original_cell_identity.py', HERE / 'xl-second-pass.py', HERE / 'xl-final-script-pass.py',
            HERE / 'terrain_diagnostic_resolution.py']}, 'modelGeometryChanges': 0, 'publication': False})

    def call(command, allowed=(0,)):
        assert subprocess.run(command, cwd=ROOT).returncode in allowed
        assert reservations.owns(read(local / 'reservation.json'))

    call(['node', str(HERE / 'acceptance-metrics-multi-retained.mjs'), '--selection', rel(doc / 'selection.json.gz'),
          '--candidates', rel(local), '--terrain-candidates', rel(doc / 'terrain-candidates.json'),
          '--out', rel(doc / 'metrics.json'), '--geometry-out', rel(local / 'runtime-geometry.json.gz')])
    call(['node', str(HERE.parent / 'building-batch/validate_candidates_multi_retained.mjs'), '--candidates', rel(local),
          '--source-forms', rel(local / 'source-forms.json'), '--terrain-candidates', rel(doc / 'terrain-candidates.json'),
          '--out', rel(doc / 'validation.json')], (0, 1))
    call(['node', str(HERE / 'check-neighbours-multi-retained.mjs'), rel(doc) + '/'])
    call(['node', str(HERE / 'check-native-neighbours-multi-retained.mjs'), rel(doc) + '/'])
    g = read(local / 'runtime-geometry.json.gz')['rows'][0]
    tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
    ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
    b = row['source']['building']
    foundation = module('reuse_foundation', 'xl-final-script-pass.py').foundation_context(tri, ground, Polygon(b['rings'][0], b['rings'][1:]))
    f = {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'foundation': foundation,
         'strictFoundationAccepted': foundation['completeTerrainTriangles'] == foundation['triangles']
         and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction'] == 0}
    save(doc / 'foundation.json', {'rows': [f], 'modelGeometryChanges': 0})
    metrics = read(doc / 'metrics.json')
    for name in ['metrics.json', 'validation.json', 'neighbour-checks.json', 'native-neighbour-checks.json', 'continuation-inputs.json']:
        for path, pinned in read(doc / name).get('inputHashes', {}).items():
            assert sha(ROOT / path) == pinned, path
    metric = metrics['rows'][0]
    validation = read(doc / 'validation.json')['results'][0]
    from terrain_diagnostic_resolution import resolve_global_bottom_warning
    diagnostic = resolve_global_bottom_warning(validation, metric, f)
    save(doc / 'global-bottom-diagnostic.json', diagnostic)
    reasons = module('reuse_acceptance', 'acceptance-policy.py').reasons(
        {'state': 'runtime-validated-awaiting-acceptance', 'sourceSHA256': row['sourceSHA256'], 'identityProof': identity['proof']}, metric, metrics['profiles']['mobile'])
    reasons.extend(diagnostic['remaining'])
    if not f['strictFoundationAccepted']:
        reasons.append('whole-source-foundation')
    native = read(doc / 'native-neighbour-checks.json')
    resolved = set(native['resolved'])
    reasons.extend('native-neighbour-regression:' + uid for uid in set(native['blocked']) - resolved)
    reasons.extend('terrain-regresses-neighbour:' + r['uid'] for r in read(doc / 'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
    finish(args, row, doc, local, reasons)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous', required=True); p.add_argument('--batch', required=True)
    p.add_argument('--protect', required=True, action='append'); p.add_argument('--owned', action='store_true')
    args = p.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    previous = ROOT / args.previous
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    if args.owned:
        try:
            owned(args, previous, doc, local)
        except AssertionError as error:
            save(doc / 'guard-failure.json', {'error': str(error), 'traceback': traceback.format_exc(), 'publication': False})
            row = read(previous / 'selection.json.gz')['rows'][0]
            finish(args, row, doc, local, ['terrain-continuation-guard:' + str(error)])
        return
    _, _, row = verify_previous(previous)
    assert not doc.exists() and not local.exists(), 'Fresh continuation only'
    inputs = read(previous / 'neighbour-inputs.json.gz')
    uids = {r['building']['uid'] for r in inputs['rows']} | {row['uid']} | set(args.protect)
    replacements = read(previous / 'terrain-candidates.json')[0]['replacesMany']
    for replacement in replacements:
        uids.update(replacement['retainedUids'])
    resources = [('building:' if uid.startswith('landsd/') else 'source-form:') + uid for uid in sorted(uids)]
    resources += ['terrain-patch:' + row['uid'], 'terrain-surface:city/data/terrain.json']
    resources += ['terrain-surface:' + r['url'] for r in replacements]
    claim = reservations.claim('codex-xl-basic-retention-' + str(uuid.uuid4()), resources, batch=args.batch)
    assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file',
                    str(local / 'reservation.json'), '--', sys.executable, __file__, '--previous', args.previous,
                    '--batch', args.batch, *[item for uid in args.protect for item in ('--protect', uid)], '--owned'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
