"""Stage the reviewed immutable three-source Times Square assembly; dry run only."""
import copy,shutil,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-times-square-private-stage-v1-20261019';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
POD='landsd/233901:0'
FUNCTIONAL=BASE/'government-xl-times-square-functional-applicability-v1-20261019'
BROWSER=BASE/'government-xl-times-square-browser-review-v2-20261019'
PHYSICAL=BASE/'government-xl-times-square-ordinary-validation-v2-20261019'
TERRAIN=PHYSICAL
PREVIOUS=HERE/'local/government-xl-times-square-assembly-browser-desktop-v1-20261019'
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
    sources={r['uid']:r['sourceSHA256']for r in qualification['sourceBindings']};assert len(sources)==3
    image_review=read(BROWSER/'ROOT-IMAGE-REVIEW.json');assert image_review['visualAcceptance']and image_review['reviewer']=='Codex ROOT'
    assert image_review['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
    report=read(BROWSER/'staged-browser.json');assert report['passed']and not report['errors']
    views=[v for v in report['views']if 'time'in v];assert len(views)==12 and len(report['jointViews'])==6
    assert len(image_review['imagesActuallyViewed'])==12
    for q in image_review['imagesActuallyViewed']:check(q)
    assert image_review['sourceCatalogue']==ref(PREVIOUS/'catalogue.json')
    candidate=read(TERRAIN/'terrain-candidates.json')[0]
    assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256']
    actors={r['uid']for r in read(PHYSICAL/'neighbour-checks.json')['rows']}|set(sources)
    keys=sorted({('basic-building:'if prefix=='building:'and not uid.startswith('landsd/')else prefix)+uid for prefix in ['building:','terrain-patch:']for uid in actors})
    claim=reservations.claim('pacifica-private-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        DOC.mkdir();STAGE.mkdir();cat=read(PREVIOUS/'catalogue.json');original=copy.deepcopy(cat)
        for e in cat['models']:
            assert e['sha256']==sources[e['uid']]and e['proceduralWindows']is False
            e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,
                aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(FUNCTIONAL/'qualification.json'),
                placementReview='Unchanged original at 1x/source pose. Complete terrain, neighbours, loader/picking/collision and desktop/mobile checks verified. Exact original facade/wall applicability preserves raw tower contact and Tower254824 compound-foundation failures; no numeric tolerance changed.')
            target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PREVIOUS/e['asset'],target);assert digest(target.read_bytes())==e['sha256']
        save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));shutil.copyfile(PREVIOUS/'source-forms.json',STAGE/'source-forms.json')
        patch=read(ROOT/candidate['path']);out=STAGE/'government-native-times-square-original-v1-20261019.json';shutil.copyfile(ROOT/candidate['path'],out);assert digest(out.read_bytes())==candidate['sha256']
        terrain=dict(source=str(out.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+out.name,resolution=patch['cell'],area='Times Square original-source terrain')
        destination='city/data/official-models/'+BATCH+'/catalogue.json'
        save(STAGE/'plan.json',dict(areas=[dict(area='Times Square podium and two unchanged original towers',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[terrain]))
        for width in [390,1280]:
            cfg=read(PREVIOUS/'browser-config.json');cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/browser-'+str(width)+'/',catalogueURL=destination,terrain=[terrain],viewportWidths=[width]);save(STAGE/('browser-config-'+str(width)+'.json'),cfg)
        deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
        for p,h in deps['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
        pub=module('pacifica_private_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
        save(DOC/'qualification.json',dict(uids=sorted(sources),sourceSHA256ByUid=sources,sourceFunctionalApplicability=ref(FUNCTIONAL/'qualification.json'),visualReview=ref(BROWSER/'ROOT-IMAGE-REVIEW.json'),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),leaseResources=keys,privateStageQualified=True,publication=False,fullAcceptance=False))
        for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
        refs.extend(p for p in STAGE.rglob('*')if p.is_file())
        module('pacifica_private_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-three-original-private-stage',list(dict.fromkeys(refs)),dict(uids=sorted(sources),privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False))
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
