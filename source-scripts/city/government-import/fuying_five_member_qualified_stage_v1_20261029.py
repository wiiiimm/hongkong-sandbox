"""Prepare one reviewed original and its complete five-member replacement; no apply."""
from pathlib import Path
import copy,shutil,sys
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
from fuying_five_member_terrain_stage_v1_20261029 import publication_adapter,OLD_URL
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-fuying181489-'
BATCH=PREFIX+'five-member-qualified-stage-v1-20261029';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
BROWSER=PREFIX+'five-member-private-browser-v1-20261029';REVIEW=PREFIX+'source-physical-visual-review-v1-20261029'
PREVIOUS=HERE/'local'/BROWSER
SOURCES={'landsd/181489:0':'bffdf5653f4dd01917b4028e0cd2f0559fcdb3ce960a4d7cabd5a0392b9ae163'}
PUBLIC_FIELDS=['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__)];cache={}
    def take(batch,p):
        if batch not in cache:cache[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert ref(p)['sha256']==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    reviewpath=BASE/REVIEW/'ROOT-SOURCE-PHYSICAL-VISUAL-REVIEW.json';review=take(REVIEW,reviewpath)
    assert all(review[k]for k in ['identityAccepted','physicalAcceptance','visualAcceptance','qualifiedForGuardedStaging','completeNeighbourInterpretationAccepted'])and review['sourceSHA256ByUid']==SOURCES
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==review['currentManifest'];refs.append(manifest)
    current=[m for u in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/u)['models']];assert len(current)==len({m['uid']for m in current})==7021 and not set(SOURCES)&{m['uid']for m in current}
    cat=take(BROWSER,PREVIOUS/'catalogue.json');cfg=take(BROWSER,PREVIOUS/'browser-config-390.json');forms=take(BROWSER,PREVIOUS/'validation-forms.json')
    assert {m['uid']:m['sha256']for m in cat['models']}==SOURCES and len(cfg['terrain'])==5
    scope=PREFIX+'five-member-full-scope-v1-20261029';obligations=take(scope,BASE/scope/'form-obligations.json.gz');s=take(scope,BASE/scope/'scope.json');assert len(obligations)==40 and len(s['touchingNativeUids'])==9
    resources=sorted({'building:'+f['uid']if f['uid'].startswith('landsd/')else'source-form:'+f['uid']for f in obligations}|{'building:'+u for u in s['touchingNativeUids']}|{'building:landsd/181489:0','terrain:city/data/terrain.json','terrain:'+OLD_URL,'server:127.0.0.1:4177'})
    qualification={**review,'privateStageQualified':True,'originalSourceReviewAccepted':True,'leaseResources':resources,'sourceReview':ref(reviewpath),'publication':False}
    save(DOC/'qualification.json',qualification)
    for m in cat['models']:
        assert m['proceduralWindows']is False and m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0
        assert not any(m.get(k)for k in ['supportDependencies','retainedBasicSupportDependencies','suppressesBuildingUids'])
        assert all(m[k]is False for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
        m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(reviewpath),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview='Exact unchanged government Fu Ying original at1x/sourcepose; complete source-role/contact/four-world foundations/neighbours and reviewed private desktop/mobile views. Low authored canopies retained; exact whole-parent five-member terrain replacement required. No geometry edits, invented window skin, suppression or support dependency. Live and installed verification remain mandatory.')
        asset=PREVIOUS/m['asset'];assert ref(asset)['sha256']==m['sha256'];refs.append(asset);dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
    save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',forms)
    drybatch=PREFIX+'five-member-terrain-publisher-dry-run-v4-20261029';dry=take(drybatch,BASE/drybatch/'summary.json');assert dry['terrainGroupDryRunPassed']and dry['globalRetainedBasicSupportCheckExecuted']
    previousplan=take(drybatch,BASE/drybatch/'terrain-only-plan.json');terrain=previousplan['topLevelTerrainPatches']
    destination='city/data/official-models/'+BATCH+'/catalogue.json'
    plan={**previousplan,'areas':[dict(area='Fu Ying House unchanged original',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)]};save(STAGE/'plan.json',plan)
    # Real live mode must consume installed terrain, not silently substitute it.
    cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=destination,terrain=terrain);save(STAGE/'live-browser-config.json',cfg)
    deps=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
    for p,h in deps['inputHashes'].items():assert ref(ROOT/p)['sha256']==h;refs.append(ROOT/p)
    previous=BASE/'government-xl-peninsula-exact-original-pair-original-installed-v3-20261029/full-xl-current-count.json';refs.append(previous)
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';refs.append(pointer)
    delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==405 and delta['expectedFixedXLDelta']==1;save(DOC/'fixed-xl-delta.json',delta)
    pub=module('fuying_five_group_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run'
    with publication_adapter(pub):
        sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main()
    assert not read(pub.DOC/'publication-plan.json')['published']
    refs.extend(pub.PINNED_INPUTS);refs.extend([HERE/'fuying_five_member_terrain_stage_v1_20261029.py',HERE/'fuying_whole_parent_five_boundary_v1_20261029.py',HERE.parent/'island-detail-integration/publish.py']);refs.extend(p for p in STAGE.rglob('*')if p.is_file())
    module('fuying_five_qualified_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-unchanged-original-and-five-member-whole-parent-installation-plan',list(dict.fromkeys(refs)),dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,qualifiedForLiveVerification=True,newRuntimeCount=7022,delta=delta,publication=False,installationApproved=False))
if __name__=='__main__':main()
