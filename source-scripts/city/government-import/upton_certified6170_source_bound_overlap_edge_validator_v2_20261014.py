"""ROOT-only fresh860 canonical edges, source-reviewed overlap metadata/real validator.
No source geometry edits, copied approval, extra tolerances or physical admission.
"""
from pathlib import Path
import copy,json,sys,time,uuid,subprocess
import numpy as np
import upton_certified6170_actual_production_capture_v1_20261014 as capture
import upton_certified6170_saved_actual_union_delta_v1_20261014 as finite
import upton_certified6170_saved_area_pair_ancestor_v1_20261014 as pairs
import upton_certified6170_saved64_actual_max_v1_20261014 as maximum
from upton_parent_edge_validator_sample_v1_20261014 import parent_grid_sampler
from exact_distinct_evidence_refs_v1_20261014 import check_distinct_refs
from upton_v6_saved64_actual_max_geometry_bound_validator_draft_v1_20261013 import canonical
from native_patch_resolution import finalize_overlap_evidence
from run import ROOT,HERE,read,save,connect,reservations
ref,check=capture.ref,capture.check;BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-certified6170-source-bound-overlap-edge-validator-v2-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
FOLDERS=[capture.DOC,finite.DOC,pairs.DOC,maximum.DOC]
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 for folder,row in zip(FOLDERS,pins['completedReceipts']):
  result=read(folder/'result.json');v=read(folder/'ROOT-VERIFIED.json');assert ref(folder/'result.json')==row['result'] and result['jobId']==row['jobId']==v['jobId'] and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
 _,_,nom,raw,pv,inp,whole=capture.load();patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');geometry=canonical(patch);assert geometry==pins['canonicalGeometrySHA256'] and not patch['nativeMesh'].get('sourceOverlap')
 measured=read(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured'];assert measured['candidateGeometryCanonicalSHA256']==geometry and measured['completeCandidateFaces']==len(raw)==pins['completeNativeFacets'] and measured['nativeProjectedExcessM2']==pins['actualMeasuredExcessM2']
 f=read(finite.DOC/'complete-actual-union-finite-delta.json.gz');assert f['newGroundSHA256']==pins['actualGroundSHA256'] and f['completeNewDrawnFaces']==pins['completeDrawnFaces']==11645 and f['completeNativeActorScope']==6650
 assert [r['uid']for r in f['actors']]==finite.baseline.OWNED+[finite.baseline.SECONDARY,finite.baseline.NATIVE] and len(f['completeBasicRows'])==1911
 for actor in f['actors']:
  assert [w['mode']for w in actor['worlds']]==list(finite.baseline.MODES)
  for w in actor['worlds']:
   assert not w['findings']['currentClearCandidateUnproved']
   if actor['uid']in finite.baseline.OWNED:assert not w['findings']['candidateOrdinaryUnproved'] and not w['findings']['candidateUncovered']
 assert sum('findings'in r for r in f['completeBasicRows'])==52
 for r in f['completeBasicRows']:
  if 'findings'in r:
   for w in r['findings']['worlds']:assert not w['findings']['currentClearCandidateUnproved']
 assert f['secondaryHeldAsForeignReceivesNoSupportCredit'] and f['allFacetAndBodyRoleObligationsRemain'] and f['allHistoricalZeroAnd23CrossingObligations'] and not f['physicalAccepted'] and not f['installationApproved'];check(f['allZerosAnd23CrossingsRetained'])
 packet=read(pairs.DOC/'complete-saved-area-pair-source-ancestor-continuation.json.gz');area=[r for r in measured['allProjectedIntersectingPairs']if r['projectedDimension']=='area'];assert packet['completeSavedPositiveAreaPairs']==len(packet['rows'])==len(area)==pins['completeAreaPairs'] and packet['unresolvedRows']==0 and packet['completeSourceFacets']==122721 and packet['completeCurrentFacets']==9214
 source_refs=[]
 for saved,row in zip(area,packet['rows']):
  assert row['newSavedMeasuredPairVerbatim']==saved and row['noCopiedApproval'] and not row['physicalAccepted'] and not row['installationApproved']
  classified=row.get('freshSourceAncestorClassification',row.get('oldSourceAncestorClassificationVerbatim'));assert classified is not None and classified['noCopiedApproval'] and not classified['physicalAccepted'] and not classified['installationApproved']
  assert len(classified['completeAncestors'])==2
  for ancestor in classified['completeAncestors']:
   source_refs.append(ancestor['sourceInput'])
 sources=check_distinct_refs(source_refs,check)
 rays=read(maximum.DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz');assert rays['samples']==len(rays['rows'])==64 and not rays['failedRows'] and rays['maxError']<.01 and rays['startEndAllInputsVerified'] and rays['completeCandidateFacets']==len(raw) and rays['noGeometryChanges']
 pos=np.asarray(patch['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);idx=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);assert pos[idx].tobytes()==raw.tobytes() and len(pos)==pins['completePositionVertices']
 assert len(measured['parentEdgeVertices'])==pins['canonicalEdgeOccurrences']==860 and measured['parentEdgeExistingLimitM']==.01
 review=read(PROPOSAL/'source-bound-overlap-review-inputs.json');assert review['preparedFor']=='ROOT' and review['codePreparedBy']=='Codex' and review['canonicalGeometrySHA256']==geometry and review['allCompleteExactPairClassesAndOldNegativesRetained'] and review['onlyMetadataHighestNativeSurface'] and review['physicalAccepted'] is False and review['installationApproved'] is False
 assert review['completedReceipts']==pins['completedReceipts'] and review['completeAreaPacket']==ref(pairs.DOC/'complete-saved-area-pair-source-ancestor-continuation.json.gz') and review['actualMAX']==ref(maximum.DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz') and review['actualFullFinite']==ref(finite.DOC/'complete-actual-union-finite-delta.json.gz')
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT
 return pins,patch,measured,raw,pv,inp,whole,f,packet,rays,pos,idx,sources,review

def schema_only():
 p,patch,m,raw,pv,inp,whole,f,packet,rays,pos,idx,sources,review=load();return dict(passed=True,caller=ref(Path(__file__)),canonicalGeometrySHA256=p['canonicalGeometrySHA256'],completeNativeFacets=len(raw),completeDrawnFaces=p['completeDrawnFaces'],fullActorScope=6650,completeBASIC=1911,wholeAffectedBASIC=52,completeAreaPairs=len(packet['rows']),actualMAXSites=64,savedEdgeOccurrences=860,noEdgeSamplerValidatorApprovalGeometryDBLeaseWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,original,m,raw,pv,inp,whole,f,packet,rays,pos,idx,sources,review=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__)) and prep['literalValidatorSampleASTExactlyUnchanged']
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json'),ref(PROPOSAL/'source-bound-overlap-review-inputs.json')]+prep['evidenceRefs']
 for folder in FOLDERS:
  receipt=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();base=read(ROOT/'3d-viewer/city/data/terrain.json');sample=parent_grid_sampler(base);rows=[];domain=inp['domain'];incidents={}
 for face,ids in enumerate(idx):
  for corner,k in enumerate(ids):incidents.setdefault(int(k),[]).append(dict(face=face,corner=corner,completeProvenance=pv[face]))
 for k,(x,y,z)in enumerate(pos):
  if min(abs(x-domain[0]),abs(x-domain[2]),abs(z-domain[1]),abs(z-domain[3]))>=.002:continue
  h=sample(float(x),float(z));gap=abs(float(y)-h);rows.append(dict(positionVertex=k,actualPackedXYZ=[float(x),float(y),float(z)],completeIncidents=incidents.get(k,[]),canonicalParentHeight=h,absoluteGap=gap,existingStrictPointZeroOnePass=gap<.01));pulse()
 assert len(rows)==860;edge=dict(rows=rows,allPassed=all(r['existingStrictPointZeroOnePass']for r in rows),maximumGap=max(r['absoluteGap']for r in rows),fullPositionIncludingUnusedInventory=True,canonicalParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),unchangedLiteralValidatorSampler=True,noNativeMaximumOrWrongParentExtrapolationSubstitute=True,existingLimitM=.01,physicalAccepted=False,installationApproved=False);save(DOC/'fresh860-canonical-parent-edge-guard.json.gz',edge)
 outcome=dict(passed=False,notExecuted=True,reason='Fresh canonical edge guard failed',rawValidatorFailure=ref(capture.DOC/'real-validator-outcome.json'),noThresholdWaiver=True)
 if edge['allPassed']:
  source_files=sources+[ref(capture.DOC/'private-native-terrain-candidate.json.gz'),ref(capture.NOM_DOC/'private-three-safe-current-certified-6170-nomination.json.gz'),ref(pairs.DOC/'complete-saved-area-pair-source-ancestor-continuation.json.gz'),ref(finite.DOC/'complete-actual-union-finite-delta.json.gz'),ref(maximum.DOC/'actual-saved64-full-candidate-native-max-ray-findings.json.gz'),ref(DOC/'fresh860-canonical-parent-edge-guard.json.gz'),ref(ROOT/'3d-viewer/city/data/terrain.json'),ref(ROOT/'3d-viewer/city/data/government-native-79882-0.json'),ref(PROPOSAL/'source-bound-overlap-review-inputs.json')]
  for q in source_files:check(q)
  audit=dict(stagedGeometrySha256=pins['canonicalGeometrySHA256'],nativeProjectedExcessM2=pins['actualMeasuredExcessM2'],float32HighestRayAgreement=rays,source=dict(files=source_files),policy='Highest native surface of exact source-reviewed computed terrain; preserve original TIN/current ancestors and all certified packed fragments.',qualification='Metadata-only approval under existing sourceOverlap contract, all pair classification negatives retained; not untouched government terrain or source body/root/whole model acceptance.',completeExactAreaPairs=ref(pairs.DOC/'complete-saved-area-pair-source-ancestor-continuation.json.gz'),fullActualFinite=ref(finite.DOC/'complete-actual-union-finite-delta.json.gz'),freshCanonical860=ref(DOC/'fresh860-canonical-parent-edge-guard.json.gz'),sourceBoundReviewInputs=ref(PROPOSAL/'source-bound-overlap-review-inputs.json'),allOldKernelHashesAndClassificationLabelsPreserved=True,noGeometryOrPoseOrThresholdChanges=True,physicalAccepted=False,installationApproved=False)
  auditpath=DOC/'geometry-bound-source-reviewed-overlap-audit.json';save(auditpath,audit);terrain=copy.deepcopy(original);terrain['nativeMesh']['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=pins['actualMeasuredExcessM2'],evidencePath=str(auditpath.relative_to(ROOT)),evidenceSHA256=ref(auditpath)['sha256']);final=finalize_overlap_evidence(terrain,auditpath);assert final['stagedGeometrySha256']==pins['canonicalGeometrySHA256']
  bare=copy.deepcopy(terrain);bare['nativeMesh'].pop('sourceOverlap');assert bare==original;path=LOCAL/'private-upton-certified6170-overlap-reviewed.json';save(path,terrain);failure=None
  try:capture.legacy.module(capture.VALIDATOR,'upton_certified6170_unchanged_native_validator').validate_native_mesh(terrain,base)
  except AssertionError as e:failure=str(e)
  outcome=dict(passed=failure is None,actualAssertion=failure,unchangedValidator=ref(capture.VALIDATOR),canonicalParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),rawValidatorFailure=ref(capture.DOC/'real-validator-outcome.json'),metadataOnlyCandidate=ref(path),audit=ref(auditpath),allFieldsExceptSourceOverlapExactlyEqual=True,noToleranceOrGeometryChanges=True,physicalAccepted=False,installationApproved=False);refs.append(ref(path))
 save(DOC/'metadata-only-proof.json',dict(validator=outcome,allFieldsExceptSourceOverlapExactlyEqual=bool(outcome.get('allFieldsExceptSourceOverlapExactlyEqual')),metadataOnlyCandidate=outcome.get('metadataOnlyCandidate'),freshCanonicalEdge=ref(DOC/'fresh860-canonical-parent-edge-guard.json.gz'),completeOrdinaryFinite=ref(finite.DOC/'complete-actual-union-finite-delta.json.gz'),fullScopeBodyZeroCrossingRootSupportForeignObligationsRetained=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0));fence();refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 capture.legacy.module(capture.legacy.FREEZER,'upton_certified6170_metadata_freezer').freeze(BATCH,'fresh-canonical860-source-bound-overlap-metadata-real-validator-only',[check(q)for q in refs],dict(uids=finite.baseline.OWNED+[finite.baseline.SECONDARY,finite.baseline.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--validate-source-reviewed-overlap-and860-only'in sys.argv and not DOC.exists() and not LOCAL.exists();load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 uids=finite.baseline.OWNED+[finite.baseline.SECONDARY,finite.baseline.NATIVE,finite.baseline.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-certified6170-metadata-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
