"""Record a completed ROOT inspection of exact live source/retained exports.

Run only after viewing the exported canvases. Does not publish or install assets.
"""
import argparse,os
from pathlib import Path
from run import ROOT,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inspection-directory',required=True);ap.add_argument('--review-note',required=True);a=ap.parse_args();assert len(a.review_note)>60
    base=ROOT/'docs/astra-city/government-import';cfgpath=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert cfgpath.is_relative_to(base);cfg=read(cfgpath)
    folder=base/(cfg['prefix']+'-original-installed-'+cfg.get('installVersion','v1')+'-'+cfg['date']);result,pins=authenticate(folder)
    sources=cfg['sources'];retained=set(cfg['retainedNativeUids']);assert result['sourceSHA256ByUid']==sources
    count=cfg['previousInstalled']+cfg['expectedFixedXLDelta'];assert result['fullXLCurrentCounts']==dict(total=521,installedVerified=count,remaining=521-count)
    target=folder/'ROOT-LIVE-EXPORT-INSPECTION.json';assert not target.exists();current={}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==result['manifest']['sha256']
    for url in read(manifest)['officialModelCatalogues']:
        for m in read(ROOT/'3d-viewer'/url)['models']:assert m['uid']not in current;current[m['uid']]=m
    assert len(current)==cfg['currentNativeActors']+len(sources)
    images=[];oldimages=[];sheets=[]
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    for width in [390,1280]:
        path=folder/('viewport-'+str(width))/'live-browser.json';report=read(path);assert report['passed']and not report['errors']
        source=[v for v in report['views']if'time'in v];old=report.get('retainedNativeOwnViews',[])
        assert len(source)==2*len(sources)and len(old)==2*len(retained)and{v['uid']for v in old}==retained
        for values,output in [(source,images),(old,oldimages)]:
            for v in values:
                assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and all(v['meshVisibility'])and not any(v['wireframeFlags'])and not v['overflow']
                if v['uid']in sources:assert v['sourceSHA256']==sources[v['uid']]and v['solidAppearance']and v['pick']==v['collision']==v['uid']
                else:assert v['uid']in retained and v['sourceSHA256']==current[v['uid']]['sha256']and v['originalTriangles']==current[v['uid']]['triangles']
                image=path.parent/v['file'];r=ref(image);assert r['sha256']==pins[r['path']];output.append(dict(**r,uid=v['uid'],width=width,time=v['time']))
        for t in ['1500','2200']:
            sheet=(ROOT/a.inspection_directory/str(width)/(str(width)+'-'+t+'.jpg')).resolve();assert sheet.is_relative_to(base)and sheet.is_file();sheets.append(ref(sheet))
    assert {(i['uid'],i['width'],i['time'])for i in images}=={(u,w,t)for u in sources for w in [390,1280]for t in ['15:00','22:00']}
    assert {(i['uid'],i['width'],i['time'])for i in oldimages}=={(u,w,t)for u in retained for w in [390,1280]for t in ['15:00','22:00']}
    save(target,dict(reviewer='ROOT',visualAcceptance=True,producer=ref(Path(__file__)),imagesActuallyViewed=images,retainedImagesActuallyViewed=oldimages,inspectionSheetsActuallyViewed=sheets,visualFinding=a.review_note,sourceGeometryChanges=0,terrainEdits=False,aiGeometryModelling=False))
    print(dict(sourceImages=len(images),retainedImages=len(oldimages),installedJobId=result['jobId']))

if __name__=='__main__':main()
