"""ROOT-only three proven whole currents plus certified6170 residual enclosure.

No repeat of ideal clipped/re-packed masks. Every new boundary uses exact
Float32 brackets/original edge nodes and passes actual packed closed coverage.
"""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time,uuid,subprocess
import numpy as np
import upton_four_whole_current_counterpart_feasibility_v1_20261014 as prior
from upton_certified_float32_parent_enclosure_v1_20261014 import enclose
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import masked_current_pair,projected_mask
from exact_original_projection_coverage_v2_20261010 import point,signed_area,subtract
from upton_append_four_saved_current_triangles_v1_20261014 import append_saved_current
from polyu_five_mask_source_plane_partition_v1_20261014 import serial
from run import ROOT,HERE,read,save,connect,reservations
finite=prior.finite;baseline=prior.baseline;capture=prior.capture;ref,check=prior.ref,prior.check;sha=prior.sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-three-safe-current-certified-6170-enclosure-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='e6d09e27fa78d6153feb7adc957f1549ab2d5c9a72cdcd19fbc09a7bd923b88b';SAFE=[6141,6159,6168];PARENT=6170
TESTS=['test_upton_certified_float32_parent_enclosure_v1_20261014','test_upton_append_four_saved_current_triangles_v1_20261014','test_upton_six_basic_preserved_ground_feasibility_v1_20261012','test_upton_exact_full_residual_current_coverage_v1_20261014']

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(prior.DOC/'result.json');assert receipt['jobId']==JOB
 verified=read(prior.DOC/'ROOT-VERIFIED.json');assert verified['jobId']==JOB and verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased']
 _,latest,saved,records,parents,nom,raw,pv,patch,scope,collapsed=prior.load()
 result=read(prior.DOC/'complete-four-whole-current-compatibility-and-packed-target-coverage.json.gz');assert result['wholeCurrentCounterpartsVerbatim']==records and result['allTwelvePackedTargetCoverageAndOrdinaryPassed'] and not result['wholeCurrentOrdinaryCompatibleWithoutUncredited']
 assert len(result['complete1911BasicRows'])==1911 and len(result['completeActors'])==4 and result['allLatestFullFiniteNegativesVerbatim']==latest
 contexts=[w for a in result['completeActors']for w in a['worlds']]+[r['wholeFourCurrentCompatibility']for r in result['complete1911BasicRows']if 'wholeFourCurrentCompatibility'in r];assert len(contexts)==16+52
 conflicts=[]
 for w in contexts:
  assert w['completeWholeSourceFacesAccounted'] and not w['uncreditedSourceFaces']
  conflicts.extend((w['uid'],w['mode'],r['sourceFace'],r['currentFace'])for r in w['conflictingSourceFaces'])
 assert sorted(conflicts)==sorted((baseline.SECONDARY,mode,face,PARENT)for mode in baseline.MODES for face in [254,255])
 assert not (prior.DOC/'private-four-whole-current-counterpart-nomination.json.gz').exists()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT
 return pins,latest,saved,records,parents,nom,raw,pv,patch,scope,result

