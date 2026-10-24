"""Draft complete current finite proof; saved source arrays only, no contact/decode replay."""
import argparse,json,subprocess,sys,uuid,numpy as np
from pathlib import Path
from fractions import Fraction as F
from run import ROOT,HERE,read,save,digest,connect,reservations
import citywalk134332_current_ground_only_supervised_draft_v1_20261013 as G
from west_wing26195_complete_finite_face_draft_v1_20261012 import CompleteGround,face_proof
BATCH='government-xl-citywalk134332-current-complete-finite-ground-v1-20261013';D=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';P=ROOT/'docs/astra-city/government-import/government-xl-citywalk134332-current-complete-finite-ground-proposal-v1-20261013';FREEZER=HERE/'citywalk134332_freeze_current_complete_finite_ground_draft_v1_20261013.py';CHUNK=256
FACES=41277;BODIES=193;UID='landsd/134332:0';GROUND_JOB='f3099a3a146f1012bc4583eb3607ac0d8b5df167dbca12af273cca189a7a1b80';GROUND_RESULT_SHA='fdaa0220288f879a152325efa630d1f3918bb3f6223bc57cc54e36c19db7e4e5';GROUND_SHA='5f944fdfaf5f2de0c6782f95488702c4648ea59a0e04d799ac5733fe67b02349'
def ref(p):return G.Q.ref(p)
def inputs(a):
 pins=read(P/'executable-pins.json')['refs']
 for e in pins:assert ref(ROOT/e['path'])==e
 scope=G.inputs(a);receipt=read(G.D/'result.json');assert ref(G.D/'result.json')['sha256']==GROUND_RESULT_SHA and receipt['jobId']==GROUND_JOB
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(GROUND_JOB,)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 d=read(G.D/'complete-current-drawn-ground.json.gz');assert d['completeRegionalGroundFaces']==4215 and d['completeSourceFaces']==FACES and d['completeOriginalBodies']==BODIES and d['startEndInputsVerified'];assert d['sourceOnly']and not d['currentAcceptance']and not d['physicalAccepted']and not d['installationApproved']
 for p,h in d['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 plan=read(G.Q.P/'ground-capture-plan.json');attrs=read(ROOT/plan['capture']['path']);r=attrs['rows'][0];idx=np.asarray(r['completeOriginalIndex'],int).reshape(-1,3);assert idx.shape==(FACES,3)and r['loadedGroupScale']==[1,1,1]
 with np.load(ROOT/plan['providerOriginalNPZ']['path'],allow_pickle=False)as z:worlds={'providerOriginal':z[plan['providerOriginalNPZKey']].astype('<f8')}
 unused={}
 for name,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  positions=np.asarray(r[key],dtype='<f8').reshape(-1,3);assert np.isfinite(positions).all()and idx.min()>=0 and idx.max()<len(positions);worlds[name]=positions[idx];unused[name]=dict(completeUnusedPositionCount=len(positions),wholePositionSHA256=digest(positions.tobytes()),wholePositionBounds=[positions.min(0).tolist(),positions.max(0).tolist()])
 assert all(w.shape==(FACES,3,3)and np.isfinite(w).all()for w in worlds.values());assert digest(worlds['providerOriginal'].tobytes())==plan['providerOriginalWorldSHA256']
 grounds={name:np.asarray(arr,dtype='<f8').reshape(-1,3,3)for name,arr in d['completeRegionalGroundWorlds'].items()};assert set(grounds)=={'actualLiteral','explicitLeftF32','explicitBalancedF32'}
 for b in d['groundWorldBindings']:assert digest(grounds[b['name']].tobytes())==b['worldTrianglesSHA256']==GROUND_SHA and grounds[b['name']].shape==(4215,3,3)
 components=read(G.Q.W.Q.COMP)['components'];labels={i:j for j,c in enumerate(components)for i in c['sourceFaceIndices']};assert len(components)==BODIES and sorted(labels)==list(range(FACES))
 return scope,receipt,d,worlds,grounds,unused,components,labels,pins

def fence(a,before,pins,ground,full=False):
 assert reservations.owns(read(LEASE));assert ref(ROOT/'3d-viewer/city/data/manifest.json')==before['currentState']['currentManifest']
 for e in pins:assert ref(ROOT/e['path'])==e
 for p,h in ground['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 state=G.Q.W.state(before['currentState']['uids']);assert json.loads(json.dumps(state,allow_nan=False))==before['currentState']['rows']
 if full:assert G.inputs(a)==before

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args();before,receipt,ground,worlds,grounds,unused,components,labels,pins=inputs(a)
 resources=sorted(['building:'+u for u in before['currentState']['uids']]+['native-model:'+before['currentState']['sourceKey'],'source-context:'+BATCH+'-compute'])
 if a.preflight_only:print(json.dumps(dict(readOnlyPreflightPassed=True,noWorker=True,sourceFaces=FACES,originalBodies=BODIES,sourceWorlds=len(worlds),groundWorlds=len(grounds),groundFaces=4215,distinctSourceWorlds=len({digest(w.tobytes())for w in worlds.values()}),groundWorldsAllByteIdentical=True,resources=len(resources))));return
 if not a.owned:
  assert not LOCAL.exists()and not D.exists();claim=reservations.claim('citywalk-full-current-finite-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True);return
 assert reservations.owns(read(LEASE));save(LOCAL/'protected-state-before.json',before);save(LOCAL/'immutable-lease-at-start.json',read(LEASE));D.mkdir();fence(a,before,pins,ground,True)
 proofs={};bindings=[];chunks=[]
 for name,w in worlds.items():
  sh=digest(w.tobytes())
  for gm,t in grounds.items():
   gh=digest(t.tobytes());key=digest((sh+gh).encode());bindings.append(dict(sourceWorld=name,groundWorld=gm,completeSourceFaces=FACES,completeGroundFaces=len(t),sourceWorldSHA256=sh,groundWorldSHA256=gh,proofTupleSHA256=key))
   if key in proofs:continue
   complete=CompleteGround(t);rows=[]
   for start in range(0,FACES,CHUNK):
    stop=min(start+CHUNK,FACES);path=LOCAL/'chunks'/key/f'{start:05d}-{stop:05d}.json.gz';contract=dict(uid=UID,sourceSHA256=G.Q.read(G.Q.P/'ground-capture-plan.json')['sourceSHA256'],worldSHA256=sh,groundSHA256=gh,firstFace=start,exclusiveLastFace=stop,completeFaces=FACES,completeGroundFaces=4215,codePins=pins,ordinaryThresholdM='-1/2');fence(a,before,pins,ground)
    if path.exists():chunk=read(path);assert chunk['contract']==contract
    else:
     chunk=dict(contract=contract,rows=[face_proof(w[i],complete,i,labels[i])for i in range(start,stop)]);tmp=path.with_name(path.name+'.pending.json.gz');save(tmp,chunk);assert read(tmp)==chunk;tmp.replace(path)
    assert [r['face']for r in chunk['rows']]==list(range(start,stop));rows.extend(chunk['rows']);chunks.append(ref(path));assert reservations.heartbeat(read(LEASE))['ok'];print(json.dumps(dict(sourceWorld=name,groundWorld=gm,completedFaces=stop,expectedFaces=FACES)),flush=True)
   assert len(rows)==FACES
   body=[dict(originalBody=i,sourceFaceIDs=c['sourceFaceIndices'],originalSourceMetadata=c,ordinaryFailingFaces=[j for j in c['sourceFaceIndices']if not rows[j]['ordinaryFiniteProved']],coverageFailingFaces=[j for j in c['sourceFaceIndices']if not rows[j]['completeProjectionCovered']],strictUncertifiedFaces=[j for j in c['sourceFaceIndices']if not rows[j]['strictPositiveFiniteProved']],gradeRootAccepted=False,terminalRoleQualified=False)for i,c in enumerate(components)]
   proofs[key]=dict(allWholeFacetProofs=rows,ordinaryFailingFaces=[r['face']for r in rows if not r['ordinaryFiniteProved']],coverageFailingFaces=[r['face']for r in rows if not r['completeProjectionCovered']],strictUncertifiedFaces=[r['face']for r in rows if not r['strictPositiveFiniteProved']],completeOriginalBodyObligations=body,foundationOrdinarySurfacePolicyProved=all(r['ordinaryFiniteProved']for r in rows),buriedFailedSurfaceInterpretationPending=True)
 fence(a,before,pins,ground,True);save(D/'diagnostic.json.gz',dict(sourceOnly=True,currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,gradeRootAccepted=False,all193RolesQualified=False,sourceGeometryChanges=0,terrainGeometryChanges=0,currentManifest=before['currentState']['currentManifest'],currentNativeCount=6650,uid=UID,completeSourceFaces=FACES,completeOriginalBodies=BODIES,allSourceGroundBindings=bindings,distinctCompleteFiniteProofs=proofs,completeUnusedPOSITIONBindings=unused,completeOriginalBodyPartition=ref(G.Q.W.Q.COMP),currentGroundProof=ref(G.D/'complete-current-drawn-ground.json.gz'),ordinaryThresholdM='-1/2',strictWarningsDoNotInvalidateOrdinaryClearFacets=True,currentNativeContactsReusedOnly=ref(G.Q.W.Q.D/'diagnostic.json.gz'),exact13IdentityContextReusableNotNewAcceptance=True,actualMAXContractAndExclusionsPreserved=True,noPointOnlyCoverageOrRootCredit=True,evidenceRefs=pins+[ref(G.D/'result.json'),ref(G.D/'complete-current-drawn-ground.json.gz')]+chunks));subprocess.run([sys.executable,str(FREEZER),'--expected-manifest',a.expected_manifest],cwd=ROOT,check=True);fence(a,before,pins,ground,True)
if __name__=='__main__':main()
