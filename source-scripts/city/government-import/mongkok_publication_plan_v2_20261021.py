"""Guarded one-source publication plan retaining the accepted opposite stadium stand."""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-qualified-publication-plan-v2-20261021';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;OLD=HERE/'local/government-xl-mongkok-staged-browser-v3-20261021'
NEW='landsd/240332:0';RETAINED='landsd/240527:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__)];pins={}
 def take(n,p):
  _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert ref(p)['sha256']==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
 n='government-xl-mongkok-source-review-v2-20261021';rp=BASE/n/'ROOT-SOURCE-REVIEW.json';review=take(n,rp);assert all(review[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
 for q in review['imagesActuallyViewed']+review['browserReports']:assert ref(ROOT/q['path'])==q;refs.append(ROOT/q['path'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==review['currentManifest'];before=read(manifest);after=copy.deepcopy(before);refs.append(manifest);pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';refs.append(pointer)
 old=[]
 for url in before['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;refs.append(p);old.extend(read(p)['models'])
 assert len(old)==len({m['uid']for m in old})==6832 and NEW not in {m['uid']for m in old}
 retained=next(m for m in old if m['uid']==RETAINED);assert retained['sha256']==review['sourceSHA256ByUid'][RETAINED]
 n='government-xl-mongkok-staged-browser-v3-20261021';cat=take(n,OLD/'catalogue.json');assert len(cat['models'])==1;entry=cat['models'][0];assert entry['uid']==NEW and entry['sha256']==review['sourceSHA256ByUid'][NEW] and not entry.get('supportDependencies')
 qualification={**review,'originalSourceReviewAccepted':True,'sourceReview':ref(rp),'installationApproved':False};save(DOC/'ROOT-SOURCE-REVIEW.json',qualification)
 entry.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,sourceIdentityReview=ref(rp),sourceFunctionalApplicability=ref(DOC/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Unchanged original stadium stand, fixed1x/source pose. Source-specific exact identity accepts original low access extension while preserving raw footprint extent diagnostics. Complete four-world foundations,66neighbours and retained opposite stand pass; desktop/mobile day/night, picking, collision and failed-download recovery reviewed.')
 src=OLD/entry['asset'];assert digest(src.read_bytes())==entry['sha256'];refs.append(src);p=STAGE/entry['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,p)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',take(n,OLD/'source-forms.json'))
 cfg=take(n,OLD/'browser-config-390.json');assert len(cfg['terrain'])==1;t=cfg['terrain'][0];p=ROOT/t['source'];patch=take('government-xl-mongkok-local-inset-v4-20261021',p);assert ref(p)['sha256']==t['sha256'];replacement=t['replaces'];oldurl='city/data/government-native-240527-0.json';assert replacement['url']==oldurl and replacement['retainedUids']==[RETAINED];oldpatch=ROOT/'3d-viewer'/oldurl;assert digest(oldpatch.read_bytes())==replacement['sha256'];refs.append(oldpatch)
 assert len([p for p in before['terrainPatches']if p['url']==oldurl])==1
 terrainurl='city/data/government-native-mongkok-original-v1-20261021.json';after['terrainPatches']=[p for p in before['terrainPatches']if p['url']!=oldurl]+[dict(area='Mong Kok Stadium original terrain',url=terrainurl,resolution=t['resolution'],bytes=p.stat().st_size,sha256=t['sha256'],source=patch['meta'])]
 url='city/data/official-models/'+BATCH+'/catalogue.json';after['officialModelCatalogues'].append(url);save(STAGE/'manifest.json',after)
 edits=[dict(destination='3d-viewer/'+url,beforeSHA256=None,source=ref(STAGE/'catalogue.json')),dict(destination='3d-viewer/'+terrainurl,beforeSHA256=None,source=ref(p)),dict(destination=str(manifest.relative_to(ROOT)),beforeSHA256=ref(manifest)['sha256'],source=ref(STAGE/'manifest.json'))]
 assets=[dict(destination='3d-viewer/'+url.rsplit('/',1)[0]+'/'+entry['asset'],source=ref(STAGE/entry['asset']))]
 previous=BASE/'government-xl-illumination-original-installed-v1-20261021/full-xl-current-count.json';delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['previousInstalled']==317 and delta['expectedFixedXLDelta']==1;refs.append(previous)
 cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url);cfg['terrain'][0]['destination']=terrainurl;save(STAGE/'live-browser-config.json',cfg)
 for e in edits+assets:
  dest=ROOT/e['destination'];assert(digest(dest.read_bytes())if dest.exists()else None)==e.get('beforeSHA256');assert ref(ROOT/e['source']['path'])==e['source']
 plan=dict(edits=edits,assets=assets,sourceSHA256ByUid={NEW:entry['sha256']},retainedSourceSHA256ByUid={RETAINED:retained['sha256']},newModels=[NEW],newVisibleModels=1,newRuntimeCount=6833,existingModelReverification=[RETAINED],delta=delta,previousXLCount=ref(previous),terrainChanges=1,terrainReplacements=[replacement],terrainDestination=terrainurl,currentManifest=ref(manifest),currentPointer=ref(pointer),sourceReview=ref(DOC/'ROOT-SOURCE-REVIEW.json'),publication=False)
 save(DOC/'publication-plan.json',plan)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([HERE/'upton_staged_image_review_binding_v1_20261014.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('stadium_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-qualified-terrain-replacement-publication-plan',list(dict.fromkeys(refs)),dict(uids=[NEW],qualifiedForLiveVerification=True,newVisibleModels=1,delta=delta,publication=False))
if __name__=='__main__':main()
