"""Independent exact-source/full-XL/global-support readback after live installation."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';installed=base/'government-xl-university-hall-standalone-original-installed-v2-20261024';out=base/'government-xl-university-hall-standalone-installed-root-readback-v1-20261024';assert not out.exists()
    receipt,pins=authenticate(installed);assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=340,remaining=181);assert receipt['completeCurrentCatalogueModels']==6864 and receipt['newlyInstalled']==1
    refs=[Path(__file__),installed/'result.json'];verified=0
    for path,sha in pins.items():
        p=ROOT/path;assert digest(p.read_bytes())==sha,path;refs.append(p);verified+=1
    uid='landsd/93417:0';sha='debfebe52c8a04231cd20bdbfeaa9057f28af6e9df054769f9c57118f4d5aa60';assert receipt['sourceSHA256ByUid']=={uid:sha}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);models=[];source=None
    for url in m['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;entries=read(path)['models'];models.extend(entries)
        for entry in entries:
            if entry['uid']==uid:source=entry;asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==sha;refs.append(asset)
    assert len(models)==len({e['uid']for e in models})==6864 and source['sha256']==sha and source['triangles']==14777
    assert all(source.get(k)is True for k in ['publicationApproved','placementReviewed','identityReviewApproved']) and source['proceduralWindows']is False
    assert not source.get('supportDependencies') and not source.get('retainedBasicSupportDependencies') and not source.get('suppressesBuildingUids') and source.get('verticalPlacementOffsetHKPD',0)==0
    previous=base/'government-xl-two-basic-supported-original-installed-v2-20261023/full-xl-current-count.json';old=read(previous);now=read(installed/'full-xl-current-count.json');before={r['sourceKey']:r for r in old['rows']};after={r['sourceKey']:r for r in now['rows']};assert set(before)==set(after) and len(after)==521
    changed=[]
    for key,row in after.items():
        if row!=before[key]:changed.append(row)
    assert len(changed)==1 and changed[0]['uid']==uid and changed[0]['installedVerified'] and changed[0]['runtimeSourceSHA256']==changed[0]['indexedSourceSHA256']==sha
    guard=module('standalone_retained_global_readback',HERE.parent/'island-detail-integration/retained_basic_support.py');support={};guard.stage_retained_basic_support(ROOT,m,{},support,read)
    assert {(r['uid'],r['supportUid'])for r in support['retainedBasicSupportChecks']} >= {('landsd/312858:0','landsd/176739:0'),('landsd/6801:0','landsd/304712:0')}
    exports=[]
    for width in [390,1280]:
        folder=installed/('viewport-'+str(width));report=read(folder/'live-browser.json');assert report['passed'] and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==2
        for v in views:
            assert v['uid']==v['pick']==v['collision']==uid and v['sourceSHA256']==sha and v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces'] and not v['retained']
            path=folder/v['file'];assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];exports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    assert len(exports)==4 and receipt['terrainEdits']is False and receipt['sourceGeometryChanges']==receipt['sourcePoseChanges']==0
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==receipt['snapshotId']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],uid)).fetchone()==('installed-verified',sha)
    result=dict(uids=[uid],passed=True,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],fullXLCurrentCounts=receipt['fullXLCurrentCounts'],completeCurrentCatalogueModels=6864,verifiedEvidenceFiles=verified,liveExportsActuallyViewed=exports,retainedBasicSupportChecks=support['retainedBasicSupportChecks'],completeFixedXLRowsCompared=521,onlyChangedFixedXLUid=uid,sourceGeometryChanges=0,terrainEdits=False,aiGeometryModelling=False)
    save(out/'ROOT-READBACK.json',result);refs.extend([manifest,pointer,previous,HERE.parent/'island-detail-integration/retained_basic_support.py']);module('university_installed_root_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'installed-standalone-original-independent-whole-xl-and-global-support-readback',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
