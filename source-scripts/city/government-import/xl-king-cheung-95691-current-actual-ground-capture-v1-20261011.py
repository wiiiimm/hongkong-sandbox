"""Fresh complete actual source/four arithmetic streams/drawn-ground input only."""
import importlib.util, json, subprocess, uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from king_cheung_current_ancillary_identity_20261011 import UID, SOURCE_SHA, RAW
INPUT = RAW.parent / 'government-xl-king-cheung-95691-current-ancillary-identity-v1-20261011'
BATCH = 'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'; DOC = RAW.parent / BATCH
JS = HERE / 'xl-king-cheung-95691-current-actual-ground-geometry-v1-20261011.mjs'
def main():
    assert not DOC.exists(); receipt = read(INPUT / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    for pin in receipt['evidenceRefs']: assert digest((ROOT / pin['path']).read_bytes()) == pin['sha256']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; before = manifest.read_bytes()
    assert before == (INPUT / 'captured-manifest.json').read_bytes()
    claim = reservations.claim('king-cheung-actual-current-ground-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH, ttl=3600); assert claim['ok']; lease = claim['reservation']
    try:
        DOC.mkdir(parents=True)
        row = read(INPUT / 'selection.json.gz')['rows'][0]
        asset = ROOT / row['candidate']['path']; assert digest(asset.read_bytes()) == SOURCE_SHA
        position_proof = packed_world_bounds(asset.read_bytes())
        save(DOC / 'whole-original-position-proof.json', position_proof)
        process = subprocess.run(['node', str(JS)], cwd=ROOT, capture_output=True, text=True)
        save(DOC / 'export-log.json', dict(exitCode=process.returncode, stdout=process.stdout, stderr=process.stderr))
        assert process.returncode == 0, process.stderr
        capture = read(DOC / 'complete-current-actual-source-and-ground.json.gz')
        assert capture['uid'] == UID and capture['sourceSHA256'] == SOURCE_SHA and capture['completeFaces'] == 18742 and capture['startAndEndInputsVerified']
        assert capture['completeOriginalPOSITIONProof'] == position_proof and digest(asset.read_bytes()) == SOURCE_SHA
        original = decode_original_world_triangles(asset.read_bytes()); index = np.asarray(capture['completeOriginalIndex'], int).reshape(-1, 3)
        streams = {'providerOriginal': original}
        for mode, key in [('actualLiteral', 'completeLiteralWorldPosition'), ('explicitLeftAssociatedF32ModelMatrix', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('explicitBalancedF32ModelMatrix', 'completeExplicitBalancedFloat32WorldPosition')]: streams[mode] = np.asarray(capture[key], dtype='<f8').reshape(-1, 3)[index]
        assert all(w.shape == (18742, 3, 3) and np.isfinite(w).all() for w in streams.values())
        ground = np.asarray(capture['currentDrawnGround']['completeRegionalPosition'], dtype='<f8').reshape(-1, 3, 3)
        assert len(ground) == capture['currentDrawnGround']['completeRegionalFaces'] and digest(ground.tobytes()) == capture['currentDrawnGround']['worldTriangleSHA256'] and np.isfinite(ground).all()
        save(DOC / 'complete-four-stream-ground-inputs.json.gz', dict(uid=UID, sourceSHA256=SOURCE_SHA, completeOriginalFaces=18742,
             completeWorldStreams={mode: dict(completeFaces=len(world), completeWorldTriangleSHA256=digest(world.astype('<f8').tobytes()), completeWorldTriangles=world.tolist()) for mode, world in streams.items()},
             completeDrawnGround=ground.tolist(), completeDrawnGroundSHA256=digest(ground.tobytes()), canopyPost43StillIsolated=True,
             noOriginalSourceEdits=True, noTerrainChanges=True, physicalAccepted=False, installationApproved=False))
        assert manifest.read_bytes() == before and reservations.owns(lease)
        for path, sha in capture['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
        refs = [Path(__file__), JS, INPUT / 'result.json', INPUT / 'selection.json.gz', INPUT / 'context.json.gz', INPUT / 'identity.json',
                HERE / 'king_cheung_current_ancillary_identity_20261011.py', HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_packed_world_bounds_v3_20261010.py',
                *[ROOT / p for p in capture['inputHashes']], DOC / 'whole-original-position-proof.json', DOC / 'export-log.json', DOC / 'complete-current-actual-source-and-ground.json.gz', DOC / 'complete-four-stream-ground-inputs.json.gz']
        s = importlib.util.spec_from_file_location('king_actual_ground_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py'); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
        r = m.freeze(BATCH, 'complete-current-actual-source-four-stream-and-drawn-ground-capture-no-support-credit', refs,
            dict(uids=[UID], completeFaces=18742, completeCurrentGroundFaces=len(ground), sourceGeometryChanges=0, terrainGeometryChanges=0, currentAcceptance=False, newlyInstalled=0))
        print(json.dumps(dict(jobId=r['jobId'], completeGroundFaces=len(ground), physicalAccepted=False)), flush=True)
    finally: assert reservations.release(lease)['ok']
if __name__ == '__main__': main()
