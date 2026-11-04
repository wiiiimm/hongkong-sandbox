"""Stage the reviewed immutable five-source Pacifica assembly; dry run only."""
import copy,shutil,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-pacifica-private-stage-v1-20261019';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
POD='landsd/283036:0'
FUNCTIONAL=BASE/'government-xl-pacifica-functional-applicability-v1-20261019'
BROWSER=BASE/'government-xl-pacifica-browser-review-v2-20261019'
PHYSICAL=BASE/'government-xl-pacifica-ordinary-validation-v2-20261019'
OWNERSHIP=BASE/'government-xl-pacifica-terrain-ownership-v1-20261019'
PREVIOUS=HERE/'local/government-xl-pacifica-assembly-browser-desktop-v5-20261019'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def main():
    assert not DOC.exists()and not STAGE.exists();pins={};refs=[Path(__file__)]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for d in [FUNCTIONAL,BROWSER,PHYSICAL,OWNERSHIP]:
            r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
            for e in r['evidenceRefs']:
                assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    qualification=read(FUNCTIONAL/'qualification.json');assert qualification['sourceScopedApplicabilityAccepted']and not qualification['remainingPhysicalReasons']
    sources={r['uid']:r['sourceSHA256']for r in qualification['sourceBindings']};assert len(sources)==5
    image_review=read(BROWSER/'ROOT-IMAGE-REVIEW.json');assert image_review['visualAcceptance']and image_review['reviewer']=='Codex ROOT'
    assert image_review['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
    report=read(BROWSER/'staged-browser.json');assert report['passed']and not report['errors']
    views=[v for v in report['views']if 'time'in v];assert len(views)==20 and len(report['jointViews'])==10
    assert len(image_review['imagesActuallyViewed'])==28
    for q in image_review['imagesActuallyViewed']:check(q)
    assert image_review['sourceCatalogue']==ref(PREVIOUS/'catalogue.json')
    candidate=read(OWNERSHIP/'terrain-candidates.json')[0];equivalence=read(OWNERSHIP/'metadata-equivalence.json')
    assert equivalence['completePayloadEqualAfterRemovingOnlyOwnershipAndEvidenceReference']and equivalence['renderedGeometryChanges']==0
    assert equivalence['replacementTerrain']==dict(path=candidate['path'],sha256=candidate['sha256'])
    actors={r['uid']for r in read(PHYSICAL/'neighbour-checks.json')['rows']}|set(sources)|{'landsd/265478:0','landsd/283034:0'}
    keys=sorted({('basic-building:'if prefix=='building:'and not uid.startswith('landsd/')else prefix)+uid for prefix in ['building:','terrain-patch:']for uid in actors})
    claim=reservations.claim('pacifica-private-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        DOC.mkdir();STAGE.mkdir();cat=read(PREVIOUS/'catalogue.json');original=copy.deepcopy(cat)
        for e in cat['models']:
            assert e['sha256']==sources[e['uid']]and e['proceduralWindows']is False
            e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,
                aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(FUNCTIONAL/'qualification.json'),
                placementReview='Unchanged original at 1x/source pose. Complete terrain, neighbours, loader/picking/collision and desktop/mobile checks verified. Exact original facade/trim applicability preserves raw Tower1/3 contact and Tower3 compound-foundation failures; no numeric tolerance changed.')
            target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PREVIOUS/e['asset'],target);assert digest(target.read_bytes())==e['sha256']
        save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=5,catalogues=['catalogue.json']));shutil.copyfile(PREVIOUS/'source-forms.json',STAGE/'source-forms.json')
        patch=read(ROOT/candidate['path']);out=STAGE/'government-native-pacifica-original-v1-20261019.json';shutil.copyfile(ROOT/candidate['path'],out);assert digest(out.read_bytes())==candidate['sha256']
        nativepath=PHYSICAL/'native-neighbour-checks.json';native=read(nativepath)
        assert not set(native['blocked'])-set(native['resolved'])
        assert all(next(r['passed']for r in native['rows']if r['uid']==u)for u in ['landsd/265478:0','landsd/283034:0'])
        save(DOC/'native-replacement-review.json',dict(status='approved-for-integration',supersededURL=candidate['replaces']['url'],supersededSHA256=candidate['replaces']['sha256'],replacementSHA256=candidate['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=['landsd/265478:0'],replacementTargetUids=patch['meta']['targetUids'],fullMeshCheck=ref(nativepath),metadataEquivalence=ref(OWNERSHIP/'metadata-equivalence.json')))
        terrain=dict(source=str(out.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+out.name,resolution=patch['cell'],area='Pacifica original-source terrain',replaces={**candidate['replaces'],'retainedUids':['landsd/265478:0']},nativeReview=ref(DOC/'native-replacement-review.json'))
        destination='city/data/official-models/'+BATCH+'/catalogue.json'
        save(STAGE/'plan.json',dict(areas=[dict(area='Pacifica Mall and four unchanged original towers',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[terrain]))
        for width in [390,1280]:
            cfg=read(PREVIOUS/'browser-config.json');cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/browser-'+str(width)+'/',catalogueURL=destination,terrain=[terrain],viewportWidths=[width]);save(STAGE/('browser-config-'+str(width)+'.json'),cfg)
        deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
        for p,h in deps['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
        pub=module('pacifica_private_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
        save(DOC/'qualification.json',dict(uids=sorted(sources),sourceSHA256ByUid=sources,sourceFunctionalApplicability=ref(FUNCTIONAL/'qualification.json'),visualReview=ref(BROWSER/'ROOT-IMAGE-REVIEW.json'),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),leaseResources=keys,metadataEquivalence=ref(OWNERSHIP/'metadata-equivalence.json'),privateStageQualified=True,publication=False,fullAcceptance=False))
        for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
        refs.extend(p for p in STAGE.rglob('*')if p.is_file())
        module('pacifica_private_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-five-original-private-stage',list(dict.fromkeys(refs)),dict(uids=sorted(sources),privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False))
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
