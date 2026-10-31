"""Bind ROOT's eight directly inspected final exports to the exact physical review."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-after-qe-waterfront203730-'

def main():
    base=ROOT/'docs/astra-city/government-import';batch=P+'source-review-v1-20261027';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        path=base/n/file;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    physical=take(P+'physical-review-v1-20261027','ROOT-PHYSICAL-REVIEW.json')
    assert all(physical[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','completeFourWorldFoundations','rawCanonicalFailuresPreserved'])
    assert physical['supportByUid']=={'landsd/203730:0':'landsd/273061:0'}and not physical['terrainEdits']
    browser=P+'private-browser-v3-20261027';sources=physical['sourceSHA256ByUid'];retained=physical['retainedNativeEntries'];expected={r['path']:r for r in physical['imagesActuallyViewed']+physical['retainedImagesActuallyViewed']};assert len(expected)==8
    seen=set();reports=[]
    for width in [1280,390]:
        path=base/browser/str(width)/'staged-browser.json';report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
        if width==390:assert {r['uid']for r in report['views']if r.get('phase')=='failed-download'and r['fallbackRetained']}==set(sources)
        for kind,rows,allowed in [('source',report['views'],sources),('retained',report['retainedNativeOwnViews'],{u:e['sha256']for u,e in retained.items()})]:
            rows=[r for r in rows if r.get('file')];assert {(r['uid'],r['time'])for r in rows}=={(u,t)for u in allowed for t in ['15:00','22:00']}and len(rows)==2*len(allowed)
            for r in rows:
                assert r['active']and r['visible']and r['fullyFramed']and not r['fallbackFaces']and r['sourceSHA256']==allowed[r['uid']]
                if kind=='source':assert r['solidAppearance']and r['pick']==r['collision']==r['uid']
                else:assert r['originalTriangles']==retained[r['uid']]['triangles']and all(r['meshVisibility'])and not any(r['wireframeFlags'])
                image=path.parent/r['file'];key=str(image.relative_to(ROOT));assert key not in seen and key in expected;seen.add(key)
                item=dict(path=key,sha256=digest(image.read_bytes()),uid=r['uid'],width=width,time=r['time']);assert item==expected[key]and item['sha256']==pins[browser][key];refs.append(image)
    assert seen==set(expected)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert physical['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));refs.append(manifest)
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        for entry in read(path)['models']:
            if entry['uid']in retained:assert entry==retained[entry['uid']];refs.append(path)
    result={**physical,'visualAcceptance':True,'originalSourceReviewAccepted':True,'retainedNativeUids':sorted(retained),'browserReports':reports,'imageInspectionMethod':'ROOT opened all eight original V3 PNG exports directly: source and retained Elements, desktop1280/mobile390, day/night. Exact current hash and per-view IDs/time/width are bound to the authenticated completed browser receipt.','visualObservations':'East-facing source views expose the complete roof/body/lower apron. Original plain provider surfaces and unlit dark night appearance are preserved, with no procedural facade skin. Existing Elements original remains present in its complete own views. Lower source/apron junction is separately bounded by exact source/physical review; browser success alone does not approve it.','installationApproved':False,'publication':False}
    save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('waterfront_original_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-waterfront-original-source-and-retained-export-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
