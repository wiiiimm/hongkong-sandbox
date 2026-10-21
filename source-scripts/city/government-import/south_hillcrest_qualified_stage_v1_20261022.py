"""Prepare the reviewed original South Hillcrest assembly and terrain; dry run."""
from pathlib import Path
import copy,shutil,sys
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import from_catalogues
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-south-hillcrest-qualified-stage-v1-20261022';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PREVIOUS=HERE/'local/government-xl-south-hillcrest-staged-browser-v1-20261022';SOURCE=BASE/'government-xl-south-hillcrest-source-review-v1-20261022';POD='landsd/259604:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 review=take(SOURCE.name,SOURCE/'ROOT-SOURCE-REVIEW.json');assert all(review[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance']);sources=review['sourceSHA256ByUid'];assert set(sources)=={'landsd/198440:0',POD}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert ref(manifest)==review['currentManifest'];refs.extend([manifest,pointer]);models=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(models)==len({m['uid']for m in models})==6836 and not set(sources)&{m['uid']for m in models}
 browser='government-xl-south-hillcrest-staged-browser-v1-20261022';cat=take(browser,PREVIOUS/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources;cfg=take(browser,PREVIOUS/'browser-config-390.json');forms=take(browser,PREVIOUS/'validation-forms.json');assert len(cfg['terrain'])==1 and not cfg.get('estimatedBaseUpdates')
 obligations=take('government-xl-south-hillcrest-private-original-scope-v2-20261022',BASE/'government-xl-south-hillcrest-private-original-scope-v2-20261022/form-obligations.json.gz');resources=['building:'+b['uid']for b in obligations]+['terrain:city/data/terrain.json'];assert len(obligations)==54
 qualification=dict(**review,privateStageQualified=True,originalSourceReviewAccepted=True,sourceReview=ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),leaseResources=sorted(set(resources)),publication=False);save(DOC/'qualification.json',qualification)
 for m in cat['models']:
  assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids')
  if m['uid']!=POD:assert m['supportDependencies']==[dict(uid=POD,state='installed',buildingCSUID=next(e for e in cat['models']if e['uid']==POD)['buildingCSUID'],sha256=sources[POD])]
  else:assert not m.get('supportDependencies')
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(SOURCE/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview='Unchanged original at fixed1x/source pose. The exact original tower and podium form one reviewed assembly. Complete four-coordinate foundations and strict/finite contacts plus all54form obligations checked; source-specific wall-ground findings retain raw flags. Desktop/mobile day/night,picking,collision,joint activation and individual failure/retry passed.')
  p=PREVIOUS/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p);dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',forms)
 terrain=copy.deepcopy(cfg['terrain']);entry=terrain[0];source=ROOT/entry['source'];assert ref(source)['sha256']==entry['sha256'];refs.append(source);dest=STAGE/'original-terrain.json';shutil.copyfile(source,dest);entry.update(source=str(dest.relative_to(ROOT)),destination='city/data/government-native-south-hillcrest-original-v1-20261022.json',area='South Hillcrest Garden original government terrain')
 url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='South Hillcrest Garden original government assembly',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)],topLevelTerrainPatches=terrain))
 cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=url,terrain=terrain);save(STAGE/'live-browser-config.json',cfg)
 deps=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps)
 for path,h in deps['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 previous=BASE/'government-xl-ronsdale-original-installed-v3-20261022/full-xl-current-count.json';delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==320 and delta['expectedFixedXLDelta']==1;refs.append(previous);save(DOC/'fixed-xl-delta.json',delta)
 pub=module('south_hillcrest_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for p,h in {key:value for pins in cache.values()for key,value in pins.items()if key in {str(r.relative_to(ROOT))for r in refs}}.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([HERE/'dependency_preflight.py',HERE/'upton_staged_image_review_binding_v1_20261014.py',HERE.parent/'island-detail-integration/publish.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('south-hillcrest_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-assembly-terrain-estimate-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSHA256ByUid=sources,qualifiedForLiveVerification=True,delta=delta,newVisibleModels=2,newRuntimeCount=6838,publication=False));print(dict(models=2,fixedXLDelta=1,publication=False),flush=True)
if __name__=='__main__':main()
