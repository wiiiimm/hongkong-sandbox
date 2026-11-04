"""Record a completed browser run after its supervisor released the old lease.

No browser work is repeated. Preserve the original wrapper assertion failure.
"""
import json
from pathlib import Path
import uuid
from run import ROOT, HERE, read, save, digest, reservations
from primrose_compound_foundation_v2_20261015 import module
from original_availability_overlay_v1_20261027 import stage

PREFIX = 'government-xl-west-kowloon-north-pair-after-ocean-'
BATCH = PREFIX + 'atomic-existing-peer-receipt-v1-20261027'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    old = base / (PREFIX + 'atomic-existing-peer-browser-v1-20261027')
    doc = base / BATCH
    assert not doc.exists()
    log = (old / 'browser.log').read_text()
    marker = log.rfind('\n{')
    outcome = json.loads(log[marker + 1:])
    assert outcome == dict(ok=True, exitCode=0, released=True)
    report = read(old / 'atomic/report.json')
    fixture = read(base / (PREFIX + 'availability-fixture-v1-20261027') / 'summary.json')
    spec_path = base / (PREFIX + 'availability-fixture-v1-20261027') / 'overlay-spec.json'
    spec = read(spec_path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == fixture['manifestSHA256']
    stage(ROOT, spec, read(manifest), {}, Path.read_bytes)
    local = HERE / 'local' / (PREFIX + 'atomic-existing-peer-browser-v1-20261027')
    catalogue = read(local / 'catalogue.json')
    sources = {m['uid']: (m['sha256'], m['triangles']) for m in catalogue['models']}
    ids = sorted(sources)
    assert ids == fixture['activationGroup']
    assert report['passed'] and not report['pageErrors'] and len(report['cases']) == 4
    assert report['cases'][0]['width'] == 1280 and report['cases'][0]['failedUid'] is None
    assert sorted(c['failedUid'] for c in report['cases'][1:]) == ids
    for case in report['cases']:
        assert case['baseOnlyRestoredCompleteGroup'] and case['completeGroupEvicted']
        assert case['audit']['frames'] > 0 and not case['audit']['violations']
        assert all(t['active'] in [[], ids] for t in case['audit']['transitions'])
        assert {s['uid']: (s['sha256'], s['triangles']) for s in case['sources']} == sources
        assert all(s['active'] for s in case['sources'])
        if case['failedUid']:
            assert case['width'] == 390 and case['failureKeptAllBasics']
    resources = read(base / (PREFIX + 'native-fallback-plan-v1-20261027.json'))['resources']
    claim = reservations.claim('north-atomic-receipt-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
    assert claim.get('ok')
    lease = claim['reservation']
    try:
        refs = [Path(__file__), old / 'atomic/report.json', old / 'browser.log', manifest, spec_path,
                ROOT / spec['source'], local / 'config.json', local / 'catalogue.json', local / 'source-forms.json',
                HERE / 'north_pair_atomic_browser_v1_20261027.py', HERE / 'model_atomic_lifecycle_browser_v2_20261027.mjs']
        for entry in catalogue['models']:
            asset = local / entry['asset']
            assert digest(asset.read_bytes()) == entry['sha256'] and asset.stat().st_size == entry['bytes']
            refs.append(asset)
        for t in read(local / 'config.json')['terrain']:
            source = ROOT / t['source']
            refs.append(source)
        doc.mkdir()
        failure = Path('/tmp/astra-north-atomic-existing-peer-v1.log').read_bytes()
        assert b'assert reservations.owns(lease)' in failure and b'AssertionError' in failure
        (doc / 'original-wrapper-failure.log').write_bytes(failure)
        refs.append(doc / 'original-wrapper-failure.log')
        module('north_atomic_receipt_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'completed-atomic-browser-receipt-after-supervisor-release', refs,
            dict(uids=ids, cases=4, passed=True, browserRerun=False, priorWrapperFailurePreserved=True,
                 originalBoundedRunnerReleased=True, physicalAcceptance=False, visualAcceptance=False,
                 installationApproved=False, publication=False, sourceGeometryChanges=0, newlyInstalled=0))
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
