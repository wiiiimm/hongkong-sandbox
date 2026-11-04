"""Bind completed physical, source-view and six-case lifecycle evidence.

Reuses already inspected exact exports and measured software checks. Does not
claim physical-phone FPS, full facet visibility, publication or installation.
"""
import sys
import uuid
from pathlib import Path
from PIL import Image
from run import ROOT, HERE, read, save, digest, reservations
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from silvercord_lippo_five_original_physical_review_v1_20261103 import Evidence, BASE, OWNER

PREFIX = 'government-xl-silvercord-lippo-'
BATCH = PREFIX+'five-original-source-review-v1-20261103'
LOCAL = HERE/'local'/BATCH
PHYSICAL = PREFIX+'five-original-physical-review-v1-20261103'
BROWSER = PREFIX+'private-six-part-browser-v4-20261103'
ATOMIC = PREFIX+'original-atomic-lifecycle-v2-20261103'


def assemble(e):
    physical = e.take(PHYSICAL,'ROOT-PHYSICAL-REVIEW.json')
    assert physical['sourceSpecificPhysicalInterpretationAccepted'] and physical['completeNeighbourInterpretationAccepted']
    sources = physical['sourceSHA256ByUid']
    manifest = e.file(ROOT/'3d-viewer/city/data/manifest.json',physical['currentManifest']['sha256'])
    current = {m['uid']:m for url in manifest['officialModelCatalogues']
               for m in e.file(ROOT/'3d-viewer'/url)['models']}
    assert len(current) == 7101
    summary = e.take(BROWSER)
    assert set(summary['uids']) == set(sources) and summary['publicInputsUnchanged']
    observed = set(summary['retainedNativeUids'])
    assert observed == {OWNER,'landsd/21915:0','landsd/156599:0','landsd/234188:0'}
    assert observed <= set(physical['retainedNativeUids'])
    reports, source_exports, retained_exports = [], {}, {}
    for width in [1280,390]:
        path = BASE/BROWSER/str(width)/'staged-browser.json'
        report = e.take(BROWSER,str(width)+'/staged-browser.json')
        assert report['passed'] and not report['errors']
        assert len(report['views']) == 10
        assert {(v['uid'],v['time']) for v in report['views']} == {(u,t) for u in sources for t in ['15:00','22:00']}
        for v in report['views']:
            assert v['width'] == width and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces']
            assert v['pick'] == v['collision'] == v['uid'] and v['sourceSHA256'] == sources[v['uid']]
            p = path.parent/v['file']; source_exports[str(p.relative_to(ROOT))] = (width,900)
        views = report['retainedNativeOwnViews']
        assert len(views) == 8 and {(v['uid'],v['time']) for v in views} == {(u,t) for u in observed for t in ['15:00','22:00']}
        for v in views:
            assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
            assert v['sourceSHA256'] == current[v['uid']]['sha256'] and v['originalTriangles'] == current[v['uid']]['triangles']
            assert all(v['meshVisibility']) and not any(v['wireframeFlags'])
            p = path.parent/v['file']; retained_exports[str(p.relative_to(ROOT))] = (width,900)
        assert len(report['jointViews']) == 5
        for joint in report['jointViews']:
            assert {m['uid']:m['sourceSHA256'] for m in joint['models']} == sources
            assert all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in joint['models'])
        reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    lifecycle = e.take(ATOMIC)
    assert lifecycle['atomicSoftwareCasesPassed'] == 6 and lifecycle['eachMobileSourceDeniedAndRetried']
    assert lifecycle['baseOnlyAndEvictionPassed'] and lifecycle['retainedOwnerFallbackAndRecoveryPassed']
    atomic = e.take(ATOMIC,'atomic/report.json')
    assert atomic['passed'] and not atomic['pageErrors'] and len(atomic['cases']) == 6
    assert atomic['actualProductionGeometryHTTPVerified'] and not atomic['moduleSubstitution']
    assert {(c['width'],c['failedUid']) for c in atomic['cases']} == {(1280,None)} | {(390,u) for u in sources}
    for case in atomic['cases']:
        assert case['baseOnlyRestoredCompleteGroup'] and case['completeGroupEvicted']
        if case['failedUid'] is not None:
            assert case['failureKeptAllBasics']
    inspections = []
    all_images = []
    inspection_specs = [
        ('government-xl-silvercord-private-success-export-sheets-v1-20261103','ROOT-EXPORT-INSPECTION.json',
         'renderedExportInspectionPassed',36,BROWSER),
        (PREFIX+'atomic-export-inspection-v1-20261103','ROOT-ATOMIC-EXPORT-INSPECTION.json',
         'atomicLifecycleExportInspectionPassed',17,ATOMIC)]
    for name, filename, flag, count, browser in inspection_specs:
        path = BASE/name/filename
        inspection = e.file(path)
        assert inspection[flag] and inspection['aiGeometryModelling'] is False
        originals = inspection['originalsReviewedViaSheets']
        assert len(originals) == len({r['path'] for r in originals}) == count
        assert {r['path'] for s in inspection['sheetsActuallyViewed'] for r in s['originals']} == {r['path'] for r in originals}
        for sheet in inspection['sheetsActuallyViewed']:
            e.pin(ROOT/sheet['path'],sheet['sha256'])
        for image in originals:
            p = ROOT/image['path']
            assert image['sha256'] == e.pins[browser][image['path']]
            e.pin(p,image['sha256'])
            expected = image.get('originalDimensions',image.get('dimensions'))
            with Image.open(p) as im:
                assert list(im.size) == expected
            all_images.append(image)
        inspections.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),
                                observations=inspection['observations']))
    assert len(all_images) == len({r['path'] for r in all_images}) == 53
    assert {r['path'] for r in all_images[:36]} == set(source_exports)|set(retained_exports)
    # Every direct browser input stays current; includes exact source assets,
    # tested catalogue/configurations, installed catalogues and production JS.
    for batch in [BROWSER,ATOMIC]:
        for path,sha in e.pins[batch].items():
            e.pin(ROOT/path,sha)
    return dict(**{k:v for k,v in physical.items() if k not in ['visualAcceptance','installationApproved','publication','basis']},
        status='approved-for-integration',visualAcceptance=True,installationApproved=False,publication=False,
        physicalReview=dict(path=str((BASE/PHYSICAL/'ROOT-PHYSICAL-REVIEW.json').relative_to(ROOT)),
                            sha256=digest((BASE/PHYSICAL/'ROOT-PHYSICAL-REVIEW.json').read_bytes())),
        browserReports=reports,browserObservedRetainedUids=sorted(observed),
        unchangedNativeTerrainEvidenceCount=1227,fullNativeTerrainScope=1228,
        imagesActuallyViewed=[r for r in all_images if r['path'] in source_exports],
        retainedImagesActuallyViewed=[r for r in all_images if r['path'] in retained_exports],
        atomicImagesActuallyViewed=all_images[36:],exportInspections=inspections,
        atomicLifecycleReport=dict(path=str((BASE/ATOMIC/'atomic/report.json').relative_to(ROOT)),
                                  sha256=digest((BASE/ATOMIC/'atomic/report.json').read_bytes())),
        physicalPhonePerformanceAccepted=False,fullFacetVisibilityClaimed=False,
        basis=physical['basis']+[
            'ROOT previously inspected all36original success exports and17atomic exports through ten hash-bound sheets. These exact records/images are reused after rechecking their complete byte/dimension/coverage bindings. Dense foreground occlusion and atomic UI-card occlusion remain recorded; source-complete loading, framing, picking/collision, peer denial/retry, Base-only/eviction and retained-owner fallback/recovery are independently measured. No physical-phone FPS or complete facet-visibility claim.',
            'The four directly observed retained actors include the only changed actual-ground native owner. The other1227terrain contexts retain exact complete before/after rendered face multisets under all required whole-source bounds; they are not dropped, newly reapproved or fabricated as fresh mesh measurements. All5408form obligations and eleven global BASIC support contracts remain part of the physical review.',
            'Approved only for a private qualified stage and guarded installation of the exact tested sources/catalogue/two terrain descriptors/support-only owner proposal. No automatic public writes or installed credit follows; live verification, exact byte fences, distinct transaction snapshot and independent full521readback remain required.'
        ])


