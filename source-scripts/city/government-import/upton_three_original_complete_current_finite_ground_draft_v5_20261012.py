"""UNEXECUTED v2 whole-tower sufficient proof + unchanged full podium finite diagnostic.
Reuses reviewed finite/projection/column kernels, fixed ordinary >= -1/2 m.
All source/body/foreign obligations survive; min/max column contact is no root.
"""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from upton_whole_tower_rectangle_global_bound_draft_v1_20261012 import whole_world_proof
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from exact_original_shared_edge_component_census_v2_20261011 import census
from upton_three_original_complete_current_runtime_capture_draft_v4_20261012 import UIDS,MANIFEST_SHA,state,native,ref,module,verified_plan
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-three-original-complete-current-finite-ground-v5-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
CAP=B/'government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012';RUNTIME=HERE/'local'/CAP.name/'runtime-geometry.json.gz';CHUNK=32

def exact_orientation(face):
 p=[[F(float(v))for v in x]for x in face];u=[p[1][k]-p[0][k]for k in range(3)];v=[p[2][k]-p[0][k]for k in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 kind='zero'if not any(n)else'vertical'if n[1]==0 else'horizontal-up'if n[0]==n[2]==0 and n[1]>0 else'horizontal-down'if n[0]==n[2]==0 else'oblique'
 return dict(exactNormal=[str(x)for x in n],exactPlaneClass=kind,originalYRange=[str(min(x[1]for x in p)),str(max(x[1]for x in p))],architectureFunction=None,foundationIntent=None)

def face_proof(face,ground,i,body):
 prior=finite(face,ground);lower=F(prior['exactCertifiedLowerClearanceM']);pairs=[];exact_min=exact_max=None
 # Complete exact min/max finite column refinement whenever contact/burial is not excluded.
 # Every broadphase candidate, including zero/vertical ground facets, is tested unchanged.
 if lower<=0:
  for j in prior['allProjectedBoundingCandidateOriginalGroundFacets']:
   q=column(face,ground[j]);pair=dict(originalGroundFace=int(j),proof=q)
   values=[F(v['exactGapM'])for v in q['allExactBasicFeasibleColumnVertices']]
   if values:
    pair['exactMaximumFiniteColumnGapM']=str(max(values));exact_min=min(values)if exact_min is None else min(exact_min,min(values));exact_max=max(values)if exact_max is None else max(exact_max,max(values))
   pairs.append(pair)
  if prior['groundProjectionCovered']:assert exact_min is not None
  if exact_min is not None:lower=exact_min
 return dict(face=i,originalBody=body,completeFiniteProjectionProof=prior,allRefinedFiniteColumnPairs=pairs,exactLowerM=str(lower),exactMinimumFiniteColumnGapM=str(exact_min)if exact_min is not None else None,exactMaximumFiniteColumnGapM=str(exact_max)if exact_max is not None else None,minimumIsExactFiniteColumnWitness=exact_min is not None,completeProjectionCovered=prior['groundProjectionCovered'],ordinaryFiniteProved=bool(prior['groundProjectionCovered']and lower>=-F(1,2)),strictPositiveFiniteProved=bool(prior['groundProjectionCovered']and lower>0),finiteSameXZZeroGapPairs=[p['originalGroundFace']for p in pairs if p['proof']['exactClosedHorizontalProjectionsMeet']and F(p['proof']['exactMinimumFiniteColumnGapM'])<=0<=F(p['exactMaximumFiniteColumnGapM'])],pointOrFacetContactIsNotWholeEdgeGradeRoot=True)

def verified_rectangle_validation():
 proposal=B/'government-xl-upton-whole-tower-rectangle-global-bound-proposal-v1-20261012';validation=read(proposal/'offline-ten-tests-v1-validation.json')
 assert validation['exitCode']==0 and validation['exactExpectedTests']==10 and validation['expectedPassSummaryPresent']is True
 assert validation['proofCode']==ref(HERE/'upton_whole_tower_rectangle_global_bound_draft_v1_20261012.py')and validation['testCode']==ref(HERE/'test_upton_whole_tower_rectangle_global_bound_draft_v1_20261012.py')
 assert validation['log']==ref(proposal/'offline-ten-tests-v1.log');log=(ROOT/validation['log']['path']).read_text();assert 'Ran 10 tests'in log and log.rstrip().endswith('OK')
 return [ref(proposal/'offline-ten-tests-v1-validation.json'),validation['proofCode'],validation['testCode'],validation['log']]

def tower_face_proof(i,body,certificate):
 assert certificate['allWholeSourceFacetsStrictPositiveFiniteProved']and certificate['completeSourceFacets']==11657
 return dict(face=i,originalBody=body,finiteMethod='complete-world-rectangle-coverage-and-exact-global-Y-bound-v1',sufficientWorldCertificateSHA256=digest(json.dumps(certificate,sort_keys=True,separators=(',',':')).encode()),completeFiniteProjectionProof=None,allRefinedFiniteColumnPairs=[],exactLowerM=certificate['exactConservativeGlobalLowerM'],exactMinimumFiniteColumnGapM=None,exactMaximumFiniteColumnGapM=None,minimumIsExactFiniteColumnWitness=False,completeProjectionCovered=True,ordinaryFiniteProved=True,strictPositiveFiniteProved=True,finiteSameXZZeroGapPairs=[],pointOrFacetContactIsNotWholeEdgeGradeRoot=True)

def main():
 validation_refs=verified_rectangle_validation()
 parser=argparse.ArgumentParser();parser.add_argument('--expected-fresh-capture-result-sha',required=True);parser.add_argument('--prior-v4-stop-audit',required=True);parser.add_argument('--expected-prior-v4-stop-sha',required=True);parser.add_argument('--owned',action='store_true');parser.add_argument('--prior-stop-audit',required=True);parser.add_argument('--expected-prior-stop-sha',required=True);args=parser.parse_args();assert args.expected_fresh_capture_result_sha=='a460d9f7ba768dec6b32d7d8a845c3c6b8775ade98c4476e3e522b3810ec55c5'
 auditpath=ROOT/args.prior_stop_audit;assert ref(auditpath)['sha256']==args.expected_prior_stop_sha;prior_audit=read(auditpath)
 assert prior_audit['priorWorkersStopped']is True and prior_audit['priorLeaseReleased']is True and prior_audit['agentInitiatedMethodSwitch']is True
 assert prior_audit['sourceGeometryChanges']==prior_audit['terrainGeometryChanges']==0 and prior_audit['physicalAccepted']is False
 assert prior_audit['priorProducer']==dict(path=str((HERE/'upton_three_original_complete_current_finite_ground_draft_v1_20261012.py').relative_to(ROOT)),sha256='388454c3bccbbfc0e16bf2688f57661544242143a255875713fe0eecc9862e88')
 assert prior_audit['completedPartialChunksImmutable']is True and prior_audit['allCompletedChunkRefs']
 for e in prior_audit['allCompletedChunkRefs']:assert ref(ROOT/e['path'])==e
 validation_refs.append(ref(auditpath))
 v4auditpath=ROOT/args.prior_v4_stop_audit;assert ref(v4auditpath)['sha256']==args.expected_prior_v4_stop_sha;v4audit=read(v4auditpath)
 assert v4audit['priorWorkersStopped']is True and v4audit['priorLeaseReleased']is True and v4audit['agentInitiatedMethodSwitch']is True
 assert v4audit['sourceGeometryChanges']==v4audit['terrainGeometryChanges']==0 and v4audit['physicalAccepted']is False
 assert v4audit['priorProducer']==dict(path=str((HERE/'upton_three_original_complete_current_finite_ground_draft_v4_20261012.py').relative_to(ROOT)),sha256='4a8a6c8da6c2ff79a196cd4b85805654bc483508d961eaa8d0b75bea63bf757a')
 assert v4audit['completedPartialChunksImmutable']is True and v4audit['allCompletedChunkRefs']
 for e in v4audit['allCompletedChunkRefs']:assert ref(ROOT/e['path'])==e
 validation_refs.append(ref(v4auditpath))
 if not args.owned:
  assert not(DOC/'diagnostic.json.gz').exists()
  claim=reservations.claim('upton-three-original-finite-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned','--prior-stop-audit',args.prior_stop_audit,'--expected-prior-stop-sha',args.expected_prior_stop_sha,'--expected-fresh-capture-result-sha',args.expected_fresh_capture_result_sha,'--prior-v4-stop-audit',args.prior_v4_stop_audit,'--expected-prior-v4-stop-sha',args.expected_prior_v4_stop_sha],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not(DOC/'diagnostic.json.gz').exists()
 assert ref(CAP/'result.json')['sha256']==args.expected_fresh_capture_result_sha;receipt=read(CAP/'result.json');assert receipt['batch']==CAP.name and receipt['jobId']=='4af6addb43b6b94fd2e5e61c868fbd62c84d06a365dc2e19b79d6856ce054502'and receipt['sourceOnly']and not receipt['physicalAccepted']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 scope=read(CAP/'capture-scope.json');assert scope['completeFaces']==13704 and scope['expectedNativeCount']==6649 and scope['currentManifest']['sha256']==MANIFEST_SHA and scope['preservedOriginalProperCrossings']==23
 expected={r['uid']:r for r in verified_plan()['actors']};selections=read(CAP/'selection.json.gz')['rows'];before=read(CAP/'protected-state-before.json');native_before=read(CAP/'native-source-state-before.json')['rows']
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','upton_finite_numeric_closure');paths=set();walker.local_imports(Path(__file__),paths)
 freezer=HERE/'upton_three_original_freeze_complete_current_finite_ground_draft_v5_20261012.py';walker.local_imports(freezer,paths)
 code_refs=[ref(p)for p in sorted(paths)];pins=scope['inputHashes'];manifest=ROOT/'3d-viewer/city/data/manifest.json'
 def fence():
  assert ref(manifest)==scope['currentManifest']and reservations.owns(lease)
  for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
  for e in receipt['evidenceRefs']+code_refs+validation_refs:assert ref(ROOT/e['path'])==e
  assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and json.loads(json.dumps(native(selections),default=str))==native_before
 fence();actual=read(CAP/'actual-render-geometry.json.gz');runtime=read(RUNTIME);assert [r['uid']for r in selections]==[r['uid']for r in actual['rows']]==[r['uid']for r in runtime['rows']]==UIDS
 actors=[];checkpoint_refs=[]
 for selection,attrs,rt,g in zip(selections,actual['rows'],runtime['rows'],scope['completeGroundByActor']):
  uid=selection['uid'];e=expected[uid];sourcepath=ROOT/selection['candidate']['path'];assert ref(sourcepath)['sha256']==e['sourceSHA256'];original=decode_original_world_triangles(sourcepath.read_bytes());assert original.shape==(e['completeFaces'],3,3)and digest(original.astype('<f8').tobytes())==e['wholeWorldSHA256']
  topology=census(original,list(range(len(original))));assert len(topology['sharedEdgeConnectedComponents'])==e['genuineBodies']and len(topology['exactNonrenderingOriginalFaces'])==e['zeroFaces'];labels={i:b for b,fs in enumerate(topology['sharedEdgeConnectedComponents'])for i in fs};assert len(labels)+e['zeroFaces']==len(original)
  orientation=[exact_orientation(f)for f in original];ground=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);gh=digest(ground.tobytes());assert len(ground)==g['completeActualGroundFaces']and gh==g['completeActualGroundSHA256'];index=np.asarray(attrs['completeOriginalIndex'],dtype=int).reshape(-1,3);assert rt['index']==attrs['completeOriginalIndex']and index.shape==(len(original),3)
  streams={'original':original}
  for name,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:streams[name]=np.asarray(attrs[key],dtype='<f8').reshape(-1,3)[index]
  proofs={};bindings={};tower_certificates={}
  if uid==UIDS[0]:
   packed=packed_world_bounds(sourcepath.read_bytes());assert packed['worldTrianglesSHA256']==e['wholeWorldSHA256']and packed['allOriginalPositionVerticesAccounted']
  for name,source in streams.items():
   assert source.shape==original.shape and np.isfinite(source).all();sh=digest(source.tobytes());bindings[name]=dict(completeFaces=len(source),wholeWorldSHA256=sh,wholeGroundSHA256=gh,proofTupleSHA256=digest((sh+gh).encode()))
   certificate=None
   if uid==UIDS[0]:
    if name=='original':bounds=packed['originalWholeSourceBounds']
    else:
     key={'literal':'completeLiteralWorldPosition','explicitLeftF32':'completeExplicitLeftAssociatedFloat32WorldPosition','explicitBalancedF32':'completeExplicitBalancedFloat32WorldPosition'}[name];vertices=np.asarray(attrs[key],dtype='<f8').reshape(-1,3);assert len(vertices)==packed['completeOriginalPositionVertices'];bounds=[vertices.min(0).tolist(),vertices.max(0).tolist()]
    certificate=whole_world_proof(source,ground,bounds);assert certificate['allWholeSourceFacetsStrictPositiveFiniteProved'],'Whole-tower sufficient proof failed; retain diagnostic and reviewed per-face route, no changed retry';tower_certificates[name]=certificate
   if sh in proofs:continue
   rows=[]
   chunk_span=len(source)if certificate is not None else CHUNK
   for start in range(0,len(source),chunk_span):
    stop=min(start+chunk_span,len(source));path=LOCAL/'chunks'/uid.replace('/','-').replace(':','-')/sh/f'{start:05d}-{stop:05d}.json.gz';contract=dict(uid=uid,sourceWorldSHA256=sh,groundSHA256=gh,firstFace=start,exclusiveLastFace=stop,codeRefs=code_refs,ordinaryThresholdM='-1/2')
    fence()
    if path.exists():chunk=read(path);assert chunk['contract']==contract
    else:
     chunk=dict(contract=contract,rows=[tower_face_proof(i,labels.get(i),certificate)if certificate is not None else face_proof(source[i],ground,i,labels.get(i))for i in range(start,stop)]);temp=path.with_name(path.name+'.pending.json.gz');save(temp,chunk);assert read(temp)==chunk;temp.replace(path)
    assert [r['face']for r in chunk['rows']]==list(range(start,stop));rows.extend(chunk['rows']);checkpoint_refs.append(ref(path));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(uid=uid,stream=name,completeFaces=stop,expectedFaces=len(source))),flush=True)
   assert len(rows)==len(source);proofs[sh]=dict(completeFaces=len(rows),allWholeFacetProofs=rows,ordinaryFailingFaces=[r['face']for r in rows if not r['ordinaryFiniteProved']],coverageFailingFaces=[r['face']for r in rows if not r['completeProjectionCovered']],strictUncertifiedFaces=[r['face']for r in rows if not r['strictPositiveFiniteProved']],minimumCertifiedOrExactLowerM=str(min(F(r['exactLowerM'])for r in rows)),allOrdinaryFiniteProved=all(r['ordinaryFiniteProved']for r in rows))
  assert set(bindings)=={'original','literal','explicitLeftF32','explicitBalancedF32'}
  actors.append(dict(uid=uid,sourceSHA256=e['sourceSHA256'],completeGroundFaces=len(ground),completeGroundSHA256=gh,wholeOriginalUnusedPOSITIONProof=packed if uid==UIDS[0]else None,wholeTowerSufficientProofByNamedWorld=tower_certificates,originalBodyCensus=topology,completeOriginalPlaneAttribution=orientation,allFourStreamBindings=bindings,distinctCompleteFiniteProofs=proofs,sourceBodyRolesQualified=False,gradeRootProved=False,wholeEdgeCapPathsQualified=False))
 fence();assert sum(expected[u]['completeFaces']for u in UIDS)==13704 and sum(expected[u]['genuineBodies']for u in UIDS)==749 and sum(expected[u]['zeroFaces']for u in UIDS)==17
 refs=code_refs+validation_refs+[ref(CAP/n)for n in ['result.json','capture-scope.json','selection.json.gz','actual-render-geometry.json.gz','original-full-source-root-context.json.gz','review.json','native-source-state-before.json','protected-state-before.json']]+[ref(RUNTIME)]+checkpoint_refs
 save(DOC/'diagnostic.json.gz',dict(uids=UIDS,sourceOnly=True,currentManifest=scope['currentManifest'],currentNativeCount=6649,completeFaces=13704,genuineBodyObligations=749,zeroFaceObligations=17,ordinaryThresholdM='-1/2',actors=actors,all23ProperSourceCrossingsRetained=True,priorV1MethodSwitchAudit=ref(auditpath),priorV4MethodSwitchAudit=ref(v4auditpath),towerAtomicChunkSpan='complete world, unchanged certificate-bound rows',priorChunksArePreservedAuditNotAliasedV2NumericalProof=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,foreignHoldsDischarged=False,gradeRootProved=False,wholeEdgeCapPathsQualified=False,rawCaptureAndHistoricalObligations=ref(CAP/'review.json'),sourceBodyFunctionAndFoundationIntentUnknown=True,exactWholeWorldAndGroundReuseOnly=True,evidenceRefs=refs))
 subprocess.run([sys.executable,str(freezer),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
 print(json.dumps(dict(batch=BATCH,completeFaces=13704,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
