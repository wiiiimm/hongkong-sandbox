"""Prepare reviewed original towers retaining exact basic supports; no terrain edits."""
from pathlib import Path
import copy,shutil,sys,os
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import'
CONFIGPATH=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve()
assert CONFIGPATH.is_relative_to(BASE)
CONFIG=read(CONFIGPATH)
assert CONFIG['prefix'].startswith('government-xl-') and '/' not in CONFIG['prefix']
BATCH=CONFIG['prefix']+'-qualified-stage-v3-'+CONFIG['date'];DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PREVIOUS=HERE/'local'/CONFIG['browser'];SOURCE=BASE/CONFIG['review']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def expected_dependencies(uid,review,include_basic=True):
 sources=CONFIG['sources'];assert len(sources)==1 and uid in sources and review['sourceSHA256ByUid']==sources
 graph=CONFIG['nativeAvailabilityDependenciesByUid'];assert set(graph)==set(sources)and review['runtimeAvailabilityDependenciesByUid']==graph
 parent=graph[uid];retained=review['retainedNativeEntries'];assert parent in retained and parent not in sources
 bindings=[d for d in review['retainedBasicSupportDependencies']if d['uid']==uid];assert len(bindings)==1
 binding=bindings[0];assert binding['sourceSHA256']==sources[uid]and binding['mustRemainBasicAndUnsuppressed']is True and binding['futureReplacementRequiresDependentRevalidation']is True
 support=binding['supportUid'];assert support not in sources and support!=parent and support not in retained
 deps=[dict(uid=parent,state='installed',buildingCSUID=retained[parent]['buildingCSUID'],sha256=retained[parent]['sha256'])]
 if include_basic:deps.append(dict(uid=support,state='surveyed-footprint-fallback'))
 return deps

def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__),CONFIGPATH];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 review=take(SOURCE.name,SOURCE/'ROOT-SOURCE-REVIEW.json');assert all(review[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance']);sources=review['sourceSHA256ByUid'];assert sources==CONFIG['sources']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert ref(manifest)==review['currentManifest'];refs.extend([manifest,pointer]);models=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(models)==len({m['uid']for m in models})==CONFIG['currentNativeActors'] and not set(sources)&{m['uid']for m in models}
 browser=CONFIG['browser'];cat=take(browser,PREVIOUS/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources;cfg=take(browser,PREVIOUS/'browser-config-390.json');forms=take(browser,PREVIOUS/'validation-forms.json');assert cfg['terrain']==[] and not cfg.get('estimatedBaseUpdates')
 resources=review['leaseResources'];assert review['terrainEdits'] is False
 from finite_basic_native_admission_v2_20261025 import replay
 refs.extend(replay(CONFIG,review))
 qualification={**review,'privateStageQualified':True,'originalSourceReviewAccepted':True,'sourceReview':ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),'leaseResources':sorted(set(resources)),'publication':False};save(DOC/'qualification.json',qualification)
 for m in cat['models']:
  assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
  assert m.get('supportDependencies')==expected_dependencies(m['uid'],review,include_basic=False)
  dependencies=[d for d in review['retainedBasicSupportDependencies'] if d['uid']==m['uid']];assert len(dependencies)==1
  m['retainedBasicSupportDependencies']=dependencies
  m['supportDependencies']=expected_dependencies(m['uid'],review)
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview=CONFIG['placementReview'])
  p=PREVIOUS/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p);dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=len(sources),catalogues=['catalogue.json']));save(STAGE/'source-forms.json',forms)
 terrain=[]
 url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=CONFIG['label'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=terrain))
 cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=url,terrain=terrain);save(STAGE/'live-browser-config.json',cfg)
 deps=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
 for path,h in deps['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 previous=BASE/CONFIG['previousCountReport'];delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==CONFIG['previousInstalled'] and delta['expectedFixedXLDelta']==CONFIG['expectedFixedXLDelta'];refs.append(previous);save(DOC/'fixed-xl-delta.json',delta)
 pub=module('selected_original_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 required_paths={str(r.relative_to(ROOT))for r in refs}
 for p,h in {key:value for pins in cache.values()for key,value in pins.items()if key in required_paths}.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([HERE/'selected_original_finite_basic_native_publish_v2_20261026.py',HERE/'selected_original_finite_basic_native_install_v2_20261026.py',HERE/'dependency_preflight.py',HERE/'upton_staged_image_review_binding_v1_20261014.py',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/retained_basic_support.py',HERE/'finite_basic_native_installed_readback_v2_20261026.py',HERE/'test_finite_basic_native_stage_v2_20261026.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('selected_original_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-assembly-terrain-estimate-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSHA256ByUid=sources,qualifiedForLiveVerification=True,delta=delta,newVisibleModels=len(sources),newRuntimeCount=CONFIG['currentNativeActors']+len(sources),publication=False));print(dict(models=len(sources),fixedXLDelta=CONFIG['expectedFixedXLDelta'],publication=False),flush=True)
if __name__=='__main__':main()
