"""Record ROOT's completed review of twelve exact live installation exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
INSTALL='government-xl-academy69025-nested-original-installed-v4-20261029'
BATCH='government-xl-academy69025-live-image-review-v1-20261029'
UID='landsd/69025:0'


def main():
    out=BASE/BATCH;assert not out.exists()
    receipt,pins=authenticate(BASE/INSTALL)
    assert receipt['installedUids']==[UID]and receipt['newlyInstalled']==1
    source=[];retained=[];refs=[Path(__file__),BASE/INSTALL/'result.json']
    for width in [390,1280]:
        folder=BASE/INSTALL/('viewport-'+str(width));reportpath=folder/'live-browser.json'
        assert digest(reportpath.read_bytes())==pins[str(reportpath.relative_to(ROOT))];refs.append(reportpath)
        report=read(reportpath);assert report['passed']and not report['errors']
        views=[v for v in report['views']if 'time'in v];assert len(views)==2 and len(report['retainedNativeOwnViews'])==4
        for rows,images in [(views,source),(report['retainedNativeOwnViews'],retained)]:
            for view in rows:
                p=folder/view['file'];sha=digest(p.read_bytes());assert sha==pins[str(p.relative_to(ROOT))]
                assert view['active']and view['visible']and view['fullyFramed']and not view['fallbackFaces']
                images.append(dict(path=str(p.relative_to(ROOT)),sha256=sha,uid=view['uid'],width=width,time=view['time']));refs.append(p)
    assert len(source)==4 and len(retained)==8
    result=dict(uids=[UID],reviewer='ROOT',installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],
                imagesActuallyViewed=source,retainedImagesActuallyViewed=retained,visualAcceptance=True,
                sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,
                qualification='ROOT inspected each of the12 actual live390/1280day/night exports. The complete white curved administration/plaza component and exterior spiral stair are visible at native pose; the retained Theatre and Academy blocks remain present and framed. Existing neighbouring night-window skins are unchanged. No screenshot-only structural or performance claim is made.')
    save(out/'ROOT-LIVE-IMAGE-OBSERVATIONS.json',result)
    module('academy_live_images_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-exact-live-source-and-retained-desktop-mobile-image-review',refs,result)


if __name__=='__main__':main()
