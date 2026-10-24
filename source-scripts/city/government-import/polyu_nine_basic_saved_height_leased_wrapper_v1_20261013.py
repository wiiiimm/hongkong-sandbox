"""Canonical owned execution wrapper for an immutable saved-context producer."""
from pathlib import Path
import importlib.util,json,sys,time,uuid,subprocess,traceback
from run import ROOT,HERE,read,save,digest,connect,reservations
BATCH='government-xl-polyu-sports305582-nine-basic-saved-height-leased-context-v1-20261013'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PRODUCER=HERE/'xl-polyu-sports305582-nine-basic-saved-height-regression-context-draft-v1-20261013.py'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
SOURCE_CONTEXT=BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013/complete-sports-four-stream-current-ground-inputs.json.gz'
JOB='ce2589c6c43d007f527d6bc78e51204abf4344a261fd41b0436dc1c6234d316f'
SOURCE='ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15'
UIDS=['landsd/'+str(i)+':0'for i in [63758,72322,89540,258381,258382,258679,258680,258681,258682,258851,258852,305585,305643,305649,305793,305828,114494,198620,235076,257998,305582,305600,305626,305627,305644]]

def ref(p):return dict(path=str(Path(p).resolve().relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def check(q):
 p=ROOT/q['path'];assert ref(p)==q,q['path'];return p

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['producer']==ref(PRODUCER)
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 producer=module('polyu_immutable_saved_height_producer',PRODUCER)
 assert not (producer.D/'calculation-v1').exists(),'Immutable producer calculation-v1 already exists; preserve it and use terminal recovery rather than overwrite.'
 hashes,a,patch,nine,failed,probes,parents=producer.preflight()
 assert len(hashes)>=8830 and len(parents)==12 and len(probes)==6701
 account=a['account'];scope=account['all25CompleteProductionBasicAndExplicitNativeInputsVerbatim'];rows=scope['rows']
 assert [r['uid']for r in rows]==UIDS and scope['completeScannedForms']==25 and scope['startAndEndInputsVerified']and not scope['physicalAccepted']and not scope['installationApproved']
 assert scope['modelGeometryChanges']==scope['terrainGeometryChanges']==0
 assert [r['currentForm']['uid']for r in rows]==UIDS and len({r['uid']for r in rows})==25
 nomination=account['complete25AffectedActualMeshNomination'];assert nomination['formsAccounted']==25 and {r['uid']for r in nomination['nominated']}==set(UIDS)and not nomination['excluded']
 assert all(r['fullNative59527FourStreamBeforeAfterTerrainQualificationPending']if r['uid']=='landsd/305793:0'else r['wholeActualMeshObligationPending']for r in nomination['nominated'])
 assert sum(r['classification']=='actual-production-BASIC'for r in rows)==24
 native=next(r for r in rows if r['uid']=='landsd/305793:0');assert not native['wholeNativeBeforeAfterTerrainRegressionProved']
 hold=account['installedPodiumFalseHoldVerbatim'];assert hold['publicationHoldPreserved']and sum(r['completeIndexedFaces']for r in hold['actualPositionRecord']['actualRenderMeshes'])==59527
 negatives=account['all752FourModeRawNegativesAnd21BodiesVerbatim'];assert [r['arithmetic']for r in negatives]==['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']and all(len(r['all752FailureRecordsVerbatim'])==752 for r in negatives)
 source=read(SOURCE_CONTEXT);assert source['uid']=='landsd/305582:0'and source['sourceSHA256']==SOURCE
 assert len(source['completeOriginalTopologyVerbatim']['sharedEdgeConnectedComponents'])==21 and len(source['completeOriginalTopologyVerbatim']['exactNonrenderingOriginalFaces'])==4
 assert len(source['completeWorldStreams'])==4 and all(r['completeFaces']==len(r['completeWorldTriangles'])==10536 for r in source['completeWorldStreams'].values())
 assert not source['currentAcceptance']and not source['physicalAccepted']and account['sourceBuildingPoseAndGeometryUnchanged']
 assert account['declaredImmutableSourceFacets']==181089 and account['outputFacets']==3214 and len(account['completeOutputFacetLineage'])==3214
 assert account['fullOwnedFourStreamAndWholeAffectedActorsPending']and account['wholeCoreClosedCoverageAndProductionSeamSamplerQualificationPending']
 validation=read(producer.D/'immutable-tests-v1/validation.json');assert validation['passed']and validation['tests']==5 and validation['exitCode']==0
 for q in validation['orderedCodePins']:check(q)
 assert digest((producer.D/'immutable-tests-v1/tests.log').read_bytes())==validation['testLogSHA256']
 resources=sorted(['building:'+u for u in UIDS]+['terrain-patch:'+u for u in UIDS]+['immutable-source-proof:'+BATCH]);assert len(resources)==len(set(resources))==51
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==producer.CURRENT
 return pins,producer,hashes,a,nine,failed,resources

def schema_only():
 p,producer,h,a,nine,failed,resources=load()
 return dict(passed=True,caller=ref(Path(__file__)),producer=ref(PRODUCER),fullInputPins=len(h),completeAffectedActors=25,canonicalResources=resources,nineSelectedDiagnosticActors=9,savedProbes=6701,candidateFacets=3214,capturedParentFacets=12,sourceFacets=10536,completeSourceBodies=21,originalNegativesPerMode=752,retainedNative59527BeforeAfterPending=True,historicProducerOutputAbsent=True,noNumericalContextDBLeaseOrWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 pins,producer,hashes,a,nine,failed,resources=load();assert lease['resources']==resources
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['producer']==ref(PRODUCER)
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']+[dict(path=k,sha256=v)for k,v in hashes.items()]
 receipt=read(producer.RUN/'result.json');assert receipt['jobId']==JOB
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 refs+=[ref(producer.RUN/'result.json')]+receipt['evidenceRefs']
 def fence():
  assert reservations.owns(lease)
  for q in refs:check(q)
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==producer.CURRENT
 fence();assert not (producer.D/'calculation-v1').exists();DOC.mkdir(parents=True)
 command=[sys.executable,str(PRODUCER),'--calculate-saved-height-context-only']
 with (DOC/'unchanged-producer.log').open('xb')as log:result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 origin=producer.D/'calculation-v1';context=origin/'context.json.gz';passed=False;failure=None;copy=None
 try:
  assert result.returncode==0, 'Immutable producer exit '+str(result.returncode)
  assert context.is_file(),'Successful producer did not leave context.json.gz'
  with context.open('rb')as src,(DOC/'context.json.gz').open('xb')as dest:
   for chunk in iter(lambda:src.read(1024*1024),b''):dest.write(chunk)
  copy=ref(DOC/'context.json.gz');assert copy['sha256']==ref(context)['sha256']
  value=read(DOC/'context.json.gz')
  assert value['fullNineRawGuardFailuresVerbatim']==failed and value['allNineCompleteCurrentForms']==[r['currentForm']for r in nine]and value['allNineWholeActualBasicBuffersAndIndexEvidenceVerbatim']==nine
  assert value['allOriginal752FailuresAndWholeSourceRolesRemain']==a['account']['all752FourModeRawNegativesAnd21BodiesVerbatim']and value['native59527BeforeAfterStillPending']
  assert value['inputHashes']==hashes and not value['currentAcceptance']and not value['physicalAccepted']and value['noNewProductionSamplerOrGuardQueries']and value['noGroundPredicateOrFullFiniteReplay']
  passed=True
 except Exception as e:failure=dict(errorType=type(e).__name__,message=str(e),traceback=traceback.format_exc(),originalAndPartialOutputsPreserved=True,noModelCorruptionOrPermanentRejectionCredit=True)
 original_refs=[ref(p)for p in origin.rglob('*')if p.is_file()]if origin.exists()else[]
 save(DOC/'diagnostic.json.gz',dict(unchangedProducer=ref(PRODUCER),producerCommand=command,producerExitCode=result.returncode,savedContextCalculationPassed=passed,actualFailure=failure,originalProducerOutputRefs=original_refs,byteExactIsolatedContext=copy,all25AffectedUIDs=UIDS,all51CanonicalResources=resources,nineSelectionDoesNotReduceScope=True,all752FourModeRawNegativesAnd21BodiesRetained=True,exactWholeSourceContext=ref(SOURCE_CONTEXT),native59527BeforeAfterStillPending=True,noProductionSamplerOrGuardReplay=True,noTerrainOrBuildingOrPoseChanges=True,physicalAccepted=False,currentAcceptance=False,newlyInstalled=0))
 refs+=original_refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]
 fence()
 frozen=module('polyu_saved_context_owned_freezer',FREEZER).freeze(BATCH,'private-polyu-nine-basic-saved-height-context-no-acceptance',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS,sourceOnly=True,contextCalculationPassed=passed,whole25AffectedActorsRetained=True,retainedNative59527Pending=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=frozen['jobId'],contextCalculationPassed=passed,producerExitCode=result.returncode,currentAcceptance=False)),flush=True)
 if not passed:raise RuntimeError('Saved context producer failure preserved and frozen; inspect diagnostic')

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--calculate-owned-saved-height-context-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 pins,producer,hashes,a,nine,failed,resources=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['producer']==ref(PRODUCER)
 claim=reservations.claim('polyu-nine-basic-saved-context-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
