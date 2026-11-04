# V5: enumerate every catalogue from the saved pre-install manifest, preserving all old asset, support, terrain, live and full521 checks.
"""Independent full-ledger, exact-old-catalogue and global-support assembly readback."""
from pathlib import Path
import os
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope


def main():
    base=ROOT/'docs/astra-city/government-import';cfgpath=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert cfgpath.is_relative_to(base);cfg=read(cfgpath);installed=base/(cfg['prefix']+'-retained-original-installed-v1-'+cfg['date']);out=base/(cfg['prefix']+'-installed-root-readback-v1-'+cfg['date']);assert not out.exists();receipt,pins=authenticate(installed);sources=cfg['sources'];n=cfg['previousInstalled']+cfg['expectedFixedXLDelta'];assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=n,remaining=521-n)and receipt['sourceSHA256ByUid']==sources and receipt['newlyInstalled']==cfg['expectedFixedXLDelta'];assert receipt['completeCurrentCatalogueModels']==cfg['currentNativeActors']+len(sources)
    refs=[Path(__file__),cfgpath,installed/'result.json'];verified=0
    for path,sha in pins.items():
        p=ROOT/path;assert digest(p.read_bytes())==sha,path;refs.append(p);verified+=1
    inventory=base/cfg.get('previousNativeInventory','government-xl-after-harbour-glory-current-native-bounds-v1-20261102');_,oldpins=authenticate(inventory);refs.append(inventory/'result.json')
    history_for_catalogues=read(installed/'historical-input-context.json')
    saved=next(q for q in history_for_catalogues['mutableCurrentByteSnapshots']if q['originalPath']=='3d-viewer/city/data/manifest.json')
    oldpath=ROOT/saved['savedHistoricalBytes']['path'];assert digest(oldpath.read_bytes())==saved['originalSHA256']==pins[str(oldpath.relative_to(ROOT))]
    oldpaths=['3d-viewer/'+u for u in read(oldpath)['officialModelCatalogues']]
    assert len(oldpaths)==len(set(oldpaths))and oldpaths
    oldcats={p:oldpins[p]for p in oldpaths};refs.extend([installed/'historical-input-context.json',oldpath])
    oldmodels=[]
    for p,h in oldcats.items():
        path=ROOT/p;assert digest(path.read_bytes())==h;refs.append(path);oldmodels.extend(read(path)['models'])
        for entry in read(path)['models']:
            asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset)
    assert len(oldmodels)==len({m['uid']for m in oldmodels})==cfg['currentNativeActors']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);urls={'3d-viewer/'+u for u in m['officialModelCatalogues']};assert set(oldcats)<=urls and len(urls-set(oldcats))==1;models=[];new=[]
    for url in m['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;entries=read(path)['models'];models.extend(entries)
        for entry in entries:
            if entry['uid']in sources:
                assert entry['sha256']==sources[entry['uid']]and all(entry.get(k)is True for k in ['publicationApproved','placementReviewed','identityReviewApproved']);assert not entry.get('retainedBasicSupportDependencies')and not entry.get('suppressesBuildingUids')and entry.get('verticalPlacementOffsetHKPD',0)==0
                asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset);new.append(entry)
    assert len(models)==len({e['uid']for e in models})==cfg['currentNativeActors']+len(sources);assert verify_support_scope(new,sources,cfg.get('supportByUid',{}));assert{e['uid']:e for e in models if e['uid']not in sources}=={e['uid']:e for e in oldmodels}
    previous=base/cfg['previousCountReport'];old=read(previous);now=read(installed/'full-xl-current-count.json');before={r['sourceKey']:r for r in old['rows']};after={r['sourceKey']:r for r in now['rows']};assert set(before)==set(after)and len(after)==521;changed=[r for k,r in after.items()if r!=before[k]];expected=set(receipt['fixedXLDelta']['newFixedXLUids']);assert len(changed)==len(expected)==cfg['expectedFixedXLDelta']and{r['uid']for r in changed}==expected
    for r in changed:assert r['installedVerified']and r['runtimeSourceSHA256']==r['indexedSourceSHA256']==sources[r['uid']]
    support={};guard=module('supported_assembly_global_retained_readback',HERE.parent/'island-detail-integration/retained_basic_support.py');guard.stage_retained_basic_support(ROOT,m,{},support,read);assert{(r['uid'],r['supportUid'])for r in support['retainedBasicSupportChecks']} >= {('landsd/312858:0','landsd/176739:0'),('landsd/6801:0','landsd/304712:0')}
    inspectionpath=installed/'ROOT-LIVE-EXPORT-INSPECTION.json';inspection=read(inspectionpath);assert inspection['reviewer']=='ROOT'and inspection['visualAcceptance'];images=inspection['imagesActuallyViewed'];assert len(images)==len({q['path']for q in images})==4*len(sources);inspected={q['path']:q['sha256']for q in images};exports=[]
    for width in [390,1280]:
        folder=installed/('viewport-'+str(width));report=read(folder/'live-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==2*len(sources)
        for v in views:
            uid=v['uid'];assert v['pick']==v['collision']==uid and v['sourceSHA256']==sources[uid]and v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces'];path=folder/v['file'];key=str(path.relative_to(ROOT));sha=digest(path.read_bytes());assert sha==pins[key]==inspected[key];exports.append(dict(path=key,sha256=sha))
    plan=read(HERE/'accepted'/(cfg['prefix']+'-retained-qualified-stage-v2-'+cfg['date'])/'plan.json');assert len(plan['topLevelTerrainPatches'])==1
    expected_patch=plan['topLevelTerrainPatches'][0];patchpath=ROOT/'3d-viewer'/cfg['terrainDestination'];assert digest(patchpath.read_bytes())==expected_patch['sha256']
    assert read(patchpath)['meta']['targetUids']==cfg['terrainTargetUids'];refs.append(patchpath)
    history=read(installed/'historical-input-context.json');old_manifest=next(q for q in history['mutableCurrentByteSnapshots']if q['originalPath']=='3d-viewer/city/data/manifest.json');before=read(ROOT/old_manifest['savedHistoricalBytes']['path'])
    replacement=expected_patch['replaces'];assert len(m['terrainPatches'])==len(before['terrainPatches'])
    assert sum(t['url']==replacement['url']for t in before['terrainPatches'])==1 and not any(t['url']==replacement['url']for t in m['terrainPatches'])
    assert sum(t['url']==cfg['terrainDestination']for t in m['terrainPatches'])==1
    assert [t for t in m['terrainPatches']if t['url']!=cfg['terrainDestination']]==[t for t in before['terrainPatches']if t['url']!=replacement['url']]
    assert m['counts']==before['counts']
    # Independently replay only the ten declared metadata edits against saved
    # pre-install tile bytes, preserving every other form and manifest field.
    import copy,json
    expected_tiles=copy.deepcopy(before['tiles']);updates=plan['illustrativeFoundations']+plan['unsurveyedBasicFoundations']
    assert len(plan['illustrativeFoundations'])==7 and len(plan['unsurveyedBasicFoundations'])==3 and len({u['uid']for u in updates})==10
    for url in sorted({u['tile']for u in updates}):
        path=ROOT/'3d-viewer'/url;oldrow=next(r for r in history['mutableCurrentByteSnapshots']if r['originalPath']==str(path.relative_to(ROOT)))
        savedpath=ROOT/oldrow['savedHistoricalBytes']['path'];assert digest(savedpath.read_bytes())==oldrow['originalSHA256'];expected_data=read(savedpath)
        for update in [u for u in updates if u['tile']==url]:
            b=next(b for b in expected_data['buildings']if b['uid']==update['uid']);assert b==update['before']
            b['foundationBase']=update['foundationBase'];b['foundationPolicy']='terrain-derived-illustrative-posts'if update in plan['illustrativeFoundations']else'terrain-derived-unsurveyed-basic-foundation-v1'
        assert read(path)==expected_data
        rows=[t for t in expected_tiles if t['url']==url];assert len(rows)==1;rows[0]['bytes']=len(path.read_bytes());refs.extend([path,savedpath])
    assert m['tiles']==expected_tiles
    assert all(model['activationGroup']==sorted(sources)for model in new)
    # Revalidate the new retained foundation registry against actual source
    # forms, current catalogue visibility and exact installed terrain geometry.
    import sys
    sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
    footing=module('hkust_unsurveyed_retained_readback',HERE.parent/'island-detail-integration/basic_unsurveyed_foundations.py');footing_report={}
    footing.stage_unsurveyed_foundations(ROOT,{},copy.deepcopy(m),{},footing_report,read,lambda p:digest(p.read_bytes()),lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode())
    assert set(footing_report['retainedUnsurveyedBasicFoundationChecks'])=={'landsd/31181:0','landsd/309838:0','landsd/339024:0'}
    refs.append(HERE.parent/'island-detail-integration/basic_unsurveyed_foundations.py')
    atomic=read(installed/'atomic-lifecycle/report.json');assert atomic['passed']and not atomic['pageErrors']and len(atomic['cases'])==4
    assert {c['failedUid']for c in atomic['cases']if c['width']==390}==set(sources)
    assert all(c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and not c['audit']['violations']for c in atomic['cases'])

    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==receipt['snapshotId']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid,sha in sources.items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],uid)).fetchone()==('installed-verified',sha)
    result=dict(uids=list(sources),passed=True,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],fullXLCurrentCounts=receipt['fullXLCurrentCounts'],completeCurrentCatalogueModels=len(models),verifiedEvidenceFiles=verified,liveExportsActuallyViewed=exports,ROOTLiveVisualInspection=inspection,completeFixedXLRowsCompared=521,onlyChangedFixedXLUids=sorted(expected),allPreviousAssetBytesVerified=True,previousAssetsVerified=len(oldmodels),unchangedOldCatalogueActors=len(oldmodels),allOldCatalogueBytesAndEntriesIdentical=True,retainedBasicSupportChecks=support['retainedBasicSupportChecks'],sourceGeometryChanges=0,aiGeometryModelling=False,exactReviewedBasicMetadataChangesVerified=10,retainedUnsurveyedFoundationChecks=footing_report['retainedUnsurveyedBasicFoundationChecks'],actualInstalledAtomicLifecyclePassed=True)
    save(out/'ROOT-READBACK.json',result);refs.extend([manifest,pointer,previous,inspectionpath,HERE/'original_supported_catalogue_scope_v1_20261024.py',HERE.parent/'island-detail-integration/retained_basic_support.py']);module('supported_assembly_installed_root_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'installed-original-assembly-independent-whole-xl-and-global-support-readback',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
