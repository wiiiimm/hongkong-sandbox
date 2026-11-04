"""Run the separate five-source atomic lifecycle and retained-owner fallback test.

Requires completed private success views. This adds no source/physical or
publication approval and does not alter installed catalogues or terrain.
"""
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
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-original-atomic-lifecycle-v1-20261103'
LOCAL = HERE/'local'/BATCH
PREVIEW = 'government-xl-silvercord-lippo-private-six-part-browser-v4-20261103'
INVENTORY = 'government-xl-after-june-current-native-bounds-reused-v1-20261103'


def owned():
    lease = read(LOCAL/'reservation.json')
    assert reservations.owns(lease) and not (BASE/BATCH).exists()
    preview, pins = authenticate(BASE/PREVIEW)
    assert preview['diagnosticOnly'] and not preview['physicalAcceptance'] and not preview['publication']
    refs = [Path(__file__),BASE/PREVIEW/'result.json']
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    config = copy.deepcopy(take(HERE/'local'/PREVIEW/'browser-config-390.json'))
    catalogue = take(ROOT/config['stage']/'catalogue.json')
    assert len(catalogue['models']) == 5 and config['viewerURL'] == 'http://127.0.0.1:4177/city.html'
    assert len(config['catalogueReplacements']) == 1
    for width in [1280,390]:
        report = take(BASE/PREVIEW/str(width)/'staged-browser.json')
        assert report['passed'] and not report['errors']
    inventory, module_pins = authenticate(BASE/INVENTORY)
    refs.append(BASE/INVENTORY/'result.json')
    hashes = {p.removeprefix('3d-viewer/'):h for p,h in module_pins.items()
              if p.startswith('3d-viewer/city/') and p.endswith('.js')}
    assert hashes
    for path,sha in hashes.items():
        file = ROOT/'3d-viewer'/path
        assert digest(file.read_bytes()) == sha
        refs.append(file)
    config.update(diagnosticOnly=True,publication=False,privateSourceBoundTileOverlays=[],
        privateFoundationTileOverlays=[],availabilityOverlays=[],productionGeometryInputHashes=hashes)
    config_path = LOCAL/'atomic-config.json'
    save(config_path,config)
    tool = HERE/'silvercord_lippo_retained_owner_atomic_lifecycle_v1_20261103.mjs'
    refs.append(tool)
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == inventory['currentManifestSHA256']
    public = {manifest:digest(manifest.read_bytes())}
    for url in read(manifest)['officialModelCatalogues']:
        p = ROOT/'3d-viewer'/url
        public[p] = digest(p.read_bytes())
    for entry in config['terrain']:
        take(ROOT/entry['source'])
    for entry in catalogue['models']:
        path = ROOT/config['stage']/entry['asset']
        assert digest(path.read_bytes()) == entry['sha256']
        refs.append(path)
    for update in config['catalogueReplacements']:
        take(ROOT/update['source'])
        p = ROOT/'3d-viewer'/update['url']
        assert public[p] == update['beforeSHA256']
    server = thread = None
    try:
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*unused):
                pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        (BASE/BATCH).mkdir(parents=True)
        with (BASE/BATCH/'browser.log').open('w') as log:
            result = subprocess.run(['node',str(tool),str(config_path.relative_to(ROOT)),str((BASE/BATCH/'atomic').relative_to(ROOT))],
                cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=3500,
                env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
        save(BASE/BATCH/'command.json',dict(exitCode=result.returncode))
        assert result.returncode == 0
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=5)
    report = read(BASE/BATCH/'atomic/report.json')
    assert report['passed'] and not report['pageErrors'] and len(report['cases']) == 6
    assert all(r['retainedOwnerActive']['active'] and r['retainedOwnerRecovered']['active']
               and not r['retainedOwnerBaseFallback']['active'] and not r['retainedOwnerEvictedFallback']['active']
               for r in report['cases'])
    assert sum(r['failedUid'] is not None and not r['retainedOwnerFailedFallback']['active'] for r in report['cases']) == 5
    for path,sha in public.items():
        assert digest(path.read_bytes()) == sha
    assert reservations.owns(lease)
    result = dict(uids=[m['uid'] for m in catalogue['models']],retainedOwnerUid=config['catalogueReplacements'][0]['ownerUid'],
        diagnosticOnly=True,atomicSoftwareCasesPassed=6,eachMobileSourceDeniedAndRetried=True,
        retainedOwnerFallbackAndRecoveryPassed=True,baseOnlyAndEvictionPassed=True,publicFilesChanged=False,
        actualExportsStillRequireInspection=True,physicalAcceptance=False,visualAcceptance=False,
        installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0)
    save(BASE/BATCH/'summary.json',result)
    refs.extend(public)
    refs += [config_path,HERE/'original_foundation_group_lifecycle_checks_v1_20261102.mjs',
             HERE/'elegant_live_fallback_checks_v1_20261028.mjs',HERE/'private_foundation_tile_routes_v1_20261102.mjs']
    module('silvercord_original_atomic_diagnostic',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'exact-original-five-part-atomic-and-retained-owner-fallback-software-diagnostic',list(dict.fromkeys(refs)),result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE/BATCH).exists()
        # The completed preview's exact source/parent/server scope is retained.
        previous = read(HERE/'local'/PREVIEW/'reservation.json')
        resources = {r for r in previous['resources'] if not r.startswith('immutable-source-proof:')}
        resources.add('immutable-source-proof:'+BATCH)
        claim = reservations.claim('silvercord-original-atomic-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
