"""Bind actual inspected source/retained exports and atomic lifecycle evidence.

Qualifies this exact private scene only; no geometry changes or publication.
"""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from west_kowloon_pair_physical_review_v1_20261027 import SOURCES, P

BATCH = P + 'visual-qualification-v1-20261027'


def main():
    base, out = ROOT / 'docs/astra-city/government-import', ROOT / 'docs/astra-city/government-import' / BATCH
    assert not out.exists()
    refs, pins, receipts = [Path(__file__)], {}, {}

    def take(batch, filename='summary.json', authenticated=True):
        if authenticated:
            if batch not in pins:
                receipts[batch], pins[batch] = authenticate(base / batch)
                refs.append(base / batch / 'result.json')
            if filename is None:
                return receipts[batch]
        path = base / batch / filename
        if authenticated:
            assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    physical = take(P + 'physical-source-review-v1-20261027')
    assert physical['physicalAcceptance'] and physical['sourceSHA256ByUid'] == SOURCES
    auxiliary = take(P + '309340-0-foundation-v2-20261027')
    assert auxiliary['establishedFoundationPolicyPassed'] and len(auxiliary['rows']) == 4
    assert all(r['triangles'] == r['completeTerrainTriangles'] == 338
               and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in auxiliary['rows'])
    runtime = P + 'three-member-runtime-v2-20261027'
    current = take(runtime, 'selection.json.gz')
    assert {r['uid']: r['sourceSHA256'] for r in current['rows']} == SOURCES
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == current['manifestSHA256']
    refs.append(manifest)
    # Explicitly prove the older auxiliary input arrays are identical too;
    # current passing foundation is independently bound to the final capture.
    geometries = []
    for name in [P + 'three-member-runtime-v1-20261027', runtime]:
        take(name, 'selection.json.gz')
        path = HERE / 'local' / name / 'runtime-geometry.json.gz'
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        geometries.append(next(r for r in read(path)['rows'] if r['uid'] == 'landsd/309340:0'))
    assert all(geometries[0][k] == geometries[1][k] for k in ['sourceSHA256','position','index','drawnGroundGeometry'])
    desktop_receipt = P + 'desktop-complete-mobile-held-v1-20261027'
    desktop = take(desktop_receipt, None)
    assert desktop['desktopDiagnosticsPassed']
    base_report_path = base / (P + 'full-existing-peer-browser-v2-20261027') / '1280/staged-browser.json'
    assert digest(base_report_path.read_bytes()) == pins[desktop_receipt][str(base_report_path.relative_to(ROOT))]
    base_report = read(base_report_path)
    refs.append(base_report_path)
    assert base_report['passed'] and not base_report['errors']
    expected = {r['uid']: r['sourceSHA256'] for r in base_report['retainedNativeOwnViews']}
    assert len(expected) == 67
    mobile = take(P + 'remaining-mobile-v1-20261027', None)
    assert mobile['all67Covered'] and mobile['retainedOnly'] and mobile['newSourceAcceptance'] is False
    selected = take(P + 'selected-retained-mobile-v1-20261027', None)
    assert selected['normalDeviceBudgetsUnchanged'] and selected['normalDeselectionFallbackVerified']
    atomic_name = P + 'atomic-existing-peer-receipt-v1-20261027'
    take(atomic_name, None)
    atomic_path = base / (P + 'atomic-existing-peer-browser-v1-20261027') / 'atomic/report.json'
    assert digest(atomic_path.read_bytes()) == pins[atomic_name][str(atomic_path.relative_to(ROOT))]
    atomic = read(atomic_path)
    assert atomic['passed'] and not atomic['pageErrors'] and len(atomic['cases']) == 4
    refs.append(atomic_path)

    def inspected_row(row, width, require_pixels=False):
        image = row.get('image') or dict(path=row['path'], sha256=row['sha256'])
        path = ROOT / image['path']
        assert path.resolve().is_relative_to(base.resolve()) and digest(path.read_bytes()) == image['sha256']
        refs.append(path)
        uid, time = row['uid'], row['time']
        assert uid in expected and time in ['15:00','22:00']
        if row.get('sourceSHA256') is not None:
            assert row['sourceSHA256'] == expected[uid]
        if require_pixels:
            assert row['actualVisibleTargetPixels'] >= 32
        return dict(uid=uid, time=time, width=width, sourceSHA256=expected[uid], image=image)

    desktop_observation = take(P + 'desktop-retained-inspection-v2-20261027', 'ROOT-DESKTOP-OBSERVATIONS.json')
    assert desktop_observation['actuallyInspectedRetainedExports'] == 134
    corrected = set(desktop_observation['cameraSupplementUids'])
    assert len(corrected) == 7
    desktop_rows = [inspected_row(r,1280) for r in desktop_observation['rows'] if r['uid'] not in corrected]
    camera = take(P + 'camera-retained-inspection-v2-20261027', 'ROOT-DESKTOP-CAMERA-OBSERVATIONS.json')
    camera_rows = [r for r in camera['rows'] if r['kind'] == 'retained-original']
    assert {r['uid'] for r in camera_rows} == corrected and len(camera_rows) == 14
    desktop_rows.extend(inspected_row(r,1280,True) for r in camera_rows)
    mobile_rows = []
    for name in ['selected-mobile-inspection-v2', 'remaining-mobile-inspection-v1',
                 'mobile-groups04to07-inspected-v1', 'mobile-groups08to10-inspected-v1']:
        observation = take(P + name + '-20261027', 'ROOT-MOBILE-OBSERVATIONS.json')
        assert observation['reviewUsedAI'] and observation['aiGeometryModellingCalls'] == 0
        mobile_rows.extend(inspected_row(r,390,True) for r in observation['rows'])
    required = {(u,t) for u in expected for t in ['15:00','22:00']}
    for rows in [desktop_rows,mobile_rows]:
        assert len(rows) == len({(r['uid'],r['time']) for r in rows}) == 134
        assert {(r['uid'],r['time']) for r in rows} == required
    sources = take(P + 'new-source-capture-observations-v1-20261027', 'ROOT-NEW-SOURCE-CAPTURE-OBSERVATIONS.json')
    assert sources['newSourceCaptureChecksPassed'] and sources['actuallyInspectedExports'] == 8
    assert {(r['uid'],r['width'],r['time']) for r in sources['rows']} == {
        (u,w,t) for u in SOURCES for w in [1280,390] for t in ['15:00','22:00']}
    for row in sources['rows']:
        assert row['sourceSHA256'] == SOURCES[row['uid']] and row['actualVisibleTargetPixels'] >= 32
        assert row['originalTriangles'] == (10322 if row['uid'] == 'landsd/182397:0' else 338)
        path = ROOT / row['image']['path']
        assert digest(path.read_bytes()) == row['image']['sha256']
        refs.append(path)
    for record in sources['evidenceRefs']:
        path = ROOT / record['path']
        assert digest(path.read_bytes()) == record['sha256']
        refs.append(path)
    result = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, currentManifestSHA256=current['manifestSHA256'],
                  sourceSpecificVisualReviewAccepted=True, visualAcceptance=True, newSourceInspectedViews=8,
                  retainedNativeActors=67, desktopRetainedInspectedViews=134, mobileRetainedInspectedViews=134,
                  correctedDesktopCameraUids=sorted(corrected), inspectedDesktop=desktop_rows, inspectedMobile=mobile_rows,
                  sourceCaptureObservations=sources['rows'], priorAuxiliaryInputsExactlyUnchanged=True,
                  freshAuxiliaryFourWorldFoundationPassed=True, allFourAtomicCasesPassed=True,
                  normalDeviceBudgetsUnchanged=True, realSelectedLuiCaptureAndNormalBasicFallbackRequired=True,
                  sourceGeometryChanges=0, sourcePoseChanges=0, sourceAppearanceReapproved=False,
                  existingNativeReaccepted=False, installationApproved=False, publication=False,
                  qualification='Exact inspected source images plus every retained actor day/night in desktop/mobile. '
                  'Seven occluded desktop cameras use their inspected actual-pixel replacements; old failed images remain. '
                  'The real UI-selected Lui capture and default-budget BASIC fallback stay explicit. All4atomic '
                  'peer-failure/retry cases are independently bound. Visual/private-scene qualification only; '
                  'no new architecture/legacy support approval, runtime budget increase, optimisation or publication.')
    save(out / 'ROOT-VISUAL-QUALIFICATION.json', result)
    save(out / 'summary.json', {k:v for k,v in result.items() if k not in ['inspectedDesktop','inspectedMobile','sourceCaptureObservations']})
    module('north_visual_qualification_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-source-and67retained-private-scene-visual-qualification', list(dict.fromkeys(refs)),
        {k:v for k,v in result.items() if k not in ['inspectedDesktop','inspectedMobile','sourceCaptureObservations']})


if __name__ == '__main__': main()
