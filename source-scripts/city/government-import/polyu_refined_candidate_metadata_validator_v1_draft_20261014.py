"""UNEXECUTED fresh-context metadata only; requires ROOT review of completed evidence."""
from pathlib import Path
import json,sys,time,uuid,subprocess,copy
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from native_patch_resolution import finalize_overlap_evidence
import polyu_refined_candidate_overlap_max_caller_v1_draft_20261014 as prior
ref,check=prior.ref,prior.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-refined-candidate-metadata-validator-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 result=read(prior.DOC/'result.json');cert=read(prior.DOC/'ROOT-VERIFIED.json');assert result['jobId']==cert['jobId']==pins['completedOverlapJob']and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
 candidate=read(prior.capture.DOC/'private-native-terrain-candidate.json.gz');assert not candidate['nativeMesh'].get('sourceOverlap')and prior.canonical(candidate)==pins['candidateCanonicalSHA256']
 outcome=read(prior.DOC/'unchanged-validator-outcome.json');assert outcome['runtimeExitCode']==0 and not outcome['executed']and outcome['freshGeometryMetadataReviewPending']
 rays=read(prior.DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz');assert rays['samples']==len(rays['rows'])==64 and not rays['failedRows']and rays['maxError']<.01 and rays['startEndAllInputsVerified']and rays['noGeometryChanges']
 assert all(r['passed']and r['geometryBoundContractPass']and r['error']<1e-5 for r in rays['rows'])
 assert rays['completeCandidateFacets']==pins['completeMeshBinding']['completeIndexedFaces']and rays['completeUnusedPositionVertices']==pins['completeMeshBinding']['completePositionVertices']
 summary=read(prior.DOC/'complete-new-overlap-summary.json');measurement=summary['measurement'];assert measurement['nativeProjectedExcessM2']==pins['measuredProjectedExcessM2']and summary['completeCandidateFacets']==rays['completeCandidateFacets']
 pair_manifest=read(prior.DOC/'complete-old-and-new-pair-evidence-manifest.json');assert pair_manifest['inheritedPrefixRawBytesEqual']and pair_manifest['inheritedPrefixRawFacetCount']==148459 and pair_manifest['completePositiveAreaPairs']==summary['completePositiveAreaPairs']
 edge=read(prior.DOC/'complete-new-base-parent-edge-inventory.json.gz');assert edge['completePositionSlotsIncludingUnused']==rays['completeUnusedPositionVertices']and edge['unchangedExistingLimitM']==.01
 failure=read(prior.capture.DOC/'real-validator-outcome.json');assert failure['actualFailure']['message']=='Native terrain contains overlapping height surfaces'
 assert prior.ref(ROOT/'3d-viewer/city/data/terrain.json')==pins['actualBaseParent']
 return pins,result,candidate,summary,rays,failure

def schema_only():
 p,r,c,s,ray,f=load();return dict(passed=True,completedOverlapJob=r['jobId'],candidateCanonicalSHA256=p['candidateCanonicalSHA256'],measuredProjectedExcessM2=p['measuredProjectedExcessM2'],samples=64,noPairsRayActorsFiniteValidatorDBLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,result,candidate,summary,rays,failure=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert reservations.owns(lease)
 fence();DOC.mkdir();terrain=copy.deepcopy(candidate);auditpath=DOC/'fresh-exact-new-source-overlap-audit.json'
 sources=distinct_refs([ref(prior.capture.DOC/'private-native-terrain-candidate.json.gz'),ref(prior.DOC/'complete-new-source-plane-and-face-map.json.gz'),ref(prior.DOC/'complete-new-overlap-summary.json'),ref(prior.DOC/'complete-old-and-new-pair-evidence-manifest.json'),ref(prior.DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz'),pins['actualBaseParent']])
 save(auditpath,dict(stagedGeometrySha256=pins['candidateCanonicalSHA256'],nativeProjectedExcessM2=pins['measuredProjectedExcessM2'],float32HighestRayAgreement=rays,source=dict(files=sources),policy='Fresh exact mixed-source highest-native-surface: immutable recorded legacy layers and authenticated current-parent-plane compatible restoration/subdivision.',qualification='64 actual runtime/ray samples, not continuousMAX/physical/native/installation approval.',completePairEvidence=ref(prior.DOC/'complete-old-and-new-pair-evidence-manifest.json'),completedOverlapJob=result['jobId'],noOldApprovalTransferred=True,noGeometryChanges=True))
 terrain['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=pins['measuredProjectedExcessM2'],evidencePath=str(auditpath.relative_to(ROOT)),evidenceSHA256=ref(auditpath)['sha256'])
 final=finalize_overlap_evidence(terrain,auditpath);assert final['stagedGeometrySha256']==pins['candidateCanonicalSHA256']
 stripped=copy.deepcopy(terrain);stripped['nativeMesh'].pop('sourceOverlap');assert stripped==candidate and prior.canonical(stripped)==pins['candidateCanonicalSHA256']
 path=LOCAL/'private-new-geometry-source-overlap-reviewed.json';save(path,terrain);actual_failure=None
 try:prior.module(check(failure['unchangedValidator']),'polyu_refined_metadata_real_validator').validate_patch(terrain,read(check(pins['actualBaseParent'])))
 except (AssertionError,ValueError)as e:actual_failure=dict(type=type(e).__name__,message=str(e))
 save(DOC/'unchanged-validator-outcome.json',dict(executed=True,passed=actual_failure is None,actualFailure=actual_failure,metadataOnlyCandidate=ref(path),audit=ref(auditpath),underlyingCandidateCanonicalSHA256=pins['candidateCanonicalSHA256'],allFieldsExceptSourceOverlapExactlyEqual=True,unchangedValidator=failure['unchangedValidator'],actualBaseParent=pins['actualBaseParent'],noThresholdChange=True,noOldApprovalTransferred=True,physicalAccepted=False,installationApproved=False))
 refs=distinct_refs(refs+[ref(path)]+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 result=prior.module(prior.capture.FREEZER,'polyu_new_metadata_freezer').freeze(BATCH,'completed-exact-new-overlap64-context-metadata-only-unchanged-validator',[check(q)for q in refs],dict(uids=[q['uid']for q in read(prior.capture.DOC/'input.json.gz')['exact25CurrentForms']],sourceOnly=True,candidateOnly=True,newlyInstalled=0,physicalAccepted=False));fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),validatorPassed=actual_failure is None)),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
 if '--owned'in sys.argv:return owned()
 assert '--reviewed-metadata-only-validator-replay'in sys.argv and not DOC.exists()and not LOCAL.exists();load();resources=reservations.normalise(['immutable-source-proof:'+BATCH])
 claim=reservations.claim('polyu-new-metadata-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
