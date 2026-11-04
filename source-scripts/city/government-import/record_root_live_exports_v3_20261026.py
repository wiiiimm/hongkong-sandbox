"""Record actually opened live source AND retained-native exports; never auto-run."""
import argparse, os
from pathlib import Path
from run import ROOT, read, save, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--accept-exports-actually-viewed-by-root', action='store_true', required=True)
    p.add_argument('--observation', action='append', required=True)
    p.add_argument('--install-version', required=True, choices=['v1','v2','v3'])
    a = p.parse_args(); base = ROOT / 'docs/astra-city/government-import'
    config = (ROOT / os.environ['ORIGINAL_INSTALL_CONFIG']).resolve(); assert config.is_relative_to(base)
    cfg = read(config); retained = set(cfg['retainedNativeUids'])
    review = read(base / cfg['review'] / 'ROOT-SOURCE-REVIEW.json')
    expected = review['retainedNativeEntries']; assert set(expected) == retained
    installed = base / (cfg['prefix'] + '-original-installed-' + a.install_version + '-' + cfg['date'])
    assert installed.exists(); images, retained_images = [], []
    for width in [390, 1280]:
        folder = installed / ('viewport-' + str(width)); report = read(folder / 'live-browser.json')
        assert report['passed'] and not report['errors']
        for v in [v for v in report['views'] if 'time' in v]:
            assert v['uid'] in cfg['sources'] and v['sourceSHA256'] == cfg['sources'][v['uid']]
            assert v['pick'] == v['collision'] == v['uid'] and v['solidAppearance']
            assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
            path = (folder / v['file']).resolve(); assert path.is_relative_to(folder)
            images.append(dict(uid=v['uid'], width=width, time=v['time'], path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
        for v in report['retainedNativeOwnViews']:
            assert v['uid'] in retained; entry = expected[v['uid']]
            assert v['sourceSHA256'] == entry['sha256'] and v['originalTriangles'] == entry['triangles']
            assert v['active'] and v['visible'] and v['fullyFramed'] and not v['overflow'] and not v['fallbackFaces']
            assert all(v['meshVisibility']) and not any(v['wireframeFlags'])
            path = (folder / v['file']).resolve(); assert path.is_relative_to(folder)
            retained_images.append(dict(uid=v['uid'], width=width, time=v['time'], path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    for rows, uids in [(images, set(cfg['sources'])), (retained_images, retained)]:
        assert len(rows) == len({r['path'] for r in rows}) == 4 * len(uids)
        assert {(r['uid'], r['width'], r['time']) for r in rows} == {(u, w, t) for u in uids for w in [390, 1280] for t in ['15:00', '22:00']}
    producer = Path(__file__).resolve()
    save(installed / 'ROOT-LIVE-EXPORT-INSPECTION.json', dict(reviewer='ROOT', visualAcceptance=True,
         producer=dict(path=str(producer.relative_to(ROOT)), sha256=digest(producer.read_bytes())),
         imagesActuallyViewed=images, retainedImagesActuallyViewed=retained_images, inspectionSheetsActuallyViewed=[],
         inspectionMethod='Every individual source and retained-native live exported canvas opened by ROOT.', observations=a.observation))
    print(dict(sourceExportsActuallyViewed=len(images), retainedExportsActuallyViewed=len(retained_images)))


if __name__ == '__main__': main()
