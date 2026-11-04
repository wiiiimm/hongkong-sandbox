"""Fresh private production replay of completed three own-layer subdivisions."""
from pathlib import Path
import sys,json,time,uuid,subprocess
import numpy as np
import upton_current_ring12_actual_production_capture_draft_v1_20261013 as previous_capture
from upton_two_original_complete_mask_current_nam_enclosure_draft_v6_20261013 import measured_projection,candidate_surface,verify_drawn_multiset
from run import ROOT,HERE,read,save,connect,reservations
from upton_own_layer_saved_nomination_binding_v1_20261013 import validate_own_layer_binding,HISTORICAL_FIELDS
legacy=previous_capture.legacy
ref,check=previous_capture.ref,previous_capture.check
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-three-own-layer-actual-production-capture-v1-20261013'
NOM_DOC=BASE/'government-xl-upton-remaining-three-own-layer-edge-nomination-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'upton_three_own_layer_actual_production_runtime_draft_v1_20261013.mjs'
V6=previous_capture.V6
JOB='85fed77eb03056242d5211b1a2c255e36e41b8fceb7de56a8cbb25b252a211aa'
VALIDATOR=HERE.parent/'island-detail-integration/native_terrain_validation.py'
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(NOM_DOC/'result.json');assert receipt['jobId']==JOB
 source=read(NOM_DOC/'private-own-layer-projected-edge-subdivision-nomination.json.gz');raw=np.asarray(source['candidateRawPositionTriplets'],dtype='<f8');pv=source['candidateFaceProvenance']
 assert source['previousRing12Nomination']==ref(previous_capture.NOM_DOC/'private-source-family-subdivision-nomination.json.gz')
 previous=read(check(source['previousRing12Nomination']));original=read(check(source['originalNomination']))
 assert raw.shape==(11580,3,3)and len(previous['candidateRawPositionTriplets'])==11577 and len(original['candidateRawPositionTriplets'])==11575
 assert validate_own_layer_binding(source,previous,original,targets={732,734,736},protected_count=68)
 inp=read(V6/'input.json.gz');assert inp['currentManifest']['sha256']==legacy.CURRENT and inp['coarseCells']==[457,449,460,451]and inp['domain']==[-2477.5,-37.5,-2267.5,102.5]
 for q in inp['allCurrentInputRefs']:check(q)
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==legacy.CURRENT
 return pins,receipt,source,raw,pv,inp
def schema_only():
 p,r,s,raw,pv,i=load()
 return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),completedNominationJob=JOB,completeNativeFacets=11580,expectedClosedDomainDrawnFacets=11608,new11577To11580MappingComplete=True,all11574OtherRawProvenanceAliasesAnd68ProtectedByteEqual=True,cumulativeOriginalMappingComplete=True,historicalNominationFieldsPreservedAsContextOnly=list(HISTORICAL_FIELDS),noProductionImportCaptureOrLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,source,raw,pv,inp=load();refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md')]+receipt['evidenceRefs']
 preparation=read(PROPOSAL/'actual-readonly-preparation.json');assert preparation['passed']and preparation['caller']==ref(Path(__file__))and preparation['runtime']==ref(RUNTIME)
 closure=read(PROPOSAL/'literal-runtime-closure-preflight.json');assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'and closure['computedImportsRejected']and closure['completeAuditedLiteralImportClosure']and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(RUNTIME.relative_to(ROOT))
 refs+=[ref(PROPOSAL/'actual-readonly-preparation.json'),ref(PROPOSAL/'literal-runtime-closure-preflight.json')]+preparation['evidenceRefs']+[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 for q in refs:check(q);pulse()
 DOC.mkdir(parents=True);save(DOC/'input.json.gz',inp)
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT)),str(NOM_DOC.relative_to(ROOT))]
 with (DOC/'actual-production-replay.log').open('xb')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(command=command,exitCode=r.returncode,noLiveChanges=True));pulse(True)
 if r.returncode==0:
  replay=read(DOC/'actual-production-replay.json.gz');assert replay['currentManifestSHA256']==legacy.CURRENT and replay['startEndAllInputsVerified']
  for path,h in replay['inputHashes'].items():refs.append(dict(path=path,sha256=h))
  patch=read(DOC/'private-native-terrain-candidate.json.gz');assert not patch['nativeMesh'].get('sourceOverlap')and not patch['nativeMesh']['source'].get('numericalCoverageGap')
  position=np.asarray(patch['nativeMesh']['position'],dtype='<f8').reshape(-1,3);index=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);assert position[index].tobytes()==raw.tobytes()
  refs.append(ref(VALIDATOR));validator=legacy.module(VALIDATOR,'upton_three_own_layer_real_validator');failure=None
  try:validator.validate_native_mesh(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
  except AssertionError as e:failure=str(e)
  save(DOC/'real-validator-outcome.json',dict(passed=failure is None,actualAssertion=failure,unchangedValidator=ref(VALIDATOR),sourceOverlapApprovalNotCopied=True,noToleranceChanges=True,notPhysicalAcceptance=True))
  # Fresh changed-geometry measurement only; no ideal ancestor/MAX/actor replay
  # and no automatic approval for this new canonical geometry.
  old_parent=read(check(inp['retainedParent']));measured=measured_projection(patch,pv,inp['domain'],old_parent);surface=candidate_surface(patch,pv);draw=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3);multiset=verify_drawn_multiset(surface,draw)
  save(DOC/'new-scoped-geometry-measured-overlap.json.gz',dict(measured=measured,completeDrawnMultiset=multiset,newGeometryRequiresFreshReviewedContext=True,measuredSamplingNotCompleteIdealHeightProof=True,noCopiedApproval=True))
 else:
  save(DOC/'real-validator-outcome.json',dict(passed=False,notExecuted=True,actualRuntimeExitCode=r.returncode,noSamplerErrorWaiver=True,noApprovalCopied=True))
 save(DOC/'diagnostic.json.gz',dict(completedNomination=ref(NOM_DOC/'result.json'),runtimeExitCode=r.returncode,privateActualProductionCandidate=True,completeAffectedOrdinaryCoverageForeignChecksUnexecuted=True,full52BasicAnd79882AndSecondaryHeldAsForeign=True,historicalNegativesRetainedAtTheirExactOriginalEvidence=True,historicalNominationFieldsNotCurrentGeometryClaims=list(HISTORICAL_FIELDS),freshNewGeometryFullScopeGatesPending=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==legacy.CURRENT;pulse(True)
 legacy.module(legacy.FREEZER,'upton_three_own_layer_actual_capture_freezer').freeze(BATCH,'three-own-layer-actual-production-candidate-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=legacy.OWNED+[legacy.SECONDARY,legacy.NATIVE],sourceOnly=True,privateCandidate=True,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--capture-three-own-layer-private-candidate-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 load();preparation=read(PROPOSAL/'actual-readonly-preparation.json');assert preparation['passed']and preparation['caller']==ref(Path(__file__))and preparation['runtime']==ref(RUNTIME)
 uids=legacy.OWNED+[legacy.SECONDARY,legacy.NATIVE,legacy.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-three-own-layer-production-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
