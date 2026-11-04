"""ROOT-only fresh full-domain production capture for completed full22 nominee."""
from pathlib import Path
import sys,json,time,uuid,subprocess
import numpy as np
import upton_full22_current_plane_restoration_nomination_v1_20261014 as nomination
import upton_three_own_layer_actual_production_capture_draft_v1_20261013 as previous_capture
from upton_full22_saved_nomination_binding_v1_20261014 import validate_binding
from upton_two_original_complete_mask_current_nam_enclosure_draft_v6_20261013 import measured_projection,candidate_surface,verify_drawn_multiset
from run import ROOT,HERE,read,save,connect,reservations
legacy=previous_capture.legacy;ref,check=nomination.ref,nomination.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-full22-current-plane-actual-production-capture-v1-20261014'
NOM_DOC=nomination.DOC;DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'upton_full22_current_plane_actual_production_runtime_v1_20261014.mjs'
V6=previous_capture.V6;VALIDATOR=previous_capture.VALIDATOR
PREVIOUS_JOB='e75d2f586b7a86fa6b4094fbfb53d70951b45c3f9420bcad0abd228b7111bbd2'
TEST='test_upton_full22_saved_nomination_binding_v1_20261014'

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__)) and pins['runtime']==ref(RUNTIME)
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(NOM_DOC/'result.json');assert receipt['jobId']==pins['completedNominationJob'] and not receipt['physicalAccepted'] and not receipt['installationApproved']
 verified=read(NOM_DOC/'ROOT-VERIFIED.json');assert verified['jobId']==receipt['jobId'] and verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased']
 _,whole,coverage,previous,oldraw,oldpv,patch,rep=nomination.load()
 source=read(NOM_DOC/'private-full22-current-plane-restoration-nomination.json.gz');assert source['schema']=='upton-full22-current-plane-restoration-nomination-v1'
 assert source['previousOwnLayerNomination']==ref(previous_capture.NOM_DOC/'private-own-layer-projected-edge-subdivision-nomination.json.gz') and source['previousActualCaptureCandidate']==ref(previous_capture.DOC/'private-native-terrain-candidate.json.gz')
 assert source['wholeCurrentRestorationFeasibility']==ref(nomination.feasibility.DOC/'complete-full22-original-current-restoration-feasibility.json.gz') and source['whole22GapCoverage']==ref(nomination.feasibility.DOC/'complete22-whole-gap-current-counterpart-plane-coverage.json.gz')
 assert source['allOldNominationProofsCountsAndAliasMappingsHistoricalOnly'] and source['all11580ExistingFacetsPreserved'] and source['all68ProtectedLiteralTripletsUnchanged']
 assert source['allPriorFiniteAndFullScopeNegativesVerbatim']==whole['latestFullFiniteNegativesVerbatim'] and source['allZeros23CrossingsRootSupportForeignObligationsRetained']
 assert source['noOverlapApprovalTransferred'] and source['freshPackedCoverageFiniteOverlapMAXSeamRuntimeBrowserRequired'] and not source['physicalAccepted'] and not source['installationApproved']
 raw=validate_binding(source,previous,patch,coverage['completeCurrentCounterpartPlanes']);assert len(oldraw)==11580 and len(source['protectedWholeCurrentTripletsUnchanged'])==68
 assert len(raw)==pins['completeNewNativeFacets'] and source['completeNewRawCandidateSHA256']==pins['completeNewRawSHA256']
 assert len(source['newNativeMesh']['position'])//3==pins['completeNewPositionVertices']
 prior_receipt=read(previous_capture.DOC/'result.json');assert prior_receipt['jobId']==PREVIOUS_JOB
 replay=read(previous_capture.DOC/'actual-production-replay.json.gz');assert replay['after']['closedDomainDrawnTriplets'] and len(replay['after']['closedDomainDrawnTriplets'])==11608
 assert replay['before']['outside']==replay['after']['outside']==8164251 and replay['currentExteriorXYZOrderedHashMatched']
 assert pins['expectedClosedDomainDrawnFacets']==len(replay['after']['closedDomainDrawnTriplets'])+len(raw)-len(oldraw)
 inp=read(V6/'input.json.gz');assert inp['currentManifest']['sha256']==legacy.CURRENT and inp['coarseCells']==[457,449,460,451] and inp['domain']==[-2477.5,-37.5,-2267.5,102.5]
 for q in inp['allCurrentInputRefs']:check(q)
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==legacy.CURRENT
 return pins,receipt,source,raw,source['candidateFaceProvenance'],inp,whole

