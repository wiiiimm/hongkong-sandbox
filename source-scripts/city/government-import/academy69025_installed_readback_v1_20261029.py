"""Independent exact installed source, all old actors, full XL and support readback."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from retained_parent_install_contract_v1_20261029 import terrain_delta,retained_views
UID='landsd/69025:0'
SOURCE='75d1193ec409e8522705df1f262f647e12beda5c4e309f9905ca8ba7e5e88414'
BATCH='government-xl-academy69025-installed-root-readback-v1-20261029'
INSTALL='government-xl-academy69025-nested-original-installed-v4-20261029'


def main():
    base=ROOT/'docs/astra-city/government-import';installed=base/INSTALL;out=base/BATCH;assert not out.exists()
    receipt,pins=authenticate(installed);assert receipt['sourceSHA256ByUid']=={UID:SOURCE}and receipt['newlyInstalled']==1
    assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=402,remaining=119)
    assert receipt['completeCurrentCatalogueModels']==7017
    refs=[Path(__file__),installed/'result.json'];verified=0
    for path,sha in pins.items():
        p=ROOT/path;assert digest(p.read_bytes())==sha,path;refs.append(p);verified+=1
    manifest=ROOT/'3d-viewer/city/data/manifest.json';current=read(manifest)
    original=next(r for r in receipt['historicalMutableByteSnapshots']if r['originalPath']=='3d-viewer/city/data/manifest.json')
    oldpath=ROOT/original['savedHistoricalBytes']['path'];assert digest(oldpath.read_bytes())==original['originalSHA256'];old=read(oldpath)
    def models(data):
        rows=[]
        for url in data['officialModelCatalogues']:
            path=ROOT/'3d-viewer'/url;rows.extend(read(path)['models']);refs.append(path)
        return rows
    before,after=models(old),models(current)
    assert len(before)==len({r['uid']for r in before})==7016
    assert len(after)==len({r['uid']for r in after})==7017
    assert after[:-1]==before and after[-1]['uid']==UID
    source=after[-1];assert source['sha256']==SOURCE and source['triangles']==14462
    assert all(source[k]is True for k in ['placementReviewed','publicationApproved','identityReviewApproved'])and source['proceduralWindows']is False
    assert not source.get('supportDependencies')and not source.get('suppressesBuildingUids')and source.get('verticalPlacementOffsetHKPD',0)==0
    assets=0
    for url in current['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        for entry in read(path)['models']:
            asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];assets+=1
    previous=base/'government-xl-fortune242706-original-installed-v4-20261029/full-xl-current-count.json'
    oldrows={r['sourceKey']:r for r in read(previous)['rows']};newrows={r['sourceKey']:r for r in read(installed/'full-xl-current-count.json')['rows']}
    assert set(oldrows)==set(newrows)and len(newrows)==521
    changed=[r for k,r in newrows.items()if r!=oldrows[k]];assert len(changed)==1 and changed[0]['uid']==UID and changed[0]['installedVerified']and changed[0]['runtimeSourceSHA256']==changed[0]['indexedSourceSHA256']==SOURCE
    # Existing installed support obligations remain mandatory on the entire map.
    guard=module('lookout_independent_global_support',HERE.parent/'island-detail-integration/retained_basic_support.py');support={};guard.stage_retained_basic_support(ROOT,current,{},support,read)
    assert {('landsd/312858:0','landsd/176739:0'),('landsd/6801:0','landsd/304712:0')}<={(r['uid'],r['supportUid'])for r in support['retainedBasicSupportChecks']}
    image_batch=base/'government-xl-academy69025-live-image-review-v1-20261029';image_receipt,image_pins=authenticate(image_batch);inspection=read(image_batch/'ROOT-LIVE-IMAGE-OBSERVATIONS.json');assert digest((image_batch/'ROOT-LIVE-IMAGE-OBSERVATIONS.json').read_bytes())==image_pins[str((image_batch/'ROOT-LIVE-IMAGE-OBSERVATIONS.json').relative_to(ROOT))];refs.extend([image_batch/'result.json',image_batch/'ROOT-LIVE-IMAGE-OBSERVATIONS.json']);assert inspection['reviewer']=='ROOT'and inspection['imagesActuallyViewed']and inspection['visualAcceptance']
    expected=set()
    for width in [390,1280]:
        folder=installed/('viewport-'+str(width));report=read(folder/'live-browser.json');assert report['passed']and not report['errors']
        views=[r for r in report['views']if 'time'in r];assert len(views)==2
        for v in views:
            assert v['uid']==v['pick']==v['collision']==UID and v['sourceSHA256']==SOURCE and v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']
            expected.add(str((folder/v['file']).relative_to(ROOT)))
    assert {r['path']for r in inspection['imagesActuallyViewed']}==expected and len(expected)==4
    for ref in inspection['imagesActuallyViewed']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']==pins[ref['path']]
    plan=read(HERE/'accepted/government-xl-academy69025-nested-qualified-stage-v2-20261029/plan.json');terrain_delta(old['terrainPatches'],current['terrainPatches'],plan['topLevelTerrainPatches'])
    expected_retained={m['uid']:m['sha256']for m in after if m['uid']in ['landsd/337711:0','landsd/337830:0']};assert len(expected_retained)==2
    live=read(installed/'live-browser.json');retained_views(live['retainedNativeOwnViews'],expected_retained,[390,1280])
    assert len(inspection['retainedImagesActuallyViewed'])==8
    for image in inspection['retainedImagesActuallyViewed']:assert digest((ROOT/image['path']).read_bytes())==image['sha256']==pins[image['path']]
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==receipt['snapshotId']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],UID)).fetchone()==('installed-verified',SOURCE)
    result=dict(uids=[UID],passed=True,installationIndependentlyVerified=True,sourceSHA256ByUid={UID:SOURCE},installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],fullXLCurrentCounts=receipt['fullXLCurrentCounts'],completeCurrentCatalogueModels=7017,oldEntriesPreserved=7016,allCurrentAssetsRehashed=assets,verifiedEvidenceFiles=verified,completeFixedXLRowsCompared=521,onlyChangedFixedXLUid=UID,liveExportsActuallyViewed=inspection['imagesActuallyViewed'],retainedBasicSupportChecks=support['retainedBasicSupportChecks'],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False)
    save(out/'ROOT-READBACK.json',result);refs.extend([manifest,oldpath,previous,pointer,image_batch/'ROOT-LIVE-IMAGE-OBSERVATIONS.json',HERE.parent/'island-detail-integration/retained_basic_support.py'])
    module('lookout_installed_independent_readback',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'installed-academy-independent-whole-xl-actor-assets-terrain-and-support-readback',list(dict.fromkeys(refs)),result)
    print(dict(passed=True,installedFixedXL=402,actors=7017,sourceGeometryChanges=0),flush=True)

if __name__=='__main__':main()
