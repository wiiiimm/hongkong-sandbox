"""ROOT-only whole22 residual current-plane coverage/actor compatibility.

No terrain/model nomination geometry is emitted. All current counterpart planes
must relate to actual whole saved gap regions, and every complete owned/affected
foreign stream is checked inside those regions. No nearby alias or approval.
"""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time,uuid,subprocess
import numpy as np
import upton_three_foreign_after_own_layer_gap_location_draft_v1_20261013 as location
import upton_three_own_layer_saved_actual_union_delta_draft_v1_20261013 as finite
from upton_captured_ground_tuple_representation_v1_20261012 import adapt_captured_ground
from exact_closed_ground_aabb_pruning_v1_20261011 import enclosing_float
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import masked_current_pair
from polyu_five_mask_source_plane_partition_v1_20261014 import masks_from_records,partition,serial
from southside_saved_local_core_parent_adapter_v3_20261012 import old
from upton_exact_full_residual_current_coverage_v1_20261014 import cover_whole_polygon
from exact_original_projection_coverage_v2_20261010 import signed_area
from run import ROOT,HERE,read,save,connect,reservations
baseline=finite.baseline;ref,check=finite.ref,finite.check;sha=finite.sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-full22-original-current-restoration-feasibility-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RECEIPTS=[(location.DOC,'f80b5da26c9f66cfd04120834e4b44c3c2e9b3c476baada7ea88b6a082d4c21d'),(finite.DOC,'16f88f149270ccc063a09d29de19f83c88a285a8bc8b2e7d06be89f0031e1188')]
TEST='test_upton_exact_full_residual_current_coverage_v1_20261014'

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 for folder,job in RECEIPTS:assert read(folder/'result.json')['jobId']==job
 saved=read(location.DOC/'complete-three-foreign-gap-locations-and-ancestors.json.gz');assert len(saved['rows'])==12 and saved['uniqueForeignFacets']==3
 original=[r for r in saved['rows']if r['savedSourceRowVerbatim']['mode']=='original'];assert [r['savedSourceRowVerbatim']['face']for r in original]==[87,205,228]
 assert [r['locationOnlyProof']['remainingPositiveAreaPieces']for r in original]==[3,17,2]
 assert sum(len(r['locationOnlyProof']['completeGapBoundary'])for r in original)==80
 for r in original:
  s=r['savedSourceRowVerbatim'];same=[q for q in saved['rows']if q['savedSourceRowVerbatim']['face']==s['face']]
  assert {q['savedSourceRowVerbatim']['mode']for q in same}==set(baseline.MODES)
  assert all(q['locationOnlyProof']['exactRemainingPolygonsXZ']==r['locationOnlyProof']['exactRemainingPolygonsXZ']for q in same),'Distinct world residuals require separate full masks; no reduction allowed'
 latest=read(finite.DOC/'complete-actual-union-finite-delta.json.gz');assert latest['newGroundSHA256']==finite.GROUND_SHA and latest['completeNewDrawnFaces']==11608
 assert [r['uid']for r in latest['actors']]==baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE]and len(latest['completeBasicRows'])==1911
 assert latest['completeNativeActorScope']==6650 and latest['secondaryHeldAsForeignReceivesNoSupportCredit']and not latest['physicalAccepted']and not latest['installationApproved']
 for a in latest['actors']:assert [w['mode']for w in a['worlds']]==list(baseline.MODES)
 assert sum(a['worlds'][0]['completeFaces']for a in latest['actors']if a['uid']in baseline.OWNED)==13312
 assert next(a['worlds'][0]['completeFaces']for a in latest['actors']if a['uid']==baseline.SECONDARY)==392 and next(a['worlds'][0]['completeFaces']for a in latest['actors']if a['uid']==baseline.NATIVE)==616
 scope=read(check(latest['same6650WholeScope']));assert scope['completeNativeActors']==6650 and len(scope['affectedBasic'])==52 and not scope['otherTouchingNativeCompleteActualStreamsUnqualified']
 assert sum(len(a['selectedWholeFaceIDs'])for a in scope['affectedBasic'])==2114 and scope['allFacetAndBodyRoleObligationsRemain']and scope['secondaryCurrentFormsMustBeIncludedInFreshForeignPhysicalChecks']
 affected={r['uid']:r for r in scope['affectedBasic']}
 for q in latest['completeBasicRows']:assert q['completeScope']['selectedFaceIDs']==(affected[q['uid']]['selectedWholeFaceIDs']if q['uid']in affected else [])
 check(latest['allZerosAnd23CrossingsRetained'])
 nomination=read(finite.capture.NOM_DOC/'private-own-layer-projected-edge-subdivision-nomination.json.gz');original_nomination=read(check(nomination['originalNomination']))
 attr=read(check(original_nomination['allCurrentTriplets']));current,representation=adapt_captured_ground(attr['rows'][0],expected_faces=9214,expected_ground_sha='b4916dac0a7c911a5b20e7dde729fa9a99fca63fa01896db8380523e6158670a',expected_source_counts=[('3d-viewer/city/data/terrain.json',32),('3d-viewer/city/data/government-native-79882-0.json',9182)])
 attribution=read(finite.capture.V6/'packed-source-current-before-compatibility.json.gz')['completeCurrentAttribution'];assert len(attribution)==9214
 for i,q in enumerate(attribution):assert q['globalCurrentFace']==i and q['globalOrderedSavedFaceSHA256']==sha(current[i])
 inv=original_nomination['wholeCurrentFaceInventory'];assert len(inv)==9214
 for i,q in enumerate(inv):assert q['originalFace']==i and q['originalFaceSHA256']==sha(current[i])and q['completeOriginalTripletRetainedInSavedInput']
 source_packet=read(check(original_nomination['allSourceOriginalTriplets']));source=np.asarray(source_packet['allOriginalTriplets'],dtype='<f8');assert source.shape==(122721,3,3)and sha(source)=='3ace7f401040b2109fd196c603f506d42f0238292742e528c3c46f786b2d93e6'
 source_inv=original_nomination['wholeSourceOriginalFaceInventory'];assert len(source_inv)==122721
 for i,q in enumerate(source_inv):assert q['originalFace']==i and q['originalFaceSHA256']==sha(source[i])and q['completeOriginalTripletRetainedInSavedInput']
 assert len(nomination['protectedWholeCurrentTripletsUnchanged'])==68
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT
 return pins,saved,original,latest,scope,current,attribution,representation

