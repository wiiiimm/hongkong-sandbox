"""Unexecuted actual T/P interface and genuine installed-P grade diagnosis.
Unchanged exact shared-nonzero-edge/contact kernels. Provider-original complete
census is reused only byte-identically; actual worlds receive independent exact
censuses, whole T/P pair contacts and every P/finite-ground contact. No root claim.
"""
import importlib.util,json,sys,subprocess,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011';SOURCE=BASE/'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
BATCH='government-xl-heya-aqua-184286-184285-current-four-world-interfaces-grade-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
T,P='landsd/184286:0','landsd/184285:0';COUNTS={T:17910,P:3844}
HELPERS=['exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py']
def contacts(a,ids_a,b,ids_b):
 r=exact_finite_contacts(a,ids_a,b,ids_b,maximum_pairs=len(ids_a)*len(ids_b));assert r['allPairsExamined']and r['sourceFacesOmitted']==0;return r
def positive(r):return[c for c in r['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]+[HERE/h for h in HELPERS];pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,SOURCE]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for pin in receipt['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p);pins[pin['path']]=pin['sha256']
 data=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];prior=read(SOURCE/'diagnostic.json.gz');assert set(data)=={T,P}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)=='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
 ground=np.asarray(data[P]['completeDrawnGround'],dtype='<f8');assert digest(ground.tobytes())==data[P]['completeDrawnGroundSHA256'];rows=[]
 for mode in ['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']:
  worlds={};topologies={}
  for uid in [T,P]:
   stream=data[uid]['completeWorldStreams'][mode];w=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert w.shape==(COUNTS[uid],3,3)and np.isfinite(w).all()and digest(w.tobytes())==stream['completeWorldTriangleSHA256'];worlds[uid]=w
   if mode=='providerOriginal':
    assert digest(w.tobytes())==prior['actors'][uid]['sourceTuple']['worldSHA256'];topologies[uid]=prior['actors'][uid]['completeOriginalTopology']
   else:topologies[uid]=census(w,list(range(COUNTS[uid])))
  component_of={uid:{face:part for part,ids in enumerate(topologies[uid]['sharedEdgeConnectedComponents'])for face in ids}for uid in [T,P]}
  if mode=='providerOriginal':cross=prior['completeTowerToPodiumPrimitiveInterfaces']
  else:cross=contacts(worlds[T],list(range(COUNTS[T])),worlds[P],list(range(COUNTS[P])))
  assert cross['allPairsExamined']and cross['sourceFacesOmitted']==0
  grade=contacts(worlds[P],list(range(COUNTS[P])),ground,list(range(len(ground))))
  cross_records=[dict(**c,towerComponent=component_of[T].get(c['sourceFaceA']),podiumComponent=component_of[P].get(c['sourceFaceB']))for c in cross['contacts']]
  grade_records=[dict(**c,podiumComponent=component_of[P].get(c['sourceFaceA']))for c in grade['contacts']]
  row=dict(arithmetic=mode,completeWorldHashes={uid:digest(w.tobytes())for uid,w in worlds.items()},completeActualTopologies=topologies,completeTowerToInstalledPodiumPrimitiveInterfaces=cross,allCrossPrimitiveRecordsWithRealComponentBindings=cross_records,positiveRealFacetCrossInterfaces=len(positive(cross)),completePodiumToGroundPrimitiveInventory=grade,allGroundPrimitiveRecordsWithRealComponentBindings=grade_records,positiveRealFacetGradeContacts=len(positive(grade)),completePodiumGroundSHA256=digest(ground.tobytes()),noZeroOrPointBridgeCredit=True,currentRootAccepted=False,physicalAccepted=False)
  rows.append(row);save(LOCAL/('completed-'+mode+'.json.gz'),row);print(json.dumps(dict(arithmetic=mode,positiveCross=len(positive(cross)),positiveGrade=len(positive(grade)),actualComponents={u:len(topologies[u]['sharedEdgeConnectedComponents'])for u in [T,P]},currentRootAccepted=False)),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uids=[T,P],rows=rows,rawTwoResidualRimFailuresRetained=prior['rawTwoResidualRimFailuresRetained'],residualSourceIncidences=prior['residualSourceIncidences'],providerOriginalCensusReusedOnlyExactByteBound=True,allCurrentGroundAndRealFacetContactsPreserved=True,installedPodiumNotReapproved=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');refs.append(DOC/'diagnostic.json.gz')
 spec=importlib.util.spec_from_file_location('heya_actual_interface_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'heya-four-world-complete-T-P-interface-and-P-grade-primitive-diagnostic',refs,dict(uids=[T,P],sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False));print(json.dumps(dict(jobId=result['jobId'],currentAcceptance=False)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 for folder in [INPUT,SOURCE]:
  for pin in read(folder/'result.json')['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 claim=reservations.claim('heya-four-world-interfaces-grade-'+str(uuid.uuid4()),['building:'+u for u in [T,P]],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
