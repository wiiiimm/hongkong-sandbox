"""UNEXECUTED saved-array finite/regression stage. No constructor or acceptance."""
from pathlib import Path
from collections import defaultdict, deque
from fractions import Fraction as F
import json, sys, time, uuid, subprocess
import numpy as np
from run import ROOT, HERE, read, save, connect, reservations
from upton_post_nam_current_binding_v1_20261013 import historical_ref
from upton_parent_tin_regression_bookkeeping_v1_20261012 import MODES, sha, triangles, closed_face_scope, finite_record
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from upton_six_basic_preserved_ground_feasibility_draft_v1_20261012 import code_paths

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-v6-saved-actual-union-finite-regression-v2-20261013'
DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH; PROPOSAL=BASE/(BATCH+'-proposal'); LEASE=LOCAL/'reservation.json'
V6=BASE/'government-xl-upton-two-original-complete-mask-current-nam-enclosure-v6-20261013'
MAX=BASE/'government-xl-upton-v6-saved64-actual-max-geometry-bound-validator-v1-20261013'
CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012'
OLD=BASE/'government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012'
REG=BASE/'government-xl-upton-whole-parent-original-tin-regression-v2-20261012'
ORIGINAL=BASE/'government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012/original-full-source-root-context.json.gz'
ARCHIVE=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012/captured-manifest.json'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
GROUND_SHA='f908dd9f49a91e71db53443f95c4d2e7063ff041d3cf554eb08ac09cbc35c236'
DOMAIN=[-2477.5,-37.5,-2267.5,102.5]
OWNED=['landsd/338946:0','landsd/12728:0']; SECONDARY='landsd/12662:0'; NATIVE='landsd/79882:0'; FOREIGN='landsd/254809:0'
FIELDS=('completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition')
def ref(p):
 import hashlib
 return dict(path=str(p.resolve().relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(q): return historical_ref(q,ROOT,ARCHIVE)
def module(p,name):
 import importlib.util
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def inputs():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 replay=read(V6/'actual-production-replay.json.gz'); old=read(OLD/'complete-candidate-clearance.json.gz')
 ground=triangles(np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
 prior_ground=triangles(np.asarray(read(BASE/'government-xl-upton-original-tin-current-ring-join-nomination-v2-20261012/actual-production-replay.json.gz')['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
 assert len(ground)==11603 and sha(ground)==GROUND_SHA and len(prior_ground)==10770 and sha(prior_ground)==old['candidateActualGroundSHA256']
 assert replay['startEndAllInputsVerified']and replay['currentManifestSHA256']==CURRENT and replay['currentExteriorXYZOrderedHashMatched']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 attrs=read(CAP/'whole-domain-current-actors.json.gz'); original={r['uid']:r for r in read(ORIGINAL)['rows']}
 scope=read(V6/'complete-affected-scope.json.gz'); assert scope['completeNativeActors']==6650 and [r['uid']for r in scope['wholeDomainTouchingNativeNominees']]==[NATIVE]and not scope['otherTouchingNativeCompleteActualStreamsUnqualified']
 assert scope['secondaryHeldAsForeign']==SECONDARY and len(scope['affectedBasic'])==52
 reviewed=read(HERE/'local'/MAX.name/'private-upton-v6-geometry-bound-overlap-reviewed.json');bare=json.loads(json.dumps(reviewed));assert bare['nativeMesh'].pop('sourceOverlap')
 assert bare==read(V6/'private-native-terrain-candidate.json.gz')
 outcome=read(MAX/'unchanged-base-parent-validator-outcome.json');assert outcome['passed']and outcome['allFieldsExceptSourceOverlapExactlyEqual']and outcome['metadataOnlyCandidate']==ref(HERE/'local'/MAX.name/'private-upton-v6-geometry-bound-overlap-reviewed.json')
 actors=[];saved={r['uid']:r for r in old['actors']}
 for row in attrs['rows']+attrs['nativeContextRows']:
  uid=row['uid']; ix=np.asarray(row['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
  worlds={mode:triangles(np.asarray(row[k],dtype='<f8').reshape(-1,3)[ix])for mode,k in zip(MODES[1:],FIELDS)}
  if uid in original:
   o=original[uid];worlds['original']=triangles(o['completeOriginalBinary64WorldTriangles']);assert sha(worlds['original'])==o['completeOriginalWorldSHA256']and o['sourceSHA256']==row['sourceSHA256']
  else:
   # Reconstruct this captured two-node native provider-world arithmetic from
   # saved source attributes, then require its independently recorded exact SHA.
   nodes=row['originalNodeMetadata'];proof=row['completeOriginalPOSITIONProof']
   assert uid==NATIVE and len(nodes)==2 and proof['sceneNodesTraversed']==[0,1]and nodes[0]['children']==[1]and nodes[1]['mesh']==0 and len(row['actualRenderMeshes'])==1
   assert all(not any(k in n for k in ['translation','rotation','scale'])for n in nodes)
   mesh=row['actualRenderMeshes'][0];p=np.asarray(mesh['completeOriginalVertexAttribute'],dtype='<f8').reshape(-1,3)
   assert np.array_equal(np.asarray(mesh['completeOriginalIndex'],dtype=np.int64).reshape(-1,3),ix)and len(p)==proof['completeOriginalPositionVertices']
   root=np.asarray(nodes[0]['matrix'],dtype='<f8').reshape(4,4,order='F');child=np.asarray(nodes[1].get('matrix',np.eye(4).reshape(-1,order='F').tolist()),dtype='<f8').reshape(4,4,order='F')
   surveyed=(np.c_[p,np.ones(len(p))]@(np.eye(4)@root@child).T)[:,:3]+np.array([-834500,0,816500])
   worlds['original']=triangles(surveyed[ix]);assert sha(worlds['original'])==proof['worldTrianglesSHA256']and [surveyed.min(0).tolist(),surveyed.max(0).tolist()]==proof['originalWholeSourceBounds']
  assert len(ix)==row['completeOriginalPOSITIONProof']['completeOriginalTriangles']
  for mode in MODES:
   w=worlds[mode];p=next(q for q in saved[uid]['worlds']if q['mode']==mode)
   assert len(w)==p['completeFaces']and sha(w)==p['wholeWorldSHA256']
  actors.append((uid,worlds,saved[uid],row['sourceSHA256']))
 assert [r[0]for r in actors]==OWNED+[SECONDARY,NATIVE]and sum(len(r[1]['original'])for r in actors[:2])==13312 and len(actors[2][1]['original'])==392 and len(actors[3][1]['original'])==616
 # Saved BASIC baseline validation is schema/hash only, not finite replay.
 assert len(attrs['basicContextRows'])==len(old['completeBasicRows'])==1911
 affected={r['uid']:r for r in scope['affectedBasic']};old_basic={r['uid']:r for r in old['completeBasicRows']};selected_count=0
 for row in attrs['basicContextRows']:
  uid=row['uid'];p=np.asarray(row['position'],dtype='<f8').reshape(-1,3);w=triangles(p[np.asarray(row['index'],dtype=np.int64).reshape(-1,3)]);q=old_basic[uid]
  assert len(w)==q['completeFaces']and len(p)==q['completeUnusedPositionVertices']and sha(w)==q['completeScope']['wholeWorldSHA256']
  ids=q['completeScope']['selectedFaceIDs'];assert ids==(affected[uid]['selectedWholeFaceIDs']if uid in affected else[]);selected_count+=len(ids)
  if uid in affected:
   rows=q['findings']['worlds'];assert len(rows)==1 and rows[0]['mode']=='capturedConstructorFloat32World'and rows[0]['wholeWorldSHA256']==sha(w)and rows[0]['candidateCompleteGroundSHA256']==sha(prior_ground)and rows[0]['completeFaces']==len(w)
 assert selected_count==2114 and len(affected)==52
 return pins,replay,ground,prior_ground,old,attrs,scope,actors
def schema_only():
 pins,replay,ground,prior_ground,old,attrs,scope,actors=inputs();native=next(r for r in actors if r[0]==NATIVE)
 return dict(passed=True,caller=ref(Path(__file__)),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),completeNewDrawnGroundFaces=len(ground),completeNewDrawnGroundSHA256=sha(ground),completeOwnedFaces=13312,secondaryForeignFaces=392,retainedNativeFaces=616,nativeOriginalSavedAttributeSHA256=sha(native[1]['original']),nativeLiteralSHA256=sha(native[1]['literal']),nativeOriginalSourceDecode=False,completeBasicRows=len(attrs['basicContextRows']),affectedBasicActors=52,affectedBasicFullFacets=2114,savedBasicBaselineWorldHashAndModeVerified=True,noFiniteContactDBOrLeaseWork=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,replay,ground,prior_ground,old,attrs,scope,actors=inputs();pre=read(PROPOSAL/'schema-preflight.json');assert pre['passed']and pre['caller']==ref(Path(__file__))
 refs=[ref(p)for p in code_paths(Path(__file__))]+pins['inputRefs']+pins['codeRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'schema-preflight.json')]
 preparation=read(PROPOSAL/'actual-readonly-preparation.json');assert preparation['passed']and preparation['caller']==ref(Path(__file__))and preparation['declaredPinsVerifiedBeforeAndAfter']
 refs +=[ref(PROPOSAL/'actual-readonly-preparation.json')]+[r['log']for r in preparation['actualCommands']]+[preparation['literalClosure']]+preparation['literalClosureRefs']
 for q in refs:check(q)
 for record in pins['receipts']:
  receipt=read(check(record['result']));assert receipt['jobId']==record['jobId']
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[record['result']]:check(q);refs.append(q);pulse()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();DOC.mkdir(parents=True);complete=CompleteGround(ground);before=CompleteGround(prior_ground);cache={};mode_cache={};results=[]
 def assess(uid,worlds,saved,role):
  modes=[]
  for mode,w in worlds.items():
   w=triangles(w);baseline=next(r for r in saved['worlds']if r['mode']==mode);sc=closed_face_scope(w,DOMAIN);ids=sc['selectedFaceIDs']
   assert sha(w)==baseline['wholeWorldSHA256']and ids==baseline['selectedFaceIDs']and baseline['candidateCompleteGroundSHA256']==sha(prior_ground)
   key=(sha(w),sha(ground),tuple(ids));mode_reused=key in mode_cache;out=mode_cache.get(key)
   if out is None:
    old_records={r['face']:r for r in baseline['findings']['rows']};assert set(old_records)==set(ids);chunks=[];rows=[];uncovered=[];ordinary=[];regressed=[];reused_count=0;fresh_count=0
    def chunk():
     nonlocal rows
     if not rows:return
     p=DOC/'chunks'/uid.replace('/','-').replace(':','-')/mode/(str(len(chunks)).zfill(5)+'.json.gz');assert not p.exists();tmp=p.with_name(p.name+'.tmp.json.gz')
     save(tmp,dict(uid=uid,mode=mode,wholeWorldSHA256=sha(w),completeNewGroundSHA256=sha(ground),completeOldGroundSHA256=sha(prior_ground),rows=rows));tmp.replace(p);chunks.append(ref(p));rows=[];pulse(True)
    for i in ids:
     face=w[i];selected,binding=complete.select(face.tolist());old_ids,old_binding=before.select(face.tolist());prior=old_records[i]['candidate'];assert prior['sourceFaceSHA256']==sha(face)and prior['completeGroundSHA256']==sha(prior_ground)
     if prior['coarse'] is not None:
      coarse=prior['coarse'];final=prior['paired']or coarse
      assert coarse['allProjectedBoundingCandidateOriginalGroundFacets']==old_ids.tolist()and coarse['sourceFaceSHA256']==sha(face)and coarse['completeCurrentGroundSHA256']==sha(prior_ground)
      assert final['sourceFaceSHA256']==sha(face)and final['completeCurrentGroundSHA256']==sha(prior_ground)
      assert prior['projectionCovered']==final['groundProjectionCovered']and prior['ordinaryBoundProved']==final['existingOrdinaryClearanceBoundProved']and prior['exactLowerM']==final['exactCertifiedLowerClearanceM']
     # Compare complete selected triplets with multiplicity, preserving prior
     # kernel order. Only exact bytes match; signed zero is not normalized.
     queues=defaultdict(deque)
     for j in selected:queues[ground[j].tobytes()].append(int(j))
     mapped=[]
     for j in old_ids:
      k=prior_ground[j].tobytes()
      if not queues[k]:mapped=[];break
      mapped.append(queues[k].popleft())
     equal=len(mapped)==len(old_ids)==len(selected)and not any(queues.values())
     if equal and prior['projectionCovered']and prior['ordinaryBoundProved']:
      assert np.asarray(ground[mapped],dtype='<f8').tobytes()==np.asarray(prior_ground[old_ids],dtype='<f8').tobytes()
      final=dict(projectionCovered=prior['projectionCovered'],ordinaryBoundProved=prior['ordinaryBoundProved'],exactLowerM=prior['exactLowerM'],oldKernelRecordVerbatim=prior,oldCompleteSelection=old_binding,newGroundFaceCorrespondence=mapped,noKernelHashRelabelling=True);reused_count+=1;kind='exact-complete-relevant-tuple-reused'
     else:
      k=(sha(face),sha(ground[selected]));kind='unchanged-existing-finite-kernel'
      if k not in cache:cache[k]=finite_record(face,ground[selected])
      final=cache[k];fresh_count+=1
     if final['ordinaryBoundProved']:assert final['projectionCovered']and F(final['exactLowerM'])>=-F(1,2)
     if not final['projectionCovered']:uncovered.append(i)
     if not final['ordinaryBoundProved']:ordinary.append(i)
     current=old_records[i]['currentSavedVerbatim'];assert current['sourceFaceSHA256']==sha(face)
     if current['ordinaryBoundProved']and not final['ordinaryBoundProved']:regressed.append(i)
     rows.append(dict(face=i,proofKind=kind,completeNewGroundSelection=binding,completeRelevantGroundSHA256=sha(ground[selected]),findings=final,currentBaselineVerbatim=current,noRootSupportRoleAcceptanceCredit=True));pulse()
     if len(rows)==64:chunk();print(json.dumps(dict(uid=uid,mode=mode,processedFaces=min(len(chunks)*64,len(ids)),expectedFaces=len(ids),reused=reused_count,fresh=fresh_count)),flush=True)
    chunk();out=dict(chunks=chunks,completeProcessedFaces=len(ids),exactRelevantProofsReused=reused_count,unchangedFiniteKernelClaims=fresh_count,candidateUncovered=uncovered,candidateOrdinaryUnproved=ordinary,currentClearCandidateUnproved=regressed);mode_cache[key]=out
   modes.append(dict(mode=mode,wholeWorldSHA256=sha(w),completeFaces=len(w),completeScope=sc,findings=out,exactCompleteTupleModeReuse=mode_reused,noStructuralOrRoleCredit=True));pulse(True)
  return dict(uid=uid,role=role,worlds=modes)
 for uid,worlds,saved,source in actors:
  results.append(dict(assess(uid,{m:worlds[m]for m in MODES},saved,'owned-whole-original'if uid in OWNED else'secondary-held-foreign'if uid==SECONDARY else'retained-native-regression'),sourceSHA256=source))
 basics=[];old_basic={r['uid']:r for r in old['completeBasicRows']};affected={r['uid']:r for r in scope['affectedBasic']}
 for r in attrs['basicContextRows']:
  uid=r['uid'];positions=np.asarray(r['position'],dtype='<f8').reshape(-1,3);w=triangles(positions[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)]);sc=closed_face_scope(w,DOMAIN);prior=old_basic[uid]
  assert sc==prior['completeScope']and sc['selectedFaceIDs']==(affected[uid]['selectedWholeFaceIDs']if uid in affected else[])
  q=dict(uid=uid,completeFaces=len(w),completeUnusedPositionVertices=len(positions),completeScope=sc,strictOutsideFacesUseExactCurrentExteriorProof=ref(V6/'actual-production-replay.json.gz'),emptyConstructorReceivesNoCredit=not len(w))
  if uid in affected:q['findings']=assess(uid,{'capturedConstructorFloat32World':w},prior['findings'],'production-constructor-regression-only')
  basics.append(q);pulse()
 assert len(basics)==1911 and len(affected)==52 and sum(len(r['completeScope']['selectedFaceIDs'])for r in basics)==2114
 complete.verify_binding();before.verify_binding()
 save(DOC/'complete-new-union-finite-regression.json.gz',dict(actors=results,completeBasicRows=basics,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),newGroundSHA256=sha(ground),completeNewDrawnFaces=len(ground),whole6650Scope=ref(V6/'complete-affected-scope.json.gz'),v6RetainedCurrentOrdinaryProofReused=ref(V6/'complete-expanded-current-owned-ordinary-compatibility.json.gz'),v6CoverageAndSixGuardsReused=True,allZerosAnd23CrossingsRetained=read(REG/'diagnostic.json.gz')['allHistoricalZeroForeignCrossingRootObligationsRetained'],secondaryReceivesNoSupportCredit=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs += [ref(p)for p in DOC.rglob('*')if p.is_file()];fence();module(FREEZER,'upton_actual_v6_finite_freezer').freeze(BATCH,'saved-actual-new-union-ordinary-finite-and-regression-only',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=OWNED+[SECONDARY,NATIVE],sourceOnly=True,completeOwnedFaces=13312,completeAffectedBasicActors=52,physicalAccepted=False,newlyInstalled=0,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json')))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-saved-actual-union-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
 uids=OWNED+[SECONDARY,NATIVE,FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-saved-v6-union-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
