"""Prepare five reviewed originals, two exact terrain descriptors and owner update.

Calls the canonical publisher in dry-run mode under the registered complete
terrain validators. No public writes, invented mesh rows or installed credit.
"""
import copy
import shutil
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from silvercord_lippo_five_original_physical_review_v1_20261103 import Evidence,BASE,GROUND
from silvercord_lippo_two_descriptor_terrain_dry_run_v2_20261103 import registered_two_descriptor_validators
from original_candidate_atomic_catalogue_contract_v1_20261103 import verify as tested_metadata
from dependency_preflight import from_catalogues,inspect_dependencies
from upton_staged_image_review_binding_v1_20261014 import inventory_delta

PREFIX='government-xl-silvercord-lippo-'
BATCH=PREFIX+'two-descriptor-qualified-stage-v1-20261103'
LOCAL=HERE/'local'/BATCH
STAGE=HERE/'accepted'/BATCH
SOURCE=PREFIX+'five-original-source-review-v1-20261103'
PHYSICAL=PREFIX+'five-original-physical-review-v1-20261103'
BROWSER=PREFIX+'private-six-part-browser-v4-20261103'
RUNTIME=PREFIX+'five-original-floor-runtime-v1-20261103'
PREVIOUS='government-xl-june-garden-original-installed-v4-20261103/full-xl-current-count.json'


def ref(path):
    return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))


