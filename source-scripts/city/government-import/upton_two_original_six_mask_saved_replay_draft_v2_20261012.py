"""UNEXECUTED exact saved-nomination resume; no partition/contact recompute.
Preserves failed v1 and unchanged closure/geometry/sampler/validator policies.
"""
from pathlib import Path
import ast,json,sys,time,uuid,subprocess,shutil,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-two-original-six-mask-saved-nomination-replay-v2-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PROPOSAL=BASE/(BATCH+'-proposal')
OLD=BASE/'government-xl-upton-two-original-six-mask-current-ground-nomination-v1-20261012';OLDP=BASE/(OLD.name+'-proposal')
FAIL=OLD/'actual-failed-attempt-and-release-summary.json';METHOD=PROPOSAL/'METHOD.md';PREFLIGHT=PROPOSAL/'unexecuted-schema-pin-check.json'
RUNTIME=HERE/'upton_two_original_six_mask_runtime_draft_v2_20261012.mjs';FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
VALIDATION=OLDP/'join-helper-validation.json';HELPER=HERE/'upton_two_original_six_mask_partition_v1_20261012.py';TEST=HERE/'test_upton_two_original_six_mask_partition_v1_20261012.py'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540';UIDS=['landsd/338946:0','landsd/12728:0'];SECONDARY='landsd/12662:0';NATIVE='landsd/79882:0';FOREIGN='landsd/254809:0'
SEEDS={'input.json.gz': 'ef15f62d6802b8babf208f0d67533b4f811e424c51d37e3dbae652cf5e0b9f21', 'geometry-nomination.json.gz': 'b1c7ec17d9c949ddc65d62cfd5f11336ada4add1a71e3ad895b4a79814fb4b31', 'complete-nominations-before-guards.json.gz': '5b9ad13a3de08bd42075019926d483bb47d57217965a5f1860dd4fe59fbbb276', 'complete-affected-scope.json.gz': 'b283e760305a09c8609d1b42a7fe1c62c048e692bdfde57f96b01b69f0484bf1'}
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):
 assert set(q)<=set(['path','sha256','bytes'])and set(['path','sha256'])<=set(q)
 p=ROOT/q['path'];assert ref(p)=={k:q[k]for k in ['path','sha256']},q
 if 'bytes'in q:assert p.stat().st_size==q['bytes']
 return p
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pre=read(PREFLIGHT);assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['runtime']==ref(RUNTIME)and pre['method']==ref(METHOD);clv=read(check(pre['literalClosureValidation']));assert clv['passed']and clv['exitCode']==0 and clv['runtime']==ref(RUNTIME)and clv['schema']=='exact-literal-static-dynamic-resource-closure-v1'and clv['computedImportsRejected']and clv['unsupportedDynamicImports']==0 and clv['startEndHashesVerified'];check(clv['log'])
 v=read(VALIDATION);assert v['exitCode']==0 and v['passedTests']==13 and v['failedTests']==0 and v['helper']==ref(HELPER)and v['test']==ref(TEST);check(v['log'])
 refs=[ref(PROPOSAL/'failed-v1-byte-preservation.json'),ref(Path(__file__)),ref(RUNTIME),ref(METHOD),ref(PREFLIGHT),pre['literalClosureValidation'],clv['log'],ref(HELPER),ref(TEST),ref(VALIDATION),v['log'],ref(FREEZER),ref(FAIL)]+[ref(x)for x in sorted(OLDP.rglob('*'))if x.is_file()]
 for path,sha in clv['inputHashes'].items():refs.append(dict(path=path,sha256=sha))
 # Same existing local import closure protocol; pin before any dynamic load.
 folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review'];todo=[Path(__file__),FREEZER];seen=set()
 while todo:
  path=todo.pop().resolve()
  if path in seen:continue
  seen.add(path);refs.append(ref(path))
  for node in ast.walk(ast.parse(path.read_text())):
   names=[node.module]if isinstance(node,ast.ImportFrom)and node.module else[x.name for x in node.names]if isinstance(node,ast.Import)else[]
   for name in names:
    for folder in folders:
     q=folder/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 fail=read(FAIL);assert fail['exitCode']==1 and not fail['completedNeonJobCreated']and fail['actualCandidateDrawAndGuardAndRealValidatorNotCompleted']
 for q in fail['savedOutputs']+fail['constructorBytes']+[fail['savedInput'],fail['reservation']]:check(q);refs.append({k:q[k]for k in ['path','sha256']})
 preservation=read(PROPOSAL/'failed-v1-byte-preservation.json')
 for q in preservation['pairs']:
  for key in ['original','archive']:
   if key in q:check(q[key]);refs.append(q[key])
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');oldlease=read(check(fail['reservation']));group=c.execute('SELECT released_at,(released_at IS NULL AND lease_until>clock_timestamp()) FROM astra_modelling.reservation_groups WHERE token=%s AND owner=%s',(oldlease['token'],oldlease['owner'])).fetchone();assert group and group[0]is not None and group[1]is False
 for batch,job,resultsha in [('government-xl-upton-whole-parent-current-domain-capture-v2-20261012','69916bb92558c08c4c5c1838f7c34f963f0e888b7ef14cb489d995ab9bc36727','91d90929b7a8f3694239ba7d5ec97ab5bc1018d52e8d205c08542a820735f120'),('government-xl-upton-whole-parent-original-tin-regression-v2-20261012','3046002072e7956b8d862a6a0ed14a66055fa962bfa3ccbef9401286910b4899','93579719eb26a37bd28fc6aadf019d305a0940e5f279f4b329c86751fbda439a'),('government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012',None,'23343a25c467135ca4300acbf7963c08b2006deb7671f660bbe66d838168a33c')]:
  folder=BASE/batch;receipt=read(folder/'result.json');assert ref(folder/'result.json')['sha256']==resultsha
  if job:assert receipt['jobId']==job
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();seed={}
 for name,sha in SEEDS.items():
  path=OLD/name;assert ref(path)['sha256']==sha;seed[name]=read(path)
 nom=seed['geometry-nomination.json.gz'];full=seed['complete-nominations-before-guards.json.gz'];scope=seed['complete-affected-scope.json.gz'];inp=seed['input.json.gz']
 assert nom['originalSourceFaces']==len(full['wholeSourceOriginalFaceInventory'])==122721 and nom['currentCapturedFaces']==len(full['wholeCurrentFaceInventory'])==9214
 assert [x['originalFace']for x in full['wholeSourceOriginalFaceInventory']]==list(range(122721))and [x['originalFace']for x in full['wholeCurrentFaceInventory']]==list(range(9214))
 a=np.asarray(nom['candidateRawPositionTriplets'],dtype='<f8');b=np.asarray(full['candidateRawPositionTriplets'],dtype='<f8');assert a.shape==b.shape==(11186,3,3)and np.isfinite(a).all()and a.tobytes()==b.tobytes()and len(full['candidateFaceProvenance'])==11186
 assert nom['core']==inp['core']==full['core']and nom['domain']==inp['domain']==full['domain']==[-2477.5,-37.5,-2267.5,102.5]
 assert len(full['completeCoreBoundaryNominations'])==325 and sum(q['completeUpperEnvelopeNomination']['complete']for q in full['completeCoreBoundaryNominations'])==323 and sum(q.get('collapsedConnectorUncredited',False)for q in full['completeCoreBoundaryNominations'])==2;assert nom['allBoundaryFiniteNominationsComplete']is False # retained diagnostic, not a new topology gate
 assert len(scope['affectedBasic'])==52 and sum(len(x['selectedWholeFaceIDs'])for x in scope['affectedBasic'])==2114 and scope['requiredNineWholeFacets']=={'landsd/214971:0':[30,39,50,54,56,57],'landsd/231778:0':[68,73,76]}
 assert [x['uid']for x in scope['wholeDomainTouchingNativeNominees']]==[NATIVE]and not scope['otherTouchingNativeCompleteActualStreamsUnqualified']
 # Persist the failed execution as a completed archival diagnostic, not a successful constructor.
 module(FREEZER,'upton_failed_v1_archive_freezer').freeze(OLD.name+'-failed-execution-archive','failed-private-nomination-execution-preservation',[check(q)for q in {(q['path'],q['sha256']):q for q in refs}.values()]+[OLD/n for n in SEEDS],dict(uids=UIDS+[SECONDARY,NATIVE],sourceOnly=True,failedConstructorExitCode=1,constructorExecutionSucceeded=False,noSuccessfulCandidateCaptured=True,physicalAccepted=False,newlyInstalled=0,currentManifestSHA256=CURRENT,failedAttempt=ref(FAIL)))
 refs.append(ref(BASE/(OLD.name+'-failed-execution-archive')/'result.json'));pulse(True)
 DOC.mkdir(parents=True)
 for name in SEEDS:
  shutil.copyfile(OLD/name,DOC/name);assert (DOC/name).read_bytes()==(OLD/name).read_bytes()
 save(DOC/'exact-saved-nomination-resume-proof.json',dict(seedFiles=[ref(OLD/name)for name in SEEDS],copiedFiles=[ref(DOC/name)for name in SEEDS],completeBinary64NomineeSHA256=digest(a.tobytes()),sourceInventory=122721,currentInventory=9214,nomineeFaces=11186,failedV1=ref(FAIL),noPartitionOrContactRecompute=True,noGeometryOrNumericPredicateChange=True))
 with (DOC/'actual-production-replay.log').open('wb')as log:subprocess.run(['node',str(RUNTIME),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 replay=read(DOC/'actual-production-replay.json.gz');assert replay['currentManifestSHA256']==CURRENT and replay['startEndAllInputsVerified']
 for path,sha in replay['inputHashes'].items():refs.append(dict(path=path,sha256=sha))
 validator_path=HERE.parent/'island-detail-integration/native_terrain_validation.py';refs.append(ref(validator_path));validator=module(validator_path,'upton_resumed_real_validator');error=None
 try:validator.validate_native_mesh(read(DOC/'private-native-terrain-candidate.json.gz'),read(ROOT/'3d-viewer/city/data/terrain.json'))
 except AssertionError as e:error=str(e)
 save(DOC/'real-validator-outcome.json',dict(passed=error is None,actualAssertion=error,unchangedValidator=ref(validator_path),noApprovalOrToleranceChanges=True,notExactSeamCertificate=True))
 save(DOC/'diagnostic.json.gz',dict(currentManifest=inp['currentManifest'],exactSavedNominationResume=ref(DOC/'exact-saved-nomination-resume-proof.json'),runtime=ref(DOC/'actual-production-replay.json.gz'),candidate=ref(DOC/'private-native-terrain-candidate.json.gz'),realValidator=ref(DOC/'real-validator-outcome.json'),wholeOwnedFourStreamOrdinaryClearanceStillRequired=True,complete52BasicBeforeAfterStillRequired=True,exactPackingCoverageAndRoutingSeamsStillRequired=True,native79882CompleteCandidateRegressionStillRequired=True,allZeroDetachedRoleAndCrossingObligationsRetained=True,noAllFacesStrictOrGlobalWatertightRequirement=True,sourceGeometryChanges=0,sourcePoseChanges=0,liveTerrainChanges=0,secondaryHeldAsForeign=SECONDARY,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(x)for x in sorted(DOC.iterdir())if x.is_file()];fence();module(FREEZER,'upton_resumed_nomination_freezer').freeze(BATCH,'private-source-preserving-original-TIN-current-ring-replay-only',[check(q)for q in {(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS+[NATIVE],sourceOnly=True,candidateOnly=True,physicalAccepted=False,newlyInstalled=0,currentManifest=inp['currentManifest'],completeOwnedFaces=13312,completeAffectedBasicActors=52,wholeSourceFacets=122721))
def main():
 if '--owned'in sys.argv:return owned()
 assert '--resume-private-nomination-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=UIDS+[SECONDARY,NATIVE,FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-exact-nomination-resume-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
