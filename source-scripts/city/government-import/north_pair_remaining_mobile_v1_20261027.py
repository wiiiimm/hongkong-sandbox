"""Finish retained mobile checks in small normal-budget, independently saved groups.

Requires the separate source/camera receipt. Never approves new models or edits
runtime budgets. Failed groups are retried individually; independent work continues.
"""
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
PARENT = PREFIX + 'desktop-complete-mobile-held-v1-20261027'
CAMERA = PREFIX + 'selected-retained-mobile-v1-20261027'
BATCH = PREFIX + 'remaining-mobile-v1-20261027'
BASE = ROOT / 'docs/astra-city/government-import'


def check_report(report, uids, expected):
    assert report['passed'] and not report['errors'] and report['retainedOnly'] is True
    assert report['newSourceAcceptance'] is False and not report['views']
    rows = report['retainedNativeOwnViews']
    assert len(rows) == 2 * len(uids)
    assert {(v['uid'], v['time']) for v in rows} == {(u, t) for u in uids for t in ['15:00', '22:00']}
    for v in rows:
        assert v['width'] == 390 and v['active'] and v['visible'] and v['fullyFramed']
        assert v['fallbackFaces'] == 0 and not v['overflow']
        assert v['sourceSHA256'] == expected[v['uid']]
        assert v['sourcePixelVisibility']['visiblePixels'] >= 32
    return True


