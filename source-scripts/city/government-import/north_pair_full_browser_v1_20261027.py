"""Fresh full source/retained views; diagnostic only, never source acceptance."""
import copy
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from run import ROOT, HERE, read, save, digest, reservations
from primrose_compound_foundation_v2_20261015 import module
from original_availability_overlay_v1_20261027 import stage

PREFIX = 'government-xl-west-kowloon-north-pair-after-ocean-'
BATCH = PREFIX + 'full-existing-peer-browser-v1-20261027'
BASE = ROOT / 'docs/astra-city/government-import'


def main():
    doc, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not doc.exists() and not local.exists(), 'Never restart a prior browser run'
    atomic_doc = BASE / (PREFIX + 'atomic-existing-peer-browser-v1-20261027')
    atomic_report = read(atomic_doc / 'atomic/report.json')
    atomic_receipt = BASE / (PREFIX + 'atomic-existing-peer-receipt-v1-20261027') / 'result.json'
    assert atomic_receipt.exists() and atomic_report['passed'] and not atomic_report['pageErrors']
    assert len(atomic_report['cases']) == 4
    fixture_dir = BASE / (PREFIX + 'availability-fixture-v1-20261027')
    fixture, spec = read(fixture_dir / 'summary.json'), read(fixture_dir / 'overlay-spec.json')
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    assert digest(manifest_path.read_bytes()) == fixture['manifestSHA256']
    stage(ROOT, spec, copy.deepcopy(manifest), {}, Path.read_bytes)
    runtime = BASE / (PREFIX + 'three-member-runtime-v2-20261027')
    selection = json.loads(gzip.decompress((runtime / 'selection.json.gz').read_bytes()))
    assert digest((runtime / 'selection.json.gz').read_bytes()) == fixture['selectionSHA256']
    scope = read(BASE / (PREFIX + 'three-member-scope-v2-20261027') / 'scope.json')
    retained = sorted(scope['touchingNativeUids'])
    assert len(retained) == 67 and 'landsd/272986:0' in retained
    resources = set(read(BASE / (PREFIX + 'native-fallback-plan-v1-20261027.json'))['resources'])
    resources.update('building:' + u for u in retained)
    claim = reservations.claim('north-full-browser-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
    assert claim.get('ok'), 'Source/retained terrain currently reserved'
    lease = claim['reservation']
    lease_path = local / 'reservation.json'
    save(lease_path, json.loads(json.dumps(lease, default=str)))
    try:
        doc.mkdir()
        source_catalogue = ROOT / fixture['privateCatalogue']
        catalogue = read(source_catalogue)
        save(local / 'catalogue.json', catalogue)
        save(local / 'source-forms.json', [r['source']['building'] for r in selection['rows']])
        refs = [Path(__file__), manifest_path, fixture_dir / 'summary.json', fixture_dir / 'overlay-spec.json',
                ROOT / spec['source'], atomic_receipt, atomic_doc / 'atomic/report.json']
        for m in catalogue['models']:
            source = source_catalogue.parent / m['asset']
            raw = source.read_bytes()
            assert digest(raw) == m['sha256'] and len(raw) == m['bytes']
            target = local / m['asset']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            refs.append(source)
        found = set()
        for url in manifest['officialModelCatalogues']:
            path = ROOT / '3d-viewer' / url
            c = read(path)
            for m in c['models']:
                if m['uid'] not in retained:
                    continue
                assert m['uid'] not in found
                found.add(m['uid'])
                asset = path.parent / m['asset']
                assert digest(asset.read_bytes()) == m['sha256']
                refs.extend([path, asset])
        assert found == set(retained)
        atomic_config = read(HERE / 'local' / (PREFIX + 'atomic-existing-peer-browser-v1-20261027') / 'config.json')
        for t in atomic_config['terrain']:
            refs.append(ROOT / t['source'])
        config = dict(stage=str(local.relative_to(ROOT)) + '/',
                      catalogueURL='city/data/official-models/private-north-full-v1/catalogue.json',
                      viewerURL='http://127.0.0.1:4177/city.html', terrain=atomic_config['terrain'],
                      availabilityOverlays=[spec], additionalRetainedUids=retained,
                      failureTestUids=[], catalogueReplacements=[], nativeSupportUidsByModel={}, fitBox=True)
        tool = HERE / 'ronsdale_three_live_browser_v16_20261027.mjs'
        refs.append(tool)
        refs.extend((ROOT / '3d-viewer/city').glob('*.js'))
        pins = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in refs}
        for width in [1280, 390]:
            # Each bounded child releases its lease on completion. The next
            # viewport is a distinct phase and must claim a fresh lease.
            if width == 390:
                assert not reservations.owns(lease)
                for path, sha in pins.items():
                    assert digest((ROOT / path).read_bytes()) == sha
                claim = reservations.claim('north-full-browser-mobile-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
                assert claim.get('ok')
                lease = claim['reservation']
                save(lease_path, json.loads(json.dumps(lease, default=str)))
            config_path = local / f'config-{width}.json'
            save(config_path, dict(**config, viewportWidths=[width], doc=str((doc / str(width)).relative_to(ROOT)) + '/'))
            command = ['node', str(tool), 'staged', str(config_path.relative_to(ROOT))]
            with (doc / f'browser-{width}.log').open('w') as log:
                subprocess.run([sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'), str(lease_path), *command],
                               cwd=ROOT, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'},
                               stdout=log, stderr=subprocess.STDOUT, check=True, timeout=7200)
            report = read(doc / str(width) / 'staged-browser.json')
            assert report['passed'] and not report['errors']
            views = report['retainedNativeOwnViews']
            assert len(views) == 134 and {(v['uid'], v['time']) for v in views} == {(u, t) for u in retained for t in ['15:00', '22:00']}
            assert all(v['active'] and v['visible'] and v['fallbackFaces'] == 0 for v in views)
            refs.extend([config_path, doc / str(width) / 'staged-browser.json', doc / f'browser-{width}.log'])
            print('Full browser passed', width, flush=True)
        for path, sha in pins.items():
            assert digest((ROOT / path).read_bytes()) == sha
        assert not reservations.owns(lease)
        claim = reservations.claim('north-full-browser-receipt-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
        assert claim.get('ok')
        lease = claim['reservation']
        assert reservations.owns(lease)
        refs.extend(p for p in doc.rglob('*.png'))
        module('north_full_browser_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'private-source-and-67-retained-full-desktop-mobile-diagnostic', refs,
            dict(uids=[m['uid'] for m in catalogue['models']], retainedUids=retained,
                 desktopMobileDiagnosticsPassed=True, physicalAcceptance=False, visualAcceptance=False,
                 installationApproved=False, publication=False, sourceGeometryChanges=0, newlyInstalled=0))
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
