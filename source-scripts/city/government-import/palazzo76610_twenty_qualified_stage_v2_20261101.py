"""Run the complete canonical publisher dry run for twenty unchanged originals."""
import argparse,copy,shutil,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
from original_supported_catalogue_scope_v1_20261024 import verify
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'twenty-qualified-stage-v2-20261101';TERRAIN='city/data/government-native-palazzo-twenty-original-v1-20261101.json'

def main():
    from north_pair_nonwall_topology_v1_20261027 import execute_reserved
    from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators as private_validator
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');args=ap.parse_args()
    lp=HERE/'local'/BATCH/'reservation.json'
    if not args.owned:
        assert not lp.parent.exists()
        resources=read(BASE/(P+'twenty-original-qualification-v2-20261101')/'ROOT-PHYSICAL-REVIEW.json')['leaseResources']
        claim=reservations.claim('villa-qualified-stage-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    assert reservations.owns(read(lp))
    out=BASE/BATCH;stage=HERE/'accepted'/BATCH;assert not out.exists()and not stage.exists();pins={};refs=[Path(__file__)]
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    def take(batch,p):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    qual=P+'twenty-original-qualification-v2-20261101';qp=BASE/qual/'ROOT-SOURCE-REVIEW.json';q=take(qual,qp)
    assert all(q[k]for k in ['qualifiedForLiveVerification','identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance','completeFourWorldFoundations'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==q['currentManifest'];refs.append(manifest);sources=q['sourceSHA256ByUid']
    oldbatch=P+'twenty-private-preview-v1-20261101';oldroot=HERE/'local'/oldbatch;oldstage=oldroot/'atomic';cat=take(oldbatch,oldstage/'catalogue.json');cfg=take(oldbatch,oldroot/'atomic-config.json');forms=take(oldbatch,oldstage/'source-forms.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources
    current=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(current)==7041 and not set(sources)&{m['uid']for m in current};assert verify(cat['models'],sources,q['supportByUid'])
    for m in cat['models']:
        assert m['activationGroup']==sorted(sources)and m['proceduralWindows']is False and m.get('verticalPlacementOffsetHKPD',0)==0 and not m.get('suppressesBuildingUids')
        assert all(m[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
        m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(qp),sourceFunctionalApplicability=ref(qp),placementReview=BATCH,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True)
        asset=oldstage/m['asset'];assert ref(asset)['sha256']==m['sha256'];refs.append(asset);dest=stage/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
    save(stage/'catalogue.json',cat);save(stage/'source-forms.json',forms);save(stage/'catalogue-index.json',dict(models=20,catalogues=['catalogue.json']))
    patch=P+'terrain-provenance-repair-v1-20261101';terrain=take(patch,BASE/patch/'summary.json');assert terrain['identicalRendererPayloadExcludingProofAnnotation']and terrain['fullCanonicalPatchValidatorPassed']and q['terrainCandidate']==terrain['candidate'];asset=ROOT/terrain['candidate']['path'];assert ref(asset)==terrain['candidate'];refs.append(asset)
    destination='city/data/official-models/'+BATCH+'/catalogue.json';plan=dict(areas=[dict(area='Twenty unchanged government source parts: Palazzo and neighbouring units',catalogue=str((stage/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[dict(source=str(asset.relative_to(ROOT)),destination=TERRAIN,sha256=terrain['candidate']['sha256'],resolution=read(asset)['cell'],area='Palazzo area original source-derived ground')]);save(stage/'plan.json',plan)
    deps=from_catalogues(manifest,[stage/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(out/'dependencies.json',deps)
    for p,h in deps['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    previous=BASE/'government-xl-prosperous235568-six-original-installed-v1-20261031/full-xl-current-count.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';refs.extend([previous,pointer]);delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==412 and delta['expectedFixedXLDelta']==1;save(out/'fixed-xl-delta.json',delta)
    pub=module('villa_premiere_complete_guarded_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=out/'publisher-dry-run';args=sys.argv[:]
    try:
        sys.argv=['publish.py',str((stage/'plan.json').relative_to(ROOT))]
        with private_validator():pub.main()
    finally:sys.argv=args
    report=read(pub.DOC/'publication-plan.json');assert not report['published']and not report.get('illustrativeFoundations') and len(report['topLevelTerrainPatches'])==1 and report['areas'][0]['models']==20
    assert ref(manifest)==q['currentManifest'];save(stage/'live-browser-config.json',dict(**{k:v for k,v in cfg.items()if k not in ['stage','catalogueURL','terrain']},stage=str(stage.relative_to(ROOT))+'/',catalogueURL=destination,terrain=plan['topLevelTerrainPatches']))
    refs.extend([HERE/'fuying_five_member_terrain_stage_v1_20261029.py',HERE/'fuying_whole_parent_five_boundary_v1_20261029.py',HERE/'three_member_native_boundary_v1_20261027.py',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/illustrative_foundations.py',*[p for p in stage.rglob('*')if p.is_file()]])
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifest=q['currentManifest'],leaseResources=q['leaseResources'],canonicalFullPublisherDryRunPassed=True,qualifiedForLiveVerification=True,qualifiedExactStage=True,publication=False,installationApproved=False,newVisibleModels=20,fixedXLDelta=delta,sourceGeometryChanges=0,sourcePoseChanges=0,qualifiedStageBrowserPending=True,qualification='Complete actual publisher dry run with exact immutable pre-annotation audit-source repair, existing old-actor/support guards intact, exact atomic20source metadata; no BASIC source-field or illustrative-foundation edits. No public/model/terrain/tile writes. Qualified-stage availability/HTTP verification and fenced live publication/readback remain required.')
    save(out/'summary.json',result);module('villa_qualified_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'twenty-original-qualified-full-publisher-dry-run',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
