"""DRAFT ONLY. Complete original/four-world finite ground diagnostic; no acceptance."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from west_wing26195_complete_finite_face_draft_v1_20261012 import CompleteGround,face_proof
from west_wing26195_complete_current_runtime_capture_draft_v2_20261012 import UID,SOURCE_SHA,FACES,MANIFEST_SHA,ref,module,state
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing26195-complete-current-finite-ground-v2-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
CAP=B/'government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012';RUNTIME=HERE/'local'/CAP.name/'runtime-geometry.json.gz';PROPOSAL=B/'government-xl-west-wing26195-complete-finite-ground-proposal-v2-20261012';FREEZER=HERE/'west_wing26195_freeze_complete_current_finite_ground_draft_v2_20261012.py';CHUNK=256
CAP_SHA='f0d258f68002b03a010e6d3f8e99f8c18d6e5e6aff6a826806e379a619fb66bb';CAP_JOB='144339ecb468a2c392791526d6f8a4decaa901f1f159f9ad383311510faa7d79'
WORLD_SHA='32969c0eb6a4ea9d4fbfab447ad4e374809399b88ecf82fd52534a1d2d1c712b';GROUND_SHA='6b30dc7bb26c7f9690dac144a743c7657b0124c391fc90d1a1dcd1381c144d6a'
NAMES={'original','literal','explicitLeftF32','explicitBalancedF32'}
def exact_orientation(face):
 p=[[F(float(v))for v in x]for x in face];u=[p[1][k]-p[0][k]for k in range(3)];v=[p[2][k]-p[0][k]for k in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 kind='zero'if not any(n)else'vertical'if n[1]==0 else'horizontal-up'if n[0]==n[2]==0 and n[1]>0 else'horizontal-down'if n[0]==n[2]==0 else'oblique'
 return dict(exactPlaneClass=kind,exactNormal=list(map(str,n)),originalYRange=[str(min(x[1]for x in p)),str(max(x[1]for x in p))],architectureFunction=None,foundationIntent=None)
def validation_refs():
 v=read(PROPOSAL/'no-worker-validation.json');assert v['exactTests']==8 and v['testExitCode']==0 and v['noDBQueries']and v['noReservations']and v['noFullDiagnosticExecution']
 for e in v['codeRefs']+[v['testLog'],v['boundedBenchmark']]:assert ref(ROOT/e['path'])==e
 assert 'Ran 8 tests'in(ROOT/v['testLog']['path']).read_text()and(ROOT/v['testLog']['path']).read_text().rstrip().endswith('OK')
 assert v['codeRefs']==[ref(HERE/n)for n in v['orderedCodeFilenames']];return [ref(PROPOSAL/'no-worker-validation.json')]+v['codeRefs']+[v['testLog'],v['boundedBenchmark']]
def load_inputs():
 assert ref(CAP/'result.json')['sha256']==CAP_SHA;receipt=read(CAP/'result.json');assert receipt['jobId']==CAP_JOB and receipt['batch']==CAP.name and receipt['sourceOnly']and not receipt['physicalAccepted']
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 scope=read(CAP/'capture-scope.json');assert scope['currentManifest']['sha256']==MANIFEST_SHA and scope['nativeCount']==6649 and scope['completeFaces']==FACES and scope['completeActualGroundFaces']==3240 and scope['completeActualGroundSHA256']==GROUND_SHA and scope['completeOriginalWorldSHA256']==WORLD_SHA and scope['startEndAllInputsVerified']and scope['existingInstalledEntryPreserved']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
 for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h,path
 selection=read(CAP/'selection.json.gz')['rows'];attrs=read(CAP/'actual-render-geometry.json.gz')['rows'];runtime=read(RUNTIME)['rows'];assert len(selection)==len(attrs)==len(runtime)==1 and selection[0]['uid']==attrs[0]['uid']==runtime[0]['uid']==UID
 source=ROOT/selection[0]['candidate']['path'];assert ref(source)['sha256']==SOURCE_SHA;t=decode_original_world_triangles(source.read_bytes()).astype('<f8');assert t.shape==(FACES,3,3)and digest(t.tobytes())==WORLD_SHA
 a=attrs[0];rt=runtime[0];index=np.asarray(a['completeOriginalIndex'],int).reshape(-1,3);assert rt['index']==a['completeOriginalIndex']and index.shape==(FACES,3)and a['loadedGroupScale']==[1,1,1]
 ground=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert len(ground)==3240 and digest(ground.tobytes())==GROUND_SHA
 streams={'original':t};unused={}
 for name,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  p=np.asarray(a[key],dtype='<f8').reshape(-1,3);assert np.isfinite(p).all();streams[name]=p[index];unused[name]=dict(completePositionCount=len(p),completeUnusedPositionSHA256=digest(p.tobytes()),completeUnusedPositionBounds=[p.min(0).tolist(),p.max(0).tolist()])
 assert set(streams)==NAMES and all(s.shape==t.shape and np.isfinite(s).all()for s in streams.values())
 return receipt,scope,selection[0],streams,ground,unused

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');a=parser.parse_args();valid=validation_refs();receipt,scope,selection,streams,ground,unused=load_inputs();before=read(CAP/'protected-state-before.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(CAP_JOB,)).fetchone()==('complete',receipt)
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']
 if not a.owned:
  assert not(DOC/'diagnostic.json.gz').exists();claim=reservations.claim('westwing-full-finite-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not(DOC/'diagnostic.json.gz').exists();walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_finite_closure');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(FREEZER,paths);codes=[ref(p)for p in sorted(paths)]
 def fence(full=False):
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h,path
  for e in codes+valid+(receipt['evidenceRefs']if full else []):assert ref(ROOT/e['path'])==e
  assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']
 fence(True);original=streams['original'];topology=census(original,list(range(FACES)));labels={i:b for b,fs in enumerate(topology['sharedEdgeConnectedComponents'])for i in fs};zeros=topology['exactNonrenderingOriginalFaces'];assert sorted(list(labels)+zeros)==list(range(FACES));orientation=[exact_orientation(f)for f in original];assert [i for i,r in enumerate(orientation)if r['exactPlaneClass']=='zero']==zeros
 complete=CompleteGround(ground);proofs={};bindings={};chunks=[]
 for name,source in streams.items():
  sh=digest(source.tobytes());key=digest((sh+GROUND_SHA).encode());bindings[name]=dict(completeFaces=FACES,wholeWorldSHA256=sh,wholeGroundSHA256=GROUND_SHA,proofTupleSHA256=key)
  if key in proofs:continue
  rows=[]
  for start in range(0,FACES,CHUNK):
   stop=min(start+CHUNK,FACES);path=LOCAL/'chunks'/key/f'{start:05d}-{stop:05d}.json.gz';contract=dict(uid=UID,sourceSHA256=SOURCE_SHA,worldSHA256=sh,groundSHA256=GROUND_SHA,completeGroundFaces=3240,firstFace=start,exclusiveLastFace=stop,codeRefs=codes,ordinaryThresholdM='-1/2');fence()
   if path.exists():chunk=read(path);assert chunk['contract']==contract
   else:
    chunk=dict(contract=contract,rows=[face_proof(source[i],complete,i,labels.get(i))for i in range(start,stop)]);temp=path.with_name(path.name+'.pending.json.gz');save(temp,chunk);assert read(temp)==chunk;temp.replace(path)
   assert [r['face']for r in chunk['rows']]==list(range(start,stop));rows.extend(chunk['rows']);chunks.append(ref(path));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(stream=name,completeFaces=stop,expectedFaces=FACES)),flush=True)
  assert len(rows)==FACES;lower=[F(r['exactLowerM'])for r in rows if r['exactLowerM']is not None];proofs[key]=dict(completeFaces=FACES,allWholeFacetProofs=rows,ordinaryFailingFaces=[r['face']for r in rows if not r['ordinaryFiniteProved']],coverageFailingFaces=[r['face']for r in rows if not r['completeProjectionCovered']],strictUncertifiedFaces=[r['face']for r in rows if not r['strictPositiveFiniteProved']],minimumCertifiedOrExactLowerM=str(min(lower))if lower else None,allOrdinaryFiniteProved=all(r['ordinaryFiniteProved']for r in rows))
 complete.verify_binding();fence(True);assert set(bindings)==NAMES
 refs=codes+valid+chunks+[ref(CAP/n)for n in ['result.json','capture-scope.json','selection.json.gz','actual-render-geometry.json.gz','original-full-source-root-context.json.gz','protected-state-before.json','metrics.json']]+[ref(RUNTIME)]
 save(DOC/'diagnostic.json.gz',dict(uid=UID,sourceOnly=True,currentManifest=scope['currentManifest'],currentNativeCount=6649,completeFaces=FACES,completeGroundFaces=3240,completeGroundSHA256=GROUND_SHA,originalBodyCensus=topology,genuineBodyObligations=len(topology['sharedEdgeConnectedComponents']),zeroFaceObligations=len(zeros),completeOriginalPlaneAttribution=orientation,completeActualUnusedPositionBindings=unused,allFourStreamBindings=bindings,distinctCompleteFiniteProofs=proofs,ordinaryThresholdM='-1/2',legacyInstalledDeliveryPreserved=True,legacyAcceptanceGapRetained=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceBodyRolesQualified=False,gradeRootProved=False,wholeEdgeCapPathsQualified=False,foreignHoldsDischarged=False,currentAllNativePhysicalProved=False,exactWholeWorldAndGroundReuseOnly=True,evidenceRefs=refs))
 subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
