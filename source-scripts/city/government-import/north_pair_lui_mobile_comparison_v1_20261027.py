"""Observe unchanged live versus staged mobile behaviour; no budget/model edits."""
import copy
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
CAMERA = PREFIX + 'source-camera-supplement-v1-20261027'
BATCH = PREFIX + 'lui-mobile-before-after-v1-20261027'
BASE = ROOT / 'docs/astra-city/government-import'
UID = 'landsd/160070:0'


def main():
    doc, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not doc.exists() and not local.exists()
    prior = HERE / 'local' / CAMERA
    assert not reservations.owns(read(prior / 'lease-390.json'))
    inventory_folder = BASE / 'government-xl-after-ocean-four-current-inventory-v1-20261027'
    _, inventory_pins = authenticate(inventory_folder)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == inventory_pins[str(manifest_path.relative_to(ROOT))]
    template = read(prior / 'config-390.json')
    old_mobile = read(BASE / CAMERA / '390/staged-browser.json')
    day = next(v for v in old_mobile['retainedNativeOwnViews'] if v['uid'] == UID and v['time'] == '15:00')
    chosen = day['sourcePixelVisibility']['cameraSearch']['selected']
    import math
    az = math.radians(chosen['azimuth'])
    template.update(retainedOnly=True, browserUids=[], autoVisibleCamera=False,
                    retainedCaptureDirectionByModel={UID: [math.sin(az), chosen['elevation'], math.cos(az)]})
    resources = set(read(BASE / (PREFIX + 'native-fallback-plan-v1-20261027.json'))['resources'])
    resources.update('building:' + u for u in template['additionalRetainedUids'])
    tool = HERE / 'ronsdale_three_live_browser_v19_20261027.mjs'
    refs = [Path(__file__), tool, HERE / 'source_pixel_visibility_witness_v1_20261027.mjs', inventory_folder / 'result.json',
            manifest_path, BASE / CAMERA / '390/staged-browser.json', prior / 'config-390.json']
    for url in read(manifest_path)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        if any(m['uid'] == UID for m in read(path)['models']):
            assert digest(path.read_bytes()) == inventory_pins[str(path.relative_to(ROOT))]
            entry = next(m for m in read(path)['models'] if m['uid'] == UID)
            assert entry['sha256'] == '24e5dc36fd94705b3dadeb4f51eb1f344145dc6020cda85951fd5741f3a72fdd'
            refs.extend([path, path.parent / entry['asset']])
    refs.extend((ROOT / '3d-viewer/city').glob('*.js'))
    refs.extend(ROOT / t['source'] for t in template['terrain'])
    refs.extend(ROOT / o['source'] for o in template['availabilityOverlays'])
    pins = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in refs}
    doc.mkdir();local.mkdir(parents=True)
    def claim():
        result = reservations.claim('north-lui-comparison-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
        assert result.get('ok');return result['reservation']
    observations = {}
    for mode in ['live', 'staged']:
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha
        config = copy.deepcopy(template)
        config.update(doc=str((doc / mode).relative_to(ROOT)) + '/', viewportWidths=[390])
        if mode == 'live':
            config.update(catalogueURL='city/data/official-models/government-xl-terrain-recovery-272986-typed-stage-20261009/catalogue.json',
                          terrain=[], availabilityOverlays=[])
        config_path = local / (mode + '.json');save(config_path, config)
        lease = claim();lease_path = local / (mode + '-lease.json');save(lease_path, json.loads(json.dumps(lease, default=str)))
        try:
            with (local / (mode + '.log')).open('w') as log:
                result = subprocess.run([sys.executable, str(HERE / 'observed_reserved_runner_v1_20261027.py'), str(lease_path),
                                         'node', str(tool), mode, str(config_path.relative_to(ROOT))], cwd=ROOT,
                                        env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, stdout=log,
                                        stderr=subprocess.STDOUT, timeout=1800)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        report_path = doc / mode / (mode + '-browser.json')
        observations[mode] = dict(exitCode=result.returncode, report=read(report_path) if report_path.exists() else None)
        refs.extend([config_path, local / (mode + '.log')])
        if report_path.exists():
            refs.append(report_path);refs.extend((doc / mode).glob('*.png'))
        save(doc / 'observations.json', observations)
        print(mode, 'recorded', result.returncode, flush=True)
    lease = claim()
    try:
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha
        refs.append(doc / 'observations.json')
        module('north_lui_comparison_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'unchanged-live-vs-staged-retained-mobile-behaviour-observation', refs,
            dict(uids=[UID], completedModes=['live', 'staged'], normalDeviceBudgetsUnchanged=True,
                 sourceGeometryChanges=0, sourcePoseChanges=0, sourceIdentityReapproved=False,
                 causalDecisionPending=True, physicalAcceptance=False, visualAcceptance=False,
                 installationApproved=False, publication=False))
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
