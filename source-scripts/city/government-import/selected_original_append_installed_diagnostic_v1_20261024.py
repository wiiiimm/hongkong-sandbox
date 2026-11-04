"""Add one exact current installed actor to an unapproved private diagnostic capture.

This does not create a new acquisition record or transfer acceptance. The added
row intentionally lacks native-stage cache keys and cannot be installed anew.
"""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'native-capture', 'uid']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.capture, a.native_capture])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    for name in [a.capture, a.native_capture]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    def take(name, filename):
        path = base / name / filename
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = deepcopy(take(a.capture, 'selection.json.gz'))
    native = next(r for r in take(a.native_capture, 'native-input.json.gz')['rows'] if r['uid'] == a.uid)
    assert a.uid not in [r['uid'] for r in selection['rows']]
    mp = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(mp.read_bytes()) == selection['manifestSHA256']
    refs.append(mp)
    manifest = read(mp)
    matches = []
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        for entry in read(path)['models']:
            if entry['uid'] == a.uid:
                assert entry == native['entry']
                matches.append((path, entry))
    assert len(matches) == 1
    catalogue, entry = matches[0]
    asset = catalogue.parent / entry['asset']
    assert digest(asset.read_bytes()) == entry['sha256']
    tile = next(t for t in manifest['tiles'] if t['id'] == native['building']['tile'])
    tilepath = ROOT / '3d-viewer' / tile['url']
    assert [f for f in read(tilepath)['buildings'] if f['uid'] == a.uid] == [native['building']]
    refs.extend([catalogue, asset, tilepath])
    selection['rows'].append(dict(uid=a.uid, modelId=entry['modelId'], triangles=entry['triangles'], sourceSHA256=entry['sha256'], originalGeometryOnly=True, installedDiagnosticOnly=True, source=dict(building=native['building'], tile=tile['url'], tileSHA256=digest(tilepath.read_bytes())), candidate=dict(path=str(asset.relative_to(ROOT)), entry=entry), native=dict(installedDiagnosticOnly=True, model=dict(triangles=entry['triangles']))))
    save(out / 'selection.json.gz', selection)
    result = dict(uids=[r['uid'] for r in selection['rows']], addedInstalledDiagnosticUid=a.uid, addedInstalledSHA256=entry['sha256'], sourceGeometryChanges=0, dependencyMetadataChanges=0, installationApproved=False, publication=False, qualification='Exact current installed entry, asset and complete form copied solely for private actual-renderer/foundation diagnostics. Native-stage acquisition identity and new acceptance are intentionally absent. Existing installed support metadata remains unchanged.')
    module('append_installed_diagnostic_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'current-installed-actor-added-to-private-original-diagnostics', refs, result)


if __name__ == '__main__':
    main()
