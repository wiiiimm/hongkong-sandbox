"""Bind the exact QE physical review to all ROOT-inspected private source/retained exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-after-tung-on-qe311317-'
UID='landsd/311317:0'


def main():
    base=ROOT/'docs/astra-city/government-import';batch=P+'source-review-v1-20261026';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    physical=take(P+'physical-review-v1-20261026','ROOT-PHYSICAL-REVIEW.json');assert all(physical[k]for k in ['sourceSpecificPhysicalInterpretationAccepted','identityAccepted','completeFourWorldFoundations','completeNeighbourInterpretationAccepted'])
    observation=take(P+'private-observation-v1-20261026','ROOT-PRIVATE-EXPORT-OBSERVATION.json');assert observation['reviewer']=='ROOT'and observation['completePrivateExportObservation']
    observed={r['path']:r['sha256']for r in observation['sourceExportsActuallySeenWithinSheets']};assert len(observed)==20
    browser=P+'private-browser-v1-20261026';retained=set(physical['retainedNativeRegression']['requiredNativeUids']);images=[];native_images=[];reports=[];seen=set()
    def image(folder,v):
        path=folder/v['file'];key=str(path.relative_to(ROOT));sha=digest(path.read_bytes());assert sha==pins[browser][key]==observed[key];refs.append(path);seen.add(key);return dict(path=key,sha256=sha)
    for width in [1280,390]:
        folder=base/browser/str(width);path=folder/'staged-browser.json';report=take(browser,path);assert report['passed']and not report['errors'];reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
        source=[v for v in report['views']if v.get('file')];assert len(source)==2 and {v['time']for v in source}=={'15:00','22:00'}
        for v in source:
            assert v['uid']==UID and v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']and v['pick']==v['collision']==UID and v['sourceSHA256']==physical['sourceSHA256ByUid'][UID]
            images.append(image(folder,v))
        if width==390:assert any(v.get('phase')=='failed-download'and v['fallbackRetained']for v in report['views'])
        natives=report['retainedNativeOwnViews'];assert len(natives)==2*len(retained)and {(v['uid'],v['time'])for v in natives}=={(u,t)for u in retained for t in ['15:00','22:00']}
        for v in natives:
            assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and all(v['meshVisibility'])and not any(v['wireframeFlags'])
            native_images.append(dict(**image(folder,v),uid=v['uid'],viewportWidth=width,time=v['time']))
    assert seen==set(observed)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert physical['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));refs.append(manifest)
    result={**physical,'visualAcceptance':True,'originalSourceReviewAccepted':True,'wallContextImagesActuallyViewed':physical['imagesActuallyViewed'],'imagesActuallyViewed':images,'browserReports':reports,'retainedNativeUids':sorted(retained),'retainedNativeVisualReviewImages':native_images,'rootPrivateObservation':dict(path=str((base/(P+'private-observation-v1-20261026')/'ROOT-PRIVATE-EXPORT-OBSERVATION.json').relative_to(ROOT)),sha256=digest((base/(P+'private-observation-v1-20261026')/'ROOT-PRIVATE-EXPORT-OBSERVATION.json').read_bytes())),'imageInspectionMethod':'ROOT opened all six authenticated unscaled uncropped contact sheets containing all four source and16 retained actual exports, desktop/mobile day/night. Every claimed source/retained PNG exactly matches the inspected sheet metadata.','visualObservations':'Complete original QE silhouette, side core, roof framing and facade bands visible in both viewport sizes. Original unlit night materials/proceduralWindowsFalse preserved; no skin added. All four retained models visible in their own day/night views. Lower-envelope/junction physical interpretation is explicitly bounded by the separate exact source review, not inferred from browser success alone.','sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'installationApproved':False,'publication':False}
    save(out/'ROOT-SOURCE-REVIEW.json',result);module('qe_original_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-qe311317-original-source-and-retained-visual-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
