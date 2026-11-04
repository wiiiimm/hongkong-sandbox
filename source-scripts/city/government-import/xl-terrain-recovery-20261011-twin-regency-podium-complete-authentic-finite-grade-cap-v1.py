"""Whole456 original P against authenticated untouched complete source TIN.

This is source-only feasibility and genuine grade/cap evidence. Historic packed
terrain candidate, current renderer and sampled foundation are not substituted
for authenticated provider facets. Main363 is not an accepted structural seed.
"""
import copy
import importlib.util
import json
import time
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse_verify
from exact_original_paired_finite_clearance_v3_20261011 import verify as paired_verify
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_verify
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261011-twin-regency-podium-complete-authentic-finite-grade-cap-v1'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
CROSS = BASE / 'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2'
OLD = BASE / 'government-xl-twin-regency-podium-original-terrain-20261007'
UID = 'landsd/223206:0'
SHA = 'fd67218f6828e36899e689d071c55bf95fa0df159ac2927643be46eead74d347'

def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))

def canonical(x):
    return digest(json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())

def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def main():
    assert not DOC.exists()
    receipt = read(CROSS / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                         (receipt['jobId'],)).fetchone() == ('complete', receipt)
    assert ref(CROSS / 'diagnostic.json.gz') in receipt['evidenceRefs']
    prior = read(CROSS / 'diagnostic.json.gz')
    source = next(r for r in prior['completeSourceInputs'] if r['uid'] == UID)
    asset = ROOT / source['asset']['path']; assert ref(asset) == source['asset']
    assert source['asset']['sha256'] == SHA
    world = decode_original_world_triangles(asset.read_bytes()); assert world.shape == (456, 3, 3)
    body = prior['bodies'][1091]
    assert body['actorUID'] == UID and len(body['actorLocalFaces']) == 363
    mainfaces = body['actorLocalFaces']
    helper_names = ['xl-owned-indexed-terrain-continuation.py', 'xl-second-pass.py',
        'exact_packed_world_geometry_20261009.py', 'exact_original_face_conservative_clearance_v5_20261010.py',
        'exact_original_paired_finite_clearance_v3_20261011.py', 'exact_original_paired_finite_clearance_v2_20261010.py',
        'exact_original_paired_finite_clearance_20261010.py', 'exact_original_triangle_pair_column_gap_20261010.py',
        'exact_original_projection_coverage_v2_20261010.py', 'exact_original_projection_coverage_20261009.py',
        'exact_original_closed_projection_intersection_20261010.py', 'original_bound_facet_wall_context_v3_20261010.py',
        'original_bound_facet_wall_context_v2_20261010.py', 'original_bound_facet_wall_context_20261010.py',
        'original_strict_clear_cap_wall_paths_20261009.py', 'exact_original_upper_ground_interfaces_20261009.py',
        'exact_original_component_contacts_20261009.py', 'exact_original_shell_intersections_20261009.py',
        'xl-popcorn-source-investigations-checkpoints-20261009.py']
    refs = [ref(Path(__file__)), ref(CROSS / 'result.json'), ref(CROSS / 'diagnostic.json.gz'), ref(asset)]
    refs.extend(ref(HERE / n) for n in helper_names)
    refs.extend(ref(OLD / n) for n in ['result.json', 'foundation.json', 'metrics.json', 'terrain.json', 'terrain-candidates.json'])
    assert all(ref(ROOT / r['path']) == r for r in receipt['evidenceRefs'])
    terrain = module('twin_original_terrain', helper_names[0])
    folder, terrain_receipt = terrain.terrain_sheet('6-NW-10A', LOCAL)
    decoder = module('twin_original_tin_decoder', helper_names[1])
    whole = np.concatenate([decoder.terrain_triangles(folder / 'terrain' / r['name'])
        for r in terrain_receipt['terrainFiles'] if r['name'].endswith('.gltf')])
    assert whole.ndim == 3 and whole.shape[1:] == (3, 3) and np.isfinite(whole).all()
    lo, hi = world.min((0, 1)), world.max((0, 1))
    keep = ((whole[:, :, 0].max(1) >= lo[0]) & (whole[:, :, 0].min(1) <= hi[0]) &
            (whole[:, :, 2].max(1) >= lo[2]) & (whole[:, :, 2].min(1) <= hi[2]))
    ground = whole[keep]; assert len(ground) and np.isfinite(ground).all()
    groundfile = LOCAL / 'complete-authentic-source-tin-ground.json.gz'
    save(groundfile, dict(sourceTerrainReceipt=terrain_receipt, completeOriginalSheetFacets=len(whole),
        completeOriginalSheetFacetSHA256=digest(whole.tobytes()), sourceCoveringWholeFacetIds=np.flatnonzero(keep).tolist(),
        completeSelectedFacets=ground.tolist(), completeSelectedFacetSHA256=digest(ground.tobytes()),
        wholeOriginalSourceBounds=[lo.tolist(), hi.tolist()], currentRendererGround=False,
        finiteSelection='Every whole original facet whose inclusive closed AABB intersects whole source projection; no clipping, slope/height filtering, resampling or height edits.'))
    refs.extend(ref(p) for p in [groundfile, folder / 'original/download.json', folder / 'directory/result.json',
        *[folder / 'terrain' / r['name'] for r in terrain_receipt['terrainFiles']]])
    claim = reservations.claim('twin-original-podium-finite-' + str(uuid.uuid4()),
        ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok']; lease = claim['reservation']; last = time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic() - last >= 20:
            assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease)
            last = time.monotonic()
    try:
        binding = dict(completeOriginalWorldTrianglesSHA256=digest(world.tobytes()),
            completeDrawnGroundSHA256=digest(ground.tobytes()), producer=ref(Path(__file__)), kernels=[ref(HERE / n) for n in helper_names])
        checkpoint = LOCAL / 'complete456-finite-progress.json.gz'
        saved = read(checkpoint) if checkpoint.exists() else None
        assert saved is None or saved['binding'] == binding
        rows = [] if saved is None else saved['rows']
        assert [r['sourceFace'] for r in rows] == list(range(len(rows)))
        pulse(True)
        for i in range(len(rows), 456):
            coarse = coarse_verify(world[i], ground)
            paired = None if coarse['existingOrdinaryClearanceBoundProved'] else paired_verify(world[i], ground)
            selected = coarse if paired is None else paired
            rows.append(dict(sourceFace=i, priorCoarseBoundProofVerbatim=dict(sourceFace=i, completeOriginal=coarse),
                pairedExactOriginalFiniteBound=paired, completeOriginalBoundProved=selected['existingOrdinaryClearanceBoundProved']))
            pulse()
            if i % 25 == 0:
                save(checkpoint, dict(binding=binding, rows=rows, complete=False))
                print(dict(completedFaces=len(rows), total=456), flush=True)
        save(checkpoint, dict(binding=binding, rows=rows, complete=True))
        cb = dict(completeOriginalWorldTrianglesSHA256=digest(world.tobytes()),
            completeDrawnGroundSHA256=digest(ground.tobytes()), completeFiniteFacetProofRowsSHA256=canonical(rows))
        ctx = contexts(world, ground, rows, expected_binding=cb, current_binding=cb); pulse(True)
        capbinding = dict(completeOriginalWorldTrianglesSHA256=digest(world.tobytes()),
            completeCurrentFacetContextsSHA256=canonical(ctx), exactOriginalContactListSHA256=canonical([]))
        caps = cap_verify(world, ctx, [], expected_binding=capbinding, current_binding=capbinding); pulse(True)
        grade = exact_upper_ground_interfaces(world, mainfaces, ground); pulse(True)
        assert len(rows) == len(ctx) == 456 and all(ref(ROOT / r['path']) == r for r in refs)
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                             (receipt['jobId'],)).fetchone() == ('complete', receipt)
        result = dict(uids=[UID], sourceSHA256=SHA, completeOriginalFaces=456,
            completeOriginalWorldSHA256=digest(world.tobytes()), completeAuthenticGroundSHA256=digest(ground.tobytes()),
            complete456FacetProofRows=rows, complete456FacetContexts=ctx, complete363MainBodyFaces=mainfaces,
            completeMainBodyOriginalGradeInterfaces=grade, strictClearCapWallPaths=caps,
            unprovedOriginalFaces=[r['sourceFace'] for r in rows if not r['completeOriginalBoundProved']],
            rawOrdinaryBelowHalfMetreFaces=[i for i, c in enumerate(ctx) if c['minimum']['minimumGapM'] < -.5],
            wholeOriginalSheetFacets=len(whole), completeRelevantOriginalTerrainFacets=len(ground),
            authenticProviderTINUnaltered=True, currentRendererGround=False, historicalPackedCandidateNotUsedAsAuthenticSource=True,
            historicalFailuresRetained=True, mainBodyNotAcceptedRootSeed=True, sourceOnly=True,
            noFreshCurrentOrFourArithmeticQualification=True, currentAcceptance=False,
            structuralRootOrBridgeCredit=False, nativeReacceptance=False, sourceGeometryChanges=0,
            terrainProposalCreated=False, newlyInstalled=0, evidenceRefs=refs)
        save(DOC / 'diagnostic.json.gz', result)
        freeze = module('twin_finite_grade_freeze', helper_names[-1])
        freeze.freeze(BATCH, 'complete456-original-podium-authentic-tin-finite-grade-cap-source-only-v1',
            [ROOT / r['path'] for r in refs] + [DOC / 'diagnostic.json.gz', checkpoint],
            dict(uids=[UID], completeOriginalFaces=456, mainBodyOriginalFaces=363,
                unprovedFaces=len(result['unprovedOriginalFaces']), genuineGradeInterfaces=len(grade),
                allAffectedWallsHaveCapPaths=caps['allAffectedHavePaths'], sourceOnly=True, currentAcceptance=False, newlyInstalled=0))
        print(dict(unproved=result['unprovedOriginalFaces'], gradeInterfaces=len(grade), capPaths=caps['allAffectedHavePaths']), flush=True)
    finally:
        assert reservations.release(lease)['ok']
if __name__ == '__main__': main()
