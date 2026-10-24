"""Capture current drawn ground for the unchanged hotel; no publication or acceptance."""
from pathlib import Path
import subprocess, shutil, uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations
from primrose_compound_foundation_v2_20261015 import module

BATCH = 'government-xl-disney-hotel-current-ground-v1-20261015'
DOC = ROOT/'docs/astra-city/government-import'/BATCH
LOCAL = HERE/'local'/BATCH
OLD = ROOT/'docs/astra-city/government-import/government-xl-eight-typed-exception-closures-recovered-20261008'
UID = 'landsd/236354:0'

def main():
    assert not DOC.exists() and not LOCAL.exists()
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    manifest_hash = digest(manifest.read_bytes())
    row = next(r for r in read(OLD/'selection.json.gz')['rows'] if r['uid'] == UID)
    source = row['source']
    tile = ROOT/'3d-viewer'/source['tile']
    current = next(b for b in read(tile)['buildings'] if b['uid'] == UID)
    assert current == source['building']
    asset = ROOT/row['candidate']['path']
    assert digest(asset.read_bytes()) == row['candidate']['entry']['sha256'] == row['sourceSHA256']
    claim = reservations.claim('disney-current-ground-'+str(uuid.uuid4()), ['original-ground-compute:'+UID], batch=BATCH, ttl=1800)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        DOC.mkdir(); LOCAL.mkdir()
        target = LOCAL/row['candidate']['entry']['asset']
        target.parent.mkdir(parents=True); shutil.copyfile(asset, target)
        save(LOCAL/'source-forms.json', {UID: dict(tile=source['tile'], tileSHA256=digest(tile.read_bytes()), building=current)})
        save(DOC/'selection.json.gz', dict(batch=BATCH, manifestSHA256=manifest_hash, rows=[row]))
        tool = HERE/'acceptance-metrics-retained-group-parent.mjs'
        command = ['node', str(tool), '--selection', str((DOC/'selection.json.gz').relative_to(ROOT)), '--candidates', str(LOCAL.relative_to(ROOT)), '--out', str((DOC/'metrics.json').relative_to(ROOT)), '--geometry-out', str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
        with (DOC/'worker.log').open('w') as log:
            subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=900, check=True)
        metrics = read(DOC/'metrics.json'); assert len(metrics['rows']) == 1
        assert not metrics['rows'][0].get('error'), metrics['rows'][0]
        geometry = read(LOCAL/'runtime-geometry.json.gz')['rows'][0]
        assert geometry['sourceSHA256'] == row['sourceSHA256']
        triangles = np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
        assert len(triangles) == 15425
        ground = np.asarray(geometry['drawnGroundGeometry']).reshape(-1,3,3)
        helper = module('disney_current_ground_foundation', HERE/'xl-final-script-pass.py')
        foundation = helper.foundation_context(triangles, ground, Polygon(current['rings'][0], current['rings'][1:]))
        save(DOC/'foundation.json', dict(uid=UID, sourceSHA256=row['sourceSHA256'], foundation=foundation, fullAcceptance=False))
        refs = [Path(__file__), OLD/'selection.json.gz', asset, LOCAL/'runtime-geometry.json.gz', HERE/'xl-final-script-pass.py']
        for path, sha in metrics['inputHashes'].items():
            assert digest((ROOT/path).read_bytes()) == sha
            refs.append(ROOT/path)
        assert digest(manifest.read_bytes()) == manifest_hash
        result = module('disney_current_ground_freezer', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'original-hotel-current-drawn-ground-foundation-v1', refs, dict(uids=[UID], foundation=foundation, fullAcceptance=False, newlyInstalled=0, sourceGeometryChanges=0))
        print(dict(jobId=result['jobId'], metrics=metrics['rows'][0], foundation=foundation), flush=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']

if __name__ == '__main__':
    main()
