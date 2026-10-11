"""Attribute all68 raw canopy failures before any terrain replacement proposal.

Complete104 facets, orientations, finite clearance/exposure, actual grade and
unchanged strict cap paths remain independently bound in all four streams.
An assertion in the strict wall route stays an explicit negative, not a waiver.
"""
import importlib.util, json, sys, uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID, SOURCE_SHA, ROLE_IDS, PART_FACES
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_bound_facet_wall_context_20261010 import canonical
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE = ROOT / 'docs/astra-city/government-import'
GROUND = BASE / 'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
FINITE = BASE / 'government-xl-king-cheung-95691-canopy-complete-current-ground-diagnostic-v1-20261011'
BATCH = 'government-xl-king-cheung-95691-canopy-current-grade-cause-v1-20261011'; DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH; LEASE = LOCAL / 'reservation.json'
def owned():
    lease = read(LEASE); assert reservations.owns(lease) and not DOC.exists()
    refs = [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [GROUND, FINITE]:
            r = read(folder / 'result.json'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (r['jobId'],)).fetchone() == ('complete', r)
            refs.append(folder / 'result.json')
            for pin in r['evidenceRefs']:
                p = ROOT / pin['path']; assert digest(p.read_bytes()) == pin['sha256']; refs.append(p)
    data = read(GROUND / 'complete-four-stream-ground-inputs.json.gz'); finite = read(FINITE / 'diagnostic.json.gz')
    ground = np.asarray(data['completeDrawnGround'], dtype='<f8'); assert digest(ground.tobytes()) == data['completeDrawnGroundSHA256']
    capture = read(GROUND / 'complete-current-actual-source-and-ground.json.gz'); manifest = ROOT / '3d-viewer/city/data/manifest.json'; before = manifest.read_bytes()
    assert digest(before) == capture['inputHashes']['3d-viewer/city/data/manifest.json']
    map_component = {i: c for c, ids in PART_FACES.items() for i in ids}; rows = []
    for mode, stream in data['completeWorldStreams'].items():
        world = np.asarray(stream['completeWorldTriangles'], dtype='<f8'); assert digest(world.tobytes()) == stream['completeWorldTriangleSHA256']
        t = world[ROLE_IDS]; previous = next(r for r in finite['rows'] if r['arithmetic'] == mode)
        records = previous['completeCanopyFaceChecks']; assert [r['sourceFace'] for r in records] == ROLE_IDS
        adapted = [dict(sourceFace=i, priorCoarseBoundProofVerbatim=dict(sourceFace=i, completeOriginal=r['coarse']),
                        pairedExactOriginalFiniteBound=r['paired'], completeOriginalBoundProved=r['completeFiniteOrdinaryBoundProved']) for i, r in enumerate(records)]
        binding = dict(completeOriginalWorldTrianglesSHA256=digest(t.tobytes()), completeDrawnGroundSHA256=digest(ground.tobytes()), completeFiniteFacetProofRowsSHA256=canonical(adapted))
        ctx = contexts(t, ground, adapted, expected_binding=binding, current_binding=binding)
        grade = exact_finite_contacts(t, range(104), ground, range(len(ground))); assert grade['allPairsExamined']
        all_interfaces = exact_finite_contacts(t, range(104), t, range(104)); assert all_interfaces['allPairsExamined']
        pairs = sorted({tuple(sorted((c['sourceFaceA'], c['sourceFaceB']))) for c in all_interfaces['contacts']
                        if c['sourceFaceA'] != c['sourceFaceB'] and c['dimension'] > 0 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2})
        normals = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); sizes = np.linalg.norm(normals, axis=1)
        inventory = []
        for i, face_id in enumerate(ROLE_IDS):
            ratio = float(normals[i, 1] / sizes[i]) if sizes[i] else None
            inventory.append(dict(originalSourceFace=face_id, completeSourceComponent=map_component[face_id],
                 completeOriginalFace=t[i].tolist(), unnormalisedFaceNormal=normals[i].tolist(), normalYRatio=ratio,
                 orientationDiagnostic='collapsed' if ratio is None else ('steep-wall' if abs(ratio) <= .25 else ('upward' if ratio > 0 else 'downward')),
                 wholeOriginalFaceYRangeHKPD=[float(t[i, :, 1].min()), float(t[i, :, 1].max())],
                 rawOrdinaryFiniteBoundProved=records[i]['completeFiniteOrdinaryBoundProved'], completeFiniteClearanceAndExposure=ctx[i],
                 completeActualFiniteGradeContacts=[c for c in grade['contacts'] if c['sourceFaceA'] == i], roleAccepted=False))
        path_binding = dict(completeOriginalWorldTrianglesSHA256=digest(t.tobytes()), completeCurrentFacetContextsSHA256=canonical(ctx), exactOriginalContactListSHA256=canonical([list(p) for p in pairs]))
        proof = None; failure = None
        try: proof = cap_paths(t, ctx, [list(p) for p in pairs], expected_binding=path_binding, current_binding=path_binding)
        except AssertionError as error: failure = str(error)
        rows.append(dict(arithmetic=mode, completeWorldSHA256=stream['completeWorldTriangleSHA256'], localFaceToOriginalSourceFace=ROLE_IDS,
             complete104FaceInventory=inventory, completeActualGradeIntersection=grade, complete104PairInterfaces=all_interfaces,
             strictClearCapPathProof=proof, strictClearCapPathRawFailure=failure,
             failingOrientationCounts={name: sum(not r['rawOrdinaryFiniteBoundProved'] and r['orientationDiagnostic'] == name for r in inventory) for name in ['steep-wall', 'upward', 'downward', 'collapsed']},
             independentlyGroundedParts=[], groundRootAccepted=False))
    save(DOC / 'diagnostic.json.gz', dict(uids=[UID], sourceSHA256=SOURCE_SHA, rows=rows, completeDrawnGroundSHA256=digest(ground.tobytes()),
         sourceGeometryChanges=0, terrainReplacementProposed=False, raw68FaceFailuresRetained=True, currentAcceptance=False,
         foundationRoleAccepted=False, buriedVisibleCapWaiver=False, physicalAccepted=False, installationApproved=False))
    assert manifest.read_bytes() == before and reservations.owns(lease)
    for path, sha in capture['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
    refs += [GROUND / 'complete-four-stream-ground-inputs.json.gz', FINITE / 'diagnostic.json.gz', manifest]
    refs += [HERE / name for name in ['king_cheung_complete_ancillary_proposal_20261011.py', 'original_bound_facet_wall_context_v3_20261010.py',
        'original_bound_facet_wall_context_v2_20261010.py', 'original_bound_facet_wall_context_20261010.py', 'original_strict_clear_cap_wall_paths_20261009.py',
        'exact_original_triangle_pair_column_gap_20261010.py', 'exact_original_projection_coverage_v2_20261010.py', 'exact_original_finite_triangle_contacts_20261010.py']]
    s = importlib.util.spec_from_file_location('king_current_grade_cause_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py'); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    r = m.freeze(BATCH, 'complete104-current-grade-orientation-finite-exposure-and-strict-cap-route-cause-no-waiver', refs + [DOC / 'diagnostic.json.gz'],
       dict(uids=[UID], failingOrientationCounts={r['arithmetic']: r['failingOrientationCounts'] for r in rows}, currentAcceptance=False, newlyInstalled=0))
    print(json.dumps(dict(jobId=r['jobId'], rows=[dict(arithmetic=r['arithmetic'], counts=r['failingOrientationCounts'], strictWallFailure=r['strictClearCapPathRawFailure']) for r in rows])), flush=True)
def main():
    if '--owned' in sys.argv: return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('king-cheung-canopy-grade-cause-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH, ttl=3600); assert claim['ok']
    save(LEASE, json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess = __import__('subprocess')
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LEASE), '--ttl', '3600', '--', sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
if __name__ == '__main__': main()
