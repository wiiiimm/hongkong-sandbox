"""Prepare reviewed original pair for guarded publication; no live writes."""
import shutil,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
from olympian_one_functional_applicability_v1_20261018 import EXPECTED,POD,TOWER
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-one-private-stage-v1-20261018';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
SOURCES={u:e[1]for u,e in EXPECTED.items()};BROWSER=BASE/'government-xl-olympian-one-assembly-browser-v3-20261018';PHYSICAL=BASE/'government-xl-olympian-one-pair-physical-v2-20261018';FUNCTIONAL=BASE/'government-xl-olympian-one-functional-applicability-v1-20261018'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def main():
 assert not DOC.exists()and not STAGE.exists();refs={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [PHYSICAL,FUNCTIONAL,BROWSER]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']+[ref(d/'result.json')]:
    assert q['path']not in refs or refs[q['path']]==q;refs[q['path']]=q
 for q in refs.values():check(q)
 qualification=read(FUNCTIONAL/'qualification.json');assert qualification['sourceScopedApplicabilityAccepted']and not qualification['remainingPhysicalReasons']and not qualification['strictInterfacePassed']
 report=read(BROWSER/'staged-browser.json');views=[v for v in report['views']if 'time'in v]
 assert report['passed']and not report['errors']and len(views)==8 and len(report['jointViews'])==4
 image_review=read(BROWSER/'ROOT-IMAGE-REVIEW.json');assert image_review['visualAcceptance']and image_review['reviewer']=='Codex ROOT'
 assert image_review['stagedBrowser']==ref(BROWSER/'staged-browser.json')and image_review['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
 assert image_review['imagesActuallyViewed']==[ref(BROWSER/v['file'])for v in views]
 for v in views:assert v['fullyFramed']and v['solidAppearance']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]
 actors={r['uid']for r in read(PHYSICAL/'neighbour-checks.json')['rows']}|set(SOURCES)|{'landsd/253891:0'}
 keys={('basic-building:'if p=='building:'and not u.startswith('landsd/')else p)+u for p in ['building:','terrain-patch:']for u in actors}
 claim=reservations.claim('olympian-one-stage-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();STAGE.mkdir();candidate=read(PHYSICAL/'terrain-candidates.json')[0];patch=read(ROOT/candidate['path']);parent=read(ROOT/'3d-viewer/city/data/terrain.json');pub=module('olympian_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.validate_patch(patch,parent);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');pub.check_patch_overlap(patch,parent.get('patches',[])+[read(ROOT/'3d-viewer'/e['url'])for e in manifest['terrainPatches']])
  previous=HERE/'local'/BROWSER.name;cat=read(previous/'catalogue.json')
  for e in cat['models']:
   assert e['sha256']==SOURCES[e['uid']];e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(FUNCTIONAL/'qualification.json'),placementReview='Exact original source at 1x/source pose. Complete compound foundations, loader/picking/collision and current neighbours pass. Reviewed tower lower facade-band applicability preserves raw 450/497 strict result; all 47 failures remain recorded.')
   target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(previous/e['asset'],target);assert ref(target)['sha256']==e['sha256']
  save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));shutil.copyfile(previous/'source-forms.json',STAGE/'source-forms.json')
  out=STAGE/'government-native-olympian-one-original-v1-20261018.json';shutil.copyfile(ROOT/candidate['path'],out);assert ref(out)['sha256']==candidate['sha256']
  terrain=dict(source=str(out.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+out.name,resolution=patch['cell'],area='Olympian City One original-source terrain');destination='city/data/official-models/'+BATCH+'/catalogue.json'
  save(STAGE/'plan.json',dict(areas=[dict(area='Olympian City One and Bank of China Centre unchanged originals',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[terrain]))
  config=read(previous/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain]);save(STAGE/'browser-config.json',config)
  deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
  for p,h in deps['inputHashes'].items():check(dict(path=p,sha256=h));refs[p]=dict(path=p,sha256=h)
  pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
  save(DOC/'qualification.json',dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,sourceFunctionalApplicability=ref(FUNCTIONAL/'qualification.json'),visualReview=ref(BROWSER/'ROOT-IMAGE-REVIEW.json'),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),leaseResources=sorted(keys),privateStageQualified=True,publication=False,fullAcceptance=False))
  for q in refs.values():check(q)
  paths=[ROOT/p for p in refs]+[Path(__file__),BROWSER/'ROOT-IMAGE-REVIEW.json']+[p for p in STAGE.rglob('*')if p.is_file()]
  module('olympian_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-pair-private-stage',paths,dict(uids=list(SOURCES),privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
