"""ROOT-only full four-view Museum/Star Mart finite surfaces, no acceptance."""
import argparse,gzip,hashlib,json,sys,time
from pathlib import Path
PACKET=Path(__file__).resolve().parent;ROOT=PACKET.parents[3]
HERE=ROOT/'source-scripts/city/government-import';CONTRACT=PACKET/'input-contract.json'
OUTPUT=PACKET/'collision-output-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(p,v):
 raw=json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 with p.open('xb')as f:f.write(gzip.compress(raw,mtime=0)if p.suffix=='.gz'else raw+b'\n')
def fence(c,h):
 assert sha(CONTRACT)==h and sha(Path(__file__))==c['callerSHA256']
 for p,v in c['filePins'].items():assert sha(ROOT/p)==v,p
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==c['currentManifestSHA256']
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
 g.add_argument('--preflight-only',action='store_true');g.add_argument('--calculate-current-full-collision-only',action='store_true')
 p.add_argument('--lease-file',type=Path);args=p.parse_args();c=read(CONTRACT);ch=sha(CONTRACT);fence(c,ch)
 assert not OUTPUT.exists();scope=read(ROOT/c['sourceContextPath']);array=read(ROOT/c['completeArrayPath'])
 assert scope['uid']==array['uid']=='landsd/165054:0'
 assert scope['sourceSHA256']==array['sourceSHA256']==c['sourceSHA256']
 assert scope['worldTrianglesSHA256']==array['worldTrianglesSHA256']==c['providerOriginalWorldSHA256']
 assert scope['completeOriginalFaces']==array['completeOriginalFaceCount']==15140
 assert len(array['completeOrderedOriginalTriangles'])==15140
 capture_path=ROOT/c['reusedCompleteCapturePath'];pose_path=ROOT/c['reusedPoseAuditPath'];log_path=ROOT/c['reusedCaptureLogPath']
 assert sha(capture_path)==c['reusedCompleteCaptureSHA256']=='25515aa53a0aba9e27009c1e94d7320bc06549076d6d3f1e60bc13ea8022a81e'
 saved_log=read(log_path);assert saved_log['exitCode']==0
 log_record=json.loads(saved_log['stdout'].strip());assert log_record['complete']and log_record['captureSHA256']==sha(capture_path)and log_record['sourceFaces']==15140
 actual=read(capture_path);pose=read(pose_path)
 assert actual['poseAuditSHA256']==sha(pose_path)and actual['startAndEndInputsVerified']
 assert actual['sourceSHA256']==c['sourceSHA256']and actual['completeOriginalFaceCount']==15140
 assert actual['entry']==read(ROOT/c['sourceRowPath'])['candidate']['entry']
 assert actual['currentSourceForm']==read(ROOT/c['sourceRowPath'])['source']['building']
 assert pose['exactLoaderTransformContractMatched']and pose['noToleranceIntroduced']and pose['sourcePoseChanges']==0
 for path,h in actual['inputHashes'].items():assert sha(ROOT/path)==h,path
 if args.preflight_only:
  assert args.lease_file is None;fence(c,ch)
  print(json.dumps({'passed':True,'sourceFaces':15140,'fullBASICUID':'landsd/57455:0','allChosenWitnessFacesNotUsedAsScope':True,'resources':c['canonicalResources'],'noModelImportsOrCalculation':True,'noDBOrLease':True}));return
 sys.path[:0]=[str(PACKET),str(HERE)];from run import reservations,connect,NATIVE_RUN
 lease=read(args.lease_file);assert lease['resources']==c['canonicalResources'] and reservations.owns(lease)
 last=time.monotonic()
 def beat(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   r=reservations.heartbeat(lease,ttl=3600);assert r['ok'];last=time.monotonic()
 def prior_neon_fence():
  row=read(ROOT/c['sourceRowPath'])
  with connect()as connection:
   connection.execute('SET TRANSACTION READ ONLY')
   for path in c['priorCompleteReceipts']:
    receipt=read(ROOT/path)
    assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   assert connection.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchall()==[(row['native']['resultSha'],)]
 prior_neon_fence()
 import numpy as np
 from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
 from exact_finite_contact_crossing_classification_20261011 import classify
 from xl_source_stream_binding_20261009 import source_stream_binding
 OUTPUT.mkdir();beat(True)
 try:
  # Complete original capture/pose/log already authenticated before claim branch.
  original=np.asarray(array['completeOrderedOriginalTriangles'],dtype='<f8');assert original.shape==(15140,3,3) and hashlib.sha256(original.tobytes()).hexdigest()==c['providerOriginalWorldSHA256']
  ix=np.asarray(actual['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
  assert len(ix)==15140 and len(actual['actualSourceMeshes'])==1
  source_mesh=actual['actualSourceMeshes'][0];attributes=source_mesh['completeAttributes'];local_ix=np.asarray(source_mesh['completeIndex'],dtype=np.int64)
  raw=(ROOT/c['originalAssetPath']).read_bytes();binding=source_stream_binding(raw);assert binding==scope['completeSourceStreamBinding']==array['completeSourceStreamBinding']
  from exact_source_attribute_json_zero_sign_transport_v1 import verify as verify_attribute_transport
  transport=verify_attribute_transport(raw,actual)
  assert len(transport['attributes']['normal']['zeroSignTransportRecords'])==c['expectedLostNORMALZeroSignScalars']==18
  for name,key in [('position','position'),('normal','normal'),('color','colour')]:
   assert transport['attributes'][name]['originalIndexedFloat32TriangleSHA256']==binding[key+'TriangleStreamSHA256']
  assert transport['attributes']['position']['completeOriginalFloat32BytesExactlyEqual']and transport['attributes']['color']['completeOriginalFloat32BytesExactlyEqual']
  save(OUTPUT/'exact-original-vs-json-attribute-transport.json',transport)
  basic=actual['starMart'];bi=np.asarray(basic['completeIndex'],dtype=np.int64).reshape(-1,3)
  base=np.asarray(basic['completePosition'],dtype='<f8').reshape(-1,3);assert len(base)==basic['completeVertices'] and len(bi)==basic['completeFaces']
  streams={'providerOriginal':original}
  for mode,key in [('literal','completeLiteralWorldPosition'),('leftFloat32','completeLeftFloat32WorldPosition'),('balancedFloat32','completeBalancedFloat32WorldPosition')]:
   positions=np.asarray(actual[key],dtype='<f8').reshape(-1,3);assert np.isfinite(positions).all();streams[mode]=positions[ix]
  foreign_positions={'providerOriginal':base,'literal':base,'leftFloat32':np.asarray(basic['leftAssociatedPerMultiplyAddFloat32WorldPosition'],dtype='<f8').reshape(-1,3),'balancedFloat32':np.asarray(basic['balancedPerMultiplyAddFloat32WorldPosition'],dtype='<f8').reshape(-1,3)}
  rows=[];cache={}
  for mode,world in streams.items():
   beat();foreign=foreign_positions[mode][bi];assert world.shape==(15140,3,3) and foreign.shape==(basic['completeFaces'],3,3)
   assert np.isfinite(world).all() and np.isfinite(foreign).all()
   key=(hashlib.sha256(world.tobytes()).hexdigest(),hashlib.sha256(foreign.tobytes()).hexdigest())
   if key not in cache:
    contacts=exact_finite_contacts(world,list(range(len(world))),foreign,list(range(len(foreign))),maximum_pairs=len(world)*len(foreign))
    for contact in contacts['contacts']:contact['crossingDiagnostic']=classify(world[contact['sourceFaceA']],foreign[contact['sourceFaceB']],contact)
    cache[key]=contacts
   row={'arithmetic':mode,'wholeSourceWorldSHA256':key[0],'wholeBASICWorldSHA256':key[1],'sourceFaces':15140,'completeBASICFaces':len(foreign),'fullFiniteSurfaceContacts':cache[key],'noFiniteSurfaceContacts':not cache[key]['contacts'],'containmentOrVolumetricClearanceCertified':False,'physicalAccepted':False}
   rows.append(row);save(OUTPUT/(mode+'-full-finite-contacts.json.gz'),row)
  beat(True);fence(c,ch);prior_neon_fence();assert reservations.owns(lease)
  for path,h in actual['inputHashes'].items():assert sha(ROOT/path)==h,path
  out={'uids':['landsd/165054:0'],'independentForeignUID':'landsd/57455:0','sourceSHA256':c['sourceSHA256'],'completeOriginalSourceFaces':15140,'fullBASICFaces':basic['completeFaces'],'fourViews':rows,'priorProjectedTwoWitnessesRetained':[12346,12347],'priorProjectedForeignOverlapM2':0.10717968519970641,'allTouchAndZeroPrimitivesRetained':True,'noChosenFaceShortcut':True,'noOwnershipException':True,'actualCaptureSHA256':sha(capture_path),'actualPoseAuditSHA256':sha(pose_path),'sourceAttributeTransportSHA256':sha(OUTPUT/'exact-original-vs-json-attribute-transport.json'),'capturedNormalByteParityClaim':False,'originalNormalSourceHashUnchanged':True,'actualCaptureReusedNoRecapture':True,'allInputHashes':c['filePins'],'currentAcceptance':False,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'terrainGeometryChanges':0}
  save(OUTPUT/'diagnostic.json.gz',out);save(OUTPUT/'result.json',{'uids':['landsd/165054:0'],'complete':True,'diagnosticSHA256':sha(OUTPUT/'diagnostic.json.gz'),'sourceFaces':15140,'BASICFaces':basic['completeFaces'],'contactCounts':[len(r['fullFiniteSurfaceContacts']['contacts'])for r in rows],'physicalAccepted':False,'currentAcceptance':False,'newlyInstalled':0})
  print(json.dumps(read(OUTPUT/'result.json')),flush=True)
 except BaseException as error:
  save(OUTPUT/'failure.json',{'complete':False,'errorType':type(error).__name__,'error':str(error),'sourceCorruptionInferred':False,'physicalAccepted':False});raise
 # External ROOT maintained supervisor releases only after child/group exit.
if __name__=='__main__':main()
