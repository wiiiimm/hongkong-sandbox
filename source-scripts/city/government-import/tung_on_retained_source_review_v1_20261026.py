"""Bind the inspected primary source and complementary overhead retained exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-after-tuen-mun-tung-on-'
UID='landsd/53852:0'
OVERHEAD={'landsd/126434:0','landsd/254604:0'}

def main():
    base=ROOT/'docs/astra-city/government-import';batch=P+'source-review-v1-20261026';out=base/batch
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    physical=P+'physical-review-v1-20261026';review=take(physical,base/physical/'ROOT-PHYSICAL-REVIEW.json')
    assert review['sourceSpecificPhysicalInterpretationAccepted']and review['identityAccepted']and review['completeFourWorldFoundations']
    primary=P+'private-diagnostic-v1-20261026';overhead=P+'private-overhead-retained-v1-20261026'
    retained=set(review['retainedNativeRegression']['requiredNativeUids']);reports=[];images=[];native_images=[]
    def img(n,folder,v):
        path=folder/v['file'];sha=digest(path.read_bytes());assert sha==pins[n][str(path.relative_to(ROOT))];refs.append(path)
        return dict(path=str(path.relative_to(ROOT)),sha256=sha)
    for width in [1280,390]:
        folder=base/primary/str(width);path=folder/'staged-browser.json';report=take(primary,path)
        assert report['passed']and not report['errors'];reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
        views=[v for v in report['views']if v.get('file')];assert len(views)==2 and {v['time']for v in views}=={'15:00','22:00'}
        for v in views:
            assert v['uid']==UID and v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']
            assert v['pick']==v['collision']==UID and v['sourceSHA256']==review['sourceSHA256ByUid'][UID]
            images.append(img(primary,folder,v))
        if width==390:assert any(v.get('phase')=='failed-download'and v['fallbackRetained']for v in report['views'])
        altfolder=base/overhead/str(width);alt=take(overhead,altfolder/'staged-browser.json');assert alt['passed']and not alt['errors']
        config=take(overhead,HERE/'local'/overhead/('browser-config-'+str(width)+'.json'))
        assert all(config['retainedCaptureDirectionByModel'][u]==[0,8,1]for u in OVERHEAD)
        selected=[(primary,folder,v)for v in report['retainedNativeOwnViews']if v['uid']not in OVERHEAD]+[(overhead,altfolder,v)for v in alt['retainedNativeOwnViews']if v['uid']in OVERHEAD]
        assert len(selected)==2*len(retained)and {(v['uid'],v['time'])for _,_,v in selected}=={(u,t)for u in retained for t in ['15:00','22:00']}
        for n,f,v in selected:
            assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and all(v['meshVisibility'])and not any(v['wireframeFlags'])
            native_images.append(dict(**img(n,f,v),uid=v['uid'],viewportWidth=width,time=v['time']))
    sheets=[]
    for width in [1280,390]:
        n=P+'overhead-contact-sheets-v1-20261026';summary=take(n,base/n/'summary.json');s=next(r for r in summary['sheets']if r['path'].endswith(str(width)+'-retained-3.png'))
        path=ROOT/s['path'];assert digest(path.read_bytes())==s['sha256']==pins[n][s['path']];refs.append(path);sheets.append(s)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert review['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));refs.append(manifest)
    result={**review,'visualAcceptance':True,'originalSourceReviewAccepted':True,'wallContextImagesActuallyViewed':review['imagesActuallyViewed'],'imagesActuallyViewed':images,'browserReports':reports,'retainedNativeUids':sorted(retained),'retainedNativeVisualReviewImages':native_images,'supplementalInspectionSheets':sheets,'supplementalRetainedBrowser':overhead,'imageInspectionMethod':'Primary source desktop two individual PNGs, mobile two via1x sheet; six retained actors via primary1x sheets. Retained126434/254604 day/night desktop/mobile via overhead sheet3 for eachwidth. Unused reverse/overhead images are not claimed reviewed.','visualObservations':'ROOT inspected original Tung On facade, roof and podium on desktop/mobile in day/night. Original dark night materials/proceduralWindowsFalse retained. Complementary overhead views expose the roofs and surroundings of126434/254604 without foreground-tower occlusion; other six retained originals are visible in primary views. Complete ground/source-role evidence is separately bound. No new geometry or terrain modification from this review.','sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'installationApproved':False,'publication':False}
    save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('tung_on_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'original-tung-on-four-source-and-complementary-retained-export-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
