"""Bind ROOT's actual live export inspection; never run before viewing exports."""
import argparse, os
from pathlib import Path
from run import ROOT, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from one_peking_cycle_runtime_contract_v1_20261101 import verify_atomic
from one_peking_cycle_retained_contract_v2_20261101 import SOURCES

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inspection', required=True)
    args = p.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    cfgpath = (ROOT / os.environ['ORIGINAL_INSTALL_CONFIG']).resolve()
    assert cfgpath.is_relative_to(base)
    cfg = read(cfgpath)
    assert cfg['sources'] == SOURCES
    installed = base / (cfg['prefix'] + '-original-installed-v1-' + cfg['date'])
    receipt, pins = authenticate(installed)
    assert receipt['sourceSHA256ByUid'] == SOURCES and receipt['publication']
    observed_path = (ROOT / args.inspection).resolve()
    assert observed_path.is_relative_to(base)
    observed = read(observed_path)
    assert observed['reviewer'] == 'Codex ROOT' and observed['allDeclaredExportsActuallyInspected']
    source_images, retained_images, atomic_images = [], [], []
    retained = set(cfg['retainedNativeUids'])
    def image(path):
        result = dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
        assert result['sha256'] == pins[result['path']]
        return result
    for width in [390, 1280]:
        folder = installed / ('viewport-' + str(width))
        report = read(folder / 'live-browser.json')
        assert report['passed'] and not report['errors']
        for v in report['views']:
            if 'time' not in v: continue
            assert v['uid'] == v['pick'] == v['collision'] and v['sourceSHA256'] == SOURCES[v['uid']]
            assert v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces']
            source_images.append(dict(uid=v['uid'], width=width, time=v['time'], **image(folder / v['file'])))
        for v in report['retainedNativeOwnViews']:
            assert v['uid'] in retained and v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces'] and not v['overflow']
            assert all(v['meshVisibility']) and not any(v['wireframeFlags'])
            retained_images.append(dict(uid=v['uid'], width=width, time=v['time'], **image(folder / v['file'])))
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    models = [m for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models'] if m['uid'] in SOURCES]
    atomic = read(installed / 'atomic-live/report.json')
    assert atomic['liveInstalledHTTP'] and atomic['catalogueAndTerrainSubstitution'] is False and verify_atomic(atomic, models)
    atomic_images = [image(installed / 'atomic-live' / (c['name'] + '.png')) for c in atomic['cases']]
    for field, rows, count in [('sourceImagesActuallyViewed', source_images, 8), ('retainedImagesActuallyViewed', retained_images, 144), ('atomicImagesActuallyViewed', atomic_images, 3)]:
        actual = {(r['path'], r['sha256']) for r in rows}
        assert len(rows) == len(actual) == count
        assert actual == {(r['path'], r['sha256']) for r in observed[field]} and len(observed[field]) == count
    for q in observed['inspectionSheetsActuallyViewed']:
        assert digest((ROOT / q['path']).read_bytes()) == q['sha256']
    output = installed / 'ROOT-LIVE-EXPORT-INSPECTION.json'
    assert not output.exists()
    save(output, dict(reviewer='ROOT', visualAcceptance=True, producer=dict(path=str(Path(__file__).resolve().relative_to(ROOT)), sha256=digest(Path(__file__).resolve().read_bytes())),
        imagesActuallyViewed=source_images, retainedImagesActuallyViewed=retained_images, atomicImagesActuallyViewed=atomic_images,
        inspectionSheetsActuallyViewed=observed['inspectionSheetsActuallyViewed'], inspectionMethod=observed['inspectionMethod'], observations=observed['limitations'],
        boundObservation=dict(path=str(observed_path.relative_to(ROOT)), sha256=digest(observed_path.read_bytes()))))

if __name__ == '__main__':
    main()
