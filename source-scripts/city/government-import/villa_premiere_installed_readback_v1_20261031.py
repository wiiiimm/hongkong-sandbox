"""Independent whole-map audit after the stable Villa Premiere recovery install."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from publication_lock import locked_publication
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-villa-premiere89917-';INSTALL=P+'five-original-installed-v3-20261031';BATCH=P+'installed-whole-map-readback-v1-20261031'

def main():
    out=BASE/BATCH;assert not out.exists();folder=BASE/INSTALL;assert not(folder/'failure-recovery.json').exists();final=read(folder/'result.json');history=read(folder/'historical-input-context.json');refs=[Path(__file__),folder/'result.json',folder/'historical-input-context.json'];aliases={};checked={};reports=[]
    for r in history['mutableCurrentByteSnapshots']:
        b=r['savedHistoricalBytes'];p=ROOT/b['path'];assert digest(p.read_bytes())==b['sha256']==r['originalSHA256'];aliases[r['originalPath'],r['originalSHA256']]=p;refs.append(p)
    phases=[P+'qualified-stage-v3-20261031',P+'qualified-stage-lifecycle-v1-20261031',P+'original-qualification-v2-20261031',P+'numerical-ground-context-v1-20261031',P+'ramp-support-checkpoint-v1-20261031',P+'post-status-rollback-readback-v1-20261031',P+'distinct-retry-baseline-v1-20261031']
    with locked_publication(ROOT),connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for batch in [INSTALL,*phases]:
            path=BASE/batch/'result.json';receipt=read(path);refs.append(path);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);reports.append(dict(batch=batch,jobId=receipt['jobId']))
            for b in receipt['evidenceRefs']:
                key=b['path'],b['sha256']
                if key not in checked:
                    p=aliases.get(key,ROOT/b['path']);assert digest(p.read_bytes())==b['sha256'],b['path'];checked[key]=dict(**b,resolvedBytes=str(p.relative_to(ROOT)));refs.append(p)
        sources=final['sourceSHA256ByUid'];assert len(sources)==5
        for uid,sha in sources.items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(final['snapshotId'],uid)).fetchone()==('installed-verified',sha)
        pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==final['snapshotId'];refs.append(pointer)
        from installation_snapshot_identity_v1_20261031 import identity as snapshot_identity
        acceptance=read(folder/'acceptance.json');inventory=ROOT/read(pointer)['inventory'];assert acceptance['transactionBatch']==INSTALL and snapshot_identity(read(inventory)['parts'],acceptance,INSTALL)==final['snapshotId']!='5507c154c3cc2416';refs.extend([inventory,HERE/'installation_snapshot_identity_v1_20261031.py',HERE/'safe_status_output_v1_20261031.py',HERE/'villa_premiere_distinct_retry_baseline_v1_20261031.py'])
        manifest=ROOT/final['manifest']['path'];assert digest(manifest.read_bytes())==final['manifest']['sha256'];after=read(manifest);refs.append(manifest)
        oldbinding=next(r for r in history['mutableCurrentByteSnapshots']if r['originalPath']==str(manifest.relative_to(ROOT)));before=read(ROOT/oldbinding['savedHistoricalBytes']['path'])
        models=[];oldmodels=[];asset_count=0
        for url in before['officialModelCatalogues']:oldmodels.extend(read(ROOT/'3d-viewer'/url)['models'])
        for url in after['officialModelCatalogues']:
            catpath=ROOT/'3d-viewer'/url;cat=read(catpath);models.extend(cat['models']);refs.append(catpath)
            for m in cat['models']:
                p=catpath.parent/m['asset'];assert digest(p.read_bytes())==m['sha256'];asset_count+=1
        assert len(models)==len({m['uid']for m in models})==asset_count==7035 and len(oldmodels)==7030 and models[:7030]==oldmodels
        new=models[7030:];assert {m['uid']:m['sha256']for m in new}==sources
        for m in new:
            assert all(m[k]is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])and m['proceduralWindows']is False
            assert m['activationGroup']==sorted(sources)and m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0 and not m.get('suppressesBuildingUids')
        support=module('villa_independent_original_support_graph',HERE/'original_supported_catalogue_scope_v1_20261024.py');assert support.verify(new,sources,{u:'landsd/89917:0'for u in sources if u!='landsd/89917:0'})
        assert after['counts']==before['counts']and len(after['terrainPatches'])==len(before['terrainPatches'])+1 and after['terrainPatches'][:-1]==before['terrainPatches']
        terrain=after['terrainPatches'][-1];assert terrain['url']=='city/data/government-native-villa-premiere-five-original-v1-20261031.json';assert digest((ROOT/'3d-viewer'/terrain['url']).read_bytes())=='3696f6d45c55904d531e9ba849cbaff42b928eb050a35c9eedfea30a53fbef9b'
        tile='3d-viewer/city/data/tiles/-7_-9.json';oldtile=read(ROOT/next(r for r in history['mutableCurrentByteSnapshots']if r['originalPath']==tile)['savedHistoricalBytes']['path']);newtile=read(ROOT/tile);expected=read(ROOT/next(r for r in history['mutableCurrentByteSnapshots']if r['originalPath']==tile)['savedHistoricalBytes']['path'])
        b=next(b for b in expected['buildings']if b['uid']=='landsd/325786:0');b.update(foundationBase=4.590000152587891,foundationPolicy='terrain-derived-illustrative-posts');assert newtile==expected;refs.append(ROOT/tile)
        target_url=tile.removeprefix('3d-viewer/');assert [{k:v for k,v in t.items()if k!='bytes'}for t in after['tiles']]==[{k:v for k,v in t.items()if k!='bytes'}for t in before['tiles']]
        assert [t for t in after['tiles']if t['url']!=target_url]==[t for t in before['tiles']if t['url']!=target_url]
        support_report={};guard=module('villa_whole_map_basic_support_guard',HERE.parent/'island-detail-integration/retained_basic_support.py');guard.stage_retained_basic_support(ROOT,after,{},support_report,read);assert len(support_report['retainedBasicSupportChecks'])==8
        counts=read(folder/'full-xl-current-count.json');assert counts['counts']==final['fullXLCurrentCounts']==dict(total=521,installedVerified=411,remaining=110)
        previous=BASE/'government-xl-disneyland-eastern75643-independent-apron-original-installed-v10-20261030/full-xl-current-count.json';oldrows={r['sourceKey']:r for r in read(previous)['rows']};newrows={r['sourceKey']:r for r in counts['rows']};assert len(oldrows)==len(newrows)==521 and set(oldrows)==set(newrows)
        assert [r['uid']for k,r in newrows.items()if r!=oldrows[k]]==['landsd/89917:0'];assert sum(r['uid']is None for r in newrows.values())==2;refs.extend([previous,folder/'full-xl-current-count.json'])
        live=read(folder/'live-http/report.json');visual=read(folder/'ROOT-LIVE-EXPORT-OBSERVATIONS.json');assert live['passed']and live['liveInstalledHTTP']and not live['catalogueAndTerrainSubstitution']and not live['pageErrors']and len(live['cases'])==6
        assert {(r['width'],r['failedUid'])for r in live['cases']}=={(1280,None)}|{(390,u)for u in sources}
        for row in live['cases']:
            assert row['completeGroupEvicted']and row['baseOnlyRestoredCompleteGroup']and not row['audit']['violations']and row['uiFreeCanvasExport'];assert {r['uid']:r['sha256']for r in row['sources']}==sources
            if row['failedUid']:assert row['failureKeptAllBasics']
            assert len(row['retainedCanopyLifecycle'])==(5 if row['failedUid']else 4)
        assert visual['liveExportsAccepted']and len(visual['imagesActuallyInspected'])==6
        for b in [visual['browserReport'],*visual['imagesActuallyInspected']]:assert digest((ROOT/b['path']).read_bytes())==b['sha256'];refs.append(ROOT/b['path'])
        result=dict(uids=sorted(sources),passed=True,installationIndependentlyVerified=True,sourceSHA256ByUid=sources,installedJobId=final['jobId'],snapshotId=final['snapshotId'],allInstalledAssetsRehashed=asset_count,oldCatalogueEntriesPreserved=7030,completeFixedXLRowsCompared=521,bothNullUIDKeysPreserved=True,retainedBasicSupportChecks=support_report,allOtherTileFormsAndRecordedSourceFieldsUnchanged=True,oldTerrainEntriesUnchanged=True,exactNewTerrainSHA256='3696f6d45c55904d531e9ba849cbaff42b928eb050a35c9eedfea30a53fbef9b',currentManifest=final['manifest'],fullXLCurrentCounts=counts['counts'],completedReports=reports,distinctVerifiedReferences=len(checked),newInstallationCredit=0,sourceGeometryChanges=0,qualification='Independent read-only audit of the stable V3 recovery, complete current7035asset hashes/7030oldcatalogueentries, all521sourcekeys/twoNULLs, exactone-canopy metadata delta/one terrain addition, eight retained BASIC supports, current activeNeon snapshot and6actualHTTP atomic cases/ROOT6exports. HistoricalV1post-statusrollback remains separate; no duplicate installation credit.')
        save(out/'summary.json',result);save(out/'verified-references.json',list(checked.values()))
    refs.extend([HERE/'original_supported_catalogue_scope_v1_20261024.py',HERE.parent/'island-detail-integration/retained_basic_support.py'])
    module('villa_whole_map_installed_readback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'stable-five-original-whole-map-assets-ledger-xl-support-readback',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
