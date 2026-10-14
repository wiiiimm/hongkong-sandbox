"""Draft bounded five complete saved regions; no worker until ROOT review."""
from pathlib import Path
import json,uuid,sys,subprocess,time,copy,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
from polyu_five_mask_source_plane_partition_v1_20261014 import serial
import polyu_four_compatible_parent_region_nomination_v1_draft_20261014 as previous
import polyu_refine_rejected_parent_regions_v1_draft_20261014 as refinement
ref,check=previous.ref,previous.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-refined-rejected-parent-nomination-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
NOM=previous.DOC;CAP=BASE/'government-xl-polyu-four-compatible-parent-current-production-v2-20261014'
TARGETS=[(1,2590,1,1),(8,0,0,0),(8,4,0,34),(8,18,1,87),(3,40,1,3)]
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 _,_,_,_,feasibility,worlds=previous.load()
 nom=read(NOM/'private-compatible-current-parent-append-nomination.json.gz');cap=read(CAP/'private-native-terrain-candidate.json.gz')
 receipt=read(NOM/'result.json');assert receipt['jobId']=='f2df44cd1ac7864fd9e0a31b55b635679d7ad8f1356eafc2bb27f28423da8400'
 assert read(CAP/'result.json')['jobId']=='8f608c0269c10496b67841ea1c50069e73030819a74fcd6e5cb10cc871c0053f'
 assert mesh_binding(nom['newNativeMesh'])==mesh_binding({k:cap['nativeMesh'][k]for k in ['position','index']})==nom['newCompleteMeshBinding']==pins['completePriorMeshBinding']
 assert len(nom['rejectedNewPieces'])==780
 selected=[]
 for target in TARGETS:
  rows=[r for r in nom['rejectedNewPieces']if tuple(r[k]for k in ['parentFacet','insideOrdinal','fan','region'])==target];assert rows
  polygon=rows[0]['idealCompatibleOwnParentPolygon'];assert all(r['idealCompatibleOwnParentPolygon']==polygon for r in rows)
  selected.append(dict(target=list(target),idealCompatibleOwnParentPolygon=polygon,priorRejectedPieces=rows))
 assert len({json.dumps(r['idealCompatibleOwnParentPolygon'],sort_keys=True)for r in selected})==5
 return pins,nom,cap,feasibility,worlds,selected

def schema_only():
 p,n,c,f,w,s=load()
 return dict(passed=True,priorTuple=n['newCompleteMeshBinding'],selectedCompleteRegions=5,all780PriorRejectsPreserved=True,sourceWorlds=4,facesPerWorld=10536,noActualRefinementOrDBLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,nom,cap,feasibility,worlds,selected=load()
 validation=read(check(pins['validationRef']));assert validation['passedTests']==9 and validation['failedTests']==0 and validation['exitCode']==0
 assert validation['executedCodeRefs']==[ref(Path(refinement.__file__)),ref(HERE/'test_polyu_refine_rejected_parent_regions_v1_draft_20261014.py')]
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['beforeEndAllPinsVerified']
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+validation['evidenceRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
 for folder in [NOM,CAP]:
  result=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert reservations.owns(lease)
 fence();DOC.mkdir();mesh=copy.deepcopy(nom['newNativeMesh']);before=mesh_binding(mesh);oldslots=before['completePositionVertices'];oldfaces=before['completeIndexedFaces']
 position=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3);keys={position[q].tobytes()for q in np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)}
 records=[];appended=[];existing=[]
 for i,s in enumerate(selected):
  pulse();parent=feasibility['complete12CapturedParentFacets'][s['target'][0]]
  def checked_piece(triangle,complete_worlds):
   pulse();return previous.geometry.compatible_piece(triangle,complete_worlds)
  result=refinement.refine(s['idealCompatibleOwnParentPolygon'],parent,worlds,max_depth=12,max_attempts=2048,checker=checked_piece)
  for piece in result['acceptedPieces']:
   triangle=piece['packing']['packedTriplet'];key=np.asarray(triangle,dtype='<f8').tobytes()
   if key in keys:existing.append(dict(region=i,**piece));continue
   keys.add(key);face=len(mesh['index'])//3;slot=len(mesh['position'])//3
   mesh['position'].extend(v for p in triangle for v in p);mesh['index'].extend([slot,slot+1,slot+2]);appended.append(dict(candidateFace=face,completeSelectedRegion=i,**piece))
  records.append(dict(**s,completeRefinement=result));save(DOC/'regions'/f'{i:02}.json.gz',serial(records[-1]));print(json.dumps(dict(regionCompleted=i+1,attempts=result['attempts'],appended=len(appended),unresolvedIdealTriangles=len(result['unresolvedIdealTriangles']))),flush=True);pulse()
 assert np.asarray(mesh['position'][:oldslots*3],dtype='<f8').tobytes()==np.asarray(nom['newNativeMesh']['position'],dtype='<f8').tobytes()
 assert mesh['index'][:oldfaces*3]==nom['newNativeMesh']['index']
 save(DOC/'private-refined-rejected-parent-nomination.json.gz',serial(dict(newNativeMesh=mesh,newCompleteMeshBinding=mesh_binding(mesh),previousCompleteMeshBinding=before,
  previousCapturedCandidate=ref(CAP/'private-native-terrain-candidate.json.gz'),previousNomination=ref(NOM/'private-compatible-current-parent-append-nomination.json.gz'),
  completeSelectedRegions=records,appendedFaces=appended,exactExistingRepresentations=existing,allPriorPositionAndIndexBytesIncludingUnusedAndSignedZeroPreserved=True,
  all780OldRejectedPiecesRemainRejected=True,noKnownConflictingTriangleRestored=True,originalGovernmentGeometryAndPoseUnchanged=True,
  sourceOverlapRequiresFreshGeometryBinding=True,actualProductionCoverageAll3366Sites25GuardRowsAndWholeNativeStillPending=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False)))
 refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 spec=importlib.util.spec_from_file_location('polyu_refined_parent_freezer',FREEZER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'bounded-five-complete-rejected-ideal-parent-region-own-plane-subdivision',[check(q)for q in refs],dict(uids=previous.UIDS,sourceOnly=True,privateCandidate=True,newlyInstalled=0,appendedFaces=len(appended),physicalAccepted=False,currentAcceptance=False))
 fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),appendedFaces=len(appended))),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
 if '--owned'in sys.argv:return owned()
 assert '--nominate-refined-rejected-regions-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
 claim=reservations.claim('polyu-refined-parent-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
