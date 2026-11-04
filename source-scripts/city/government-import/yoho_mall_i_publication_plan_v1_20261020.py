"""Stage eight immutable originals and an exact reviewed terrain replacement; no publication."""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-qualified-publication-plan-v1-20261020';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;OLD=HERE/'local/government-xl-yoho-mall-i-private-browser-v4-20261020'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists() and not STAGE.exists();refs=[Path(__file__)];receipts={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for n in ['source-review-v2','neighbour-review-v3','private-browser-v4','private-terrain-v1','regional-scope-v1']:
   p=BASE/('government-xl-yoho-mall-i-'+n+'-20261020')/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);receipts[n]={e['path']:e['sha256']for e in r['evidenceRefs']};refs.append(p)
 def bound(n,p):
  assert digest(p.read_bytes())==receipts[n][str(p.relative_to(ROOT))],str(p);refs.append(p);return read(p)
 reviewpath=BASE/'government-xl-yoho-mall-i-source-review-v2-20261020/ROOT-SOURCE-REVIEW.json';review=bound('source-review-v2',reviewpath)
 assert all(review[k] for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','foreignContactContextAccepted','visualAcceptance'])
 # Recheck every consumed exact review/image/report, without treating historical mutable module bytes as current inputs.
 for q in review['imagesActuallyViewed']+review['browserReports']:
  assert ref(ROOT/q['path'])==q;refs.append(ROOT/q['path'])
 nearpath=BASE/'government-xl-yoho-mall-i-neighbour-review-v3-20261020/ROOT-NEIGHBOUR-REVIEW.json';near=bound('neighbour-review-v3',nearpath);assert near['sourceSpecificNeighbourInterpretationAccepted']and not near['remainingNeighbourFailures']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==review['currentManifest'];before=read(manifest);after=copy.deepcopy(before);refs.append(manifest)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==near['currentSnapshotId'];refs.append(pointer)
 cat=bound('private-browser-v4',OLD/'catalogue.json');models=cat['models'];sources={m['uid']:m['sha256']for m in models};assert len(models)==8 and sources==review['sourceSHA256ByUid']
 allold=[]
 for url in before['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;refs.append(p);allold.extend(read(p)['models'])
 assert len(allold)==len({m['uid']for m in allold})==6782 and not(set(sources)&{m['uid']for m in allold})
 current={m['uid']:m for m in allold}
 # The neighbour review already binds these installed originals; retain their exact catalogue bytes in this plan.
 assert len(near['checkedNativeUids'])==7 and all(u in current for u in near['checkedNativeUids'])
 qualification={**review,'originalSourceReviewAccepted':True,'sourceReview':ref(reviewpath),'neighbourReview':ref(nearpath),'installationApproved':False,'publication':False}
 save(DOC/'ROOT-SOURCE-REVIEW.json',qualification)
 for m in models:
  m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,sourceIdentityReview=ref(reviewpath),sourceFunctionalApplicability=ref(DOC/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Immutable original geometry at fixed1x/source pose. Exact original identity, complete four-mode foundations and source-specific contact review; entire terrain-replacement neighbour scope and desktop/mobile browser evidence. Raw warnings retained in the bound review.')
  for dep in m['supportDependencies']:
   assert dep['uid']=='landsd/189427:0'and dep['sha256']==sources[dep['uid']];dep['state']='installed'
  p=STAGE/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/m['asset'],p);assert digest(p.read_bytes())==m['sha256']
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=8,catalogues=['catalogue.json']));shutil.copyfile(OLD/'source-forms.json',STAGE/'source-forms.json')
 config=bound('private-browser-v4',OLD/'browser-config-390.json');terrain=config['terrain'];assert len(terrain)==1;t=terrain[0];patchpath=ROOT/t['source'];patch=bound('private-terrain-v1',patchpath);assert ref(patchpath)['sha256']==t['sha256']
 replacement=t['replaces'];assert set(replacement['retainedUids'])==set(near['checkedNativeUids']);oldpatch=[p for p in before['terrainPatches']if p['url']==replacement['url']];assert len(oldpatch)==1 and oldpatch[0]['sha256']==replacement['sha256'];assert digest((ROOT/'3d-viewer'/replacement['url']).read_bytes())==replacement['sha256'];refs.append(ROOT/'3d-viewer'/replacement['url'])
 terrainurl='city/data/government-native-yoho-mall-i-original-v1-20261020.json';newpatch=dict(area='Yoho Mall I and Grand Yoho original assembly',url=terrainurl,resolution=t['resolution'],bytes=patchpath.stat().st_size,sha256=t['sha256'],source=patch['meta'])
 after['terrainPatches']=[newpatch if p['url']==replacement['url']else p for p in before['terrainPatches']];assert len(after['terrainPatches'])==len(before['terrainPatches'])
 url='city/data/official-models/'+BATCH+'/catalogue.json';after['officialModelCatalogues'].append(url);save(STAGE/'manifest.json',after)
 edits=[dict(destination='3d-viewer/'+url,beforeSHA256=None,source=ref(STAGE/'catalogue.json')),dict(destination='3d-viewer/'+terrainurl,beforeSHA256=None,source=ref(patchpath)),dict(destination=str(manifest.relative_to(ROOT)),beforeSHA256=digest(manifest.read_bytes()),source=ref(STAGE/'manifest.json'))]
 assets=[dict(destination='3d-viewer/'+url.rsplit('/',1)[0]+'/'+m['asset'],source=ref(STAGE/m['asset']))for m in models]
 previous=BASE/'government-xl-heya-aqua-original-installed-v1-20261020/full-xl-current-count.json';delta=inventory_delta(read(previous),models,manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['expectedFixedXLDelta']>0
 config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,viewportWidths=[390,1280],failureTestUids=sorted(sources));config['terrain'][0]['destination']=terrainurl
 save(STAGE/'browser-config.json',config);save(STAGE/'live-browser-config.json',config)
 for e in edits+assets:
  dest=ROOT/e['destination'];assert(digest(dest.read_bytes())if dest.exists()else None)==e.get('beforeSHA256');assert ref(ROOT/e['source']['path'])==e['source']
 plan=dict(edits=edits,assets=assets,sourceSHA256ByUid=sources,existingModelReverification=near['checkedNativeUids'],newModels=sorted(sources),newVisibleModels=8,newRuntimeCount=len(allold)+8,delta=delta,previousXLCount=ref(previous),terrainChanges=1,terrainReplacement=replacement,terrainDestination=terrainurl,currentManifest=ref(manifest),sourceReview=ref(DOC/'ROOT-SOURCE-REVIEW.json'),publication=False)
 save(DOC/'publication-plan.json',plan);refs.extend([previous,HERE/'upton_staged_image_review_binding_v1_20261014.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('yoho_mall_plan_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-qualified-terrain-replacement-publication-plan',list(dict.fromkeys(refs)),dict(uids=sorted(sources),qualifiedForLiveVerification=True,newVisibleModels=8,delta=delta,publication=False))
if __name__=='__main__':main()
