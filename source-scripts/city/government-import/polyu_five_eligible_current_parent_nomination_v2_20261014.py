"""ROOT-only five exact-mask private current-parent restoration nomination.

No model/source/pose edits or acceptance. Existing private terrain outside the
eligible masks keeps its own saved plane; the restored regions use only the
captured original current-parent planes. Full 25-actor scope remains pending.
"""
from pathlib import Path
import json,sys,time,uuid,subprocess,hashlib,shutil
from fractions import Fraction as F
import numpy as np
import polyu_nine_complete_parent_restoration_feasibility_v1_20261013 as feasibility
from polyu_five_mask_source_plane_partition_v1_20261014 import packed_pieces,serial,verify_saved_packing,protected_literal_declaration
from polyu_five_mask_source_plane_partition_fast_v1_20261014 import PreparedMasks,partition
from run import ROOT,HERE,read,save,connect,reservations
ref,check=feasibility.ref,feasibility.check
prior=feasibility.prior
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-five-eligible-current-parent-nomination-v2-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='d6ebd0cf69b4b5f81ba757a919513eaefa88a4371b6cb875ea3ff5a77645787f'
ELIGIBLE=['landsd/'+str(i)+':0'for i in [63758,258381,258681,198620,305626]]
CONFLICTS={'landsd/'+str(i)+':0':n for i,n in [(72322,21),(89540,141),(258852,24),(305600,4)]}
BUILD=BASE/'government-xl-polyu-sports305582-authentic-local-private-terrain-v2-20261013'
TEST='test_polyu_five_mask_source_plane_partition_fast_v1_20261014'
OLD_BATCH='government-xl-polyu-five-eligible-current-parent-nomination-v1-20261014'
OLD_DOC=BASE/OLD_BATCH;OLD_LOCAL=HERE/'local'/OLD_BATCH
ACCELERATION=BASE/'government-xl-polyu-five-mask-partition-acceleration-code-proposal-v1-20261014'
PREFIX_ROWS=832;PREFIX_FACES=1485
PREFIX_PROOF_SHA='8cc3e885d26958a640069012d5aca9b9d2df4eb0eae03bff41e1046f2165e0c8'
PREFIX_PACKED_SHA='e6f33d8f75803d8178eb4310d7d40498f4d3881be40e36c3ae40b911c294de21'

def prefix_rows(raw,lineage):
 contract=read(ACCELERATION/'saved-prefix-fixture-pins.json')
 for q in contract['evidenceRefs']:check(q)
 assert len(contract['progressRefs'])==13 and contract['eligibleUIDs']==ELIGIBLE
 rows=[];proof_hash=hashlib.sha256();cursor=0
 for q in contract['progressRefs']:
  chunk=read(check(q));assert chunk['oldPrivateProcessed']==len(rows)+64 and not chunk['unresolved']and len(chunk['oldMappings'])==64
  rows.extend(chunk['oldMappings'])
 assert len(rows)==PREFIX_ROWS and [q['oldPrivateFace']for q in rows]==list(range(PREFIX_ROWS))
 for i,q in enumerate(rows):
  assert q['previousLineageVerbatim']==lineage[i]
  assert np.asarray(q['wholeOldRawTriplet'],dtype='<f8').tobytes()==raw[i].tobytes()
  assert q['newCandidateFaces']==list(range(cursor,cursor+len(q['newCandidateFaces'])))
  cursor+=len(q['newCandidateFaces'])
  proof_hash.update(json.dumps(q['completeExactMaskPartition'],sort_keys=True,separators=(',',':')).encode())
 assert cursor==PREFIX_FACES and proof_hash.hexdigest()==PREFIX_PROOF_SHA
 return rows,contract

