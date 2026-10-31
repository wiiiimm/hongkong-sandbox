"""Independent full-ledger, exact-old-catalogue and global-support assembly readback."""
from pathlib import Path
import os
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope


def main():
    base=ROOT/'docs/astra-city/government-import';cfgpath=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert cfgpath.is_relative_to(base);cfg=read(cfgpath);installed=base/(cfg['prefix']+'-supported-retained-original-installed-v1-'+cfg['date']);out=base/(cfg['prefix']+'-supported-retained-installed-root-readback-v1-'+cfg['date']);assert not out.exists();receipt,pins=authenticate(installed);sources=cfg['sources'];n=cfg['previousInstalled']+cfg['expectedFixedXLDelta'];assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=n,remaining=521-n)and receipt['sourceSHA256ByUid']==sources and receipt['newlyInstalled']==cfg['expectedFixedXLDelta'];assert receipt['completeCurrentCatalogueModels']==cfg['currentNativeActors']+len(sources)
    refs=[Path(__file__),cfgpath,installed/'result.json'];verified=0
    for path,sha in pins.items():
        p=ROOT/path;assert digest(p.read_bytes())==sha,path;refs.append(p);verified+=1
    inventory=base/cfg['previousNativeInventory'];_,oldpins=authenticate(inventory);refs.append(inventory/'result.json');oldcats={p:h for p,h in oldpins.items()if p.startswith('3d-viewer/city/data/official-models/')and p.endswith('/catalogue.json')};assert oldcats
    physical=read(base/cfg['physical']/'ROOT-PHYSICAL-REVIEW.json');update=physical['installedSupportUpdate'];changedpath='3d-viewer/'+update['url'];assert changedpath in oldcats and oldcats[changedpath]==update['beforeSHA256']
    aliases={r['originalPath']:r for r in receipt['historicalMutableByteSnapshots']};oldmodels=[]
    for p,h in oldcats.items():
        path=ROOT/p
        if p==changedpath:
            historical=aliases[p];saved=historical['savedHistoricalBytes'];oldpath=ROOT/saved['path'];assert digest(oldpath.read_bytes())==h==saved['sha256']==historical['originalSHA256'];refs.append(oldpath)
            beforecat=read(oldpath);expectedcat=__import__('copy').deepcopy(beforecat);owner=next(m for m in expectedcat['models']if m['uid']==update['ownerUid']);assert owner==update['beforeEntry'];owner['supportDependencies']=update['afterEntry']['supportDependencies'];assert owner==update['afterEntry'];assert read(path)==expectedcat;oldmodels.extend(beforecat['models'])
        else:
            assert digest(path.read_bytes())==h;oldmodels.extend(read(path)['models'])
        refs.append(path)
        for model in read(path)['models']:
            asset=path.parent/model['asset'];assert digest(asset.read_bytes())==model['sha256'];refs.append(asset)
    expectedold=__import__('copy').deepcopy(oldmodels);owner=next(m for m in expectedold if m['uid']==update['ownerUid']);assert owner==update['beforeEntry'];owner['supportDependencies']=update['afterEntry']['supportDependencies'];assert owner==update['afterEntry']
    assert len(oldmodels)==len({m['uid']for m in oldmodels})==cfg['currentNativeActors']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);urls={'3d-viewer/'+u for u in m['officialModelCatalogues']};assert set(oldcats)<=urls and len(urls-set(oldcats))==1;models=[];new=[]
    for url in m['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;entries=read(path)['models'];models.extend(entries)
        for entry in entries:
            if entry['uid']in sources:
                assert entry['sha256']==sources[entry['uid']]and all(entry.get(k)is True for k in ['publicationApproved','placementReviewed','identityReviewApproved']);assert not entry.get('retainedBasicSupportDependencies')and not entry.get('suppressesBuildingUids')and entry.get('verticalPlacementOffsetHKPD',0)==0
                asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset);new.append(entry)
    assert len(models)==len({e['uid']for e in models})==cfg['currentNativeActors']+len(sources);assert verify_support_scope(new,sources,cfg['supportByUid']);assert{e['uid']:e for e in models if e['uid']not in sources}=={e['uid']:e for e in expectedold}
    previous=base/cfg['previousCountReport'];old=read(previous);now=read(installed/'full-xl-current-count.json');before={r['sourceKey']:r for r in old['rows']};after={r['sourceKey']:r for r in now['rows']};assert set(before)==set(after)and len(after)==521;changed=[r for k,r in after.items()if r!=before[k]];expected=set(receipt['fixedXLDelta']['newFixedXLUids']);assert len(changed)==len(expected)==cfg['expectedFixedXLDelta']and{r['uid']for r in changed}==expected
    for r in changed:assert r['installedVerified']and r['runtimeSourceSHA256']==r['indexedSourceSHA256']==sources[r['uid']]
    support={};guard=module('supported_assembly_global_retained_readback',HERE.parent/'island-detail-integration/retained_basic_support.py');guard.stage_retained_basic_support(ROOT,m,{},support,read);assert{(r['uid'],r['supportUid'])for r in support['retainedBasicSupportChecks']} >= {('landsd/312858:0','landsd/176739:0'),('landsd/6801:0','landsd/304712:0')}
    inspectionpath=installed/'ROOT-LIVE-EXPORT-INSPECTION.json';inspection=read(inspectionpath);assert inspection['reviewer']=='ROOT'and inspection['visualAcceptance'];images=inspection['imagesActuallyViewed'];assert len(images)==len({q['path']for q in images})==4*len(sources);inspected={q['path']:q['sha256']for q in images};exports=[]
    for width in [390,1280]:
        folder=installed/('viewport-'+str(width));report=read(folder/'live-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==2*len(sources)
        for v in views:
            uid=v['uid'];assert v['pick']==v['collision']==uid and v['sourceSHA256']==sources[uid]and v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces'];path=folder/v['file'];key=str(path.relative_to(ROOT));sha=digest(path.read_bytes());assert sha==pins[key]==inspected[key];exports.append(dict(path=key,sha256=sha))
    retained=set(physical['retainedNativeUids']);current={m['uid']:m for m in models};retainedexports=[];failedexports=[]
    for width in [390,1280]:
        folder=installed/('viewport-'+str(width));report=read(folder/'live-browser.json');views=report['retainedNativeOwnViews']
        assert len(views)==2*len(retained)and{(v['uid'],v['time'])for v in views}=={(uid,t)for uid in retained for t in ['15:00','22:00']}
        for v in views:
            model=current[v['uid']];assert v['sourceSHA256']==model['sha256']and v['originalTriangles']==model['triangles']and v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and all(v['meshVisibility'])and not any(v['wireframeFlags'])
            path=folder/v['file'];q=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()));assert pins[q['path']]==q['sha256'];retainedexports.append(q)
        failed=report.get('retainedDependencyFallbackViews',[]);assert len(failed)==(1 if width==390 else 0)
        for v in failed:
            assert v['uid']==update['ownerUid']and v['sourceSHA256']==update['ownerSHA256']and v['basicLoaded']and not v['basicHidden']and not v['active']and v['fallbackFaces']>0 and not v['loadingTravel']and not v['travelling']and v['supportDependencies']==update['afterEntry']['supportDependencies']
            assert v['failedParents']==sorted(d['uid']for d in update['afterEntry']['supportDependencies'])
            path=folder/v['file'];q=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()));assert pins[q['path']]==q['sha256'];failedexports.append(q)
    assert sorted(inspection['retainedImagesActuallyViewed'],key=lambda q:q['path'])==sorted(retainedexports,key=lambda q:q['path'])
    assert inspection['dependencyFailureImagesActuallyViewed']==failedexports
    plan=read(HERE/'accepted'/(cfg['prefix']+'-supported-retained-qualified-stage-v2-'+cfg['date'])/'plan.json');terrain=plan['topLevelTerrainPatches'];assert len(terrain)==1;terrain=terrain[0];replacement=terrain['replaces']
    oldmanifest=read(ROOT/aliases[str(manifest.relative_to(ROOT))]['savedHistoricalBytes']['path'])
    assert len(m['terrainPatches'])==len(oldmanifest['terrainPatches'])and not any(p['url']==replacement['url']for p in m['terrainPatches'])
    assert [p for p in m['terrainPatches']if p['url']!=terrain['destination']]==[p for p in oldmanifest['terrainPatches']if p['url']!=replacement['url']]
    for url,sha in [(replacement['url'],replacement['sha256']),(terrain['destination'],terrain['sha256'])]:
        path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==sha;refs.append(path)
    assert set(read(ROOT/'3d-viewer'/terrain['destination'])['meta']['targetUids'])==set(replacement['retainedUids'])|set(read(base/cfg['patch']/'result.json')['uids'])
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==receipt['snapshotId']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid,sha in sources.items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],uid)).fetchone()==('installed-verified',sha)
    result=dict(uids=list(sources),passed=True,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],fullXLCurrentCounts=receipt['fullXLCurrentCounts'],completeCurrentCatalogueModels=len(models),verifiedEvidenceFiles=verified,liveExportsActuallyViewed=exports,ROOTLiveVisualInspection=inspection,completeFixedXLRowsCompared=521,onlyChangedFixedXLUids=sorted(expected),unchangedOldCatalogueActors=len(oldmodels),allOldActorsPreservedExceptReviewedSupportDependencies=True,reviewedInstalledSupportUpdate=update,retainedLiveExportsActuallyViewed=retainedexports,dependencyFailureLiveExportsActuallyViewed=failedexports,terrainReplacementVerified=terrain,retainedBasicSupportChecks=support['retainedBasicSupportChecks'],sourceGeometryChanges=0,aiGeometryModelling=False)
    save(out/'ROOT-READBACK.json',result);refs.extend([manifest,pointer,previous,inspectionpath,HERE/'original_supported_catalogue_scope_v1_20261024.py',HERE.parent/'island-detail-integration/retained_basic_support.py']);module('supported_retained_assembly_installed_root_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'installed-original-assembly-independent-whole-xl-and-global-support-readback',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
