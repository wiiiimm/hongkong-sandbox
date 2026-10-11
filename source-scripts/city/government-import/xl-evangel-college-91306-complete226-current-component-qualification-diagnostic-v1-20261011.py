"""Complete 226-component current qualification diagnostic, no typed acceptance.

216 conditional envelope bodies, five independently standing bodies and five
nonstructural visual candidates partition every real source component. All33
zero-area records remain in whole finite/runtime proofs and provide no bridge.
Uses unchanged ordinary footing and .1m complete finite boundary host kernels.
"""
import importlib.util,json,sys,uuid,subprocess
from collections import deque
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from evangel_college_original_wing_extension_identity_20261011 import UID,SOURCE_SHA
from evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011 import source_proposal_pin_path
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011'
GRAPH=BASE/'government-xl-evangel-college-91306-complete226-source-component-interfaces-v1-20261011'
PHYSICAL=BASE/'government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011'
FINITE=BASE/'government-xl-evangel-college-91306-complete13960-preserved-candidate-finite-diagnostic-v2-20261011'
GRADE=BASE/'government-xl-evangel-college-91306-current-four-body-grade-paths-v3-20261011'
BATCH='government-xl-evangel-college-91306-complete226-current-component-qualification-diagnostic-v1-20261011'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
VISUAL=[28,29,30,221,222];STANDING=[62,90,98,99,100]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
# Exact existing closed-loop/exhaustive host nomination policy, no King roles.
BOUNDARY_PATH=HERE/'xl-king-cheung-95691-complete191-detached-boundary-mount-diagnostic-v2-20261011.py'
boundary_policy=module('evangel_existing_boundary_census',BOUNDARY_PATH)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__),BOUNDARY_PATH]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,GRAPH,PHYSICAL,FINITE,GRADE]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for pin in receipt['evidenceRefs']:
    p=source_proposal_pin_path(pin)if folder in [INPUT,GRAPH]else ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');graph=read(GRAPH/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz');grade=read(GRADE/'diagnostic.json.gz')
 runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path);assert len(runtime['rows'])==1 and runtime['rows'][0]['uid']==UID;refs.append(runtime_path)
 ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);groundsha=digest(ground.tobytes());assert groundsha==finite['completeGrounds']['currentDrawn']['completeWorldSHA256']==grade['completeActualCandidateGroundSHA256']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==runtime['inputHashes']['3d-viewer/city/data/manifest.json']and data['sourceSHA256']==SOURCE_SHA
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 assert read(PHYSICAL/'diagnostic.json.gz')['all17CurrentActorGuardsRetained']
 rows=[];cache={}
 for mode,stream in data['completeWorldStreams'].items():
  world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');sha=digest(world.tobytes());assert world.shape==(13960,3,3)and sha==stream['completeWorldTriangleSHA256']
  g=next(r for r in graph['rows']if r['arithmetic']==mode);f=next(r for r in finite['rows']if r['arithmetic']==mode);r=next(r for r in grade['rows']if r['arithmetic']==mode);assert g['completeWorldSHA256']==f['completeWholeWorldSHA256']==r['completeWorldSHA256']==sha
  topology=census(world,list(range(13960)));assert topology==g['completeOriginalTopology'];parts=topology['sharedEdgeConnectedComponents'];assert len(parts)==226 and len(topology['exactNonrenderingOriginalFaces'])==33
  records=f['complete13960FaceComparisons'];excluded=set(VISUAL+STANDING);envelope=sorted(set(range(226))-excluded);assert len(envelope)==216
  downward=set(r['rawDownwardFacesRetainedAsUncredited']);assert len(downward)==22
  adjacency={i:set()for i in envelope};edge_records=[]
  for pair in g['everyNominatedPairPrimitiveInventory']:
   a,b=pair['originalComponentA'],pair['originalComponentB']
   if a not in adjacency or b not in adjacency:continue
   eligible=[contact for contact in pair['completePrimitiveContactInventory']['contacts']if contact['dimension']>0 and contact['sourcePrimitiveDimensionA']==contact['sourcePrimitiveDimensionB']==2 and contact['sourceFaceA']not in downward and contact['sourceFaceB']not in downward]
   if eligible:adjacency[a].add(b);adjacency[b].add(a);edge_records.append(dict(originalComponentA=a,originalComponentB=b,completeEligibleOriginalContacts=eligible))
  # Deterministic BFS with explicit parent, no point/zero/down bridge.
  paths={13:[13]};queue=deque([13])
  while queue:
   i=queue.popleft()
   for j in sorted(adjacency[i]):
    if j not in paths:paths[j]=paths[i]+[j];queue.append(j)
  conditional_hosts=sorted(i for component in envelope for i in parts[component]if i not in downward)
  assert not set(conditional_hosts)&{i for c in VISUAL+STANDING for i in parts[c]}
  if sha not in cache:
   visual=[]
   for component in VISUAL:
    ids=parts[component];inv,edges,incidences,loops=boundary_policy.boundary(world,ids);near,far=boundary_policy.nearby_hosts(world,ids,conditional_hosts);proofs=[]
    for index,edge in enumerate(edges):
     trials=[dict(coordinatePermutation=perm,completeFiniteHostBandProof=edge_band(np.asarray(edge,dtype='<f8')[:,perm],world[near][:,:,perm]))for perm in [[0,1,2],[1,0,2],[0,2,1]]]if near else []
     proofs.append(dict(originalBoundaryEdgeIndex=index,completeOriginalEdge=[list(v)for v in edge],completeCoordinatePermutationTrials=trials,fullEdgeAssociated=any(p['completeFiniteHostBandProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for p in trials),emptyHostScopeExplicitlyUnqualified=not near))
    assert all(records[i]['groundComparisons']['currentDrawn']['completeFiniteOrdinaryBoundProved']for i in ids)
    visual.append(dict(originalComponent=component,completeOriginalFaces=ids,completeOriginalComponentCensus=inv,completeOriginalEdgeIncidences=incidences,completeEveryOriginalClosedBoundaryLoop=[[[list(v)for v in e]for e in loop]for loop in loops],completeBoundaryEdgeFiniteHostBandProofs=proofs,completeHostCandidateFaceIds=near,strictlyOutsideUnchangedBandHostFaces=far,completeBoundaryAssociated=all(p['fullEdgeAssociated']for p in proofs),allOriginalFacetsOrdinaryClear=True,nonstructuralVisualInterpretationApproved=False,structuralRootCredit=False,structuralBridgeCredit=False))
   standing=[]
   for component in STANDING:
    ids=parts[component];t=world[ids];input_path=LOCAL/('footing-'+mode+'-'+str(component)+'.json.gz');save(input_path,dict(arithmetic=mode,part=dict(component=component,originalFaceIds=ids,position=t.reshape(-1).tolist(),index=list(range(len(t)*3)),bottomHKPD=float(t[:,:,1].min())),terrain=dict(position=ground.reshape(-1).tolist(),index=list(range(len(ground)*3))),physicalAccepted=False));refs.append(input_path)
    footing=json.loads(subprocess.check_output(['node',str(HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs'),str(input_path)],cwd=ROOT));contacts=exact_finite_contacts(world,ids,ground,range(len(ground)),maximum_pairs=len(ids)*len(ground));assert contacts['allPairsExamined']and contacts['sourceFacesOmitted']==0
    standing.append(dict(originalComponent=component,completeOriginalFaces=ids,completeOriginalGeometry=t.tolist(),completeOriginalBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],completeOrdinaryFootingVerbatim=footing,completeOriginalGroundContactInventory=contacts,completeCurrentFiniteFacetRows=[records[i]for i in ids],allOriginalFacetsOrdinaryClear=all(records[i]['groundComparisons']['currentDrawn']['completeFiniteOrdinaryBoundProved']for i in ids),independentGroundRootAccepted=False,sourceGeometryChanges=0))
   cache[sha]=dict(complete216ConditionalEnvelopeComponents=envelope,completeEligibleEnvelopeInterfaceInventory=edge_records,completeConditionalEnvelopeSourcePaths=[dict(originalComponent=i,originalComponentPath=paths[i])for i in sorted(paths)],unresolvedEnvelopeComponents=sorted(set(envelope)-set(paths)),completeConditionalHostFaceIds=conditional_hosts,completeFiveVisualDispositions=visual,completeFiveStandingDispositions=standing,all33ZeroFacesRetainedAndUncredited=topology['exactNonrenderingOriginalFaces'],all226RealComponentsPartitionedExactly=True,sourceOnly=True,currentAcceptance=False,physicalAccepted=False)
  rows.append(dict(arithmetic=mode,completeWorldSHA256=sha,**cache[sha]));save(LOCAL/('completed-'+mode+'.json.gz'),dict(row=rows[-1],completeActualGroundSHA256=groundsha));print(json.dumps(dict(arithmetic=mode,envelopeUnresolved=rows[-1]['unresolvedEnvelopeComponents'],visualUnresolved=[x['originalComponent']for x in rows[-1]['completeFiveVisualDispositions']if not x['completeBoundaryAssociated']],footings={x['originalComponent']:x['completeOrdinaryFootingVerbatim']['passed']for x in rows[-1]['completeFiveStandingDispositions']})),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,completeActualGroundSHA256=groundsha,currentManifestSHA256=digest(before),fixedFiniteVisualBandM=.1,all13960OriginalFacetsRetained=True,completeComponentPartition=dict(conditionalEnvelope=216,standing=5,visualCandidates=5,zeroFaces=33),currentAcceptance=False,physicalAccepted=False,newlyInstalled=0,qualification='Conditional source connectivity is not structural certification; visuals provide no root or bridge. Every ordinary footing/finite failure remains verbatim; no role acceptance or terrain/source change.'))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(HERE/n for n in ['exact_original_shared_edge_component_census_v2_20261011.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_finite_triangle_contacts_20261010.py','xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs','support-interface.mjs','support-contact.mjs','triangle-point-index.mjs']);refs.append(DOC/'diagnostic.json.gz');refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 freezer=module('evangel226_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');result=freezer.freeze(BATCH,'complete226-current-component-footing-and-finite-visual-boundary-diagnostic',refs,dict(uids=[UID],currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=result['jobId'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 claim=reservations.claim('evangel226-current-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
