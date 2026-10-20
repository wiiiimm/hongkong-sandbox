"""Stage five unchanged originals, reviewed terrain and one guarded BASIC base; dry run only."""
from pathlib import Path
import copy,shutil,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-five-private-stage-v1-20261020';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;POD='landsd/285642:0';PREVIOUS=HERE/'local/government-xl-china-ferry-perimeter-browser-v1-20261020'
def folder(n):return BASE/('government-xl-china-ferry-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();pins={};refs=[Path(__file__)]
 names=['five-physical-review-v1','five-image-review-v1','perimeter-browser-v1','five-browser-mobile-v1','five-browser-desktop-v1','five-loader-v1','five-original-identity-v2','companion-identity-review-v1','current-neighbours-v1','estimated-base-proposal-v1','final-terrain-budget-v1']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in names:
   f=folder(n);r=read(f/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(f/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 physical=read(folder('five-physical-review-v1')/'ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted']and len(physical['accounts'])==20;sources=physical['sourceSHA256ByUid'];assert len(sources)==5
 visual=read(folder('five-image-review-v1')/'ROOT-IMAGE-REVIEW.json');assert visual['ordinaryModelViewsAccepted']and len(visual['imagesActuallyViewed'])==20
 reports=[];images=list(visual['imagesActuallyViewed'])
 for n in ['five-browser-desktop-v1','five-browser-mobile-v1','perimeter-browser-v1']:
  p=folder(n)/'staged-browser.json';r=read(p);assert r['passed']and not r['errors'];reports.append(ref(p))
  if n=='perimeter-browser-v1':
   for v in r['views']+r.get('retainedNativeOwnViews',[])+r['perimeterViews']:
    if 'file'in v:images.append(ref(folder(n)/v['file']))
 assert len(images)==26
 identityReview={r['uid']:r for r in read(folder('companion-identity-review-v1')/'review.json')['rows']}
 for uid,sha in sources.items():
  ident=read(folder('five-original-identity-v2')/uid.split('/')[1]/'identity.json');assert ident['sourceSHA256']==sha
  if uid in identityReview:assert identityReview[uid]['sourceIdentityApproved']and identityReview[uid]['sourceSHA256']==sha and not identityReview[uid]['suppressesBuildingUids']
  else:assert ident['passed']and not ident['reasons']
 native=read(folder('current-neighbours-v1')/'native-neighbour-checks.json');assert all(x['passed']for x in native['rows'])and not(set(native['blocked'])-set(native['resolved']))
 near=read(folder('estimated-base-proposal-v1')/'neighbour-checks.json');flagged={r['uid']for r in near['rows']if r['reasons']};assert flagged==set(sources)-{POD}
 assert all(r['reasons']==['increased-neighbour-ground-gap']for r in near['rows']if r['uid']in flagged)
 v=read(folder('five-loader-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==5 and not v['exceptions']
 keys=['building:'+x['uid']for x in near['rows']]+['terrain:city/data/terrain.json'];claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();STAGE.mkdir();cat=read(PREVIOUS/'catalogue.json');cfg=read(PREVIOUS/'browser-config.json');assert {e['uid']:e['sha256']for e in cat['models']}==sources
  qualification=dict(uids=sorted(sources),sourceSHA256ByUid=sources,privateStageQualified=True,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),rawStrictFailuresRetained=True,sourceScopedApplicabilityAccepted=True,leaseResources=keys,sourceReviews=[ref(folder('five-physical-review-v1')/'ROOT-PHYSICAL-REVIEW.json'),ref(folder('companion-identity-review-v1')/'review.json')],browserReports=reports,imagesActuallyViewed=images,visualAcceptance=True,sourceGeometryChanges=0,publication=False)
  save(DOC/'qualification.json',qualification)
  for e in cat['models']:
   assert e['proceduralWindows']is False and not e.get('suppressesBuildingUids');assert bool(e['supportDependencies'])==(e['uid']!=POD)
   e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(DOC/'qualification.json'),placementReview='Exact original 1x government source. Four-mode strict companion foundations/support; exact terminal lower-perimeter intersections reviewed with raw warnings retained. Current native neighbour and guarded estimated BASIC base checked. Desktop/mobile original-source picking, collision, solid rendering and independent retry verified. No extra suppression or procedural windows.')
   p=STAGE/e['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PREVIOUS/e['asset'],p);assert digest(p.read_bytes())==e['sha256']
  save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=5,catalogues=['catalogue.json']));shutil.copyfile(PREVIOUS/'source-forms.json',STAGE/'source-forms.json')
  terrain=copy.deepcopy(cfg['terrain']);assert len(terrain)==1
  for e in terrain:
   p=STAGE/Path(e['source']).name;shutil.copyfile(ROOT/e['source'],p);assert digest(p.read_bytes())==e['sha256'];e['source']=str(p.relative_to(ROOT))
  proposal=read(folder('estimated-base-proposal-v1')/'proposal.json');assert len(proposal['buildings'])==1 and proposal['buildings'][0]['uid']=='landsd/81118:0'
  save(STAGE/'estimated-bases.json',dict(parentSha256=digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes()),refinementSha256=terrain[0]['sha256'],buildings=proposal['buildings']))
  destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='China Ferry five original sources',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination,estimates=[str((STAGE/'estimated-bases.json').relative_to(ROOT))])],topLevelTerrainPatches=terrain))
  deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(x['blockers']for x in deps['rows']);save(DOC/'dependencies.json',deps)
  for p,h in deps['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  pub=module('china_ferry_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  refs.extend(p for p in STAGE.rglob('*')if p.is_file());module('china_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-original-qualified-private-stage-with-estimated-base',list(dict.fromkeys(refs)),dict(uids=sorted(sources),privateStageQualified=True,publisherDryRunPassed=True,publication=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