def prior_terminal_ready(live=False):
 """ROOT creates this evidence only after observing terminal/reap/release."""
 ready=read(PROPOSAL/'ROOT-resume-readiness.json')
 assert ready['passed']and ready['v1Batch']==OLD_BATCH and ready['v2Caller']==ref(Path(__file__))
 assert ready['authoritativeV1SessionID']==63993 and type(ready['observedV1TerminalExitCode'])is int
 assert ready['v1TerminalObserved']and ready['v1CanonicalReservationsReleased']and ready['v1ProducerProcessesAbsent']
 assert ready['v1SourceContextFreezerNotStarted']and ready['v1NoCompletedNominationReceipt']
 pids=ready['v1ProducerPIDs'];assert len(pids)>=3 and len(set(pids))==len(pids)and all(type(p)is int and p>0 for p in pids)
 assert all(not Path('/proc',str(p)).exists()for p in pids),'Original producer PID is present: no replacement'
 for q in ready['evidenceRefs']:check(q)
 verified=read(check(ready['rootVerifiedPrefixRef']))
 assert verified['savedRows']==PREFIX_ROWS and verified['reconstructedPrefixCandidateFaces']==PREFIX_FACES
 assert verified['completeOrderedSavedProofSHA256']==PREFIX_PROOF_SHA and verified['reconstructedOrderedPrefixPackedTripletsSHA256']==PREFIX_PACKED_SHA
 assert verified['completeOrderedMaskOccurrences']==5553 and verified['exactUniqueOrderedMasks']==1234 and verified['actualPartitionCalls']==0
 assert not (OLD_DOC/'result.json').exists()and not (OLD_DOC/'private-five-mask-current-parent-nomination.json.gz').exists()
 old_lease=read(check(ready['v1ReservationRef']))
 expected_old=sorted(['building:'+u for u in prior.UIDS]+['terrain-patch:'+u for u in prior.UIDS]+['immutable-source-proof:'+OLD_BATCH])
 assert old_lease['batch']==OLD_BATCH and old_lease['resources']==expected_old
 if live:
  assert not reservations.owns(old_lease),'Original canonical lease still owned'
 return ready

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(feasibility.DOC/'result.json');assert receipt['jobId']==JOB
 result=read(feasibility.DOC/'complete-nine-parent-restoration-feasibility.json.gz')
 assert result['all25AffectedActors']==prior.UIDS and len(result['all51CanonicalResources'])==51
 assert len(result['rows'])==9 and not result['currentAcceptance']and not result['physicalAccepted']
 assert [r['uid']for r in result['rows']if r['eligibleCurrentParentMaskNominationOnly']]==ELIGIBLE
 assert {r['uid']:len(r['allConflictingSourceFaces'])for r in result['rows']if r['allConflictingSourceFaces']}==CONFLICTS
 masks=[]
 for r in result['rows']:
  assert not r['unresolvedDegenerateMaskIDs']and len(r['sourceWorlds'])==4
  for w in r['sourceWorlds']:
   assert w['completeSourceFaces']==10536 and w['allSourceFacesAccounted']
   if r['uid']in ELIGIBLE:assert not w['conflictingSourceFaces']and not w['uncreditedSourceOrParentDegeneracies']
  m=read(check(r['completeMask']));assert m['uid']==r['uid']and m['completeClosedUnionNoSampleOrBBoxMask']and not m['degenerateProjectionsNotCoveredByPositiveUnion']
  assert m['currentFormVerbatim']==r['currentFormAndExactUID']and m['completeUnusedPositionsRetainedInSourceEvidence']
  if r['uid']in ELIGIBLE:
   assert sorted(m['positiveMaskIDs']+m['degenerateMaskIDs'])==list(range(len(m['rows'])))
   for i in m['positiveMaskIDs']:assert m['rows'][i]['mask']==i;masks.append({**m['rows'][i],'uid':r['uid'],'maskEvidence':r['completeMask']})
 base=read(BUILD/'full-computed-private-candidate-and-account.json.gz');account=base['account'];patch=read(check(dict(path=base['candidatePath'],sha256=base['candidateSHA256'])))
 positions=np.asarray(patch['nativeMesh']['position'],dtype='<f8').reshape(-1,3);indices=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);raw=positions[indices]
 assert raw.shape==(3214,3,3)and np.isfinite(raw).all()and raw.astype('<f4').astype('<f8').tobytes()==raw.tobytes()
 lineage=account['completeOutputFacetLineage'];assert len(lineage)==3214 and account['declaredImmutableSourceFacets']==181089 and account['selectedOriginalFacets']==7690
 for i,r in enumerate(lineage):assert r['outputFacet']==i and np.asarray(r['actualPackedPoints'],dtype='<f8').tobytes()==raw[i].tobytes()
 assert account['sourceBuildingPoseAndGeometryUnchanged']and account['fullOwnedFourStreamAndWholeAffectedActorsPending']
 assert account['all752FourModeRawNegativesAnd21BodiesVerbatim']==result['all752FourModeNegativesAndWhole21SourceRolesRetained']
 assert all(len(r['all752FailureRecordsVerbatim'])==752 for r in result['all752FourModeNegativesAndWhole21SourceRolesRetained'])
 assert result['retainedNative59527FullBeforeAfterStillPending']and result['original3366GuardSitesNotPersisted']and result['noSavedContextToOriginalGuardSiteEquivalence']
 assert sum(r['completeIndexedFaces']for r in account['installedPodiumFalseHoldVerbatim']['actualPositionRecord']['actualRenderMeshes'])==59527
 parents=result['complete12CapturedParentFacets'];assert np.asarray(parents).shape==(12,3,3)
 resources=sorted(['building:'+u for u in prior.UIDS]+['terrain-patch:'+u for u in prior.UIDS]+['immutable-source-proof:'+BATCH]);assert len(resources)==51
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==read(feasibility.PROPOSAL/'actual-readonly-preparation.json')['schemaVerbatim'].get('currentManifestSHA256', 'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7')
 assert len(masks)==5553
 prefix_rows(raw,lineage) # Hash/schema only; no prefix partition or packing.
 return pins,receipt,result,masks,base,patch,raw,lineage,parents,resources

