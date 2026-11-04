"""Capture all five originals on the unchanged private complete floor return.

Reuse completed podium foundation math only after exact whole-array parity.
No terrain publication, source edits or physical approval.
"""
import copy
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
LOCAL = HERE / 'local' / BATCH
CAPTURE = 'government-xl-silvercord-lippo-five-original-selection-v1-20261103'
CANDIDATE = 'government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'
PRIOR = 'government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103'
UIDS = ['landsd/233997:0', 'landsd/231645:0', 'landsd/237843:0', 'landsd/238659:0', 'landsd/239032:0']
PODIUMS = set(UIDS[:2])


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    proposal = take(CANDIDATE, BASE / CANDIDATE / 'summary.json')
    assert proposal['status'] == 'private-coordinated-floor-candidate-assembled'
    assert not proposal['terrainValidatorPassed']
    candidate = take(CANDIDATE, ROOT / proposal['candidate']['path'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    mh = digest(manifest.read_bytes())
    assert mh == proposal['currentManifestSHA256']
    refs.append(manifest)
    old = proposal['replacedParent']
    old_path = ROOT / '3d-viewer' / old['url']
    assert digest(old_path.read_bytes()) == old['sha256']
    retained = read(old_path)['meta']['targetUids']
    assert set(retained) <= set(candidate['meta']['targetUids'])
    refs.append(old_path)
    selection = take(CAPTURE, BASE / CAPTURE / 'selection.json.gz')
    assert selection['manifestSHA256'] == mh
    rows = copy.deepcopy(selection['rows'])
    assert {r['uid'] for r in rows} == set(UIDS)
    for row in rows:
        path = ROOT / row['candidate']['path']
        raw = path.read_bytes()
        assert digest(raw) == row['sourceSHA256'] == row['candidate']['entry']['sha256']
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        assert [f for f in read(tile)['buildings'] if f['uid'] == row['uid']] == [row['source']['building']]
        target = LOCAL / row['candidate']['entry']['asset']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        row['candidate']['path'] = str(target.relative_to(ROOT))
        refs.extend([path, tile, target])
    out = BASE / BATCH
    selected = out / 'selection.json.gz'
    save(selected, dict(rows=rows, manifestSHA256=mh))
    north = proposal['additionalTopLevelPatch']
    north_path = ROOT / north['path']
    assert digest(north_path.read_bytes()) == north['sha256']
    refs.append(north_path)
    terrain = out / 'unapproved-terrain-diagnostic-input.json'
    save(terrain, [dict(**proposal['candidate'], replaces=dict(url=old['url'], sha256=old['sha256'], retainedUids=retained)),
                   dict(path=north['path'], sha256=north['sha256'])])
    tool = HERE / 'acceptance_metrics_multi_retained_v2.mjs'
    geometry_path = LOCAL / 'runtime-geometry.json.gz'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), '--selection', str(selected.relative_to(ROOT)),
            '--candidates', str(LOCAL.relative_to(ROOT)), '--terrain-candidates', str(terrain.relative_to(ROOT)),
            '--out', str((out / 'metrics.json').relative_to(ROOT)),
            '--geometry-out', str(geometry_path.relative_to(ROOT))], cwd=ROOT, stdout=log,
            stderr=subprocess.STDOUT, timeout=3600, check=True)
    actual = read(geometry_path)
    refs.extend([tool, geometry_path])
    assert {r['uid'] for r in actual['rows']} == set(UIDS)
    for path, sha in actual['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    prior = take(PRIOR, HERE / 'local' / PRIOR / 'runtime-geometry.json.gz')
    old_geometry = {r['uid']: r for r in prior['rows']}
    final = module('five_original_floor_foundations', HERE / 'xl-final-script-pass.py')
    results = []
    for row in rows:
        assert reservations.owns(lease)
        uid = row['uid']
        g = next(r for r in actual['rows'] if r['uid'] == uid)
        assert g['sourceSHA256'] == row['sourceSHA256']
        if uid in PODIUMS:
            before = old_geometry[uid]
            assert before['sourceSHA256'] == g['sourceSHA256']
            for key in ['position', 'index', 'drawnGroundGeometry']:
                assert np.array_equal(np.asarray(before[key]), np.asarray(g[key])), (uid, key)
            foundation = take(PRIOR, BASE / PRIOR / (uid.split('/')[1] + '.json'))['foundation']
            reused = True
        else:
            tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
            ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
            b = row['source']['building']
            foundation = final.foundation_context(tri, ground, Polygon(b['rings'][0], b['rings'][1:]))
            reused = False
        save(out / (uid.split('/')[1] + '.json'), dict(uid=uid, foundation=foundation, exactPriorFoundationReused=reused))
        results.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], exactPriorFoundationReused=reused,
            **{k: foundation[k] for k in ['fullyBuriedTriangles', 'fullyBuriedUpwardTriangles', 'minimumGapM']}))
    result = dict(uids=UIDS, rows=results, currentManifestSHA256=mh, completeOriginalSources=5,
        exactUnchangedPodiumSourceAndGroundArraysVerified=True, podiumFoundationCalculationsRepeated=0,
        unapprovedTerrainDiagnosticOnly=True, terrainValidatorPassed=False, physicalAcceptance=False,
        installationApproved=False, publication=False, sourceGeometryChanges=0, sourcePoseChanges=0,
        qualification='Actual renderer capture of five unchanged originals on the exact complete private return. Both podium source/index/whole drawn-ground arrays equal their completed prior capture exactly; their foundation proof is reused. Three newly recovered originals receive fresh current-ground foundation measurements. This grants no compound support, identity, collision, neighbour, terrain-publication or browser approval.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == mh
    module('five_original_floor_runtime_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'five-original-private-complete-floor-production-renderer-diagnostic', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        old = read(BASE / CANDIDATE / 'summary.json')['replacedParent']
        parent = read(ROOT / '3d-viewer' / old['url'])
        resources = {'building:' + uid for uid in parent['meta']['targetUids'] + UIDS}
        resources |= {'terrain:' + old['url'], 'terrain:city/data/terrain.json', 'immutable-source-proof:' + BATCH}
        claim = reservations.claim('silvercord-lippo-five-original-floor-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
