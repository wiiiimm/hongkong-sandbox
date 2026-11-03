"""Independent whole-521, old-asset, owner, terrain and live-export readback."""
import copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_candidate_atomic_catalogue_contract_v1_20261103 import verify as verify_metadata
from silvercord_lippo_two_descriptor_qualified_stage_v1_20261103 import STAGE,BASE,SOURCE,RUNTIME,PREVIOUS,GROUND

BATCH='government-xl-silvercord-lippo-original-installed-v1-20261103'
OUT='government-xl-silvercord-lippo-installed-root-readback-v1-20261103'


def verify_fixed_cohort(previous,current,sources):
    assert previous['counts']==dict(total=521,installedVerified=427,remaining=94)
    assert current['counts']==dict(total=521,installedVerified=429,remaining=92)
    a={r['sourceKey']:r for r in previous['rows']};b={r['sourceKey']:r for r in current['rows']}
    assert len(previous['rows'])==len(current['rows'])==len(a)==len(b)==521 and set(a)==set(b)
    for report in [previous,current]:
        assert all(type(r['installedVerified'])is bool for r in report['rows'])
        assert sum(r['installedVerified']for r in report['rows'])==report['counts']['installedVerified']
        assert sum(r['uid']is None for r in report['rows'])==2
        assert all(not r['installedVerified']for r in report['rows']if r['uid']is None)
    changed=[r for k,r in b.items()if r!=a[k]]
    assert len(changed)==2 and {r['uid']for r in changed}==GROUND
    for r in changed:
        assert not a[r['sourceKey']]['installedVerified'] and r['installedVerified']
        assert r['runtimeSourceSHA256']==r['indexedSourceSHA256']==sources[r['uid']]
    return True


