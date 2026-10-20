"""Stage exact original tower/podium and reviewed source terrain; publisher dry run."""
from pathlib import Path
import copy,shutil,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-private-stage-v2-20261020';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
BROWSER=BASE/'government-xl-tower6803-browser-review-v2-20261020';PREVIOUS=HERE/'local/government-xl-tower6803-browser-desktop-v1-20261020';POD='landsd/15047:0'
def folder(n):return BASE/('government-xl-tower6803-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def main():
 assert not DOC.exists() and not STAGE.exists();pins={};refs=[Path(__file__)]
 for d in [BROWSER,folder('physical-review-v1'),folder('loader-v1'),folder('current-neighbours-v1'),folder('current-terrain-scope-v1'),folder('podium-native-yaw-v1')]:
  r=read(d/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 physical=read(folder('physical-review-v1')/'ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted'] and physical['rawFailuresPreserved'] and len(physical['sampleAccounts'])==4
 sources=physical['sourceSHA256ByUid'];assert set(sources)=={'landsd/6803:0',POD}
 images=read(BROWSER/'ROOT-IMAGE-REVIEW.json');assert images['visualAcceptance'] and len(images['imagesActuallyViewed'])==8 and images['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
 v=read(folder('loader-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==2 and v['exceptions']==0
 near=read(folder('current-neighbours-v1')/'summary.json');assert not near['remainingFailures'] and near['forms']==10
 scope=read(folder('current-terrain-scope-v1')/'scope.json');assert scope['allCurrentActorsNominated'] and not scope['touchingNativeUids'] and scope['currentNativeActors']==6762
 identityPath=BASE/'government-xl-next-twenty-original-identity-v2-20261020/6803:0/identity.json';ir=read(identityPath.parent.parent/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(ir['jobId'],)).fetchone()==('complete',ir)
 assert ref(identityPath) in ir['evidenceRefs'];identity=read(identityPath);assert identity['passed'] and identity['sourceSHA256']==sources['landsd/6803:0'];refs.extend([identityPath,identityPath.parent.parent/'result.json'])
 yaw=read(folder('podium-native-yaw-v1')/'proof.json');assert yaw['sourceBoundIdentityPassed'] and yaw['sourceSHA256']==sources[POD]
 neighbourIds={x['building']['uid'] for x in read(folder('current-neighbours-v1')/'neighbour-inputs.json.gz')['rows']}
 keys=['building:'+u for u in sorted(neighbourIds|set(sources))]+['terrain:city/data/terrain.json']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();STAGE.mkdir();cat=read(PREVIOUS/'catalogue.json');rows={r['uid']:r for r in read(folder('private-terrain-capture-v1')/'selection.json.gz')['rows']}
  qualification=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifest=images['currentManifest'],privateStageQualified=True,sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],rawStrictFailuresRetained=True,sourceReviews=[ref(folder('physical-review-v1')/'ROOT-PHYSICAL-REVIEW.json'),ref(folder('podium-native-yaw-v1')/'proof.json')],visualReview=ref(BROWSER/'ROOT-IMAGE-REVIEW.json'),leaseResources=keys,terrainReplacement=True,sourceGeometryChanges=0,sourcePoseChanges=0,publication=False)
  save(DOC/'qualification.json',qualification)
  for e in cat['models']:
   assert e['sha256']==sources[e['uid']] and e['proceduralWindows'] is False and not e.get('suppressesBuildingUids');r=rows[e['uid']]
   e.update(originalSourceKey=r['native']['cacheKey']+'/'+r['modelId'],sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(DOC/'qualification.json'),placementReview='Unchanged original tower and podium at native 1x pose; exact native yaw and authored facade/podium intersections reviewed with raw warnings retained. Original-source terrain passes complete foundations, full current actor scope and all10 ordinary neighbour checks. Desktop/mobile day-night picking/collision and independent fallback/retry verified. No extra suppression or procedural windows.')
   target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PREVIOUS/e['asset'],target);assert digest(target.read_bytes())==e['sha256']
  save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));shutil.copyfile(PREVIOUS/'source-forms.json',STAGE/'source-forms.json')
  config=read(PREVIOUS/'browser-config.json');terrain=copy.deepcopy(config['terrain']);assert len(terrain)==1
  for e in terrain:
   check(dict(path=e['source'],sha256=e['sha256']));p=STAGE/Path(e['source']).name;shutil.copyfile(ROOT/e['source'],p);e['source']=str(p.relative_to(ROOT))
  destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='Tower 1 and original podium',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=terrain))
  for width in [390,1280]:
   cfg=copy.deepcopy(config);cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/browser-'+str(width)+'/',catalogueURL=destination,terrain=terrain,viewportWidths=[width]);save(STAGE/('browser-config-'+str(width)+'.json'),cfg)
  deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(r['blockers'] for r in deps['rows']);save(DOC/'dependencies.json',deps)
  for p,h in deps['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  pub=module('tower6803_private_stage_pub',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  refs.extend(p for p in STAGE.rglob('*') if p.is_file())
  module('tower6803_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-pair-and-government-terrain-private-stage',list(dict.fromkeys(refs)),dict(uids=sorted(sources),privateStageQualified=True,publisherDryRunPassed=True,publication=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
