"""Independent full-ledger, exact-old-catalogue and global-support assembly readback."""
from pathlib import Path
import os
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope
from yoho_five_original_catalogue_scope_v1_20261024 import verify_metadata,SOURCES,RETAINED,PARENT


def main():
    base=ROOT/'docs/astra-city/government-import';cfgpath=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert cfgpath.is_relative_to(base);cfg=read(cfgpath);installed=base/(cfg['prefix']+'-original-installed-v3-'+cfg['date']);out=base/(cfg['prefix']+'-installed-root-readback-v1-'+cfg['date']);assert not out.exists();receipt,pins=authenticate(installed);sources=cfg['sources'];n=cfg['previousInstalled']+cfg['expectedFixedXLDelta'];assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=n,remaining=521-n)and receipt['sourceSHA256ByUid']==sources and receipt['newlyInstalled']==cfg['expectedFixedXLDelta'];assert receipt['completeCurrentCatalogueModels']==cfg['currentNativeActors']+len(sources)
    refs=[Path(__file__),cfgpath,installed/'result.json'];verified=0
    for path,sha in pins.items():
        p=ROOT/path;assert digest(p.read_bytes())==sha,path;refs.append(p);verified+=1
    inventory=base/cfg['previousNativeInventory'];_,oldpins=authenticate(inventory);refs.append(inventory/'result.json');oldcats={p:h for p,h in oldpins.items()if p.startswith('3d-viewer/city/data/official-models/')and p.endswith('/catalogue.json')};assert oldcats
    oldmodels=[]
    for p,h in oldcats.items():
        path=ROOT/p;assert digest(path.read_bytes())==h;refs.append(path);entries=read(path)['models'];oldmodels.extend(entries)
        for entry in entries:
            asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset)
    assert len(oldmodels)==len({m['uid']for m in oldmodels})==cfg['currentNativeActors']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);urls={'3d-viewer/'+u for u in m['officialModelCatalogues']};assert set(oldcats)<=urls and len(urls-set(oldcats))==1;models=[];new=[]
    for url in m['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;entries=read(path)['models'];models.extend(entries)
        for entry in entries:
            if entry['uid']in sources:
                assert entry['sha256']==sources[entry['uid']]and all(entry.get(k)is True for k in ['publicationApproved','placementReviewed','identityReviewApproved']);assert not entry.get('retainedBasicSupportDependencies')and not entry.get('suppressesBuildingUids')and entry.get('verticalPlacementOffsetHKPD',0)==0
                asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset);new.append(entry)
    assert len(models)==len({e['uid']for e in models})==cfg['currentNativeActors']+len(sources);assert verify_support_scope(new,sources,cfg['supportByUid'])and sources==SOURCES and verify_metadata(new);assert{e['uid']:e for e in models if e['uid']not in sources}=={e['uid']:e for e in oldmodels}
    previous=base/cfg['previousCountReport'];old=read(previous);now=read(installed/'full-xl-current-count.json');before={r['sourceKey']:r for r in old['rows']};after={r['sourceKey']:r for r in now['rows']};assert set(before)==set(after)and len(after)==521;changed=[r for k,r in after.items()if r!=before[k]];expected=set(receipt['fixedXLDelta']['newFixedXLUids']);assert len(changed)==len(expected)==cfg['expectedFixedXLDelta']and{r['uid']for r in changed}==expected
    for r in changed:assert r['installedVerified']and r['runtimeSourceSHA256']==r['indexedSourceSHA256']==sources[r['uid']]
    support={};guard=module('supported_assembly_global_retained_readback',HERE.parent/'island-detail-integration/retained_basic_support.py');guard.stage_retained_basic_support(ROOT,m,{},support,read);assert{(r['uid'],r['supportUid'])for r in support['retainedBasicSupportChecks']} >= {('landsd/312858:0','landsd/176739:0'),('landsd/6801:0','landsd/304712:0')}
    inspectionpath=installed/'ROOT-LIVE-EXPORT-INSPECTION.json';inspection=read(inspectionpath);assert inspection['reviewer']=='ROOT'and inspection['visualAcceptance'];images=inspection['imagesActuallyViewed'];assert len(images)==len({q['path']for q in images})==4*len(sources);inspected={q['path']:q['sha256']for q in images};exports=[]
    retainedImages=inspection['retainedImagesActuallyViewed'];assert len(retainedImages)==len({q['path']for q in retainedImages})==4*len(RETAINED);retainedInspected={q['path']:q['sha256']for q in retainedImages};retainedExports=[]
    for width in [390,1280]:
        folder=installed/('viewport-'+str(width));report=read(folder/'live-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==2*len(sources)
        retained=report['retainedNativeOwnViews'];assert len(retained)==2*len(RETAINED)and{v['uid']for v in retained}==RETAINED
        for v in retained:
            uid=v['uid'];entry=next(m for m in oldmodels if m['uid']==uid);assert v['sourceSHA256']==entry['sha256']and v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces'];path=folder/v['file'];key=str(path.relative_to(ROOT));sha=digest(path.read_bytes());assert sha==pins[key]==retainedInspected[key];retainedExports.append(dict(path=key,sha256=sha))
        assert any({m['uid']for m in j['models']}==set(sources)and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in report['jointViews'])
        for v in views:
            uid=v['uid'];assert v['pick']==v['collision']==uid and v['sourceSHA256']==sources[uid]and v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces'];path=folder/v['file'];key=str(path.relative_to(ROOT));sha=digest(path.read_bytes());assert sha==pins[key]==inspected[key];exports.append(dict(path=key,sha256=sha))
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==receipt['snapshotId']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid,sha in sources.items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],uid)).fetchone()==('installed-verified',sha)
    result=dict(uids=list(sources),passed=True,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],fullXLCurrentCounts=receipt['fullXLCurrentCounts'],completeCurrentCatalogueModels=len(models),verifiedEvidenceFiles=verified,liveExportsActuallyViewed=exports,retainedLiveExportsActuallyViewed=retainedExports,allPreviousAssetBytesVerified=True,previousAssetsVerified=len(oldmodels),ROOTLiveVisualInspection=inspection,completeFixedXLRowsCompared=521,onlyChangedFixedXLUids=sorted(expected),unchangedOldCatalogueActors=len(oldmodels),allOldCatalogueBytesAndEntriesIdentical=True,retainedBasicSupportChecks=support['retainedBasicSupportChecks'],sourceGeometryChanges=0,aiGeometryModelling=False)
    patchpath=ROOT/'3d-viewer'/cfg['terrainDestination'];patch=read(patchpath);assert patch['meta']['targetUids']==[PARENT]and len(patch['nativeMesh']['index'])==1236;refs.append(patchpath)
    save(out/'ROOT-READBACK.json',result);refs.extend([manifest,pointer,previous,inspectionpath,HERE/'yoho_five_original_catalogue_scope_v1_20261024.py',HERE/'original_supported_catalogue_scope_v1_20261024.py',HERE.parent/'island-detail-integration/retained_basic_support.py']);module('supported_assembly_installed_root_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'installed-original-assembly-independent-whole-xl-and-global-support-readback',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
