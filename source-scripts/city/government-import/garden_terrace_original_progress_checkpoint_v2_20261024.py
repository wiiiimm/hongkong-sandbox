"""Bind ROOT's inspected V2 exports without transferring physical/publication approval."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-next-repairs-garden-terrace2-'
PRIOR = PREFIX + 'three-original-progress-checkpoint-v1-20261024'
BROWSER = PREFIX + 'three-unapproved-preview-v2-20261024'
BATCH = PREFIX + 'three-original-progress-checkpoint-v2-20261024'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs = [Path(__file__)]
    receipts = {}
    pins = {}

    def take(batch, path):
        if batch not in receipts:
            receipts[batch], pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    prior = take(PRIOR, BASE / PRIOR / 'remaining-work.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == prior['currentManifestSHA256']
    refs.append(manifest)
    sources = prior['sourceSHA256ByUid']
    assert len(sources) == 3 and prior['sourceFaces'] == 22814
    images, sheets, reports = [], [], []

    def ref(path):
        return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

    for width in [1280, 390]:
        path = BASE / BROWSER / str(width) / 'staged-browser.json'
        report = take(BROWSER, path)
        assert report['passed'] and not report['errors']
        reports.append(ref(path))
        source_views = [v for v in report['views'] if 'time' in v]
        retained = report['retainedNativeOwnViews']
        assert len(source_views) == 6 and len(retained) == 2
        assert {(v['uid'], v['time']) for v in source_views} == {
            (uid, time) for uid in sources for time in ['15:00', '22:00']
        }
        for view in source_views + retained:
            assert view['fullyFramed']
            assert view['active'] and view['visible'] and not view['fallbackFaces']
            assert all(view['meshVisibility']) and not any(view['wireframeFlags'])
            if view['uid'] in sources:
                assert view['solidAppearance']
                assert view['pick'] == view['collision'] == view['uid']
                assert view['sourceSHA256'] == sources[view['uid']]
            else:
                assert view['uid'] == 'landsd/304714:0'
                assert view['originalTriangles'] == 821
                assert view['sourceSHA256'] == 'f06178309a08955ef93e0d5424e864075632670d3bb2902d3c7d9aaee933beca'
                assert view['wanted'] and not view['overflow']
            image = path.parent / view['file']
            assert digest(image.read_bytes()) == pins[BROWSER][str(image.relative_to(ROOT))]
            refs.append(image)
            images.append(dict(**ref(image), uid=view['uid'], width=width, time=view['time']))
        for time in ['1500', '2200']:
            sheet = BASE / (PREFIX + 'three-root-inspection-v2-20261024') / str(width) / (str(width) + '-' + time + '.jpg')
            assert sheet.is_file()
            refs.append(sheet)
            sheets.append(ref(sheet))
    assert len(images) == 16
    inspection = dict(
        reviewer='ROOT', visualInspectionComplete=True,
        imagesActuallyViewed=images, inspectionSheetsActuallyViewed=sheets,
        browserReports=reports, visualAcceptance=True,
        visualFinding='ROOT inspected all16 complete source/retained exports through four V2 sheets. Block2 is now visibly inspectable from the revised high southern view. The original podium, two towers and retained No1 podium have coherent visible surfaces. Natural partial foreground/own-tower occlusion remains; originals remain dark at night while legacy neighbours are illuminated. This is bounded visual inspection, not a claim that every surface is visible or that these models have physical/publication acceptance.',
        supersedesVisualRejectionOnly=PRIOR, physicalAcceptance=False,
        installationApproved=False, publication=False,
        sourceGeometryChanges=0, sourcePoseChanges=0, terrainGeometryChanges=0,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False)
    save(out / 'ROOT-V2-EXPORT-INSPECTION.json', inspection)
    remaining = {**prior, 'visualAcceptance': True, 'physicalAcceptance': False,
                 'installationApproved': False, 'newlyInstalled': 0,
                 'completedJobs': {**prior['completedJobs'], BROWSER: receipts[BROWSER]['jobId'], PRIOR: receipts[PRIOR]['jobId']},
                 'visualInspection': ref(out / 'ROOT-V2-EXPORT-INSPECTION.json'),
                 'remaining': prior['remaining'][1:],
                 'qualification': 'V2 actual-export visual inspection only. Complete prior mathematical evidence and raw negatives remain unchanged. No new Garden Terrace installation, physical acceptance or permanent rejection. Full347installed/174unfinished XL scope remains active.'}
    save(out / 'remaining-work.json', remaining)
    module('garden_v2_visual_checkpoint_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'original-garden-terrace-inspected-v2-preview-and-remaining-integration-obligations',
        list(dict.fromkeys(refs)), remaining)


if __name__ == '__main__':
    main()
