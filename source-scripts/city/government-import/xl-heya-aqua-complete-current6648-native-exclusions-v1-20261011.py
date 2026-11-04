"""DRAFT fresh scalar bounds exclusions; P184285 remains a coupled actor.

Every other installed actor is tested against whole unused owned POSITION in
four modes by actual literal/left/balanced native bounds. Any overlap/touch is
saved as a full finite actor obligation, never accepted by metadata or name.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from complete_actual_native_position_bounds_separation_20261011 import verify
from exact_finite_contact_crossing_classification_20261011 import classify

BASE=ROOT/'docs/astra-city/government-import'
NATIVE=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v3-20261011'
ACTUAL=BASE/'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011'
ACCOUNT=BASE/'government-xl-heya-aqua-current-main-family-exposed-root-account-v1-20261011'
IDENTITY=BASE/'government-xl-heya-aqua-184286-current-owned-identity-v1-20261011'
BATCH='government-xl-heya-aqua-complete-current6648-native-exclusions-v1-20261011'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
T,P='landsd/184286:0','landsd/184285:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 assert reservations.owns(read(LEASE))and not DOC.exists()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest)
 assert start['sha256']=='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
 refs=[Path(__file__),HERE/'complete_actual_native_position_bounds_separation_20261011.py',
  HERE/'test_complete_actual_native_position_bounds_separation_20261011.py',
  HERE/'exact_finite_contact_crossing_classification_20261011.py',
  HERE/'test_exact_finite_contact_crossing_classification_20261011.py'];pins={r['path']:r['sha256']for r in map(ref,refs)}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [NATIVE,ACTUAL,ACCOUNT,IDENTITY]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for pin in receipt['evidenceRefs']:
    assert ref(ROOT/pin['path'])==pin;refs.append(ROOT/pin['path']);pins[pin['path']]=pin['sha256']
 inp=read(NATIVE/'input.json.gz');inventory=read(NATIVE/'inventory.json.gz')
 assert inp['currentManifest']==start and inp['currentBoundOnly']and inventory['currentBoundOnly']
 assert inventory['completeNativeActors']==inventory['successfullyCapturedActors']==6648 and not inventory['errors']and inventory['startAndEndInputHashesVerified']
 native={r['uid']:r for r in inventory['rows']};raw={r['uid']:r for r in inp['rows']}
 assert len(native)==len(raw)==6648 and set(native)==set(raw)and P in native and T not in native
 catalogue_models={}
 for url in read(manifest)['officialModelCatalogues']:
  for e in read(ROOT/'3d-viewer'/url)['models']:
   assert e['uid']not in catalogue_models;catalogue_models[e['uid']]=e
 assert set(catalogue_models)==set(native)
 for uid,r in raw.items():
  assert r['rawCurrentEntry']==catalogue_models[uid]and native[uid]['sourceSHA256']==r['rawCurrentEntry']['sha256']==ref(ROOT/r['source']['path'])['sha256']
  assert r['currentBuilding']==inp['currentAllNativeSourceForms'][uid]and r['currentBuilding']['buildingCSUID']==r['rawCurrentEntry']['buildingCSUID']
 geometry=read(ACTUAL/'complete-current-actual-source-and-ground-184286-0.json.gz')
 captured_inputs=read(ACTUAL/'capture-inputs.json.gz');selected=[r for r in captured_inputs['completeCurrentForms']if r['uid']==T];assert len(selected)==1
 assert geometry['uid']==T and geometry['sourceSHA256']=='f9c73a61b679ebc18df1741c01c7e98463a4269928a38b882e3a41d268646155'
 assert geometry['completeRecursiveLoaderModuleClosure']==inventory['completeRecursiveProductionModuleClosure']
 packed=geometry['completeOriginalPOSITIONProof'];assert packed['allOriginalPositionVerticesAccounted']and packed['completeOriginalTriangles']==17910
 bounds={'providerOriginal':packed['originalWholeSourceBounds']}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:
  points=np.asarray(geometry[key],dtype='<f8').reshape(-1,3);assert len(points)==packed['completeOriginalPositionVertices']and np.isfinite(points).all()
  bounds[mode]=[points.min(0).tolist(),points.max(0).tolist()]
 carrier=read(ACTUAL/'complete-current-actual-source-and-ground-184285-0.json.gz')
 installed=read(IDENTITY/'installed-support-entry.json');assert raw[P]['rawCurrentEntry']==carrier['entry']==installed['entry']
 assert ref(ROOT/installed['catalogue']['path'])==installed['catalogue']and ref(ROOT/installed['asset']['path'])==installed['asset']==raw[P]['source']
 assert raw[P]['source']['sha256']==carrier['sourceSHA256']=='46add0484e7cedd20b7de12c9843a2cba8bb419f5824dde27fb9b41fb8efa1b2'
 assert raw[P]['completeOriginalPOSITIONProof']==carrier['completeOriginalPOSITIONProof']
 assert carrier['completeRecursiveLoaderModuleClosure']==inventory['completeRecursiveProductionModuleClosure']
 for field,key in [('completeLiteralBounds','completeLiteralWorldPosition'),('completeLeftAssociatedF32Bounds','completeExplicitLeftAssociatedFloat32WorldPosition'),('completeBalancedF32Bounds','completeExplicitBalancedFloat32WorldPosition')]:
  a=np.asarray(carrier[key],dtype='<f8').reshape(-1,3);assert native[P][field]==[a.min(0).tolist(),a.max(0).tolist()]
 separated=[];overlapping=[]
 for uid in sorted(native):
  if uid==P:continue
  try:proof=verify(bounds,[native[uid]])
  except AssertionError as error:
   overlapping.append(dict(uid=uid,rawCurrentNativeInput=raw[uid],completeActualNativePositionBounds=native[uid],unresolvedFiniteActorObligation=str(error)))
  else:separated.append(proof['rows'][0])
 assert len(separated)+len(overlapping)==6647
 account=read(ACCOUNT/'proposal.json.gz');assert len(account['rows'])==4
 interfacefolder=BASE/'government-xl-heya-aqua-184286-184285-current-four-world-interfaces-grade-v1-20261011'
 # This complete interface artifact is already recursively bound by ACCOUNT.
 assert ref(interfacefolder/'diagnostic.json.gz')['sha256']==pins[str((interfacefolder/'diagnostic.json.gz').relative_to(ROOT))]
 interfaces=read(interfacefolder/'diagnostic.json.gz');actual=read(ACTUAL/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];coupled=[]
 for mode in ['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']:
  item=next(r for r in interfaces['rows']if r['arithmetic']==mode)
  worlds={u:np.asarray(actual[u]['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8')for u in [T,P]}
  for u,w in worlds.items():assert digest(w.tobytes())==item['completeWorldHashes'][u]
  records=[dict(contact=c,exactFiniteContactClassification=classify(worlds[T][c['sourceFaceA']],worlds[P][c['sourceFaceB']],c))for c in item['allCrossPrimitiveRecordsWithRealComponentBindings']]
  coupled.append(dict(arithmetic=mode,completeTowerPodiumPrimitiveClassifications=records,
   properTriangleInteriorCrossings=[i for i,r in enumerate(records)if r['exactFiniteContactClassification']['properTriangleInteriorCrossing']],
   boundaryOrAuthoredJoinInterpretationNotAutomaticallyGranted=True))
 save(DOC/'diagnostic.json.gz',dict(uids=[T],currentManifest=start,completeOwnedUnusedPositionBounds=bounds,
  completeCurrentNativeActors=6648,completeForeignNativeActors=6647,allSeparatedNativeActors=separated,
  actualNativeActorsRequiringFullFiniteCollision=overlapping,
  allOtherInstalledNativeWholeActualPositionBoundsStrictlyDisjoint=not overlapping,
  coupledInstalledPodium=dict(uid=P,rawCurrentInput=raw[P],completeActualNativeBounds=native[P],
   wholePodiumCurrentFourWorldFiniteAndInterfaceAccount=ref(ACCOUNT/'proposal.json.gz'),
   currentInstalledBinding=ref(IDENTITY/'installed-support-entry.json'),notIgnoredOrReapproved=True),
  completeCoupledOriginalPrimitiveContext=coupled,
  sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False))
 assert ref(manifest)==start and reservations.owns(read(LEASE))
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 refs.append(DOC/'diagnostic.json.gz')
 s=importlib.util.spec_from_file_location('heya_complete_native_guard_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 result=m.freeze(BATCH,'heya-fresh6648-native-complete-POSITION-exclusions-with-explicit-original-carrier',refs,
  dict(uids=[T],completeCurrentNativeActors=6648,actualNativeActorsRequiringFullFiniteCollision=[r['uid']for r in overlapping],physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=result['jobId'],actualNativeActorsRequiringFullFiniteCollision=[r['uid']for r in overlapping])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 claim=reservations.claim('heya-current6648-native-exclusions-'+str(uuid.uuid4()),['building:'+u for u in [T,P]],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
