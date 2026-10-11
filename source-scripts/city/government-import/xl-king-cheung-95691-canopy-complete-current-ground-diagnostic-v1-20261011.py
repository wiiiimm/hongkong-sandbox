"""Complete104 canopy faces/current finite ground and independent part footings.

All four complete source arithmetic streams remain distinct. This bounded
diagnostic never approves the remaining18638 faces, terrain, runtime or import.
Every negative survives, including isolated43 and no canopy/mainbody contact.
"""
import importlib.util, json, subprocess, time, sys, uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID, SOURCE_SHA, PART_FACES, ROLE_IDS
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE = ROOT / 'docs/astra-city/government-import'
INPUT = BASE / 'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
IDENTITY = BASE / 'government-xl-king-cheung-95691-current-ancillary-identity-v1-20261011'
BATCH = 'government-xl-king-cheung-95691-canopy-complete-current-ground-diagnostic-v1-20261011'; DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH; LEASE = LOCAL / 'reservation.json'
def owned():
    lease = read(LEASE); assert reservations.owns(lease)
    assert not DOC.exists(); refs = [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [INPUT, IDENTITY]:
            r = read(folder / 'result.json'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (r['jobId'],)).fetchone() == ('complete', r)
            refs.append(folder / 'result.json')
            for pin in r['evidenceRefs']:
                p = ROOT / pin['path']; assert digest(p.read_bytes()) == pin['sha256']; refs.append(p)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; before = manifest.read_bytes()
    assert before == (IDENTITY / 'captured-manifest.json').read_bytes()
    capture = read(INPUT / 'complete-current-actual-source-and-ground.json.gz')
    data = read(INPUT / 'complete-four-stream-ground-inputs.json.gz')
    assert data['uid'] == UID and data['sourceSHA256'] == SOURCE_SHA and data['completeOriginalFaces'] == 18742
    assert set(data['completeWorldStreams']) == {'providerOriginal', 'actualLiteral', 'explicitLeftAssociatedF32ModelMatrix', 'explicitBalancedF32ModelMatrix'}
    ground = np.asarray(data['completeDrawnGround'], dtype='<f8')
    assert ground.ndim == 3 and ground.shape[1:] == (3, 3) and len(ground) > 0 and digest(ground.tobytes()) == data['completeDrawnGroundSHA256']
    results = []; face_cache = {}; clock = time.monotonic()
    for mode, stream in data['completeWorldStreams'].items():
        world = np.asarray(stream['completeWorldTriangles'], dtype='<f8')
        assert world.shape == (18742, 3, 3) and np.isfinite(world).all() and digest(world.tobytes()) == stream['completeWorldTriangleSHA256']
        faces = []
        for i in ROLE_IDS:
            face = world[i]; key = digest(face.tobytes())
            if key not in face_cache:
                first = coarse(face, ground); second = None if first['existingOrdinaryClearanceBoundProved'] else paired(face, ground)
                face_cache[key] = dict(coarse=first, paired=second, completeFiniteOrdinaryBoundProved=first['existingOrdinaryClearanceBoundProved'] or bool(second and second['existingOrdinaryClearanceBoundProved']))
            faces.append(dict(sourceFace=i, **face_cache[key]))
            if time.monotonic() - clock > 20:
                print(json.dumps(dict(arithmetic=mode, completedRoleFace=i, totalRoleFaces=104)), flush=True); clock = time.monotonic()
        parts = []
        for component, ids in PART_FACES.items():
            part = world[ids]; path = DOC / (mode + '-part-' + str(component) + '-strict-footing-input.json.gz')
            save(path, dict(part=dict(component=component, originalFaceIds=ids, position=part.reshape(-1).tolist(), index=list(range(part.size // 3)), bottomHKPD=float(part[:, :, 1].min())),
                            terrain=dict(position=ground.reshape(-1).tolist(), index=list(range(ground.size // 3))), arithmetic=mode, physicalAccepted=False))
            process = subprocess.run(['node', str(HERE / 'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs'), str(path)], cwd=ROOT, capture_output=True, text=True)
            save(DOC / (mode + '-part-' + str(component) + '-strict-footing-log.json'), dict(exitCode=process.returncode, stdout=process.stdout, stderr=process.stderr))
            assert process.returncode == 0, process.stderr
            footing = json.loads(process.stdout)
            part_ids = set(ids); other_ids = [i for i in range(18742) if i not in part_ids]
            contacts = exact_finite_contacts(world, ids, world, other_ids)
            assert contacts['allPairsExamined'] and contacts['sourceFacesOmitted'] == 0
            parts.append(dict(component=component, completeOriginalFaceIds=ids, completeWorldPartBounds=[part.min((0, 1)).tolist(), part.max((0, 1)).tolist()],
                              unchangedStrictWholePartFooting=footing, completeAllOtherOriginalPrimitiveContacts=contacts,
                              ordinaryGroundRootProposed=footing['passed'], structuralSupportAccepted=False))
        results.append(dict(arithmetic=mode, completeWholeSourceFaces=18742, completeWorldSHA256=stream['completeWorldTriangleSHA256'], completeCanopyFaces=104,
                            completeCanopyFaceChecks=faces, unprovedCanopyFiniteFaceIds=[f['sourceFace'] for f in faces if not f['completeFiniteOrdinaryBoundProved']],
                            completeCanopyParts=parts, ordinaryRootPassedParts=[p['component'] for p in parts if p['unchangedStrictWholePartFooting']['passed']],
                            rawFootingFailedParts=[p['component'] for p in parts if not p['unchangedStrictWholePartFooting']['passed']]))
    save(DOC / 'diagnostic.json.gz', dict(uids=[UID], sourceSHA256=SOURCE_SHA, rows=results, completeDrawnGroundSHA256=data['completeDrawnGroundSHA256'],
         completeDrawnGroundFaces=len(ground), all104FacesAccountedEachArithmetic=True, remaining18638OrdinaryFacesNotCertifiedByThisDiagnostic=True,
         canopyIdentityIsNotGroundingCredit=True, sourceGeometryChanges=0, terrainGeometryChanges=0, sourceOnly=True,
         currentAcceptance=False, physicalAccepted=False, structuralSupportAccepted=False, runtimeApproved=False, installationApproved=False))
    assert manifest.read_bytes() == before and reservations.owns(lease)
    for path, sha in capture['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
    refs += [INPUT / 'complete-four-stream-ground-inputs.json.gz', INPUT / 'complete-current-actual-source-and-ground.json.gz', manifest]
    refs += [HERE / name for name in ['king_cheung_complete_ancillary_proposal_20261011.py', 'exact_original_face_conservative_clearance_v5_20261010.py',
        'exact_original_projection_coverage_v2_20261010.py', 'exact_original_paired_finite_clearance_20261010.py', 'exact_original_projection_coverage_20261009.py',
        'exact_original_closed_projection_intersection_20261010.py', 'exact_original_finite_triangle_contacts_20261010.py', 'exact_original_shared_edge_component_census_v2_20261011.py',
        'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs', 'support-interface.mjs', 'support-contact.mjs', 'triangle-point-index.mjs']]
    refs += [p for p in DOC.rglob('*') if p.is_file()]
    s = importlib.util.spec_from_file_location('king_canopy_ground_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py'); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    r = m.freeze(BATCH, 'complete104-four-stream-current-finite-and-independent-freestanding-whole-part-footing-diagnostic', refs,
        dict(uids=[UID], completeRoleFaces=104, rawFootingFailedParts={r['arithmetic']: r['rawFootingFailedParts'] for r in results},
             unprovedCanopyFiniteFaceIds={r['arithmetic']: r['unprovedCanopyFiniteFaceIds'] for r in results}, currentAcceptance=False, newlyInstalled=0))
    print(json.dumps(dict(jobId=r['jobId'], rows=[dict(arithmetic=r['arithmetic'], unproved=r['unprovedCanopyFiniteFaceIds'], roots=r['ordinaryRootPassedParts']) for r in results])), flush=True)
def main():
    if '--owned' in sys.argv: return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('king-cheung-canopy-current-ground-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH, ttl=3600)
    assert claim['ok']; save(LEASE, json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LEASE), '--ttl', '3600', '--', sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
if __name__ == '__main__': main()
