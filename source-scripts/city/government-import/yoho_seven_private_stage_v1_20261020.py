"""Stage exact original tower/podium and reviewed source terrain; publisher dry run."""
from pathlib import Path
import copy,shutil,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-seven-private-stage-v1-20261020';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
BROWSER=BASE/'government-xl-yoho-seven-browser-review-v1-20261020';PREVIOUS=HERE/'local/government-xl-yoho-seven-browser-own-mobile-v2-20261020';POD='landsd/301636:0'
def folder(n):return BASE/('government-xl-yoho-seven-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def main():
 assert not DOC.exists() and not STAGE.exists();pins={};refs=[Path(__file__)]
 for d in [BROWSER,folder('physical-review-v1'),folder('loader-v1'),folder('current-neighbours-v2'),BASE/'government-xl-yoho300857-current-terrain-scope-v1-20261020',BASE/'government-xl-yoho-compound-identity-review-v1-20261020']:
  r=read(d/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 physical=read(folder('physical-review-v1')/'ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted'] and physical['rawStrictFailuresRetained'] and len(physical['accounts'])==28
 sources=physical['sourceSHA256ByUid'];assert len(sources)==7 and POD in sources
 images=read(BROWSER/'ROOT-IMAGE-REVIEW.json');assert images['visualAcceptance'] and len(images['imagesActuallyViewed'])==42 and images['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
 v=read(folder('loader-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==7 and v['exceptions']==0
 near=read(folder('current-neighbours-v2')/'summary.json');assert not near['remainingFailures'] and near['forms']==217
 scope=read(BASE/'government-xl-yoho300857-current-terrain-scope-v1-20261020'/'scope.json');assert scope['allCurrentActorsNominated'] and not scope['touchingNativeUids'] and scope['currentNativeActors']==6764
 identityDoc=BASE/'government-xl-yoho-seven-original-identity-v4-20261020';ir=read(identityDoc/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(ir['jobId'],)).fetchone()==('complete',ir)
 for uid in set(sources)-{POD,'landsd/301659:0'}:
  p=identityDoc/uid.split('/')[1]/'identity.json';assert ref(p)in ir['evidenceRefs'];proof=read(p);assert proof['passed'] and proof['sourceSHA256']==sources[uid];refs.append(p)
 refs.append(identityDoc/'result.json')
 identity=read(BASE/'government-xl-yoho-compound-identity-review-v1-20261020/ROOT-COMPOUND-IDENTITY-REVIEW.json');assert identity['compoundIdentityAccepted'] and not identity['standaloneSmallStructureIdentityAccepted'] and identity['requiredCompanionSHA256']==sources[POD]
 neighbourIds={x['building']['uid'] for x in read(folder('current-neighbours-v2')/'neighbour-inputs.json.gz')['rows']}
 keys=['building:'+u for u in sorted(neighbourIds|set(sources))]+['terrain:city/data/terrain.json']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();STAGE.mkdir();cat=read(PREVIOUS/'catalogue.json');rows={r['uid']:r for r in read(folder('private-terrain-v1')/'selection.json.gz')['rows']}
  qualification=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifest=images['currentManifest'],privateStageQualified=True,sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],rawStrictFailuresRetained=True,sourceReviews=[ref(folder('physical-review-v1')/'ROOT-PHYSICAL-REVIEW.json'),ref(BASE/'government-xl-yoho-compound-identity-review-v1-20261020'/'ROOT-COMPOUND-IDENTITY-REVIEW.json')],visualReview=ref(BROWSER/'ROOT-IMAGE-REVIEW.json'),leaseResources=keys,terrainReplacement=True,sourceGeometryChanges=0,sourcePoseChanges=0,publication=False)
  save(DOC/'qualification.json',qualification)
  for e in cat['models']:
   assert e['sha256']==sources[e['uid']] and e['proceduralWindows'] is False and not e.get('suppressesBuildingUids');r=rows[e['uid']]
   e.update(originalSourceKey=r['native']['cacheKey']+'/'+r['modelId'],sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(DOC/'qualification.json'),placementReview='Unchanged original tower and podium at native 1x pose; exact compound identity and authored ground/podium intersections reviewed with raw warnings retained. Original-source terrain passes complete foundations, full current actor scope and all217 ordinary neighbour checks. Desktop/mobile day-night picking/collision and independent fallback/retry verified. No extra suppression or procedural windows.')
   target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PREVIOUS/e['asset'],target);assert digest(target.read_bytes())==e['sha256']
  save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=7,catalogues=['catalogue.json']));shutil.copyfile(PREVIOUS/'source-forms.json',STAGE/'source-forms.json')
  config=read(PREVIOUS/'browser-config.json');terrain=copy.deepcopy(config['terrain']);assert len(terrain)==1
  for e in terrain:
   check(dict(path=e['source'],sha256=e['sha256']));p=STAGE/Path(e['source']).name;shutil.copyfile(ROOT/e['source'],p);e['source']=str(p.relative_to(ROOT))
  destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='Seven unchanged YOHO originals',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=terrain))
  for width in [390,1280]:
   tested=HERE/'local'/('government-xl-yoho-seven-browser-own-mobile-v2-20261020' if width==390 else 'government-xl-yoho-seven-browser-own-desktop-v2-20261020');cfg=read(tested/'browser-config.json');cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/browser-'+str(width)+'/',catalogueURL=destination,terrain=terrain,viewportWidths=[width]);save(STAGE/('browser-config-'+str(width)+'.json'),cfg)
  deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(r['blockers'] for r in deps['rows']);save(DOC/'dependencies.json',deps)
  for p,h in deps['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  pub=module('tower6803_private_stage_pub',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  refs.extend(p for p in STAGE.rglob('*') if p.is_file())
  module('tower6803_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-pair-and-government-terrain-private-stage',list(dict.fromkeys(refs)),dict(uids=sorted(sources),privateStageQualified=True,publisherDryRunPassed=True,publication=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
