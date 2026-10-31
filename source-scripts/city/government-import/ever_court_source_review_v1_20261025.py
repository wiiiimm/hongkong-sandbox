"""Bind actual inspected Ever Court and retained-boundary exports; never publish."""
from copy import deepcopy
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ever_court_boundary_scope_v1_20261025 import UID, NATIVE, retained_views

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-ever-court-original-source-review-v1-20261025'
BROWSER = 'government-xl-ever-court-current-private-browser-v3-20261025'
INSPECTION = BASE / 'government-xl-ever-court-private-export-inspection-v3-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [HERE / 'ever_court_source_review_v1_20261025.py'], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    physical = take('government-xl-ever-court-current-physical-review-v2-20261025', 'ROOT-PHYSICAL-REVIEW.json')
    assert physical['sourceSpecificPhysicalInterpretationAccepted'] and physical['identityAccepted']
    assert physical['retainedNativeUids'] == [NATIVE] and physical['supportByUid'] == {}
    sources = physical['sourceSHA256ByUid']
    assert set(sources) == {UID}
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())) == physical['currentManifest']
    refs.append(manifest)
    current = {}
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(path)
        for model in read(path)['models']:
            assert model['uid'] not in current
            current[model['uid']] = model
    assert len(current) == 6911 and UID not in current
    panels = read(INSPECTION / 'panel-bindings.json')
    inspected = read(INSPECTION / 'ROOT-EXPORT-INSPECTION.json')
    refs.extend([INSPECTION / 'panel-bindings.json', INSPECTION / 'ROOT-EXPORT-INSPECTION.json'])
    assert inspected['reviewer'] == 'ROOT' and inspected['visualAcceptance']
    images = [i for row in panels['rows'] for i in row['panels']]
    assert len(images) == 8 and set(i['uid'] for i in images) == {UID, NATIVE}
    assert inspected['imagesActuallyViewed'] == images
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
        assert r['passed'] and not r['errors']
        views = [v for v in r['views'] if 'time' in v]
        assert len(views) == 2 and {(v['uid'], v['width'], v['time']) for v in views} == {(UID, width, t) for t in ['15:00', '22:00']}
        for v in views:
            assert v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces']
            assert v['active'] and v['visible'] and v['pick'] == v['collision'] == UID and v['sourceSHA256'] == sources[UID]
            assert not v.get('suppressed', {})
        assert retained_views(r['retainedNativeOwnViews'], current, width)
        for v in views + r['retainedNativeOwnViews']:
            expected = str((path.parent / v['file']).relative_to(ROOT))
            image = next(i for i in images if i['path'] == expected)
            assert (image['uid'], image['width'], image['time']) == (v['uid'], width, v['time'])
            assert pins[BROWSER][expected] == image['sha256']
        assert any({m['uid'] for m in j['models']} == {UID} and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in j['models']) for j in r['jointViews'])
        if width == 390:
            assert {v['uid'] for v in r['views'] if v.get('phase') == 'failed-download' and v['fallbackRetained']} == {UID}
        reports.append(reference)
    catalogue = HERE / 'local' / BROWSER / 'catalogue.json'
    assert digest(catalogue.read_bytes()) == pins[BROWSER][str(catalogue.relative_to(ROOT))]
    models = read(catalogue)['models']
    assert len(models) == 1 and models[0]['uid'] == UID and models[0]['sha256'] == sources[UID]
    assert models[0]['proceduralWindows'] is False and not models[0].get('supportDependencies') and not models[0].get('suppressesBuildingUids')
    refs.append(catalogue)
    result = deepcopy(physical)
    result.update(reviewer='ROOT', visualAcceptance=True, imagesActuallyViewed=[i for i in images if i['uid'] == UID], retainedImagesActuallyViewed=[i for i in images if i['uid'] == NATIVE], browserReports=reports, installationApproved=False, publication=False, stagedInspection=inspected)
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    refs.append(HERE / 'ever_court_boundary_scope_v1_20261025.py')
    module('ever_court_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-original-ever-court-source-and-inspected-private-browser-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
