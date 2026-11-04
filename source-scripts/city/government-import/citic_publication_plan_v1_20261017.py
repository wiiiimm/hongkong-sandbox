"""Prepare an exact, reversible CITIC catalogue update; this script never publishes."""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-qualified-publication-plan-v1-20261017';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
P='landsd/232579:0';T='landsd/278303:0';SOURCE_STAGE=HERE/'local/government-xl-citic-pair-private-stage-v2-20261017'
NAMES=['government-xl-citic-reviewed-boundary-identity-v1-20261017','government-xl-citic-pair-private-stage-v2-20261017','government-xl-citic-pair-browser-v1-20261017','government-xl-citic-pair-browser-diagnostic-v1-20261017']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists() and not STAGE.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 cat=read(SOURCE_STAGE/'catalogue.json');sources={m['uid']:m['sha256'] for m in cat['models']};assert set(sources)=={P,T}
 desktop=read(BASE/NAMES[2]/'staged-browser.json');mobile=read(BASE/NAMES[3]/'staged-browser.json');assert mobile['passed'] and not mobile['errors']
 views=[v for v in desktop['views'] if v.get('width')==1280 and 'time' in v]+[v for v in mobile['views'] if 'time' in v];assert len(views)==8
 assert {(v['uid'],v['width'],v['time']) for v in views}=={(u,w,t) for u in [P,T] for w in [1280,390] for t in ['15:00','22:00']}
 for v in views:assert v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces'] and v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==sources[v['uid']]
 joint=[v for v in desktop['jointViews'] if v['width']==1280]+mobile['jointViews'];assert len(joint)==4
 for v in joint:assert {m['uid']:m['sourceSHA256'] for m in v['models']}==sources and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in v['models'])
 failed=[v for v in mobile['views'] if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['fallbackRetained'] and failed[0]['dependentFallbacks']=={T:dict(active=False)}
 inspected=[(NAMES[2],P,1280,'1500'),(NAMES[2],T,1280,'1500'),(NAMES[2],T,1280,'2200'),(NAMES[3],P,390,'1500'),(NAMES[3],T,390,'1500'),(NAMES[3],T,390,'2200')]
 images=[ref(BASE/n/f"staged-{u.replace('/','-').replace(':','-')}-{w}-{t}.png") for n,u,w,t in inspected]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=read(manifest);pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';previous=BASE/'government-xl-opus-original-installed-v1-20261017/full-xl-current-count.json'
 delta=inventory_delta(read(previous),cat['models'],manifest_sha=ref(manifest)['sha256'],snapshot=read(pointer)['snapshotId']);assert delta['expectedFixedXLDelta']==1 and delta['newFixedXLUids']==[T]
 DOC.mkdir();STAGE.mkdir()
 review=dict(reviewer='Codex ROOT',sourceGeometryAppearanceAccepted=True,reviewedImages=images,limits='Mobile controls/minimap/title obscure part of the lower model. No unobstructed mobile UI or physical-phone performance claim. Original desktop+mobile run timed out at first mobile joint load; unchanged mobile-only reproduction passed all original assertions. Failed report retained.',sourceGeometryChanges=0)
 save(DOC/'ROOT-IMAGE-INSPECTION.json',review)
 for e in cat['models']:
  e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceFunctionalApplicability=ref(BASE/NAMES[1]/'qualification.json'),sourceIdentityReview=ref(BASE/NAMES[0]/'decision.json'),placementReview='Exact unchanged government sources, reviewed rear-boundary source identity, strict eight-contact podium interface, full original/rendered finite clearance and compound foundation, production loader and desktop/mobile day/night picking/collision and failed-support recovery.')
  if e['uid']==T:e['supportDependencies'][0]['state']='installed'
  raw=(SOURCE_STAGE/e['asset']).read_bytes();assert digest(raw)==e['sha256'];dest=STAGE/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',read(SOURCE_STAGE/'source-forms.json'))
 old=[];matches=[]
 for url in before['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;c=read(path);old.extend(c['models'])
  if any(m['uid']==P for m in c['models']):matches.append((path,c))
 assert len(matches)==1 and T not in {m['uid'] for m in old};oldpath,oldcat=matches[0];oldentry=next(m for m in oldcat['models'] if m['uid']==P);assert oldentry['sha256']==sources[P]
 replacement={**oldcat,'models':[m for m in oldcat['models'] if m['uid']!=P],'counts':{**oldcat['counts'],'packedModels':len(oldcat['models'])-1}}
 save(STAGE/'retained-catalogue.json',replacement);destination='city/data/official-models/'+BATCH+'/catalogue.json';after=copy.deepcopy(before);after['officialModelCatalogues'].append(destination);save(STAGE/'manifest.json',after)
 config=read(SOURCE_STAGE/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination);config['catalogueReplacements']=[dict(url=str(oldpath.relative_to(ROOT/'3d-viewer')),source=str((STAGE/'retained-catalogue.json').relative_to(ROOT)),originalSHA256=ref(oldpath)['sha256'])];save(STAGE/'browser-config.json',config)
 planned=[m for m in old if m['uid']!=P]+cat['models'];assert len(planned)==len(old)+1 and len({m['uid'] for m in planned})==len(planned)
 assert {m['uid']:m for m in planned if m['uid'] not in {P,T}}=={m['uid']:m for m in old if m['uid']!=P}
 plan=dict(currentManifest=ref(manifest),currentReviewPointer=ref(pointer),previousXLCount=ref(previous),delta=delta,sourceSHA256ByUid=sources,newVisibleModels=1,existingModelReverification=[P],newModels=[T],newRuntimeCount=len(planned),terrainChanges=0,sourceGeometryChanges=0,publication=False,
  edits=[dict(source=ref(STAGE/'retained-catalogue.json'),destination=str(oldpath.relative_to(ROOT)),beforeSHA256=ref(oldpath)['sha256']),dict(source=ref(STAGE/'catalogue.json'),destination='3d-viewer/'+destination,beforeSHA256=None),dict(source=ref(STAGE/'manifest.json'),destination=str(manifest.relative_to(ROOT)),beforeSHA256=ref(manifest)['sha256'])],assets=[dict(source=ref(STAGE/e['asset']),destination=str((ROOT/'3d-viewer'/destination).parent.relative_to(ROOT))+'/'+e['asset']) for e in cat['models']],requiresLiveBrowserAndLedgerBeforeInstalledCredit=True)
 save(DOC/'publication-plan.json',plan)
 refs.extend([manifest,pointer,previous,oldpath,HERE/'upton_staged_image_review_binding_v1_20261014.py',*[p for p in STAGE.rglob('*') if p.is_file()]])
 result=module('citic_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-citic-exact-reversible-publication-plan-v1',list(dict.fromkeys(refs)),dict(uids=[P,T],qualifiedForLiveVerification=True,expectedFixedXLDelta=1,newVisibleModels=1,existingModelReverification=[P],installationApproved=False,newlyInstalled=0,modelGeometryChanges=0));print(dict(jobId=result['jobId'],newVisibleModels=1,expectedFixedXLDelta=1),flush=True)
if __name__=='__main__':main()
