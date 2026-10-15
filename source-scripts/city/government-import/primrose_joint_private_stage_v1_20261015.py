"""Qualify exact original Primrose assembly without altering government geometry."""
import sys,shutil,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-primrose-joint-private-stage-v1-20261015';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
BROWSER=BASE/'government-xl-primrose-current-assembly-browser-v1-20261015';REBIND=BASE/'government-xl-primrose-current-map-rebind-v1-20261015'
PODIUM='landsd/74573:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def data(name,file):return read(BASE/('government-xl-primrose-'+name+'-20261015')/file)
def main():
 assert not DOC.exists()and not STAGE.exists();refs={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [REBIND,BROWSER]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']+[ref(d/'result.json')]:
    if q['path']in refs:assert refs[q['path']]==q
    refs[q['path']]=q
 for q in refs.values():check(q)
 reconciliation=read(REBIND/'reconciliation.json');assert reconciliation['allChangesOutsidePrimroseParent']and reconciliation['allOtherEvidenceUnchanged'];check(reconciliation['currentManifest'])
 identity=data('current-identity-v1','result.json');assert len(identity['rows'])==4 and all(r['passed']and not r['reasons']for r in identity['rows'])
 tower=data('towers-complete-finite-v1','summary.json')['rows'];assert len(tower)==12 and all(not r['unproved']and not r['uncovered']for r in tower)
 foundation=data('compound-foundation-v2','summary.json')['rows'];assert len(foundation)==16
 for r in foundation:
  if r['uid']!=PODIUM:assert r['strictFoundationAccepted']
  else:assert r['foundation']['fullyBuriedTriangles']==1 and r['foundation']['fullyBuriedUpwardTriangles']==0
 basic=data('join-basic-finite-v5','summary.json');assert basic['all54ActorsComplete']and basic['noIntroducedFailures']and len(basic['rows'])==54 and all(not r['introducedUnproved']and not r['afterUncovered']for r in basic['rows'])
 role=data('podium-role-review-v2','ROOT-SOURCE-REVIEW.json');assert role['sourceRoleInterpretationAccepted']and role['rawStrictClearanceFailuresRetained']and len(role['verticalFaces'])==15 and len(role['downwardFaces'])==7
 shelter=data('shelter-source-review-v1','ROOT-SOURCE-REVIEW.json');assert shelter['conditionalBasicSuppressionApprovedForStaging']and shelter['originalPodiumUID']==PODIUM and shelter['suppressedBasicUID']=='landsd/74566:0'
 report=read(BROWSER/'staged-browser.json');views=[v for v in report['views']if 'time'in v];assert report['passed']and not report['errors']and len(views)==16 and len(report['jointViews'])==8
 failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['suppressedBasicsRestored']=={'landsd/74566:0':True}
 review=read(BROWSER/'ROOT-ASSEMBLY-IMAGE-REVIEW.json');assert review['wholeAssemblyVisualAcceptance']and review['reviewedWholeAssemblyViews']==4
 for q in review['reviewedImages']:check(q)
 rows=data('remaining-original-components-v2','selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};assert sources[PODIUM]==role['sourceSHA256']==shelter['originalPodiumSHA256']
 for r in rows:assert r['source']['building']in read(ROOT/'3d-viewer'/r['source']['tile'])['buildings']
 keys=sorted({('basic-building:' if prefix=='building:'and not u.startswith('landsd/')else prefix)+u for prefix in ['building:','terrain-patch:']for u in set(sources)|{r['uid']for r in basic['rows']}}|{'immutable-source-proof:'+BATCH});claim=reservations.claim('primrose-qualified-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();STAGE.mkdir();candidate=data('private-terrain-floor-v5','terrain-candidates.json')[0];patch=read(ROOT/candidate['path']);parent=read(ROOT/'3d-viewer/city/data/terrain.json');pub=module('primrose_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.validate_patch(patch,parent);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');pub.check_patch_overlap(patch,parent.get('patches',[])+[read(ROOT/'3d-viewer'/e['url'])for e in manifest['terrainPatches']])
  qualification=dict(uids=list(sources),sourceSHA256ByUid=sources,privateStageQualified=True,rawStrictFailuresRetained=True,podiumReviewedVerticalFaces=role['verticalFaces'],podiumReviewedDownwardFaces=role['downwardFaces'],podiumBuriedDownwardClosureFaces=1,towerFullClearanceWorlds=12,retainedBasicActors=54,newNeighbourFailures=0,conditionalShelterSuppression='landsd/74566:0',failedPodiumRestoresShelter=True,sourceGeometryChanges=0,sourcePoseChanges=0,visualReview=ref(BROWSER/'ROOT-ASSEMBLY-IMAGE-REVIEW.json'),currentMapReconciliation=ref(REBIND/'reconciliation.json'),publication=False,fullAcceptance=False)
  save(DOC/'qualification.json',qualification)
  previous=HERE/'local'/BROWSER.name;cat=read(previous/'catalogue.json')
  for e in cat['models']:
   assert e['sha256']==sources[e['uid']];e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(DOC/'qualification.json'),placementReview='Unchanged original at source pose and 1x scale. Complete three-tower compound clearance and foundation; source-specific podium lower-closure/wall review preserves numerical warnings. Full neighbour checks and current browser assembly/fallback pass.')
   target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(previous/e['asset'],target);assert ref(target)['sha256']==e['sha256']
  save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=4,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[r['source']['building']for r in rows]);out=STAGE/'government-native-primrose-original-v1-20261015.json';shutil.copyfile(ROOT/candidate['path'],out);assert ref(out)['sha256']==candidate['sha256']
  terrain=dict(source=str(out.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+out.name,resolution=patch['cell'],area='Primrose original-source terrain');destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='Primrose Hill unchanged original assembly',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[terrain]))
  config=read(previous/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain]);save(STAGE/'browser-config.json',config)
  pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
  for q in refs.values():check(q)
  paths=[ROOT/p for p in refs]+[Path(__file__),BROWSER/'ROOT-ASSEMBLY-IMAGE-REVIEW.json']+[p for p in STAGE.rglob('*')if p.is_file()]
  module('stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-four-original-assembly-private-stage-v1',paths,dict(uids=list(sources),privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
