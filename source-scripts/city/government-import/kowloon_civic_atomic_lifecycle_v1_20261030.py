"""Exercise all five exact original peers failing/retrying; private routes only."""
import functools
import http.server
import json
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-kowloon-city-civic-five-after-fuying-'
PRIOR = PREFIX + 'unapproved-atomic-private-browser-v1-20261030'
BATCH = PREFIX + 'atomic-lifecycle-v1-20261030'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'


def main():
    _, pins = authenticate(BASE / PRIOR)
    source = HERE / 'local' / PRIOR / 'browser-config-1280.json'
    assert digest(source.read_bytes()) == pins[str(source.relative_to(ROOT))]
    config = read(source)
    uids = sorted(read(ROOT / config['stage'] / 'catalogue.json')['models'], key=lambda r: r['uid'])
    uids = [r['uid'] for r in uids]
    assert len(uids) == 5
    if '--owned' not in sys.argv:
        assert not DOC.exists() and not LOCAL.exists()
        resources = ['building:' + uid for uid in uids] + ['terrain:city/data/terrain.json', 'server:127.0.0.1:4177']
        claim = reservations.claim(BATCH + '-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        lease = claim['reservation']
        save(LEASE, json.loads(json.dumps(lease, default=str)))
        try:
            subprocess.run([sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'),
                            str(LEASE), sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        return
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    config.update(diagnosticOnly=True, publication=False, expectedUids=uids)
    save(DOC / 'configuration.json', config)
    tool = HERE / 'kowloon_civic_atomic_lifecycle_browser_v1_20261030.mjs'
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def copyfile(self, source, outputfile):
            try:
                super().copyfile(source, outputfile)
            except (BrokenPipeError, ConnectionResetError):
                pass
    assert config['viewerURL'] == 'http://127.0.0.1:4177/city.html'
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 4177), functools.partial(Handler, directory=str(ROOT / '3d-viewer')))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with (DOC / 'worker.log').open('w') as log:
            subprocess.run(['node', str(tool), str((DOC / 'configuration.json').relative_to(ROOT)),
                            str((DOC / 'browser').relative_to(ROOT))], cwd=ROOT, stdout=log,
                           stderr=subprocess.STDOUT, timeout=2400, check=True)
        report = read(DOC / 'browser/report.json')
        assert report['passed'] and len(report['cases']) == 6
        assert {r['failedUid'] for r in report['cases'] if r['width'] == 390} == set(uids)
        refs = [Path(__file__), tool, source, BASE / PRIOR / 'result.json']
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha
            refs.append(ROOT / path)
        result = dict(uids=uids, cases=6, diagnosticOnly=True, publication=False,
                      installationApproved=False, sourceGeometryChanges=0,
                      qualification='Five-peer current runtime atomic availability, each peer download failure/retry, Base-only, eviction and collision-map lifecycle. Private exact assets/terrain only; separate visual, identity and installation review required.')
        assert reservations.owns(lease)
        module('civic_lifecycle_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'private-five-original-atomic-availability-lifecycle', refs, result)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)


if __name__ == '__main__':
    main()
