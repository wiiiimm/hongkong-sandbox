"""ROOT-only normal execution; source context, no identity/physical approval.

Import and preflight are metadata-only and do not import project/geometry code.
V1 and its complete81-pin evidence packet remain untouched.
"""
import argparse,gzip,hashlib,importlib.util,json,os,sys,time,uuid
from pathlib import Path

PACKET=Path(__file__).resolve().parent
ROOT=PACKET.parents[3]
HERE=ROOT/'source-scripts/city/government-import'
RESEARCH=ROOT/'docs/astra-city/government-import/government-xl-lai-chi-kok281463-provider-site-scope-v2-20261013'
CONTRACT=PACKET/'comparison-input-contract-v2.json'
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-identity-190-actionable-ledger-20261010/result.json'
PRIOR_JOB='d705c0870384ecba840b1252c45b14688f73e165d0cdbc00d4277a6e0e8704ea'
BATCH='government-xl-lai-chi-kok281463-complete-original-site-podium-context-v2-20261013'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
LEASE=LOCAL/'reservation.json'
PROCESS=LOCAL/'owned-process.json'
MANIFEST=ROOT/'3d-viewer/city/data/manifest.json'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
UID='landsd/281463:0'
SOURCE='1480540e0a32849425d5238eeea7ecb3a7124633226c1eae9cab2d041b968d86'
WORLD='d8ab9b872ef0696d3d95d8e47df0f64db2e540229961f0142d1e83af7cf08b22'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def fence(contract,contract_sha):
 assert sha(CONTRACT)==contract_sha and sha(MANIFEST)==CURRENT
 for rel,value in contract['allInputHashes'].items():assert sha(ROOT/rel)==value
def summary(diag_sha,diag_bytes,component_count,zero_count):
 assert len(diag_sha)==64 and all(c in '0123456789abcdef' for c in diag_sha)
 assert type(diag_bytes)is int and diag_bytes>0
 assert type(component_count)is int and 0<component_count<=37577
 assert type(zero_count)is int and 0<=zero_count<37577
 return {'uids':[UID],'uid':UID,'modelId':'B321562211902063C0','sourceSHA256':SOURCE,'worldTrianglesSHA256':WORLD,'completeOriginalFaces':37577,'completeRealEdgeComponents':component_count,'nonrenderingOriginalFacesRetainedUncredited':zero_count,'historicalFarFaceCount':106,'completeCompressedDiagnostic':{'path':str((DOC/'diagnostic.json.gz').relative_to(ROOT)),'sha256':diag_sha,'bytes':diag_bytes},'priorExactSourceCompletedJob':PRIOR_JOB,'primaryImagesNotRegistered':True,'sameNameDoesNotExpandOwnership':True,'sevenIndependentForeignActorsRetained':True,'sourceRoleAccepted':False,'identityAccepted':False,'physicalAccepted':False,'currentAcceptance':False,'modelReviewWrites':0,'sourceGeometryChanges':0,'terrainGeometryChanges':0,'newlyInstalled':0}
def preflight():
 contract=read(CONTRACT);contract_sha=sha(CONTRACT);fence(contract,contract_sha)
 assert contract['sourceSHA256']==SOURCE and contract['worldTrianglesSHA256']==WORLD
 assert contract['currentAcceptance'] is False and contract['sourceGeometryChanges']==0
 assert not DOC.exists() and len(contract['canonicalResources'])==18
 assert contract['canonicalResources']==sorted(set(contract['canonicalResources']))
 assert 'building:'+UID in contract['canonicalResources']
 roles=read(ROOT/contract['priorRolePath']);assert roles['uid']==UID and roles['sourceSHA256']==SOURCE and roles['worldTrianglesSHA256']==WORLD
 assert roles['variants']['direct-shared-OSM']['stats']['sourceFacesBeyond10m']==106
 exact=read(RESEARCH/'provider-site-scope-findings.json')
 assert exact['exactProviderAttributes']['BuildingCSUID']=='3215622119P20070611'
 assert exact['exactProviderAttributes']['BuildingNameEN']=='LAI CHI KOK PARK SPORTS CENTRE'
 assert exact['sourceJSONMetadata']['meshes'][0]['primitives'][0]['indices']==3
 assert exact['sourceJSONMetadata']['accessors'][3]['count']==112731
 prior=read(PRIOR);assert prior['jobId']==PRIOR_JOB
 matched=[r for r in prior['rows'] if r['uid']==UID and r['sourceSHA256']==SOURCE];assert len(matched)==1 and matched[0]['installed'] is False
 # Freezer representation/schema guard only, not synthetic source proof.
 probe=summary('0'*64,1,1,0)
 assert probe['uids']==[UID] and json.loads(json.dumps(probe))==probe
 assert not {'completeComponents','completeOriginalTopology','completeOriginalWorldTriangles'}&set(probe)
 assert len(json.dumps(probe).encode())<16384 and all(probe[k] is False for k in ('sourceRoleAccepted','identityAccepted','physicalAccepted','currentAcceptance'))
 fence(contract,contract_sha)
 return contract,contract_sha,roles,exact,prior