def schema_only():
 pins,latest,saved,records,parents,nom,raw,pv,patch,scope,result=load()
 return dict(passed=True,caller=ref(Path(__file__)),safeWholeCurrentIDs=SAFE,onlyConflictCurrentParent=PARENT,onlyConflictingUID=baseline.SECONDARY,conflictingSourceFaces=[254,255],allFourModesRetained=True,allTwelvePriorWholeFourPackedCoveragePassesRetained=True,freshActualGroundFaces=11634,oldCandidateFacets=11606,protectedLiterals=68,completeActors=6650,completeBasicRecords=1911,wholeAffectedBasicActors=52,noResidualSubtractionLatticeHullPackingPairFiniteDBLeaseWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,latest,saved,records,parents,nom,raw,pv,patch,scope,old=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder,job in [(prior.DOC,JOB)]+prior.RECEIPTS:
  receipt=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();_,ground,_,_,attrs,actual_scope,actors=finite.inputs();assert sha(ground)==latest['newGroundSHA256'] and actual_scope==scope
 safe_records=[r for r in records if r['originalCurrentFace']in SAFE];parent_record=next(r for r in records if r['originalCurrentFace']==PARENT);parent=np.asarray(parent_record['wholeOriginalCurrentTriplet'],dtype='<f8')
 safe_triangles=np.asarray([r['wholeOriginalCurrentTriplet']for r in safe_records],dtype='<f8');safe_union=np.concatenate([ground,safe_triangles]);safe_selection=baseline.CompleteGround(safe_union);current_selection=baseline.CompleteGround(ground)
 secondary=next(worlds for uid,worlds,_,_ in actors if uid==baseline.SECONDARY);masks=[];enclosures=[];unresolved=[];safe_targets=[]
 # Rebind the fresh12 rows; derive only residuals still missing after SAFE3.
 for row in saved:
  face=secondary[row['mode']][row['sourceFace']];old_row=row['freshSavedRowVerbatim'];assert sha(face)==old_row['currentBaselineVerbatim']['sourceFaceSHA256']
  old_ids,old_binding=current_selection.select([[F(v)for v in p]for p in face.tolist()]);assert old_binding==old_row['completeNewGroundSelection'] and sha(ground[old_ids])==old_row['completeRelevantGroundSHA256']
  ids,binding=safe_selection.select([[F(v)for v in p]for p in face.tolist()]);proof=finite.finite_record(face,safe_union[ids]);safe_targets.append(dict(**row,completeSafeThreeSelection=binding,safeThreeFiniteProof=proof,hypotheticalOnlyNotActualGroundCapture=True))
  if proof['projectionCovered']:
   if not proof['ordinaryBoundProved']:unresolved.append(dict(mode=row['mode'],sourceFace=row['sourceFace'],reason='SAFE3 complete coverage but ordinary clearance fails',proof=proof))
   continue
  poly=[point(p)for p in face[:,[0,2]]];remaining=[poly]
  for t in safe_union[ids]:
   p=[point(q)for q in t[:,[0,2]]]
   if signed_area(p):
    if signed_area(p)<0:p.reverse()
    remaining=[part for piece in remaining for part in subtract(piece,p)]
   pulse()
   if not remaining:break
  coverage=proof['coarse']['completeOriginalProjectionCoverage'];assert str(sum((abs(signed_area(p))for p in remaining),F(0)))==coverage['exactUncoveredAreaM2'] and len(remaining)==coverage['remainingPositiveAreaPieces']
  for piece,poly in enumerate(remaining):
   mi=len(masks);record=dict(mask=mi,uid=baseline.SECONDARY,mode=row['mode'],sourceFace=row['sourceFace'],sourceFaceSHA256=sha(face),sourceWorldSHA256=row['wholeWorldSHA256'],piece=piece,exactFreshResidualXZ=serial(poly),completeSafeThreeSelectedGroundBinding=binding,completeSafeThreeRelevantGroundSHA256=sha(safe_union[ids]),freshSafeThreeFiniteProof=proof,currentParentOriginalFace=PARENT,wholeCurrentParentTripletSHA256=sha(parent),allPriorNegativesAndRolesRetained=True);masks.append(record)
   try:
    certification=enclose(poly,parent.tolist(),pulse=pulse);enclosures.append(dict(maskVerbatim=record,completeFloat32EnclosureCertificate=certification))
   except (AssertionError,ValueError,OverflowError)as e:unresolved.append(dict(maskVerbatim=record,reason=type(e).__name__+': '+str(e),noBBoxBufferSnapOrOtherLayerYWaiver=True,noGeometryEmittedForThisMask=True))
  pulse()
 safe_selection.verify_binding();current_selection.verify_binding()
 save(DOC/'fresh-only6170-residuals-and-certified-enclosures.json.gz',serial(dict(safeWholeCurrentCounterpartsVerbatim=safe_records,conflictingWholeCurrent6170Verbatim=parent_record,twelveSafeThreePackedFiniteProofs=safe_targets,allFreshOnly6170ResidualMasks=masks,enclosures=enclosures,unresolved=unresolved,completePriorWholeCurrentConflictPacketVerbatim=old,allWorldLabelsPreservedNoUnprovenMaskReduction=True,onlyActualResidualsEnclosedNotOriginalIdeal22Masks=True,allOldGeometryAndSourceInventoriesUntouched=True,physicalAccepted=False,installationApproved=False)))
 # Every generated piece keeps independent source-mask/world lineage. No model
 # simplification, mask deduplication, or replacement of old source triangles.
 additions=[]
 for enclosure in enclosures:
  c=enclosure['completeFloat32EnclosureCertificate'];nodes=c['completeOwnPlanePackedNodeCertificates']
  for r in c['actualPackedFacetRecords']:
   i=r['localFacet'];additions.append(dict(actualPackedTriplet=r['actualPackedTriplet'],exactOwnPlanePoints=[nodes[j]['exactOwnPlanePoint']for j in [0,i+1,i+2]],mask=enclosure['maskVerbatim']['mask'],completePackingFacetCertificate=r,completeClosedResidualCertificate=c['actualHeightIndexedWholeClosedMaskCoverage']))
 pieces=np.asarray([r['actualPackedTriplet']for r in additions],dtype='<f8').reshape(-1,3,3);pxz=pieces[:,:,[0,2]];low=pxz.min(1)if len(pieces)else np.empty((0,2));high=pxz.max(1)if len(pieces)else np.empty((0,2));projected=[projected_mask(p)for p in pieces];cache={}
 def assess(uid,mode,w,prior_world):
  assert sha(w)==prior_world['wholeWorldSHA256'] and len(w)==prior_world['completeSourceFaces'];safe_chunks=[];accounted=set()
  # Exact safe3 reuse is authenticated against EVERY whole source face row,
  # complete4 current ancestry, all old chunks and unchanged world bytes.
  for q in prior_world['chunks']:
   chunk=read(check(q));assert chunk['uid']==uid and chunk['mode']==mode and chunk['wholeWorldSHA256']==sha(w) and chunk['fourWholeCurrentSHA256']==sha(parents)
   for r in chunk['rows']:
    face=r['sourceFace'];assert face not in accounted and r['sourceFaceSHA256']==sha(w[face]);accounted.add(face)
    for p in r['completeWholeProjectedPairProofs']:
     if p['originalCurrentFace']in SAFE:
      proof=p['unchangedFullProjectedPairProof'];assert not proof.get('violatesExistingOrdinaryBound') and not proof.get('exactSourceZero') and not proof.get('collapsedCurrentGroundProjection')
   safe_chunks.append(q);pulse()
  assert accounted==set(range(len(w)));rows=[];chunks=[];conflicts=[];uncredited=[]
  for face_id,face in enumerate(w):
   xz=face[:,[0,2]];ids=np.flatnonzero(np.all(high>=xz.min(0),axis=1)&np.all(low<=xz.max(0),axis=1));proofs=[]
   for k in ids:
    key=(sha(face),sha(pieces[k]))
    if key not in cache:cache[key]=masked_current_pair(face,pieces[k],projected[k])
    proof=cache[key];proofs.append(dict(newEnclosureLocalFacet=int(k),mask=additions[k]['mask'],actualPackedTripletSHA256=sha(pieces[k]),unchangedFullProjectedActualPairProof=proof))
    if proof.get('violatesExistingOrdinaryBound'):conflicts.append(dict(sourceFace=face_id,sourceFaceSHA256=sha(face),sourceWholeFace=face.tolist(),enclosureLocalFacet=int(k),mask=additions[k]['mask'],exactActualPackedConflictWitness=proof))
    if proof.get('exactSourceZero')or proof.get('collapsedCurrentGroundProjection'):uncredited.append(dict(sourceFace=face_id,enclosureLocalFacet=int(k),proofVerbatim=proof))
   rows.append(dict(sourceFace=face_id,sourceFaceSHA256=sha(face),completeEnclosureClosedAABBCandidates=ids.tolist(),allOmittedEnclosuresStrictlyClosedAABBDisjoint=True,completeActualPackedFullProjectedPairProofs=proofs,noSupportRootRoleCredit=True))
   if len(rows)==64 or face_id==len(w)-1:
    path=DOC/'chunks'/uid.replace('/','-').replace(':','-')/mode/(str(len(chunks)).zfill(5)+'.json.gz');save(path,dict(uid=uid,mode=mode,wholeWorldSHA256=sha(w),completeNewEnclosureTripletsSHA256=sha(pieces),rows=rows));chunks.append(ref(path));rows=[];pulse()
  return dict(uid=uid,mode=mode,completeSourceFaces=len(w),wholeWorldSHA256=sha(w),authenticatedSafeThreePriorChunksVerbatim=safe_chunks,safeThreeWholeCurrentPriorWorldVerbatim=prior_world,noOldHashLabelOrApprovalRelabelling=True,newActualEnclosureChunks=chunks,conflicts=conflicts,uncredited=uncredited,allWholeFacesAccounted=True,noPhysicalAcceptance=True)
 results=[];prior_actors={r['uid']:r for r in old['completeActors']}
 for uid,worlds,_,source_sha in actors:
  old_actor=prior_actors[uid];assert old_actor['sourceSHA256']==source_sha
  results.append(dict(uid=uid,sourceSHA256=source_sha,worlds=[assess(uid,mode,worlds[mode],next(w for w in old_actor['worlds']if w['mode']==mode))for mode in baseline.MODES]));print(json.dumps(dict(uid=uid,certified6170EnclosureCompatibilityOnly=True)),flush=True)
 prior_basic={r['uid']:r for r in old['complete1911BasicRows']};affected={r['uid']for r in scope['affectedBasic']};basics=[]
 for r in attrs['basicContextRows']:
  uid=r['uid'];previous=prior_basic[uid]
  if uid in affected:
   positions=np.asarray(r['position'],dtype='<f8').reshape(-1,3);w=finite.triangles(positions[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)]);basics.append(dict(uid=uid,wholeEnclosureCompatibility=assess(uid,'capturedConstructorFloat32World',w,previous['wholeFourCurrentCompatibility']),completeUnusedPositionVertices=len(positions),priorBasicVerbatim=previous))
  else:basics.append(dict(uid=uid,priorBasicVerbatim=previous,strictWholeParentOutsideContextRetained=True,noAcceptanceCredit=True))
 assert len(basics)==1911 and sum('wholeEnclosureCompatibility'in r for r in basics)==52
 # Closure on complete hypothetical actual packed union, not an ideal mask proof.
 trial=np.concatenate([safe_union,pieces]);selection=baseline.CompleteGround(trial);targets=[]
 for row in saved:
  face=secondary[row['mode']][row['sourceFace']];ids,binding=selection.select([[F(v)for v in p]for p in face.tolist()]);proof=finite.finite_record(face,trial[ids]);targets.append(dict(**row,completeTrialGroundSelection=binding,completeTrialRelevantGroundSHA256=sha(trial[ids]),actualPackedCompleteUnionFiniteProof=proof,hypotheticalUntilFreshActualProductionCapture=True));pulse()
 selection.verify_binding();streams=[w for a in results for w in a['worlds']]+[r['wholeEnclosureCompatibility']for r in basics if 'wholeEnclosureCompatibility'in r];clear=all(not w['conflicts'] and not w['uncredited']for w in streams);covered=all(r['actualPackedCompleteUnionFiniteProof']['projectionCovered'] and r['actualPackedCompleteUnionFiniteProof']['ordinaryBoundProved']for r in targets)
 save(DOC/'complete-whole-scope-actual-enclosure-compatibility-and12-coverage.json.gz',serial(dict(actors=results,complete1911BasicRows=basics,all52WholeBasicAndFourActorsFourWorldsRetained=True,allGeneratedPackedEnclosuresOrdinaryCompatibleWithoutUncredited=clear,allTwelveActualPackedUnionCoverageAndOrdinaryPassed=covered,twelveTargetResults=targets,allOriginalLatestFullFiniteNegativesVerbatim=latest,canonical860PointGuardsRetainedAsPriorContext=True,freshActualProductionFullFiniteOverlapMAXRootRuntimeBrowserPending=True,unresolvedCertificates=unresolved,physicalAccepted=False,installationApproved=False)))
 if not unresolved and clear and covered:
  bound=append_saved_current(raw,pv,patch['nativeMesh'],safe_records,nom['protectedWholeCurrentTripletsUnchanged']);candidate=bound['candidateRawPositionTriplets'];provenance=bound['candidateFaceProvenance'];positions=bound['newNativeMesh']['position'];indices=bound['newNativeMesh']['index'];enclosure_mapping=[]
  for r in additions:
   j=len(candidate);face=np.asarray(r['actualPackedTriplet'],dtype='<f8');assert face.tobytes()==face.astype('<f4').astype('<f8').tobytes();k=len(positions)//3;positions.extend(face.reshape(-1).tolist());indices.extend(range(k,k+3));candidate.append(face.tolist());provenance.append(dict(candidateFace=j,kind='capturedCurrentRing',originalFace=PARENT,completeCurrentSourceAttribution=parent_record['completeCurrentAttribution'],region='certifiedFloat32FreshResidualEnclosureOnOwnParent',computedFragment=True,savedInputByteExact=False,rawNominationFaceSHA256=sha(face),exactOriginalPlanePoints=r['exactOwnPlanePoints'],currentResidualEnclosure=dict(mask=r['mask'],completeFreshMaskLineage=masks[r['mask']],completePackingFacetCertificate=r['completePackingFacetCertificate'],allXZAlreadyExactFloat32OwnPlaneYCertified=True,noOtherLayerYUsed=True)))
   enclosure_mapping.append(dict(newCandidateFace=j,mask=r['mask'],completePackedFaceCertificate=r))
  assert np.asarray(candidate[:11606],dtype='<f8').tobytes()==raw.tobytes() and provenance[:11606]==pv and positions[:len(patch['nativeMesh']['position'])]==patch['nativeMesh']['position'] and indices[:len(patch['nativeMesh']['index'])]==patch['nativeMesh']['index']
  bound['newNativeMesh']['source']=dict(kind='private-three-safe-whole-current-and-certified6170-residual-enclosures',noNewPackingOfWholeCurrentTriplets=True,noApprovalOrHeightLayerYTransfer=True)
  bound['safeThreeAppendOperationContextVerbatim']=dict(noNewPackingOrSourcePlaneInterpolation=bound['noNewPackingOrSourcePlaneInterpolation'],onlyWholeCurrentIDs=SAFE,operationBeforeCertified6170Fragments=True)
  bound['noNewPackingOrSourcePlaneInterpolation']=False
  bound['certified6170OwnPlaneInterpolationAndFloat32YPackingDeclared']=True
  save(DOC/'private-three-safe-current-certified-6170-nomination.json.gz',serial(dict(schema='upton-three-safe-current-certified6170-enclosure-nomination-v1',**bound,completeCurrent6170EnclosureMapping=enclosure_mapping,previousFull22Nomination=ref(capture.NOM_DOC/'private-full22-current-plane-restoration-nomination.json.gz'),previousActualCaptureCandidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),completeNewCandidateFacets=len(candidate),completeNewRawSHA256=sha(np.asarray(candidate,dtype='<f8')),wholeCurrentSafeIDs=SAFE,onlyCertifiedEnclosureParentID=PARENT,all11606OldRawProvenancePositionIndexAnd68ProtectedBytesRetained=True,allOldMapsCountsPartitionProofsHistoricalOnly=True,completeEnclosureCertificates=ref(DOC/'fresh-only6170-residuals-and-certified-enclosures.json.gz'),completeWholeScopeCompatibilityAndPackedCoverage=ref(DOC/'complete-whole-scope-actual-enclosure-compatibility-and12-coverage.json.gz'),allSourceCurrentInventoriesWholeParent6650Actors1911Basic52AndFourWorldRolesRetained=True,freshActualProductionFullFiniteOverlapMAXSeamRootRuntimeBrowserRequired=True,originalBuildingGeometryPoseChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0)))
 fence();refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 baseline.module(baseline.FREEZER,'upton_certified6170_freezer').freeze(BATCH,'three-safe-authentic-current-and-exact-certified-float32-only6170-enclosure-private-nomination',[check(q)for q in refs],dict(uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--nominate-three-safe-current-certified6170-only'in sys.argv and not DOC.exists() and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE,baseline.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-three-safe-certified6170-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
