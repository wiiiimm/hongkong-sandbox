"""DRAFT: actual T4/P0 exposed path and complete attached tower account.

Reuse provider original census exactly. Other actual worlds independently test
every closed-bounds-nominated tower component pair. Only positive real-facet
interfaces connect the attached source envelope; the named58 terminal visuals
are a separate nonstructural interpretation. No current acceptance or publishing.
"""
import importlib.util,json,subprocess,sys,uuid
from collections import deque
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from heya_aqua_current_exposed_grade_path_20261011 import verify,positive,T,P
from heya_aqua_58_original_terminal_visual_placement_20261011 import NAMED
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

BASE=ROOT/'docs/astra-city/government-import'
ACTUAL=BASE/'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011'
SOURCE=BASE/'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
FINITE=BASE/'government-xl-heya-aqua-184286-184285-complete-four-stream-current-finite-v1-20261011'
INTERFACE=BASE/'government-xl-heya-aqua-184286-184285-current-four-world-interfaces-grade-v1-20261011'
VISUAL=BASE/'government-xl-heya-aqua-58-original-terminal-visual-placement-proposal-v1-20261011'
VALIDATION=BASE/'government-xl-heya-aqua-current-grade-path-validation-v1-20261011'
BATCH='government-xl-heya-aqua-current-main-family-exposed-root-account-v1-20261011'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
HELPERS=['heya_aqua_current_exposed_grade_path_20261011.py',
 'test_heya_aqua_current_exposed_grade_path_20261011.py',
 'heya_aqua_58_original_terminal_visual_placement_20261011.py',
 'exact_original_rational_interface_segment_clearance_20261011.py',
 'exact_original_finite_triangle_contacts_20261010.py',
 'exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py']

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 validation=read(VALIDATION/'validation.json')
 assert validation['allPassed'] and validation['testsRun']==12
 codes=[Path(__file__)]+[HERE/h for h in HELPERS]
 assert validation['codeHashes']=={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in codes}
 refs=codes+[VALIDATION/'validation.json'];pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in codes}
 for r in validation['evidenceRefs']:
  assert digest((ROOT/r['path']).read_bytes())==r['sha256'];refs.append(ROOT/r['path']);pins[r['path']]=r['sha256']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [ACTUAL,SOURCE,FINITE,INTERFACE,VISUAL]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   refs.append(folder/'result.json')
   for pin in receipt['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p);pins[pin['path']]=pin['sha256']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
 assert digest(before)=='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
 data=read(ACTUAL/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows']
 original=read(SOURCE/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz')
 interfaces=read(INTERFACE/'diagnostic.json.gz');visual=read(VISUAL/'proposal.json.gz')
 assert visual['completeNamedTerminalComponents']==NAMED and len(visual['completeNamedTerminalFaces'])==1312
 assert not visual['structuralRootCredit']and not visual['structuralBridgeCredit']and not visual['loadBearingClaim']
 rows=[];cache={}
 for mode in MODES:
  item=next(r for r in interfaces['rows']if r['arithmetic']==mode)
  worlds={u:np.asarray(data[u]['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8')for u in [T,P]}
  for u,w in worlds.items():
   assert digest(w.tobytes())==item['completeWorldHashes'][u]==data[u]['completeWorldStreams'][mode]['completeWorldTriangleSHA256']
  parts={u:item['completeActualTopologies'][u]['sharedEdgeConnectedComponents']for u in [T,P]}
  assert len(parts[T])==574 and len(parts[P])==34
  for u in [T,P]:
   assert parts[u]==original['actors'][u]['completeOriginalTopology']['sharedEdgeConnectedComponents']
   assert item['completeActualTopologies'][u]['exactNonrenderingOriginalFaces']==[]
  ground={u:np.asarray(data[u]['completeDrawnGround'],dtype='<f8')for u in [T,P]}
  assert float(worlds[T].min((0,1))[1])>float(ground[T].max((0,1))[1])
  for u in [T,P]:
   f=next(r for r in finite['rows']if r['uid']==u and r['arithmetic']==mode)
   assert f['completeWholeWorldSHA256']==digest(worlds[u].tobytes())and f['completeCurrentGroundSHA256']==digest(ground[u].tobytes())and f['failedFacesRetained']==[]
  root=verify(world=worlds[P],ground=ground[P],parts=parts[P],
   grade_records=item['allGroundPrimitiveRecordsWithRealComponentBindings'],
   cross_records=item['allCrossPrimitiveRecordsWithRealComponentBindings'],
   finite_row=next(r for r in finite['rows']if r['uid']==P and r['arithmetic']==mode))
  graph={i:set()for i in range(574)};pairs=[];w=worlds[T];wsha=digest(w.tobytes())
  bounds=[(w[ids].min((0,1)),w[ids].max((0,1)))for ids in parts[T]]
  expected=[]
  for i,(lo,hi)in enumerate(bounds):
   for j in range(i+1,len(bounds)):
    other_lo,other_hi=bounds[j]
    if np.all(hi>=other_lo)and np.all(other_hi>=lo):expected.append((i,j))
  prior={(p['componentA'],p['componentB']):p for p in original['everyBoundsNominatedWithinActorComponentPair']if p['uid']==T}
  for i,j in expected:
   if mode=='providerOriginal':r=prior[(i,j)]['completePrimitiveContactInventory']
   else:
    key=(wsha,i,j)
    if key not in cache:cache[key]=exact_finite_contacts(w,parts[T][i],w,parts[T][j],maximum_pairs=len(parts[T][i])*len(parts[T][j]))
    r=cache[key]
   assert r['allPairsExamined']and r['sourceFacesOmitted']==0
   contacts=[c for c in r['contacts']if positive(c)]
   if contacts:graph[i].add(j);graph[j].add(i)
   pairs.append(dict(componentA=i,componentB=j,completePrimitiveContactInventory=r,positiveRealFacetInterfaces=len(contacts)))
  if mode=='providerOriginal':assert set(expected)==set(prior)
  reachable={4};parent={4:None};queue=deque([4])
  while queue:
   current=queue.popleft()
   for node in sorted(graph[current]):
    if node not in reachable:reachable.add(node);parent[node]=current;queue.append(node)
  expected_attached=set(range(574))-set(NAMED)
  unaccounted=sorted(expected_attached-reachable);assert not reachable&set(NAMED)
  assert reachable==expected_attached,('Actual attached source family differs',mode,unaccounted)
  row=dict(arithmetic=mode,completeWorldHashes=item['completeWorldHashes'],
   originalExposedGradeToT4Path=root,completeWithinTowerBoundsNominatedPairs=pairs,
   allExcludedWithinTowerPairsStrictWholeBoundsDisjoint=True,
   completeAttachedTowerComponents=sorted(reachable),componentParentFromT4={str(k):v for k,v in parent.items()},
   completeAttachedTowerFaceIds=sorted(i for k in reachable for i in parts[T][k]),
   completeNamed58Components=NAMED,completeNamed58FaceIds=visual['completeNamedTerminalFaces'],
   allCompleteSourceFacesAccounted=17910,engineeringSupportCertified=False,
   terminalVisualsNeverProvideRootOrBridge=True,currentAcceptance=False)
  assert len(row['completeAttachedTowerFaceIds'])==16598
  assert sorted(row['completeAttachedTowerFaceIds']+row['completeNamed58FaceIds'])==list(range(17910))
  rows.append(row);save(LOCAL/('completed-'+mode+'.json.gz'),row)
  print(json.dumps(dict(arithmetic=mode,attachedComponents=len(reachable),terminalVisuals=58,exposedOriginalPath=True)),flush=True)
 save(DOC/'proposal.json.gz',dict(uids=[T,P],rows=rows,
  rawTwoResidualRimFailuresRetained=original['rawTwoResidualRimFailuresRetained'],
  completeNamed58ProviderPlacementProof=visual,installedPodiumReapproved=False,
  sourceGeometryChanges=0,terrainGeometryChanges=0,engineeringSupportCertified=False,
  sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,currentAcceptance=False,installationApproved=False))
 assert manifest.read_bytes()==before and reservations.owns(lease)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');refs.append(DOC/'proposal.json.gz')
 spec=importlib.util.spec_from_file_location('heya_exposed_main_family_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'heya-complete-actual-attached-source-family-and-exposed-P0-grade-path-proposal',refs,dict(uids=[T,P],currentAcceptance=False,installationApproved=False))
 print(json.dumps(dict(jobId=result['jobId'],currentAcceptance=False)),flush=True)

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 claim=reservations.claim('heya-actual-main-family-'+str(uuid.uuid4()),['building:'+u for u in [T,P]],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
