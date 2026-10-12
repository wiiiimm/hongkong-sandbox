"""DRAFT only: bounded exact partial-edge / connected-facet surface context."""
import argparse,json,subprocess,sys,uuid,itertools
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as Q
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
import west_wing26195_bounded_current_grade_cap_routes_draft_v2_20261012 as P
from west_wing26195_exact_saved_segment_exposure_draft_v1_20261012 import classify,source_segment,point,at
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
BATCH='government-xl-west-wing26195-exposed-edge-connected-facet-corridors-v1-20261012';DOC=P.BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=P.BASE/'government-xl-west-wing26195-exposed-edge-subinterval-connected-facet-proposal-v1-20261012';FREEZER=HERE/'west_wing26195_freeze_exposed_edge_connected_facet_corridors_draft_v1_20261012.py';HELPER=HERE/'west_wing26195_exact_saved_segment_exposure_draft_v1_20261012.py';TEST=HERE/'test_west_wing26195_exact_saved_segment_exposure_draft_v1_20261012.py'
PRIOR_SHA='1ac8072a8f44e9124089ee6dfd2e1ef9c4b77cf906cf3b2d2e9f3494bc02ca0a';PRIOR_JOB='74b5215e3f2271cdc04a5fc213835c930e22f32393fedea9a5b45407947e92e6';MAX_PAIRS=10000;FACE_BUDGET=64;ref=P.ref

def exact(v):return tuple(Q(float(x))for x in v)
def strings(p):return list(map(str,p))
def validation():
 v=read(PROPOSAL/'test-validation.json');assert v['exactTests']==20 and v['exitCode']==0 and v['codeRefs']==[ref(p)for p in [HELPER,TEST,Path(__file__),FREEZER]];assert ref(ROOT/v['testLog']['path'])==v['testLog'];log=(ROOT/v['testLog']['path']).read_text();assert 'Ran 20 tests'in log and log.rstrip().endswith('OK');return [ref(PROPOSAL/'test-validation.json'),ref(PROPOSAL/'METHOD.md')]+v['codeRefs']+[v['testLog']]
def inputs():
 _,scope,worlds,ground,finite=P.inputs();assert ref(P.DOC/'result.json')['sha256']==PRIOR_SHA;r=read(P.DOC/'result.json');assert r['jobId']==PRIOR_JOB and r['sourceOnly']and not r['physicalAccepted']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(PRIOR_JOB,)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 old=read(P.DOC/'diagnostic.json.gz');assert old['allFourStreamBindings']==finite['allFourStreamBindings']and old['wholeGroundSHA256']==P.F.GROUND_SHA and old['currentManifest']==scope['currentManifest'];return r,scope,worlds,ground,finite,old

