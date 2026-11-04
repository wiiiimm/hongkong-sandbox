"""Whole untouched13960 facets versus authentic source TIN and actual ground.

No replacement or acceptance credit. The original TIN is an independent causal
comparison; every existing raw current-ground failure remains explicit.
"""
import importlib.util,json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from evangel_college_original_wing_extension_identity_20261011 import UID,SOURCE_SHA
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011';TIN=BASE/'government-xl-evangel-college-91306-authentic-tin-source-context-v1-20261011';PRIOR=BASE/'government-xl-evangel-college-91306-complete13960-current-finite-diagnostic-v1-20261011'
BATCH='government-xl-evangel-college-91306-authentic-tin-complete-source-comparison-v2-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
CAPTURED_MANIFEST=BASE/'government-xl-evangel-college-91306-current-complete-identity-diagnostic-v1-20261011/captured-manifest.json'
HISTORICAL_MANIFEST_SHA='de8db939e48be0ed3661a9f3bf59454d92ff27f4a1024f34a401b17612e03e54'
def exact_historical_path(path,sha):
 if path=='3d-viewer/city/data/manifest.json':
  assert sha==HISTORICAL_MANIFEST_SHA and digest(CAPTURED_MANIFEST.read_bytes())==sha
  return CAPTURED_MANIFEST
 return ROOT/path
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__),CAPTURED_MANIFEST,HERE/'xl-evangel-college-91306-authentic-tin-complete-source-comparison-v1-20261011.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,TIN,PRIOR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:p=exact_historical_path(pin['path'],pin['sha256']);assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 capture=read(INPUT/'complete-current-actual-source-and-ground.json.gz');data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');tin=read(TIN/'complete-authentic-source-tin-ground.json.gz');prior=read(PRIOR/'diagnostic.json.gz')
 assert data['uid']==UID and data['sourceSHA256']==tin['sourceSHA256']==SOURCE_SHA and tin['sourceTerrainReceipt']['sheet']=='12-NW-21C'
 current=np.asarray(data['completeDrawnGround'],dtype='<f8');ground=np.asarray(tin['completeSelectedFacets'],dtype='<f8');ground_sha=digest(ground.tobytes());assert ground_sha==tin['completeSelectedFacetSHA256']and digest(current.tobytes())==data['completeDrawnGroundSHA256']and np.isfinite(ground).all()
 manifest=CAPTURED_MANIFEST;before=manifest.read_bytes();assert digest(before)==HISTORICAL_MANIFEST_SHA==capture['inputHashes']['3d-viewer/city/data/manifest.json']
 rows=[];cache={}
 for mode,stream in data['completeWorldStreams'].items():
  world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert world.shape==(13960,3,3)and digest(world.tobytes())==stream['completeWorldTriangleSHA256'];old=next(r for r in prior['rows']if r['arithmetic']==mode);assert old['completeWholeWorldSHA256']==stream['completeWorldTriangleSHA256']
  faces=[]
  for face_id,face in enumerate(world):
   key=(digest(face.tobytes()),ground_sha)
   if key not in cache:
    a=coarse(face,ground);b=None if a['existingOrdinaryClearanceBoundProved']else paired(face,ground);cache[key]=dict(coarse=a,paired=b,completeFiniteOrdinaryBoundProved=a['existingOrdinaryClearanceBoundProved']or bool(b and b['existingOrdinaryClearanceBoundProved']))
   saved=old['complete13960FaceComparisons'][face_id];assert saved['sourceFace']==face_id
   faces.append(dict(sourceFace=face_id,orientationDiagnostic=saved['orientationDiagnostic'],wholeOriginalYRangeHKPD=saved['wholeOriginalYRangeHKPD'],currentDrawnRawFinite=saved['groundComparisons']['currentDrawn'],authenticOriginalTINFinite=cache[key]))
   if face_id%2000==0:print(json.dumps(dict(arithmetic=mode,completedSourceFaces=face_id)),flush=True)
  rows.append(dict(arithmetic=mode,completeWholeWorldSHA256=stream['completeWorldTriangleSHA256'],complete13960FaceComparisons=faces,currentDrawnFailedFaces=old['failedFacesByGround']['currentDrawn'],authenticOriginalTINFailedFaces=[f['sourceFace']for f in faces if not f['authenticOriginalTINFinite']['completeFiniteOrdinaryBoundProved']],authenticOriginalTINUpwardFailedFaces=[f['sourceFace']for f in faces if f['orientationDiagnostic']=='upward'and not f['authenticOriginalTINFinite']['completeFiniteOrdinaryBoundProved']],currentRawFailuresRetained=True,currentGroundRootAccepted=False))
  save(LOCAL/('completed-mode-'+mode+'.json.gz'),dict(inputHashes=capture['inputHashes'],authenticGroundSHA256=ground_sha,row=rows[-1],checkpointOnly=True,currentAcceptance=False))
  print(json.dumps(dict(arithmetic=mode,currentFailed=len(rows[-1]['currentDrawnFailedFaces']),authenticFailed=len(rows[-1]['authenticOriginalTINFailedFaces']),authenticUpward=rows[-1]['authenticOriginalTINUpwardFailedFaces'])),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,completeAuthenticSelectedGroundFaces=len(ground),completeAuthenticSelectedGroundSHA256=ground_sha,completeCurrentGroundFaces=len(current),completeCurrentGroundSHA256=data['completeDrawnGroundSHA256'],authenticGroundYRangeHKPD=[float(ground[:,:,1].min()),float(ground[:,:,1].max())],sourceOnly=True,historicalCapturedBaselineOnly=True,capturedManifestArchive=dict(path=str(CAPTURED_MANIFEST.relative_to(ROOT)),sha256=HISTORICAL_MANIFEST_SHA,originalPath='3d-viewer/city/data/manifest.json'),authenticTINIsNotCurrentDrawnGround=True,terrainReplacementProposed=False,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,currentAcceptance=False,installationApproved=False))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in capture['inputHashes'].items():assert digest(exact_historical_path(p,h).read_bytes())==h
 refs.extend(HERE/n for n in ['evangel_college_original_wing_extension_identity_20261011.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_projection_coverage_v2_20261010.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.append(DOC/'diagnostic.json.gz')
 s=importlib.util.spec_from_file_location('evangel_authentic_whole_compare_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.freeze(BATCH,'complete13960-four-stream-authentic-source-TIN-vs-current-ground-cause-no-replacement-credit',refs,dict(uids=[UID],completeWholeSourceFaces=13960,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('evangel-authentic-full-compare-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
