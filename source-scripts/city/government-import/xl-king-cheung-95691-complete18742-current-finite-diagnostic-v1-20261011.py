"""Check all18742 unchanged source facets against complete actual current drawn ground.

All18742/four streams and finite projection remain complete.
Raw whole-facet negatives remain; no typed support or installation credit.
"""
import importlib.util, json, sys, uuid, subprocess
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID, SOURCE_SHA, ROLE_IDS, PART_FACES
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE = ROOT / 'docs/astra-city/government-import'
INPUT = BASE / 'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
TIN = BASE / 'government-xl-king-cheung-95691-authentic-tin-source-context-v1-20261011'
GRADE = BASE / 'government-xl-king-cheung-95691-canopy-current-grade-cause-v1-20261011'
BATCH = 'government-xl-king-cheung-95691-complete18742-current-finite-diagnostic-v1-20261011'
DOC = BASE / BATCH; LOCAL = HERE / 'local' / BATCH; LEASE = LOCAL / 'reservation.json'
def owned():
    lease = read(LEASE); assert reservations.owns(lease) and not DOC.exists()
    refs = [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [INPUT, GRADE]:
            r = read(folder / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (r['jobId'],)).fetchone() == ('complete', r)
            refs.append(folder / 'result.json')
            for pin in r['evidenceRefs']:
                p = ROOT / pin['path']; assert digest(p.read_bytes()) == pin['sha256']; refs.append(p)
    capture = read(INPUT / 'complete-current-actual-source-and-ground.json.gz')
    data = read(INPUT / 'complete-four-stream-ground-inputs.json.gz')
    prior = read(GRADE / 'diagnostic.json.gz')
    assert data['uid'] == UID and data['sourceSHA256'] == SOURCE_SHA
    grounds = dict(currentDrawn=np.asarray(data['completeDrawnGround'], dtype='<f8'))
    assert digest(grounds['currentDrawn'].tobytes()) == data['completeDrawnGroundSHA256']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; before = manifest.read_bytes()
    assert digest(before) == capture['inputHashes']['3d-viewer/city/data/manifest.json']
    rows = []; cache = {}
    for mode, stream in data['completeWorldStreams'].items():
        world = np.asarray(stream['completeWorldTriangles'], dtype='<f8')
        assert world.shape == (18742, 3, 3) and digest(world.tobytes()) == stream['completeWorldTriangleSHA256']
        old = next(r for r in prior['rows'] if r['arithmetic'] == mode)
        faces = []
        for face_id in range(18742):
            comparisons = {}
            for kind, ground in grounds.items():
                key = (digest(world[face_id].tobytes()), digest(ground.tobytes()))
                if key not in cache:
                    a = coarse(world[face_id], ground)
                    b = None if a['existingOrdinaryClearanceBoundProved'] else paired(world[face_id], ground)
                    cache[key] = dict(coarse=a, paired=b, completeFiniteOrdinaryBoundProved=a['existingOrdinaryClearanceBoundProved'] or bool(b and b['existingOrdinaryClearanceBoundProved']))
                comparisons[kind] = cache[key]
            original = next((f for f in old['complete104FaceInventory'] if f['originalSourceFace'] == face_id),None)
            if original is not None: assert comparisons['currentDrawn']['completeFiniteOrdinaryBoundProved'] == original['rawOrdinaryFiniteBoundProved']
            face=world[face_id];normal=np.cross(face[1]-face[0],face[2]-face[0]);length=np.linalg.norm(normal)
            ratio=float(normal[1]/length)if length else None
            orientation='collapsed'if ratio is None else 'steep-wall'if abs(ratio)<=.25 else 'upward'if ratio>0 else 'downward'
            faces.append(dict(sourceFace=face_id,orientationDiagnostic=orientation,wholeOriginalYRangeHKPD=[float(face[:,1].min()),float(face[:,1].max())],groundComparisons=comparisons))
            if face_id%1000==0:print(json.dumps(dict(arithmetic=mode,completedSourceFaces=face_id)),flush=True)
        rows.append(dict(arithmetic=mode, completeWholeWorldSHA256=stream['completeWorldTriangleSHA256'], complete18742FaceComparisons=faces,
                         failedFacesByGround={kind: [f['sourceFace'] for f in faces if not f['groundComparisons'][kind]['completeFiniteOrdinaryBoundProved']] for kind in grounds},
                         currentRawFailuresRetained=True, currentGroundRootAccepted=False))
        print(json.dumps(dict(arithmetic=mode, failures=rows[-1]['failedFacesByGround'])), flush=True)
    save(DOC / 'diagnostic.json.gz', dict(uids=[UID], sourceSHA256=SOURCE_SHA, rows=rows,
         completeGrounds={kind: dict(completeFaces=len(g), completeWorldSHA256=digest(g.tobytes()), wholeGroundYRangeHKPD=[float(g[:,:,1].min()),float(g[:,:,1].max())]) for kind,g in grounds.items()},
         terrainReplacementProposed=False,
         noBelowGradeFoundationExposureAssumption=True, geometryChanges=0, currentAcceptance=False, physicalAccepted=False, installationApproved=False))
    assert reservations.owns(lease) and manifest.read_bytes() == before
    for path, sha in capture['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
    refs += [HERE / n for n in ['king_cheung_complete_ancillary_proposal_20261011.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_projection_coverage_v2_20261010.py']]
    s=importlib.util.spec_from_file_location('king_tin_compare_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'); m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    r=m.freeze(BATCH,'complete18742-four-stream-current-finite-diagnostic-no-role-or-installation-credit',refs+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeWholeSourceFaces=18742,currentAcceptance=False,newlyInstalled=0))
    print(json.dumps(dict(jobId=r['jobId'])),flush=True)
def main():
    if '--owned' in sys.argv: return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim=reservations.claim('king-cheung-whole-source-current-finite-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok']
    save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
