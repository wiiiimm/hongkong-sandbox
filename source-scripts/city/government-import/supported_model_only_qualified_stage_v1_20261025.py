"""Prepare the reviewed co-imported supported originals with zero-contact retained natives; preserve current native entries."""
from pathlib import Path
import copy,shutil,sys,os
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope
from original_supported_model_only_contract_v1_20261025 import verify_metadata as metadata_contract,verify_native_scope as native_contract,verify_browser_native_scope
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import'
CONFIGPATH=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve()
assert CONFIGPATH.is_relative_to(BASE)
CONFIG=read(CONFIGPATH)
assert CONFIG['prefix'].startswith('government-xl-')and'/'not in CONFIG['prefix']and CONFIG['supportByUid'] and CONFIG['retainedNativeUids']==[]
SOURCES=CONFIG['sources'];SUPPORTS=CONFIG['supportByUid']
ORIGINAL_ENTRIES={r['uid']:r['candidate']['entry']for r in read(BASE/CONFIG['originalSelection']/'selection.json.gz')['rows']}
assert set(ORIGINAL_ENTRIES)==set(SOURCES)
def verify_metadata(models):return metadata_contract(models,SOURCES,SUPPORTS,ORIGINAL_ENTRIES)
def verify_native_scope(scope,native,current):return native_contract(scope,native,current,SOURCES,set(CONFIG['retainedNativeUids']),CONFIG['currentNativeActors'])
BATCH=CONFIG['prefix']+'-qualified-stage-v1-'+CONFIG['date'];DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PREVIOUS=HERE/'local'/CONFIG['browser'];SOURCE=BASE/CONFIG['review']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__),CONFIGPATH];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 original=take(CONFIG['originalSelection'],BASE/CONFIG['originalSelection']/'selection.json.gz');assert {r['uid']:r['candidate']['entry']for r in original['rows']}==ORIGINAL_ENTRIES
 review=take(SOURCE.name,SOURCE/'ROOT-SOURCE-REVIEW.json');assert all(review[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance']);sources=review['sourceSHA256ByUid'];assert sources==CONFIG['sources']==SOURCES and CONFIG['supportByUid']==SUPPORTS
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert ref(manifest)==review['currentManifest'];refs.extend([manifest,pointer]);models=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(models)==len({m['uid']for m in models})==CONFIG['currentNativeActors'] and not set(sources)&{m['uid']for m in models}
 browser=CONFIG['browser'];cat=take(browser,PREVIOUS/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources;cfg=take(browser,PREVIOUS/'browser-config-390.json');forms=take(browser,PREVIOUS/'validation-forms.json');assert cfg['terrain']==[] and not cfg.get('estimatedBaseUpdates')
 scope=take(CONFIG['scope'],BASE/CONFIG['scope']/'summary.json');assert scope['currentManifestSHA256']==ref(manifest)['sha256']and set(sources)<=set(scope['uids'])
 scope={**scope,'uids':sorted(sources),'rows':[r for r in scope['rows']if r['uid']in sources]};assert len(scope['rows'])==len(sources)
 browser_reports=[take(browser,BASE/browser/str(w)/'staged-browser.json')for w in [1280,390]]
 assert verify_browser_native_scope(cfg,SUPPORTS,SOURCES,CONFIG['retainedNativeUids'],browser_reports)
 native=take(CONFIG['nativeContacts'],BASE/CONFIG['nativeContacts']/'summary.json');native={**native,'rows':[r for r in native['rows']if r['uid']in sources]};assert verify_native_scope(scope,native,{m['uid']:m for m in models})
 for url in read(manifest)['officialModelCatalogues']:
  current=ROOT/'3d-viewer'/url
  if any(m['uid']in {r['nativeUid']for r in native['rows']}for m in read(current)['models']):
   refs.append(current)
   for m in read(current)['models']:
    if m['uid']in {r['nativeUid']for r in native['rows']}:
     asset=(current.parent/m['asset']).resolve();assert digest(asset.read_bytes())==m['sha256'];refs.append(asset)
 obligations={}
 for r in scope['rows']:
  assert r['currentNativeActorsChecked']==CONFIG['currentNativeActors']
  for form in take(CONFIG['scope'],BASE/CONFIG['scope']/(r['uid'].split('/')[1]+'-forms.json.gz')):obligations[form['building']['uid']]=form['building']
 resources=['building:'+u for u in obligations];assert len(obligations)==CONFIG['neighbourForms']
 physical=take(CONFIG['physical'],BASE/CONFIG['physical']/'ROOT-PHYSICAL-REVIEW.json');assert physical['supportByUid']==CONFIG['supportByUid']and physical['requiredOriginalAssembly']==sources and set(resources)==set(physical['leaseResources'])
 assert verify_support_scope(cat['models'],sources,CONFIG['supportByUid'])and verify_metadata(cat['models'])
 qualification={**review,'privateStageQualified':True,'originalSourceReviewAccepted':True,'sourceReview':ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),'leaseResources':sorted(set(resources)),'publication':False};save(DOC/'qualification.json',qualification)
 for m in cat['models']:
  assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
  assert m.get('supportDependencies',[])==next(x for x in read(PREVIOUS/'catalogue.json')['models']if x['uid']==m['uid']).get('supportDependencies',[])
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview=CONFIG['placementReview'])
  p=PREVIOUS/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p);dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=len(sources),catalogues=['catalogue.json']));save(STAGE/'source-forms.json',forms)
 assert physical['terrainEdits']is False;terrain=[]
 url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=CONFIG['label'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=terrain))
 cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=url,terrain=terrain);save(STAGE/'live-browser-config.json',cfg)
 deps=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
 for path,h in deps['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 previous=BASE/CONFIG['previousCountReport'];delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==CONFIG['previousInstalled'] and delta['expectedFixedXLDelta']==CONFIG['expectedFixedXLDelta'];refs.append(previous);save(DOC/'fixed-xl-delta.json',delta)
 pub=module('selected_original_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 required_paths={str(r.relative_to(ROOT))for r in refs}
 for p,h in {key:value for pins in cache.values()for key,value in pins.items()if key in required_paths}.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([HERE/'original_supported_model_only_contract_v1_20261025.py',HERE/'original_independent_model_only_contract_v1_20261024.py',HERE/'original_supported_catalogue_scope_v1_20261024.py',HERE/'dependency_preflight.py',HERE/'upton_staged_image_review_binding_v1_20261014.py',HERE.parent/'island-detail-integration/publish.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('selected_original_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-supported-model-only-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSHA256ByUid=sources,qualifiedForLiveVerification=True,delta=delta,newVisibleModels=len(sources),newRuntimeCount=CONFIG['currentNativeActors']+len(sources),publication=False));print(dict(models=len(sources),fixedXLDelta=CONFIG['expectedFixedXLDelta'],publication=False),flush=True)
if __name__=='__main__':main()
