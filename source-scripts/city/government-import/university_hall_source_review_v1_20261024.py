"""Bind ROOT's four inspected University Hall exports and exact physical evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-university-hall-standalone-source-review-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    physical='government-xl-next-repairs-university-hall-93417-physical-review-v2-20261024';review=take(physical,base/physical/'ROOT-PHYSICAL-REVIEW.json');assert review['qualifiedFourWorldSourceClearance'] and review['retainedBasicSupportDependencies']==[]
    browser='government-xl-university-hall-standalone-private-browser-v2-20261024';reports=[];images=[]
    for width in [1280,390]:
        folder=base/browser/str(width);report=take(browser,folder/'staged-browser.json');assert report['passed'] and not report['errors'];reports.append(dict(path=str((folder/'staged-browser.json').relative_to(ROOT)),sha256=digest((folder/'staged-browser.json').read_bytes())))
        views=[v for v in report['views']if 'time'in v];assert len(views)==2 and {v['time']for v in views}=={'15:00','22:00'}
        for v in views:
            assert v['uid']=='landsd/93417:0' and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces'] and v['active'] and v['visible'] and not v['retained']
            assert v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==review['sourceSHA256ByUid'][v['uid']]
            path=folder/v['file'];sha=digest(path.read_bytes());assert pins[browser][str(path.relative_to(ROOT))]==sha;refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=sha))
        if width==390:
            failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['fallbackRetained']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert review['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()))
    result={**review,'visualAcceptance':True,'originalSourceReviewAccepted':True,'wallContextImagesActuallyViewed':review['imagesActuallyViewed'],'imagesActuallyViewed':images,'browserReports':reports,'standalonePathUserApproval':'Approve guarded standalone installation','standaloneApprovalScope':'Exact University Hall original only, zero source support dependencies, preserve existing global retained-support checks, desktop/mobile browser checks before installation.','sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'installationApproved':False,'publication':False,'visualObservations':'ROOT inspected all four actual exported desktop/mobile day/night canvases. The unchanged detailed hall retains its main roof, cylindrical corner towers, facade piers, ornate roofline and stairs. It is fully framed on both viewports. No opaque neighbouring building hides the source in these captures. Source facades remain dark at night with procedural windows disabled; existing neighbours retain their lit/noisy shader. Source-specific lower-wall/ground interpretation is separately bound to the two corrected wall close-ups and exact finite evidence; no whole-source appearance claim replaces it. No remodelling, terrain change or source displacement.'}
    save(out/'ROOT-SOURCE-REVIEW.json',result);module('university_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'standalone-original-source-and-four-inspected-desktop-mobile-exports',refs+[manifest],result)

if __name__=='__main__':main()
