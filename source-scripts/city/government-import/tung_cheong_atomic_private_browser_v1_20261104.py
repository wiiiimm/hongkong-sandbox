"""Private atomic Tung Cheong originals; no source association or publication approval.

Reuse the authenticated complete retained scene, unchanged terrain and source
arrays. Exercise each peer's failure separately before ordinary joint/own views.
"""
import copy
import functools
import http.server
import os
from pathlib import Path
import subprocess
import sys
import threading
import uuid

from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-tung-cheong-atomic-private-browser-v1-20261104'
PRIOR = 'government-xl-tung-cheong53799-private-browser-v1-20261103'
PREP = 'government-xl-tung-cheong-pair-preparation-v1-20261104'
SELECT = 'government-xl-tung-cheong-paired-diagnostic-selection-v1-20261104'
HIGH, LOW = 'landsd/53799:0', 'landsd/223636:0'


def main():
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    leasefile = HERE / 'local' / (BATCH + '-control') / 'reservation.json'
    assert not out.exists() and not local.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    prepared = take(PREP, BASE / PREP / 'summary.json')
    nominated = take(SELECT, BASE / SELECT / 'summary.json')
    assert prepared['diagnosticOnly'] and prepared['identityAccepted'] is False
    assert nominated['nativeLowViewerUid'] is None and nominated['sourceAssociationAccepted'] is False
    resources = sorted(set(nominated['leaseResources']) | {'server:127.0.0.1:4177'})
    if '--owned' not in sys.argv:
        assert not leasefile.parent.exists()
        claim = reservations.claim('tung-cheong-atomic-browser-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], leasefile, [sys.executable, __file__, '--owned'])
    lease = read(leasefile)
    assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_bytes = manifest.read_bytes()
    assert digest(manifest_bytes) == prepared['currentManifestSHA256'] == nominated['currentManifestSHA256']
    refs.append(manifest)
    selection = take(PREP + '-runtime', BASE / (PREP + '-runtime') / 'selection.json.gz')
    assert selection['manifestSHA256'] == digest(manifest_bytes)
    rows = selection['rows']
    assert [r['uid'] for r in rows] == [HIGH, LOW]
    take(PREP, BASE / PREP / 'unchanged-complete-four-world-source-arrays.json')
    scope = take(PREP + '-terrain-scope', BASE / (PREP + '-terrain-scope') / 'scope.json')
    forms = take(PREP + '-terrain-scope', BASE / (PREP + '-terrain-scope') / 'form-obligations.json.gz')
    prior_scope_batch = 'government-xl-tung-cheong53799-post-inset-v1-20261103-scope'
    old_scope = take(prior_scope_batch, BASE / prior_scope_batch / 'scope.json')
    assert scope == old_scope
    old_forms = take(prior_scope_batch, BASE / prior_scope_batch / 'form-obligations.json.gz')
    assert forms == old_forms and len(forms) == 40
    checks_batch = 'government-xl-tung-cheong53799-full-neighbours-v1-20261103-checks'
    checks = take(checks_batch, BASE / checks_batch / 'summary.json')
    assert checks['forms'] == len(forms) and not checks['basicFlags']
    assert set(checks['nativeResolved']) == set(checks['requiredNativeUids']) == set(scope['touchingNativeUids'])
    assert all(r['passed'] is True for r in checks['nativeRows'])
    previous = HERE / 'local' / PRIOR
    config = take(PRIOR, previous / 'browser-config-390.json')
    assert config['additionalRetainedUids'] == scope['touchingNativeUids']
    terrain = take(PREP + '-terrain', BASE / (PREP + '-terrain') / 'summary.json')
    assert terrain['candidateBytesUnchanged'] is True and terrain['additionalExplicitCompanionUids'] == [LOW]
    assert len(config['terrain']) == 1 and config['terrain'][0]['sha256'] == terrain['candidate']['sha256']
    assert config['terrain'][0]['replacesMany'] == terrain['replacedNativeTerrain']
    for t in config['terrain']:
        source = ROOT / t['source']
        assert digest(source.read_bytes()) == t['sha256']
        refs.append(source)
        for replaced in t['replacesMany']:
            source = ROOT / replaced['path']
            assert digest(source.read_bytes()) == replaced['sha256']
            refs.append(source)
    source_scope = take(PREP + '-source-scope', BASE / (PREP + '-source-scope') / 'summary.json')
    assert all(r['currentNativeActorsChecked'] == 7106 for r in source_scope['rows'])
    assert {n['uid'] for r in source_scope['rows'] for n in r['nearbyNativeActors']} <= set(scope['touchingNativeUids'])
    catalogue = take(PRIOR, previous / 'catalogue.json')
    assert len(catalogue['models']) == 1 and catalogue['models'][0]['uid'] == HIGH
    old_high = copy.deepcopy(catalogue['models'][0])
    entries = []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in rows:
            native = row['native']
            records = db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s', (native['cacheKey'],)).fetchall()
            assert len(records) == 1 and records[0][1] == native['resultSha']
            entry = copy.deepcopy(row['candidate']['entry'])
            entry.update(sourceTile=records[0][0], priority='landmark', proceduralWindows=False)
            assert entry['sha256'] == row['sourceSHA256'] and entry['rootTranslation'] == [-834500, 0, 816500]
            assert entry['activationGroup'] == sorted([HIGH, LOW])
            assert all(entry.get(k) is False for k in ['publicationApproved', 'placementReviewed', 'identityReviewApproved', 'sourceIdentityReviewed'])
            assert not any(entry.get(k) for k in ['supportDependencies', 'retainedBasicSupportDependencies', 'suppressesBuildingUids', 'partialSource', 'embeddedModel', 'embeddedModels', 'verticalPlacementOffsetHKPD'])
            if row['uid'] == HIGH:
                comparison = copy.deepcopy(entry)
                del comparison['activationGroup']
                assert comparison == old_high
            tile = ROOT / '3d-viewer' / row['source']['tile']
            assert digest(tile.read_bytes()) == row['source']['tileSHA256']
            assert [f for f in read(tile)['buildings'] if f['uid'] == row['uid']] == [row['source']['building']]
            assert row['source']['building'] in forms
            refs.append(tile)
            asset = ROOT / row['candidate']['path']
            assert digest(asset.read_bytes()) == entry['sha256']
            refs.append(asset)
            target = local / entry['asset']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(asset.read_bytes())
            entries.append(entry)
    catalogue.update(models=entries, counts=dict(packedModels=2))
    save(local / 'catalogue.json', catalogue)
    save(local / 'catalogue-index.json', dict(models=2, catalogues=['catalogue.json']))
    save(local / 'source-forms.json', [r['source']['building'] for r in rows])
    save(local / 'validation-forms.json', {r['uid']: r['source'] for r in rows})
    config.update(stage=str(local.relative_to(ROOT)) + '/', catalogueURL='city/data/official-models/' + BATCH + '/catalogue.json', browserUids=[HIGH, LOW], jointUids=[HIGH, LOW], failureTestUids=[], viewportWidths=[1280,390], atomicCaptureDirectionByViewport={1280:[-1,1.8,-1],390:[-1,2.6,-1]})
    config['retainedBuildingUids'] = [u for u in config['retainedBuildingUids'] if u != LOW]
    assert set(config['retainedBuildingUids']) == {f['uid'] for f in forms} - {HIGH, LOW, *scope['touchingNativeUids']}
    config['captureDirectionByModel'][LOW] = [-1, 1.8, -1]
    save(local / 'config.json', config)
    out.mkdir(parents=True)
    tool = HERE / 'ronsdale_three_live_browser_v15_20261026.mjs'
    atomic = HERE / 'model_atomic_lifecycle_browser_v4_20261101.mjs'
    parser = HERE / 'original_private_catalogue_preflight_v1_20261103.mjs'
    closure = HERE / 'private_viewer_runtime_closure_v1_20261028.mjs'
    refs.extend([tool, atomic, parser, closure])
    subprocess.run(['node', str(parser), str((local / 'catalogue.json').relative_to(ROOT))], cwd=ROOT, check=True)
    closurepath = out / 'runtime-input-closure.json'
    subprocess.run(['node', str(closure), 'capture', str(closurepath.relative_to(ROOT))], cwd=ROOT, check=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
        def copyfile(self, source, outputfile):
            try: super().copyfile(source, outputfile)
            except (BrokenPipeError, ConnectionResetError): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1',4177), functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
    thread = threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    def run_node(name, argv):
        assert reservations.owns(lease) and manifest.read_bytes() == manifest_bytes
        save(out / 'state.json', dict(running=True, phase=name))
        print('starting ' + name, flush=True)
        with (out / (name + '.log')).open('w') as log:
            completed = subprocess.run(['node', *argv], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=1800, env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
        save(out / (name + '-command.json'), dict(exitCode=completed.returncode))
        assert completed.returncode == 0, name
    try:
        run_node('atomic-lifecycle', [str(atomic), str((local/'config.json').relative_to(ROOT)), str((out/'atomic-lifecycle').relative_to(ROOT))])
        atomic_report = read(out / 'atomic-lifecycle/report.json')
        assert atomic_report['passed'] and not atomic_report['pageErrors'] and len(atomic_report['cases']) == 3
        assert {c['failedUid'] for c in atomic_report['cases'] if c['width']==390} == {HIGH,LOW}
        assert all(c['failureKeptAllBasics'] for c in atomic_report['cases'] if c['width']==390)
        for width in [1280,390]:
            cfg = local / ('browser-config-' + str(width) + '.json')
            save(cfg, dict(**{k:v for k,v in config.items() if k not in ['viewportWidths','doc']},viewportWidths=[width],doc=str((out/str(width)).relative_to(ROOT))+'/'))
            run_node('browser-' + str(width), [str(tool),'staged',str(cfg.relative_to(ROOT))])
            report = read(out / str(width) / 'staged-browser.json')
            assert report['passed'] and not report['errors']
            assert len([v for v in report['views'] if 'time' in v]) == 4
            assert len(report['retainedNativeOwnViews']) == 2*len(scope['touchingNativeUids'])
            assert {v['uid'] for v in report['retainedNativeOwnViews']} == set(scope['touchingNativeUids'])
        assert reservations.owns(lease) and manifest.read_bytes() == manifest_bytes
        subprocess.run(['node',str(closure),'verify',str(closurepath.relative_to(ROOT))],cwd=ROOT,check=True)
        refs.append(closurepath)
        refs.extend(ROOT/p for p in read(closurepath)['inputHashes'])
        refs.extend(p for p in local.rglob('*') if p.is_file())
        result = dict(uids=[HIGH,LOW],sourceSHA256ByUid={e['uid']:e['sha256'] for e in entries},diagnosticOnly=True,publication=False,installationApproved=False,identityAccepted=False,sourceAssociationAccepted=False,nativeLowViewerUid=None,physicalAcceptance=False,visualAcceptance=False,currentManifestSHA256=digest(manifest_bytes),retainedNativeUids=scope['touchingNativeUids'],fullAffectedBaseForms=len(forms),completeAtomicLifecycleCases=3,sourceGeometryChanges=0,sourcePoseChanges=0,terrainBytesChanged=0,leaseResources=resources,qualification=__doc__)
        save(out/'state.json',dict(running=False,completed=True))
        save(out/'summary.json',result)
        module('tung_cheong_atomic_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-atomic-paired-original-complete-retained-scene',list(dict.fromkeys(refs)),result)
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


if __name__ == '__main__': main()
