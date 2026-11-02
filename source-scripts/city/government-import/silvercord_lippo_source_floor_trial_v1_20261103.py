"""Test the existing bounded lower-ground kernel on all original upward negatives.

Only a private captured-ground array is produced. No source modelling, current
terrain replacement, support acceptance or publication is performed.
"""
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v3_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from retained_bounded_floor_work_v1_20261102 import inset

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-silvercord-lippo-current-floor-sequence-v1-20261103'
BATCH = 'government-xl-silvercord-lippo-private-source-floor-trial-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    refs = [Path(__file__), HERE / 'retained_bounded_floor_work_v1_20261102.py',
            HERE / 'source_floor_return_with_existing_seabed_v1_20261102.py',
            HERE / 'bounded_original_upward_floor_return_v1_20261029.py']
    pins = {}
    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    runtime = PREFIX + '-runtime'; selected = take(runtime, BASE / runtime / 'selection.json.gz')
    geometry = take(runtime, HERE / 'local' / runtime / 'runtime-geometry.json.gz')
    assert {r['uid'] for r in selected['rows']} == set(UIDS)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']; refs.append(manifest)
    for path, sha in geometry['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha, path
        refs.append(ROOT / path)
    outcomes = []
    for row in selected['rows']:
        uid = row['uid']; key = uid.split('/')[1].replace(':', '-')
        asset = ROOT / row['candidate']['path']; assert digest(asset.read_bytes()) == row['sourceSHA256']; refs.append(asset)
        original = decode_original_world_triangles(asset.read_bytes()); assert len(original) == row['triangles']
        negative = take(PREFIX + '-low-' + key, BASE / (PREFIX + '-low-' + key) / 'original.json.gz')
        assert negative['sourceWorldSHA256'] == digest(original.astype('<f8').tobytes())
        ids = []
        for entry in negative['rows']:
            face = original[entry['sourceFace']]; assert np.array_equal(face, entry['vertices'])
            normal = np.cross(face[1] - face[0], face[2] - face[0])
            if normal[1] > .25 * np.linalg.norm(normal): ids.append(entry['sourceFace'])
        source = original[ids]
        if not ids:
            outcomes.append(dict(uid=uid, upwardNegativeFaces=[], trialNeeded=False)); continue
        g = next(r for r in geometry['rows'] if r['uid'] == uid)
        ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
        assert digest(ground.tobytes()) == negative['groundSHA256']
        after, proof = inset(ground, source)
        out = BASE / BATCH / key
        save(out / 'private-ground.json.gz', dict(before=ground.tolist(), after=after.tolist(), sourceFaceIndices=ids))
        save(out / 'return-proof.json.gz', proof)
        outcomes.append(dict(uid=uid, upwardNegativeFaces=ids, trialNeeded=True,
                             originalGroundFaces=len(ground), privateGroundFaces=len(after),
                             changedOriginalGroundFaces=proof['changedTerrainFaceIndices'],
                             outsideWorkFacesLiteral=proof['outsideWorkFacesLiteral']))
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selected['manifestSHA256']
    result = dict(uids=UIDS, rows=outcomes, status='private-existing-kernel-return-constructed',
                  privateDerivedGroundOnly=True, sourceGeometryChanges=0, sourcePoseChanges=0,
                  physicalAcceptance=False, retainedParentAcceptance=False, installationApproved=False,
                  next='Bind changed ground faces to complete actual parent terrain and all retained actors, then validate source clearance/support/foreign/runtime before any publication.')
    save(BASE / BATCH / 'summary.json', result)
    module('pair_source_floor_trial_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'private-captured-ground-original-upward-source-floor-return-trial', list(dict.fromkeys(refs)), result)
    print(dict(privateGroundTrialCompleted=True, installationApproved=False), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('pair-source-floor-trial-' + str(uuid.uuid4()),
                                   ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok']
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
