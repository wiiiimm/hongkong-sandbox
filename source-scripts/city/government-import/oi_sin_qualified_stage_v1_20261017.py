"""Exact four-original Oi Sin installation stage; dry run only."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-oi-sin-qualified-stage-v1-20261017';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PREVIOUS=BASE/'government-xl-aqua272788-original-installed-v1-20261017/full-xl-current-count.json'
def folder(n):return BASE/('government-xl-oi-sin-'+n+'-20261017')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
ROWS=read(folder('four-originals-physical-v2')/'selection.json.gz')['rows'];SOURCES={r['uid']:r['sourceSHA256']for r in ROWS};PODIUM='landsd/91128:0'
def verify():
 pins={}
 for name in ['original-boundary-review-v1','carpark-source-review-v1','four-originals-neighbours-v2','four-originals-browser-v4','current-native-scope-v3']:
  p=folder(name)/'result.json';r=read(p)
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']+[ref(p)]:
   assert e['path']not in pins or pins[e['path']]==e;pins[e['path']]=e
 for e in pins.values():check(e)
 return pins

def main():
 assert not DOC.exists()and not STAGE.exists();pins=verify()
 tower=read(folder('original-boundary-review-v1')/'ROOT-SOURCE-REVIEW.json');review=read(folder('carpark-source-review-v1')/'ROOT-SOURCE-REVIEW.json');assert tower['sourceSpecificBoundaryInterpretationAccepted']and tower['sourceIdentityAssemblyQualified'];assert review['sourceSpecificJunctionInterpretationAccepted']and review['smallCarparkIdentity']['sourceSpecificAssemblyIdentityAccepted'];assert review['sourceSHA256ByUid']==SOURCES
 neighbours=read(folder('four-originals-neighbours-v2')/'summary.json');assert not neighbours['remainingFailures']and neighbours['forms']==18
 scope=read(folder('current-native-scope-v3')/'scope.json');assert scope['allCurrentActorsNominated']and not scope['touchingNativeUids']and scope['currentNativeActors']==6674
 images=read(folder('four-originals-browser-v4')/'ROOT-IMAGE-INSPECTION.json');assert images['sourceGeometryAppearanceAccepted']
 for e in images['reviewedImages']:check(e)
 browser=read(folder('four-originals-browser-v4')/'staged-browser.json');assert browser['passed']and not browser['errors'];assert len([v for v in browser['views']if 'time'in v])==16
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==read(PREVIOUS)['manifestSHA256']
 prior=HERE/'local'/folder('four-originals-browser-v4').name;cat=read(prior/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==SOURCES
 DOC.mkdir();STAGE.mkdir();qualification=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,currentManifest=ref(manifest),privateStageQualified=True,sourceGeometryChanges=0,sourcePoseChanges=0,rawStrictFailuresRetained=True,sourceReviews=[ref(folder(n)/'ROOT-SOURCE-REVIEW.json')for n in ['original-boundary-review-v1','carpark-source-review-v1']],completeNeighbourEvidence=ref(folder('four-originals-neighbours-v2')/'result.json'),publication=False)
 save(DOC/'qualification.json',qualification);save(DOC/'ROOT-IMAGE-INSPECTION.json',images)
 rows={r['uid']:r for r in ROWS}
 for m in cat['models']:
  r=rows[m['uid']];assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids');m.update(originalSourceKey=r['sectionId']+'/'+r['modelId'],sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceFunctionalApplicability=ref(DOC/'qualification.json'),sourceIdentityReview=ref(folder('carpark-source-review-v1')/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Complete unchanged original assembly at1x. Exact-source identity/junction reviews retain raw strict warnings; all-mode foundations and actual perimeter evidence, all current neighbours and desktop/mobile exports verified.')
  if m['uid']!=PODIUM:assert len(m['supportDependencies'])==1 and m['supportDependencies'][0]['uid']==PODIUM and m['supportDependencies'][0]['sha256']==SOURCES[PODIUM]
  p=STAGE/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(prior/m['asset'],p);assert ref(p)['sha256']==m['sha256']
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=4,catalogues=['catalogue.json']));shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json')
 candidate=read(folder('four-originals-physical-v2')/'terrain-candidates.json')[0];assert not candidate.get('replaces');p=ROOT/candidate['path'];check(dict(path=candidate['path'],sha256=candidate['sha256']));dest=STAGE/'government-native-oi-sin-original-v1-20261017.json';shutil.copyfile(p,dest)
 terrain=dict(source=str(dest.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+dest.name,resolution=5,area='Oi Sin original assembly terrain');url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='Oi Sin four unchanged originals',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=[terrain]))
 config=read(prior/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,terrain=[terrain]);save(STAGE/'browser-config.json',config)
 pub=module('oi_sin_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for e in pins.values():check(e)
 r=module('oi_sin_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-four-original-qualified-stage-v1',[Path(__file__),PREVIOUS,*[ROOT/p for p in pins],folder('four-originals-browser-v4')/'ROOT-IMAGE-INSPECTION.json',*[p for p in STAGE.rglob('*')if p.is_file()]],dict(uids=list(SOURCES),privateStageQualified=True,publisherDryRunPassed=True,publication=False,nextStep='Guarded atomic four-original installation with terrain addition, live checks and verified ledger/count update.'));print(r['jobId'],flush=True)
if __name__=='__main__':main()
