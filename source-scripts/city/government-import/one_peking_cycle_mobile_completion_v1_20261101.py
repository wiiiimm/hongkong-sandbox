"""Finish the normal mobile preview only after independent atomic retry tests.

Reuse the completed, hash-bound desktop viewport. Preserve the failed combined
attempt and every source/terrain byte. This performs no production publication.
"""
import argparse, copy, functools, http.server, os, shutil, subprocess, sys, threading, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from one_peking_cycle_retained_contract_v2_20261101 import SOURCES, SUPPORTS
from original_supported_catalogue_scope_v1_20261024 import verify as verify_graph

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-one-peking-after-twin-'
PREVIOUS = P + 'cycle-private-browser-v4-20261101'
LIFECYCLE = P + 'cycle-atomic-lifecycle-v1-20261101'
BATCH = P + 'cycle-mobile-completion-v1-20261101'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    out, local, previous = BASE / BATCH, HERE / 'local' / BATCH, HERE / 'local' / PREVIOUS
    assert not out.exists()
    refs, pins, receipts = [Path(__file__)], {}, {}
    def take(batch, path):
        if batch not in pins:
            receipts[batch], pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    lifecycle = take(LIFECYCLE, BASE / LIFECYCLE / 'summary.json')
    assert lifecycle['passed'] and lifecycle['independentPerPeerFailuresPassed'] and lifecycle['completeAtomicLifecyclePassed']
    assert lifecycle['sourceSHA256ByUid'] == SOURCES
    report = take(LIFECYCLE, BASE / LIFECYCLE / 'report.json')
    assert report['passed'] and not report['pageErrors'] and len(report['cases']) == 3
    assert {(c['width'], c['failedUid']) for c in report['cases']} == {(1280, None), (390, 'landsd/233985:0'), (390, 'landsd/240487:0')}
    for c in report['cases']:
        assert c['baseOnlyRestoredCompleteGroup'] and c['completeGroupEvicted'] and c['audit']['frames'] > 0 and not c['audit']['violations']
        assert all(t['active'] in [[], sorted(SOURCES)] for t in c['audit']['transitions'])
        assert {s['uid']: s['sha256'] for s in c['sources']} == SOURCES
        if c['failedUid']: assert c['failureKeptAllBasics']
    cat = take(PREVIOUS, previous / 'catalogue.json')
    cfg = take(PREVIOUS, previous / 'browser-config-390.json')
    assert verify_graph(cat['models'], SOURCES, SUPPORTS)
    assert all(all(m[k] is False for k in ['publicationApproved', 'placementReviewed', 'identityReviewApproved', 'sourceIdentityReviewed']) for m in cat['models'])
    configuration = take(PREVIOUS, BASE / 'government-xl-one-peking-cycle-private-browser-config-v4-20261101.json')
    retained = set(configuration['retainedNativeUids'])
    assert len(retained) == 36 and set(cfg['additionalRetainedUids']) == retained
    desktop_path = BASE / PREVIOUS / '1280/staged-browser.json'
    desktop = take(PREVIOUS, desktop_path)
    assert receipts[PREVIOUS]['desktopPassed'] and not receipts[PREVIOUS]['mobilePassed']
    assert desktop['passed'] and not desktop['errors']
    def verify_viewport(viewport, width):
        source_views = [v for v in viewport['views'] if 'time' in v]
        assert len(source_views) == 4 and {(v['uid'], v['time']) for v in source_views} == {(u, t) for u in SOURCES for t in ['15:00', '22:00']}
        for v in source_views:
            assert v['width'] == width and v['uid'] == v['pick'] == v['collision']
            assert v['sourceSHA256'] == SOURCES[v['uid']] and v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces']
        native_views = viewport['retainedNativeOwnViews']
        assert len(native_views) == 72 and {(v['uid'], v['time']) for v in native_views} == {(u, t) for u in retained for t in ['15:00', '22:00']}
        assert all(v['width'] == width and v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces'] for v in native_views)
    verify_viewport(desktop, 1280)
    for v in [*desktop['views'], *desktop['retainedNativeOwnViews']]:
        if 'file' in v:
            p = desktop_path.parent / v['file']
            assert digest(p.read_bytes()) == pins[PREVIOUS][str(p.relative_to(ROOT))]
            refs.append(p)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[PREVIOUS][str(manifest.relative_to(ROOT))]
    before = manifest.read_bytes()
    refs.append(manifest)
    # Bind actual production constructors, not just the source catalogue URL.
    metrics_batch = P + 'cycle-drawn-foundations-v2-20261101'
    metrics = take(metrics_batch, BASE / metrics_batch / 'metrics.json')
    for path, sha in metrics['inputHashes'].items():
        p = ROOT / path
        assert digest(p.read_bytes()) == sha
        refs.append(p)
    resources = read(previous / 'reservation.json')['resources']
    lease_path = local / 'reservation.json'
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('one-peking-normal-mobile-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lease_path, [sys.executable, __file__, '--owned'])
    lease = read(lease_path)
    assert reservations.owns(lease) and set(resources) == set(lease['resources'])
    for name in ['catalogue.json', 'catalogue-index.json', 'source-forms.json', 'validation-forms.json']:
        source = previous / name
        take(PREVIOUS, source)
        shutil.copyfile(source, local / name)
    for m in cat['models']:
        source = previous / m['asset']
        assert digest(source.read_bytes()) == SOURCES[m['uid']]
        target = local / m['asset']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        refs.extend([source, target])
    cfg = copy.deepcopy(cfg)
    cfg.update(stage=str(local.relative_to(ROOT)) + '/', catalogueURL='city/data/official-models/' + BATCH + '/catalogue.json', viewportWidths=[390], doc=str((out / '390').relative_to(ROOT)) + '/', failureTestUids=[])
    for t in cfg['terrain']:
        path = ROOT / t['source']
        assert digest(path.read_bytes()) == t['sha256']
        refs.append(path)
    save(local / 'browser-config-390.json', cfg)
    tool = HERE / 'ronsdale_three_live_browser_v25_20261101.mjs'
    refs.extend([tool, local / 'browser-config-390.json'])
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
        with (out / 'browser-390.log').open('w') as log:
            process = subprocess.run(['node', str(tool), 'staged', str((local / 'browser-config-390.json').relative_to(ROOT))], cwd=ROOT, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, stdout=log, stderr=subprocess.STDOUT, timeout=1800)
        save(out / 'command-390.json', dict(exitCode=process.returncode))
        assert process.returncode == 0 and reservations.owns(lease) and manifest.read_bytes() == before
        mobile = read(out / '390/staged-browser.json')
        assert mobile['passed'] and not mobile['errors']
        verify_viewport(mobile, 390)
        for p in refs:
            rel = str(p.relative_to(ROOT))
            for batch in pins:
                if rel in pins[batch]: assert digest(p.read_bytes()) == pins[batch][rel]
        summary = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, previewOnly=True, allBrowserDiagnosticsPassed=True, desktopEvidenceBatch=PREVIOUS, desktopReport=str(desktop_path.relative_to(ROOT)), mobileReport=str((out / '390/staged-browser.json').relative_to(ROOT)), independentAtomicFailureEvidence=LIFECYCLE, retainedNativeUids=sorted(retained), sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False, identityAccepted=False, visualAcceptance=False, installationApproved=False, publication=False,
            qualification='Complete unchanged desktop viewport reused by exact hashes; normal full mobile source2/retained36/picking/collision/day-night preview passed. Independent per-peer503/retry, complete BASIC fallback, Base/Auto and eviction must remain bound to the separate atomic lifecycle receipt. All approval flags remain false. Export inspection, final source/physical review and guarded publication are separate.')
        save(out / 'summary.json', summary)
        refs.extend(p for p in local.rglob('*') if p.is_file() and p.name != 'reservation.json')
        module('one_peking_normal_mobile_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-private-desktop-mobile-preview-with-independent-atomic-retry-evidence', list(dict.fromkeys(refs)), summary)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)

if __name__ == '__main__':
    main()
