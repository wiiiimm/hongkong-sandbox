"""Bind exact completed browser exports actually inspected to a reviewed original assembly."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'physical', 'browser', 'runtime', 'inspection']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs, cache = [Path(__file__)], {}
    def take(name, path):
        if name not in cache:
            cache[name] = authenticate(base / name)[1]
            refs.append(base / name / 'result.json')
        assert digest(path.read_bytes()) == cache[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    physical = take(args.physical, base / args.physical / 'ROOT-PHYSICAL-REVIEW.json')
    assert physical['sourceSpecificPhysicalInterpretationAccepted']
    sources = physical['sourceSHA256ByUid']
    selected = take(args.runtime, base / args.runtime / 'selection.json.gz')
    assert {r['uid']: r['sourceSHA256'] for r in selected['rows']} == sources
    reports, expected = [], set()
    for width in [1280, 390]:
        path = base / args.browser / str(width) / 'staged-browser.json'
        report = take(args.browser, path)
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 2*len(sources)
        assert {(v['uid'], v['time']) for v in views} == {(uid, time) for uid in sources for time in ['15:00', '22:00']}
        for view in views:
            assert view['active'] and view['visible'] and view['fullyFramed'] and view['solidAppearance'] and not view['fallbackFaces']
            assert view['pick'] == view['collision'] == view['uid'] and view['sourceSHA256'] == sources[view['uid']]
        assert report['jointViews'] and all({m['uid']: m['sourceSHA256'] for m in j['models']} == sources and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in j['models']) for j in report['jointViews'])
        if width == 390:
            assert {v['uid'] for v in report['views'] if v.get('phase') == 'failed-download' and v['fallbackRetained']} == set(sources)
        expected.update(str((path.parent / v['file']).relative_to(ROOT)) for v in views)
        reports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    inspected = ROOT / args.inspection
    viewed = read(inspected)
    assert viewed['reviewer'] == 'ROOT' and viewed['visualAcceptance'] is True
    images = viewed['imagesActuallyViewed']
    assert len(images) == len({q['path'] for q in images}) == 4*len(sources)
    assert {q['path'] for q in images} == expected
    refs.append(inspected)
    for item in images:
        assert digest((ROOT / item['path']).read_bytes()) == item['sha256'] == cache[args.browser][item['path']]
        refs.append(ROOT / item['path'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    refs.append(manifest)
    result = dict(uids=sorted(sources), sourceSHA256ByUid=sources, currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())), identityAccepted=True, sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True, visualAcceptance=True, imagesActuallyViewed=images, browserReports=reports, requiredOriginalAssembly=sorted(sources), sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True, installationApproved=False, qualification='Exact unchanged source assembly and scoped physical review, with completed current desktop/mobile day/night, picking/collision, joint activation and individual failure/retry. ROOT inspected every recorded source export. Guarded publication and live verification remain required.')
    save(doc / 'ROOT-SOURCE-REVIEW.json', result)
    save(doc / 'ROOT-INSPECTED-EXPORTS.json', viewed)
    module('selected_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'exact-selected-original-qualified-source-review', refs, result)


if __name__ == '__main__':
    main()
