"""Prepare the reviewed four originals with an atomic coordinated terrain pair; dry run."""
from pathlib import Path
import copy,shutil,sys,os
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
from retained_native_nonregression_v1_20261023 import terrain_decision
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import'
CONFIGPATH=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve()
assert CONFIGPATH.is_relative_to(BASE)
CONFIG=read(CONFIGPATH)
assert CONFIG['prefix'].startswith('government-xl-') and '/' not in CONFIG['prefix']
BATCH=CONFIG['prefix']+'-coordinated-qualified-stage-v1-'+CONFIG['date'];DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PREVIOUS=HERE/'local'/CONFIG['browser'];SOURCE=BASE/CONFIG['review']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__),CONFIGPATH];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 review=take(SOURCE.name,SOURCE/'ROOT-SOURCE-REVIEW.json');assert all(review[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance']);sources=review['sourceSHA256ByUid'];assert sources==CONFIG['sources']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert ref(manifest)==review['currentManifest'];refs.extend([manifest,pointer]);models=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(models)==len({m['uid']for m in models})==CONFIG['currentNativeActors'] and not set(sources)&{m['uid']for m in models}
 browser=CONFIG['browser'];cat=take(browser,PREVIOUS/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources;cfg=take(browser,PREVIOUS/'browser-config-390.json');forms=take(browser,PREVIOUS/'validation-forms.json');assert len(cfg['terrain'])==2 and not cfg.get('estimatedBaseUpdates')
 obligations=take(CONFIG['scope'],BASE/CONFIG['scope']/'form-obligations.json.gz');resources=[('building:' if b['uid'].startswith('landsd/') else 'source-form:')+b['uid']for b in obligations]+['terrain:city/data/terrain.json'];assert len(obligations)==CONFIG['neighbourForms']
 physical=take(CONFIG['physical'],BASE/CONFIG['physical']/'ROOT-PHYSICAL-REVIEW.json')
 replacements=physical['exactTerrainReplacements'];assert len(replacements)==2 and [e['replaces']for e in cfg['terrain']]==replacements
 retainedTargets=set()
 for replacement in replacements:
  oldpath=ROOT/'3d-viewer'/replacement['url'];assert ref(oldpath)['sha256']==replacement['sha256'];refs.append(oldpath)
  assert set(read(oldpath)['meta']['targetUids'])==set(replacement['retainedUids'])
  retainedTargets.update(replacement['retainedUids'])
  resources.append('terrain:'+replacement['url'])
 assert retainedTargets<=set(physical['retainedNativeRegression']['requiredNativeUids'])
 resources+=['building:'+u for u in set(physical['retainedNativeRegression']['requiredNativeUids'])|set(sources)]
 qualification=dict(**review,privateStageQualified=True,originalSourceReviewAccepted=True,sourceReview=ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),leaseResources=sorted(set(resources)),publication=False);save(DOC/'qualification.json',qualification)
 for m in cat['models']:
  assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
  expected=CONFIG['supportByUid'].get(m['uid'])
  if expected:
   parent=next(r for r in cat['models']if r['uid']==expected)
   assert m.get('supportDependencies')==[dict(uid=expected,state='installed',csuid=parent['buildingCSUID'],sha256=sources[expected])]
  else:assert not m.get('supportDependencies')
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview=CONFIG['placementReview'])
  p=PREVIOUS/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p);dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=len(sources),catalogues=['catalogue.json']));save(STAGE/'source-forms.json',forms)
 terrain=copy.deepcopy(cfg['terrain'])
 for number,entry in enumerate(terrain):
  source=ROOT/entry['source'];assert ref(source)['sha256']==entry['sha256'];refs.append(source);dest=STAGE/('original-terrain-'+str(number)+'.json');shutil.copyfile(source,dest)
  entry.update(source=str(dest.relative_to(ROOT)),destination=CONFIG['terrainDestinations'][number],area=CONFIG['label'])
  assert entry['replaces']==replacements[number]
  assert set(read(dest)['meta']['targetUids'])==set(replacements[number]['retainedUids'])|set(sources)
 integration=HERE.parent/'island-detail-integration'
 if str(integration)not in sys.path:sys.path.insert(0,str(integration))
 from coordinated_native_boundary import validate_effective_coordinated_members
 validate_effective_coordinated_members([read(ROOT/e['source'])for e in terrain]);refs.append(integration/'coordinated_native_boundary.py')
 nativebatch=CONFIG['nativeNeighbours'];native=take(nativebatch,BASE/nativebatch/'summary.json')
 assert not native['basicFlags'] and set(native['requiredNativeUids'])=={r['uid']for r in native['nativeRows']}
 assert set(native['nativeResolved'])=={r['uid']for r in native['nativeRows']if r['passed']}
 assert set(native['requiredNativeUids'])==set(physical['retainedNativeRegression']['requiredNativeUids'])
 assert CONFIG['supportByUid']=={'landsd/20270:0':'landsd/159422:0','landsd/274231:0':'landsd/269430:0'}
 assert physical['retainedNativeRegression']['rawNativeFailures']==['landsd/177605:0']
 contextName=CONFIG['unchangedNativeContext'];context=take(contextName,BASE/contextName/'summary.json')
 assert context['nativeUid']=='landsd/177605:0' and context['supportUid']=='landsd/177604:0'
 contextPins=cache[contextName]
 for tested,entry in zip(cfg['terrain'],terrain):
  source=ROOT/tested['source'];assert contextPins[str(source.relative_to(ROOT))]==tested['sha256']==ref(source)['sha256'];refs.append(source)
  assert read(source)['nativeMesh']['position']==read(ROOT/entry['source'])['nativeMesh']['position']and read(source)['nativeMesh']['index']==read(ROOT/entry['source'])['nativeMesh']['index']
 installed={m['uid']:m for m in models};decisions=[]
 for row in native['nativeRows']:
  assert row['terrain']['newlyWhollyBuried']==row['terrain']['newlyUpwardWhollyBuried']==0
  decisions.append(copy.deepcopy(row)if row['passed'] else terrain_decision(row,context,installed))
 assert sum(not r['passed']for r in native['nativeRows'])==1 and all(r['passed']for r in decisions)
 assert set(cfg['additionalRetainedUids'])==retainedTargets
 refs.append(HERE/'retained_native_nonregression_v1_20261023.py')
 meshcheck=DOC/'native-neighbour-checks.json';save(meshcheck,dict(rows=decisions,rawNativeRows=native['nativeRows'],aiCalls=0,modelGeometryChanges=0,rawReport=ref(BASE/nativebatch/'summary.json')))
 for number,(replacement,entry)in enumerate(zip(replacements,terrain)):
  nativeReview=DOC/('native-replacement-review-'+str(number)+'.json')
  save(nativeReview,dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=entry['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=replacement['retainedUids'],replacementTargetUids=read(ROOT/entry['source'])['meta']['targetUids'],fullMeshCheck=ref(meshcheck),qualification='Exact paired terrain/source identities, every retained target and all current actor decisions are bound. Legacy raw support negative remains false under exact complete-bounds terrain nonregression; no source reacceptance. Both coordinated members are required.'))
  entry['nativeReview']=ref(nativeReview)
 url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=CONFIG['label'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=terrain))
 cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=url,terrain=terrain);save(STAGE/'live-browser-config.json',cfg)
 deps=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
 for path,h in deps['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 previous=BASE/CONFIG['previousCountReport'];delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==CONFIG['previousInstalled'] and delta['expectedFixedXLDelta']==CONFIG['expectedFixedXLDelta'];refs.append(previous);save(DOC/'fixed-xl-delta.json',delta)
 pub=module('selected_original_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 # Build membership once; still rehash every required direct reference.
 required_paths={str(r.relative_to(ROOT))for r in refs}
 for p,h in {key:value for pins in cache.values()for key,value in pins.items()if key in required_paths}.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([HERE/'dependency_preflight.py',HERE/'upton_staged_image_review_binding_v1_20261014.py',HERE.parent/'island-detail-integration/publish.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('selected_original_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-assembly-coordinated-terrain-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSHA256ByUid=sources,qualifiedForLiveVerification=True,delta=delta,newVisibleModels=len(sources),newRuntimeCount=CONFIG['currentNativeActors']+len(sources),publication=False));print(dict(models=len(sources),fixedXLDelta=CONFIG['expectedFixedXLDelta'],publication=False),flush=True)
if __name__=='__main__':main()
