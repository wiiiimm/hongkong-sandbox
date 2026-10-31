"""Bind ROOT's twelve actually opened exports to the exact reviewed originals."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dragon_three_original_identity_physical_review_v1_20261026 import PREFIX, SOURCES


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = PREFIX + 'three-qualified-source-review-v1-20261026'; out = base / batch
    assert not out.exists(); refs = [Path(__file__)]; pins = {}
    def take(suffix, name):
        folder = base / (PREFIX + suffix + '-20261026')
        if folder.name not in pins:
            pins[folder.name] = authenticate(folder)[1]; refs.append(folder / 'result.json')
        path = folder / name
        assert digest(path.read_bytes()) == pins[folder.name][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    physical = take('three-identity-physical-review-v1', 'ROOT-PHYSICAL-REVIEW.json')
    assert physical['sourceSHA256ByUid'] == SOURCES
    assert all(physical[k] for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted'])
    selection = take('three-original-ground-v1', 'selection.json.gz')
    assert {r['uid']: r['sourceSHA256'] for r in selection['rows']} == SOURCES
    scope = take('three-scope-v1', 'summary.json'); forms = set()
    for r in scope['rows']:
        forms.update(f['building']['uid'] for f in take('three-scope-v1', r['uid'].split('/')[1] + '-forms.json.gz'))
    assert physical['leaseResources'] == sorted('building:' + u for u in forms)
    native = take('three-empty-native-v1', 'summary.json')
    assert native['emptyNativeContactSetProved'] and native['rows'] == []
    images = []; reports = []
    for width in [1280, 390]:
        filename = str(width) + '/staged-browser.json'
        report = take('three-private-browser-v1', filename)
        assert report['passed'] and not report['errors'] and report['retainedNativeOwnViews'] == []
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 6
        for v in views:
            assert v['sourceSHA256'] == SOURCES[v['uid']] and v['pick'] == v['collision'] == v['uid']
            assert all(v[k] for k in ['active','visible','fullyFramed','solidAppearance']) and not v['fallbackFaces']
            path = base / (PREFIX + 'three-private-browser-v1-20261026') / str(width) / v['file']
            assert digest(path.read_bytes()) == pins[PREFIX + 'three-private-browser-v1-20261026'][str(path.relative_to(ROOT))]
            refs.append(path); images.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()), uid=v['uid'], width=width, time=v['time']))
        assert report['jointViews'] and all({m['uid']:m['sourceSHA256'] for m in j['models']} == SOURCES and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in j['models']) for j in report['jointViews'])
        if width == 390:
            assert {v['uid'] for v in report['views'] if v.get('phase') == 'failed-download' and v['fallbackRetained']} == set(SOURCES)
        path = base / (PREFIX + 'three-private-browser-v1-20261026') / filename
        reports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    assert {(i['uid'],i['width'],i['time']) for i in images} == {(u,w,t) for u in SOURCES for w in [390,1280] for t in ['15:00','22:00']}
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert physical['currentManifest']['sha256'] == digest(manifest.read_bytes()) == selection['manifestSHA256']; refs.append(manifest)
    review = dict(physical, visualAcceptance=True, imagesActuallyViewed=images, browserReports=reports,
        completeFourWorldFoundations=True, completeCurrentNeighbourChecks=len(forms),
        identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True,
            basis='Each exact current component route is qualified in the authenticated three-source identity receipt; explicit source identity is accepted in the bounded ROOT review, with all raw footprint/cell failures preserved.'),
        retainedNativeUids=[], retainedNativeEntries={}, retainedImagesActuallyViewed=[],
        browserVisualObservations=['ROOT opened all twelve original individual desktop/mobile day/night canvas exports.',
            'Tower roof and semicircular balcony facade are readable. Podium is low among taller neighbours; lower interfaces are interpreted from the separately inspected complete source/BASIC and assembly diagrams, not falsely claimed visible through foreground buildings.',
            'Small corner cuboid roof/side is partly concealed by adjoining native deck in its close view; the full coloured source assembly shows the unchanged cuboid/deck join. No added procedural windows; all originals are dark at night.',
            'Mobile podium own views contain tower/corner BASIC fallbacks during recovery. Final joint reports confirm all three originals active. No separate joint image is claimed.'],
        visualReviewScope='Faithful original source rendering with the disclosed foreground/deck occlusion; no photographic-completeness or engineering collision certification.',
        installationApproved=False, publication=False)
    save(out / 'ROOT-SOURCE-REVIEW.json', review); save(out / 'ROOT-PHYSICAL-REVIEW.json', review)
    module('dragon_browser_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'exact-three-original-source-and-actually-inspected-browser-exports-review', refs, review)
    print(dict(imagesOpened=len(images), neighbourForms=len(forms), qualifiedForPublicationChecks=True, installed=0), flush=True)


if __name__ == '__main__':
    main()
