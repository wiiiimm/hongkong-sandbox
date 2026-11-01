"""Use the existing per-peer atomic lifecycle harness on the exact private pair."""
import argparse, functools, http.server, json, os, subprocess, sys, threading, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from one_peking_cycle_retained_contract_v2_20261101 import SOURCES, SUPPORTS

BASE = ROOT / 'docs/astra-city/government-import'
PREVIEW = 'government-xl-one-peking-after-twin-cycle-private-browser-v4-20261101'
BATCH = 'government-xl-one-peking-after-twin-cycle-atomic-lifecycle-v1-20261101'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    out, local, stage = BASE / BATCH, HERE / 'local' / BATCH, HERE / 'local' / PREVIEW
    assert not out.exists()
    receipt, pins = authenticate(BASE / PREVIEW)
    assert receipt['desktopPassed'] and not receipt['mobilePassed'] and not receipt['installationApproved']
    refs = [Path(__file__), BASE / PREVIEW / 'result.json']
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    catalogue = take(stage / 'catalogue.json')
    take(stage / 'source-forms.json')
    cfg = take(stage / 'browser-config-390.json')
    assert {m['uid']: m['sha256'] for m in catalogue['models']} == SOURCES
    for m in catalogue['models']:
        assert m['activationGroup'] == sorted(SOURCES) and all(m[k] is False for k in ['publicationApproved', 'placementReviewed', 'identityReviewApproved', 'sourceIdentityReviewed'])
        path = stage / m['asset']
        assert digest(path.read_bytes()) == SOURCES[m['uid']]
        refs.append(path)
        assert [d['uid'] for d in m.get('supportDependencies', [])] == ([SUPPORTS[m['uid']]] if m['uid'] in SUPPORTS else [])
    patch_batch = 'government-xl-one-peking-after-twin-cycle-preparation-v3-20261101'
    _, patch_pins = authenticate(BASE / patch_batch)
    refs.append(BASE / patch_batch / 'result.json')
    for t in cfg['terrain']:
        path = ROOT / t['source']
        assert digest(path.read_bytes()) == t['sha256'] == patch_pins[t['source']]
        refs.append(path)
    resources = read(stage / 'reservation.json')['resources']
    lp = local / 'reservation.json'
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('one-peking-per-peer-atomic-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and set(resources) == set(lease['resources'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[str(manifest.relative_to(ROOT))]
    before = manifest.read_bytes()
    refs.append(manifest)
    preview_cfg = take(BASE / 'government-xl-one-peking-cycle-private-browser-config-v4-20261101.json')
    cfg.update(diagnosticOnly=True, publication=False, viewportWidths=[1280, 390], atomicCaptureDirectionByViewport={w: preview_cfg['captureDirectionsByViewport'][str(w)]['landsd/240487:0'] for w in [1280, 390]})
    config = local / 'config.json'
    save(config, cfg)
    tool = HERE / 'model_atomic_lifecycle_browser_v4_20261101.mjs'
    refs.extend([config, tool])
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
        def copyfile(self, source, target):
            try: super().copyfile(source, target)
            except (BrokenPipeError, ConnectionResetError): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 4177), functools.partial(Handler, directory=str(ROOT / '3d-viewer')))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        out.mkdir()
        with (out / 'browser.log').open('w') as log:
            process = subprocess.run(['node', str(tool), str(config.relative_to(ROOT)), str(out.relative_to(ROOT))], cwd=ROOT, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, stdout=log, stderr=subprocess.STDOUT, timeout=3600)
        save(out / 'command.json', dict(exitCode=process.returncode))
        assert process.returncode == 0 and reservations.owns(lease) and manifest.read_bytes() == before
        report = read(out / 'report.json')
        assert report['passed'] and not report['pageErrors']
        assert {(c['width'], c['failedUid']) for c in report['cases']} == {(1280, None), (390, 'landsd/233985:0'), (390, 'landsd/240487:0')}
        for c in report['cases']:
            assert c['baseOnlyRestoredCompleteGroup'] and c['completeGroupEvicted'] and c['audit']['frames'] > 0 and not c['audit']['violations']
            if c['failedUid']: assert c['failureKeptAllBasics']
            assert {s['uid']: s['sha256'] for s in c['sources']} == SOURCES
        result = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, passed=True, independentPerPeerFailuresPassed=True, completeAtomicLifecyclePassed=True, physicalAcceptance=False, visualAcceptance=False, installationApproved=False, publication=False, sourceGeometryChanges=0, sourcePoseChanges=0)
        save(out / 'summary.json', result)
        module('one_peking_atomic_lifecycle_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-original-pair-independent-failure-base-auto-eviction-lifecycle', refs, result)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)

if __name__ == '__main__':
    main()
