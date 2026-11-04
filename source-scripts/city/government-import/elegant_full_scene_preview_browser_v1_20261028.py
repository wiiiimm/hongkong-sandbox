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

FIXTURE = PREFIX+'full-scene-preview-fixture-v1-20261028'


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
    prior = HERE/'ronsdale_three_live_browser_v16_20261028.mjs'
    tool = HERE/'ronsdale_three_live_browser_v17_20261028.mjs'
    assert tool.read_text().replace("assert.equal(b.structureType,'Open-sided Structure');", "assert.equal(b.structureType,'Open-sided');") == prior.read_text()
    refs.extend([prior, tool])
    out.mkdir()
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
            print(dict(width=width, phase='private-full-scene-browser-start'), flush=True)
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
        for path, sha in pins.items():
            assert digest((ROOT/path).read_bytes()) == sha, path
        result = dict(uids=config['browserUids'], retainedNativeUids=config['additionalRetainedUids'],
            commands=commands, allBrowserDiagnosticsPassed=all(c['diagnosticPassed'] for c in commands),
            diagnosticOnly=True, fullSceneFixture=FIXTURE, sourceGeometryChanges=0,
            governmentGeometryChanges=0, privateBasicFoundations=3, terrainMembers=2,
            availabilityAcceptance=False, failureTestsDeliberatelyDeferred=True,
            physicalAccepted=False, visualReviewApproved=False, installationApproved=False, publication=False,
            qualification='Unapproved actual-viewer observations on desktop1280/mobile390 using the exact16original/9retained/two-terrain/three-foundation fixture. All old V15 assertions retained; V16 adds a private foundation-only overlay and V17 only corrects the exact source type spelling before use. No performance, architecture, placement, visual or publication approval. Candidate dependency/atomic/failure acceptance is deliberately deferred and cannot be inferred. Actual exported images still need ROOT inspection.')
        save(out/'summary.json', result)
        assert reservations.owns(lease)
        module('elegant_full_scene_browser_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'unapproved-full-scene-desktop-mobile-original-viewer-observation', list(dict.fromkeys(refs)), result)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        server_log.close()


if __name__ == '__main__':
    main()
