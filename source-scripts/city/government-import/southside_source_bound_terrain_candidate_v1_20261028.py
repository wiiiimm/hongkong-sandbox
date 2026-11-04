"""Construct a NEW unapproved private source-core/parent-apron terrain candidate."""
import argparse
import copy
import json
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from source_bound_terrain_transition_v1_20261028 import build, parent_faces, plane, heights

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-source-bound-terrain-candidate-v1-20261028'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
MASK = BASE/'government-xl-southside-source-bound-terrain-mask-v1-20261028'
PRIOR = BASE/'government-xl-southside-unchanged-highest-surface-proof-v1-20261028'
SCOPE = BASE/'government-xl-southside-private-terrain-overlap-v1-20261028'
GROUND = BASE/'government-xl-la-marina-southside-original-terrain-v1-20261028'


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def freeze(refs, result):
    # The older generic source checkpoint hard-codes terrainGeometryChanges=0.
    # This new private recipe really changes terrain, so record that honestly
    # while keeping public writes/publication/source-building edits at zero.
    stage = 'private-source-bound-terrain-construction-diagnostic'
    refs = sorted(set(refs + [p for p in DOC.rglob('*') if p.is_file()]))
    bound = [ref(p) for p in refs]
    claim = reservations.claim('private-terrain-checkpoint-' + str(uuid.uuid4()),
                               ['source-context:' + BATCH], batch=BATCH, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        payload = dict(uids=result['uids'], evidenceRefs=bound)
        jid = jobs.enqueue(BATCH, stage, payload)
        job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        saved = dict(payload, **result, jobId=jid, batch=BATCH, stage=stage)
        with connect() as db:
            db.row_factory = dict_row
            db.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(db, lease)
            for row in bound:
                assert ref(ROOT/row['path']) == row
            assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                              (Jsonb(saved), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', saved)
        save(DOC/'result.json', saved)
        save(DOC/'neon-sync.json', dict(jobId=jid, resultVerified=True))
        print(dict(jobId=jid, neonVerified=True), flush=True)
    finally:
        assert reservations.release(lease)['ok']


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins = [Path(__file__), HERE/'source_bound_terrain_transition_v1_20261028.py',
                  HERE/'test_source_bound_terrain_transition_v1_20261028.py', HERE/'native_patch_resolution.py'], {}
    for batch in [MASK, PRIOR, SCOPE]:
        _, bound = authenticate(batch)
        refs.append(batch/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    mask = take(MASK/'summary.json')
    assert mask['allFourOutsideFormsDisjoint'] and mask['allOriginalVerticesInsideCore']
    assert {'building:' + u for u in mask['uids']} <= set(lease['resources'])
    prior = take(PRIOR/'summary.json')
    assert prior['existingNativeHeightContractPassed']
    patch = take(PRIOR/'height-contract-only-terrain.json.gz')
    scope = take(SCOPE/'scope.json')
    parentpath = ROOT/'3d-viewer/city/data/terrain.json'
    assert digest(parentpath.read_bytes()) == patch['meta']['parentSha256']
    parent = read(parentpath); refs.append(parentpath)
    core, outer = shapely.from_wkt(mask['nativeCoreWKT']), shapely.from_wkt(mask['proposedOuterEditWKT'])
    domain = shapely.box(*scope['bounds'])
    assert shapely.box(*scope['nativeCore']).covers(shapely.from_wkt(mask['sourceProjectionWKT']))
    tests = subprocess.run([sys.executable, str(HERE/'test_source_bound_terrain_transition_v1_20261028.py')],
                           cwd=ROOT, capture_output=True, text=True)
    save(DOC/'tests.json', dict(exitCode=tests.returncode, stdout=tests.stdout, stderr=tests.stderr))
    assert tests.returncode == 0
    mesh = patch['nativeMesh']
    old = np.asarray(mesh['position'], dtype='<f4').astype('<f8').reshape(-1, 3)[np.asarray(mesh['index']).reshape(-1, 3)]
    roots = parent_faces(parent, patch['coarseCells'])
    out, lineage, audit = build(old, roots, core, outer, domain,
                               progress=lambda n, count: print(dict(sourceFacesProcessed=n, candidateFaces=count), flush=True))
    assert reservations.owns(lease)
    runtime = out.astype('<f4').astype('<f8')
    core_ids = [i for i, row in enumerate(lineage) if row['kind'].startswith('unchanged-core')]
    assert all(np.array_equal(out[i], old[lineage[i]['originalFace']]) for i in core_ids)
    drifts = []
    for i, row in enumerate(lineage):
        if row['kind'] != 'clipped-core':
            continue
        face = old[row['originalFace']]
        delta = float(abs(heights(plane(face), runtime[i][:, [0, 2]])-runtime[i][:, 1]).max())
        drifts.append(dict(candidateFace=i, originalFace=row['originalFace'], heightEquationErrorM=delta))
    max_drift = max((r['heightEquationErrorM'] for r in drifts), default=0)
    violations = [r for r in drifts if r['heightEquationErrorM'] >= .01]
    new = copy.deepcopy(patch)
    new['id'] = BATCH
    new['nativeMesh'].pop('sourceOverlap', None)
    new['nativeMesh']['source'].pop('coordinatedBoundary', None)
    new['nativeMesh']['position'] = out.reshape(-1).tolist()
    new['nativeMesh']['index'] = list(range(len(out)*3))
    new['nativeMesh']['source']['policy'] = 'Original unchanged source core; finite parent-plane-aware transition and exact exterior parent. Private candidate only.'
    new['meta']['source']['sourceBoundEdit'] = dict(mask=ref(MASK/'summary.json'), parent=ref(parentpath),
                                                 kernel=ref(HERE/'source_bound_terrain_transition_v1_20261028.py'))
    new['meta']['source']['policy'] = new['nativeMesh']['source']['policy']
    asset = DOC/'candidate-terrain.json.gz'
    save(asset, new)
    save(DOC/'lineage.json.gz', dict(rows=lineage, construction=audit, clippedCoreFloat32HeightDrift=drifts))
    polys = shapely.polygons(runtime[:, :, [0, 2]])
    valid = shapely.area(polys) > 1e-10
    union = shapely.union_all(polys[valid])
    coverage_gap = float(union.symmetric_difference(domain).area)
    exterior_indices = [i for i, row in enumerate(lineage) if row['kind'] == 'exterior-parent']
    exterior_error = max((float(abs(runtime[i][:, 1]-heights(plane(roots[lineage[i]['parentFace']]), runtime[i][:, [0, 2]])).max())
                          for i in exterior_indices), default=0)
    result = dict(uids=['landsd/315025:0'], sourceContextUids=mask['uids'], candidate=ref(asset),
                  candidateFaces=len(out), oldMasterFaces=len(old), construction=audit,
                  coreWholeFacesRetainedExactly=len(core_ids), allWholeCoreFacesByteCoordinateEqual=True,
                  maximumClippedCoreFloat32PlaneDriftM=max_drift, clippedCoreHeightDriftViolations=violations,
                  runtimeVertexDisplacementM=float(abs(runtime-out).max()), coverageGapM2=coverage_gap,
                  projectedOverlapM2=float(shapely.area(polys[valid]).sum()-union.area),
                  maximumExteriorParentPlaneDriftM=exterior_error,
                  runtimeNodeBudgetPassed=len(out) <= 25000, privateTerrainConstructed=True,
                  privateTerrainHeightEditingOutsideCore=True, terrainGeometryChanges=len(out)-len(core_ids),
                  publicTerrainGeometryChanges=0, modelGeometryChanges=0, sourceGeometryChanges=0,
                  scriptExternalAICalls=0, aiGeometryModelling=False, newlyInstalled=0, publication=False,
                  identityAccepted=False, physicalAccepted=False, installationApproved=False,
                  permanentRejection=False, fullTerrainAcceptance=False,
                  qualification='NEW private terrain recipe, not a partition of the old approved candidate. Every whole source-core face retained exactly; core fragments retain old planes with explicit Float32 drift. Apron heights intentionally blend source to exact original parent; exterior uses finite original parent planes. Vertical and degenerate source projections handled explicitly. No building geometry/pose or live terrain changed. Full overlap, coverage, budget, root/seam, original-model, all84-neighbour and browser acceptance remain mandatory and cannot transfer from the rectangular proposal.')
    save(DOC/'summary.json', result)
    assert reservations.owns(lease)
    freeze(list(dict.fromkeys(refs)), result)
    print({k: result[k] for k in ['candidateFaces', 'coreWholeFacesRetainedExactly', 'maximumClippedCoreFloat32PlaneDriftM',
                                'coverageGapM2', 'maximumExteriorParentPlaneDriftM', 'runtimeNodeBudgetPassed']}, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(MASK); authenticate(GROUND)
    mask = read(MASK/'summary.json')
    resources = {'building:' + u for u in mask['uids']}
    resources.update('building:' + r['uid'] for r in mask['outsideForms'])
    resources.update('source-terrain:' + s for s in read(GROUND/'summary.json')['sheets'])
    resources.add('terrain:city/data/terrain.json')
    claim = reservations.claim('southside-source-bound-terrain-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
