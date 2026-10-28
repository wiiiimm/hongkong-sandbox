"""Run private desktop/mobile full-scene observations without publishing assets."""
import argparse
import copy
import functools
import http.server
import os
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from elegant_basic_footing_foreign_volume_v1_20261028 import BASE, PREFIX

FIXTURE = PREFIX+'full-scene-preview-fixture-v2-20261028'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith(PREFIX) and '/' not in a.batch
    out, local = BASE/a.batch, HERE/'local'/a.batch
    assert not out.exists()
    fixture, pins = authenticate(BASE/FIXTURE)
    inputs_path = BASE/FIXTURE/'fixture-inputs.json'
    assert digest(inputs_path.read_bytes()) == pins[str(inputs_path.relative_to(ROOT))]
    inputs = read(inputs_path)
    resources, lp = set(inputs['resources']), local/'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('elegant-full-scene-browser-'+str(uuid.uuid4()), sorted(resources), batch=a.batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    refs = [Path(__file__), BASE/FIXTURE/'result.json', inputs_path]
    for path, sha in pins.items():
        assert digest((ROOT/path).read_bytes()) == sha, path
        refs.append(ROOT/path)
    config_path = ROOT/inputs['configPath']
    config = read(config_path)
    assert config['diagnosticOnly'] and config['publication'] is False
    assert config['viewerURL'] == 'http://127.0.0.1:4177/city.html'
    assert len(config['browserUids']) == 16 and len(config['additionalRetainedUids']) == 9 and len(config['terrain']) == 2
    assert config['failureTestUids'] == [] and inputs['failureTestsDeliberatelyDeferred']
    for overlay in config['privateFoundationTileOverlays']:
        assert digest((ROOT/overlay['source']).read_bytes()) == overlay['afterSHA256']
        original = ROOT/'3d-viewer'/overlay['url']
        assert digest(original.read_bytes()) == overlay['beforeSHA256']
        expected = copy.deepcopy(read(original))
        for change in overlay['changes']:
            b = next(f for f in expected['buildings'] if f['uid'] == change['uid'])
            assert b == change['before'] and change['proposalApproved'] is False
            assert b.get('foundationBase') is None and b.get('foundationPolicy') is None and not b.get('modelGeometry')
            if change['role'] == 'existing-estimated-open-canopy':
                assert b['structureType'] == 'Open-sided Structure'
            else:
                assert change['role'] == 'surveyed-solid-podium' and b['structureType'] == 'Podium'
            b['foundationBase'] = change['foundationBase']
        assert read(ROOT/overlay['source']) == expected
    prior = HERE/'ronsdale_three_live_browser_v17_20261028.mjs'
    tool = HERE/'ronsdale_three_live_browser_v19_20261028.mjs'
    parity_path = HERE/'ronsdale_joint_box_fit_adapter_v1_20261028.json'
    parity = read(parity_path)
    observed_path = HERE/'ronsdale_joint_failure_observation_adapter_v1_20261028.json'
    observed = read(observed_path)
    assert digest(tool.read_bytes()) == observed['newSHA256']
    restored = tool.read_text()
    assert restored.count(observed['after']) == 1
    restored = restored.replace(observed['after'], observed['before'], 1)
    assert digest(restored.encode()) == observed['oldSHA256'] == parity['newSHA256']
    assert digest(prior.read_bytes()) == parity['oldSHA256']
    refs.append(observed_path)
    for change in reversed(parity['replacements']):
        assert restored.count(change['after']) == 1
        restored = restored.replace(change['after'], change['before'], 1)
    assert restored == prior.read_text()
    refs.append(parity_path)
    prior_browser_path = BASE/(PREFIX+'full-scene-preview-browser-v2-20261028')
    prior_receipt, prior_pins = authenticate(prior_browser_path)
    prior_desktop = prior_browser_path/'1280/staged-browser.json'
    assert digest(prior_desktop.read_bytes()) == prior_pins[str(prior_desktop.relative_to(ROOT))]
    desktop = read(prior_desktop)
    assert desktop['passed'] and len(desktop['views']) == 32 and len(desktop['retainedNativeOwnViews']) == 18
    refs.extend([prior_browser_path/'result.json', prior_desktop])
    refs.extend([prior, tool])
    tool = HERE/'elegant_foundation_closeups_v1_20261028.mjs'
    refs.append(tool)
    original_stage = ROOT/config['stage']
    catalogue = read(original_stage/'catalogue.json')
    before_by_uid = {m['uid']: m for m in catalogue['models']}
    assert len(before_by_uid) == 16
    catalogue['models'].sort(key=lambda m: m['uid'] != 'landsd/100673:0')
    assert catalogue['models'][0]['uid'] == 'landsd/100673:0'
    assert {m['uid']: m for m in catalogue['models']} == before_by_uid
    for entry in catalogue['models']:
        source = original_stage/entry['asset']
        assert digest(source.read_bytes()) == entry['sha256']
        dest = local/entry['asset']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
        refs.append(dest)
    save(local/'catalogue.json', catalogue)
    save(local/'source-forms.json', read(original_stage/'source-forms.json'))
    config['stage'] = str(local.relative_to(ROOT))+'/'
    config['catalogueURL'] = 'city/data/official-models/'+a.batch+'/catalogue.json'
    refs.extend([local/'catalogue.json', local/'source-forms.json'])
    out.mkdir()
    save(out/'selection-order.json', dict(firstUserSelectedUid='landsd/100673:0',
         catalogueEntryOrderOnlyChanged=True, modelEntriesAndAssetBytesUnchanged=True,
         productionBudgetsUnchanged=True, fullJointAssertionsExecuted=False))
    catalogue_preflight = HERE/'private_original_catalogue_preflight_v1_20261028.mjs'
    refs.append(catalogue_preflight)
    with (out/'production-catalogue-preflight.log').open('w') as log:
        subprocess.run(['node', str(catalogue_preflight), config['stage']+'catalogue.json',
                        'http://127.0.0.1:4177/'+config['catalogueURL']], cwd=ROOT,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    closure_tool = HERE/'private_viewer_runtime_closure_v1_20261028.mjs'
    closure_path = out/'runtime-input-closure.json'
    subprocess.run(['node', str(closure_tool), 'capture', str(closure_path.relative_to(ROOT))], cwd=ROOT, check=True)
    refs.extend([closure_tool, closure_path])
    server_log = (out/'private-server.log').open('w')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):
            server_log.write((fmt % args)+'\n')
            server_log.flush()

    # Bind only our private loopback port. An occupied port aborts; never restart
    # or terminate another server, including the shared 4176 instance.
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 4177), functools.partial(Handler, directory=str(ROOT/'3d-viewer')))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    commands = []
    try:
        preflight = local/'preflight-config.json'
        save(preflight, dict(config, doc=str(out.relative_to(ROOT))+'/'))
        subprocess.run(['node', str(tool), 'preflight', str(preflight.relative_to(ROOT))], cwd=ROOT, check=True)
        refs.append(preflight)
        for width in [1280, 390]:
            assert reservations.owns(lease)
            destination = out/str(width)
            cfg = local/('config-'+str(width)+'.json')
            save(cfg, dict(config, viewportWidths=[width], doc=str(destination.relative_to(ROOT))+'/'))
            refs.append(cfg)
            print(dict(width=width, phase='private-targeted-camera-start'), flush=True)
            with (out/('browser-'+str(width)+'.log')).open('w') as log:
                result = subprocess.run(['node', str(tool), 'staged', str(cfg.relative_to(ROOT))], cwd=ROOT,
                    env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, stdout=log, stderr=subprocess.STDOUT, timeout=2400)
            report_path = destination/'staged-browser.json'
            report = read(report_path) if report_path.exists() else {}
            commands.append(dict(width=width, exitCode=result.returncode, reportPresent=report_path.exists(),
                                 diagnosticPassed=result.returncode == 0 and report.get('passed') is True))
            save(out/('command-'+str(width)+'.json'), commands[-1])
            print(commands[-1], flush=True)
            if report_path.exists():
                refs.append(report_path)
        subprocess.run(['node', str(closure_tool), 'verify', str(closure_path.relative_to(ROOT))], cwd=ROOT, check=True)
        for path in read(closure_path)['inputHashes']:
            refs.append(ROOT/path)
        for path, sha in pins.items():
            assert digest((ROOT/path).read_bytes()) == sha, path
        result = dict(uids=['landsd/99061:0','landsd/213586:0','landsd/336456:0'], commands=commands,
            diagnosticOnly=True, fullSceneFixture=FIXTURE, sourceGeometryChanges=0,
            physicalAccepted=False, visualReviewApproved=False, installationApproved=False, publication=False,
            qualification='Targeted unselected BASIC foundation close-ups and lower-band ray-picking nomination only, with actual source-context residency recorded. Not a full joint-context acceptance. Production meshes, source placement and budgets unchanged. Not full-scene acceptance or installation credit.')
        save(out/'summary.json', result)
        assert reservations.owns(lease)
        module('elegant_full_scene_browser_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'private-basic-foundation-closeup-camera-diagnostic', list(dict.fromkeys(refs)), result)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        server_log.close()


if __name__ == '__main__':
    main()