def schema_only():
 p,s,original,latest,scope,current,attribution,rep=load()
 return dict(passed=True,caller=ref(Path(__file__)),wholeResidualPolygons=22,wholeResidualBoundaryEdges=80,savedAllFourWorldRows=12,completeCurrentFacets=9214,completeOriginalTINFacets=122721,completeNativeActorScope=6650,completeOwnedFacesPerMode=13312,secondary392AndNative616AllFourModes=True,completeBasicRows=1911,affectedBasicActors=52,affectedBasicSelectedFacets=2114,protectedLiteralCurrentFacets=68,noMaskCoveragePlanePartitionActorReconstructionOrPredicateDBLeaseWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,saved,original,latest,scope,current,attribution,representation=load()
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder,job in RECEIPTS:
  receipt=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir()
 # World reconstruction/hash verification is owned-only, with unchanged saved
 # actor binding code. No source archive decoder or complete finite replay.
 _,_,_,_,attrs,_,actors=finite.inputs()
 for uid,worlds,_,source_sha in actors:
  a=next(r for r in latest['actors']if r['uid']==uid);assert a['sourceSHA256']==source_sha
  for mode,w in worlds.items():assert sha(w)==next(r['wholeWorldSHA256']for r in a['worlds']if r['mode']==mode)
 masks=[];polygons=[]
 for r in original:
  s=r['savedSourceRowVerbatim']
  for pi,values in enumerate(r['locationOnlyProof']['exactRemainingPolygonsXZ']):
   poly=[tuple(F(v)for v in p)for p in values];assert abs(signed_area(poly))>0
   if signed_area(poly)<0:poly.reverse()
   polygon_id=len(polygons);polygons.append(dict(polygon=polygon_id,uid=s['uid'],foreignFace=s['face'],piece=pi,exactWholeResidualPolygonXZ=poly,allFourWorldLocationRecords=[q for q in saved['rows']if q['savedSourceRowVerbatim']['face']==s['face']]))
   lifted=[(p[0],F(0),p[1])for p in poly];fans=list(old.fan(lifted));assert sum((abs(signed_area([(p[0],p[2])for p in t]))for t in fans),F(0))==abs(signed_area(poly))
   for t in fans:
    if abs(signed_area([(p[0],p[2])for p in t])):masks.append(dict(polygon=polygon_id,uid=s['uid'],foreignFace=s['face'],piece=pi,exactClosedProjection=[(p[0],p[2])for p in t]))
 assert len(polygons)==22
 compiled=masks_from_records(masks)
 low=np.array([[enclosing_float(q['bounds'][k],True)for k in [0,1]]for q in compiled]);high=np.array([[enclosing_float(q['bounds'][k],False)for k in [2,3]]for q in compiled])
 cxz=current[:,:,[0,2]];clo=cxz.min(1);chi=cxz.max(1)
 current_ids=np.flatnonzero(np.any(np.all(chi[:,None,:]>=low[None,:,:],axis=2)&np.all(clo[:,None,:]<=high[None,:,:],axis=2),axis=1))
 projected=[];counterparts=[];excluded=[]
 for i in current_ids:
  face=current[i];tri=[(F(float(p[0])),F(float(p[2])))for p in face];a=signed_area(tri)
  if a==0:excluded.append(dict(originalCurrentFace=int(i),wholeOriginalCurrentTriplet=face.tolist(),completeCurrentAttribution=attribution[i],projectedVerticalOrZeroNoAffineHeightCredit=True));continue
  if a<0:tri.reverse()
  projected.append((int(i),tri));proof=partition(face,compiled)
  if proof['inside']:counterparts.append(dict(originalCurrentFace=int(i),wholeOriginalCurrentTriplet=face.tolist(),wholeOriginalCurrentTripletSHA256=sha(face),completeCurrentAttribution=attribution[i],completeOwnCurrentPlaneMaskPartition=serial(proof),noOtherLayerYOrSourceGeometryChange=True))
  pulse()
 cover=[]
 for p in polygons:
  proof=cover_whole_polygon(p['exactWholeResidualPolygonXZ'],projected)
  cover.append(dict(maskVerbatim=serial(p),wholeCurrentCoverage=serial(proof)));pulse()
 save(DOC/'complete22-whole-gap-current-counterpart-plane-coverage.json.gz',serial(dict(rows=cover,completeCurrentCounterpartPlanes=counterparts,completeCurrentROIFaceIDs=current_ids.tolist(),allOtherCurrentFacesStrictlyClosedAABBDisjointFromEveryMask=True,completeProjectedVerticalOrZeroCurrentROIContext=excluded,fullCurrentRepresentation=representation,source122721InventoryUnchanged=True,all80ClosedBoundariesChecked=True,notRuntimeSamplerMAXOrPackingOrAcceptanceProof=True)))
 affine_current_ids=np.asarray([i for i,t in projected],dtype=np.int64)
 affected={r['uid']:r for r in scope['affectedBasic']};basic_previous={r['uid']:r for r in latest['completeBasicRows']};results=[];cache={}
 def assess(uid,mode,w,role,prior_world):
  assert sha(w)==prior_world['wholeWorldSHA256']and len(w)==prior_world['completeFaces']
  chunks=[];rows=[];conflicts=[];uncredited=[];outside=[]
  for face_id,face in enumerate(w):
   xz=face[:,[0,2]];mids=np.flatnonzero(np.all(high>=xz.min(0),axis=1)&np.all(low<=xz.max(0),axis=1));pairs=[]
   if not len(mids):outside.append(face_id)
   else:
    gids=affine_current_ids[np.all(chi[affine_current_ids]>=xz.min(0),axis=1)&np.all(clo[affine_current_ids]<=xz.max(0),axis=1)]
    for gid in gids:
     local=[int(mi)for mi in mids if np.all(high[mi]>=clo[gid])and np.all(low[mi]<=chi[gid])]
     for mi in local:
      key=(sha(face),int(gid),int(mi))
      if key not in cache:cache[key]=masked_current_pair(face,current[gid],compiled[mi]['lineage']['exactClosedProjection'])
      proof=cache[key]
      if proof.get('closedMaskedProjectionDisjoint'):continue
      pairs.append(dict(originalCurrentFace=int(gid),mask=int(mi),wholeGapPolygon=compiled[mi]['lineage']['polygon'],unchangedExactMaskedCurrentPairProof=proof))
      if proof.get('violatesExistingOrdinaryBound'):conflicts.append(face_id)
      if proof.get('exactSourceZero')or proof.get('collapsedCurrentGroundProjection'):uncredited.append(face_id)
      pulse()
   rows.append(dict(sourceFace=face_id,wholeSourceFaceSHA256=sha(face),completeClosedMaskCandidates=mids.tolist(),allOtherMasksStrictlyClosedAABBDisjoint=True,allRelevantCurrentPlaneMaskPairs=pairs,originalCurrentProjectedVerticalsRetainedInWholeROIEvidenceNotUsedAsAffineHeightPlanes=True,noRoleRootSupportOrAcceptanceCredit=True))
   if len(rows)==64 or face_id==len(w)-1:
    path=DOC/'chunks'/uid.replace('/','-').replace(':','-')/mode/(str(len(chunks)).zfill(5)+'.json.gz');save(path,dict(uid=uid,mode=mode,role=role,wholeWorldSHA256=sha(w),completeCurrentGroundSHA256=sha(current),rows=rows));chunks.append(ref(path));rows=[];pulse()
  return dict(uid=uid,mode=mode,role=role,wholeWorldSHA256=sha(w),completeFaces=len(w),chunks=chunks,allSourceFacesAccounted=True,strictlyMaskDisjointWholeSourceFaceIDs=outside,conflictingCurrentMaskSourceFaces=sorted(set(conflicts)),uncreditedCurrentMaskSourceFaces=sorted(set(uncredited)),priorFiniteWorldVerbatim=prior_world,allExistingUncoveredOrdinaryRoleRootNegativesRemainVerbatim=True,notWholeActorPhysicalOrSupportAcceptance=True)
 for uid,worlds,_,source_sha in actors:
  a=next(r for r in latest['actors']if r['uid']==uid)
  results.append(dict(uid=uid,sourceSHA256=source_sha,role=a['role'],worlds=[assess(uid,mode,worlds[mode],a['role'],next(r for r in a['worlds']if r['mode']==mode))for mode in baseline.MODES]));print(json.dumps(dict(uid=uid,completeCurrentMaskFeasibilityOnly=True)),flush=True)
 basic_rows=[]
 for q in attrs['basicContextRows']:
  uid=q['uid'];old_row=basic_previous[uid]
  if uid in affected:
   pos=np.asarray(q['position'],dtype='<f8').reshape(-1,3);w=baseline.triangles(pos[np.asarray(q['index'],dtype=np.int64).reshape(-1,3)])
   prior_world=old_row['findings']['worlds'][0];assert prior_world['mode']=='capturedConstructorFloat32World'and sha(w)==prior_world['wholeWorldSHA256']
   result=assess(uid,'capturedConstructorFloat32World',w,'complete-affected-BASIC-regression',prior_world)
   basic_rows.append(dict(uid=uid,completePositionVerticesIncludingUnused=len(pos),wholeCurrentMaskFeasibility=result,priorBasicRowVerbatim=old_row))
  else:basic_rows.append(dict(uid=uid,priorBasicRowVerbatim=old_row,strictWholeParentOutsideProofRetained=True,noNewAcceptanceCredit=True))
 assert len(basic_rows)==1911 and sum('wholeCurrentMaskFeasibility'in r for r in basic_rows)==52
 current_masks_clear=all(not w['conflictingCurrentMaskSourceFaces']and not w['uncreditedCurrentMaskSourceFaces']for a in results for w in a['worlds'])and all(not r['wholeCurrentMaskFeasibility']['conflictingCurrentMaskSourceFaces']and not r['wholeCurrentMaskFeasibility']['uncreditedCurrentMaskSourceFaces']for r in basic_rows if 'wholeCurrentMaskFeasibility'in r)
 save(DOC/'complete-full22-original-current-restoration-feasibility.json.gz',dict(whole22PolygonCoverage=ref(DOC/'complete22-whole-gap-current-counterpart-plane-coverage.json.gz'),actors=results,complete1911BasicRows=basic_rows,all52AffectedWholeBasicStreamsRetained=True,wholeCurrentMaskOrdinaryCompatibilityWithoutUncredited=current_masks_clear,allWholeClosedResidualsCoveredByAuthenticCurrent=all(r['wholeCurrentCoverage']['wholeClosedResidualCovered']for r in cover),latestFullFiniteNegativesVerbatim=latest,historicalInsufficientOwnLayerNomination=ref(finite.capture.NOM_DOC/'private-own-layer-projected-edge-subdivision-nomination.json.gz'),all68ProtectedLiteralsUnchangedNoTerrainEmitted=True,allZero23CrossingRootSupportForeignObligationsRetained=True,fullParentExteriorAndRuntimeMAXPackingSeamGatesPending=True,noTerrainBuildingPoseOrSourceGeometryEdits=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()];fence()
 baseline.module(baseline.FREEZER,'upton_full22_original_current_feasibility_freezer').freeze(BATCH,'whole22-saved-gap-original-current-counterpart-plane-and-complete-actor-feasibility-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE],sourceOnly=True,terrainEmitted=False,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--test-full22-original-current-restoration-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE,baseline.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-full22-original-current-feasibility-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
