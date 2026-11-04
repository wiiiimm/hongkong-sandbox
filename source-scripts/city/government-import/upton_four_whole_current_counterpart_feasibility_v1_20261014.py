"""ROOT-only decisive four complete CURRENT counterpart trial; no gap re-clipping.

Whole exact saved Float32 triangles avoid degenerate re-packed thin masks. A
private append-only nominee is emitted only after whole-scope ordinary pair
compatibility AND all twelve fresh failing rows' packed projected coverage pass.
"""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time,uuid,subprocess
import numpy as np
import upton_full22_saved_actual_union_delta_v1_20261014 as finite
import upton_full22_saved_area_pair_ancestor_v1_20261014 as pairs
import upton_full22_parent_edge_contract_diagnostic_v1_20261014 as boundary
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import masked_current_pair,projected_mask
from upton_append_four_saved_current_triangles_v1_20261014 import append_saved_current
from run import ROOT,HERE,read,save,connect,reservations
baseline=finite.baseline;capture=finite.capture;ref,check=finite.ref,finite.check;sha=finite.sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-four-whole-current-counterpart-feasibility-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
IDS=[6141,6159,6168,6170];FACES=[87,205,228]
RECEIPTS=[(finite.DOC,'dbf5bf4ffde84bbf237b1f45f1453c003ab0a04f8cc1a426b4998492bf3bfb78'),(pairs.DOC,'c5e9d823e4d12d6470d116735e0e585e61eb435aed5969c780c751b37edece45'),(boundary.DOC,'6809fe4b318015a85470e620a0b8421b8386fbf55ad7aeb728f896fe1072a8c4')]
TESTS=['test_upton_append_four_saved_current_triangles_v1_20261014','test_upton_six_basic_preserved_ground_feasibility_v1_20261012']

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 for folder,job in RECEIPTS:
  assert read(folder/'result.json')['jobId']==job
  verified=read(folder/'ROOT-VERIFIED.json');assert verified['jobId']==job and verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased']
 latest=read(finite.DOC/'complete-actual-union-finite-delta.json.gz');assert latest['newGroundSHA256']=='c0184d753db5e9f721e2705b41665e02c34ba9992a0c593ff40091d70c5b2e55' and latest['completeNewDrawnFaces']==11634
 assert latest['completeNativeActorScope']==6650 and len(latest['completeBasicRows'])==1911 and not latest['physicalAccepted'] and not latest['installationApproved']
 second=next(r for r in latest['actors']if r['uid']==baseline.SECONDARY);assert len(second['worlds'])==4 and all(w['findings']['currentClearCandidateUnproved']==FACES for w in second['worlds'])
 saved=[]
 for w in second['worlds']:
  rows=[r for q in w['findings']['chunks']for r in read(check(q))['rows']if r['face']in FACES];assert [r['face']for r in rows]==FACES
  for r in rows:
   assert not r['findings']['projectionCovered'] and not r['findings']['ordinaryBoundProved'] and F(r['findings']['exactLowerM'])>=-F(1,2)
   assert r['completeNewGroundSelection']['completeGroundSHA256']==latest['newGroundSHA256']
   saved.append(dict(mode=w['mode'],wholeWorldSHA256=w['wholeWorldSHA256'],sourceFace=r['face'],freshSavedRowVerbatim=r))
 assert len(saved)==12
 _,whole,coverage,oldnom,oldraw,oldpv,oldpatch,rep=capture.nomination.load();records=coverage['completeCurrentCounterpartPlanes'];assert [r['originalCurrentFace']for r in records]==IDS
 parents=np.asarray([r['wholeOriginalCurrentTriplet']for r in records],dtype='<f8');assert parents.shape==(4,3,3) and parents.tobytes()==parents.astype('<f4').astype('<f8').tobytes()
 for r,p in zip(records,parents):assert sha(p)==r['wholeOriginalCurrentTripletSHA256'] and r['completeCurrentAttribution']['globalOrderedSavedFaceSHA256']==sha(p) and r['completeCurrentAttribution']['globalCurrentFace']==r['originalCurrentFace']
 nom=read(capture.NOM_DOC/'private-full22-current-plane-restoration-nomination.json.gz');raw=np.asarray(nom['candidateRawPositionTriplets'],dtype='<f8');pv=nom['candidateFaceProvenance'];patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');assert raw.shape==(11606,3,3) and len(pv)==11606 and len(nom['protectedWholeCurrentTripletsUnchanged'])==68
 for r in nom['protectedWholeCurrentTripletsUnchanged']:assert sha(raw[r['newCandidate']])==r['rawTripletSHA256']
 scope=read(check(latest['same6650WholeScope']));assert scope['completeNativeActors']==6650 and len(scope['affectedBasic'])==52 and sum(len(r['selectedWholeFaceIDs'])for r in scope['affectedBasic'])==2114
 check(latest['allZerosAnd23CrossingsRetained'])
 edge=read(boundary.DOC/'complete860-canonical-parent-edge-vertex-guard.json.gz');assert edge['allPassed'] and len(edge['rows'])==860 and edge['existingStrictLimitM']==.01
 pack=read(capture.NOM_DOC/'complete-added-current-plane-packing-diagnostic.json.gz');collapsed=[r['newCandidateFace']for r in pack['rows']if len({(v[0],v[2])for v in r['packingProof']['packedPieceTriplet']})<3];assert collapsed==[11580,11581,11588,11589,11590,11591,11594]
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT
 return pins,latest,saved,records,parents,nom,raw,pv,patch,scope,collapsed

