"""Complete908 source components and exact positive-dimensional interfaces.

Inclusive whole-component AABBs only nominate pairs; every nominated primitive
pair uses the established exact kernel. No point or collapsed-face root glue.
The four low original groups are candidate anchors, not granted ground roots.
"""
import importlib.util,json,sys,uuid,subprocess,time
from collections import deque
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID,SOURCE_SHA
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_shared_edge_component_census_v2_20261011 import census
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
TOPO=BASE/'government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011'
BATCH='government-xl-king-cheung-95691-complete908-source-component-interfaces-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,TOPO]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 capture=read(INPUT/'complete-current-actual-source-and-ground.json.gz');data=read(INPUT/'complete-four-stream-ground-inputs.json.gz')
 assert data['uid']==UID and data['sourceSHA256']==SOURCE_SHA
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==capture['inputHashes']['3d-viewer/city/data/manifest.json']
 frozen=read(TOPO/'diagnostic.json.gz')['completeTopology'];rows=[];cache={}
 for mode,stream in data['completeWorldStreams'].items():
  world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');sha=digest(world.tobytes());assert world.shape==(18742,3,3)and sha==stream['completeWorldTriangleSHA256']
  if sha not in cache:
   topology=census(world);parts=topology['sharedEdgeConnectedComponents'];assert len(parts)==908
   if mode=='providerOriginal':assert topology==frozen
   lows=np.asarray([world[p].min((0,1))for p in parts]);highs=np.asarray([world[p].max((0,1))for p in parts]);pairs=[];tested=0;clock=time.monotonic();candidates=0
   for i in range(908):
    nominated=[int(j)for j in np.flatnonzero(np.all(highs>=lows[i],axis=1)&np.all(lows<=highs[i],axis=1))if j>i]
    for j in nominated:
     candidates+=1;contact=exact_finite_contacts(world,parts[i],world,parts[j],maximum_pairs=len(parts[i])*len(parts[j]));assert contact['allPairsExamined']and contact['sourceFacesOmitted']==0
     tested+=contact['trianglePairsTested']
     positive=[c for c in contact['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
     pairs.append(dict(originalComponentA=i,originalComponentB=j,completePrimitiveContactInventory=contact,
                       actualPositiveDimensionalRealFacetContactCount=len(positive),positiveSourceInterfacePresent=bool(positive)))
    if time.monotonic()-clock>20:print(json.dumps(dict(arithmetic=mode,completedComponents=i,totalComponents=908,exactPairs=tested)),flush=True);clock=time.monotonic()
   graph={i:set()for i in range(908)}
   for p in pairs:
    if p['positiveSourceInterfacePresent']:a,b=p['originalComponentA'],p['originalComponentB'];graph[a].add(b);graph[b].add(a)
   anchors=[34,39,43,44];paths={i:[i]for i in anchors};queue=deque(anchors)
   while queue:
    i=queue.popleft()
    for j in sorted(graph[i]):
     if j not in paths:paths[j]=paths[i]+[j];queue.append(j)
   collapsed=topology['exactNonrenderingOriginalFaces'];nonrendering_contacts=None
   if collapsed:
    nonrendering_contacts=exact_finite_contacts(world,collapsed,world,topology['completeRenderableFaceIds'],maximum_pairs=len(collapsed)*len(topology['completeRenderableFaceIds']));assert nonrendering_contacts['allPairsExamined']and nonrendering_contacts['sourceFacesOmitted']==0
   cache[sha]=dict(completeOriginalTopology=topology,completeOriginalComponentBounds=[dict(component=i,completeFaceIds=parts[i],worldBounds=[lows[i].tolist(),highs[i].tolist()])for i in range(908)],
                   completePossibleComponentPairs=908*907//2,completeInclusiveBoundNominatedPairs=candidates,
                   everyNominatedPairPrimitiveInventory=pairs,allStrictlyDisjointComponentPairsExcludedByCompleteExactBounds=True,
                   completeNonrenderingPrimitiveContacts=nonrendering_contacts,nonrenderingFacesRetainedInWholeFiniteAndRuntimeProof=True,
                   exactPositiveInterfacePairCount=sum(p['positiveSourceInterfacePresent']for p in pairs),
                   candidateAnchorGroups=anchors,sourceInterfacePathsFromUnapprovedAnchors=[dict(component=i,originalComponentPath=paths[i])for i in sorted(paths)],
                   componentsWithoutCandidateSourcePath=[i for i in range(908)if i not in paths],groundRootsAccepted=False,
                   noPointOrDegenerateGraphCredit=True,physicalAccepted=False)
  if mode=='providerOriginal':assert cache[sha]['completeOriginalTopology']==frozen
  rows.append(dict(arithmetic=mode,completeWorldSHA256=sha,**cache[sha]))
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,completeWholeOriginalFaces=18742,rows=rows,
      sourceGeometryChanges=0,terrainGeometryChanges=0,allOriginalAndActualWorldsExplicit=True,currentAcceptance=False,
      noFunctionOrLoadBearingInference=True,structuralSupportAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs +=[HERE/n for n in ['king_cheung_complete_ancillary_proposal_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','test_exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py']]
 s=importlib.util.spec_from_file_location('king_whole908_graph_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=m.freeze(BATCH,'complete908-original-and-current-world-component-interfaces-no-point-or-root-credit',refs+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeOriginalFaces=18742,completeOriginalComponents=908,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=r['jobId'],unreached={r['arithmetic']:len(r['componentsWithoutCandidateSourcePath'])for r in rows})),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('king-cheung-whole908-interfaces-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
