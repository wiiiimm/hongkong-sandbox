"""Authenticate3-SW-11B source terrain, no replacement or current-ground credit.

Keep complete original sheet hashes/poses and every whole facet nominated by
the union of complete original/literal/twoF32 source POSITION bounds. No slope
filter, clipping, interpolation, height adjustment or building edit is applied.
"""
import importlib.util, json, sys, uuid, subprocess
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID, SOURCE_SHA
BASE = ROOT / 'docs/astra-city/government-import'
INPUT = BASE / 'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
RAW = BASE / 'government-xl-king-cheung-95691-current-original-identity-v1-20261011'
BATCH = 'government-xl-king-cheung-95691-authentic-tin-source-context-v1-20261011'; DOC = BASE / BATCH; LOCAL = HERE / 'local' / BATCH; LEASE = LOCAL / 'reservation.json'
def module(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def owned():
    lease = read(LEASE); assert reservations.owns(lease) and not DOC.exists()
    refs = [Path(__file__), INPUT / 'result.json', INPUT / 'complete-current-actual-source-and-ground.json.gz', RAW / 'indexed-diagnostic.json']
    receipt = read(INPUT / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    for pin in receipt['evidenceRefs']:
        p = ROOT / pin['path']; assert digest(p.read_bytes()) == pin['sha256']; refs.append(p)
    capture = read(INPUT / 'complete-current-actual-source-and-ground.json.gz')
    assert capture['uid'] == UID and capture['sourceSHA256'] == SOURCE_SHA
    routing = read(RAW / 'indexed-diagnostic.json'); assert routing['primarySheet'] == '3-SW-11B' and routing['adjacentSheets'] == []
    index = module('king_authentic_tin_recovery', HERE / 'xl-owned-indexed-terrain-continuation.py')
    folder, terrain_receipt = index.terrain_sheet('3-SW-11B', LOCAL)
    verified = index.verified_terrain(folder); assert verified and terrain_receipt['sheet'] == '3-SW-11B'
    original_receipt, files = verified
    assert original_receipt['directorySHA256'] == terrain_receipt['directorySHA256']
    decoder = module('king_authentic_tin_decoder', HERE / 'xl-second-pass.py'); decoder.LOCAL = LOCAL
    pieces = []
    for record in files:
        path = folder / 'terrain' / record['name']; raw = path.read_bytes()
        assert len(raw) == record['bytes'] and digest(raw) == record['sha256']; refs.append(path)
        if path.suffix == '.gltf': pieces.append(decoder.terrain_triangles(path))
    assert pieces
    whole = np.concatenate(pieces); assert whole.ndim == 3 and whole.shape[1:] == (3, 3) and len(whole) > 0 and np.isfinite(whole).all()
    bounds = np.asarray([capture['completeOriginalPOSITIONProof']['originalWholeSourceBounds'], *capture['completeWholeUnusedVertexBounds']], dtype='<f8')
    assert bounds.shape == (4, 2, 3) and np.isfinite(bounds).all()
    low, high = bounds[:, 0].min(0), bounds[:, 1].max(0)
    keep = (whole[:, :, 0].max(1) >= low[0]) & (whole[:, :, 0].min(1) <= high[0]) & (whole[:, :, 2].max(1) >= low[2]) & (whole[:, :, 2].min(1) <= high[2])
    ground = whole[keep]; assert len(ground) > 0
    save(DOC / 'complete-authentic-source-tin-ground.json.gz', dict(uids=[UID], sourceSHA256=SOURCE_SHA, sourceTerrainReceipt=terrain_receipt,
         completeOriginalSheetFacets=len(whole), completeOriginalSheetFacetSHA256=digest(whole.tobytes()),
         everySelectedOriginalFacetId=np.flatnonzero(keep).tolist(), completeSelectedFacets=ground.tolist(), completeSelectedFacetSHA256=digest(ground.tobytes()),
         completeAllFourPOSITIONBounds=bounds.tolist(), sourceBoundsUnion=[low.tolist(), high.tolist()],
         closedAABBWholeFacetSelection=True, zeroProjectionAndAllSlopesRetained=True, sourceOnly=True,
         currentRendererGround=False, terrainReplacementProposed=False, sourceGeometryChanges=0, currentGroundRootAccepted=False,
         physicalAccepted=False, installationApproved=False))
    refs += [folder / 'original/download.json', folder / 'directory/result.json', HERE / 'xl-owned-indexed-terrain-continuation.py', HERE / 'xl-second-pass.py',
             HERE / 'king_cheung_complete_ancillary_proposal_20261011.py', DOC / 'complete-authentic-source-tin-ground.json.gz']
    refs += [p for p in (LOCAL / 'terrain-repairs').rglob('*') if p.is_file()] if (LOCAL / 'terrain-repairs').exists() else []
    assert reservations.owns(lease)
    for pin in receipt['evidenceRefs']: assert digest((ROOT / pin['path']).read_bytes()) == pin['sha256']
    result = module('king_authentic_tin_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,
        'authenticated-original3SW11B-complete-source-terrain-context-no-current-ground-replacement-credit', refs,
        dict(uids=[UID], completeOriginalSheetFacets=len(whole), completeRelevantFacets=len(ground), sourceOnly=True,
             terrainReplacementProposed=False, currentAcceptance=False, newlyInstalled=0))
    print(json.dumps(dict(jobId=result['jobId'], completeSheetFacets=len(whole), selectedFacets=len(ground), transferredBytes=terrain_receipt['transferredBytes'])), flush=True)
def main():
    if '--owned' in sys.argv: return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('king-cheung-authentic-tin-context-' + str(uuid.uuid4()), ['building:' + UID, 'immutable-source-sheet:3-SW-11B'], batch=BATCH, ttl=3600); assert claim['ok']
    save(LEASE, json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(LEASE), '--ttl', '3600', '--', sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
if __name__ == '__main__': main()
