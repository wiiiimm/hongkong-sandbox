"""Prepare four reviewed immutable originals and exact retained terrain; dry run.

Separate positive contract for supported atomic co-imports. Independent-source
and installed-parent installers keep their existing, narrower requirements.
"""
import shutil,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_coordinated_retained_contract_v1_20261027 import verify_metadata,verify_retained_entries,verify_native_interfaces
from original_nested_coordinated_publisher_v1_20261027 import publisher
from dependency_preflight import from_catalogues
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import'
CONFIGPATH=BASE/'government-xl-ocean-coordinated-original-install-config-v1-20261027.json'
CONFIG=read(CONFIGPATH);SOURCES=CONFIG['sources']
BATCH=CONFIG['prefix']+'-qualified-stage-v1-'+CONFIG['date'];DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
SOURCE=BASE/CONFIG['review'];PREVIOUS=HERE/'local'/CONFIG['browser']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
    assert not DOC.exists() and not STAGE.exists();refs=[Path(__file__),CONFIGPATH];pins={}
    def take(name,path):
        if name not in pins:
            pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    review=take(CONFIG['review'],SOURCE/'ROOT-SOURCE-REVIEW.json')
    assert all(review[k] for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance','qualifiedForLiveVerification'])
    assert not review['installationApproved'] and not review['publication'] and review['sourceSHA256ByUid']==SOURCES
    manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert ref(manifest)==review['currentManifest'] and read(pointer)['snapshotId']==CONFIG['previousSnapshotId'];refs.extend([manifest,pointer])
    current={}
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path)
        for m in read(path)['models']:assert m['uid'] not in current;current[m['uid']]=m
    assert verify_retained_entries(current,review['retainedNativeEntries'],SOURCES,CONFIG['currentNativeActors'])
    scope=take(CONFIG['modelScope'],BASE/CONFIG['modelScope']/'summary.json')
    contacts=take(CONFIG['nativeContacts'],BASE/CONFIG['nativeContacts']/'summary.json')
    assert verify_native_interfaces(review,scope,contacts,current,SOURCES)
    selection=take(CONFIG['runtime'],BASE/CONFIG['runtime']/'selection.json.gz')
    original={r['uid']:r['candidate']['entry'] for r in selection['rows']}
    cat=take(CONFIG['browser'],PREVIOUS/'catalogue.json');forms=take(CONFIG['browser'],PREVIOUS/'source-forms.json')
    assert verify_metadata(cat['models'],SOURCES,CONFIG['supportByUid'],original,CONFIG['groundOwnerUids'])
    cfg=take(CONFIG['browser'],PREVIOUS/'browser-config-390.json');assert len(cfg['terrain'])==1 and cfg['catalogueReplacements']==[] and cfg['failureTestUids']==[]
    obligations=take(CONFIG['scope'],BASE/CONFIG['scope']/'form-obligations.json.gz');assert len(obligations)==CONFIG['neighbourForms']
    patch=take(CONFIG['patch'],BASE/CONFIG['patch']/'summary.json');replaced=patch['replacedNativeTerrain'][0]
    replacement={k:replaced[k] for k in ['url','sha256','retainedUids']}
    assert cfg['terrain'][0]['replaces']==replacement
    terrain=ROOT/patch['candidate']['path'];old=ROOT/'3d-viewer'/replacement['url'];refs.extend([terrain,old])
    pub,retention=publisher('ocean_qualified_original_nested_dry_run',old,terrain,CONFIG['groundOwnerUids'],SOURCES,patch)
    qualification={**review,'privateStageQualified':True,'originalSourceReviewAccepted':True,'sourceReview':ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),'leaseResources':review['leaseResources'],'retention':retention,'publication':False}
    save(DOC/'qualification.json',qualification)
    for model in cat['models']:
        model.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview=CONFIG['placementReview'])
        asset=PREVIOUS/model['asset'];assert digest(asset.read_bytes())==SOURCES[model['uid']];refs.append(asset)
        dest=STAGE/model['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
    assert verify_metadata(cat['models'],SOURCES,CONFIG['supportByUid'],original,CONFIG['groundOwnerUids'])
    save(STAGE/'catalogue.json',cat);save(STAGE/'source-forms.json',forms);save(STAGE/'catalogue-index.json',dict(models=len(SOURCES),catalogues=['catalogue.json']))
    terrain_copy=STAGE/'original-terrain.json';shutil.copyfile(terrain,terrain_copy)
    assert ref(terrain_copy)['sha256']==patch['candidate']['sha256']
    regression=review['retainedNativeRegression'];assert set(regression['requiredNativeUids'])==set(CONFIG['retainedNativeUids'])==set(regression['nativeResolved'])
    rows=regression['nativeRows'];assert len(rows)==27 and all(r['passed'] and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in rows)
    meshcheck=DOC/'native-neighbour-checks.json';save(meshcheck,dict(rows=rows,aiCalls=0,modelGeometryChanges=0,physicalReview=ref(BASE/CONFIG['physical']/'ROOT-PHYSICAL-REVIEW.json')))
    native_review=DOC/'native-replacement-review.json'
    save(native_review,dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=ref(terrain_copy)['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=replacement['retainedUids'],replacementTargetUids=read(terrain_copy)['meta']['targetUids'],fullMeshCheck=ref(meshcheck),retention=retention))
    entry=dict(source=str(terrain_copy.relative_to(ROOT)),destination=CONFIG['terrainDestination'],sha256=ref(terrain_copy)['sha256'],resolution=read(terrain_copy)['cell'],area=CONFIG['label'],replaces=replacement,nativeReview=ref(native_review))
    destination='city/data/official-models/'+BATCH+'/catalogue.json'
    save(STAGE/'plan.json',dict(areas=[dict(area=CONFIG['label'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[entry]))
    cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[entry])
    cfg['retainedCaptureDirectionByModel']=cfg.get('retainedCaptureDirectionByModel',{})
    from ocean_retained_camera_supplement_v1_20261027 import UIDS
    cfg['retainedCaptureDirectionByModel'].update({u:[0,1,.01] for u in UIDS});save(STAGE/'live-browser-config.json',cfg)
    dependencies=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers'] for r in dependencies['rows']);save(DOC/'dependencies.json',dependencies)
    for path,sha in dependencies['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    previous=BASE/CONFIG['previousCountReport'];refs.append(previous)
    delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId'])
    assert delta['previousInstalled']==CONFIG['previousInstalled'] and delta['expectedFixedXLDelta']==CONFIG['expectedFixedXLDelta'];save(DOC/'fixed-xl-delta.json',delta)
    pub.DOC=DOC/'publisher-dry-run';oldargv=sys.argv[:]
    try:sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main()
    finally:sys.argv=oldargv
    assert read(pub.DOC/'publication-plan.json')['published'] is False and ref(manifest)==review['currentManifest']
    refs.extend([HERE/'original_coordinated_retained_contract_v1_20261027.py',HERE/'original_nested_coordinated_publisher_v1_20261027.py',HERE.parent/'island-detail-integration/publish.py'])
    for group in pins.values():
        for path,sha in group.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    refs.extend(p for p in STAGE.rglob('*') if p.is_file())
    module('ocean_coordinated_qualified_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-supported-atomic-original-retained-terrain-plan-v1',list(dict.fromkeys(refs)),dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,qualifiedForLiveVerification=True,delta=delta,newVisibleModels=len(SOURCES),newRuntimeCount=CONFIG['currentNativeActors']+len(SOURCES),publication=False))

if __name__=='__main__':main()
