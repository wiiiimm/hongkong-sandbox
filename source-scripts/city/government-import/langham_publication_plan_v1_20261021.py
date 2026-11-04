"""Stage one accepted immutable original and reviewed terrain; no live writes."""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-qualified-publication-plan-v1-20261021';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;UID='landsd/79318:0'
NAMES=dict(review='government-xl-langham-source-review-v1-20261021',browser='government-xl-langham-private-browser-v1-20261021')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists() and not STAGE.exists();refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for key,name in NAMES.items():
   p=BASE/name/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);pins[key]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(key,p):
  assert digest(p.read_bytes())==pins[key][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rp=BASE/NAMES['review']/'ROOT-SOURCE-REVIEW.json';review=take('review',rp)
 assert all(review[k] for k in ['identityAccepted','completeFoundationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
 for q in review['imagesActuallyViewed']+review['browserReports']:
  assert ref(ROOT/q['path'])==q;refs.append(ROOT/q['path'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==review['currentManifest'];before=read(manifest);after=copy.deepcopy(before);refs.append(manifest)
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';currentPointer=read(pointer);refs.append(pointer)
 oldmodels=[]
 for url in before['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;refs.append(p);oldmodels.extend(read(p)['models'])
 assert len(oldmodels)==len({m['uid'] for m in oldmodels})==6799 and UID not in {m['uid'] for m in oldmodels}
 OLD=HERE/'local'/NAMES['browser'];cat=take('browser',OLD/'catalogue.json');assert len(cat['models'])==1;m=cat['models'][0];assert m['uid']==UID and m['sha256']==review['sourceSHA256ByUid'][UID]
 assert len(m['supportDependencies'])==1 and m['supportDependencies'][0]['uid']=='landsd/224399:0' and m['supportDependencies'][0]['state']=='installed'
 qualification={**review,'originalSourceReviewAccepted':True,'sourceReview':ref(rp)};save(DOC/'ROOT-SOURCE-REVIEW.json',qualification)
 m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,sourceIdentityReview=ref(rp),sourceFunctionalApplicability=ref(DOC/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Immutable original at fixed source placement and 1x scale. Complete four-mode foundation and exact original podium-contact interpretation; unchanged existing terrain and podium, desktop/mobile day-night and failed-download checks passed. Raw support warnings retained.')
 raw=(OLD/m['asset']).read_bytes();assert digest(raw)==m['sha256'];refs.append(OLD/m['asset']);dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));forms=take('browser',OLD/'source-forms.json');save(STAGE/'source-forms.json',forms)
 url='city/data/official-models/'+BATCH+'/catalogue.json';after['officialModelCatalogues'].append(url);save(STAGE/'manifest.json',after)
 edits=[dict(destination='3d-viewer/'+url,beforeSHA256=None,source=ref(STAGE/'catalogue.json')),dict(destination=str(manifest.relative_to(ROOT)),beforeSHA256=digest(manifest.read_bytes()),source=ref(STAGE/'manifest.json'))]
 assets=[dict(destination='3d-viewer/'+url.rsplit('/',1)[0]+'/'+m['asset'],source=ref(STAGE/m['asset']))]
 previous=BASE/'government-xl-manhattan-original-installed-v1-20261021/full-xl-current-count.json';delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=currentPointer['snapshotId']);assert delta['expectedFixedXLDelta']==1 and delta['previousInstalled']==295;refs.append(previous)
 cfg=take('browser',OLD/'browser-config-390.json');cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url);assert cfg['terrain']==[];save(STAGE/'browser-config.json',cfg);save(STAGE/'live-browser-config.json',cfg)
 for e in edits+assets:
  p=ROOT/e['destination'];assert (digest(p.read_bytes()) if p.exists() else None)==e.get('beforeSHA256');assert ref(ROOT/e['source']['path'])==e['source']
 plan=dict(edits=edits,assets=assets,sourceSHA256ByUid={UID:m['sha256']},newModels=[UID],newVisibleModels=1,newRuntimeCount=6800,existingModelReverification=['landsd/224399:0'],delta=delta,previousXLCount=ref(previous),terrainChanges=0,terrainReplacement=None,terrainDestination=None,currentManifest=ref(manifest),currentPointer=ref(pointer),sourceReview=ref(DOC/'ROOT-SOURCE-REVIEW.json'),publication=False)
 save(DOC/'publication-plan.json',plan);refs.extend([HERE/'upton_staged_image_review_binding_v1_20261014.py',*[p for p in STAGE.rglob('*') if p.is_file()]])
 module('langham_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'single-original-qualified-publication-plan',list(dict.fromkeys(refs)),dict(uids=[UID],qualifiedForLiveVerification=True,newVisibleModels=1,delta=delta,publication=False))
if __name__=='__main__':main()
