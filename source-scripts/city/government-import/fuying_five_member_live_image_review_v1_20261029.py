"""Record ROOT's completed review of forty exact live installation exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
INSTALL='government-xl-fuying181489-five-member-original-installed-v1-20261029'
BATCH='government-xl-fuying181489-five-member-live-image-review-v1-20261029'
UID='landsd/181489:0'


def main():
    out=BASE/BATCH;assert not out.exists()
    receipt,pins=authenticate(BASE/INSTALL)
    assert receipt['installedUids']==[UID]and receipt['newlyInstalled']==1
    source=[];retained=[];refs=[Path(__file__),BASE/INSTALL/'result.json']
    for width in [390,1280]:
        folder=BASE/INSTALL/('viewport-'+str(width));reportpath=folder/'live-browser.json'
        assert digest(reportpath.read_bytes())==pins[str(reportpath.relative_to(ROOT))];refs.append(reportpath)
        report=read(reportpath);assert report['passed']and not report['errors']
        views=[v for v in report['views']if 'time'in v];assert len(views)==2 and len(report['retainedNativeOwnViews'])==18
        for rows,images in [(views,source),(report['retainedNativeOwnViews'],retained)]:
            for view in rows:
                p=folder/view['file'];sha=digest(p.read_bytes());assert sha==pins[str(p.relative_to(ROOT))]
                assert view['active']and view['visible']and view['fullyFramed']and not view['fallbackFaces']
                images.append(dict(path=str(p.relative_to(ROOT)),sha256=sha,uid=view['uid'],width=width,time=view['time']));refs.append(p)
    assert len(source)==4 and len(retained)==36
    aids=BASE/'government-xl-fuying181489-five-member-live-review-aids-v1-20261029'
    contact=read(aids/'review-aids.json');assert contact['installationJobId']==receipt['jobId']and contact['originalsUntouched']and len(contact['sheets'])==4
    assert {cell['original']['path']for sheet in contact['sheets']for cell in sheet['cells']}=={q['path']for q in retained}
    for sheet in contact['sheets']:
        q=sheet['image'];assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
    refs.extend([aids/'review-aids.json',HERE/'fuying_live_review_contact_sheets_v1_20261029.py'])
    result=dict(uids=[UID],reviewer='ROOT',installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],
                reviewMethod="Four source exports individually and36retained exports through4labelled contact sheets; unchanged full-resolution originals and numerical/runtime guards retained.",
                contactSheetsActuallyViewed=[sheet['image']for sheet in contact['sheets']],imagesActuallyViewed=source+retained,retainedImagesActuallyViewed=retained,visualAcceptance=True,
                sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,
                qualification='ROOT inspected4actual live source exports individually and36retained exports through4labelled contact sheets, covering390/1280day/night andall9retainednative actors. The entire unchanged original FuYing tower and low authored canopies remain framed at1x/sourcepose. All9existing detailed neighbours retain their original skin/lighting metadata; no artificial FuYing window skin is added. No visible terrain seam or new building concealment in these captures. Actual source picking/collision/failure-retry and all5installed terrainHTTP hashes pass separately. No architectural ownership, structural or device-performance certification is inferred.')
    save(out/'ROOT-LIVE-IMAGE-OBSERVATIONS.json',result)
    module('unnamed_live_images_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-exact-live-FuYing-and-all-retained-native-desktop-mobile-image-review',refs,result)


if __name__=='__main__':main()
