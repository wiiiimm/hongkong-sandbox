"""Capture retained originals using real UI selection and verify normal fallback.

No production/runtime/model edits. Source captures are separately preserved,
including the old retained timeout. This receipt never grants source approval.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

PREFIX = 'government-xl-west-kowloon-north-pair-after-ocean-'
OLD = PREFIX + 'source-camera-supplement-v1-20261027'
COMPARE = PREFIX + 'lui-mobile-before-after-v1-20261027'
BATCH = PREFIX + 'selected-retained-mobile-v1-20261027'
BASE = ROOT / 'docs/astra-city/government-import'
UID = 'landsd/160070:0'
SOURCES = {'landsd/182397:0': 'f16aa7f57a9b89962a6e1f3183e4dea922c7dbcb173515e608deae1ddc4b48b1',
           'landsd/309340:0': 'a8d145aaefe5aff04cd0f3d36b51ddf03baa951cb24d30504f0e9de272f12f0a'}


def main():
    doc, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not doc.exists() and not local.exists()
    comparison, comparison_pins = authenticate(BASE / COMPARE)
    observations = read(BASE / COMPARE / 'observations.json')
    live, staged = [observations[m]['report']['retainedActorTimeout'] for m in ['live', 'staged']]
    assert live['uid'] == staged['uid'] == UID and live['time'] == staged['time'] == '22:00'
    assert live['camera'] == staged['camera'] and live['target'] == staged['target']
    assert live['stats']['limits'] == staged['stats']['limits']
    assert all(o['selectedId'] is None and not o['active'] and not o['wanted'] and not o['cacheErrors'] for o in [live, staged])
    m = live['model'];cost = m['decodedGeometryBytes'] * 2 + m['indexedVertices'] * 24 + m['triangles'] * 124 + 65536
    assert live['stats']['limits']['residentBytes'] < cost <= live['stats']['limits']['selectedResidentBytes']
    template = read(HERE / 'local' / OLD / 'config-390.json')
    uids = sorted(template['additionalRetainedUids']);assert len(uids) == 7 and UID in uids
    refs = [Path(__file__), BASE / COMPARE / 'result.json', BASE / COMPARE / 'observations.json']
    for width in [1280, 390]:
        report_path = BASE / OLD / str(width) / 'staged-browser.json'
        report = read(report_path)
        assert len(report['views']) == 4
        assert report.get('passed') if width == 1280 else report['errors'] == ['page.waitForFunction: Timeout 120000ms exceeded.']
        assert {(v['uid'], v['time']) for v in report['views']} == {(u, t) for u in SOURCES for t in ['15:00', '22:00']}
        for view in report['views']:
            assert view['sourceSHA256'] == SOURCES[view['uid']] and view['sourcePixelVisibility']['visiblePixels'] >= 32
            assert view['active'] and view['fullyFramed'] and not view['fallbackFaces']
            refs.append(report_path.parent / view['file'])
        refs.append(report_path)
    tool = HERE / 'ronsdale_three_live_browser_v20_20261027.mjs'
    refs.extend([tool, HERE / 'source_pixel_visibility_witness_v1_20261027.mjs'])
    refs.extend((ROOT / '3d-viewer/city').glob('*.js'))
    pins = dict(comparison_pins)
    pins.update({str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in refs})
    resources = set(read(BASE / (PREFIX + 'native-fallback-plan-v1-20261027.json'))['resources']) | {'building:' + u for u in uids}
    def claim():
        result = reservations.claim('north-selected-retained-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
        assert result.get('ok');return result['reservation']
    for path, sha in pins.items():
        assert digest((ROOT / path).read_bytes()) == sha
    lease = claim();local.mkdir(parents=True);doc.mkdir()
    try:
        config = dict(template)
        config.update(browserUids=[], retainedOnly=True, keepSelectedForRetainedCapture=[UID], viewportWidths=[390],
                      doc=str((doc / '390').relative_to(ROOT)) + '/')
        config_path = local / 'config-390.json';save(config_path, config)
        lease_path = local / 'reservation.json';save(lease_path, json.loads(json.dumps(lease, default=str)))
        with (doc / 'browser-390.log').open('w') as log:
            subprocess.run([sys.executable, str(HERE / 'observed_reserved_runner_v1_20261027.py'), str(lease_path),
                            'node', str(tool), 'staged', str(config_path.relative_to(ROOT))], cwd=ROOT,
                           env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, stdout=log,
                           stderr=subprocess.STDOUT, timeout=1800, check=True)
        assert not reservations.owns(lease)
        report_path = doc / '390/staged-browser.json';report = read(report_path)
        assert report['passed'] and not report['errors'] and report['retainedOnly'] and not report['views']
        rows = report['retainedNativeOwnViews'];assert len(rows) == 14
        assert {(v['uid'], v['time']) for v in rows} == {(u, t) for u in uids for t in ['15:00', '22:00']}
        for v in rows:
            assert v['active'] and v['visible'] and v['fullyFramed'] and v['sourcePixelVisibility']['visiblePixels'] >= 32
            assert v['runtimeBudgetObservation']['stats']['limits'] == live['stats']['limits']
            if v['uid'] == UID:
                assert v['selectedCapture'] and v['runtimeBudgetObservation']['selectedId'] == UID
        fallbacks = report['retainedDeselectionFallbacks'];assert len(fallbacks) == 1
        fallback = fallbacks[0]
        assert fallback['uid'] == UID and fallback['selectedId'] is None and not fallback['active']
        assert fallback['basicLoaded'] and not fallback['basicHidden'] and fallback['fallbackFaces'] > 0
        lease = claim()
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha
        refs.extend([config_path, report_path, doc / 'browser-390.log']);refs.extend((doc / '390').glob('*.png'))
        module('north_selected_retained_mobile_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'normal-ui-selected-retained-mobile-and-basic-fallback-diagnostic', refs,
            dict(uids=uids, actualSourcePixelsRequired=True, sourceSHA256ByUid=SOURCES, originalSourceCapturesPreserved=8,
                 retainedMobileViewCount=14, selectedRetainedUids=[UID], normalDeselectionFallbackVerified=True,
                 normalDeviceBudgetsUnchanged=True, fullMobileAcceptanceStillRequired=True, sourceGeometryChanges=0,
                 physicalAcceptance=False, visualAcceptance=False, installationApproved=False, publication=False))
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
