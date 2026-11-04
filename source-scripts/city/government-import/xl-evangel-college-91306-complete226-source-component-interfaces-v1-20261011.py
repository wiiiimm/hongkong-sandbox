"""Complete original/current component interfaces; no ground or point roots.

Inclusive complete 3D bounds only nominate pairs. Every finite original pair
within those bounds is checked; exact area/nonzero-edge topology retains all
zero primitives without giving them structural graph credit.
"""
import importlib.util,json,sys,uuid,subprocess,time
from collections import deque
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from evangel_college_original_wing_extension_identity_20261011 import UID,SOURCE_SHA
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_shared_edge_component_census_v2_20261011 import census
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011';PROPOSAL=BASE/'government-xl-evangel-college-91306-original-wing-extension-proposal-v1-20261011';SOURCE=BASE/'government-xl-evangel-college-91306-western-original-patches-context-v1-20261011'
BATCH='government-xl-evangel-college-91306-complete226-source-component-interfaces-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,PROPOSAL]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 capture=read(INPUT/'complete-current-actual-source-and-ground.json.gz');data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');assert data['uid']==UID and data['sourceSHA256']==SOURCE_SHA
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==capture['inputHashes']['3d-viewer/city/data/manifest.json']
 frozen=read(SOURCE/'diagnostic.json.gz')['completeSourceTopology'];rows=[];cache={}
 for mode,stream in data['completeWorldStreams'].items():
  world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');sha=digest(world.tobytes());assert world.shape==(13960,3,3)and sha==stream['completeWorldTriangleSHA256']
  if sha not in cache:
   topology=census(world,list(range(len(world))));parts=topology['sharedEdgeConnectedComponents'];assert len(parts)==226
   if mode=='providerOriginal':assert topology==frozen
   lows=np.asarray([world[p].min((0,1))for p in parts]);highs=np.asarray([world[p].max((0,1))for p in parts]);pairs=[];tested=0;clock=time.monotonic();candidates=0
   for i in range(len(parts)):
    nominated=[int(j)for j in np.flatnonzero(np.all(highs>=lows[i],axis=1)&np.all(lows<=highs[i],axis=1))if j>i]
    for j in nominated:
     candidates+=1;contact=exact_finite_contacts(world,parts[i],world,parts[j],maximum_pairs=len(parts[i])*len(parts[j]));assert contact['allPairsExamined']and contact['sourceFacesOmitted']==0;tested+=contact['trianglePairsTested']
     positive=[c for c in contact['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
     pairs.append(dict(originalComponentA=i,originalComponentB=j,completePrimitiveContactInventory=contact,actualPositiveDimensionalRealFacetContactCount=len(positive),positiveSourceInterfacePresent=bool(positive)))
    if time.monotonic()-clock>20:print(json.dumps(dict(arithmetic=mode,completedComponents=i,totalComponents=len(parts),exactPairs=tested)),flush=True);clock=time.monotonic()
   graph={i:set()for i in range(len(parts))}
   for p in pairs:
    if p['positiveSourceInterfacePresent']:a,b=p['originalComponentA'],p['originalComponentB'];graph[a].add(b);graph[b].add(a)
   remaining=set(graph);families=[]
   while remaining:
    start=min(remaining);seen={start};queue=deque([start])
    while queue:
     for j in sorted(graph[queue.popleft()]):
      if j not in seen:seen.add(j);queue.append(j)
    remaining-=seen;families.append(sorted(seen))
   collapsed=topology['exactNonrenderingOriginalFaces'];zero_contacts=None
   if collapsed:
    zero_contacts=exact_finite_contacts(world,collapsed,world,topology['completeRenderableFaceIds'],maximum_pairs=len(collapsed)*len(topology['completeRenderableFaceIds']));assert zero_contacts['allPairsExamined']and zero_contacts['sourceFacesOmitted']==0
   cache[sha]=dict(completeOriginalTopology=topology,completeOriginalComponentBounds=[dict(component=i,completeFaceIds=parts[i],worldBounds=[lows[i].tolist(),highs[i].tolist()])for i in range(len(parts))],completePossibleComponentPairs=len(parts)*(len(parts)-1)//2,completeInclusiveBoundNominatedPairs=candidates,everyNominatedPairPrimitiveInventory=pairs,allStrictlyDisjointComponentPairsExcludedByCompleteExactBounds=True,completeNonrenderingPrimitiveContacts=zero_contacts,nonrenderingFacesRetainedInWholeFiniteAndRuntimeProof=True,exactPositiveInterfacePairCount=sum(p['positiveSourceInterfacePresent']for p in pairs),completePositiveInterfaceFamilies=families,groundRootsAccepted=False,noPointOrDegenerateGraphCredit=True,physicalAccepted=False)
  if mode=='providerOriginal':assert cache[sha]['completeOriginalTopology']==frozen
  rows.append(dict(arithmetic=mode,completeWorldSHA256=sha,**cache[sha]))
  save(LOCAL/('completed-mode-'+mode+'.json.gz'),dict(uids=[UID],sourceSHA256=SOURCE_SHA,completeInputHashes=capture['inputHashes'],sourceWorldRow=rows[-1],methodHashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in [Path(__file__),HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py']},checkpointOnly=True,currentAcceptance=False,groundRootsAccepted=False))
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,completeWholeOriginalFaces=13960,rows=rows,sourceGeometryChanges=0,terrainGeometryChanges=0,allOriginalAndActualWorldsExplicit=True,currentAcceptance=False,noFunctionOrLoadBearingInference=True,structuralSupportAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(HERE/n for n in ['evangel_college_original_wing_extension_identity_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','test_exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py']);refs.extend([SOURCE/'diagnostic.json.gz',DOC/'diagnostic.json.gz']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 s=importlib.util.spec_from_file_location('evangel_whole226_graph_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.freeze(BATCH,'complete226-original-and-current-world-component-interfaces-no-point-or-root-credit',refs,dict(uids=[UID],completeOriginalFaces=13960,completeOriginalComponents=226,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=r['jobId'],families={r['arithmetic']:len(r['completePositiveInterfaceFamilies'])for r in rows})),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('evangel-whole226-interfaces-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
