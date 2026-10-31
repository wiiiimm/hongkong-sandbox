"""Record ROOT's completed review of twelve exact live installation exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
INSTALL='government-xl-unnamed265269-canopy-original-installed-v4-20261029'
BATCH='government-xl-unnamed265269-live-image-review-v1-20261029'
UID='landsd/265269:0'


def main():
    out=BASE/BATCH;assert not out.exists()
    receipt,pins=authenticate(BASE/INSTALL)
    assert receipt['installedUids']==[UID]and receipt['newlyInstalled']==1
    source=[];retained=[];refs=[Path(__file__),BASE/INSTALL/'result.json']
    for width in [390,1280]:
        folder=BASE/INSTALL/('viewport-'+str(width));reportpath=folder/'live-browser.json'
        assert digest(reportpath.read_bytes())==pins[str(reportpath.relative_to(ROOT))];refs.append(reportpath)
        report=read(reportpath);assert report['passed']and not report['errors']
        views=[v for v in report['views']if 'time'in v];assert len(views)==2 and not report['retainedNativeOwnViews']
        for rows,images in [(views,source),(report['retainedNativeOwnViews'],retained)]:
            for view in rows:
                p=folder/view['file'];sha=digest(p.read_bytes());assert sha==pins[str(p.relative_to(ROOT))]
                assert view['active']and view['visible']and view['fullyFramed']and not view['fallbackFaces']
                images.append(dict(path=str(p.relative_to(ROOT)),sha256=sha,uid=view['uid'],width=width,time=view['time']));refs.append(p)
    assert len(source)==4 and not retained
    result=dict(uids=[UID],reviewer='ROOT',installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],
                imagesActuallyViewed=source,retainedImagesActuallyViewed=retained,visualAcceptance=True,
                sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,
                qualification='ROOT inspected all4 actual live390/1280day/night exports. The complete unnamed original roof/body and canopy are framed at native pose; the duplicate estimated BASIC canopy is hidden only while the original is active. Existing surrounding BASICs remain present. No architectural name, screenshot-only structural or performance claim is invented.')
    save(out/'ROOT-LIVE-IMAGE-OBSERVATIONS.json',result)
    module('unnamed_live_images_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-exact-live-unnamed-source-desktop-mobile-image-review',refs,result)


if __name__=='__main__':main()