def schema_only():
 p,l,s,records,parents,n,raw,pv,patch,scope,collapsed=load()
 return dict(passed=True,caller=ref(Path(__file__)),completeCurrentCounterpartIDs=IDS,wholeCurrentTripletsAlreadyExactFloat32=True,actualFreshForeignFailureRows=12,completeCurrentGroundDrawnFacets=11634,oldCandidateFacets=11606,all68ProtectedAndSourceInventoriesRetained=True,wholeActorScope=6650,completeBasicRecords=1911,wholeAffectedBasicActors=52,wholeOwnedFacesPerMode=13312,secondary392Native616AllFourModes=True,priorSevenDuplicatePackedXZVertices=collapsed,all860CanonicalBoundaryPointGuardsPassedHeldAsContext=True,noPairFinitePackingConstructionDBLeaseWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,latest,saved,records,parents,nom,raw,pv,patch,scope,collapsed=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'PACKED-ENCLOSURE-FALLBACK.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder,job in RECEIPTS:
  receipt=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir()
 _,ground,_,_,attrs,actor_scope,actors=finite.inputs();assert sha(ground)==latest['newGroundSHA256'] and actor_scope==scope
 masks=[projected_mask(p)for p in parents];pxz=parents[:,:,[0,2]];low=pxz.min(1);high=pxz.max(1);cache={};results=[]
 def assess(uid,mode,w,role,old_world):
  assert len(w)==old_world['completeFaces'] and sha(w)==old_world['wholeWorldSHA256'];rows=[];chunks=[];conflicts=[];uncredited=[];outside=[]
  for face_id,face in enumerate(w):
   xz=face[:,[0,2]];selected=np.flatnonzero(np.all(high>=xz.min(0),axis=1)&np.all(low<=xz.max(0),axis=1));proofs=[]
   if not len(selected):outside.append(face_id)
   for k in selected:
    key=(sha(face),int(k))
    if key not in cache:cache[key]=masked_current_pair(face,parents[k],masks[k])
    proof=cache[key];proofs.append(dict(originalCurrentFace=IDS[k],wholeCurrentTripletSHA256=sha(parents[k]),unchangedFullProjectedPairProof=proof))
    if proof.get('violatesExistingOrdinaryBound'):conflicts.append(dict(sourceFace=face_id,currentFace=IDS[k],sourceFaceSHA256=sha(face),wholeOriginalSourceFace=face.tolist(),wholeOriginalCurrentTriplet=parents[k].tolist(),fullSourcePlaneWitnessVerbatim=proof,originalSourceRolesAndGeometryImmutable=True))
    if proof.get('exactSourceZero')or proof.get('collapsedCurrentGroundProjection'):uncredited.append(dict(sourceFace=face_id,currentFace=IDS[k],proofVerbatim=proof,noSourceRoleOrSupportCredit=True))
   rows.append(dict(sourceFace=face_id,sourceFaceSHA256=sha(face),completeWholeCurrentClosedAABBCandidates=[IDS[int(k)]for k in selected],allOmittedWholeCurrentFacetsStrictlyClosedAABBDisjoint=True,completeWholeProjectedPairProofs=proofs,noRootRoleOrSupportAcceptance=True))
   if len(rows)==64 or face_id==len(w)-1:
    path=DOC/'chunks'/uid.replace('/','-').replace(':','-')/mode/(str(len(chunks)).zfill(5)+'.json.gz');save(path,dict(uid=uid,mode=mode,role=role,wholeWorldSHA256=sha(w),fourWholeCurrentSHA256=sha(parents),rows=rows));chunks.append(ref(path));rows=[];pulse()
  return dict(uid=uid,mode=mode,role=role,completeSourceFaces=len(w),wholeWorldSHA256=sha(w),chunks=chunks,completeWholeSourceFacesAccounted=True,strictFourWholeCurrentDisjointSourceFaceIDs=outside,conflictingSourceFaces=conflicts,uncreditedSourceFaces=uncredited,priorFullFiniteWorldVerbatim=old_world,allPriorNegativesRetainedNoAcceptance=True)
 for uid,worlds,_,source_sha in actors:
  old=next(r for r in latest['actors']if r['uid']==uid);assert old['sourceSHA256']==source_sha
  results.append(dict(uid=uid,sourceSHA256=source_sha,worlds=[assess(uid,mode,worlds[mode],old['role'],next(w for w in old['worlds']if w['mode']==mode))for mode in baseline.MODES]));print(json.dumps(dict(uid=uid,fourWholeCurrentCompatibilityOnly=True)),flush=True)
 affected={r['uid']for r in scope['affectedBasic']};old_basic={r['uid']:r for r in latest['completeBasicRows']};basics=[]
 for r in attrs['basicContextRows']:
  uid=r['uid'];old=old_basic[uid]
  if uid in affected:
   positions=np.asarray(r['position'],dtype='<f8').reshape(-1,3);w=finite.triangles(positions[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)]);world=old['findings']['worlds'][0];assert world['mode']=='capturedConstructorFloat32World'
   basics.append(dict(uid=uid,wholeFourCurrentCompatibility=assess(uid,world['mode'],w,'whole-affected-BASIC',world),completeUnusedPositionVertices=len(positions),priorBasicVerbatim=old))
  else:basics.append(dict(uid=uid,priorBasicVerbatim=old,strictOutsideWholeParentDomainRetained=True,noAcceptanceCredit=True))
 assert len(basics)==1911 and sum('wholeFourCurrentCompatibility'in r for r in basics)==52
 # Decisive fresh packed-union coverage, not repeated residual-location evidence.
 trial=np.concatenate([ground,parents]);selection=baseline.CompleteGround(trial);current=baseline.CompleteGround(ground);target_results=[];secondary=next(worlds for uid,worlds,_,_ in actors if uid==baseline.SECONDARY)
 for row in saved:
  face=secondary[row['mode']][row['sourceFace']];saved_row=row['freshSavedRowVerbatim'];assert sha(face)==saved_row['currentBaselineVerbatim']['sourceFaceSHA256']
  old_ids,old_binding=current.select([[F(v)for v in p]for p in face.tolist()]);assert old_binding==saved_row['completeNewGroundSelection'] and sha(ground[old_ids])==saved_row['completeRelevantGroundSHA256']
  new_ids,new_binding=selection.select([[F(v)for v in p]for p in face.tolist()]);proof=finite.finite_record(face,trial[new_ids]);target_results.append(dict(**row,completeTrialGroundSelection=new_binding,completeTrialRelevantGroundSHA256=sha(trial[new_ids]),unchangedExactPackedUnionFiniteProof=proof,hypotheticalUnionNotYetActualCaptured=True,allOldFailureRecordsPreserved=True));pulse()
 selection.verify_binding();current.verify_binding()
 streams=[w for r in results for w in r['worlds']]+[r['wholeFourCurrentCompatibility']for r in basics if 'wholeFourCurrentCompatibility'in r]
 clear=all(not w['conflictingSourceFaces'] and not w['uncreditedSourceFaces']for w in streams);covered=all(r['unchangedExactPackedUnionFiniteProof']['projectionCovered'] and r['unchangedExactPackedUnionFiniteProof']['ordinaryBoundProved']for r in target_results)
 save(DOC/'complete-four-whole-current-compatibility-and-packed-target-coverage.json.gz',dict(wholeCurrentCounterpartsVerbatim=records,completeActors=results,complete1911BasicRows=basics,all52WholeBasicAndFourActorFourWorldStreamsChecked=True,wholeCurrentOrdinaryCompatibleWithoutUncredited=clear,twelveFreshTargetPackedUnionProofs=target_results,allTwelvePackedTargetCoverageAndOrdinaryPassed=covered,allLatestFullFiniteNegativesVerbatim=latest,priorSevenCollapsedProjectedVertexCases=collapsed,canonical860EdgePassContext=ref(boundary.DOC/'complete860-canonical-parent-edge-vertex-guard.json.gz'),fullCurrent9214AndOriginalTIN122721InventoriesRetainedViaPreviousNomination=True,fullParentExteriorRuntimeMAXOverlapRootBrowserGatesPending=True,physicalAccepted=False,installationApproved=False))
 if clear and covered:
  bound=append_saved_current(raw,pv,patch['nativeMesh'],records,nom['protectedWholeCurrentTripletsUnchanged']);new=np.asarray(bound['candidateRawPositionTriplets'],dtype='<f8');assert new.shape==(11610,3,3)
  bound['newNativeMesh']['source']=dict(kind='private-four-authentic-whole-current-counterparts-no-new-packing',originalCurrentCounterpartIDs=IDS,noNewCoverageOverlapOrPhysicalApproval=True)
  save(DOC/'private-four-whole-current-counterpart-nomination.json.gz',dict(schema='upton-four-whole-current-counterpart-nomination-v1',**bound,previousFull22Nomination=ref(capture.NOM_DOC/'private-full22-current-plane-restoration-nomination.json.gz'),previousActualCaptureCandidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),completeNewCandidateFacets=len(new),completeNewRawSHA256=sha(new),all11606OldRawProvenancePositionIndexAnd68LiteralPrefixesRetained=True,allOldMasksPartitionMapsCountClaimsHistoricalOnly=True,wholeCompatibilityAndTargetPackedProof=ref(DOC/'complete-four-whole-current-compatibility-and-packed-target-coverage.json.gz'),wholeSourceCurrentAndParentDomainAnd6650ScopeRolesPreserved=True,allPriorNegativeReceiptsRetained=[ref(folder/'result.json')for folder,job in RECEIPTS],freshActualProductionFullFiniteOverlapMAXSeamRootRuntimeBrowserStillRequired=True,originalBuildingGeometryPoseChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 else:
  save(DOC/'whole-current-conflicts-and-certified-packing-enclosure-next-route.json.gz',dict(wholeCompatibilityPassed=clear,targetPackedCoveragePassed=covered,completeFreshConflictAndUncreditedSourceFaceWorldWitnesses=[dict(uid=w['uid'],mode=w['mode'],conflicts=w['conflictingSourceFaces'],uncredited=w['uncreditedSourceFaces'])for w in streams if w['conflictingSourceFaces']or w['uncreditedSourceFaces']],completeFreshTargetRows=target_results,certifiedPackingEnclosurePlan=ref(PROPOSAL/'PACKED-ENCLOSURE-FALLBACK.md'),onlyFreshResidualMasksMayBeEnclosed=True,noEpsilonBufferBBoxOrSourceGeometryWaiver=True,noUnverifiedEnclosureGeometryEmitted=True,noPermanentRejectionOrCorruptionCredit=True,physicalAccepted=False,installationApproved=False))
 fence();refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 baseline.module(baseline.FREEZER,'upton_four_whole_current_freezer').freeze(BATCH,'decisive-four-whole-current-source-byte-compatible-packed-coverage-private-nomination-only',[check(q)for q in refs],dict(uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--test-four-whole-current-counterparts-only'in sys.argv and not DOC.exists() and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE,baseline.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-four-whole-current-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
