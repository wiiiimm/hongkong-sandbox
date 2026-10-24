"""Bind ROOT's actual 8-export inspection to the two unchanged TVB originals."""
from copy import deepcopy
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope
from tvb_two_original_physical_review_v1_20261025 import SOURCES
SUPPORTS = {}

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-tvb-two-original-source-review-v1-20261025'
BROWSER = 'government-xl-tvb-two-original-private-browser-v1-20261025'
INSPECTION = BASE / 'government-xl-tvb-two-original-private-export-inspection-v1-20261025'
RETAINED = {'way/186639167:0'}


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [HERE / 'tvb_two_original_source_review_v1_20261025.py', HERE / 'tvb_two_original_physical_review_v1_20261025.py'], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    physical = take('government-xl-tvb-two-original-physical-review-v1-20261025', 'ROOT-PHYSICAL-REVIEW.json')
    assert physical['sourceSHA256ByUid'] == SOURCES and physical['supportByUid'] == SUPPORTS
    assert physical['sourceSpecificPhysicalInterpretationAccepted'] and physical['identityAccepted'] and physical['completeNeighbourInterpretationAccepted']
    assert physical['retainedNativeUids'] == []
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())) == physical['currentManifest']
    refs.append(manifest)
    current = []
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(path)
        current.extend(read(path)['models'])
    assert len(current) == len({m['uid'] for m in current}) == 6924
    assert not set(SOURCES) & {m['uid'] for m in current}
    panels = read(INSPECTION / 'panel-bindings.json')
    inspected = read(INSPECTION / 'ROOT-EXPORT-INSPECTION.json')
    refs.extend([INSPECTION / 'panel-bindings.json', INSPECTION / 'ROOT-EXPORT-INSPECTION.json'])
    assert inspected['reviewer'] == 'ROOT' and inspected['visualAcceptance']
    images = [i for row in panels['rows'] for i in row['panels']]
    assert len(images) == len({i['path'] for i in images}) == 8
    assert {(i['uid'], i['width'], i['time']) for i in images} == {(u, w, t) for u in SOURCES for w in [390, 1280] for t in ['15:00', '22:00']}
    image_order = lambda r: (r['uid'], r['width'], r['time'], r['path'])
    assert sorted(inspected['imagesActuallyViewed'], key=image_order) == sorted(images, key=image_order)
    for image in images:
        path = ROOT / image['path']
        assert digest(path.read_bytes()) == image['sha256']
        refs.append(path)
    reports = []
    for width in [1280, 390]:
        r = take(BROWSER, f'{width}/staged-browser.json')
        path = BASE / BROWSER / str(width) / 'staged-browser.json'
        reference = dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
        assert reference in panels['reports']
        assert r['passed'] and not r['errors'] and r['retainedNativeOwnViews'] == []
        views = [v for v in r['views'] if 'time' in v]
        assert len(views) == 4
        assert {(v['uid'], v['width'], v['time']) for v in views} == {(u, width, t) for u in SOURCES for t in ['15:00', '22:00']}
        for v in views:
            assert v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces']
            assert v['active'] and v['visible'] and v['pick'] == v['collision'] == v['uid']
            assert v['sourceSHA256'] == SOURCES[v['uid']] and not v.get('suppressed', {})
            assert set(v['retained']) == RETAINED
            assert all(state['loaded'] and not state['hidden'] and not state['detailedActive'] for state in v['retained'].values())
            expected = str((path.parent / v['file']).relative_to(ROOT))
            image = next(i for i in images if i['path'] == expected)
            assert (image['uid'], image['width'], image['time']) == (v['uid'], width, v['time'])
            assert pins[BROWSER][expected] == image['sha256']
        assert r['jointViews'] and all({m['uid']: m['sourceSHA256'] for m in j['models']} == SOURCES and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in j['models']) for j in r['jointViews'])
        if width == 390:
            failed = [v for v in r['views'] if v.get('phase') == 'failed-download']
            assert len(failed) == 2 and {v['uid'] for v in failed if v['fallbackRetained']} == set(SOURCES)
        reports.append(reference)
    catalogue = HERE / 'local' / BROWSER / 'catalogue.json'
    assert digest(catalogue.read_bytes()) == pins[BROWSER][str(catalogue.relative_to(ROOT))]
    models = read(catalogue)['models']
    assert verify_support_scope(models, SOURCES, SUPPORTS)
    assert all(m['proceduralWindows'] is False and not m.get('suppressesBuildingUids') for m in models)
    refs.append(catalogue)
    result = deepcopy(physical)
    result.update(reviewer='ROOT', visualAcceptance=True, sourceContextImagesActuallyViewed=physical['imagesActuallyViewed'], imagesActuallyViewed=images, browserReports=reports, stagedInspection=inspected, installationApproved=False, publication=False)
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    refs.append(HERE / 'original_supported_catalogue_scope_v1_20261024.py')
    module('kwong_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-two-source-tvb-inspected-private-browser-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
