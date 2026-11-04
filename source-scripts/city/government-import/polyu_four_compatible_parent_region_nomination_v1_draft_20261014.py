"""UNEXECUTED append-only four-mask parent restoration; ROOT reviewed execution only."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib,sys,time,uuid,subprocess,copy,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
from polyu_five_mask_source_plane_partition_fast_v1_20261014 import PreparedMasks
from polyu_five_mask_positive_hit_partition_v3_draft_20261014 import partition
from polyu_five_mask_source_plane_partition_v1_20261014 import serial
import polyu_compatible_current_parent_regions_v1_draft_20261014 as geometry
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-four-compatible-parent-region-nomination-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/'government-xl-polyu-four-gap-source-compatible-parent-regions-v1-20261014-proposal';LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
FEAS=BASE/'government-xl-polyu-nine-complete-parent-restoration-feasibility-v1-20261013'
MAX=BASE/'government-xl-polyu-saved64-actual-max-reviewed-validator-v1-20261014'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
UIDS=['landsd/72322:0','landsd/89540:0','landsd/258852:0','landsd/305600:0']
JOB='7bc85e0b01ff4495ee14cd5f0bb953e70f34c97d2d14ab4e616fad53ef7ef2e4'
def ref(p):return dict(path=str(Path(p).resolve().relative_to(ROOT)),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def check(q):
 p=(ROOT/q['path']).resolve();assert p.is_relative_to(ROOT)and ref(p)==q,q;return p
def fan(poly):return [[poly[0],poly[i],poly[i+1]]for i in range(1,len(poly)-1)]
def load():
 pins=read(PROPOSAL/'nomination-draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 receipt=read(MAX/'result.json');cert=read(MAX/'ROOT-VERIFIED.json');assert receipt['jobId']==cert['jobId']==JOB and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
 outcome=read(MAX/'unchanged-validator-outcome.json');assert outcome['passed']and outcome['allFieldsExceptSourceOverlapExactlyEqual']and not outcome['currentAcceptance']
 original=read(check(outcome['metadataOnlyCandidate']));assert len(original['nativeMesh']['index'])==148459*3 and len(original['nativeMesh']['position'])==587502*3
 assert mesh_binding({k:original['nativeMesh'][k]for k in ['position','index']})==pins['completeOldMeshBinding']
 assert read(FEAS/'result.json')['jobId']==pins['completedFeasibilityJob']
 feasibility=read(FEAS/'complete-nine-parent-restoration-feasibility.json.gz');source=read(check(feasibility['exactSourceContext']));worlds={}
 for mode,row in source['completeWorldStreams'].items():
  raw=np.asarray(row['completeWorldTriangles'],dtype='<f8');assert raw.shape==(10536,3,3)and np.isfinite(raw).all()
  assert hashlib.sha256(raw.tobytes()).hexdigest()==row['completeWorldTriangleSHA256']
  worlds[mode]=(raw,raw[:,:,[0,2]].min(1),raw[:,:,[0,2]].max(1),row['completeWorldTriangleSHA256'])
 assert len(worlds)==4 and len(feasibility['complete12CapturedParentFacets'])==12
 local=read(PROPOSAL/'complete-failed-saved-column-analysis.json');assert local['mode']=='complete-saved-failed-sites'and local['noDBLeaseOrJob']
 assert [r['uid']for r in local['rows']]==UIDS and [r['completeFailedSites']for r in local['rows']]==[446,86,139,81]
 assert all(r['analyzedSites']==r['completeFailedSites']and not r['minimumHeightConflictingSites']and not r['savedBeforeHeightConflictingSites']for r in local['rows'])
 return pins,receipt,outcome,original,feasibility,worlds
def schema_only():
 p,r,o,c,f,w=load()
 return dict(passed=True,caller=ref(Path(__file__)),oldFaces=148459,oldUnusedPositionSlots=587502,completeSourceWorlds=4,sourceFacesPerWorld=10536,
  currentParentFacets=12,completeFailedGuardSites=752,noBadRegionPackingFiniteDBOrLease=True,sourceEpochHistoricalC00=True,currentAcceptance=False)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,outcome,original,feasibility,worlds=load();assert lease['resources']==['immutable-source-proof:'+BATCH]
 prep=read(PROPOSAL/'actual-nomination-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 validation=read(check(prep['helperValidationRef']));assert validation['passedTests']==7 and validation['failedTests']==0 and validation['exitCode']==0
 assert validation['executedCodeRefs']==[ref(Path(geometry.__file__)),ref(HERE/'test_polyu_compatible_current_parent_regions_v1_draft_20261014.py')]
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+validation['evidenceRefs']+[ref(PROPOSAL/'nomination-draft-pins.json'),ref(PROPOSAL/'actual-nomination-readonly-preparation.json')])
 for folder,jid in [(MAX,JOB),(FEAS,pins['completedFeasibilityJob'])]:
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',read(folder/'result.json'))
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert reservations.owns(lease)
 fence();DOC.mkdir();records=[];bad={i:[]for i in range(12)};unique={i:{}for i in range(12)}
 for uid in UIDS:
  actor=next(r for r in feasibility['rows']if r['uid']==uid);mask=read(check(actor['completeMask']))
  for i in mask['positiveMaskIDs']:records.append(dict(uid=uid,originalMask=i,maskEvidence=actor['completeMask'],exactClosedProjection=mask['rows'][i]['exactClosedProjection']))
  for mode in actor['sourceWorlds']:
   ids=set(mode['conflictingSourceFaces']);chunks={i//64 for i in ids};seen=set()
   for ci in sorted(chunks):
    chunkref=mode['chunks'][ci];data=read(check(chunkref));assert data['sourceArithmetic']==mode['arithmetic']and data['completeSourceWorldSHA256']==worlds[mode['arithmetic']][3]
    for row in data['rows']:
     if row['sourceFace']not in ids:continue
     for pair_id,pair in enumerate(row['allIntersectingRetainedParentMaskPairs']):
      proof=pair['unchangedMaskedCurrentPairProof']
      if not proof.get('violatesExistingOrdinaryBound'):continue
      seen.add(row['sourceFace']);points=geometry.forbidden_projection(proof);hull,cells=geometry.strictly_enclosing_f32_hull(points);parent=pair['parentFacet'];signature=tuple(hull)
      occurrence=dict(uid=uid,arithmetic=mode['arithmetic'],sourceFace=row['sourceFace'],mask=pair['mask'],parentFacet=parent,sourceChunk=chunkref,pairOrdinal=pair_id,completeSavedNegativeProof=proof,
       exactClosedBadProjection=points,strictImmediateFloat32Cells=cells,strictEnclosingHull=hull,noOldFailureRemoved=True)
      bad[parent].append(occurrence)
      if signature not in unique[parent]:unique[parent][signature]=len(unique[parent])
    pulse()
   assert seen==ids,(uid,mode['arithmetic'],sorted(ids-seen))
 save(DOC/'complete-saved-bad-region-and-mask-provenance.json.gz',serial(dict(completeMaskOccurrences=records,badRegionOccurrences=bad,exactGeometryDedupPreservesEveryOccurrence=True,
  fullRecordedCurrentParentFacets=feasibility['complete12CapturedParentFacets'],sourceBuildingGeometryAndPoseUnchanged=True)))
 prepared=PreparedMasks(records);mesh=copy.deepcopy({k:original['nativeMesh'][k]for k in ['position','index']});new=[];rejected=[];parents=[];shared={};compat_cache={}
 old_rendered_position=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3)
 old_tuple_keys={old_rendered_position[q].tobytes()for q in np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)};existing=[]
 for parent_id,parent in enumerate(feasibility['complete12CapturedParentFacets']):
  forbidden_records=[]
  for hull in unique[parent_id]:
   for triangle in fan(list(hull)):forbidden_records.append(dict(exactClosedProjection=triangle,forbiddenHull=list(hull)))
  forbidden=PreparedMasks(forbidden_records);inside=partition(parent,prepared);account=[]
  for inside_id,entry in enumerate(inside['inside']):
   for fan_id,triangle in enumerate(fan(entry['polygon'])):
    remaining=partition(triangle,forbidden)
    for region_id,poly in enumerate(remaining['outside']):
     for piece_id,piece in enumerate(geometry.downward_parent_pieces(poly,parent,shared)):
      packed=piece['packedTriplet'];key=np.asarray(packed,dtype='<f8').tobytes()
      if key not in compat_cache:compat_cache[key]=geometry.compatible_piece(packed,worlds)
      proof=compat_cache[key];provenance=dict(parentFacet=parent_id,insideOrdinal=inside_id,insideMask=entry['mask'],firstMaskOwner=records[entry['mask']],fan=fan_id,region=region_id,piece=piece_id,
       idealCompatibleOwnParentPolygon=poly,packing=piece,completeNewPieceOrdinaryCompatibility=proof)
      if not proof['eligible']:rejected.append(provenance);continue
      if key in old_tuple_keys:existing.append(provenance);continue
      old_tuple_keys.add(key);face=len(mesh['index'])//3;slot=len(mesh['position'])//3
      mesh['position'].extend(v for p in packed for v in p);mesh['index'].extend([slot,slot+1,slot+2]);new.append(dict(candidateFace=face,**provenance));account.append(face);pulse()
  parents.append(dict(parentFacet=parent_id,completeExactFourMaskUnionPartition=inside,completeForbiddenHullOccurrences=len(forbidden_records),newCandidateFaces=account))
  save(DOC/'parents'/f'{parent_id:02}.json.gz',serial(parents[-1]));print(json.dumps(dict(parentCompleted=parent_id+1,appended=len(new),rejected=len(rejected))),flush=True);pulse()
 assert mesh['position'][:587502*3]==original['nativeMesh']['position']and mesh['index'][:148459*3]==original['nativeMesh']['index']
 assert np.asarray(mesh['position'][:587502*3],dtype='<f8').tobytes()==np.asarray(original['nativeMesh']['position'],dtype='<f8').tobytes()
 save(DOC/'private-compatible-current-parent-append-nomination.json.gz',serial(dict(newNativeMesh=mesh,previousApprovedCandidate=outcome['metadataOnlyCandidate'],previousCompleteMeshBinding=pins['completeOldMeshBinding'],
  newCompleteMeshBinding=mesh_binding(mesh),appendedFaces=new,rejectedNewPieces=rejected,exactExistingRepresentations=existing,completeParentAccounts=parents,
  all148459OldFacesAnd587502PositionsIncludingUnusedExactlyPreserved=True,sourceFaceZerosRetainedUncredited=True,recordedSourceLayersUnmerged=True,
  sourceOverlapMustBeReviewedForNewGeometry=True,noOldApprovalTransferred=True,actualProductionGuardCoverageAndMAXStillPending=True,
  fullOwned10536FourWorldNative59527FourWorldAndBASICStillRequired=True,historicalSourceContext=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False)))
 refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 spec=importlib.util.spec_from_file_location('polyu_four_parent_freezer',FREEZER);freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
 result=freezer.freeze(BATCH,'historical-four-mask-source-compatible-own-current-parent-plane-append-nomination',[check(q)for q in refs],dict(uids=UIDS,sourceOnly=True,privateCandidate=True,newlyInstalled=0,physicalAccepted=False,currentAcceptance=False,appendedFaces=len(new),rejectedPieces=len(rejected)))
 fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),appendedFaces=len(new),rejectedPieces=len(rejected))),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
 if '--owned'in sys.argv:return owned()
 assert '--nominate-compatible-current-parent-regions-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
 prep=read(PROPOSAL/'actual-nomination-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 claim=reservations.claim('polyu-four-current-regions-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
