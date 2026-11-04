"""UNEXECUTED metadata-only inherited-overlap audit and unchanged validator replay.
No terrain numeric edits; completed pair/ray/actor proofs are reused by exact pins.
"""
from pathlib import Path
import ast,copy,json,sys,time,uuid,subprocess
from run import ROOT,HERE,read,save,connect,reservations
from upton_inherited_overlap_boundary_draft_v1_20261012 import ref,check,module,CURRENT,UIDS,FOREIGN
from native_patch_resolution import finalize_overlap_evidence
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-geometry-bound-inherited-overlap-replay-v1-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json'
RECON=BASE/'government-xl-upton-actual-full-draw-ruling-reconciliation-v1-20261012'
PRIOR=BASE/'government-xl-upton-inherited-ring-overlap-finite-boundary-v1-20261012'
NOM=BASE/'government-xl-upton-original-tin-current-ring-join-nomination-v2-20261012'
AUD=BASE/'government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012'
CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012'
VALIDATOR=HERE.parent/'island-detail-integration/native_terrain_validation.py'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
RECEIPTS=[(RECON,'0e2e21303c85bf1931bb3634db092af8c48a6cd2d5d678c665d605ea4321a7d6','cb594ac5bb379566af66fdf75ead2e26f272be10848139bf717667974ca8729e'),(PRIOR,'8afdd174bc4cbf629535df003ea134826b938657fdee7af4b0be390d8cd92dcb','42f01d81e542e731edbf49b9eeb2bc96d6d60cb1a0e99e57117ff50c677722be'),(AUD,'fbee12e07218f022deb4af6244a2487c6ce751da40fc5fe326c38c6bcef88a5e','75b9bf7514c3f4811824061a2a754aa134458bba498a677a3fa6d75a89284fcc'),(NOM,'0514c963b8c79bae794a1bcd2683730f2af78788245e05434ce1a38f66d72427','d3ef62c5a2534b0381cdbf05c883f6300e536ba2083a86f11dc489f89cf58219')]
def code_paths():
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review'];seen=set();todo=[Path(__file__),VALIDATOR,FREEZER]
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return sorted(seen)
def schema_only():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['inputRefs']:check(q)
 for folder,jid,h in RECEIPTS:
  r=read(folder/'result.json');assert r['jobId']==jid and ref(folder/'result.json')['sha256']==h
 review=read(RECON/'existing-overlap-approval-contract-review-inputs.json');measure=read(AUD/'measured-projection-and-parent-edge.json.gz');rays=read(AUD/'actual-native-sampler-ray-findings.json.gz');patch=read(check(review['candidate']))
 assert 'sourceOverlap'not in patch['nativeMesh']
 assert review['wholeCandidateGeometryCanonicalSHA256']==measure['candidateGeometryCanonicalSHA256']=='86e403af01c5efcfeca92cd45a6d720c03cc12e2c07430f245f1041f05a6cf1f'
 assert review['measuredProjectedExcessM2']==measure['nativeProjectedExcessM2']>0
 assert rays['samples']==review['existingRaySamples']==len(rays['rows'])==64 and not rays['failedRows']and rays['maxError']==review['existingRayMaxError']<.01
 assert rays['startEndAllInputsVerified']and rays['noGeometryChanges']
 assert read(AUD/'real-validator-outcome.json')['actualAssertion']=='Native terrain contains overlapping height surfaces'
 overlaps=read(PRIOR/'complete-ring-overlap-inheritance.json.gz');assert overlaps['completePairs']==len(overlaps['rows'])==1260
 assert all(q['exactInheritance']['projectionInherited']and q['completeDrawnUnionIdealAffineMax']['proof']['completeIdealAffineMaxRegionCovered']for q in overlaps['rows'])
 changes=read(RECON/'fifteen-saved-affine-change-existing-contract.json.gz');assert len(changes['rows'])==15 and all(q['belowExistingSamplerAudit01MContract']for q in changes['rows'])
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),completeInheritedAreaPairs=1260,actualSampledRayRows=64,noProjectionRayActorOrSourceDecode=True,noDBOrLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 schema_only();refs=[ref(p)for p in code_paths()]+[ref(PROPOSAL/p)for p in ['METHOD.md','draft-pins.json','schema-preflight.json']]
 for folder,jid,h in RECEIPTS:
  r=read(folder/'result.json');assert r['jobId']==jid and ref(folder/'result.json')['sha256']==h
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',r)
  for q in r['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 for q in read(PROPOSAL/'draft-pins.json')['inputRefs']:check(q);refs.append(q)
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();review=read(RECON/'existing-overlap-approval-contract-review-inputs.json');source=check(review['candidate']);original=read(source);terrain=copy.deepcopy(original);assert 'sourceOverlap'not in terrain['nativeMesh']
 nom=read(NOM/'complete-nominations-before-guards.json.gz');rays=read(check(review['actualProductionSamplerRayEvidence']));measure=read(AUD/'measured-projection-and-parent-edge.json.gz')
 source_files=[ref(source),ref(NOM/'complete-nominations-before-guards.json.gz'),nom['allSourceOriginalTriplets'],nom['allCurrentTriplets'],ref(PRIOR/'complete-current-source-attribution.json.gz'),ref(RECON/'complete-actual-draw-attribution.json.gz'),ref(ROOT/'3d-viewer/city/data/terrain.json'),ref(ROOT/'3d-viewer/city/data/government-native-79882-0.json')]
 for q in source_files:check(q)
 audit=dict(stagedGeometrySha256=review['wholeCandidateGeometryCanonicalSHA256'],nativeProjectedExcessM2=review['measuredProjectedExcessM2'],float32HighestRayAgreement=copy.deepcopy(rays),source=dict(files=source_files),policy='Retain the exact reviewed candidate facets and select the highest native surface; all positive-area pairs are inherited captured-current-ring fragments.',qualification='Private geometry-bound metadata review of an explicitly computed original-TIN/current-exterior join; not an untouched-government-terrain or whole-actor approval.',full1260ProjectedInheritance=review['fullCurrentInheritance'],fifteenIdealAffineRanges=review['fifteenFullAffineRanges'],fullActualDrawReconciliation=ref(RECON/'complete-actual-ruling-reconciliation.json.gz'),sampledRayEvidenceReusedWithoutRerun=True,idealAffineProofIsNotBitwiseJSSamplerEquality=True,all433RawFixedBandNegativesRetained=True,noGlobalTopologyAdmissionRequirement=True,noPhysicalOrInstallationApproval=True)
 DOC.mkdir(parents=True);audit_path=DOC/'geometry-bound-inherited-overlap-audit.json';save(audit_path,audit)
 terrain['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=audit['nativeProjectedExcessM2'],evidencePath=str(audit_path.relative_to(ROOT)),evidenceSHA256=ref(audit_path)['sha256'])
 finalized=finalize_overlap_evidence(terrain,audit_path);assert finalized['stagedGeometrySha256']==review['wholeCandidateGeometryCanonicalSHA256']
 without=copy.deepcopy(terrain);without['nativeMesh'].pop('sourceOverlap');assert without==original
 path=LOCAL/'private-government-native-upton-overlap-reviewed.json';save(path,terrain);assert read(path)==terrain
 base=read(ROOT/'3d-viewer/city/data/terrain.json');failure=None
 try:module(VALIDATOR,'upton_unchanged_overlap_validator').validate_native_mesh(terrain,base)
 except AssertionError as e:failure=str(e)
 outcome=dict(passed=failure is None,actualAssertion=failure,unchangedValidator=ref(VALIDATOR),actualParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),priorRawFailure=ref(AUD/'real-validator-outcome.json'),onlySourceOverlapMetadataAdded=True,noCoverageOrOverlapToleranceChanges=True,noActorOrPhysicalAcceptance=True)
 save(DOC/'unchanged-validator-outcome.json',outcome)
 proof=dict(originalCandidate=ref(source),metadataOnlyCandidate=ref(path),geometryBoundOverlapAudit=ref(audit_path),allFieldsExceptSourceOverlapExactlyEqual=True,allPositionIndexGridGeorefRoutingVegetationValuesUnchanged=True,originalCanonicalGeometrySHA256=finalized['stagedGeometrySha256'],completeActualGroundBeforeAfterReceipt=ref(NOM/'actual-production-replay.json.gz'),fullOwnedNativeBasicClearanceReused=review['completeOwnedNativeBasicOrdinaryEvidence'],sampledActualRayProofReused=review['actualProductionSamplerRayEvidence'],fullActualBoundaryProofReused=ref(RECON/'complete-actual-ruling-reconciliation.json.gz'),allEarlierFailuresRetained=True,terrainNumericGeometryChanges=0,physicalAccepted=False,installationApproved=False,validator=outcome)
 save(DOC/'metadata-only-proof.json',proof);save(DOC/'diagnostic.json.gz',proof)
 refs+=[ref(p)for p in DOC.iterdir()if p.is_file()]+[ref(path)];fence();module(FREEZER,'upton_inherited_overlap_final_freezer').freeze(BATCH,'private-geometry-bound-inherited-overlap-metadata-unchanged-validator',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS,currentManifestSHA256=CURRENT,sourceOnly=True,candidateOnly=True,metadataOnly=True,unchangedValidatorPassed=failure is None,unchangedValidatorFailure=failure,terrainGeometryChanges=0,physicalAccepted=False,newlyInstalled=0));print(json.dumps(outcome),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--metadata-only-overlap-validator-replay'in sys.argv and not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-overlap-metadata-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
