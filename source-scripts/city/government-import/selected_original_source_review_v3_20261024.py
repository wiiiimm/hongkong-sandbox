"""Bind inspected source and retained exports, including a failed-parent recovery."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'physical', 'browser', 'runtime', 'inspection', 'previous-attributes', 'attributes']:
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
    retained_expected, dependency_expected = set(), set()
    manifestpath = ROOT/'3d-viewer/city/data/manifest.json'
    retained_uids=set(physical['retainedNativeUids'])
    retained_models={}
    for url in read(manifestpath)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        for model in read(path)['models']:
            if model['uid'] in retained_uids:
                assert model['uid'] not in retained_models
                retained_models[model['uid']]=model;refs.append(path)
    assert set(retained_models)==retained_uids
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
        retained=report['retainedNativeOwnViews']
        assert len(retained)==2*len(retained_uids)
        assert {(v['uid'],v['time'])for v in retained}=={(uid,time)for uid in retained_uids for time in ['15:00','22:00']}
        for v in retained:
            assert v['active']and v['visible']and v['fullyFramed']and not v['overflow']and not v['fallbackFaces']
            assert v['sourceSHA256']==retained_models[v['uid']]['sha256']and v['originalTriangles']==retained_models[v['uid']]['triangles']
            assert all(v['meshVisibility'])and not any(v['wireframeFlags'])
        retained_expected.update(str((path.parent/v['file']).relative_to(ROOT))for v in retained)
        if width==390:
            update=physical['installedSupportUpdate'];failed=report['retainedDependencyFallbackViews']
            assert len(failed)==1
            v=failed[0];assert v['uid']==update['ownerUid']and v['sourceSHA256']==update['ownerSHA256']
            assert v['basicLoaded']and not v['basicHidden']and not v['active']and v['fallbackFaces']>0 and not v['loadingTravel']and not v['travelling']
            assert v['failedParents']==[d['uid']for d in update['afterEntry']['supportDependencies']]
            assert v['supportDependencies']==update['afterEntry']['supportDependencies']
            dependency_expected.add(str((path.parent/v['file']).relative_to(ROOT)))
        expected.update(str((path.parent / v['file']).relative_to(ROOT)) for v in views)
        reports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    inspected = ROOT / args.inspection
    viewed = read(inspected)
    assert viewed['reviewer'] == 'ROOT' and viewed['visualAcceptance'] is True
    images = viewed['imagesActuallyViewed']
    assert len(images) == len({q['path'] for q in images}) == 4*len(sources)
    assert {q['path'] for q in images} == expected
    refs.append(inspected)
    for preview in viewed.get('inspectionPreviewRefs',[]):
        path=ROOT/preview['path'];assert digest(path.read_bytes())==preview['sha256'];refs.append(path)
    for item in images:
        assert digest((ROOT / item['path']).read_bytes()) == item['sha256'] == cache[args.browser][item['path']]
        refs.append(ROOT / item['path'])
    extra_groups={}
    for key,expected_paths in [('retainedImagesActuallyViewed',retained_expected),('dependencyFailureImagesActuallyViewed',dependency_expected)]:
        group=viewed[key]
        assert len(group)==len({v['path']for v in group})==len(expected_paths)and {v['path']for v in group}==expected_paths
        for item in group:
            path=ROOT/item['path'];assert digest(path.read_bytes())==item['sha256']==cache[args.browser][item['path']];refs.append(path)
        extra_groups[key]=group
    # Reuse of older actual-ground proofs must preserve every full indexed
    # coordinate stream, not only the literal stream that was recaptured.
    oldattrs=take(args.previous_attributes,base/args.previous_attributes/'attributes.json.gz')
    freshattrs=take(args.attributes,base/args.attributes/'attributes.json.gz')
    import numpy as np
    oldby={r['uid']:r for r in oldattrs['rows']};newby={r['uid']:r for r in freshattrs['rows']}
    for uid in sources:
        assert oldby[uid]['sourceSHA256']==newby[uid]['sourceSHA256']==sources[uid]
        for field in ['completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
            assert np.array_equal(np.asarray(oldby[uid][field]),np.asarray(newby[uid][field]))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    refs.append(manifest)
    result = dict(uids=sorted(sources), sourceSHA256ByUid=sources, currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())), identityAccepted=True, sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True, visualAcceptance=True, imagesActuallyViewed=images, browserReports=reports, requiredOriginalAssembly=sorted(sources), sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True, installationApproved=False, qualification='Exact unchanged source assembly and scoped physical review, with completed current desktop/mobile day/night, picking/collision, joint activation and individual failure/retry. ROOT inspected every recorded source export. Guarded publication and live verification remain required.')
    result.update(status='approved-for-integration',retainedNativeUids=sorted(retained_uids),installedSupportUpdate=physical['installedSupportUpdate'],allThreeCompleteCoordinateStreamsReusedExactly=True,**extra_groups)
    save(doc / 'ROOT-SOURCE-REVIEW.json', result)
    save(doc / 'ROOT-INSPECTED-EXPORTS.json', viewed)
    module('selected_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'exact-selected-original-qualified-source-review', refs, result)


if __name__ == '__main__':
    main()
