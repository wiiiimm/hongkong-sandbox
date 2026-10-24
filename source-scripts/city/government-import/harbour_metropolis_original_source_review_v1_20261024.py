"""Exact hotel/installed podium source-role and inspected-preview review.
No source edits, production writes, old-parent reacceptance or installation credit.
"""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-harbour-metropolis-original-source-review-v1-20261024'
BROWSER = 'government-xl-harbour-metropolis-supported-unapproved-preview-v1-20261024'
UID, PARENT = 'landsd/259378:0', 'landsd/240841:0'
SHA = '1f7f3f42844aa20b23bf30f398b7f67035953c98b1b530d5529c8be4dd4c8034'
PARENT_SHA = 'e17d2d53e8d2c8b186f3bbbedf32bd6a8f7121e2d8b598f4b1fe36a65b791bf3'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def ref(path): return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))
    def take(batch, name='summary.json'):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name
        assert ref(path)['sha256'] == pins[batch][ref(path)['path']]
        refs.append(path)
        return read(path)
    identity = take('government-xl-harbour-metropolis-bounded-extent-identity-v1-20261024', 'identity.json')
    assert identity['identityAccepted'] and identity['sourceSHA256'] == SHA
    scope_batch = 'government-xl-next-three-after-ventilation-model-scope-v1-20261024'
    scope = take(scope_batch)
    scoped = next(r for r in scope['rows'] if r['uid'] == UID)
    assert scoped['currentNativeActorsChecked'] == 6895 and scoped['sourceSHA256'] == SHA
    forms = take(scope_batch, '259378:0-forms.json.gz')
    assert {r['building']['uid'] for r in forms} == {UID, PARENT, 'landsd/259576:0'}
    native = take('government-xl-next-three-current-native-contacts-v1-20261024')
    assert len(native['rows']) == 1
    n = native['rows'][0]
    assert (n['uid'], n['nativeUid'], n['sourceSHA256'], n['nativeSHA256']) == (UID, PARENT, SHA, PARENT_SHA)
    assert n['rawCurrentNativeEntry'] == identity['requiredInstalledPodiumEntry']
    assert {r['mode'] for r in n['modes']} == {'original', 'literal', 'leftF32', 'balancedF32'}
    assert all(r['areaContactPairs'] == 15 for r in n['modes'])
    foreign = take('government-xl-harbour-metropolis-current-foreign-v1-20261024')
    assert foreign['foreignPairs'] == 1 and foreign['rows'][0]['foreignUid'] == 'landsd/259576:0'
    assert all(r['positiveContactPairs'] == 0 and r['projectedOverlapAreaM2'] == 0 for r in foreign['rows'][0]['modes'])
    support = take('government-xl-harbour-metropolis-installed-support-v2-20261024')
    assert support['supportedUid'] == UID and support['installedSupportUid'] == PARENT
    for r in support['rows']:
        f = r['compoundFoundation']
        assert r['unresolved'] == r['finitePaths'] == 3 and not r['support']['passed']
        assert f['triangles'] == f['completeTerrainTriangles'] == 14504
        assert f['fullyBuriedTriangles'] == 2 and f['fullyBuriedUpwardTriangles'] == 0
    burial = take('government-xl-harbour-metropolis-installed-buried-context-v1-20261024')
    for r in burial['rows']:
        assert [f['faceIndex'] for f in r['buriedFaces']] == [11119, 11120]
        for face in r['buriedFaces']:
            normal = np.asarray(face['normal'])
            assert abs(normal[1]) / np.linalg.norm(normal) < .001 and not face['upward']
    interface_batch = 'government-xl-harbour-metropolis-original-interface-context-v1-20261024'
    interface = take(interface_batch)
    assert len(interface['rows']) == 4
    assert all(r['buriedFaces'] == [11119, 11120] and r['finitePaths'] == 2 and r['componentFaces'] == [12189] for r in interface['rows'])
    plot = BASE / interface_batch / 'complete-original-joint-perspectives.png'
    assert ref(plot)['sha256'] == pins[interface_batch][ref(plot)['path']]
    refs.append(plot)
    preview, pins[BROWSER] = authenticate(BASE / BROWSER)
    refs.append(BASE / BROWSER / 'result.json')
    assert preview['previewOnly'] and not preview['installationApproved']
    reports, images, sheets = [], [], []
    for width, name in [(1280, 'desktop'), (390, 'mobile')]:
        report_path = BASE / BROWSER / str(width) / 'staged-browser.json'
        report = take(BROWSER, str(width) + '/staged-browser.json')
        assert report['passed'] and not report['errors']
        reports.append(ref(report_path))
        for v in report['views']:
            if 'time' in v:
                assert v['uid'] == UID and v['sourceSHA256'] == SHA and v['fullyFramed'] and v['solidAppearance']
                assert not v['fallbackFaces'] and v['pick'] == v['collision'] == UID
        old = report['retainedNativeOwnViews']
        assert len(old) == 2 and all(v['uid'] == PARENT and v['sourceSHA256'] == PARENT_SHA and v['originalTriangles'] == 101394 and v['fullyFramed'] and v['active'] and v['visible'] and not v['fallbackFaces'] for v in old)
        sheet_dir = BASE / ('government-xl-harbour-metropolis-supported-preview-' + name + '-sheets-v1-20261024')
        binding = sheet_dir / (str(width) + '-panel-bindings.json')
        panels = read(binding)
        assert panels['report'] == ref(report_path)
        refs.append(binding)
        for row in panels['rows']:
            sheet = ROOT / row['sheet']
            assert ref(sheet)['sha256'] == row['sha256']
            refs.append(sheet)
            sheets.append(ref(sheet))
            for image in row['panels']:
                path = ROOT / image['path']
                assert ref(path)['sha256'] == image['sha256'] == pins[BROWSER][image['path']]
                refs.append(path)
                images.append(dict(path=image['path'], sha256=image['sha256'], uid=image['uid'], width=width, time=image['time']))
    assert len(images) == len({(i['uid'], i['width'], i['time']) for i in images}) == 8
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert ref(manifest)['sha256'] == scope['currentManifestSHA256'] == support['currentManifestSHA256']
    refs.append(manifest)
    observations = [
        'ROOT inspected all eight source/retained desktop/mobile day/night exports and the complete unchanged original joint diagram. The hotel rises from the existing extended podium; the full tower silhouette and podium remain visible. No new procedural window skin is used. Retained original appearance is unchanged; mobile failed-download fallback and retry passed.',
        'The unique original root, stable source identity and exact whole GeoRef cell bind this hotel. Its 1086.8996m2 footprint excess lies entirely on the exact retained podium, with zero unrelated overlap; the two generic extent negatives remain archived.',
        'The two fully covered surfaces11119/11120 are near-vertical lower facade triangles in the main12189face hotel component, extending into the original podium at the authored construction interface. They are not upward public floors or invented horizontal base closures. Their actual normal, vertices, sample gaps, full component and continuous paths to exact podium contacts are bound in four worlds. Accept this precise original lower-facade/podium interface; no general buried-wall exemption or engineering bearing-depth assertion.',
        'All three strict unresolved rim witnesses reach the unchanged original podium through continuous exact source-surface paths in every coordinate representation. Preserve strict FALSE and all raw negative gaps. The private trial declares that exact installed native dependency; no support dependency, geometry, terrain or pose is removed or changed on the retained parent.',
        'All6895 installed actors were screened for four-world bounds; only the retained podium overlaps. All15 area-contact pairs per world remain explicitly recorded. The sole other current form259576 has zero finite positive contacts and zero projected overlap in allfour worlds. Full three-form lease and guarded source-specific installation still required.'
    ]
    result = dict(uids=[UID], sourceSHA256ByUid={UID: SHA}, requiredOriginalAssembly={UID: SHA},
                  reviewer='ROOT', identityAccepted=True, originalSourceReviewAccepted=True,
                  sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
                  visualAcceptance=True, rawClearancePassed=False, rawStrictSupportPassed=False,
                  completeFourWorldFoundations=True, qualifiedFourWorldSourceClearance=True,
                  completeFourWorldSourceClearance=True, completeCurrentNeighbourChecks=3,
                  identityProof={k: True for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted']},
                  currentManifest=ref(manifest), leaseResources=sorted('building:' + f['building']['uid'] for f in forms),
                  supportByUid={UID: PARENT}, nativeSupportByUid={UID: PARENT},
                  requiredInstalledSupportEntry=n['rawCurrentNativeEntry'], retainedBasicSupportDependencies=[],
                  retainedCurrentBasicSupportUids=[], terrainEdits=False, sourceGeometryChanges=0, sourcePoseChanges=0,
                  sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                  browserReports=reports, imagesActuallyViewed=[i for i in images if i['uid'] == UID],
                  retainedImagesActuallyViewed=[i for i in images if i['uid'] == PARENT],
                  inspectionPreviewsActuallyViewed=sheets, actualGroundContextPlot=ref(plot),
                  observations=observations, publication=False, installationApproved=False)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'raw-support-and-clearance-negatives.json', support)
    module('harbour_source_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-original-hotel-installed-podium-source-physical-inspected-preview-review', list(dict.fromkeys(refs)), dict(uids=[UID], sourceSHA256ByUid={UID: SHA}, originalSourceReviewAccepted=True, sourceSpecificPhysicalInterpretationAccepted=True, identityAccepted=True, visualAcceptance=True, installationApproved=False, sourceGeometryChanges=0))


if __name__ == '__main__': main()
