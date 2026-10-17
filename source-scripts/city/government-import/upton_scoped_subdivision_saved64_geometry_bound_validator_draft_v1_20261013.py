"""UNEXECUTED fresh scoped geometry MAX64 and conditional metadata replay."""
from pathlib import Path
import sys,json,copy,time,uuid,subprocess
import numpy as np
import upton_v6_saved64_actual_max_geometry_bound_validator_draft_v1_20261013 as previous
import upton_source35676_35677_actual_production_capture_draft_v1_20261013 as capture
from run import ROOT,HERE,read,save,connect,reservations
from native_patch_resolution import finalize_overlap_evidence
ref,check=previous.ref,previous.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-scoped-subdivision-saved64-geometry-bound-validator-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'upton_scoped_subdivision_saved64_max_runtime_draft_v1_20261013.mjs'
GEOMETRY='f878d03d1f2d03a193a3faaeec0c116640356c246b7e3d1d5cdc1f5657d80b36';EXCESS=2.2535033273961744
JOB='8f0fe445fdc53797987668c1d3f7cde2b643c68625872e7c3d7f1d9aaf201f77'
def arrays(patch):
 mesh=patch['nativeMesh'];p=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3);i=np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3);return p[i]
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');assert previous.canonical(patch)==GEOMETRY and not patch['nativeMesh'].get('sourceOverlap')
 measured=read(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured'];assert measured['candidateGeometryCanonicalSHA256']==GEOMETRY and measured['nativeProjectedExcessM2']==EXCESS and measured['completeCandidateFaces']==11576
 assert measured['float32HighestRayAgreement']['samples']==len(measured['float32HighestRayAgreement']['rows'])==64
 nomination=read(capture.nomination.DOC/'private-source-family-subdivision-nomination.json.gz');raw=arrays(patch);assert raw.tobytes()==np.asarray(nomination['candidateRawPositionTriplets'],dtype='<f8').tobytes()
 old_raw=arrays(read(previous.V6/'private-native-terrain-candidate.json.gz'));old_measured=read(previous.V6/'new-geometry-measured-overlap-and-exact-height-attribution.json.gz')['measured'];ancestor=read(previous.ANCESTOR/'complete-2128-saved-area-pair-source-ancestor-classification.json.gz');assert ancestor['completeSavedPositiveAreaPairs']==len(ancestor['rows'])==2128
 inverse={j:r['oldCandidateFace']for r in nomination['completeOldNewIndexMapping']for j in r['newCandidateFaces']};assert set(inverse)==set(range(11576))
 old_pairs={(p['leftFace'],p['rightFace']):p for p in old_measured['allProjectedIntersectingPairs']if p['projectedDimension']=='area'}
 old_classes={(r['fullSavedCandidatePairProof']['leftFace'],r['fullSavedCandidatePairProof']['rightFace']):r for r in ancestor['rows']}
 new_pairs=[p for p in measured['allProjectedIntersectingPairs']if p['projectedDimension']=='area'];assert len(new_pairs)==len(old_pairs)==len(old_classes)==2128
 mapped=[];seen=set()
 for p in new_pairs:
  a,b=p['leftFace'],p['rightFace'];i,j=inverse[a],inverse[b];assert i<j and 380 not in (i,j) # A changed positive-area pair needs a new bounded review, never inheritance.
  key=(i,j);assert key in old_pairs and key in old_classes and key not in seen;seen.add(key)
  assert raw[a].tobytes()==old_raw[i].tobytes()and raw[b].tobytes()==old_raw[j].tobytes()
  assert raw[a].astype('<f4').tobytes()==old_raw[i].astype('<f4').tobytes()and raw[b].astype('<f4').tobytes()==old_raw[j].astype('<f4').tobytes()
  old_pair=old_pairs[key];assert p['measuredAreaM2']==old_pair['measuredAreaM2']and p['representativePointHeightMeasurements']==old_pair['representativePointHeightMeasurements']
  mapped.append(dict(newCandidateFaces=[a,b],oldCandidateFaces=[i,j],newSavedMeasuredPairVerbatim=p,oldSavedMeasuredPairVerbatim=old_pair,oldSourceAncestorClassificationVerbatim=old_classes[key],bothRawAndFloat32TripletsExactlyEqual=True,oldLabelsRemainOldGeometryContext=True,noOldGeometryApprovalTransferred=True))
 assert seen==set(old_pairs)and ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==previous.prior.CURRENT
 return pins,patch,measured,nomination,mapped
def schema_only():
 pins,patch,m,n,rows=load();return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),newGeometryCanonicalSHA256=GEOMETRY,completeNativeFaces=11576,areaPairCorrespondence=len(rows),actualNewSavedSites=64,noPairGeometryMAXRayValidatorDBLeaseOrApproval=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,original,m,nomination,mapped=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
 closure=read(PROPOSAL/'literal-runtime-closure-preflight.json');assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'and closure['computedImportsRejected']and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(RUNTIME.relative_to(ROOT))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json'),ref(PROPOSAL/'literal-runtime-closure-preflight.json')]+prep['evidenceRefs']+[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
 for folder,job in [(capture.DOC,JOB),(previous.ANCESTOR,'9fa949d029e3c40b6bca3a24883b908ada421bd5fba48734eab9a8a6222805ae')]:
  receipt=read(folder/'result.json');assert receipt['jobId']==job
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 for q in refs:check(q);pulse()
 DOC.mkdir(parents=True);save(DOC/'complete2128-exact-new-old-area-pair-correspondence.json.gz',dict(rows=mapped,completePairs=2128,changedSource35676TrianglesNotAreaPairs=True,newGeometryRequiresFreshActualRuntimeAndReview=True,noApprovalCopied=True))
 candidate=capture.DOC/'private-native-terrain-candidate.json.gz';measure=capture.DOC/'new-scoped-geometry-measured-overlap.json.gz';save(DOC/'input.json.gz',dict(currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),candidate=ref(candidate),measuredOverlap=ref(measure),geometryCanonicalSHA256=GEOMETRY,runtimeInputRefs=pins['inputRefs']+[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]))
 with (DOC/'actual-saved64-runtime.log').open('xb')as log:run=subprocess.run(['node',str(RUNTIME),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(exitCode=run.returncode,noGeometryChanges=True));pulse(True)
 outcome=dict(executed=False,reason='Actual runtime failed or saved-site MAX/ray disagreement',rawValidatorFailure=ref(capture.DOC/'real-validator-outcome.json'),noPhysicalOrInstallationApproval=True)
 if run.returncode==0:
  rays=read(DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz');assert rays['samples']==len(rays['rows'])==64 and rays['completeCandidateFacets']==11576 and rays['startEndAllInputsVerified']and rays['noGeometryChanges']
  refs+=[dict(path=k,sha256=v)for k,v in rays['inputHashes'].items()]+[dict(path=k,sha256=v)for k,v in rays['completeRecursiveProductionModuleClosure']['inputHashes'].items()]
  if not rays['failedRows']and rays['maxError']<.01:
   terrain=copy.deepcopy(original);sources=[ref(candidate),ref(measure),ref(capture.nomination.DOC/'private-source-family-subdivision-nomination.json.gz'),nomination['originalSourceTriplets'],ref(previous.ANCESTOR/'complete-2128-saved-area-pair-source-ancestor-classification.json.gz'),ref(DOC/'complete2128-exact-new-old-area-pair-correspondence.json.gz'),ref(ROOT/'3d-viewer/city/data/terrain.json'),ref(ROOT/'3d-viewer/city/data/government-native-79882-0.json')]
   for q in sources:check(q)
   audit=dict(stagedGeometrySha256=GEOMETRY,nativeProjectedExcessM2=EXCESS,float32HighestRayAgreement=rays,source=dict(files=sources),policy='Exact ROOT-reviewed scoped original-source35676 subdivision with mixed original-TIN/current terrain layers; highest native surface.',qualification='Geometry-bound metadata only; samples are not complete continuous MAX, physical, root or installation approval.',complete2128ByteBoundNewOldSourcePairCorrespondence=ref(DOC/'complete2128-exact-new-old-area-pair-correspondence.json.gz'),oldAncestorIdealHeightsDoNotClaimBitwiseJSEquality=True,noOldGeometryApprovalTransferred=True,sourceGeometryOrPoseChanges=0)
   auditpath=DOC/'geometry-bound-scoped-mixed-source-overlap-audit.json';save(auditpath,audit);terrain['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=EXCESS,evidencePath=str(auditpath.relative_to(ROOT)),evidenceSHA256=ref(auditpath)['sha256']);final=finalize_overlap_evidence(terrain,auditpath);assert final['stagedGeometrySha256']==GEOMETRY
   stripped=copy.deepcopy(terrain);stripped['nativeMesh'].pop('sourceOverlap');assert stripped==original and previous.canonical(stripped)==GEOMETRY
   path=LOCAL/'private-scoped-upton-geometry-bound-overlap-reviewed.json';save(path,terrain);failure=None
   try:previous.prior.load_module(previous.VALIDATOR,'upton_scoped_same_native_validator').validate_native_mesh(terrain,read(ROOT/'3d-viewer/city/data/terrain.json'))
   except AssertionError as e:failure=str(e)
   outcome=dict(executed=True,passed=failure is None,actualAssertion=failure,unchangedValidator=ref(previous.VALIDATOR),actualBaseParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),rawValidatorFailure=ref(capture.DOC/'real-validator-outcome.json'),metadataOnlyCandidate=ref(path),audit=ref(auditpath),allFieldsExceptSourceOverlapExactlyEqual=True,noToleranceOrSamplerChanges=True,noPhysicalOrInstallationApproval=True);refs.append(ref(path))
 save(DOC/'unchanged-base-parent-validator-outcome.json',outcome);save(DOC/'diagnostic.json.gz',dict(validator=outcome,newGeometryCanonicalSHA256=GEOMETRY,measuredProjectedExcessM2=EXCESS,noConstructorPairOrActorReplay=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==previous.prior.CURRENT;pulse(True)
 previous.prior.load_module(previous.prior.FREEZER,'upton_scoped_max_freezer').freeze(BATCH,'scoped-saved64-production-MAX-geometry-bound-metadata-validator-diagnostic',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=previous.prior.UIDS+[previous.prior.NATIVE],sourceOnly=True,geometryChanges=0,validatorOutcome=outcome,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-scoped-saved64-max-and-reviewed-validator-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=previous.prior.UIDS+[previous.prior.SECONDARY,previous.prior.NATIVE,previous.prior.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-scoped-max-metadata-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
