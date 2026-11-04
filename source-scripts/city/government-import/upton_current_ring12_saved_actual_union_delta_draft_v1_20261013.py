"""Fresh saved-ring12 delta; exact complete relevant tuples only may reuse proofs."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict,deque
import sys,json,time,uuid,subprocess
import numpy as np
import upton_v6_saved_actual_union_finite_regression_draft_v3_20261013 as baseline
import upton_current_ring12_actual_production_capture_draft_v1_20261013 as capture
import upton_scoped_subdivision_saved_actual_union_delta_draft_v1_20261013 as previous_delta
from run import ROOT,HERE,read,save,connect,reservations
ref,check=baseline.ref,baseline.check
sha,triangles,finite_record,closed_face_scope=baseline.sha,baseline.triangles,baseline.finite_record,baseline.closed_face_scope
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-current-ring12-saved-actual-union-delta-v1-20261013'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
GROUND_SHA='49188567c55f7903d96a8a82e246d7fef436d3b9569858eb3eed45944bda7258'
CAP_JOB='8054682423db19952e6f6de614c792245a43a601ae363b3055d0e42100a1f06d'
OLD_JOB='d5ede71c98345b8d3e767d6ac428c29480e20e61b664b8ca01ca8a65577c1e6a'
def inputs():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 _,before,_,_,attrs,scope,actors=previous_delta.inputs() # Latest completed delta: saved array/schema checks, no finite/source decoding.
 previous=read(previous_delta.DOC/'complete-actual-union-finite-delta.json.gz');assert previous['newGroundSHA256']==sha(before)==previous_delta.GROUND_SHA and previous['completeNewDrawnFaces']==11604
 assert previous['same6650WholeScope']==ref(baseline.V6/'complete-affected-scope.json.gz')and previous['secondaryHeldAsForeignReceivesNoSupportCredit']and not previous['physicalAccepted']and not previous['installationApproved']
 check(previous['allZerosAnd23CrossingsRetained'])
 replay=read(capture.DOC/'actual-production-replay.json.gz');ground=triangles(np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
 assert len(ground)==11605 and sha(ground)==GROUND_SHA and replay['startEndAllInputsVerified']and replay['currentExteriorXYZOrderedHashMatched']and replay['currentManifestSHA256']==baseline.CURRENT
 for p,h in replay['inputHashes'].items():check(dict(path=p,sha256=h))
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT
 assert [r['uid']for r in previous['actors']]==baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE]and len(previous['completeBasicRows'])==1911
 for uid,worlds,_,source in actors:
  actor=next(r for r in previous['actors']if r['uid']==uid);assert actor['sourceSHA256']==source
  assert [w['mode']for w in actor['worlds']]==list(baseline.MODES)
  for m,w in worlds.items():
   row=next(r for r in actor['worlds']if r['mode']==m);assert row['wholeWorldSHA256']==sha(w)and row['completeFaces']==len(w)and row['completeScope']==closed_face_scope(w,baseline.DOMAIN)
 assert scope['completeNativeActors']==6650 and len(scope['affectedBasic'])==52 and scope['secondaryHeldAsForeign']==baseline.SECONDARY
 assert not scope['otherTouchingNativeCompleteActualStreamsUnqualified']and [r['uid']for r in scope['wholeDomainTouchingNativeNominees']]==[baseline.NATIVE]
 assert scope['allFacetAndBodyRoleObligationsRemain']and scope['secondaryCurrentFormsMustBeIncludedInFreshForeignPhysicalChecks']
 assert sum(len(worlds['original'])for uid,worlds,_,_ in actors if uid in baseline.OWNED)==13312
 assert len(next(worlds for uid,worlds,_,_ in actors if uid==baseline.SECONDARY)['original'])==392 and len(next(worlds for uid,worlds,_,_ in actors if uid==baseline.NATIVE)['original'])==616
 return pins,ground,before,previous,attrs,scope,actors
def schema_only():
 p,g,b,old,attrs,scope,actors=inputs()
 return dict(passed=True,caller=ref(Path(__file__)),newDrawnFaces=len(g),newGroundSHA256=sha(g),oldDrawnFaces=len(b),oldGroundSHA256=sha(b),completeNativeActorScope=6650,completeOwnedFaces=13312,secondaryForeignFaces=392,native79882Faces=616,completeBasicActors=1911,affectedBasicActors=52,noFiniteKernelOrSelectionReplay=True,noLeaseDBOrSourceDecode=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,ground,before,old,attrs,scope,actors=inputs();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']
 for folder,job in [(capture.DOC,CAP_JOB),(previous_delta.DOC,OLD_JOB)]:
  receipt=read(folder/'result.json');assert receipt['jobId']==job
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',receipt)
  refs+=[ref(folder/'result.json')]+receipt['evidenceRefs']
 for q in refs:check(q);pulse()
 DOC.mkdir(parents=True);complete=baseline.CompleteGround(ground);prior=baseline.CompleteGround(before);cache={};mode_cache={}
 def assess(uid,worlds,saved,role):
  modes=[]
  for mode,w in worlds.items():
   old_mode=next(r for r in saved['worlds']if r['mode']==mode);sc=closed_face_scope(w,baseline.DOMAIN);ids=sc['selectedFaceIDs'];assert old_mode['wholeWorldSHA256']==sha(w)and old_mode['completeScope']==sc
   key=(sha(w),sha(ground),tuple(ids));mode_reused=key in mode_cache;out=mode_cache.get(key)
   if out is None:
    old_rows={}
    for q in old_mode['findings']['chunks']:
     check(q);refs.append(q);chunk=read(check(q));assert chunk['uid']==uid and chunk['wholeWorldSHA256']==sha(w)and chunk['completeNewGroundSHA256']==sha(before)
     for r in chunk['rows']:assert r['face']not in old_rows;old_rows[r['face']]=r
    assert set(old_rows)==set(ids);chunks=[];rows=[];uncovered=[];ordinary=[];regressed=[];reused=0;fresh=0
    def flush():
     nonlocal rows
     if not rows:return
     path=DOC/'chunks'/uid.replace('/','-').replace(':','-')/mode/(str(len(chunks)).zfill(5)+'.json.gz');assert not path.exists();tmp=path.with_name(path.name+'.tmp.json.gz');save(tmp,dict(uid=uid,mode=mode,wholeWorldSHA256=sha(w),completeNewGroundSHA256=sha(ground),completeOldGroundSHA256=sha(before),rows=rows));tmp.replace(path);chunks.append(ref(path));rows=[];pulse(True)
    for face_id in ids:
     face=w[face_id];exact=[[F(v)for v in p]for p in face.tolist()];new_ids,binding=complete.select(exact);old_ids,old_binding=prior.select(exact);saved_row=old_rows[face_id]
     assert saved_row['completeNewGroundSelection']==old_binding and saved_row['completeRelevantGroundSHA256']==sha(before[old_ids])and saved_row['currentBaselineVerbatim']['sourceFaceSHA256']==sha(face)
     queues=defaultdict(deque)
     for j in new_ids:queues[ground[j].tobytes()].append(int(j))
     mapping=[]
     for j in old_ids:
      if not queues[before[j].tobytes()]:mapping=[];break
      mapping.append(queues[before[j].tobytes()].popleft())
     equal=len(mapping)==len(old_ids)==len(new_ids)and not any(queues.values())
     if equal:
      assert ground[mapping].tobytes()==before[old_ids].tobytes();s=saved_row['findings'];final=dict(projectionCovered=s['projectionCovered'],ordinaryBoundProved=s['ordinaryBoundProved'],exactLowerM=s['exactLowerM'],oldKernelRecordVerbatim=s,oldSelectedGroundBinding=old_binding,newGroundFaceCorrespondence=mapping,noOldWholeGroundHashRelabelling=True,unchangedNegativeRetained=not s['ordinaryBoundProved']);kind='exact-complete-selected-source-ground-tuple-reused';reused+=1
     else:
      k=(sha(face),sha(ground[new_ids]));kind='changed-complete-selected-tuple-existing-finite-kernel'
      if k not in cache:cache[k]=finite_record(face,ground[new_ids])
      final=cache[k];fresh+=1
     if final['ordinaryBoundProved']:assert final['projectionCovered']and F(final['exactLowerM'])>=-F(1,2)
     if not final['projectionCovered']:uncovered.append(face_id)
     if not final['ordinaryBoundProved']:ordinary.append(face_id)
     current=saved_row['currentBaselineVerbatim']
     if current['ordinaryBoundProved']and not final['ordinaryBoundProved']:regressed.append(face_id)
     rows.append(dict(face=face_id,proofKind=kind,completeNewGroundSelection=binding,completeRelevantGroundSHA256=sha(ground[new_ids]),findings=final,currentBaselineVerbatim=current,priorCandidateRowVerbatim=saved_row,noRootSupportRoleAcceptanceCredit=True));pulse()
     if len(rows)==64:flush();print(json.dumps(dict(uid=uid,mode=mode,processed=len(chunks)*64,total=len(ids),exactTupleReuse=reused,changedTupleFinite=fresh)),flush=True)
    flush();out=dict(chunks=chunks,completeProcessedFaces=len(ids),exactRelevantProofsReused=reused,changedTupleFiniteClaims=fresh,candidateUncovered=uncovered,candidateOrdinaryUnproved=ordinary,currentClearCandidateUnproved=regressed);mode_cache[key]=out
   modes.append(dict(mode=mode,wholeWorldSHA256=sha(w),completeFaces=len(w),completeScope=sc,findings=out,exactCompleteTupleModeReuse=mode_reused,noStructuralOrRoleCredit=True));pulse(True)
  return dict(uid=uid,role=role,worlds=modes)
 results=[];old_actors={r['uid']:r for r in old['actors']}
 for uid,worlds,_,source in actors:results.append(dict(assess(uid,{m:worlds[m]for m in baseline.MODES},old_actors[uid],'owned-whole-original'if uid in baseline.OWNED else'held-foreign'if uid==baseline.SECONDARY else'retained-native-regression'),sourceSHA256=source))
 basics=[];old_basic={r['uid']:r for r in old['completeBasicRows']};affected={r['uid']:r for r in scope['affectedBasic']}
 for r in attrs['basicContextRows']:
  uid=r['uid'];p=np.asarray(r['position'],dtype='<f8').reshape(-1,3);w=triangles(p[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)]);sc=closed_face_scope(w,baseline.DOMAIN);saved=old_basic[uid];assert sc==saved['completeScope']and sc['selectedFaceIDs']==(affected[uid]['selectedWholeFaceIDs']if uid in affected else[])
  row=dict(uid=uid,completeFaces=len(w),completeUnusedPositionVertices=len(p),completeScope=sc,strictOutsideFacesUseExactCurrentExteriorProof=ref(capture.DOC/'actual-production-replay.json.gz'),emptyConstructorReceivesNoCredit=not len(w))
  if uid in affected:row['findings']=assess(uid,{'capturedConstructorFloat32World':w},saved['findings'],'complete-affected-BASIC-regression')
  basics.append(row);pulse()
 assert len(basics)==1911 and len(affected)==52 and sum(len(r['completeScope']['selectedFaceIDs'])for r in basics)==2114
 complete.verify_binding();prior.verify_binding();save(DOC/'complete-actual-union-finite-delta.json.gz',dict(actors=results,completeBasicRows=basics,newGroundSHA256=sha(ground),completeNewDrawnFaces=len(ground),oldGroundSHA256=sha(before),completeOldDrawnFaces=len(before),previousCompletedDelta=ref(previous_delta.DOC/'result.json'),completeNativeActorScope=scope['completeNativeActors'],allHistoricalZeroAnd23CrossingObligations=scope['allHistoricalZeroAnd23CrossingObligations'],allFacetAndBodyRoleObligationsRemain=scope['allFacetAndBodyRoleObligationsRemain'],secondaryCurrentFormsMustBeIncludedInFreshForeignPhysicalChecks=scope['secondaryCurrentFormsMustBeIncludedInFreshForeignPhysicalChecks'],same6650WholeScope=ref(baseline.V6/'complete-affected-scope.json.gz'),actualSixGuards=ref(capture.DOC/'six-existing-production-protection-guards.json.gz'),rawOverlapValidatorFailure=ref(capture.DOC/'real-validator-outcome.json'),allZerosAnd23CrossingsRetained=old['allZerosAnd23CrossingsRetained'],secondaryHeldAsForeignReceivesNoSupportCredit=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]
 for q in refs:check(q);pulse()
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==baseline.CURRENT;pulse(True)
 baseline.module(baseline.FREEZER,'upton_ring12_finite_delta_freezer').freeze(BATCH,'current-ring12-saved-actual-union-finite-regression-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-saved-current-ring12-actual-union-delta-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 inputs();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
 uids=baseline.OWNED+[baseline.SECONDARY,baseline.NATIVE,baseline.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-ring12-union-delta-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