def main():
 a=argparse.ArgumentParser();a.add_argument('--owned',action='store_true');a=a.parse_args();valid=validation();r,scope,worlds,ground,finite,old=inputs();assert not(DOC/'diagnostic.json.gz').exists()
 if not a.owned:
  c=reservations.claim('westwing-exposed-corridors-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert c['ok'],c;save(LOCAL/'reservation.json',json.loads(json.dumps(c['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);walker=P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_corridor_codes');files=set();walker.local_imports(Path(__file__),files);walker.local_imports(FREEZER,files);codes=[ref(p)for p in sorted(files)];complete=CompleteGround(ground);results={}
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  for e in codes+valid:assert ref(ROOT/e['path'])==e
  b=read(P.F.CAP/'protected-state-before.json');assert json.loads(json.dumps(P.F.state(b['uids']),default=str))==b['rows']
 fence()
 for mode,world in worlds.items():
  binding=old['allFourStreamBindings'][mode];key=binding['proofTupleSHA256'];assert digest(world.tobytes())==binding['wholeWorldSHA256']and binding['wholeGroundSHA256']==complete.ground_sha
  if key in results:continue
  previous=old['distinctBoundedRouteDiagnostics'][key];records=finite['distinctCompleteFiniteProofs'][key]['allWholeFacetProofs'];saved=previous['allExaminedWholeEdgeProofs'];assert len(saved)==88;grade={x['seedFace']:x for x in previous['routes']};seeds=sorted(i for i,x in grade.items()if not x['boundedOriginalPath']);assert len(seeds)==25 and len(grade)==42 and sum(bool(x['boundedOriginalPath'])for x in grade.values())==17
  context=sorted(set(seeds)|{i for e in saved for i in e['faces']});nodes=[];by_face=defaultdict(list);node_ids={};adj=defaultdict(set);links={};edge_records=[];anchors=[]
  def eligible(i):return records[i]['strictPositiveFiniteProved']or i in grade and grade[i]['genuineExposedGradeDiagnostic']
  def node(i,p):
   p=point(p);k=(i,p)
   if k not in node_ids:
    # A collapsed current facet may not gain corridor/bridge credit.
    face=[strings(exact(v))for v in world[i]];source_segment(face,[strings(p),strings(exact(world[i,0]))]if p!=exact(world[i,0])else[strings(p),strings(exact(world[i,1]))]);j=len(nodes);node_ids[k]=j;nodes.append(dict(sourceFace=i,exactPoint=strings(p)));by_face[i].append(j)
   return node_ids[k]
  for i in context:
   if not eligible(i):continue
   if records[i]['strictPositiveFiniteProved']:
    for p in world[i]:node(i,strings(exact(p)))
   if i in grade:
    exposure=grade[i]['completeUnchangedVertexExposure'];assert Q(exposure['exactExposureLowerBoundM'])>0
    for v in exposure['allThreeOriginalVertexFiniteColumnProofs']:
     j=v['originalVertex'];assert v['actualHighestOriginalVertex']==world[i,j].tolist()
     if Q(v['exactExposureLowerBoundM'])>0:node(i,strings(exact(world[i,j])))
  for index,e in enumerate(saved):
   fence();i,j=e['faces'];assert i!=j and eligible(i)and eligible(j);ends=[strings(exact(p))for p in e['unchangedOriginalWholeSharedEdge']]
   for f in [i,j]:
    actual={tuple(sorted((exact(world[f,k]),exact(world[f,(k+1)%3]))))for k in range(3)};assert tuple(sorted(map(point,ends)))in actual;source_segment([strings(exact(v))for v in world[f]],ends)
   classification=classify(e['completeFiniteEdgeProof'],expected_ground_sha=complete.ground_sha,expected_ground_faces=3240,expected_endpoints=ends);parts=[]
   if e['completeFiniteEdgeProof']['strictlyExposedWholePositiveInterface']:nominees=[dict(exactClosedInteriorParameterInterval=['0','1'],exactEndpoints=ends,representativePoint=strings(at(*map(point,ends),Q(1,2))))]
   else:nominees=classification['positiveLengthExposedNominees']
   for n in nominees:
    proof=e['completeFiniteEdgeProof']if n['exactClosedInteriorParameterInterval']==['0','1']else complete.segment(n['exactEndpoints']);ok=proof['strictlyExposedWholePositiveInterface'];part=dict(n,completeGroundSegmentCertificate=proof,independentlyStrictPositive=ok,wholeEdgeProofReused=n['exactClosedInteriorParameterInterval']==['0','1']);parts.append(part)
    if ok:
     a=node(i,n['representativePoint']);b=node(j,n['representativePoint']);adj[a].add(b);adj[b].add(a);links[tuple(sorted((a,b)))]=dict(kind='positive-length-genuine-original-edge-subsegment',savedEdgeIndex=index,partIndex=len(parts)-1,sourceFaces=[i,j],nodeIds=[a,b])
   edge_records.append(dict(savedWholeEdgeVerbatim=e,exposureClassification=classification,subsegmentCertificates=parts))
  pair_count=sum(len(v)*(len(v)-1)//2 for v in by_face.values());assert pair_count<=MAX_PAIRS,dict(boundedCorridorPairLimit=MAX_PAIRS,actualPairCount=pair_count)
  corridor_records=[]
  for i,ns in sorted(by_face.items()):
   fence()
   for a,b in itertools.combinations(ns,2):
    if len(corridor_records)%16==0:fence();print(json.dumps(dict(world=mode,phase='within-original-facet-corridors',completed=len(corridor_records),boundedTotal=pair_count)),flush=True)
    ends=[nodes[a]['exactPoint'],nodes[b]['exactPoint']];membership=source_segment([strings(exact(v))for v in world[i]],ends);proof=complete.segment(ends);idx=len(corridor_records);corridor_records.append(dict(sourceFace=i,nodeIds=[a,b],exactSourceFacetMembership=membership,completeGroundSegmentCertificate=proof,strictConnectedCorridor=proof['strictlyExposedWholePositiveInterface']))
    if proof['strictlyExposedWholePositiveInterface']:adj[a].add(b);adj[b].add(a);links[tuple(sorted((a,b)))]=dict(kind='complete-strict-within-original-facet-corridor',corridorIndex=idx,nodeIds=[a,b])
  starts=defaultdict(set)
  for seed in seeds:
   fence();print(json.dumps(dict(world=mode,phase='grade-connectors',seedFace=seed)),flush=True);contacts=[]
   for v in grade[seed]['verifiedPositiveUpperGroundIntervals']:
    ends=list(map(point,v['nominatedInterval']['exactSegmentEndpoints']));contacts.append(at(ends[0],ends[1],Q(1,2)))
   for contact in sorted(set(contacts)):
    for n in by_face[seed]:
     ends=[strings(contact),nodes[n]['exactPoint']]
     if point(ends[0])==point(ends[1]):continue
     membership=source_segment([strings(exact(v))for v in world[seed]],ends);proof=complete.segment(ends);exposure=None;ok=False
     if proof['closedWholeSegmentProjectionCovered']and proof['exactMinimumGapM']is not None and Q(proof['exactMinimumGapM'])==0:
      if not any(x.get('collapsedProjectionConservative')for x in proof['selectedGroundKernelProof']['allFinitePieces']):
       exposure=classify(proof,expected_ground_sha=complete.ground_sha,expected_ground_faces=3240,expected_endpoints=ends);ok=exposure['strictPositiveExceptInitialEndpoint']and exposure['initialEndpointGapM']=='0'
     anchors.append(dict(seedFace=seed,nodeId=n,exactOriginalFacetMembership=membership,completeGroundSegmentCertificate=proof,exactExposureClassification=exposure,nonnegativeGradeConnectionStrictExceptStart=ok))
     if ok:starts[seed].add(n)
  def cap(i):
   n=list(map(Q,P.F.exact_orientation(world[i])['exactNormal']));return records[i]['strictPositiveFiniteProved']and n[1]>0 and 16*n[1]*n[1]>sum(v*v for v in n)
  routes=[]
  for seed in seeds:
   parent={n:None for n in sorted(starts[seed])};queue=deque(sorted(parent));seen_faces={seed};target=None;budget=False
   while queue and target is None:
    a=queue.popleft()
    if cap(nodes[a]['sourceFace']):target=a;break
    for b in sorted(adj[a]):
     if b in parent:continue
     face=nodes[b]['sourceFace']
     if face not in seen_faces and len(seen_faces)>=FACE_BUDGET:budget=True;continue
     seen_faces.add(face);parent[b]=a;queue.append(b)
   path=[]
   if target is not None:
    path=[target]
    while parent[path[-1]]is not None:path.append(parent[path[-1]])
   routes.append(dict(seedFace=seed,nonnegativeGradeConnectedStartNodes=sorted(starts[seed]),boundedConnectedNodePath=path,completePathTransitionCertificates=[links[tuple(sorted((a,b)))]for a,b in zip(path,path[1:])],strictPositiveNonsteepCapFace=nodes[target]['sourceFace']if target is not None else None,exactStrictPositiveCapCertificate=dict(sourceFace=nodes[target]['sourceFace'],unchangedFullFacetProof=records[nodes[target]['sourceFace']],exactOriginalOrientation=P.F.exact_orientation(world[nodes[target]['sourceFace']]))if target is not None else None,visitedSourceFaces=sorted(seen_faces),faceBudget=FACE_BUDGET,budgetReached=budget,diagnosticRouteFound=target is not None))
  results[key]=dict(wholeWorldSHA256=binding['wholeWorldSHA256'],completeGroundSHA256=complete.ground_sha,exact25UnresolvedSeeds=seeds,exact88SavedWholeEdgesPreserved=saved,completeFixedSourceFacetContext=context,previous17PathsRetainedVerbatim=[x for x in previous['routes']if x['boundedOriginalPath']],edgeExposureDiagnostics=edge_records,allDiagnosticNodes=nodes,allWithinFacetSegmentCertificates=corridor_records,allGradeToExposedNodeCertificates=anchors,boundedConnectedRoutes=routes,wholeEdgePredicateUnchanged=True,pointOrEndpointOnlyRouteCredit=False,noFiniteOrGradeArithmeticRerun=True,sourceOrTerrainGeometryChanges=0,physicalAccepted=False);save(LOCAL/('completed-'+mode+'.json.gz'),results[key]);print(json.dumps(dict(world=mode,newBoundedConnectedRoutes=sum(x['diagnosticRouteFound']for x in routes),corridorPairs=pair_count)),flush=True)
  fence();assert reservations.heartbeat(lease)['ok']
 complete.verify_binding();fence();save(DOC/'diagnostic.json.gz',dict(uid=P.F.UID,sourceOnly=True,currentManifest=scope['currentManifest'],nativeCount=6649,completeSourceFaces=46918,completeGroundFaces=3240,wholeGroundSHA256=complete.ground_sha,allFourStreamBindings=old['allFourStreamBindings'],distinctBoundedCorridorDiagnostics=results,all42OrdinaryFailuresAnd443StrictUncertifiedRetained=True,all118OriginalBodyObligationsAndOther117SupportObligationsRetained=True,legacyDeliveryAnd15ReviewsUnchanged=True,physicalAccepted=False,gradeRootAccepted=False,burialRoleAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,evidenceRefs=codes+valid+[ref(P.DOC/'result.json'),ref(P.DOC/'diagnostic.json.gz')]));subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