def schema_only():
 pins,receipt,source,raw,pv,inp,whole=load()
 return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),completedNominationJob=receipt['jobId'],completeNativeFacets=len(raw),completeNewRawSHA256=source['completeNewRawCandidateSHA256'],expectedClosedDomainDrawnFacets=pins['expectedClosedDomainDrawnFacets'],all11580OldRawProvenancePositionIndexPrefixesAnd68ProtectedUnchanged=True,allFourCurrentCounterpartMapsAndOriginalHistoricalCompositionBound=True,completeNativeActorScope=6650,completeBasicRecords=1911,wholeAffectedBasicActors=52,owned13312Secondary392Native616FourWorldRolesHeld=True,historicalZeros23CrossingsAndAllNegativesRetained=True,completeOriginalGridNodes=841,completeNewGridSamplerNodes=1247,existingSixGuards516SitesUnchanged=True,wholeExteriorDrawCount=8164251,noProductionImportCaptureSourceCalculationDBLeaseWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,receipt,source,raw,pv,inp,whole=load();refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md')]
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__)) and prep['runtime']==ref(RUNTIME)
 closure=read(PROPOSAL/'actual-literal-runtime-closure-preflight.json');assert closure['computedImportsRejected'] and closure['completeAuditedLiteralImportClosure'] and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(RUNTIME.relative_to(ROOT))
 refs+=[ref(PROPOSAL/'actual-readonly-preparation.json'),ref(PROPOSAL/'actual-literal-runtime-closure-preflight.json')]+prep['evidenceRefs']+[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
 for folder,job in [(NOM_DOC,receipt['jobId']),(previous_capture.DOC,PREVIOUS_JOB)]:
  q=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',q)
  refs+=[ref(folder/'result.json')]+q['evidenceRefs']
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==legacy.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();fresh={**inp,'completedNominationJob':receipt['jobId'],'completeNewNativeFacets':len(raw),'completeNewRawSHA256':source['completeNewRawCandidateSHA256'],'completeNewPositionVertices':pins['completeNewPositionVertices'],'expectedClosedDomainDrawnFacets':pins['expectedClosedDomainDrawnFacets'],'previousPrivateCandidate':ref(previous_capture.DOC/'private-native-terrain-candidate.json.gz'),'fullScopeBindings':dict(currentWhole6650Scope=whole['latestFullFiniteNegativesVerbatim']['same6650WholeScope'],complete1911BasicRowsAnd52WholeAffected=ref(nomination.feasibility.DOC/'complete-full22-original-current-restoration-feasibility.json.gz'),latestFullFiniteNegatives=ref(nomination.feasibility.finite.DOC/'complete-actual-union-finite-delta.json.gz'),allActorFourWorldAndSourceRolesRemainPending=True)}
 save(DOC/'input.json.gz',fresh)
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT)),str(NOM_DOC.relative_to(ROOT))]
 with (DOC/'actual-production-replay.log').open('xb')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(command=command,exitCode=r.returncode,noLiveChanges=True));pulse(True)
 if r.returncode==0:
  replay=read(DOC/'actual-production-replay.json.gz');assert replay['currentManifestSHA256']==legacy.CURRENT and replay['startEndAllInputsVerified']
  for path,h in replay['inputHashes'].items():refs.append(dict(path=path,sha256=h))
  patch=read(DOC/'private-native-terrain-candidate.json.gz');assert not patch['nativeMesh'].get('sourceOverlap') and not patch['nativeMesh']['source'].get('numericalCoverageGap')
  assert patch['nativeMesh']['position']==source['newNativeMesh']['position'] and patch['nativeMesh']['index']==source['newNativeMesh']['index']
  position=np.asarray(patch['nativeMesh']['position'],dtype='<f8').reshape(-1,3);index=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);assert position[index].tobytes()==raw.tobytes()
  refs.append(ref(VALIDATOR));validator=legacy.module(VALIDATOR,'upton_full22_actual_unchanged_validator');failure=None
  try:validator.validate_native_mesh(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
  except AssertionError as e:failure=str(e)
  save(DOC/'real-validator-outcome.json',dict(passed=failure is None,actualAssertion=failure,unchangedValidator=ref(VALIDATOR),sourceOverlapApprovalNotCopied=True,noToleranceChanges=True,notPhysicalAcceptance=True))
  # New geometry's actual measurement only, never ideal/MAX/finite acceptance.
  old_parent=read(check(inp['retainedParent']));measured=measured_projection(patch,pv,inp['domain'],old_parent);surface=candidate_surface(patch,pv);draw=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3);multiset=verify_drawn_multiset(surface,draw)
  save(DOC/'new-scoped-geometry-measured-overlap.json.gz',dict(measured=measured,completeDrawnMultiset=multiset,newGeometryRequiresFreshReviewedContext=True,measuredSamplingNotCompleteIdealHeightProof=True,noCopiedApproval=True))
 else:save(DOC/'real-validator-outcome.json',dict(passed=False,notExecuted=True,actualRuntimeExitCode=r.returncode,noSamplerErrorWaiver=True,noApprovalCopied=True))
 save(DOC/'diagnostic.json.gz',dict(completedNomination=ref(NOM_DOC/'result.json'),runtimeExitCode=r.returncode,privateActualProductionCandidate=True,complete6650Scope1911Basic52WholeAffectedHeld=True,owned13312Secondary392Native616FourWorldRolesHeld=True,all68ProtectedAndSourceInventoriesRetained=True,historicalFullFiniteNegativesVerbatim=whole['latestFullFiniteNegativesVerbatim'],freshFullScopePackingCoverageFiniteOverlapMAXSeamRootRuntimeBrowserGatesPending=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 fence();refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 legacy.module(legacy.FREEZER,'upton_full22_actual_capture_freezer').freeze(BATCH,'full22-own-current-plane-fresh-actual-production-candidate-only',[check(q)for q in refs],dict(uids=legacy.OWNED+[legacy.SECONDARY,legacy.NATIVE],sourceOnly=True,privateCandidate=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--capture-full22-current-plane-private-candidate-only'in sys.argv and not DOC.exists() and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__)) and prep['runtime']==ref(RUNTIME)
 uids=legacy.OWNED+[legacy.SECONDARY,legacy.NATIVE,legacy.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-full22-current-production-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