def owned():
    lease = read(LOCAL/'reservation.json')
    assert reservations.owns(lease) and not (BASE/BATCH).exists()
    e = Evidence(); e.refs = [Path(__file__),HERE/'silvercord_lippo_five_original_physical_review_v1_20261103.py']
    review = assemble(e); e.finish(); assert reservations.owns(lease)
    save(BASE/BATCH/'ROOT-SOURCE-REVIEW.json',review)
    result = dict(uids=review['uids'],sourceSHA256ByUid=review['sourceSHA256ByUid'],
        identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,
        visualAcceptance=True,actualInspectedExports=53,atomicCases=6,installationApproved=False,publication=False,
        sourceGeometryChanges=0,sourcePoseChanges=0)
    save(BASE/BATCH/'summary.json',result)
    module('silvercord_five_original_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'qualified-exact-five-original-physical-visual-and-owner-lifecycle-review',list(dict.fromkeys(e.refs)),result)


if __name__ == '__main__':
    if '--preflight' in sys.argv:
        e = Evidence(); review = assemble(e); e.finish()
        print(dict(sourceReviewPreflightPassed=True,models=len(review['uids']),exports=53,publication=False),flush=True)
    elif '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE/BATCH).exists()
        claim = reservations.claim('silvercord-five-original-source-review-'+str(uuid.uuid4()),
            ['building:landsd/'+u+':0' for u in ['233997','231645','237843','238659','239032','239465']]
            + ['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
