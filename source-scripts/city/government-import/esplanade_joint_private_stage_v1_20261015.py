"""Exact two-original private stage; source roles retained, no public mutation."""
from pathlib import Path
import importlib.util,sys,shutil,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-esplanade-joint-private-stage-v1-20261015';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
TOWER='landsd/268828:0';PODIUM='landsd/309385:0';SOURCES={TOWER:'38a2e79ad1b90b7f800f1920b3a22a3890bd177cbc9258feccb32a9d7bd332f8',PODIUM:'ab5f78c1349cfb01db2d60bb36af0122ec8d374abaa5c8b63eaac63f58cd097c'}
NAMES={
 'physical':'government-xl-esplanade-pair-current-physical-v3-20261015',
 'identity':'government-xl-esplanade-podium-reviewed-identity-v1-20261015',
 'review':'government-xl-esplanade-warning-applicability-review-v2-20261015',
 'scope':'government-xl-esplanade-current-native-parent-scope-v1-20261015',
 'capture':'government-xl-esplanade-basic-ground-capture-v1-20261015',
 'finite':'government-xl-esplanade-basic-finite-v1-20261015',
 'foundation':'government-xl-esplanade-compound-foundation-v1-20261015',
 'podiumOriginal':'government-xl-esplanade-podium-finite-v1-20261015',
 'podiumRender':'government-xl-esplanade-render-finite-v2-20261015',
 'roleOriginal':'government-xl-esplanade-exact-wall-exposure-v1-20261015',
 'roleRender':'government-xl-esplanade-render-grade-roles-v2-20261015',
 'supportOriginal':'government-xl-esplanade-exact-tower-podium-paths-v1-20261015',
 'supportRender':'government-xl-esplanade-render-tower-podium-paths-v1-20261015'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def load():
 refs={};receipts={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for key,name in NAMES.items():
   p=BASE/name/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);receipts[key]=r
   for q in r['evidenceRefs']+[ref(p)]:
    if q['path']in refs:assert refs[q['path']]==q['sha256']
    refs[q['path']]=q['sha256']
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h
 def data(key,file):
  p=BASE/NAMES[key]/file;refs[str(p.relative_to(ROOT))]=digest(p.read_bytes());return read(p)
 identity=data('identity','identity-review.json');assert identity['uid']==PODIUM and identity['sourceSHA256']==SOURCES[PODIUM]and identity['identityReviewApproved']and all(identity['identityProof'].values())
 original=data('physical','owned-source-identity.json')['rows'];tower=next(r for r in original if r['uid']==TOWER);assert tower['passed']and not tower['reasons']and tower['sourceSHA256']==SOURCES[TOWER]
 review=data('review','ROOT-warning-applicability.json');assert review['sourceSHA256ByUid']==SOURCES and review['sourceInterpretationAccepted']and not review['rawOrdinaryReasonsResolved']and review['strictContactCountersNotRewritten']
 assert {r['mode']for r in review['podiumModes']}=={r['mode']for r in review['towerModes']}=={'original','literal','left','balanced'}
 for r in review['towerModes']:assert len(r['failures'])==21 and all(x['exactSharedEdgePathsToPositivePodiumContact']for x in r['failures'])
 scope=data('scope','scope.json.gz');assert scope['completeCurrentNativeModels']==6653 and not scope['touchingNativeUids']and all(r['strictlyOutsideParentDomain']for r in scope['rows'])
 basic=data('finite','summary.json');actors=data('capture','basic-actors.json.gz');assert basic['noIntroducedFailures']and len(basic['rows'])==len(actors['rows'])==11 and sum(r['completeFaces']for r in basic['rows'])==2200
 assert {r['uid']for r in basic['rows']}=={r['uid']for r in actors['rows']}
 assert all(not r['introducedUnproved']and not r['afterUncovered']for r in basic['rows'])
 capture=data('capture','capture-report.json.gz');assert capture['strictExteriorUnchanged']and capture['startEndAllInputsVerified']
 foundation=data('foundation','compound-foundation.json');assert foundation['allFourPass']and len(foundation['rows'])==4 and all(r['strictFoundationAccepted']and r['foundation']['completeTerrainTriangles']==23998 for r in foundation['rows'])
 for key,modes in [('podiumOriginal',['original','literal']),('podiumRender',['left','balanced'])]:
  for mode in modes:
   d=data(key,mode+'.json.gz');assert len(d['faces'])==1476 and [r['sourceFace']for r in d['faces']]==list(range(1476));assert all(r['proof']['groundProjectionCovered']for r in d['faces']);assert [r['sourceFace']for r in d['faces']if not r['proof']['existingOrdinaryClearanceBoundProved']]==[510,516,518,1276]
 for key,modes in [('roleOriginal',['original','literal']),('roleRender',['left','balanced'])]:
  for mode in modes:
   d=data(key,mode+'.json.gz')['capPaths'];assert d['allAffectedHavePaths']and not d['rawExposureFailures']and d['affectedOriginalWallFaces']==[510,516,518,1276]
 validation=data('physical','validation.json');assert validation['loaderAccepted']==validation['checksPassed']==2 and validation['exceptions']==0
 decisions=data('physical','physical-decisions.json')['rows'];assert {r['uid']:r['numericReasons']for r in decisions}=={TOWER:['ground-contact-unresolved'],PODIUM:['terrain-intersects-source-over-0.5m','strict-identity-fit']}
 oldfoundation=data('physical','foundation.json')['rows'];assert len(oldfoundation)==2 and all(r['strictFoundationAccepted']for r in oldfoundation)
 budget=data('physical','final-terrain-budget.json');assert budget['passed']and not budget['runtimeBudgetChanged']
 candidate=data('physical','terrain-candidates.json')[0];assert candidate['bounds']==scope['parentDomain']
 rows=data('physical','selection.json.gz')['rows'];assert {r['uid']:r['sourceSHA256']for r in rows}==SOURCES
 for row in rows:
  assert read(ROOT/'3d-viewer'/row['source']['tile'])['buildings'].count(row['source']['building'])==1
 current=ROOT/'3d-viewer/city/data/manifest.json';assert digest(current.read_bytes())==scope['currentManifestSHA256']
 return refs,rows,candidate,actors,decisions

def main():
 assert not DOC.exists()and not STAGE.exists();refs,rows,candidate,actors,decisions=load();keys=sorted({prefix+r['uid']for prefix in ['building:','terrain-patch:']for r in actors['rows']+rows}|{'immutable-source-proof:'+BATCH});c=reservations.claim('esplanade-joint-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation']
 try:
  DOC.mkdir();pub=module('esplanade_unchanged_publisher',HERE.parent/'island-detail-integration/publish.py');patch=read(ROOT/candidate['path']);parent=read(ROOT/'3d-viewer/city/data/terrain.json');pub.validate_patch(patch,parent);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');pub.check_patch_overlap(patch,parent.get('patches',[])+[read(ROOT/'3d-viewer'/p['url'])for p in manifest['terrainPatches']])
  review=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,privateStageQualified=True,rawPhysicalDecisions=decisions,exactSourceWarningInterpretation=ref(BASE/NAMES['review']/'ROOT-warning-applicability.json'),exactPodiumIdentity=ref(BASE/NAMES['identity']/'identity-review.json'),completeBASICFaces=2200,completeBASICActors=11,nativeTouchingActors=0,compoundFoundationAllFourPass=True,rawFailuresNotRelabelledAsNumericPass=True,sourceGeometryChanges=0,sourcePoseChanges=0,publication=False,installationApproved=False)
  save(DOC/'qualification.json',review);save(DOC/'publisher-terrain-validation.json',dict(passed=True,candidate=candidate,validator=ref(HERE.parent/'island-detail-integration/native_terrain_validation.py')))
  STAGE.mkdir();local=HERE/'local'/NAMES['physical'];cat=read(local/'catalogue.json');assert cat['rootTranslation']==[-834500,0,816500]
  for e in cat['models']:
   assert e['sha256']==SOURCES[e['uid']];e.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(DOC/'qualification.json'),supportDependencies=[])
   if e['uid']==TOWER:e['supportDependencies']=[dict(uid=PODIUM,state='candidate',csuid='1484527460P20191115',sha256=SOURCES[PODIUM])]
   dest=STAGE/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(local/e['asset'],dest);assert digest(dest.read_bytes())==e['sha256']and dest.stat().st_size==e['bytes']
  cat.update(area='The Esplanade unchanged original tower and podium',counts=dict(packedModels=2));save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[r['source']['building']for r in rows]);out=STAGE/'government-native-esplanade-original-v1-20261015.json';shutil.copyfile(ROOT/candidate['path'],out)
  terrain=dict(source=str(out.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+out.name,resolution=patch['cell'],area=cat['area']);destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=cat['area'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[terrain]))
  config=read(HERE/'local/government-xl-esplanade-private-browser-v2-20261015/browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain]);save(STAGE/'browser-config.json',config)
  pub.DOC=DOC/'publisher-dry-run';oldargv=sys.argv;sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))]
  try:pub.main()
  finally:sys.argv=oldargv
  assert not read(pub.DOC/'publication-plan.json')['published']
  for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h
  paths=[ROOT/p for p in refs]+[Path(__file__),HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py']+[p for p in STAGE.rglob('*')if p.is_file()];module('esplanade_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pair-source-specific-private-stage-v1',paths,dict(uids=list(SOURCES),publisherDryRunPassed=True,privateStageQualified=True,fullAcceptance=False));print('Private stage and publisher dry run pass; live publication not performed',flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
