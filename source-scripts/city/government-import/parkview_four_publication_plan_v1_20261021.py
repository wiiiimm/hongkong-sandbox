"""Stage unchanged Parkview Blocks12–15 and reviewed terrain; requires completed source review."""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-four-qualified-publication-plan-v1-20261021';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;OLD=HERE/'local/government-xl-parkview-retained-mobile-v1-20261021'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__)];pins={}
 def take(n,p):
  _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert ref(p)['sha256']==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
 n='government-xl-parkview-four-source-review-v1-20261021';rp=BASE/n/'ROOT-SOURCE-REVIEW.json';review=take(n,rp)
 assert all(review[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
 for q in review['imagesActuallyViewed']+review['browserReports']:assert ref(ROOT/q['path'])==q;refs.append(ROOT/q['path'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==review['currentManifest'];before=read(manifest);after=copy.deepcopy(before);refs.append(manifest);pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';refs.append(pointer)
 old=[]
 for url in before['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;refs.append(p);old.extend(read(p)['models'])
 assert len(old)==len({m['uid']for m in old})==6826
 n='government-xl-parkview-retained-mobile-v1-20261021';cat=take(n,OLD/'catalogue.json');sources={m['uid']:m['sha256']for m in cat['models']};assert sources==review['sourceSHA256ByUid']and set(sources)=={'landsd/253980:0','landsd/255260:0','landsd/255648:0','landsd/255440:0'};assert not set(sources)&{m['uid']for m in old}
 qualification={**review,'originalSourceReviewAccepted':True,'sourceReview':ref(rp),'installationApproved':False};save(DOC/'ROOT-SOURCE-REVIEW.json',qualification)
 for m in cat['models']:
  assert m.get('supportDependencies')==[dict(uid='landsd/254491:0',state='installed',buildingCSUID='3860813197P20060312',sha256='8d1de7a507bedd3b321786220569d5ff4ee279496220bd1e5c93580411c7ad77')]
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,sourceIdentityReview=ref(rp),sourceFunctionalApplicability=ref(DOC/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Unchanged original at fixed1x/source pose. Exact source identities and source-specific native-podium physical review; actual terrain foundations and26form/11retained-original regression pass. Joint desktop/mobile views and individual download recovery reviewed. Raw contact and legacy negatives retained.')
  src=OLD/m['asset'];assert digest(src.read_bytes())==m['sha256'];refs.append(src);p=STAGE/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,p)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=4,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',take(n,OLD/'source-forms.json'))
 cfg=take(n,OLD/'browser-config-390.json');assert len(cfg['terrain'])==1;t=cfg['terrain'][0];replacement=t['replaces'];assert set(replacement['retainedUids'])==set(review['retainedUids']) and len(review['retainedUids'])==11;refs.append(ROOT/'3d-viewer'/replacement['url']);p=ROOT/t['source'];patch=take('government-xl-parkview-12-15-private-terrain-v2-20261021',p);assert ref(p)['sha256']==t['sha256'];assert digest((ROOT/'3d-viewer'/replacement['url']).read_bytes())==replacement['sha256'];assert len([e for e in before['terrainPatches']if e['url']==replacement['url']])==1
 terrainurl='city/data/government-native-parkview-four-original-v1-20261021.json';after['terrainPatches']=[e for e in before['terrainPatches']if e['url']!=replacement['url']]+[dict(area='Parkview Blocks12-15 original terrain',url=terrainurl,resolution=t['resolution'],bytes=p.stat().st_size,sha256=t['sha256'],source=patch['meta'])]
 url='city/data/official-models/'+BATCH+'/catalogue.json';after['officialModelCatalogues'].append(url);save(STAGE/'manifest.json',after)
 edits=[dict(destination='3d-viewer/'+url,beforeSHA256=None,source=ref(STAGE/'catalogue.json')),dict(destination='3d-viewer/'+terrainurl,beforeSHA256=None,source=ref(p)),dict(destination=str(manifest.relative_to(ROOT)),beforeSHA256=ref(manifest)['sha256'],source=ref(STAGE/'manifest.json'))]
 assets=[dict(destination='3d-viewer/'+url.rsplit('/',1)[0]+'/'+m['asset'],source=ref(STAGE/m['asset']))for m in cat['models']]
 previous=BASE/'government-xl-thei-original-installed-v1-20261021/full-xl-current-count.json';delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==315 and delta['expectedFixedXLDelta']==1;refs.append(previous)
 cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url);cfg['terrain'][0]['destination']=terrainurl;save(STAGE/'live-browser-config.json',cfg)
 for e in edits+assets:
  dest=ROOT/e['destination'];assert(digest(dest.read_bytes())if dest.exists()else None)==e.get('beforeSHA256');assert ref(ROOT/e['source']['path'])==e['source']
 plan=dict(edits=edits,assets=assets,sourceSHA256ByUid=sources,newModels=sorted(sources),newVisibleModels=4,newRuntimeCount=6830,existingModelReverification=[],delta=delta,previousXLCount=ref(previous),terrainChanges=1,terrainReplacements=[replacement],terrainDestination=terrainurl,currentManifest=ref(manifest),currentPointer=ref(pointer),sourceReview=ref(DOC/'ROOT-SOURCE-REVIEW.json'),publication=False)
 save(DOC/'publication-plan.json',plan)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([HERE/'upton_staged_image_review_binding_v1_20261014.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('piers_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-qualified-terrain-replacement-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(sources),qualifiedForLiveVerification=True,newVisibleModels=4,delta=delta,publication=False))
if __name__=='__main__':main()
