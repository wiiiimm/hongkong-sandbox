"""Exact three-original Orchards stage with retained-native terrain replacement."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-qualified-stage-v1-20261017';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PREVIOUS=BASE/'government-xl-oi-sin-original-installed-v1-20261017/full-xl-current-count.json'
TOWER='landsd/254629:0';PODIUM='landsd/233002:0';COMMUNITY='landsd/256434:0';RETAINED='landsd/254621:0'
def folder(n):return BASE/('government-xl-orchards-'+n+'-20261017')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
ROWS=[r for r in read(folder('assembly-terrain-candidate-v1')/'selection.json.gz')['rows']if r['uid']!=RETAINED];SOURCES={r['uid']:r['sourceSHA256']for r in ROWS}
def verify():
 pins={}
 for name in ['podium-component-identity-v1','named-connection-identity-v1','assembly-terrain-candidate-v1','assembly-neighbours-v1','assembly-four-foundations-v1','original-roles-review-v1','assembly-runtime-validation-v1','assembly-visual-review-v1']:
  p=folder(name)/'result.json';r=read(p)
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']+[ref(p)]:
   assert e['path']not in pins or pins[e['path']]==e;pins[e['path']]=e
 for e in pins.values():check(e)
 return pins

def main():
 assert not DOC.exists()and not STAGE.exists();pins=verify();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==read(PREVIOUS)['manifestSHA256']
 review=read(folder('original-roles-review-v1')/'ROOT-SOURCE-REVIEW.json');assert review['sourceSpecificBoundaryInterpretationAccepted']and review['sourceSpecificGradeInterpretationAccepted'];assert all(review['sourceSHA256ByUid'][u]==s for u,s in SOURCES.items())
 identities={u:read(folder(n)/'identity.json')for u,n in [(TOWER,'named-connection-identity-v1'),(PODIUM,'podium-component-identity-v1')]}
 for u,r in identities.items():assert r['passed']and r['sourceSHA256']==SOURCES[u]and r['exactRouteManifestSHA256']==ref(manifest)['sha256']
 assert identities[PODIUM]['requiredCompanionUid']==COMMUNITY and identities[PODIUM]['requiredCompanionSHA256']==SOURCES[COMMUNITY]
 neighbours=read(folder('assembly-neighbours-v1')/'summary.json');assert not neighbours['basicFlags']and neighbours['forms']==49 and neighbours['nativeResolved']==[RETAINED]
 scope=read(folder('assembly-terrain-candidate-v1')/'scope.json');assert scope['allCurrentActorsNominated']and scope['currentNativeActors']==6678 and scope['touchingNativeUids']==[RETAINED]
 foundations=read(folder('assembly-four-foundations-v1')/'summary.json');assert foundations['allModesPassed']and len(foundations['rows'])==16 and all(r['passed']and r['buried']==0 for r in foundations['rows'])
 validation=read(folder('assembly-runtime-validation-v1')/'validation.json');assert validation['loaderAccepted']==validation['checksPassed']==validation['models']==3 and validation['exceptions']==0
 assert validation['concerns']=={'sampled-ground-gap-below-model-bottom':1,'sampled-terrain-above-model-bottom':2}
 images=read(folder('assembly-visual-review-v1')/'ROOT-IMAGE-INSPECTION.json');assert images['sourceGeometryAppearanceAccepted']and len(images['reviewedImages'])==18
 for e in images['reviewedImages']:check({k:e[k]for k in ['path','sha256']})
 browser=read(folder('assembly-private-browser-v4')/'staged-browser.json');assert browser['passed']and not browser['errors']and len([r for r in browser['views']if 'time'in r])==12 and len(browser['retainedNativeOwnViews'])==4
 prior=HERE/'local'/folder('assembly-private-browser-v4').name;cat=read(prior/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==SOURCES
 DOC.mkdir();STAGE.mkdir();qualification=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,currentManifest=ref(manifest),privateStageQualified=True,sourceGeometryChanges=0,sourcePoseChanges=0,rawStrictFailuresRetained=True,sourceReviews=[ref(folder(n)/f)for n,f in [('original-roles-review-v1','ROOT-SOURCE-REVIEW.json'),('podium-component-identity-v1','identity.json'),('named-connection-identity-v1','identity.json')]],requiredIdentityCompanion=dict(owner=PODIUM,uid=COMMUNITY,sha256=SOURCES[COMMUNITY]),rawValidatorConcerns=validation['concerns'],diagnosticResolution='Tower2 rests on the exact original podium; its one original ledge corner has the bounded source review. Podium and community negative bottom samples are the exact reviewed grade-wall/underside faces. Raw strict reasons remain unchanged; all complete foundations and neighbour checks pass.',retainedUid=RETAINED,publication=False)
 save(DOC/'qualification.json',qualification);save(DOC/'ROOT-IMAGE-INSPECTION.json',images);rows={r['uid']:r for r in ROWS}
 for m in cat['models']:
  r=rows[m['uid']];assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids');m.update(originalSourceKey=r['native']['cacheKey']+'/'+r['modelId'],sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceFunctionalApplicability=ref(DOC/'qualification.json'),sourceIdentityReview=ref(DOC/'qualification.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Unchanged original at1x; exact source identity and grade/ledge interpretations, all-mode complete foundations, current neighbours and exported desktop/mobile views verified. Raw strict diagnostics retained.')
  if m['uid']==TOWER:assert m['supportDependencies'][0]['uid']==PODIUM and m['supportDependencies'][0]['sha256']==SOURCES[PODIUM]
  else:assert not m.get('supportDependencies')
  p=STAGE/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(prior/m['asset'],p);assert ref(p)['sha256']==m['sha256']
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json')
 candidate=read(folder('assembly-terrain-candidate-v1')/'terrain-candidates.json')[0];check(dict(path=candidate['path'],sha256=candidate['sha256']));dest=STAGE/'government-native-orchards-original-v1-20261017.json';shutil.copyfile(ROOT/candidate['path'],dest)
 mesh=folder('assembly-neighbours-v1')/'native-neighbour-checks.json';report=read(mesh);assert report['aiCalls']==report['modelGeometryChanges']==0 and all(r['passed']for r in report['rows'])
 decision=dict(status='approved-for-integration',supersededURL=candidate['replaces']['url'],supersededSHA256=candidate['replaces']['sha256'],replacementSHA256=candidate['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=[RETAINED],replacementTargetUids=read(dest)['meta']['targetUids'],fullMeshCheck=ref(mesh),scope=ref(folder('assembly-terrain-candidate-v1')/'scope.json'))
 save(DOC/'native-replacement-review.json',decision)
 terrain=dict(source=str(dest.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+dest.name,resolution=5,area='Orchards original assembly terrain',replaces=candidate['replaces'],nativeReview=ref(DOC/'native-replacement-review.json'));url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='Orchards three unchanged originals',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=[terrain]))
 config=read(prior/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,terrain=[terrain]);config['captureDirectionByModel'][COMMUNITY]=[0,1.4,-.25];save(STAGE/'browser-config.json',config)
 pub=module('orchards_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for e in pins.values():check(e)
 r=module('orchards_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-three-original-qualified-stage-v1',[Path(__file__),PREVIOUS,*[ROOT/p for p in pins],*[p for p in STAGE.rglob('*')if p.is_file()]],dict(uids=list(SOURCES)+[RETAINED],privateStageQualified=True,publisherDryRunPassed=True,publication=False));print(r['jobId'],flush=True)
if __name__=='__main__':main()