def schema_only():
 p,r,s,m,b,patch,raw,l,parents,resources=load()
 return dict(passed=True,caller=ref(Path(__file__)),completedFeasibilityJob=JOB,eligibleUIDs=ELIGIBLE,conflictUIDsAndCounts=CONFLICTS,complete25Actors=prior.UIDS,canonicalResources=resources,eligiblePositiveMaskOccurrences=len(m),oldPrivateFacets=3214,currentParentFacets=12,ownedSourceFacesPerMode=10536,completeOriginalTerrainFacets=181089,negativeFacesPerMode=752,sourceBodies=21,native59527WholeBeforeAfterPending=True,noMaskPartitionPackingCalculationDBLeaseWorker=True,savedPrefixRows=PREFIX_ROWS,savedPrefixCandidateFaces=PREFIX_FACES,remainingOldPrivateFacets=3214-PREFIX_ROWS,oldTerminalReleaseReadinessNotClaimedBySchema=True)

def owned():
 ready=prior_terminal_ready(live=True)
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 pins,receipt,result,records,base,patch,raw,lineage,parents,resources=load();assert lease['resources']==resources
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json'),ref(PROPOSAL/'ROOT-resume-readiness.json')]+prep['evidenceRefs']+ready['evidenceRefs']
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 refs+=[ref(feasibility.DOC/'result.json')]+receipt['evidenceRefs'];last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']=='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'and reservations.owns(lease)
 fence();DOC.mkdir();masks=PreparedMasks(records);assert len(masks.masks)==5553 and len(masks.first_ids)==1234
 positions=list(patch['nativeMesh']['position']);old_indices=patch['nativeMesh']['index'];index=[];provenance=[];old_map=[];parent_map=[];unresolved=[]
 declared_protected,protection_declaration=protected_literal_declaration(base['account'],len(raw));protected=set(declared_protected)
 save(DOC/'protected-literal-declaration-context.json',protection_declaration)
 def emit(piece,kind,ancestor,partition_proof,mask=None):
  j=len(provenance);start=len(positions)//3;positions.extend(v for p in piece['packedPieceTriplet']for v in p);index.extend(range(start,start+3))
  provenance.append(dict(candidateFace=j,kind=kind,ancestor=ancestor,exactOwnPlanePoints=serial(piece['exactOwnPlanePoints']),exactPackedSourcePlaneResiduals=serial(piece['exactPackedSourcePlaneResiduals']),packingResidualsMeasuredNotWaived=True,mask=mask,noOtherLayerYUsed=True,partitionProof=partition_proof));return j
 saved_rows,prefix_contract=prefix_rows(raw,lineage);packed_hash=hashlib.sha256()
 for i,saved in enumerate(saved_rows):
  face,old_record=raw[i],lineage[i];proof=saved['completeExactMaskPartition'];ideal=old_record['exactProposedPoints'];ids=[]
  if proof.get('projectedVerticalOrZeroPreservedWhole')or F(proof['exactInsideMaskUnionIntrinsicArea'])==0:
   j=len(provenance);ids.append(j);index.extend(old_indices[3*i:3*i+3]);packed_hash.update(np.asarray([face],dtype='<f8').tobytes())
   provenance.append(dict(candidateFace=j,kind='unchangedPreviousPrivateDraw',oldPrivateFace=i,previousLineageVerbatim=old_record,wholeOldRawTripletByteEqual=True,verticalOrZeroGetsNoNewHeightCredit=proof.get('projectedVerticalOrZeroPreservedWhole',False)))
  else:
   polygons=[[tuple(F(v)for v in p)for p in poly]for poly in proof['outside']]
   for piece in packed_pieces(polygons,ideal):
    ids.append(emit(piece,'previousPrivateOwnPlaneOutsideEligibleMasks',dict(oldPrivateFace=i,previousLineageVerbatim=old_record),proof))
    packed_hash.update(np.asarray([piece['packedPieceTriplet']],dtype='<f8').tobytes())
  assert ids==saved['newCandidateFaces'];old_map.append(saved);pulse()
 assert len(provenance)==PREFIX_FACES and packed_hash.hexdigest()==PREFIX_PACKED_SHA
 for q in prefix_contract['progressRefs']:
  source=check(q);target=DOC/'progress'/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert ref(target)['sha256']==q['sha256']
 save(DOC/'prefix-resume-lineage.json',dict(reusedPartitionRows=PREFIX_ROWS,reconstructedCandidateFaces=PREFIX_FACES,partitionRowsCopiedVerbatim=True,actualPrefixPartitionCalls=0,completeOrderedProofSHA256=PREFIX_PROOF_SHA,reconstructedOrderedPackedSHA256=PREFIX_PACKED_SHA,sourceProgressRefs=prefix_contract['progressRefs'],originalHelper=ref(HERE/'polyu_five_mask_source_plane_partition_v1_20261014.py'),unfinishedHelper=ref(HERE/'polyu_five_mask_source_plane_partition_fast_v1_20261014.py'),mixedOriginalAndAcceleratedKernelProvenance=True,noAcceptanceCredit=True))
 print(json.dumps(dict(stage='saved-prefix-reconstructed',oldPrivateProcessed=PREFIX_ROWS,candidateFaces=PREFIX_FACES)),flush=True)
 for i in range(PREFIX_ROWS,len(raw)):
  face,old_record=raw[i],lineage[i]
  try:
   ideal=old_record['exactProposedPoints'];assert verify_saved_packing(ideal,face)
   proof=partition(ideal,masks,protected_literal=i in protected);ids=[]
   if proof.get('projectedVerticalOrZeroPreservedWhole')or proof['exactInsideMaskUnionIntrinsicArea']==0:
    j=len(provenance);ids.append(j);index.extend(old_indices[3*i:3*i+3]);provenance.append(dict(candidateFace=j,kind='unchangedPreviousPrivateDraw',oldPrivateFace=i,previousLineageVerbatim=old_record,wholeOldRawTripletByteEqual=True,verticalOrZeroGetsNoNewHeightCredit=proof.get('projectedVerticalOrZeroPreservedWhole',False)))
   else:
    for piece in packed_pieces(proof['outside'],ideal):ids.append(emit(piece,'previousPrivateOwnPlaneOutsideEligibleMasks',dict(oldPrivateFace=i,previousLineageVerbatim=old_record),serial(proof)))
   old_map.append(dict(oldPrivateFace=i,newCandidateFaces=ids,wholeOldRawTriplet=face.tolist(),previousLineageVerbatim=old_record,completeExactMaskPartition=serial(proof),removedFragmentsRemainInSourceInventory=True))
  except (AssertionError,ValueError,KeyError)as e:unresolved.append(dict(oldPrivateFace=i,reason=type(e).__name__+': '+str(e),noGeometryOrToleranceWaiver=True))
  if (i+1)%64==0:save(DOC/'progress'/(str(i+1).zfill(5)+'.json.gz'),serial(dict(oldPrivateProcessed=i+1,oldMappings=old_map[-64:],unresolved=unresolved,noAcceptance=True)));pulse()
 for i,face in enumerate(parents):
  try:
   proof=partition(face,masks);assert not proof.get('projectedVerticalOrZeroPreservedWhole');ids=[]
   for hit in proof['inside']:
    for piece in packed_pieces([hit['polygon']],face):ids.append(emit(piece,'capturedCurrentParentInsideEligibleMasks',dict(capturedParentFacet=i,wholeOriginalCapturedParentTriplet=face),serial(proof),dict(mask=hit['mask'],completeMaskLineage=records[hit['mask']])))
   parent_map.append(dict(capturedParentFacet=i,newCandidateFaces=ids,wholeOriginalCapturedParentTriplet=face,completeExactMaskPartition=serial(proof)))
  except (AssertionError,ValueError,KeyError)as e:unresolved.append(dict(capturedParentFacet=i,reason=type(e).__name__+': '+str(e),noGeometryOrToleranceWaiver=True))
  pulse()
 save(DOC/'complete-five-mask-partition-diagnostic.json.gz',serial(dict(oldMappings=old_map,parentMappings=parent_map,unresolved=unresolved,allEligibleMaskOccurrences=records,completeFeasibilitySummaryVerbatim=result,completePreviousAccountVerbatim=base['account'],protectedLiteralDeclarationContext=protection_declaration,all25AffectedUIDs=prior.UIDS,all51Resources=resources,noBuildingSourcePoseGeometryChanges=True,allPriorGuardsAndNegativeContextsHeld=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0)))
 if not unresolved:
  assert len(old_map)==3214 and len(parent_map)==12
  assert positions[:len(patch['nativeMesh']['position'])]==patch['nativeMesh']['position']
  assert len(index)==len(provenance)*3 and all(0<=i<len(positions)//3 for i in index)
  for i in protected:
   ids=old_map[i]['newCandidateFaces'];assert len(ids)==1 and index[3*ids[0]:3*ids[0]+3]==old_indices[3*i:3*i+3]
  save(DOC/'private-five-mask-current-parent-nomination.json.gz',serial(dict(schema='private-source-plane-preserving-five-current-parent-mask-nomination-v1',previousPrivateCandidate=dict(path=base['candidatePath'],sha256=base['candidateSHA256']),newNativeMesh=dict(position=positions,index=index),candidateFaceProvenance=provenance,completeOldPrivateMapping=old_map,completeCapturedParentMapping=parent_map,oldPositionBufferRetainedIncludingUnusedVertices=True,eligibleUIDs=ELIGIBLE,independentConflictActors=CONFLICTS,completeSourceTerrain181089StillImmutable=True,all25AffectedActors=prior.UIDS,all752FourModeNegativesAnd21BodiesRetained=result['all752FourModeNegativesAndWhole21SourceRolesRetained'],native59527WholeBeforeAfterPending=True,original3366GuardSitesNeedFreshActualReplay=True,fullPackingCoverageSeamMAXFiniteRootRuntimeBrowserGatesPending=True,noApprovalOrOldCountFlagsTransferred=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0)))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence()
 prior.module('polyu_five_mask_nomination_v2_freezer',prior.FREEZER).freeze(BATCH,'private-five-exact-eligible-current-parent-mask-resumed-source-plane-nomination-v2-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=prior.UIDS,sourceOnly=True,terrainNominationNotAcceptance=True,unresolved=len(unresolved),physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--nominate-five-eligible-current-parent-masks-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 pins,receipt,result,m,b,patch,raw,l,parents,resources=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 prior_terminal_ready(live=True) # Observed terminal/reap/release before any fresh claim.
 claim=reservations.claim('polyu-five-current-parent-nomination-v2-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
