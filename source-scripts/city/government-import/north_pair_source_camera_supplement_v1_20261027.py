"""Camera-only source supplement after full retained run; no model edits."""
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, reservations
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate

PREFIX = 'government-xl-west-kowloon-north-pair-after-ocean-'
PARENT = PREFIX + 'full-existing-peer-browser-v2-20261027'
BATCH = PREFIX + 'source-camera-supplement-v1-20261027'
BASE = ROOT / 'docs/astra-city/government-import'


def main():
    doc, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not doc.exists() and not local.exists()
    assert (BASE / PARENT / 'result.json').exists(), 'Finish full retained run first'
    parent_pins = authenticate(BASE / PARENT)[1]
    parent_local = HERE / 'local' / PARENT
    catalogue = read(parent_local / 'catalogue.json')
    sources = {m['uid']: m['sha256'] for m in catalogue['models']}
    assert set(sources) == {'landsd/182397:0', 'landsd/309340:0'}
    config = read(parent_local / 'config-1280.json')
    config.pop('viewportWidths', None)
    config.pop('doc', None)
    # Camera is west/north of North Tower, and west of the small auxiliary.
    # The failed original views remain immutable in the parent evidence.
    config.update(additionalRetainedUids=[], captureDirectionByModel={
        'landsd/182397:0': [-1, .6, -.7], 'landsd/309340:0': [-1, .7, 0]},
        stage=str(local.relative_to(ROOT)) + '/', fitBox=True)
    refs = [Path(__file__), BASE / PARENT / 'result.json', parent_local / 'catalogue.json', parent_local / 'source-forms.json']
    save(local / 'catalogue.json', catalogue)
    save(local / 'source-forms.json', read(parent_local / 'source-forms.json'))
    for m in catalogue['models']:
        asset = parent_local / m['asset'];raw = asset.read_bytes()
        assert digest(raw) == m['sha256'] and len(raw) == m['bytes']
        target = local / m['asset'];target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(raw);refs.append(asset)
    for t in config['terrain']:
        refs.append(ROOT / t['source'])
    for overlay in config['availabilityOverlays']:
        refs.append(ROOT / overlay['source'])
    tool = HERE / 'ronsdale_three_live_browser_v17_20261027.mjs'
    refs.extend([tool, HERE / 'source_pixel_visibility_witness_v1_20261027.mjs', ROOT / '3d-viewer/city/data/manifest.json'])
    refs.extend((ROOT / '3d-viewer/city').glob('*.js'))
    pins = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in refs}
    for path, sha in pins.items():
        if path in parent_pins:
            assert parent_pins[path] == sha, 'Supplement must retain the parent evidence inputs'
    resources = read(BASE / (PREFIX + 'native-fallback-plan-v1-20261027.json'))['resources']
    lease = None
    def claim():
        result = reservations.claim('north-source-camera-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert result.get('ok');return result['reservation']
    doc.mkdir()
    try:
        for width in [1280, 390]:
            for path, sha in pins.items():
                assert digest((ROOT / path).read_bytes()) == sha
            lease = claim();lease_path = local / f'lease-{width}.json';save(lease_path, json.loads(json.dumps(lease, default=str)))
            config_path = local / f'config-{width}.json';save(config_path, dict(**config, viewportWidths=[width], doc=str((doc / str(width)).relative_to(ROOT)) + '/'))
            with (doc / f'browser-{width}.log').open('w') as log:
                subprocess.run([sys.executable, str(HERE / 'observed_reserved_runner_v1_20261027.py'), str(lease_path),
                                'node', str(tool), 'staged', str(config_path.relative_to(ROOT))], cwd=ROOT,
                               env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=1800)
            assert not reservations.owns(lease)
            report = read(doc / str(width) / 'staged-browser.json')
            assert report['passed'] and not report['errors'] and len(report['views']) == 4
            assert {(v['uid'], v['time']) for v in report['views']} == {(u, t) for u in sources for t in ['15:00', '22:00']}
            assert all(v['sourcePixelVisibility']['visiblePixels'] >= 32 for v in report['views'])
            refs.extend([config_path, doc / str(width) / 'staged-browser.json', doc / f'browser-{width}.log'])
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha
        lease = claim()
        refs.extend(doc.rglob('*.png'))
        module('north_source_camera_supplement_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'camera-only-exact-original-source-visibility-supplement', refs,
            dict(uids=sorted(sources), sourceSHA256ByUid=sources, parentFullRetainedRun=PARENT,
                 actualSourcePixelsRequired=True, cameraOnlyChanges=True, sourceGeometryChanges=0,
                 physicalAcceptance=False, visualAcceptance=False, installationApproved=False, publication=False))
    finally:
        if lease and reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