def process_exists(pid,group=False):
 try:
  (os.killpg if group else os.kill)(pid,0);return True
 except ProcessLookupError:return False
 except PermissionError:return True
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--preflight-only',action='store_true');parser.add_argument('--owned',action='store_true');args=parser.parse_args();assert not(args.preflight_only and args.owned)
 if args.owned:
  lease=read(LEASE);assert os.getpgrp()==os.getpid()
  with PROCESS.open('x') as stream:json.dump({'pid':os.getpid(),'pgid':os.getpgrp(),'cwd':str(ROOT),'argv':sys.argv,'token':lease['token'],'callerSHA256':sha(Path(__file__))},stream)
 else:assert not LOCAL.exists()
 contract,contract_sha,prior,metadata,prior_receipt=preflight()
 if args.preflight_only:
  print(json.dumps({'passed':True,'faces':37577,'expectedHistoricalFarFaces':106,'resources':18,'currentManifestSHA256':CURRENT,'priorExactSourceCompletedJob':PRIOR_JOB,'savedPriorExactSourceRowMatches':True,'lightweightFreezerUIDsAndReferenceSchemaPassed':True,'noDB':True,'noLease':True,'noSourceDecode':True,'allStartEndLiteralPinsUnchanged':True}));return
 sys.path.insert(0,str(HERE))
 from run import save,connect,reservations
 if not args.owned:
  from reservation_runner import run_reserved
  claim=reservations.claim('lai-chi-kok-source-scope-v2-'+str(uuid.uuid4()),contract['canonicalResources'],batch=BATCH,ttl=3600);assert claim['ok'],claim
  lease=claim['reservation'];save(LEASE,json.loads(json.dumps(lease,default=str)));result=None
  try:
   result=run_reserved(LEASE,[sys.executable,str(Path(__file__)),'--owned'],ttl=3600,heartbeat_seconds=20)
   save(LOCAL/'supervisor-result.json',result)
   assert result['exitCode']==0 and result['released'] is True,result
  finally:
   # Fallback for initial-renewal/supervisor failure. Never release a live child.
   if reservations.owns(lease):
    if PROCESS.exists():
     state=read(PROCESS);assert state['token']==lease['token']
     assert not process_exists(state['pid']) and not process_exists(state['pgid'],True),'child/group still live; retain exact lease'
    else:assert result is not None and result['error'] in ('lease-not-owned-or-unreachable','command-launch-failed'),'no child absence proof; retain exact lease'
    assert reservations.release(lease)['ok']
  return
 assert lease['resources']==contract['canonicalResources'] and reservations.owns(lease)
 with connect() as connection:
  connection.execute('SET TRANSACTION READ ONLY')
  assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(PRIOR_JOB,)).fetchone()==('complete',prior_receipt)
 fence(contract,contract_sha)
 heartbeat_at=time.monotonic()
 def heartbeat_due(force=False):
  nonlocal heartbeat_at
  if force or time.monotonic()-heartbeat_at>=20:
   renewal=reservations.heartbeat(lease,ttl=3600);assert renewal['ok'],renewal;heartbeat_at=time.monotonic()
 heartbeat_due(True)
 import numpy as np
 import shapely
 from shapely.geometry import Polygon
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 from exact_original_shared_edge_component_census_v2_20261011 import census
 from xl_source_stream_binding_20261009 import source_stream_binding
 raw=(ROOT/metadata['sourceAssetPath']).read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE
 world=decode_original_world_triangles(raw)
 assert world.shape==(37577,3,3) and np.isfinite(world).all()
 assert hashlib.sha256(world.astype('<f8').tobytes()).hexdigest()==WORLD
 topology=census(world,list(range(len(world))))
 groups=topology['sharedEdgeConnectedComponents'];zeros=topology['exactNonrenderingOriginalFaces']
 represented=[i for ids in groups for i in ids]+zeros
 assert len(represented)==37577 and sorted(represented)==list(range(37577))
 form=metadata['currentFormVerbatim'];foot=Polygon(form['rings'][0],form['rings'][1:])
 # Unchanged old diagnostic threshold; only recovers unsaved106 face IDs.
 distances=shapely.distance(shapely.points(world[:,:,[0,2]].reshape(-1,2)),foot).reshape(-1,3)
 far=np.flatnonzero(distances.max(axis=1)>10).tolist();assert len(far)==106
 far_world=world[far]
 assert [far_world.min((0,1)).tolist(),far_world.max((0,1)).tolist()]==prior['variants']['direct-shared-OSM']['stats']['farSourceBounds']
 components=[]
 for i,ids in enumerate(groups):
  heartbeat_due()
  components.append({'component':i,'completeOriginalFaceIds':ids,'completeOriginalWorldTriangles':world[ids].tolist(),'worldBounds':[world[ids].min((0,1)).tolist(),world[ids].max((0,1)).tolist()],'historicalFarFaceIds':[face for face in ids if face in set(far)],'sourceRoleAccepted':False,'groundOrStructuralRootCredit':False})
 heartbeat_due(True)
 out={'uids':[UID],'uid':UID,'modelId':'B321562211902063C0','sourceSHA256':SOURCE,'worldTrianglesSHA256':WORLD,'originalCoordinateView':'providerOriginal only; no runtime arithmetic views captured','completeOriginalFaces':37577,'completeSourceStreamBinding':source_stream_binding(raw),'completeOriginalTopology':topology,'completeComponents':components,'historicalFarFaceIdsRecovered':far,'historicalNonrenderingOriginalFacesUncredited':zeros,'exactNonrenderingOriginalPrimitiveWorldTriangles':world[zeros].tolist(),'priorRoleRecordVerbatim':prior,'providerAndOperatorScopeRecordVerbatim':metadata,'primaryImagesNotRegistered':True,'sourceGeometryChanges':0,'terrainGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'currentAcceptance':False,'sourceRoleAccepted':False,'modelReviewWrites':0,'newlyInstalled':0}
 out=json.loads(json.dumps(out,sort_keys=True));save(DOC/'diagnostic.json.gz',out)
 fence(contract,contract_sha);heartbeat_due(True);assert reservations.owns(lease)
 diagnostic=DOC/'diagnostic.json.gz';frozen=summary(sha(diagnostic),diagnostic.stat().st_size,len(groups),len(zeros))
 assert len(json.dumps(frozen).encode())<16384
 refs=[ROOT/rel for rel in contract['allInputHashes']]+[CONTRACT,diagnostic]
 spec=importlib.util.spec_from_file_location('lckp_scope_context_freeze_v2',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
 receipt=freezer.freeze(BATCH,'exact-provider-named-park-podium-component-context-no-role-credit-v2',refs,frozen)
 fence(contract,contract_sha);heartbeat_due(True);assert reservations.owns(lease)
 print(json.dumps({'jobId':receipt['jobId'],'completeOriginalFaces':37577,'historicalFarFaceIds':106,'diagnosticSHA256':sha(diagnostic),'currentAcceptance':False}),flush=True)
if __name__=='__main__':main()
