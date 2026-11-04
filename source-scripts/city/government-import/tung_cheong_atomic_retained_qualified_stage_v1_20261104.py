"""Stage only the exact reviewed atomic Tung Cheong pair; canonical dry run.

Based on the retained-original v4 stage. The unchanged terrain remains owned
by its reviewed high source; the separately grounded companion is atomic only.
All original publisher/retained-source/global-support checks remain required.
"""
from exact_single_terrain_replacement_v1_20261102 import replacement as canonical_replacement
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
BATCH=CONFIG['prefix']+'-atomic-retained-qualified-stage-v1-'+CONFIG['date'];DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PREVIOUS=HERE/'local'/CONFIG['browser'];SOURCE=BASE/CONFIG['review']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__),CONFIGPATH];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 review=take(SOURCE.name,SOURCE/'ROOT-SOURCE-REVIEW.json');assert all(review[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance']);sources=review['sourceSHA256ByUid'];assert sources==CONFIG['sources'];assert sources=={'landsd/53799:0':'9bcebd56adced618cad3251df6bae41191b515aa6153986c85e1eed0b1585c49','landsd/223636:0':'b980c1f30da1c162f1e961eb8c17df7b64fde72de89de59d5add13ab24c86eda'};assert review['compoundIdentityAccepted']is True and review['standaloneLowSourceIdentityAccepted']is False and review['activationGroupRequired']is True;assert review['terrainGroundOwnerUids']==['landsd/53799:0']and review['unchangedSurfaceCompanionUids']==['landsd/223636:0']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert ref(manifest)==review['currentManifest'];refs.extend([manifest,pointer]);models=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(models)==len({m['uid']for m in models})==CONFIG['currentNativeActors'] and not set(sources)&{m['uid']for m in models}
 browser=CONFIG['browser'];cat=take(browser,PREVIOUS/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources;cfg=take(browser,PREVIOUS/'browser-config-390.json');forms=take(browser,PREVIOUS/'validation-forms.json');assert len(cfg['terrain'])==1 and not cfg.get('estimatedBaseUpdates')
 obligations=take(CONFIG['scope'],BASE/CONFIG['scope']/'form-obligations.json.gz');resources=[('building:' if b['uid'].startswith('landsd/') else 'source-form:')+b['uid']for b in obligations]+['terrain:city/data/terrain.json'];assert len(obligations)==CONFIG['neighbourForms']
 physical=take(CONFIG['physical'],BASE/CONFIG['physical']/'ROOT-PHYSICAL-REVIEW.json')
 replacement=physical['exactTerrainReplacement'];assert canonical_replacement(cfg['terrain'][0])==replacement
 oldpath=ROOT/'3d-viewer'/replacement['url'];assert ref(oldpath)['sha256']==replacement['sha256'];refs.append(oldpath)
 assert set(read(oldpath)['meta']['targetUids'])==set(replacement['retainedUids'])
 assert set(replacement['retainedUids'])<=set(physical['retainedNativeRegression']['requiredNativeUids'])
 resources+=['terrain:'+replacement['url']]+['building:'+u for u in physical['retainedNativeRegression']['requiredNativeUids']]
 qualification={**review,'privateStageQualified':True,'originalSourceReviewAccepted':True,'sourceReview':ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),'leaseResources':sorted(set(resources)),'publication':False};save(DOC/'qualification.json',qualification)
 for m in cat['models']:
  assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
  assert not m.get('supportDependencies'), 'Both exact originals have separately verified terrain contact; do not invent a native dependency'
  assert m['activationGroup']==sorted(sources), 'The unmatched low original is qualified only with this exact tower'
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview=CONFIG['placementReview'])
  p=PREVIOUS/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p);dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=len(sources),catalogues=['catalogue.json']));save(STAGE/'source-forms.json',forms)
 terrain=copy.deepcopy(cfg['terrain']);entry=terrain[0];assert canonical_replacement(entry)==replacement;entry.pop('replacesMany',None);entry['replaces']=replacement;source=ROOT/entry['source'];assert ref(source)['sha256']==entry['sha256'];refs.append(source);dest=STAGE/'original-terrain.json';shutil.copyfile(source,dest);entry.update(source=str(dest.relative_to(ROOT)),destination=CONFIG['terrainDestination'],area=CONFIG['label'])
 assert entry['replaces']==replacement
 assert physical==review and physical['requiredOriginalAssembly']==sources
 assert set(read(dest)['meta']['targetUids'])==set(replacement['retainedUids'])|{'landsd/53799:0'}
 assert read(dest)==read(source), 'Keep exact fully validated terrain and existing ownership metadata'
 nativebatch=CONFIG['nativeNeighbours'];native=take(nativebatch,BASE/nativebatch/'summary.json')
 assert not native['basicFlags'] and set(native['requiredNativeUids'])==set(native['nativeResolved'])
 assert set(native['requiredNativeUids'])==set(physical['retainedNativeRegression']['requiredNativeUids'])
 assert all(r['passed'] and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['nativeRows'])
 meshcheck=DOC/'native-neighbour-checks.json';save(meshcheck,dict(rows=native['nativeRows'],aiCalls=0,modelGeometryChanges=0,rawReport=ref(BASE/nativebatch/'summary.json')))
 nativeReview=DOC/'native-replacement-review.json'
 save(nativeReview,dict(status='approved-for-integration',supersededURL=replacement['url'],supersededSHA256=replacement['sha256'],replacementSHA256=entry['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=replacement['retainedUids'],replacementTargetUids=read(dest)['meta']['targetUids'],fullMeshCheck=ref(meshcheck),qualification='Exact old terrain/source identities and every retained target are bound. Complete scoped ordinary and native mesh regressions passed. Existing model metadata/negative flags remain unchanged. No AI geometry modelling.'))
 entry['nativeReview']=ref(nativeReview)
 url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=CONFIG['label'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=terrain))
 cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=url,terrain=terrain);save(STAGE/'live-browser-config.json',cfg)
 deps=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
 for path,h in deps['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 previous=BASE/CONFIG['previousCountReport'];delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==CONFIG['previousInstalled'] and delta['expectedFixedXLDelta']==CONFIG['expectedFixedXLDelta'];refs.append(previous);save(DOC/'fixed-xl-delta.json',delta)
 pub=module('selected_original_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];
 from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators
 with complete_boundary_validators():pub.main()
 assert not read(pub.DOC/'publication-plan.json')['published']
 for p,h in {key:value for pins in cache.values()for key,value in pins.items()if key in {str(r.relative_to(ROOT))for r in refs}}.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([HERE/'fuying_five_member_terrain_stage_v1_20261029.py',HERE/'fuying_whole_parent_five_boundary_v1_20261029.py',HERE/'three_member_native_boundary_v1_20261027.py',HERE/'exact_single_terrain_replacement_v1_20261102.py',HERE/'test_exact_single_terrain_replacement_v1_20261102.py',HERE/'dependency_preflight.py',HERE/'upton_staged_image_review_binding_v1_20261014.py',HERE.parent/'island-detail-integration/publish.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('selected_original_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-assembly-terrain-estimate-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSHA256ByUid=sources,qualifiedForLiveVerification=True,delta=delta,newVisibleModels=len(sources),newRuntimeCount=CONFIG['currentNativeActors']+len(sources),publication=False));print(dict(models=len(sources),fixedXLDelta=CONFIG['expectedFixedXLDelta'],publication=False),flush=True)
if __name__=='__main__':main()