def main():
    installed=BASE/BATCH;out=BASE/OUT
    assert not out.exists()
    receipt,pins=authenticate(installed)
    sources=receipt['sourceSHA256ByUid']
    assert len(sources)==5 and receipt['newlyInstalled']==2 and receipt['completeCurrentCatalogueModels']==7106
    assert receipt['fullXLCurrentCounts']==dict(total=521,installedVerified=429,remaining=92)
    refs=[Path(__file__),installed/'result.json']
    for path,sha in pins.items():
        p=(ROOT/path).resolve();assert p.is_relative_to(ROOT.resolve())
        assert digest(p.read_bytes())==sha,path
        refs.append(p)
    source_review=read(BASE/SOURCE/'ROOT-SOURCE-REVIEW.json')
    update=source_review['installedSupportUpdate']
    history=read(installed/'historical-input-context.json')
    aliases={r['originalPath']:r for r in history['mutableCurrentByteSnapshots']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    old_ref=aliases[str(manifest.relative_to(ROOT))]
    old_path=ROOT/old_ref['savedHistoricalBytes']['path']
    assert digest(old_path.read_bytes())==old_ref['originalSHA256']==source_review['currentManifest']['sha256']
    before,after=read(old_path),read(manifest)
    _,old_pins=authenticate(BASE/SOURCE)
    old_models=[]
    for url in before['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;key=str(p.relative_to(ROOT));sha=old_pins[key]
        if url==update['url']:
            saved=aliases[key]['savedHistoricalBytes'];oldcat=ROOT/saved['path']
            assert digest(oldcat.read_bytes())==saved['sha256']==sha==update['beforeSHA256']
            original=read(oldcat);expected=copy.deepcopy(original)
            owner=next(m for m in expected['models'] if m['uid']==update['ownerUid'])
            assert owner==update['beforeEntry'];owner['supportDependencies']=update['afterEntry']['supportDependencies']
            assert owner==update['afterEntry'] and read(p)==expected
            refs.append(oldcat)
        else:
            assert digest(p.read_bytes())==sha
            original=read(p)
        old_models.extend(original['models']);refs.append(p)
        for model in original['models']:
            asset=p.parent/model['asset'];assert digest(asset.read_bytes())==model['sha256'];refs.append(asset)
    assert len(old_models)==len({m['uid'] for m in old_models})==7101
    models=[m for url in after['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']]
    assert len(models)==len({m['uid'] for m in models})==7106
    expected=copy.deepcopy(old_models)
    next(m for m in expected if m['uid']==update['ownerUid'])['supportDependencies']=update['afterEntry']['supportDependencies']
    assert {m['uid']:m for m in models if m['uid']not in sources}=={m['uid']:m for m in expected}
    new=[m for m in models if m['uid']in sources]
    originals={r['uid']:r['candidate']['entry'] for r in read(BASE/RUNTIME/'selection.json.gz')['rows']}
    assert verify_metadata(new,sources,source_review['supportByUid'],originals,GROUND)
    for model in new:
        assert all(model[k] is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
    plan=read(STAGE/'plan.json');terrain=plan['topLevelTerrainPatches'];assert len(terrain)==2
    assert after['officialModelCatalogues']==before['officialModelCatalogues']+[plan['areas'][0]['destination']]
    assert {k:v for k,v in before.items() if k not in ['officialModelCatalogues','terrainPatches']}=={k:v for k,v in after.items() if k not in ['officialModelCatalogues','terrainPatches']}
    replaced=[t for t in terrain if 'replaces'in t];assert len(replaced)==1
    replacement=replaced[0]['replaces'];destinations={t['destination'] for t in terrain}
    assert len(after['terrainPatches'])==len(before['terrainPatches'])+1
    assert not any(p['url']==replacement['url'] for p in after['terrainPatches'])
    assert [p for p in after['terrainPatches']if p['url']not in destinations]==[p for p in before['terrainPatches']if p['url']!=replacement['url']]
    old=ROOT/'3d-viewer'/replacement['url'];assert digest(old.read_bytes())==replacement['sha256'];refs.append(old)
    oldtargets=set(read(old)['meta']['targetUids'])
    for t in terrain:
        p=ROOT/'3d-viewer'/t['destination'];assert digest(p.read_bytes())==t['sha256'] and read(p)==read(ROOT/t['source'])
        assert set(read(p)['meta']['targetUids'])==(oldtargets|GROUND if'replaces'in t else GROUND)
        refs.append(p)
    previous=read(BASE/PREVIOUS);counts=read(installed/'full-xl-current-count.json')
    assert verify_fixed_cohort(previous,counts,sources)
    assert counts['counts']==receipt['fullXLCurrentCounts']
    inspection=read(installed/'ROOT-LIVE-EXPORT-INSPECTION.json')
    assert inspection['reviewer']=='ROOT' and inspection['visualAcceptance'] and inspection['allDeclaredExportsActuallyInspected']
    inspected={r['path']:r['sha256'] for r in inspection['imagesActuallyViewed']+inspection['retainedImagesActuallyViewed']}
    assert len(inspected)==36
    retained=set(source_review['browserObservedRetainedUids']);assert len(retained)==4
    current={m['uid']:m for m in models};exports=[]
    for width in [390,1280]:
        folder=installed/('viewport-'+str(width));report=read(folder/'live-browser.json')
        assert report['passed'] and not report['errors']
        own=[v for v in report['views'] if'time'in v];other=report['retainedNativeOwnViews']
        assert len(own)==10 and {(v['uid'],v['time']) for v in own}=={(u,t) for u in sources for t in ['15:00','22:00']}
        assert len(other)==8 and {(v['uid'],v['time']) for v in other}=={(u,t) for u in retained for t in ['15:00','22:00']}
        for v in own+other:
            assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces'] and v['sourceSHA256']==current[v['uid']]['sha256']
            p=folder/v['file'];key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[key]==inspected[key]
            refs.append(p);exports.append(dict(path=key,sha256=pins[key]))
        for v in own:assert v['pick']==v['collision']==v['uid'] and v['solidAppearance']
        for v in other:assert v['originalTriangles']==current[v['uid']]['triangles'] and all(v['meshVisibility']) and not any(v['wireframeFlags'])
    assert {r['path'] for r in exports}==set(inspected)
    atomic=receipt['atomicLifecycleReused'];assert digest((ROOT/atomic['path']).read_bytes())==atomic['sha256']
    proof=read(ROOT/atomic['path']);assert proof['passed'] and not proof['pageErrors'] and len(proof['cases'])==6
    assert {(c['width'],c['failedUid']) for c in proof['cases']}=={(1280,None)}|{(390,u) for u in sources}
    assert source_review['fullTerrainNativeActors']==1228 and source_review['unchangedNativeTerrainEvidenceCount']==1227
    support={};checker=module('silvercord_independent_global_basic_support_check',HERE.parent/'island-detail-integration/retained_basic_support.py')
    checker.stage_retained_basic_support(ROOT,after,{},support,read)
    assert len(support['retainedBasicSupportChecks'])==11
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==receipt['snapshotId']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid,sha in sources.items():
            assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(receipt['snapshotId'],uid)).fetchone()==('installed-verified',sha)
    result=dict(uids=sorted(sources),passed=True,installationIndependentlyVerified=True,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],
        fullXLCurrentCounts=counts['counts'],completeFixedXLRowsCompared=521,unmatchedUIDKeysRetained=2,onlyNewFixedXLUids=sorted(GROUND),
        completeCurrentCatalogueModels=7106,oldOriginalAssetsVerified=7101,allOldActorsPreservedExceptReviewedSupportDependencies=True,
        rootLiveExportsActuallyInspected=36,atomicLifecycle=atomic,retainedBasicSupportChecks=support['retainedBasicSupportChecks'],
        sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False)
    save(out/'ROOT-READBACK.json',result)
    refs += [old_path,manifest,pointer,BASE/PREVIOUS,installed/'ROOT-LIVE-EXPORT-INSPECTION.json',installed/'full-xl-current-count.json',STAGE/'plan.json',ROOT/atomic['path']]
    module('silvercord_complete_independent_installed_readback',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        OUT,'independent-whole-xl-original-assets-two-terrain-and-owner-installed-readback',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
