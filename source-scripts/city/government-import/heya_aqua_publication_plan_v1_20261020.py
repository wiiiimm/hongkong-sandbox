"""Prepare one unchanged Heya tower installation; no terrain or retained actor edits."""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-qualified-publication-plan-v1-20261020';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;OLD=HERE/'local/government-xl-heya-aqua-private-browser-v5-20261020';UID='landsd/184287:0'
NAMES=['identity-review-v1','physical-review-v1','current-applicability-v2','neighbour-clearance-v2','private-browser-v5']
def folder(n):return BASE/('government-xl-heya-aqua-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=folder(n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 identity=read(folder('identity-review-v1')/'review.json');physical=read(folder('physical-review-v1')/'review.json');app=read(folder('current-applicability-v2')/'applicability.json');clear=read(folder('neighbour-clearance-v2')/'clearance.json')
 assert identity['identityOnlyApproved']and physical['localWallInterpretationAccepted']and identity['sourceSHA256']==physical['sourceSHA256ByUid'][UID]
 assert app['currentNativeActors']==6781 and {a['uid']for a in app['touchingNativeActors']}=={'landsd/184285:0','landsd/184286:0'}and app['unrelatedRecordedFormIntersections']==0
 assert clear['retainedTowerInstalledVerified']and len(clear['rows'])==4 and all(r['projectionIntersectionM2']==0 and r['minimumHorizontalSeparationM']>0 for r in clear['rows'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==app['currentManifest'];before=read(manifest);after=copy.deepcopy(before);cat=read(OLD/'catalogue.json');assert len(cat['models'])==1;entry=cat['models'][0];assert entry['uid']==UID and entry['sha256']==identity['sourceSHA256'];allold=[m for url in before['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(allold)==len({m['uid']for m in allold})==6781 and UID not in {m['uid']for m in allold}
 support=next(m for m in allold if m['uid']=='landsd/184285:0');assert support['sha256']==physical['sourceSHA256ByUid'][support['uid']]
 qualification=dict(uids=[UID],originalSourceReviewAccepted=True,identityReview=ref(folder('identity-review-v1')/'review.json'),physicalReview=ref(folder('physical-review-v1')/'review.json'),currentApplicability=ref(folder('current-applicability-v2')/'applicability.json'),neighbourClearance=ref(folder('neighbour-clearance-v2')/'clearance.json'),currentManifest=ref(manifest),sourceSHA256ByUid={UID:entry['sha256']},rawStrictFailuresRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=0,retainedModelChanges=0,publication=False,installationApproved=False)
 save(DOC/'ROOT-SOURCE-REVIEW.json',qualification)
 entry.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,proceduralWindows=False,sourceIdentityReview=ref(folder('identity-review-v1')/'review.json'),sourceFunctionalApplicability=ref(DOC/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Unchanged original at fixed1x/source pose. Exact identity, full four-mode compound foundation and source-specific wall-joint review; complete current native inventory, neighbour tower separation, staged desktop/mobile picking/collision/fallback checks. Raw strict contact warnings retained in bound review.')
 assert entry['supportDependencies']==[dict(uid=support['uid'],csuid=support['buildingCSUID'],sha256=support['sha256'],state='installed')]
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/entry['asset'],asset);assert digest(asset.read_bytes())==entry['sha256'];save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));shutil.copyfile(OLD/'source-forms.json',STAGE/'source-forms.json')
 url='city/data/official-models/'+BATCH+'/catalogue.json';after['officialModelCatalogues'].append(url);save(STAGE/'manifest.json',after)
 edits=[dict(destination='3d-viewer/'+url,beforeSHA256=None,source=ref(STAGE/'catalogue.json')),dict(destination=str(manifest.relative_to(ROOT)),beforeSHA256=digest(manifest.read_bytes()),source=ref(STAGE/'manifest.json'))];assets=[dict(destination='3d-viewer/'+url.rsplit('/',1)[0]+'/'+entry['asset'],source=ref(asset))]
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';previous=BASE/'government-xl-victoria-mall-original-installed-v1-20261020/full-xl-current-count.json';delta=inventory_delta(read(previous),[entry],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['expectedFixedXLDelta']==1
 config=read(OLD/'browser-config-1280.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url,terrain=[],viewportWidths=[1280]);save(STAGE/'browser-config.json',config);save(STAGE/'live-browser-config.json',config)
 for e in edits+assets:
  dest=ROOT/e['destination'];assert(digest(dest.read_bytes())if dest.exists()else None)==e.get('beforeSHA256');assert ref(ROOT/e['source']['path'])==e['source']
 save(DOC/'publication-plan.json',dict(edits=edits,assets=assets,sourceSHA256ByUid={UID:entry['sha256']},existingModelReverification=[],newModels=[UID],newVisibleModels=1,newRuntimeCount=len(allold)+1,delta=delta,previousXLCount=ref(previous),terrainChanges=0,currentManifest=ref(manifest),sourceReview=ref(DOC/'ROOT-SOURCE-REVIEW.json'),publication=False))
 refs.extend([previous,pointer,HERE/'upton_staged_image_review_binding_v1_20261014.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 module('heya_publication_plan_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'one-original-tower-current-qualified-publication-plan',list(dict.fromkeys(refs)),dict(uids=[UID],qualifiedForLiveVerification=True,newVisibleModels=1,delta=delta,publication=False))
if __name__=='__main__':main()
