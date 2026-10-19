"""Stage unchanged original 147996 and reviewed full-parent native terrain; dry run only."""
import copy,shutil,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-lee-kong-pair-private-stage-v1-20261020';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
POD='landsd/72296:0'
FUNCTIONAL=BASE/'government-xl-lee-kong-pair-qualification-v1-20261020'
BROWSER=BASE/'government-xl-lee-kong-pair-browser-review-v1-20261020'
PHYSICAL=BASE/'government-xl-lee-kong-pair-loader-v1-20261020'
TERRAIN=PHYSICAL
NEIGHBOURS=BASE/'government-xl-lee-kong-pair-neighbours-v1-20261020'
PREVIOUS=HERE/'local/government-xl-lee-kong-pair-browser-desktop-v2-20261020'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def main():
    assert not DOC.exists()and not STAGE.exists();pins={};refs=[Path(__file__)]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for d in [FUNCTIONAL,BROWSER,PHYSICAL]:
            r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
            for e in r['evidenceRefs']:
                assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    qualification=read(FUNCTIONAL/'qualification.json');assert qualification['sourceScopedApplicabilityAccepted']and not qualification['remainingPhysicalReasons']
    sources={r['uid']:r['sourceSHA256']for r in qualification['sourceBindings']};assert len(sources)==2
    image_review=read(BROWSER/'ROOT-IMAGE-REVIEW.json');assert image_review['visualAcceptance']and image_review['reviewer']=='Codex ROOT'
    assert image_review['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
    assert len(image_review['imagesActuallyViewed'])==8
    for q in image_review['imagesActuallyViewed']:check(q)
    for q in image_review['browserReports']:
        check(q);report=read(ROOT/q['path']);assert report['passed']and not report['errors']
    terrain=read(PREVIOUS/'browser-config.json')['terrain'];assert len(terrain)==1
    candidate=read(TERRAIN/'terrain-candidates.json')[0];assert terrain[0]['source']==candidate['path'];terrain[0]['sha256']=candidate['sha256']
    assert qualification['terrainReplacement'] is True
    keys=['building:'+u for u in read(NEIGHBOURS/'summary.json')['requiredNativeUids']+list(sources)]+['terrain:'+candidate['replaces']['url'],'terrain:city/data/terrain.json']
    claim=reservations.claim('pacifica-private-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        DOC.mkdir();STAGE.mkdir();cat=read(PREVIOUS/'catalogue.json');original=copy.deepcopy(cat)
        for e in cat['models']:
            assert e['sha256']==sources[e['uid']]and e['proceduralWindows']is False
            e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,
                aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(FUNCTIONAL/'qualification.json'),
                placementReview='Unchanged original pair at fixed1x/native pose. All22034 faces pass four-coordinate foundation checks. Tower has72/72 strict contacts on the original podium. All80 basic neighbours and both retained native actors checked. Validated full-parent terrain replacement; loader, picking/collision and desktop/mobile review passed. No additional basic model suppression.')
            target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PREVIOUS/e['asset'],target);assert digest(target.read_bytes())==e['sha256']
        save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));shutil.copyfile(PREVIOUS/'source-forms.json',STAGE/'source-forms.json')
        raw_path=NEIGHBOURS/'native-neighbour-checks.json';native=read(raw_path)
        resolved=native['rows'];assert all(r['passed'] for r in resolved)
        fullcheck=DOC/'reviewed-native-neighbour-checks.json'
        save(fullcheck,dict(rows=resolved,rawReport=ref(raw_path),sourceReview=ref(FUNCTIONAL/'qualification.json'),aiCalls=0,modelGeometryChanges=0))
        patch=read(ROOT/candidate['path']);replacement=candidate['replaces'];assert set(replacement['retainedUids'])<={r['uid']for r in resolved}
        oldpatch=read(ROOT/'3d-viewer'/replacement['url']);oldtargets=oldpatch['meta']['targetUids'];assert set(oldtargets)<=set(replacement['retainedUids'])
        assert set(oldtargets)<=set(patch['meta']['targetUids'])
        native_review=DOC/'native-replacement-review.json'
        save(native_review,dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=candidate['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=oldtargets,fullAffectedNativeUids=replacement['retainedUids'],replacementTargetUids=patch['meta']['targetUids'],fullMeshCheck=ref(fullcheck),sourceReview=ref(FUNCTIONAL/'qualification.json')))
        terrain[0]['nativeReview']=ref(native_review)
        destination='city/data/official-models/'+BATCH+'/catalogue.json'
        save(STAGE/'plan.json',dict(areas=[dict(area='Lee Kong unchanged government podium and tower',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=terrain))
        for width in [390,1280]:
            cfg=read(PREVIOUS/'browser-config.json');cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/browser-'+str(width)+'/',catalogueURL=destination,terrain=terrain,viewportWidths=[width],failureTestUids=['landsd/253697:0']);save(STAGE/('browser-config-'+str(width)+'.json'),cfg)
        deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
        for p,h in deps['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
        pub=module('pacifica_private_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
        save(DOC/'qualification.json',dict(uids=sorted(sources),sourceSHA256ByUid=sources,sourceFunctionalApplicability=ref(FUNCTIONAL/'qualification.json'),visualReview=ref(BROWSER/'ROOT-IMAGE-REVIEW.json'),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),leaseResources=keys,privateStageQualified=True,publication=False,fullAcceptance=False))
        for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
        refs.extend(p for p in STAGE.rglob('*')if p.is_file())
        module('pacifica_private_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-sheung-shui-original-private-stage',list(dict.fromkeys(refs)),dict(uids=sorted(sources),privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False))
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
