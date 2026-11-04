"""Bind ROOT's eight inspected exports and the two exact physical reviews."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import'
    batch='government-xl-two-basic-supported-source-review-v1-20261023'
    out=base/batch
    assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:
            pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    physical='government-xl-two-basic-supported-physical-review-v1-20261023'
    review=take(physical,base/physical/'ROOT-PHYSICAL-REVIEW.json')
    browser='government-xl-two-basic-supported-private-browser-v1-20261023'
    reports=[];images=[]
    for width in [1280,390]:
        folder=base/browser/str(width)
        report=take(browser,folder/'staged-browser.json')
        assert report['passed'] and not report['errors']
        reports.append(dict(path=str((folder/'staged-browser.json').relative_to(ROOT)),sha256=digest((folder/'staged-browser.json').read_bytes())))
        views=[v for v in report['views']if 'time'in v]
        assert len(views)==4
        for v in views:
            assert v['uid']in review['sourceSHA256ByUid']
            assert v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces'] and v['active'] and v['visible']
            assert v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==review['sourceSHA256ByUid'][v['uid']]
            path=folder/v['file'];take_image=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
            assert pins[browser][take_image['path']]==take_image['sha256'];refs.append(path);images.append(take_image)
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert review['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()))
    result={**review,'visualAcceptance':True,'originalSourceReviewAccepted':True,'imagesActuallyViewed':images,'browserReports':reports,
            'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'installationApproved':False,'publication':False,
            'visualObservations':'ROOT inspected all eight exported desktop/mobile day/night canvases. Both original towers retain roof equipment, balconies and complete silhouettes; the existing basic podium remains visible below each tower. Bohemian has partial foreground/neighbour occlusion on the right; geometry and placement are unchanged. Nighttime original facades remain dark with procedural windows disabled; surrounding basic buildings retain their existing bright/noisy window shader. No architectural reconstruction or geometry edits.'}
    save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('two_basic_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'two-original-retained-basic-source-and-export-review',refs+[manifest],result)


if __name__=='__main__':main()
