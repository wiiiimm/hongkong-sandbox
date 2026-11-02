"""Bind ROOT's actual direct inspection of independent original live exports.

No automatic visual judgement: the observation is supplied only after viewing.
"""
import argparse,os
from pathlib import Path
from run import ROOT,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--observation',required=True);a=p.parse_args()
    base=ROOT/'docs/astra-city/government-import';cfgpath=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert cfgpath.is_relative_to(base);cfg=read(cfgpath);sources=cfg['sources'];assert 1<=len(sources)<=40 and cfg['supportByUid']=={}
    folder=base/(cfg['prefix']+'-original-installed-v1-'+cfg['date']);receipt,pins=authenticate(folder)
    assert receipt['publication']and receipt['sourceSHA256ByUid']==sources and receipt['newlyInstalled']==cfg['expectedFixedXLDelta']
    observation=(ROOT/a.observation).resolve();assert observation.is_relative_to(base);seen=read(observation)
    assert seen['reviewer']=='Codex ROOT'and seen['allDeclaredExportsActuallyInspected']and seen['limitations']
    images=[]
    for width in [390,1280]:
        reportpath=folder/('viewport-'+str(width))/'live-browser.json';assert digest(reportpath.read_bytes())==pins[str(reportpath.relative_to(ROOT))]
        report=read(reportpath);assert report['passed']and not report['errors']and not report['retainedNativeOwnViews']
        views=[v for v in report['views']if 'time'in v];assert len(views)==2*len(sources)
        for v in views:
            uid=v['uid'];assert uid in sources and v['sourceSHA256']==sources[uid]and v['pick']==v['collision']==uid and v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and not v['overflow']
            assert all(v['meshVisibility'])and not any(v['wireframeFlags'])
            path=reportpath.parent/v['file'];image=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uid=uid,width=width,time=v['time']);assert pins[image['path']]==image['sha256'];images.append(image)
        assert report['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==sources and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in report['jointViews'])
    assert len(images)==len({r['path']for r in images})==len(seen['imagesActuallyViewed'])==4*len(sources)
    assert {(r['uid'],r['width'],r['time'])for r in images}=={(u,w,t)for u in sources for w in [390,1280]for t in ['15:00','22:00']}
    assert {(r['path'],r['sha256'])for r in images}=={(r['path'],r['sha256'])for r in seen['imagesActuallyViewed']}
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    target=folder/'ROOT-LIVE-EXPORT-INSPECTION.json';assert not target.exists()
    save(target,dict(reviewer='ROOT',visualAcceptance=True,producer=ref(Path(__file__)),imagesActuallyViewed=images,retainedImagesActuallyViewed=[],inspectionSheetsActuallyViewed=[],inspectionMethod='Every declared live PNG source canvas opened directly',observations=seen['limitations'],boundObservation=ref(observation),aiGeometryModelling=False))
    print(dict(sourceImages=len(images),installedJobId=receipt['jobId']))
if __name__=='__main__':main()
