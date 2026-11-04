"""Bind actual ROOT image observations to exact original physical/browser evidence.

Fails closed until all supplemental camera images have actually been inspected.
Does not publish, create geometry, or reapprove existing installed source records.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ocean_coordinated_full_browser_v2_20261027 import verify_atomic
from ocean_retained_camera_supplement_v1_20261027 import UIDS as SUPPLEMENT_UIDS

BASE=ROOT/'docs/astra-city/government-import'
CONFIGPATH=BASE/'government-xl-ocean-coordinated-original-install-config-v1-20261027.json'
CONFIG=read(CONFIGPATH);BATCH=CONFIG['review'];DOC=BASE/BATCH
FULL=BASE/CONFIG['browser'];SUPPLEMENT=BASE/'government-xl-ocean-retained-camera-supplement-v1-20261027'
OBS=BASE/'government-xl-scripted-continuation-20261023'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def checked_observations(rows,expected,pins):
    """Require every exact expected image once; reviewed booleans aren't approval."""
    assert len(rows)==len(expected) and len({r['path'] for r in rows})==len(rows)
    assert {r['path'] for r in rows}==set(expected)
    for row in rows:
        assert row['actuallyViewedByRoot'] is True
        assert row['sha256']==pins[row['path']]==digest((ROOT/row['path']).read_bytes())
    return [dict(path=r['path'],sha256=r['sha256']) for r in rows]

def main():
    assert not DOC.exists();refs=[Path(__file__),CONFIGPATH];pins={};receipts={}
    for name in [CONFIG['physical'],CONFIG['browser'],SUPPLEMENT.name]:
        receipt,items=authenticate(BASE/name);receipts[name]=receipt;refs.append(BASE/name/'result.json')
        for path,sha in items.items():
            assert path not in pins or pins[path]==sha
            assert digest((ROOT/path).read_bytes())==sha,path
            pins[path]=sha
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    physical=take(BASE/CONFIG['physical']/'ROOT-PHYSICAL-REVIEW.json')
    assert physical['sourceSHA256ByUid']==CONFIG['sources']
    assert all(physical[k] for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','companionRootsApproved'])
    assert not physical['visualAcceptance'] and not physical['installationApproved']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==physical['currentManifest'];refs.append(manifest)
    full=receipts[CONFIG['browser']];supplement=receipts[SUPPLEMENT.name]
    assert full['allBrowserDiagnosticsPassed'] and full['atomicFailureCases']==5
    assert supplement['allBrowserDiagnosticsPassed'] and supplement['mandatoryAtomicCasesBoundToFullRun']==5
    assert supplement['fullBrowserReceipt']==CONFIG['browser'] and supplement['supplementRetainedUids']==SUPPLEMENT_UIDS
    stage=HERE/'local'/CONFIG['browser'];catalogue=take(stage/'catalogue.json')
    assert verify_atomic(take(FULL/'atomic-lifecycle/report.json'),catalogue['models'])
    expected_source=[];expected_retained=[];expected_supplement=[];reports=[];supplement_reports=[]
    for width in [1280,390]:
        path=FULL/str(width)/'staged-browser.json';report=take(path);reports.append(ref(path))
        assert report['passed'] and not report['errors']
        views=[v for v in report['views'] if 'time' in v]
        assert len(views)==2*len(CONFIG['sources'])
        assert {(v['uid'],v['time']) for v in views}=={(u,t) for u in CONFIG['sources'] for t in ['15:00','22:00']}
        for v in views:
            assert v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance']
            assert v['fallbackFaces']==0 and v['pick']==v['collision']==v['uid']
            assert v['sourceSHA256']==CONFIG['sources'][v['uid']]
            expected_source.append(str((path.parent/v['file']).relative_to(ROOT)))
        retained=report['retainedNativeOwnViews'];assert len(retained)==54
        assert {(v['uid'],v['time']) for v in retained}=={(u,t) for u in CONFIG['retainedNativeUids'] for t in ['15:00','22:00']}
        for v in retained:
            assert v['active'] and v['visible'] and v['fullyFramed'] and v['fallbackFaces']==0
            assert v['sourceSHA256']==physical['retainedNativeEntries'][v['uid']]['sha256']
            expected_retained.append(str((path.parent/v['file']).relative_to(ROOT)))
        path=SUPPLEMENT/str(width)/'staged-browser.json';report=take(path);supplement_reports.append(ref(path))
        assert report['passed'] and not report['errors'];retained=report['retainedNativeOwnViews']
        assert len(retained)==12 and {(v['uid'],v['time']) for v in retained}=={(u,t) for u in SUPPLEMENT_UIDS for t in ['15:00','22:00']}
        for v in retained:
            assert v['active'] and v['visible'] and v['fullyFramed'] and v['fallbackFaces']==0
            assert v['sourceSHA256']==physical['retainedNativeEntries'][v['uid']]['sha256']
            expected_supplement.append(str((path.parent/v['file']).relative_to(ROOT)))
    source_rows=[]
    for kind in ['desktop','mobile']:
        path=OBS/('ocean-coordinated-v2-'+kind+'-source-observations-20261027.json')
        refs.append(path);record=read(path);assert record['batch']==CONFIG['browser'];source_rows+=record['imagesActuallyViewed']
    source_images=checked_observations(source_rows,expected_source,pins)
    path=OBS/'ocean-coordinated-v2-all-retained-observations-20261027.json';refs.append(path);record=read(path)
    assert record['retainedImageCount']==108 and record['cameraSupplementUids']==SUPPLEMENT_UIDS
    retained_images=checked_observations([im for row in record['rows'] for im in row['imagesActuallyViewed']],expected_retained,pins)
    path=OBS/'ocean-camera-supplement-root-observations-20261027.json';refs.append(path);record=read(path)
    assert record['batch']==SUPPLEMENT.name and record['allSupplementViewsUsableForBoundedAppearanceReview'] is True
    assert sorted(record['uids'])==SUPPLEMENT_UIDS and not record['existingSourceReapproved']
    supplemental_images=checked_observations(record['imagesActuallyViewed'],expected_supplement,pins)
    result={**physical,'visualAcceptance':True,'qualifiedForLiveVerification':True,'installationApproved':False,'publication':False,'currentManifest':ref(manifest),'browserReports':reports,'supplementalBrowserReports':supplement_reports,'imagesActuallyViewed':source_images,'retainedImagesActuallyViewed':retained_images,'supplementalImagesActuallyViewed':supplemental_images,'obstructedOriginalImagesPreserved':True,'existingInstalledSourcesReapproved':False,'performanceAcceptance':False,'basis':[*physical['basis'],'Exact full-run source and retained images inspected by ROOT. Six obstructed retained cameras supplemented without changing source assets, placement, terrain or installed metadata. Source-specific appearance acceptance is distinct from existing-source approval and from live publication.']}
    save(DOC/'ROOT-SOURCE-REVIEW.json',result)
    refs.extend(ROOT/path for path in pins)
    module('ocean_coordinated_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-coordinated-source-physical-and-actual-image-review-v1',list(dict.fromkeys(refs)),dict(uids=sorted(CONFIG['sources']),sourceSHA256ByUid=CONFIG['sources'],identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,qualifiedForLiveVerification=True,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,existingCatalogueChanges=0))

if __name__=='__main__':main()