def owned():
    lease=read(LOCAL/'reservation.json')
    assert reservations.owns(lease) and not (BASE/BATCH).exists() and not STAGE.exists()
    e=Evidence();e.refs=[Path(__file__),HERE/'silvercord_lippo_two_descriptor_terrain_dry_run_v2_20261103.py',
        HERE/'original_candidate_atomic_catalogue_contract_v1_20261103.py']
    review=e.take(SOURCE,'ROOT-SOURCE-REVIEW.json')
    assert review['status']=='approved-for-integration' and all(review[k] for k in [
        'identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
    source=review['sourceSHA256ByUid'];supports=review['supportByUid']
    physical=e.take(PHYSICAL,'ROOT-PHYSICAL-REVIEW.json')
    assert physical['sourceSHA256ByUid']==source and physical['fullTerrainForms']==5408 and physical['fullTerrainNativeActors']==1228
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json'
    manifest=e.file(manifest_path,review['currentManifest']['sha256'])
    pointer=e.file(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
    models=[m for url in manifest['officialModelCatalogues'] for m in e.file(ROOT/'3d-viewer'/url)['models']]
    assert len(models)==len({m['uid'] for m in models})==7101 and not set(source)&{m['uid'] for m in models}
    selection=e.take(RUNTIME,'selection.json.gz')
    originals={r['uid']:r['candidate']['entry'] for r in selection['rows']}
    previous=HERE/'local'/BROWSER
    e.take(BROWSER)
    cat=e.file(previous/'catalogue.json',e.pins[BROWSER][str((previous/'catalogue.json').relative_to(ROOT))])
    assert tested_metadata(cat['models'],source,supports,originals,GROUND)
    cfg=e.file(previous/'browser-config-390.json',e.pins[BROWSER][str((previous/'browser-config-390.json').relative_to(ROOT))])
    forms=e.file(previous/'validation-forms.json',e.pins[BROWSER][str((previous/'validation-forms.json').relative_to(ROOT))])
    assert len(cfg['terrain'])==2 and not cfg.get('estimatedBaseUpdates')
    qualified=copy.deepcopy(review)
    qualified.update(privateStageQualified=True,originalSourceReviewAccepted=True,sourceReview=ref(BASE/SOURCE/'ROOT-SOURCE-REVIEW.json'),
                     leaseResources=sorted(lease['resources']),publication=False)
    save(BASE/BATCH/'qualification.json',qualified)
    for m in cat['models']:
        m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,
                 sourceIdentityReview=ref(BASE/SOURCE/'ROOT-SOURCE-REVIEW.json'),
                 sourceFunctionalApplicability=ref(BASE/BATCH/'qualification.json'),aiGeometryModelling=False,
                 sourceEvidenceInterpretationUsedAI=True,
                 placementReview='Exact unchanged original assembly; bounded source-specific lower-wall/skin and native-podium roles, complete current neighbours and retained terrain, desktop/mobile and per-peer owner fallback/recovery reviewed. No AI geometry modelling.')
        asset=previous/m['asset'];e.pin(asset,m['sha256'])
        dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
    assert tested_metadata(cat['models'],source,supports,originals,GROUND)
    save(STAGE/'catalogue.json',cat)
    save(STAGE/'catalogue-index.json',dict(models=5,catalogues=['catalogue.json']))
    save(STAGE/'source-forms.json',forms)
    terrain=copy.deepcopy(cfg['terrain'])
    assert sum('replaces' in entry for entry in terrain)==1
    for i,entry in enumerate(terrain):
        node=e.file(ROOT/entry['source'],entry['sha256'])
        suffix='parent' if 'replaces' in entry else 'north'
        dest=STAGE/(suffix+'-terrain.json')
        shutil.copyfile(ROOT/entry['source'],dest)
        entry.update(source=str(dest.relative_to(ROOT)),destination='city/data/'+BATCH+'-'+suffix+'.json',area='Exact original Silvercord/Lippo floor return')
        assert not node.get('nativeMesh') if suffix=='parent' else bool(node.get('nativeMesh'))
        if suffix=='parent':
            old=e.file(ROOT/'3d-viewer'/entry['replaces']['url'],entry['replaces']['sha256'])
            assert set(node['meta']['targetUids'])==set(old['meta']['targetUids'])|GROUND
            assert len(node['meta']['targetUids'])==31 and len(old['meta']['targetUids'])==29
        else:
            assert set(node['meta']['targetUids'])==GROUND
    update=review['installedSupportUpdate']
    current_path=ROOT/'3d-viewer'/update['url']
    e.file(current_path,update['beforeSHA256'])
    from silvercord_lippo_private_six_part_browser_v4_20261103 import exact_owner_after
    assert exact_owner_after(read(current_path),e.file(ROOT/update['source'],update['sha256']),update)
    contact=BASE/'government-xl-lippo-current-native-podium-migration-probe-v1-20261103/summary.json'
    e.take(contact.parent.name)
    dependency=BASE/BATCH/'installed-support-dependency-review.json'
    save(dependency,dict(contactReport=str(contact.relative_to(ROOT)),contactReportSHA256=ref(contact)['sha256'],
        catalogues=[dict(source=str(current_path.relative_to(ROOT)),url=update['url'],oldSHA256=update['beforeSHA256'],models=[update['ownerUid']])],
        changes=[dict(catalogue=str(current_path.relative_to(ROOT)),uid=update['ownerUid'],modelSHA256=update['ownerSHA256'],
            modelId=update['beforeEntry']['modelId'],buildingCSUID=update['beforeEntry']['buildingCSUID'],
            oldSupportDependencies=update['beforeEntry']['supportDependencies'],supportDependencies=update['afterEntry']['supportDependencies'])],
        requiresNewNativeUids=sorted(d['uid'] for d in update['afterEntry']['supportDependencies'])))
    url='city/data/official-models/'+BATCH+'/catalogue.json'
    plan=dict(areas=[dict(area='Five unchanged Silvercord/Lippo originals',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],
              topLevelTerrainPatches=terrain,dependencyReviews=[dict(**ref(dependency),visualApproval=ref(BASE/SOURCE/'ROOT-SOURCE-REVIEW.json'))])
    save(STAGE/'plan.json',plan)
    cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=url,terrain=terrain)
    save(STAGE/'live-browser-config.json',cfg)
    deps=from_catalogues(manifest_path,[STAGE/'catalogue.json'])
    effective=[update['afterEntry'] if m['uid']==update['ownerUid'] else m for m in models]
    cleared=inspect_dependencies(effective,cat['models'])
    assert not any(r['blockers'] for r in cleared['rows'])
    save(BASE/BATCH/'dependencies.json',dict(**cleared,inputHashes=deps['inputHashes'],reviewedMigration=ref(dependency)))
    for path,sha in deps['inputHashes'].items():e.pin(ROOT/path,sha)
    prior=e.file(BASE/PREVIOUS)
    delta=inventory_delta(prior,cat['models'],manifest_sha=ref(manifest_path)['sha256'],snapshot=pointer['snapshotId'])
    assert delta['previousInstalled']==427 and delta['expectedFixedXLDelta']==2
    save(BASE/BATCH/'fixed-xl-delta.json',delta)
    pub=module('silvercord_two_descriptor_qualified_canonical_publisher',HERE.parent/'island-detail-integration/publish.py')
    pub.DOC=BASE/BATCH/'publisher-dry-run'
    argv=sys.argv[:]
    try:
        sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))]
        with registered_two_descriptor_validators(pub):pub.main()
    finally:
        sys.argv=argv
    report=read(pub.DOC/'publication-plan.json')
    assert report['published'] is False and len(report['topLevelTerrainPatches'])==2
    assert len(report['dependencyUpdates'])==1 and report['dependencyUpdates'][0]['uid']==update['ownerUid']
    e.finish();assert reservations.owns(lease)
    result=dict(uids=sorted(source),sourceSHA256ByUid=source,qualifiedForLiveVerification=True,
        canonicalFullPublisherDryRunPassed=True,newVisibleModels=5,expectedFixedXLDelta=2,
        newRuntimeCount=7106,terrainDescriptors=2,fullTerrainForms=5408,fullTerrainNativeActors=1228,
        rawFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,publication=False,installationApproved=False)
    save(BASE/BATCH/'summary.json',result)
    e.refs += [dependency,HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/model_dependencies.py',
               HERE/'fuying_five_member_terrain_stage_v1_20261029.py',HERE/'silvercord_lippo_registered_boundary_v1_20261103.py',
               *[p for p in STAGE.rglob('*') if p.is_file()]]
    module('silvercord_two_descriptor_qualified_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'qualified-five-original-two-descriptor-and-retained-owner-publication-plan',list(dict.fromkeys(e.refs)),result)


if __name__=='__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE/BATCH).exists() and not STAGE.exists()
        review=read(BASE/SOURCE/'ROOT-SOURCE-REVIEW.json')
        config=read(HERE/'local'/BROWSER/'browser-config-390.json')
        resources={'building:'+u for u in review['uids']+[review['installedSupportUpdate']['ownerUid']]}
        resources|={'terrain:city/data/terrain.json','immutable-source-proof:'+BATCH}
        for entry in config['terrain']:
            if 'replaces' in entry:
                resources.add('terrain:'+entry['replaces']['url'])
                parent=ROOT/'3d-viewer'/entry['replaces']['url']
                assert digest(parent.read_bytes())==entry['replaces']['sha256']
                resources.update('building:'+u for u in read(parent)['meta']['targetUids'])
        claim=reservations.claim('silvercord-two-descriptor-qualified-stage-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
