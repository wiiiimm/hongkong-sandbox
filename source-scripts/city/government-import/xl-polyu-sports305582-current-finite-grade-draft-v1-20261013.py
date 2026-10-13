"""UNEXECUTED complete Sports finite/grade diagnostic; no roots or acceptance."""
import importlib.util,json,subprocess,sys,uuid
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';DRAFT=BASE/'government-xl-polyu-sports305582-current-finite-grade-draft-v1-20261013'
INPUT=BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013'
BATCH='government-xl-polyu-sports305582-current-finite-grade-v1-20261013';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UID='landsd/305582:0';PODIUM='landsd/305793:0';SOURCE='ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15';MANIFEST='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
def normal(face):
 p,q,r=[[F.from_float(float(x))for x in v]for v in face];u=[q[i]-p[i]for i in range(3)];v=[r[i]-p[i]for i in range(3)]
 return [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
def preflight():
 assert not DOC.exists();contract=read(DRAFT/'input-contract.json');refs=[Path(__file__),DRAFT/'METHOD.md',DRAFT/'input-contract.json',DRAFT/'southside-finite-template.diff'];pins={}
 for pin in contract['filePins']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'],pin['path'];refs.append(p);pins[pin['path']]=pin['sha256']
 receipt=read(INPUT/'result.json');assert receipt['jobId']=='74fc230cb2ea65e352f2d47ec20440f455bc6ae428158ba68472ab528a37bf5e'and not receipt['currentAcceptance']and not receipt['physicalAccepted']
 before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert digest(before)==MANIFEST and before==(INPUT/'captured-manifest.json').read_bytes()
 data=read(INPUT/'complete-sports-four-stream-current-ground-inputs.json.gz');capture=read(INPUT/'capture-inputs.json.gz');raw=read(INPUT/'complete-current-actual-source-and-ground-305582-0.json.gz')
 assert data['uid']==UID and data['sourceSHA256']==SOURCE and set(data['completeWorldStreams'])==set(MODES)and data['unrelated235076And114494SupportNotTransferred']is True
 assert capture['manifestSHA256']==MANIFEST and capture['installedPodiumDependency']['entry']['uid']==PODIUM and capture['installedPodiumDependency']['entry']['publicationApproved']is False and capture['installedPodiumDependency']['publicationHoldPreserved']is True
 forms=capture['completeCurrentForms'];assert len(forms)==12 and len({f['uid']for f in forms})==12
 resources=sorted(set([('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms]+['terrain-patch:'+UID]));assert len(resources)==13
 for u in [UID,PODIUM,'landsd/72322:0','landsd/258852:0','landsd/305600:0']:assert u in {f['uid']for f in forms}
 ground=np.asarray(data['completeDrawnGround'],dtype='<f8');gsha=digest(ground.tobytes());assert ground.shape==(12,3,3)and np.isfinite(ground).all()and gsha==data['completeDrawnGroundSHA256']==raw['currentDrawnGround']['worldTriangleSHA256']
 assert ground.tolist()==np.asarray(raw['currentDrawnGround']['completeRegionalPosition'],dtype='<f8').reshape(-1,3,3).tolist()and raw['startAndEndInputsVerified']is True
 topology=data['completeOriginalTopologyVerbatim'];assert topology['completeOriginalFaceIds']==list(range(10536))and len(topology['sharedEdgeConnectedComponents'])==21 and len(topology['exactNonrenderingOriginalFaces'])==4
 assert sorted([i for part in topology['sharedEdgeConnectedComponents']for i in part]+topology['exactNonrenderingOriginalFaces'])==list(range(10536))
 worlds={}
 for mode in MODES:
  stream=data['completeWorldStreams'][mode];w=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert w.shape==(10536,3,3)and stream['completeFaces']==10536 and np.isfinite(w).all()and digest(w.tobytes())==stream['completeWorldTriangleSHA256'];worlds[mode]=w
 assert digest(worlds['providerOriginal'].tobytes())==contract['providerOriginalWorldSHA256']
 for p in refs:pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 assert(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 return dict(receipt=receipt,refs=refs,pins=pins,before=before,data=data,capture=capture,ground=ground,groundSHA=gsha,worlds=worlds,resources=resources)
def owned(s):
 lease=read(LEASE);assert lease['resources']==s['resources']and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(s['receipt']['jobId'],)).fetchone()==('complete',s['receipt'])
 rows=[];cache={}
 for mode in MODES:
  world=s['worlds'][mode];topology=s['data']['completeOriginalTopologyVerbatim']if mode=='providerOriginal'else census(world,list(range(10536)));zeros=set(topology['exactNonrenderingOriginalFaces']);records=[]
  for i,face in enumerate(world):
   fsha=digest(face.tobytes());key=(fsha,s['groundSHA'])
   if key not in cache:
    a=coarse(face,s['ground']);b=None if a['existingOrdinaryClearanceBoundProved']else paired(face,s['ground']);cache[key]=dict(coarse=a,paired=b,completeFiniteOrdinaryBoundProved=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved'])))
   n=normal(face);label='zero-area'if i in zeros else('steep-wall'if 16*n[1]*n[1]<=sum(x*x for x in n)else('upward-nonsteep'if n[1]>0 else'downward-or-sloping-nonsteep'))
   records.append(dict(sourceFace=i,completeOriginalFacetSHA256=fsha,exactOrientationDiagnostic=label,currentDrawnGroundComparison=cache[key]))
   if i%2000==0:print(json.dumps(dict(arithmetic=mode,completedSourceFaces=i)),flush=True)
  grade=exact_finite_contacts(world,list(range(10536)),s['ground'],list(range(12)),maximum_pairs=10536*12);assert grade['allPairsExamined']and grade['sourceFacesOmitted']==0
  failed=[r['sourceFace']for r in records if not r['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']]
  row=dict(uid=UID,arithmetic=mode,sourceSHA256=SOURCE,completeWholeWorldSHA256=digest(world.tobytes()),completeCurrentGroundSHA256=s['groundSHA'],completeOriginalFaceCount=10536,completeCapturedGroundFacets=12,completeOriginalTopology=topology,completeOriginalFaceComparisons=records,failedFacesRetained=failed,completeAllOriginalPrimitiveGradeContacts=grade,positiveDimensionalRealFacetGradeContacts=[q for q in grade['contacts']if q['dimension']>0 and q['sourcePrimitiveDimensionA']==q['sourcePrimitiveDimensionB']==2],allZeroFacesUncredited=sorted(zeros),allGroundAndPointContactsRetainedWithoutRootCredit=True,currentGroundRootAccepted=False,currentAcceptance=False,physicalAccepted=False)
  rows.append(row);save(LOCAL/('completed-'+mode+'.json.gz'),row);print(json.dumps(dict(arithmetic=mode,rawFailures=len(failed),measuredBodies=len(topology['sharedEdgeConnectedComponents']),zeros=len(zeros),allPrimitiveGradeContacts=len(grade['contacts']))),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],rows=rows,currentCaptureReceipt=s['receipt']['jobId'],fullSourceSlots=42144,installedPodiumDependencyVerbatim=s['capture']['installedPodiumDependency'],all12CurrentFormsVerbatim=s['capture']['completeCurrentForms'],noHistorical235076Or114494ProofTransfer=True,noNormalAsArchitecturalFunction=True,noPointZeroOrContactRootCredit=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==s['before']
 for p,h in s['pins'].items():assert digest((ROOT/p).read_bytes())==h,p
 refs=s['refs']+[DOC/'diagnostic.json.gz']+[p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json'];spec=importlib.util.spec_from_file_location('polyu_finite_grade_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 out=m.freeze(BATCH,'sports-complete-current-finite-and-original-grade-no-role-credit',refs,dict(uids=[UID],completeSourceFaces=10536,sourceWorldSlots=42144,currentNatives=6650,nativePublicationHoldPreserved=True,currentAcceptance=False,physicalAccepted=False));print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)
def main():
 s=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noDB=True,noLease=True,noFiniteOrGradePredicatesRun=True,sourceFaces=10536,sourceSlots=42144,providerOriginalBodies=21,providerOriginalZeros=4,currentGroundFacets=12,currentForms=12,canonicalResources=s['resources'],currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return owned(s)
 assert not LOCAL.exists();claim=reservations.claim('polyu-sports-finite-grade-'+str(uuid.uuid4()),s['resources'],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
