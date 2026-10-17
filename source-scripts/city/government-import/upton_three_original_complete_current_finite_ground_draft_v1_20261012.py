"""UNEXECUTED complete four-stream finite current-ground diagnostic; no acceptance.
Reuses reviewed finite/projection/column kernels, fixed ordinary >= -1/2 m.
All source/body/foreign obligations survive; min/max column contact is no root.
"""
import json,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from exact_original_shared_edge_component_census_v2_20261011 import census
from upton_three_original_complete_current_runtime_capture_draft_v2_20261012 import UIDS,MANIFEST_SHA,state,native,ref,module,verified_plan
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-three-original-complete-current-finite-ground-v1-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
CAP=B/'government-xl-upton-three-original-complete-current-runtime-capture-v2-20261012';RUNTIME=HERE/'local'/CAP.name/'runtime-geometry.json.gz';CHUNK=32

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

def main():
 if '--owned'not in sys.argv:
  assert not(DOC/'diagnostic.json.gz').exists()
  claim=reservations.claim('upton-three-original-finite-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not(DOC/'diagnostic.json.gz').exists()
 receipt=read(CAP/'result.json');assert receipt['jobId']=='9ce5921b5373fd94334b8d5236fae4149836e7086cf31357ace1b44c77a28154'and receipt['sourceOnly']and not receipt['physicalAccepted']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 scope=read(CAP/'capture-scope.json');assert scope['completeFaces']==13704 and scope['expectedNativeCount']==6649 and scope['currentManifest']['sha256']==MANIFEST_SHA and scope['preservedOriginalProperCrossings']==23
 expected={r['uid']:r for r in verified_plan()['actors']};selections=read(CAP/'selection.json.gz')['rows'];before=read(CAP/'protected-state-before.json');native_before=read(CAP/'native-source-state-before.json')['rows']
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','upton_finite_numeric_closure');paths=set();walker.local_imports(Path(__file__),paths)
 freezer=HERE/'upton_three_original_freeze_complete_current_finite_ground_draft_v1_20261012.py';walker.local_imports(freezer,paths)
 code_refs=[ref(p)for p in sorted(paths)];pins=scope['inputHashes'];manifest=ROOT/'3d-viewer/city/data/manifest.json'
 def fence():
  assert ref(manifest)==scope['currentManifest']and reservations.owns(lease)
  for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
  for e in receipt['evidenceRefs']+code_refs:assert ref(ROOT/e['path'])==e
  assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and json.loads(json.dumps(native(selections),default=str))==native_before
 fence();actual=read(CAP/'actual-render-geometry.json.gz');runtime=read(RUNTIME);assert [r['uid']for r in selections]==[r['uid']for r in actual['rows']]==[r['uid']for r in runtime['rows']]==UIDS
 actors=[];checkpoint_refs=[]
 for selection,attrs,rt,g in zip(selections,actual['rows'],runtime['rows'],scope['completeGroundByActor']):
  uid=selection['uid'];e=expected[uid];sourcepath=ROOT/selection['candidate']['path'];assert ref(sourcepath)['sha256']==e['sourceSHA256'];original=decode_original_world_triangles(sourcepath.read_bytes());assert original.shape==(e['completeFaces'],3,3)and digest(original.astype('<f8').tobytes())==e['wholeWorldSHA256']
  topology=census(original,list(range(len(original))));assert len(topology['sharedEdgeConnectedComponents'])==e['genuineBodies']and len(topology['exactNonrenderingOriginalFaces'])==e['zeroFaces'];labels={i:b for b,fs in enumerate(topology['sharedEdgeConnectedComponents'])for i in fs};assert len(labels)+e['zeroFaces']==len(original)
  orientation=[exact_orientation(f)for f in original];ground=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);gh=digest(ground.tobytes());assert len(ground)==g['completeActualGroundFaces']and gh==g['completeActualGroundSHA256'];index=np.asarray(attrs['completeOriginalIndex'],dtype=int).reshape(-1,3);assert rt['index']==attrs['completeOriginalIndex']and index.shape==(len(original),3)
  streams={'original':original}
  for name,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:streams[name]=np.asarray(attrs[key],dtype='<f8').reshape(-1,3)[index]
  proofs={};bindings={}
  for name,source in streams.items():
   assert source.shape==original.shape and np.isfinite(source).all();sh=digest(source.tobytes());bindings[name]=dict(completeFaces=len(source),wholeWorldSHA256=sh,wholeGroundSHA256=gh,proofTupleSHA256=digest((sh+gh).encode()))
   if sh in proofs:continue
   rows=[]
   for start in range(0,len(source),CHUNK):
    stop=min(start+CHUNK,len(source));path=LOCAL/'chunks'/uid.replace('/','-').replace(':','-')/sh/f'{start:05d}-{stop:05d}.json.gz';contract=dict(uid=uid,sourceWorldSHA256=sh,groundSHA256=gh,firstFace=start,exclusiveLastFace=stop,codeRefs=code_refs,ordinaryThresholdM='-1/2')
    fence()
    if path.exists():chunk=read(path);assert chunk['contract']==contract
    else:
     chunk=dict(contract=contract,rows=[face_proof(source[i],ground,i,labels.get(i))for i in range(start,stop)]);temp=path.with_name(path.name+'.pending.json.gz');save(temp,chunk);assert read(temp)==chunk;temp.replace(path)
    assert [r['face']for r in chunk['rows']]==list(range(start,stop));rows.extend(chunk['rows']);checkpoint_refs.append(ref(path));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(uid=uid,stream=name,completeFaces=stop,expectedFaces=len(source))),flush=True)
   assert len(rows)==len(source);proofs[sh]=dict(completeFaces=len(rows),allWholeFacetProofs=rows,ordinaryFailingFaces=[r['face']for r in rows if not r['ordinaryFiniteProved']],coverageFailingFaces=[r['face']for r in rows if not r['completeProjectionCovered']],strictUncertifiedFaces=[r['face']for r in rows if not r['strictPositiveFiniteProved']],minimumCertifiedOrExactLowerM=str(min(F(r['exactLowerM'])for r in rows)),allOrdinaryFiniteProved=all(r['ordinaryFiniteProved']for r in rows))
  assert set(bindings)=={'original','literal','explicitLeftF32','explicitBalancedF32'}
  actors.append(dict(uid=uid,sourceSHA256=e['sourceSHA256'],completeGroundFaces=len(ground),completeGroundSHA256=gh,originalBodyCensus=topology,completeOriginalPlaneAttribution=orientation,allFourStreamBindings=bindings,distinctCompleteFiniteProofs=proofs,sourceBodyRolesQualified=False,gradeRootProved=False,wholeEdgeCapPathsQualified=False))
 fence();assert sum(expected[u]['completeFaces']for u in UIDS)==13704 and sum(expected[u]['genuineBodies']for u in UIDS)==749 and sum(expected[u]['zeroFaces']for u in UIDS)==17
 refs=code_refs+[ref(CAP/n)for n in ['result.json','capture-scope.json','selection.json.gz','actual-render-geometry.json.gz','original-full-source-root-context.json.gz','review.json','native-source-state-before.json','protected-state-before.json']]+[ref(RUNTIME)]+checkpoint_refs
 save(DOC/'diagnostic.json.gz',dict(uids=UIDS,sourceOnly=True,currentManifest=scope['currentManifest'],currentNativeCount=6649,completeFaces=13704,genuineBodyObligations=749,zeroFaceObligations=17,ordinaryThresholdM='-1/2',actors=actors,all23ProperSourceCrossingsRetained=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,foreignHoldsDischarged=False,gradeRootProved=False,wholeEdgeCapPathsQualified=False,rawCaptureAndHistoricalObligations=ref(CAP/'review.json'),sourceBodyFunctionAndFoundationIntentUnknown=True,exactWholeWorldAndGroundReuseOnly=True,evidenceRefs=refs))
 subprocess.run([sys.executable,str(freezer),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
 print(json.dumps(dict(batch=BATCH,completeFaces=13704,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
