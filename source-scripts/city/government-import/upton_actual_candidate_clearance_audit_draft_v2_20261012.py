"""UNEXECUTED complete ordinary candidate clearance + nonapproving audit.
No constructor, overlap approval, source change, live or acceptance operation.
"""
from pathlib import Path
from fractions import Fraction as F
import ast,json,sys,time,uuid,subprocess,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from upton_parent_tin_regression_bookkeeping_v1_20261012 import MODES,sha,triangles,closed_face_scope,finite_record
from upton_actual_candidate_clearance_audit_v1_20261012 import candidate_surface,verify_drawn_multiset,measured_projection,reuse_key,compare_candidate
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PROPOSAL=BASE/(BATCH+'-proposal')
NOM=BASE/'government-xl-upton-original-tin-current-ring-join-nomination-v2-20261012'
REG=BASE/'government-xl-upton-whole-parent-original-tin-regression-v2-20261012'
CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012'
HELPER=HERE/'upton_actual_candidate_clearance_audit_v1_20261012.py';TEST=HERE/'test_upton_actual_candidate_clearance_audit_v1_20261012.py';RUNTIME=HERE/'upton_actual_candidate_clearance_audit_runtime_draft_v1_20261012.mjs'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540';UIDS=['landsd/338946:0','landsd/12728:0','landsd/12662:0'];NATIVE='landsd/79882:0';FOREIGN='landsd/254809:0'
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):
 p=ROOT/q['path'];assert ref(p)=={k:q[k]for k in ['path','sha256']},q
 if 'bytes'in q:assert p.stat().st_size==q['bytes']
 return p
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def code_paths():
 folders=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review'];todo=[Path(__file__),FREEZER];seen=set()
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for d in folders:
     q=d/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return sorted(seen)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 v=read(PROPOSAL/'audit-helper-validation.json');assert v['exitCode']==0 and v['passedTests']==13 and v['failedTests']==0 and v['helper']==ref(HELPER)and v['test']==ref(TEST);check(v['log'])
 pre=read(PROPOSAL/'preflight.json');assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['method']==ref(PROPOSAL/'METHOD.md')and pre['runtime']==ref(RUNTIME)
 cl=read(check(pre['actualLiteralClosureValidation']));assert cl['passed']and cl['runtime']==ref(RUNTIME)and cl['schema']=='exact-literal-static-dynamic-resource-closure-v1'and cl['computedImportsRejected']and cl['unsupportedDynamicImports']==0 and cl['startEndHashesVerified'];check(cl['log'])
 refs=[ref(p)for p in code_paths()]+[ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'audit-helper-validation.json'),v['log'],ref(PROPOSAL/'preflight.json'),pre['actualLiteralClosureValidation'],cl['log'],ref(RUNTIME),ref(TEST),ref(NOM/'independent-completed-readback-summary.json')]
 for p,h in cl['inputHashes'].items():refs.append(dict(path=p,sha256=h))
 for folder,jid,resultsha in [(NOM,'0514c963b8c79bae794a1bcd2683730f2af78788245e05434ce1a38f66d72427','d3ef62c5a2534b0381cdbf05c883f6300e536ba2083a86f11dc489f89cf58219'),(REG,'3046002072e7956b8d862a6a0ed14a66055fa962bfa3ccbef9401286910b4899','93579719eb26a37bd28fc6aadf019d305a0940e5f279f4b329c86751fbda439a'),(CAP,'69916bb92558c08c4c5c1838f7c34f963f0e888b7ef14cb489d995ab9bc36727','91d90929b7a8f3694239ba7d5ec97ab5bc1018d52e8d205c08542a820735f120')]:
  receipt=read(folder/'result.json');assert receipt['jobId']==jid and ref(folder/'result.json')['sha256']==resultsha
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();nom=read(NOM/'complete-nominations-before-guards.json.gz');replay=read(NOM/'actual-production-replay.json.gz');patch=read(NOM/'private-native-terrain-candidate.json.gz');prior=read(REG/'diagnostic.json.gz');attrs=read(CAP/'whole-domain-current-actors.json.gz');capture=read(CAP/'input.json.gz');scope=read(NOM/'complete-affected-scope.json.gz')
 assert replay['startEndAllInputsVerified']and replay['currentManifestSHA256']==CURRENT and replay['currentExteriorXYZOrderedHashMatched']and replay['before']['outside']==replay['after']['outside']==8164251 and replay['before']['exteriorOrderedBinary64SHA256']==replay['after']['exteriorOrderedBinary64SHA256']
 old=triangles(np.asarray(replay['before']['closedDomainDrawnTriplets']).reshape(-1,3,3));ground=triangles(np.asarray(replay['after']['closedDomainDrawnTriplets']).reshape(-1,3,3));assert len(old)==9214 and len(ground)==10770 and sha(old)==prior['wholeCurrentDrawnGroundSHA256']
 assert scope['completeNativeActors']==6649 and[x['uid']for x in scope['wholeDomainTouchingNativeNominees']]==[NATIVE]and not scope['otherTouchingNativeCompleteActualStreamsUnqualified']
 assert scope['requiredNineWholeFacets']=={'landsd/214971:0':[30,39,50,54,56,57],'landsd/231778:0':[68,73,76]}
 d=nom['domain'];assert d==capture['domain']==prior['wholeDomain']==[-2477.5,-37.5,-2267.5,102.5];base=read(ROOT/'3d-viewer/city/data/terrain.json');g=base['meta']['georef'];c=patch['coarseCells'];assert c==[457,449,460,451]and[g['bE']+c[0]*g['aE']-834500,816500-(g['bN']+c[1]*g['aN']),g['bE']+c[2]*g['aE']-834500,816500-(g['bN']+c[3]*g['aN'])]==d
 actual=candidate_surface(patch,nom['candidateFaceProvenance']);assert len(actual)==10742;multiset=verify_drawn_multiset(actual,ground)
 DOC.mkdir(parents=True);save(DOC/'input.json.gz',dict(candidate=ref(NOM/'private-native-terrain-candidate.json.gz'),candidateActualGroundSHA256=sha(ground),currentActualGroundSHA256=sha(old),runtimeInputRefs=refs,domain=d,sourceGeometryChanges=0,noApproval=True))
 measurement=measured_projection(patch,nom['candidateFaceProvenance'],d,base);measurement['actualCandidateInDrawnGround']=multiset;save(DOC/'measured-projection-and-parent-edge.json.gz',measurement)
 with(DOC/'actual-native-sampler-ray.log').open('wb')as log:subprocess.run(['node',str(RUNTIME),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 rays=read(DOC/'actual-native-sampler-ray-findings.json.gz');assert rays['startEndAllInputsVerified']
 for p,h in rays['inputHashes'].items():refs.append(dict(path=p,sha256=h))
 for p,h in rays['completeRecursiveProductionModuleClosure']['inputHashes'].items():refs.append(dict(path=p,sha256=h))
 cache={};result=[];savedactors={r['uid']:r for r in prior['actors']};sources={r['uid']:r for r in capture['ownedRows']+capture['nativeRows']}
 def assess(uid,worlds,saved,role):
  output=[];unique={}
  for mode,world in worlds.items():
   world=triangles(world);baseline=next(r for r in saved['worlds']if r['mode']==mode);assert baseline['wholeWorldSHA256']==sha(world)and baseline['wholeCurrentGroundSHA256']==sha(old);ids=baseline['selectedFaceIDs'];sc=closed_face_scope(world,d);assert baseline['fullClosedDomainFaceScope']==sc
   key=(sha(world),sha(ground),tuple(ids));reused=key in unique
   if not reused:
    rows=[];before={r['face']:r for r in baseline['allWholeFacetComparisons']['rows']};assert set(before)==set(ids)
    for i in ids:
     face=world[i];k=reuse_key(face,ground)
     if k not in cache:cache[k]=finite_record(face,ground)
     q=cache[k];a=before[i]['current'];assert a['sourceFaceSHA256']==sha(face)and a['completeGroundSHA256']==sha(old)
     rows.append(dict(face=i,currentSavedVerbatim=a,candidate=q,comparison=compare_candidate(a,q,sc['wholeFaceWithinCapturedDomain'][i])));pulse()
     if len(rows)%64==0:save(LOCAL/'progress'/uid.replace('/','-').replace(':','-')/(mode+'.json.gz'),dict(complete=False,sourceWorldSHA256=sha(world),candidateGroundSHA256=sha(ground),expectedFaces=len(ids),processedFaces=len(rows),rows=rows));print(json.dumps(dict(uid=uid,mode=mode,processedFaces=len(rows),expectedFaces=len(ids))),flush=True)
    unique[key]=dict(rows=rows,candidateUncovered=[r['face']for r in rows if not r['candidate']['projectionCovered']],candidateOrdinaryUnproved=[r['face']for r in rows if not r['candidate']['ordinaryBoundProved']],currentClearCandidateUnproved=[r['face']for r in rows if r['comparison']['currentClearCandidateUnproved']],currentUnprovedCandidateClear=[r['face']for r in rows if r['comparison']['currentUnprovedCandidateClear']])
   output.append(dict(mode=mode,wholeWorldSHA256=sha(world),candidateCompleteGroundSHA256=sha(ground),completeFaces=len(world),selectedFaceIDs=ids,completeScope=sc,findings=unique[key],sameCompleteTupleReuse=reused,priorCompleteBodyCensus=baseline['bodyCensus'],noSupportRoleOrAcceptanceCredit=True));pulse(True)
  return dict(uid=uid,role=role,worlds=output)
 for row in attrs['rows']+attrs['nativeContextRows']:
  uid=row['uid'];s=sources[uid];original=triangles(decode_original_world_triangles(check(dict(path=s['path'],sha256=row['sourceSHA256'])).read_bytes()));proof=row['completeOriginalPOSITIONProof'];assert sha(original)==proof['worldTrianglesSHA256'];ix=np.asarray(row['completeOriginalIndex'],np.int64).reshape(-1,3);assert len(ix)==len(original)==s['entry']['triangles'];worlds={'original':original}
  for mode,k in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
   vertices=np.asarray(row[k],dtype='<f8').reshape(-1,3);assert len(vertices)==proof['completeOriginalPositionVertices'];worlds[mode]=vertices[ix]
  assert all(all(closed_face_scope(w,nom['core'])['wholeFaceWithinCapturedDomain'])for w in worlds.values());result.append(assess(uid,worlds,savedactors[uid],'owned-original'if uid in UIDS else'unchanged-native-regression-only'))
 assert sum(r['worlds'][0]['completeFaces']for r in result[:3])==13704 and result[3]['worlds'][0]['completeFaces']==616
 basic=[];oldbasic={r['uid']:r for r in prior['completeBasicRows']};affected={r['uid']:r for r in scope['affectedBasic']}
 for r in attrs['basicContextRows']:
  uid=r['uid'];v=np.asarray(r['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(r['index'],np.int64).reshape(-1,3);w=v[ix];sc=closed_face_scope(w,d);assert sc==oldbasic[uid]['scope']and sha(w)==oldbasic[uid]['completeWorldSHA256'];q=dict(uid=uid,completeFaces=len(w),completeUnusedPositionVertices=len(v),completeScope=sc,strictOutsideFacetsRetainCurrentExteriorXYZProof=True,emptyConstructorReceivesNoCredit=not len(w))
  if sc['selectedFaceIDs']:
   assert uid in affected and sc['selectedFaceIDs']==affected[uid]['selectedWholeFaceIDs'];q['findings']=assess(uid,{'capturedConstructorFloat32World':w},oldbasic[uid]['affectedComparisons'],'production-constructor-context-only')
  basic.append(q);pulse()
 assert len(basic)==1911 and sum('findings'in r for r in basic)==52 and sum(len(r['completeScope']['selectedFaceIDs'])for r in basic)==2114
 for uid,ids in scope['requiredNineWholeFacets'].items():assert set(ids)<=set(next(r for r in basic if r['uid']==uid)['completeScope']['selectedFaceIDs'])
 seams=[]
 for i,r in enumerate(nom['completeCoreBoundaryNominations']):
  segment=np.asarray([[float(F(v))for v in p]for p in r['packedSourceEdge']],dtype='<f8');proof=verify_contact_segment(segment,ground);seams.append(dict(savedBoundary=i,sourceCandidateFaces=r['sourceCandidateFaces'],actualCandidateGroundProof=proof,fixedBandIsNotExactSeamCertificate=True));pulse()
 validator_path=HERE.parent/'island-detail-integration/native_terrain_validation.py';refs.append(ref(validator_path));failure=None
 try:module(validator_path,'upton_candidate_unchanged_validator').validate_native_mesh(patch,base)
 except AssertionError as e:failure=str(e)
 save(DOC/'complete-candidate-clearance.json.gz',dict(actors=result,completeBasicRows=basic,existingOrdinaryLimitM='-1/2',currentGroundSHA256=sha(old),candidateActualGroundSHA256=sha(ground),completeCandidateDrawnFaces=len(ground),priorZerosAnd23CrossingsRetained=prior['allHistoricalZeroForeignCrossingRootObligationsRetained'],allBodyRoleRootAndPhysicalObligationsRetained=True,allFourWorldsLabelled=True,fullFacetsNeverClipped=True,sourceGeometryChanges=0,liveTerrainChanges=0,physicalAccepted=False,installationApproved=False))
 save(DOC/'complete-core-boundary-fixed-band-findings.json.gz',dict(rows=seams,completeSegments=len(seams),notExactSeamCertificate=True,noGeometryChanges=True))
 save(DOC/'real-validator-outcome.json',dict(passed=failure is None,actualAssertion=failure,unchangedValidator=ref(validator_path),noApprovalWritten=True,noCandidateEdits=True))
 save(DOC/'diagnostic.json.gz',dict(completeCandidateClearance=ref(DOC/'complete-candidate-clearance.json.gz'),measuredProjection=ref(DOC/'measured-projection-and-parent-edge.json.gz'),actualSamplerRays=ref(DOC/'actual-native-sampler-ray-findings.json.gz'),coreBoundaryFindings=ref(DOC/'complete-core-boundary-fixed-band-findings.json.gz'),unchangedValidator=ref(DOC/'real-validator-outcome.json'),candidate=ref(NOM/'private-native-terrain-candidate.json.gz'),noApprovalWritten=True,physicalAccepted=False,installationApproved=False))
 refs+=[ref(p)for p in sorted(DOC.iterdir())if p.is_file()];fence();module(FREEZER,'upton_candidate_clearance_freezer').freeze(BATCH,'private-actual-candidate-ordinary-clearance-measured-overlap-only',[check(q)for q in{(p['path'],p['sha256']):p for p in refs}.values()],dict(uids=UIDS+[NATIVE],currentManifest=capture['currentManifest'],completeOwnedFaces=13704,sourceOnly=True,candidateOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert '--check-private-candidate-only'in sys.argv and not DOC.exists()and not LOCAL.exists();uids=UIDS+[NATIVE,FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-actual-candidate-audit-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
