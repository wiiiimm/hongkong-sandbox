"""Diagnostic production-renderer replay of an explicitly unapproved candidate.

This cannot satisfy the validated-patch or installation entry points. It tests
whether the constructed parent renders exactly the proven private floor return.
"""
import copy
import sys
import uuid
import subprocess
from collections import Counter
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103'
CANDIDATE = 'government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'
CAPTURE = 'government-xl-silvercord-lippo-current-floor-sequence-v1-20261103-runtime'
TRIAL = 'government-xl-silvercord-lippo-complete-floor-work-v3-20261103'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def face_key(t): return tuple(sorted(tuple(float(v) for v in p) for p in t))


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    refs = [Path(__file__)]; pins = {}
    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]; refs.append(path); return read(path)
    proposal = take(CANDIDATE, BASE / CANDIDATE / 'summary.json')
    assert proposal['status'] == 'private-coordinated-floor-candidate-assembled' and not proposal['terrainValidatorPassed']
    candidate_path = ROOT / proposal['candidate']['path']; candidate = take(CANDIDATE, candidate_path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; mh = digest(manifest.read_bytes()); refs.append(manifest)
    assert mh == proposal['currentManifestSHA256']
    old = proposal['replacedParent']; path = ROOT / '3d-viewer' / old['url']; assert digest(path.read_bytes()) == old['sha256']; refs.append(path)
    retained = read(path)['meta']['targetUids']; assert set(retained) <= set(candidate['meta']['targetUids'])
    rows = copy.deepcopy(take(CAPTURE, BASE / CAPTURE / 'selection.json.gz')['rows']); assert {r['uid'] for r in rows} == set(UIDS)
    for row in rows:
        path = ROOT / row['candidate']['path']; raw = path.read_bytes(); assert digest(raw) == row['sourceSHA256']; refs.append(path)
        tile = ROOT / '3d-viewer' / row['source']['tile']; assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        assert [f for f in read(tile)['buildings'] if f['uid'] == row['uid']] == [row['source']['building']]; refs.append(tile)
        target = LOCAL / row['candidate']['entry']['asset']; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw); refs.append(target)
        row['candidate']['path'] = str(target.relative_to(ROOT))
    out = BASE / BATCH; selection_path = out / 'selection.json.gz'; save(selection_path, dict(rows=rows, manifestSHA256=mh))
    terrain_path = out / 'unapproved-terrain-diagnostic-input.json'
    north=proposal['additionalTopLevelPatch'];north_path=ROOT/north['path'];assert digest(north_path.read_bytes())==north['sha256'];refs.append(north_path)
    save(terrain_path, [dict(**proposal['candidate'], replaces=dict(url=old['url'], sha256=old['sha256'], retainedUids=retained)),dict(path=north['path'],sha256=north['sha256'])])
    metrics = out / 'metrics.json'; geometry_path = LOCAL / 'runtime-geometry.json.gz'
    tool = HERE / 'acceptance_metrics_multi_retained_v2.mjs'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), '--selection', str(selection_path.relative_to(ROOT)), '--candidates', str(LOCAL.relative_to(ROOT)),
                        '--terrain-candidates', str(terrain_path.relative_to(ROOT)), '--out', str(metrics.relative_to(ROOT)),
                        '--geometry-out', str(geometry_path.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=3600, check=True)
    actual = read(geometry_path); refs.extend([tool, geometry_path])
    for path, sha in actual['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha; refs.append(ROOT / path)
    trial = take(TRIAL, BASE / TRIAL / '231645-0/private-ground.json.gz')
    row = next(r for r in rows if r['uid'] == 'landsd/231645:0')
    expected = np.asarray(trial['after'], dtype='<f4').astype('<f8'); bounds = np.asarray(row['candidate']['entry']['worldBounds'])
    xz = expected[:, :, [0, 2]]; lo, hi = bounds[0, [0, 2]]-1, bounds[1, [0, 2]]+1
    expected = expected[np.all(xz.max(1) >= lo, axis=1) & np.all(xz.min(1) <= hi, axis=1)]
    drawn = np.asarray(next(r for r in actual['rows'] if r['uid'] == row['uid'])['drawnGroundGeometry']).reshape(-1, 3, 3)
    expected_keys=Counter(map(face_key, expected));drawn_keys=Counter(map(face_key, drawn))
    equal=all(drawn_keys[k]==n for k,n in expected_keys.items())
    complete_before=take(CAPTURE, HERE/'local'/CAPTURE/'runtime-geometry.json.gz');old_drawn=np.asarray(next(r for r in complete_before['rows']if r['uid']==row['uid'])['drawnGroundGeometry']).reshape(-1,3,3)
    old_keys=Counter(map(face_key,old_drawn));work_before=Counter(map(face_key,np.asarray(trial['before'],dtype='<f4').astype('<f8')))
    outside=old_keys-work_before
    equal=equal and drawn_keys==outside+expected_keys
    assert equal,'Full current model-ground multiset differs from literal outside plus complete return'
    save(out / 'actual-floor-return-readback.json', dict(exactWholeRenderedFaceMultisetMatchesPrivateTrial=equal,
                                                      expectedFaces=len(expected), actualFaces=len(drawn), installationApproved=False))
    final = module('private_pair_floor_foundations', HERE / 'xl-final-script-pass.py'); results = []
    for row in rows:
        g = next(r for r in actual['rows'] if r['uid'] == row['uid']); assert g['sourceSHA256'] == row['sourceSHA256']
        tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
        ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3); b = row['source']['building']
        foundation = final.foundation_context(tri, ground, Polygon(b['rings'][0], b['rings'][1:]))
        save(out / (row['uid'].split('/')[1] + '.json'), dict(uid=row['uid'], foundation=foundation))
        results.append(dict(uid=row['uid'], **{k: foundation[k] for k in ['fullyBuriedTriangles', 'fullyBuriedUpwardTriangles', 'minimumGapM']}))
    result = dict(uids=UIDS, rows=results, exactWholeRenderedFaceMultisetMatchesPrivateTrial=equal,
                  currentManifestSHA256=mh, unapprovedTerrainDiagnosticOnly=True, terrainValidatorPassed=False,
                  physicalAcceptance=False, installationApproved=False, publication=False, sourceGeometryChanges=0,
                  next='Use actual renderer readback and full affected actor regressions to validate the complete coordinated graph; this diagnostic does not replace canonical terrain validation or installation gates.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == mh
    module('private_pair_floor_runtime_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'explicit-unapproved-coordinated-parent-production-renderer-diagnostic', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv: owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        old = read(BASE / CANDIDATE / 'summary.json')['replacedParent']; parent = read(ROOT / '3d-viewer' / old['url'])
        keys = {'building:'+u for u in parent['meta']['targetUids']+UIDS} | {'terrain:'+old['url'], 'immutable-source-proof:'+BATCH}
        claim = reservations.claim('private-pair-floor-runtime-' + str(uuid.uuid4()), sorted(keys), batch=BATCH, ttl=3600)
        assert claim['ok']
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
