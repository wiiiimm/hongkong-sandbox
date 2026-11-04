"""Bounded private ground trial against unchanged Stonecutters source geometry.

This is a feasibility check, not a terrain publisher or acceptance override.
"""
import json
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_merchants_finite_inset_v4_20261021 import plane, lift

UID = 'landsd/127037:0'
BATCH = 'government-xl-stonecutters-ground-trial-v1-20261021'
BASE = ROOT / 'docs/astra-city/government-import'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
SOURCE = BASE / 'government-xl-stonecutters-current-runtime-v1-20261021'

def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    _, pins = authenticate(SOURCE)
    refs = [Path(__file__), SOURCE / 'result.json']
    consumed = {}
    def take(path):
        key = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == pins[key], key
        consumed[key] = pins[key]
        refs.append(path)
        return read(path)
    row = take(SOURCE / 'selection.json.gz')['rows'][0]
    assert row['uid'] == UID
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    refs.append(asset)
    source = decode_original_world_triangles(asset.read_bytes())
    runtime = take(HERE / 'local' / SOURCE.name / 'runtime-geometry.json.gz')['rows'][0]
    assert runtime['uid'] == UID and runtime['sourceSHA256'] == row['sourceSHA256']
    report = take(SOURCE / 'metrics.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == report['inputHashes'][str(manifest.relative_to(ROOT))]
    ground = np.asarray(runtime['drawnGroundGeometry']).reshape(-1, 3, 3)
    projected = shapely.polygons(ground[:, :, [0, 2]])
    projection = shapely.union_all(shapely.polygons(source[:, :, [0, 2]]))
    core = projection.buffer(1, join_style='mitre')
    outer = core.buffer(8, join_style='mitre')
    available = shapely.union_all(projected)
    missing = outer.difference(available).area
    assert missing <= 1e-8, f'Need expanded current terrain capture: {missing} square metres missing'
    floor = float(source[:, :, 1].min())
    output, lineage = [], []
    for i, (face, polygon) in enumerate(zip(ground, projected)):
        if polygon.area <= 1e-10 or polygon.disjoint(outer):
            output.append(face.copy())
            lineage.append(i)
            continue
        coeff = plane(face)
        for region in (polygon.intersection(core), polygon.intersection(outer).difference(core), polygon.difference(outer)):
            for fragment in lift(region, coeff):
                for vertex in fragment:
                    weight = max(0., 1. - shapely.Point(vertex[[0, 2]]).distance(core) / 8.)
                    vertex[1] = min(vertex[1], vertex[1] + weight * (floor - vertex[1]))
                output.append(fragment)
                lineage.append(i)
    output = np.asarray(output)
    assert np.isfinite(output).all()
    building = row['source']['building']
    final = module('stone_trial_foundation', HERE / 'xl-final-script-pass.py')
    foundation = final.foundation_context(source, output, shapely.Polygon(building['rings'][0], building['rings'][1:]))
    save(LOCAL / 'private-ground.json.gz', dict(triangles=output.tolist(), notPublishable=True))
    save(DOC / 'foundation.json', foundation)
    save(DOC / 'lineage.json.gz', dict(originalGroundFaceIds=lineage, coreWKT=core.wkt, outerWKT=outer.wkt))
    summary = dict(uids=[UID], sourceSHA256=row['sourceSHA256'], originalTriangles=len(source),
                   sourceMinimumY=floor, baselineFaces=len(ground), trialFaces=len(output),
                   foundation={k: v for k, v in foundation.items() if k != 'components'},
                   installationApproved=False, productionChanges=0,
                   nextStep='Validate complete replacement domain, all neighbours, original identity, renderer and visual gates; this local trial alone is not publishable.')
    save(DOC / 'summary.json', summary)
    for key, expected in consumed.items():
        assert digest((ROOT / key).read_bytes()) == expected, key
    assert digest(asset.read_bytes()) == row['sourceSHA256'] and reservations.owns(lease)
    refs += [LOCAL / 'private-ground.json.gz', HERE / 'xl-final-script-pass.py',
             HERE / 'china_merchants_finite_inset_v4_20261021.py', HERE / 'exact_packed_world_geometry_20261009.py']
    module('stone_trial_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'original-ground-repair-feasibility', refs, summary)
    print(json.dumps(summary), flush=True)

def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim(BATCH + '-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(lease, default=str)))
    try:
        subprocess.run([sys.executable, str(HERE / 'harbourfront_reserved_runner_v1_20261021.py'),
                        str(LOCAL / 'reservation.json'), sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']

if __name__ == '__main__':
    main()
