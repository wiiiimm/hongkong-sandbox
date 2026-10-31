"""Complete191 source-owned detached opening/perimeter association diagnostic.

Every original boundary edge is tested under the unchanged .1m finite host band.
No near point, functional label, structural root or visual-to-visual propagation.
The complete attached source envelope is a conditional host pending foundation.
"""
import importlib.util,json,sys,uuid,subprocess,time
from collections import defaultdict,Counter,deque
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID,SOURCE_SHA
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
from exact_original_shared_edge_component_census_v2_20261011 import census
def nearby_hosts(world,ids,hosts):
 lo=world[ids].min((0,1));hi=world[ids].max((0,1));near=[];excluded=[]
 for j in hosts:
  a=world[j].min(0);b=world[j].max(0);gaps=[max(F(float(lo[k]))-F(float(b[k])),F(float(a[k]))-F(float(hi[k])),F(0))for k in range(3)];lower=sum(v*v for v in gaps)
  if lower>F(.1)**2:excluded.append(dict(sourceFace=j,exactLowerSquaredDistance=str(lower)))
  else:near.append(j)
 assert len(near)+len(excluded)==len(hosts)
 return near,excluded
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
GRAPH=BASE/'government-xl-king-cheung-95691-complete908-source-component-interfaces-v2-20261011'
FINITE=BASE/'government-xl-king-cheung-95691-complete18742-current-finite-diagnostic-v1-20261011'
BATCH='government-xl-king-cheung-95691-complete191-detached-boundary-mount-diagnostic-v2-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def boundary(world,ids):
 inv=census(world,ids);assert inv['sharedEdgeConnectedComponents']==[ids]and not inv['exactNonrenderingOriginalFaces']and inv['nonmanifoldEdges']==inv['twoFaceOrientationConflicts']==0
 incidences=defaultdict(list)
 for i in ids:
  for a,b in zip(world[i],np.roll(world[i],-1,axis=0)):
   assert tuple(a)!=tuple(b);incidences[tuple(sorted((tuple(a),tuple(b))))].append(i)
 edges=sorted(e for e,rows in incidences.items()if len(rows)==1);assert len(edges)in [4,8]
 degree=Counter(v for e in edges for v in e);assert all(n==2 for n in degree.values())
 adjacency={v:set()for v in degree}
 for a,b in edges:adjacency[a].add(b);adjacency[b].add(a)
 unseen=set(adjacency);loops=[]
 while unseen:
  start=min(unseen);order=[start];previous=None;current=start
  while True:
   following=min(v for v in adjacency[current]if v!=previous)
   if following==start:break
   assert following in unseen and following not in order;order.append(following);previous,current=current,following
  assert len(order)>=3 and all(v in unseen for v in order);unseen-=set(order)
  loops.append([tuple(sorted((a,b)))for a,b in zip(order,order[1:]+order[:1])])
 assert sorted(e for loop in loops for e in loop)==edges
 return inv,edges,[dict(edge=[list(v)for v in e],completeOriginalFaceIncidences=rows)for e,rows in sorted(incidences.items())],loops
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,GRAPH,FINITE]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');cap=read(INPUT/'complete-current-actual-source-and-ground.json.gz');graph=read(GRAPH/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz')
 assert data['uid']==UID and data['sourceSHA256']==SOURCE_SHA
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==cap['inputHashes']['3d-viewer/city/data/manifest.json']
 rows=[];cache={}
 for mode,stream in data['completeWorldStreams'].items():
  world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');sha=digest(world.tobytes());assert world.shape==(18742,3,3)and sha==stream['completeWorldTriangleSHA256']
  previous=next(r for r in graph['rows']if r['arithmetic']==mode);assert previous['completeWorldSHA256']==sha
  topology=census(world,list(range(18742)));assert topology==previous['completeOriginalTopology'];parts=topology['sharedEdgeConnectedComponents'];un=previous['componentsWithoutCandidateSourcePath'];assert len(un)==191
  adjacency={i:set()for i in range(908)}
  for p in previous['everyNominatedPairPrimitiveInventory']:
   if p['positiveSourceInterfacePresent']:a,b=p['originalComponentA'],p['originalComponentB'];adjacency[a].add(b);adjacency[b].add(a)
  paths={34:[34]};queue=deque([34])
  while queue:
   i=queue.popleft()
   for j in sorted(adjacency[i]):
    if j not in paths:paths[j]=paths[i]+[j];queue.append(j)
  assert 23 in paths and not set(un)&set(paths)
  hosts=sorted(f for i in paths for f in parts[i]);assert not set(hosts)&{f for i in un for f in parts[i]}
  fr=next(r for r in finite['rows']if r['arithmetic']==mode)['complete18742FaceComparisons']
  if sha not in cache:
   output=[];clock=time.monotonic()
   for component in un:
    ids=parts[component];inv,edges,incidences,loops=boundary(world,ids);near,excluded=nearby_hosts(world,ids,hosts);proofs=[]
    for edge_index,edge in enumerate(edges):
     trials=[]
     for perm in [[0,1,2],[1,0,2],[0,2,1]]:
      if near:
       proof=edge_band(np.asarray(edge,dtype='<f8')[:,perm],world[near][:,:,perm]);trials.append(dict(coordinatePermutation=perm,completeFiniteHostBandProof=proof))
     proofs.append(dict(originalBoundaryEdgeIndex=edge_index,completeOriginalEdge=[list(v)for v in edge],completeCoordinatePermutationTrials=trials,
      fullEdgeAssociated=any(p['completeFiniteHostBandProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for p in trials),emptyHostScopeExplicitlyUnqualified=not near))
    assert all(fr[i]['groundComparisons']['currentDrawn']['completeFiniteOrdinaryBoundProved']for i in ids)
    output.append(dict(originalComponent=component,completeOriginalFaces=ids,completeExactOriginalComponentCensus=inv,completeOriginalEdgeIncidences=incidences,
      completeAllAuthoredBoundaryEdges=[list(map(list,e))for e in edges],completeEveryOriginalClosedBoundaryLoop=[[[list(v)for v in e]for e in loop]for loop in loops],allOriginalLoopsMandatory=True,completeBoundaryEdgeFiniteHostBandProofs=proofs,
      completeHostCandidateFaceIds=near,strictlyOutsideUnchangedBandHostFaces=excluded,
      completeBoundaryAssociated=all(p['fullEdgeAssociated']for p in proofs),
      allOriginalFacetsOrdinaryClear=True,visualRoleProposed=False,structuralRootCredit=False,structuralBridgeCredit=False))
    if time.monotonic()-clock>20:print(json.dumps(dict(arithmetic=mode,completedDetails=len(output),totalDetails=191)),flush=True);clock=time.monotonic()
   cache[sha]=dict(completeDetachedComponentDispositions=output,conditionalAttachedHostOriginalFaceIds=hosts,
    completeConditionalHostPositiveSourcePaths=[dict(component=i,originalComponentPath=paths[i])for i in sorted(paths)],
    all191CompleteBoundariesAssociated=all(r['completeBoundaryAssociated']for r in output),
    unresolvedCompleteBoundaryComponents=[r['originalComponent']for r in output if not r['completeBoundaryAssociated']])
  rows.append(dict(arithmetic=mode,completeWorldSHA256=sha,**cache[sha]))
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,completeDetachedOriginalComponents=191,
  fixedFiniteMountBandM=.1,completeAllOriginalFacesRetained=True,conditionalHostFoundationStillIndependent=True,
  noVisualHostTransferOrPropagation=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs +=[HERE/'xl-king-cheung-95691-complete191-detached-boundary-mount-diagnostic-v1-20261011.py',HERE/'test_king_cheung_complete191_boundary_mount_census_20261011.py',HERE/'local/government-xl-king-cheung-95691-complete191-detached-boundary-mount-diagnostic-v1-20261011/test-failure.json',HERE/'test_king_cheung_complete191_boundary_mount_census_v2_20261011.py']
 refs +=[HERE/n for n in ['exact_original_edge_finite_facade_distance_band_v2_20261010.py','test_exact_original_edge_finite_facade_distance_band_v2_20261010.py',
  'exact_original_shared_edge_component_census_v2_20261011.py']]
 s=importlib.util.spec_from_file_location('king191_mount_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=m.freeze(BATCH,'complete191-detached-original-boundary-finite-host-band-diagnostic-no-root-credit',refs+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeOriginalVisualCandidates=191,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'],unresolved={r['arithmetic']:r['unresolvedCompleteBoundaryComponents']for r in rows})),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('king-cheung191-boundary-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
