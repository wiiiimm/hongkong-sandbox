"""Record ROOT's completed review of eight exact live installation exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
INSTALL='government-xl-peninsula-exact-original-pair-original-installed-v3-20261029'
BATCH='government-xl-peninsula-exact-pair-live-image-review-v1-20261029'
UID='landsd/270876:0'
UIDS=[UID,'landsd/266543:0']


def main():
    out=BASE/BATCH;assert not out.exists()
    receipt,pins=authenticate(BASE/INSTALL)
    assert set(receipt['installedUids'])==set(UIDS)and receipt['newlyInstalled']==1
    source=[];retained=[];refs=[Path(__file__),BASE/INSTALL/'result.json']
    for width in [390,1280]:
        folder=BASE/INSTALL/('viewport-'+str(width));reportpath=folder/'live-browser.json'
        assert digest(reportpath.read_bytes())==pins[str(reportpath.relative_to(ROOT))];refs.append(reportpath)
        report=read(reportpath);assert report['passed']and not report['errors']
        views=[v for v in report['views']if 'time'in v];assert len(views)==4 and not report['retainedNativeOwnViews']
        for rows,images in [(views,source),(report['retainedNativeOwnViews'],retained)]:
            for view in rows:
                p=folder/view['file'];sha=digest(p.read_bytes());assert sha==pins[str(p.relative_to(ROOT))]
                assert view['active']and view['visible']and view['fullyFramed']and not view['fallbackFaces']
                images.append(dict(path=str(p.relative_to(ROOT)),sha256=sha,uid=view['uid'],width=width,time=view['time']));refs.append(p)
    assert len(source)==8 and not retained
    result=dict(uids=UIDS,reviewer='ROOT',installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],
                imagesActuallyViewed=source,retainedImagesActuallyViewed=retained,visualAcceptance=True,
                sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,
                qualification='ROOT inspected all8 actual live390/1280day/night exports: both unchanged hotel and upper tower are framed together at native pose, original roof detail replaces its duplicate BASIC roof while active, surroundings remain visible. Actual peer failure/Base/Auto/eviction restoration is separately verified by installed HTTP lifecycle. No structural or device-performance claims follow from screenshots.')
    save(out/'ROOT-LIVE-IMAGE-OBSERVATIONS.json',result)
    module('unnamed_live_images_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-exact-live-unnamed-source-desktop-mobile-image-review',refs,result)


if __name__=='__main__':main()
