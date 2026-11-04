"""Complete current BASIC foundation and exact finite-negative context on Southside.

Diagnostic only: no wall/floor role or unresolved support warning is approved.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import shutil
import sys
import uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_original_triangle_pair_column_gap_20261010 import verify

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-current-basic-compound-context-v1-20261104'
OUT = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
SUPPORT = 'government-xl-southside-current-basic-original-support-v1-20261104'
RUNTIME = 'government-xl-southside-source-bound-current-podium-runtime-v1-20261104'
UID = 'landsd/315025:0'


def examine(task):
    body, mode, ground, path = task
    tri = np.asarray(body['position'], dtype='<f8').reshape(-1, 3)[np.asarray(body['index']).reshape(-1, 3)]
    ground = np.asarray(ground, dtype='<f8').reshape(-1, 3, 3)
    b = body['building']
    final = module('southside_actual_basic_foundation', HERE / 'xl-final-script-pass.py')
    foundation = final.foundation_context(tri, ground, Polygon(b['rings'][0], b['rings'][1:]))
    glo, ghi = ground[:, :, [0, 2]].min(1), ground[:, :, [0, 2]].max(1)
    threshold = Fraction(-1, 2)
    global_max = Fraction(float(ground[:, :, 1].max()))
    negative, pruned, tested = [], 0, 0
    for i, face in enumerate(tri):
        if Fraction(float(face[:, 1].min())) - global_max >= threshold:
            pruned += 1
            continue
        xz = face[:, [0, 2]]
        ids = np.flatnonzero(np.all(ghi >= xz.min(0), axis=1) & np.all(glo <= xz.max(0), axis=1))
        pairs = []
        for j in ids:
            # This bound can prune a pair only when every finite source vertex
            # exceeds every provider vertex by the unchanged half-metre limit.
            if Fraction(float(face[:, 1].min())) - Fraction(float(ground[j, :, 1].max())) >= threshold:
                continue
            proof = verify(face, ground[j])
            tested += 1
            if proof['exactClosedHorizontalProjectionsMeet'] and Fraction(proof['exactMinimumFiniteColumnGapM']) < threshold:
                pairs.append(dict(groundFace=int(j), proof=proof))
        if pairs:
            normal = np.cross(face[1]-face[0], face[2]-face[0])
            length = float(np.linalg.norm(normal))
            ratio = float(normal[1])/length if length else None
            role = 'degenerate' if not length else 'vertical' if abs(ratio) <= 1e-6 else 'upward' if ratio > .25 else 'downward' if ratio < -.25 else 'sloped'
            negative.append(dict(sourceFace=i, vertices=face.tolist(), normalYRatio=ratio, geometricOrientation=role, negativePairs=pairs))
    record = dict(uid=body['uid'], mode=mode, sourceWorldSHA256=digest(tri.tobytes()), compoundGroundSHA256=digest(ground.tobytes()), completeBasicFaces=len(tri), completeCompoundGroundFaces=len(ground), foundation=foundation, globallyHeightPrunedFaces=pruned, exactFinitePairsTested=tested, negativeFaces=negative, ordinaryClearanceThresholdM=-.5, diagnosticOnly=True, installationApproved=False)
    save(path, record)
    return dict(uid=body['uid'], mode=mode, completeBasicFaces=len(tri), exactFinitePairsTested=tested, exactNegativeFaceCount=len(negative), geometricNegativeOrientations=dict(Counter(r['geometricOrientation'] for r in negative)), completeGround=foundation['completeTerrainTriangles']==foundation['triangles'], fullyBuriedTriangles=foundation['fullyBuriedTriangles'], fullyBuriedUpwardTriangles=foundation['fullyBuriedUpwardTriangles'], fullyBuriedAreaFraction=foundation['fullyBuriedAreaFraction'], establishedFoundationPolicyPassed=foundation['completeTerrainTriangles']==foundation['triangles'] and foundation['fullyBuriedUpwardTriangles']==0 and foundation['fullyBuriedAreaFraction']<=.001)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert not OUT.exists()
    _, sp = authenticate(BASE / SUPPORT)
    inputpath, checkpath = [BASE / SUPPORT / n for n in ['input.json.gz', 'checks.json.gz']]
    for path in [inputpath, checkpath]:
        assert digest(path.read_bytes()) == sp[str(path.relative_to(ROOT))]
    inp, checks = read(inputpath), read(checkpath)
    assert len(checks['bodies']) == 16
    resources = {'building:'+b['uid'] for b in checks['bodies']} | {'building:'+UID, 'terrain:city/data/terrain.json'}
    if not args.owned:
        assert not LOCAL.exists()
        claim = reservations.claim('southside-current-basic-compound-'+str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])
    lease = read(LEASE)
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    _, rp = authenticate(BASE / RUNTIME)
    runtimepath = HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz'
    assert digest(runtimepath.read_bytes()) == rp[str(runtimepath.relative_to(ROOT))]
    runtime = read(runtimepath)['rows']
    assert len(runtime) == 1 and runtime[0]['uid'] == UID
    assert runtime[0]['sourceSHA256'] == inp['sourceSHA256']
    terrain = np.asarray(runtime[0]['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    refs = [Path(__file__), BASE / SUPPORT / 'result.json', BASE / RUNTIME / 'result.json', inputpath, checkpath, runtimepath]
    for path, sha in checks['inputHashes'].items():
        assert digest((ROOT/path).read_bytes()) == sha
        refs.append(ROOT/path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == inp['currentManifestSHA256']
    OUT.mkdir()
    modes, reused, tasks = {}, {}, []
    for mode in inp['supportModes']:
        tri = np.asarray(mode['geometry']['position'], dtype='<f8').reshape(-1, 3)[np.asarray(mode['geometry']['index']).reshape(-1, 3)]
        assert len(tri) == 11699 and digest(tri.tobytes()) == mode['worldSHA256']
        same = next((name for name, old in modes.items() if np.array_equal(old, tri)), None)
        if same:
            reused[mode['name']] = same
        else:
            modes[mode['name']] = tri
    for body in checks['bodies']:
        for name, podium in modes.items():
            tasks.append((body, name, np.concatenate([terrain, podium]), OUT/(body['uid'].split('/')[1]+'-'+name+'.json.gz')))
    rows = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for result in pool.map(examine, tasks):
            assert reservations.owns(lease)
            rows.append(result)
            print(result, flush=True)
    for name, source in reused.items():
        for old in [r for r in rows if r['mode']==source]:
            uid = old['uid']
            original = OUT/(uid.split('/')[1]+'-'+source+'.json.gz')
            copied = OUT/(uid.split('/')[1]+'-'+name+'.json.gz')
            shutil.copyfile(original, copied)
            rows.append(dict(old, mode=name, exactBytesReusedFromMode=source, qualification='Complete source and compound ground arrays exactly equal; saved proof bytes remain unchanged with their original mode label.'))
    assert len(rows) == 64
    summary = dict(uids=[UID], sourceSHA256=inp['sourceSHA256'], currentManifestSHA256=inp['currentManifestSHA256'], retainedBasicForms=16, testedUniqueSourceWorlds=len(modes), exactlyEqualWorldReuse=reused, rows=rows, rawTerrainAndSupportFailuresPreserved=True, geometryChanges=0, physicalAccepted=False, supportDependenciesApproved=False, installationApproved=False, qualification='Every complete actual current BASIC face against all drawn candidate ground and complete original podium facets. Established foundation policy and exact finite-column negatives are reported separately. Downward/vertical labels are geometric orientations only, not reviewed architectural roles. No support warning, current BASIC neighbour guard, source identity or whole-source publication obligation is waived.')
    save(OUT/'summary.json', summary)
    refs += [HERE/n for n in ['xl-final-script-pass.py', 'exact_original_triangle_pair_column_gap_20261010.py']]
    assert reservations.owns(lease)
    module('southside_current_basic_compound_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-current-basic-compound-foundation-and-exact-finite-negatives', list(dict.fromkeys(refs)), summary)


if __name__ == '__main__':
    main()