def main():
    doc, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not doc.exists() and not local.exists(), 'Do not restart an existing sequence'
    parent, parent_pins = authenticate(BASE / PARENT)
    camera, camera_pins = authenticate(BASE / CAMERA)
    inventory_folder = BASE / 'government-xl-after-ocean-four-current-inventory-v1-20261027'
    inventory, inventory_pins = authenticate(inventory_folder)
    assert inventory['currentNativeActors'] == 6989
    assert parent['desktopDiagnosticsPassed'] and camera['actualSourcePixelsRequired']
    assert camera['sourceGeometryChanges'] == 0 and camera['installationApproved'] is False
    assert camera['normalDeviceBudgetsUnchanged'] and camera['normalDeselectionFallbackVerified']
    assert camera['originalSourceCapturesPreserved'] == 8 and camera['retainedMobileViewCount'] == 14
    original = read(BASE / (PREFIX + 'full-existing-peer-browser-v2-20261027') / '1280/staged-browser.json')
    expected = {r['uid']: r['sourceSHA256'] for r in original['retainedNativeOwnViews']}
    assert len(expected) == 67
    camera_report = read(BASE / CAMERA / '390/staged-browser.json')
    assert camera_report['passed'] and not camera_report['errors']
    already = sorted({r['uid'] for r in camera_report['retainedNativeOwnViews']})
    assert len(already) == 7 and set(already) <= set(expected)
    assert len(camera_report['retainedNativeOwnViews']) == 14
    assert {(r['uid'], r['time']) for r in camera_report['retainedNativeOwnViews']} == {(u, t) for u in already for t in ['15:00', '22:00']}
    for row in camera_report['retainedNativeOwnViews']:
        assert row['sourceSHA256'] == expected[row['uid']] and row['sourcePixelVisibility']['visiblePixels'] >= 32
    pending = sorted(set(expected) - set(already))
    assert len(pending) == 60
    template = read(HERE / 'local' / CAMERA / 'config-390.json')
    refs = [Path(__file__), BASE / PARENT / 'result.json', BASE / CAMERA / 'result.json', BASE / CAMERA / '390/staged-browser.json', inventory_folder / 'result.json']
    # All runtime/source/terrain/catalogue inputs must remain the exact reviewed
    # camera inputs. Its output images are immutable too; no approval transfers.
    pins = dict(camera_pins)
    source_stage = ROOT / template['stage']
    assert source_stage.resolve().is_relative_to(ROOT)
    old_stage = HERE / 'local' / (PREFIX + 'full-existing-peer-browser-v2-20261027')
    for filename in ['catalogue.json', 'source-forms.json']:
        old_path = old_stage / filename
        assert digest(old_path.read_bytes()) == parent_pins[str(old_path.relative_to(ROOT))]
        assert read(source_stage / filename) == read(old_path)
        actual = source_stage / filename;refs.append(actual)
        pins[str(actual.relative_to(ROOT))] = digest(actual.read_bytes())
    for entry in read(source_stage / 'catalogue.json')['models']:
        assert entry['sha256'] == camera['sourceSHA256ByUid'][entry['uid']]
        actual = source_stage / entry['asset']
        assert digest(actual.read_bytes()) == entry['sha256'] and actual.stat().st_size == entry['bytes']
        refs.append(actual);pins[str(actual.relative_to(ROOT))] = entry['sha256']
    found = set()
    for url in read(ROOT / '3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        matching = [m for m in read(path)['models'] if m['uid'] in expected]
        if not matching:
            continue
        rel = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == inventory_pins[rel], 'Installed catalogue metadata changed'
        refs.append(path);pins[rel] = inventory_pins[rel]
        for entry in matching:
            uid = entry['uid'];assert uid not in found and entry['sha256'] == expected[uid]
            asset = path.parent / entry['asset'];assetrel = str(asset.relative_to(ROOT))
            assert digest(asset.read_bytes()) == inventory_pins[assetrel] == entry['sha256']
            refs.append(asset);pins[assetrel] = entry['sha256'];found.add(uid)
    assert found == set(expected)
    tool = HERE / 'ronsdale_three_live_browser_v18_20261027.mjs'
    helper = HERE / 'source_pixel_visibility_witness_v1_20261027.mjs'
    refs.extend([tool, helper])
    pins.update({str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in [tool, helper]})
    resources = set(read(BASE / (PREFIX + 'native-fallback-plan-v1-20261027.json'))['resources'])
    resources.update('building:' + u for u in expected)
    freezer = module('north_mobile_group_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    doc.mkdir();local.mkdir(parents=True)
    state = dict(alreadyCovered=already, pending=pending, completed=[], held=[], publication=False, installationApproved=False)
    save(doc / 'progress.json', state)

    def verify_inputs():
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha, 'Frozen mobile input changed: ' + path

    def claim(name):
        result = reservations.claim('north-mobile-' + str(uuid.uuid4()), sorted(resources), batch=name, ttl=3600)
        assert result.get('ok'), 'Current source/terrain scope is reserved'
        return result['reservation']

    def phase(uids, suffix):
        name = BATCH + '-' + suffix
        out = BASE / name;work = local / suffix
        assert not out.exists() and not work.exists()
        verify_inputs();lease = claim(name);out.mkdir();work.mkdir()
        lease_path = work / 'reservation.json';save(lease_path, json.loads(json.dumps(lease, default=str)))
        config = copy.deepcopy(template)
        config.update(additionalRetainedUids=uids, retainedOnly=True, browserUids=[], failureTestUids=[],
                      autoVisibleCamera=True, viewportWidths=[390], doc=str(out.relative_to(ROOT)) + '/')
        config_path = work / 'config.json';save(config_path, config)
        error = None;passed = False
        try:
            with (out / 'browser.log').open('w') as log:
                run = subprocess.run([sys.executable, str(HERE / 'observed_reserved_runner_v1_20261027.py'), str(lease_path),
                                      'node', str(tool), 'staged', str(config_path.relative_to(ROOT))], cwd=ROOT,
                                     env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'},
                                     stdout=log, stderr=subprocess.STDOUT, timeout=1800)
            if run.returncode == 0:
                passed = check_report(read(out / 'staged-browser.json'), uids, expected)
            else:
                error = 'browser-command-exit-' + str(run.returncode)
        except (subprocess.TimeoutExpired, AssertionError) as exc:
            error = type(exc).__name__
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        # Completion bookkeeping gets its own lease after the bounded child has
        # released. A failed browser phase is stored with passed:false, not waived.
        lease = claim(name)
        try:
            verify_inputs()
            phase_refs = refs + [config_path, out / 'browser.log']
            phase_refs.extend(p for p in out.rglob('*') if p.is_file())
            freezer.freeze(name, 'independent-retained-only-mobile-original-diagnostic', list(dict.fromkeys(phase_refs)),
                           dict(uids=uids, passed=passed, error=error, retainedOnly=True, newSourceAcceptance=False,
                                normalDeviceBudgetsUnchanged=True, sourceGeometryChanges=0, physicalAcceptance=False,
                                visualAcceptance=False, installationApproved=False, publication=False))
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        refs.append(out / 'result.json')
        print(name, 'passed' if passed else 'held', flush=True)
        return passed, name

    for offset in range(0, len(pending), 6):
        group = pending[offset:offset + 6]
        passed, name = phase(group, 'group-' + str(offset // 6 + 1).zfill(2))
        if passed:
            state['completed'].extend(dict(uid=u, batch=name) for u in group)
        else:
            for uid in group:
                passed, single = phase([uid], 'single-' + uid.split('/')[1].replace(':', '-'))
                state['completed' if passed else 'held'].append(dict(uid=uid, batch=single))
        save(doc / 'progress.json', state)
    covered = set(already) | {r['uid'] for r in state['completed']}
    assert covered | {r['uid'] for r in state['held']} == set(expected)
    lease = claim(BATCH)
    try:
        verify_inputs();refs.append(doc / 'progress.json')
        freezer.freeze(BATCH, 'composed-67-retained-mobile-original-diagnostics', refs,
                       dict(uids=sorted(expected), coveredUids=sorted(covered), held=state['held'],
                            all67Covered=covered == set(expected), retainedOnly=True, newSourceAcceptance=False,
                            sourceGeometryChanges=0, physicalAcceptance=False, visualAcceptance=False,
                            installationApproved=False, publication=False))
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
