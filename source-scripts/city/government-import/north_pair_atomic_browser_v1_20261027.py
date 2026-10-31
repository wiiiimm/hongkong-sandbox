"""Bounded leased atomic software diagnostic, with no physical review credit."""
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from run import ROOT, HERE, read, save, digest, reservations
from primrose_compound_foundation_v2_20261015 import module
from original_availability_overlay_v1_20261027 import stage

PREFIX = 'government-xl-west-kowloon-north-pair-after-ocean-'
BATCH = PREFIX + 'atomic-existing-peer-browser-v1-20261027'
BASE = ROOT / 'docs/astra-city/government-import'


def main():
    doc = BASE / BATCH
    local = HERE / 'local' / BATCH
    assert not doc.exists() and not local.exists(), 'Never restart an existing diagnostic'
    fixture = read(BASE / (PREFIX + 'availability-fixture-v1-20261027') / 'summary.json')
    spec_path = BASE / (PREFIX + 'availability-fixture-v1-20261027') / 'overlay-spec.json'
    spec = read(spec_path)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == fixture['manifestSHA256']
    stage(ROOT, spec, read(manifest_path), {}, Path.read_bytes)
    runtime = BASE / (PREFIX + 'three-member-runtime-v2-20261027')
    selection = json.loads(gzip.decompress((runtime / 'selection.json.gz').read_bytes()))
    assert digest((runtime / 'selection.json.gz').read_bytes()) == fixture['selectionSHA256']
    source_stage = ROOT / fixture['atomicFixtureCatalogue']
    catalogue = read(source_stage)
    ids = sorted(m['uid'] for m in catalogue['models'])
    assert ids == fixture['activationGroup']
    fallback_plan = read(BASE / (PREFIX + 'native-fallback-plan-v1-20261027.json'))
    scope = read(BASE / (PREFIX + 'three-member-scope-v2-20261027') / 'scope.json')
    resources = set(fallback_plan['resources']) | {'building:' + u for u in scope['touchingNativeUids']}
    claim = reservations.claim('north-atomic-diagnostic-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
    assert claim.get('ok'), 'Source or retained terrain currently reserved'
    lease = claim['reservation']
    lease_path = local / 'reservation.json'
    save(lease_path, json.loads(json.dumps(lease, default=str)))
    refs = [Path(__file__), spec_path, manifest_path, source_stage]
    try:
        for entry in catalogue['models']:
            asset = source_stage.parent / entry['asset']
            raw = asset.read_bytes()
            assert digest(raw) == entry['sha256'] and len(raw) == entry['bytes']
            target = local / entry['asset']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            refs.append(asset)
        save(local / 'catalogue.json', catalogue)
        save(local / 'source-forms.json', [r['source']['building'] for r in selection['rows']])
        terrain = []
        for i, row in enumerate(read(runtime / 'terrain-candidates.json')):
            source = ROOT / row['path']
            assert digest(source.read_bytes()) == row['sha256']
            terrain.append(dict(source=row['path'], destination=f'city/data/private-north-atomic-member-{i}.json',
                                resolution=read(source)['cell'], area='Private atomic diagnostic', replaces=row['replaces']))
            refs.append(source)
        config_path = local / 'config.json'
        save(config_path, dict(diagnosticOnly=True, publication=False, stage=str(local.relative_to(ROOT)) + '/',
                               catalogueURL='city/data/official-models/private-north-atomic-v1/catalogue.json',
                               viewerURL='http://127.0.0.1:4177/city.html', terrain=terrain, availabilityOverlays=[spec]))
        tool = HERE / 'model_atomic_lifecycle_browser_v2_20261027.mjs'
        refs.extend([tool, config_path, local / 'catalogue.json', local / 'source-forms.json'])
        pins = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in refs}
        doc.mkdir()
        command = ['node', str(tool), str(config_path.relative_to(ROOT)), str((doc / 'atomic').relative_to(ROOT))]
        with (doc / 'browser.log').open('w') as log:
            subprocess.run([sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'), str(lease_path), *command],
                           cwd=ROOT, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'},
                           stdout=log, stderr=subprocess.STDOUT, check=True, timeout=1800)
        report = read(doc / 'atomic/report.json')
        assert report['passed'] and not report['pageErrors'] and len(report['cases']) == 4
        assert sorted(c['failedUid'] for c in report['cases'] if c['failedUid']) == ids
        for case in report['cases']:
            assert case['baseOnlyRestoredCompleteGroup'] and case['completeGroupEvicted'] and not case['audit']['violations']
            assert {s['uid']: s['sha256'] for s in case['sources']} == {m['uid']: m['sha256'] for m in catalogue['models']}
            if case['failedUid']:
                assert case['failureKeptAllBasics'] and case['width'] == 390
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha
        assert reservations.owns(lease)
        refs.extend([doc / 'atomic/report.json', doc / 'browser.log'])
        module('north_atomic_browser_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'private-existing-original-peer-atomic-software-diagnostic', refs,
            dict(uids=ids, cases=4, passed=True, sourceGeometryChanges=0, newlyInstalled=0,
                 physicalAcceptance=False, visualAcceptance=False, installationApproved=False, publication=False))
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
