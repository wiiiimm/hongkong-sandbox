"""Preserve completed desktop checks and the actual partial mobile failure."""
import json
from pathlib import Path
import uuid
from run import ROOT, HERE, read, digest, reservations
from primrose_compound_foundation_v2_20261015 import module

PREFIX = 'government-xl-west-kowloon-north-pair-after-ocean-'
PARENT = PREFIX + 'full-existing-peer-browser-v2-20261027'
BATCH = PREFIX + 'desktop-complete-mobile-held-v1-20261027'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    assert not (base / BATCH).exists()
    parent = base / PARENT
    local = HERE / 'local' / PARENT
    old_lease = read(local / 'reservation.json')
    assert not reservations.owns(old_lease), 'Prior worker must be terminal/released'
    desktop = read(parent / '1280/staged-browser.json')
    mobile = read(parent / '390/staged-browser.json')
    assert desktop['passed'] and not desktop['errors'] and len(desktop['retainedNativeOwnViews']) == 134
    assert len(desktop['views']) == 4 and len(mobile['retainedNativeOwnViews']) == 15
    assert mobile['errors'] == ['page.waitForFunction: Timeout 120000ms exceeded.']
    assert mobile['retainedNativeOwnViews'][-1]['uid'] == 'landsd/160070:0'
    fixture = read(base / (PREFIX + 'availability-fixture-v1-20261027') / 'summary.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == fixture['manifestSHA256']
    catalogue = read(local / 'catalogue.json')
    resources = set(read(base / (PREFIX + 'native-fallback-plan-v1-20261027.json'))['resources'])
    resources.update('building:' + v['uid'] for v in desktop['retainedNativeOwnViews'])
    claim = reservations.claim('north-desktop-receipt-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
    assert claim.get('ok')
    lease = claim['reservation']
    try:
        refs = [Path(__file__), manifest, local / 'catalogue.json', local / 'source-forms.json',
                local / 'config-1280.json', local / 'config-390.json',
                parent / '1280/staged-browser.json', parent / '390/staged-browser.json',
                parent / 'browser-1280.log', parent / 'browser-390.log',
                HERE / 'north_pair_full_browser_v2_20261027.py', HERE / 'ronsdale_three_live_browser_v16_20261027.mjs']
        for m in catalogue['models']:
            asset = local / m['asset']
            assert digest(asset.read_bytes()) == m['sha256']
            refs.append(asset)
        for t in read(local / 'config-1280.json')['terrain']:
            refs.append(ROOT / t['source'])
        for width in [1280, 390]:
            refs.extend((parent / str(width)).glob('*.png'))
        refs.extend((ROOT / '3d-viewer/city').glob('*.js'))
        module('north_desktop_partial_mobile_receipt', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'completed-desktop-and-preserved-partial-mobile-timeout', refs,
            dict(uids=[m['uid'] for m in catalogue['models']], desktopDiagnosticsPassed=True,
                 desktopRetainedViews=134, desktopSourceViews=4, mobileDiagnosticsPassed=False,
                 completedMobileRetainedViews=15, mobileHoldUid='landsd/160070:0',
                 mobileHoldReason='retained-actor-inactive-at-night-capture-timeout', browserRerun=False,
                 sourceCameraFailuresPreserved=True, physicalAcceptance=False, visualAcceptance=False,
                 installationApproved=False, publication=False, sourceGeometryChanges=0, newlyInstalled=0))
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
