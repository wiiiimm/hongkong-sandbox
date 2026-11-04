"""Unexecuted complete original T/P four-stream current-ground finite diagnosis.
Existing ordinary coarse -> exact paired kernels only. All source facets and all
captured finite terrain facets retained; no structural, root or native reapproval.
"""
import importlib.util,json,sys,subprocess,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011'
SOURCE=BASE/'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
BATCH='government-xl-heya-aqua-184286-184285-complete-four-stream-current-finite-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UIDS=['landsd/184286:0','landsd/184285:0'];COUNTS={UIDS[0]:17910,UIDS[1]:3844}
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]+[HERE/n for n in ['exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_triangle_pair_column_gap_20261010.py']];pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,SOURCE]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p);pins[pin['path']]=pin['sha256']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)=='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
 data=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];assert set(data)==set(UIDS)
 source=read(SOURCE/'diagnostic.json.gz');cache={};rows=[]
 for uid in UIDS:
  item=data[uid];n=COUNTS[uid];ground=np.asarray(item['completeDrawnGround'],dtype='<f8');gsha=digest(ground.tobytes());assert ground.ndim==3 and ground.shape[1:]==(3,3)and np.isfinite(ground).all()and gsha==item['completeDrawnGroundSHA256']
  topology=source['actors'][uid]['completeOriginalTopology'];assert len(topology['sharedEdgeConnectedComponents'])==(574 if uid==UIDS[0]else 34)
  for mode,stream in item['completeWorldStreams'].items():
   assert mode in ['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'];world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');wsha=digest(world.tobytes());assert world.shape==(n,3,3)and np.isfinite(world).all()and wsha==stream['completeWorldTriangleSHA256']
   faces=[]
   for face_id in range(n):
    key=(digest(world[face_id].tobytes()),gsha)
    if key not in cache:
     a=coarse(world[face_id],ground);b=None if a['existingOrdinaryClearanceBoundProved']else paired(world[face_id],ground)
     cache[key]=dict(coarse=a,paired=b,completeFiniteOrdinaryBoundProved=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved'])))
    faces.append(dict(sourceFace=face_id,completeOriginalFacetSHA256=digest(world[face_id].tobytes()),currentDrawnGroundComparison=cache[key]))
    if face_id%2000==0:print(json.dumps(dict(uid=uid,arithmetic=mode,completedSourceFaces=face_id)),flush=True)
   failed=[f['sourceFace']for f in faces if not f['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']]
   row=dict(uid=uid,arithmetic=mode,sourceSHA256=item['sourceSHA256'],completeWholeWorldSHA256=wsha,completeCurrentGroundSHA256=gsha,completeOriginalFaceComparisons=faces,failedFacesRetained=failed,completeOriginalFaceCount=n,completeCapturedGroundFacets=len(ground),currentGroundRootAccepted=False,physicalAccepted=False)
   rows.append(row);save(LOCAL/('completed-'+uid.split('/')[1].replace(':','-')+'-'+mode+'.json.gz'),row);print(json.dumps(dict(uid=uid,arithmetic=mode,rawFailedFaces=failed)),flush=True)
  assert len(item['completeWorldStreams'])==4
 save(DOC/'diagnostic.json.gz',dict(uids=UIDS,rows=rows,sourceCensusReceipt=read(SOURCE/'result.json')['jobId'],allCompleteFacetsAndCapturedFiniteGroundPreserved=True,installedPodiumIsNotReapproved=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 for n in ['exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_triangle_pair_column_gap_20261010.py']:refs.append(HERE/n)
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');refs.append(DOC/'diagnostic.json.gz')
 s=importlib.util.spec_from_file_location('heya_current_finite_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=m.freeze(BATCH,'heya-whole-two-original-four-stream-current-finite-diagnostic-no-role-credit',refs,dict(uids=UIDS,completeSourceFaces=COUNTS,currentAcceptance=False,physicalAccepted=False))
 print(json.dumps(dict(jobId=r['jobId'],currentAcceptance=False)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 for folder in [INPUT,SOURCE]:
  for pin in read(folder/'result.json')['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 claim=reservations.claim('heya-complete-current-finite-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
