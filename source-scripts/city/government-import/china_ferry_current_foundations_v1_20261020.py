"""Refresh China Ferry's current terrain and locate exact original buried faces.

Diagnostic only: no model/terrain edits or publication approval.
"""
import json
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
SRC = BASE / 'government-xl-next-twenty-current-terrain-v2-20261020'
GROUND = BASE / 'government-xl-next-twenty-original-ground-v3-20261020'
BATCH = 'government-xl-china-ferry-current-foundations-v1-20261020'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
UID = 'landsd/285642:0'


def authenticate(folder):
    receipt = read(folder / 'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                          (receipt['jobId'],)).fetchone() == ('complete', receipt)
    pins = {}
    for ref in receipt['evidenceRefs']:
        assert ref['path'] not in pins or pins[ref['path']] == ref['sha256']
        pins[ref['path']] = ref['sha256']
    return receipt, pins


def face_diagnostics(final, triangles, ground):
    lo, hi = triangles.min((0, 1)), triangles.max((0, 1))
    keep = ((ground[:, :, 0].max(1) >= lo[0] - 1)
            & (ground[:, :, 0].min(1) <= hi[0] + 1)
            & (ground[:, :, 2].max(1) >= lo[2] - 1)
            & (ground[:, :, 2].min(1) <= hi[2] + 1))
    native = ground[keep]
    polygons = shapely.polygons(native[:, :, [0, 2]])
    valid = shapely.area(polygons) > 1e-10
    native, polygons = native[valid], polygons[valid]
    points = np.concatenate([triangles, triangles.mean(1)[:, None, :]], axis=1)
    heights = final.s.context.shared.samples(
        points[:, :, [0, 2]].reshape(-1, 2), native,
        shapely.STRtree(polygons)).reshape(-1, 4)
    gaps = points[:, :, 1] - heights
    complete = np.isfinite(heights).all(1)
    buried = complete & (gaps < -.5).all(1)
    cross = np.cross(triangles[:, 1] - triangles[:, 0],
                     triangles[:, 2] - triangles[:, 0])
    upward = cross[:, 1] > .25 * np.linalg.norm(cross, axis=1)
    return dict(
        completeTerrainTriangles=int(complete.sum()),
        uncoveredFaceIndices=np.flatnonzero(~complete).tolist(),
        buriedFaces=[dict(faceIndex=int(i), upward=bool(upward[i]),
                          vertices=triangles[i].tolist(), sampleGaps=gaps[i].tolist())
                     for i in np.flatnonzero(buried)])


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    refs = [Path(__file__)]
    pins = {}
    receipts = []
    for folder in (SRC, GROUND):
        receipt, bound = authenticate(folder)
        receipts.append(receipt)
        refs.append(folder / 'result.json')
        for p, h in bound.items():
            assert p not in pins or pins[p] == h
            pins[p] = h
    manifest = '3d-viewer/city/data/manifest.json'
    for p, h in pins.items():
        if p != manifest:
            assert digest((ROOT / p).read_bytes()) == h, p
            refs.append(ROOT / p)
    # Historical receipts continue to bind the old manifest. This diagnostic
    # explicitly captures the new manifest; it does not rewrite those receipts.
    current_hash = digest((ROOT / manifest).read_bytes())
    save(DOC / 'historical-input-context.json', dict(
        priorManifestSHA256=pins[manifest], currentManifestSHA256=current_hash,
        historicalReceiptIds=[r['jobId'] for r in receipts],
        reason='Refresh current terrain after subsequent original installations'))
    selection = read(SRC / 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == UID)
    selection['rows'] = [row]
    selection['manifestSHA256'] = current_hash
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    save(DOC / 'selection.json.gz', selection)
    capture = HERE / 'acceptance-metrics-multi-retained.mjs'
    command = ['node', str(capture), '--selection',
               str((DOC / 'selection.json.gz').relative_to(ROOT)), '--candidates',
               str((HERE / 'local' / SRC.name).relative_to(ROOT)), '--out',
               str((DOC / 'metrics.json').relative_to(ROOT)), '--geometry-out',
               str((LOCAL / 'runtime-geometry.json.gz').relative_to(ROOT))]
    save(DOC / 'command.json', command)
    with (DOC / 'worker.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(DOC / 'metrics.json')
    assert len(report['rows']) == 1 and not report['rows'][0].get('error')
    runtime = read(LOCAL / 'runtime-geometry.json.gz')['rows'][0]
    assert runtime['sourceSHA256'] == row['sourceSHA256']
    original = decode_original_world_triangles(asset.read_bytes())
    rendered = np.asarray(runtime['position']).reshape(-1, 3)[
        np.asarray(runtime['index']).reshape(-1, 3)]
    current_ground = np.asarray(runtime['drawnGroundGeometry']).reshape(-1, 3, 3)
    original_ground_path = HERE / 'local' / GROUND.name / '285642:0-ground.json.gz'
    assert digest(original_ground_path.read_bytes()) == pins[str(original_ground_path.relative_to(ROOT))]
    original_ground = np.asarray(read(original_ground_path)['completeOriginalTerrain'])
    final = module('china_ferry_foundation', HERE / 'xl-final-script-pass.py')
    building = row['source']['building']
    polygon = Polygon(building['rings'][0], building['rings'][1:])
    summaries = {}
    for name, triangles, ground in (
            ('rendered-current', rendered, current_ground),
            ('original-source-sheet', original, original_ground)):
        assert len(triangles) == 20464
        foundation = final.foundation_context(triangles, ground, polygon)
        details = face_diagnostics(final, triangles, ground)
        assert len(details['buriedFaces']) == foundation['fullyBuriedTriangles']
        save(DOC / (name + '.json.gz'), dict(
            uid=UID, sourceSHA256=row['sourceSHA256'],
            foundation=foundation, **details, installationApproved=False))
        summaries[name] = {k: v for k, v in foundation.items() if k != 'components'}
        print(name, summaries[name], flush=True)
    for p, h in report['inputHashes'].items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
    assert reservations.owns(lease)
    refs += [capture, HERE / 'xl-final-script-pass.py',
             HERE / 'exact_packed_world_geometry_20261009.py',
             LOCAL / 'runtime-geometry.json.gz', original_ground_path, asset]
    module('china_ferry_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'current-terrain-and-exact-original-buried-face-diagnostic',
        list(dict.fromkeys(refs)), dict(
            uids=[UID], summaries=summaries, installationApproved=False,
            nextStep='Inspect exact remaining original buried upward faces and source-sheet coverage; preserve all current neighbour and runtime gates.'))


def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists()
    claim = reservations.claim(BATCH + '-' + str(uuid.uuid4()),
                               ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(lease, default=str)))
    try:
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
                        'run', '--lease-file', str(LOCAL / 'reservation.json'), '--ttl',
                        '3600', '--', sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
