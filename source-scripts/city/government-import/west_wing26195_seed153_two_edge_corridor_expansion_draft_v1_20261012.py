"""DRAFT ONLY. Exact seed153/ordinary-pass wall154/strict cap44545 corridor."""
import argparse,itertools,json,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
from run import ROOT,HERE,read,save,connect,reservations,digest
import west_wing26195_exposed_edge_connected_facet_corridors_draft_v1_20261012 as G
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
BATCH='government-xl-west-wing26195-seed153-two-edge-corridor-expansion-v1-20261012';DOC=G.P.BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=G.P.BASE/'government-xl-west-wing26195-seed153-genuine-adjacency-expansion-proposal-v1-20261012';FREEZER=HERE/'west_wing26195_freeze_seed153_two_edge_corridor_expansion_draft_v1_20261012.py';RESULT_SHA='d761a5e5336cb58a9535c7e1e0a4a58021d6f3588eeefa42e2d7f9ba86623209';JOB='67805072f17832400bfe15830c39a5413d7850b03f8e797de4b93b0afae7099b';ref=G.ref

def validation():
 v=read(PROPOSAL/'no-worker-validation.json');assert v['exactTests']==8 and v['testExitCode']==0 and v['noDBQueries']and v['noReservations']and v['noGroundArithmetic'];assert v['codeRefs']==[ref(p)for p in [Path(__file__),FREEZER,HERE/'test_west_wing26195_seed153_two_edge_corridor_expansion_draft_v1_20261012.py']];assert ref(ROOT/v['testLog']['path'])==v['testLog'];log=(ROOT/v['testLog']['path']).read_text();assert 'Ran 8 tests'in log and log.rstrip().endswith('OK');return [ref(PROPOSAL/'no-worker-validation.json')]+v['codeRefs']+[v['testLog']]

def inputs():
 r,scope,worlds,ground,finite,old=G.inputs();receipt=read(G.DOC/'result.json');assert ref(G.DOC/'result.json')['sha256']==RESULT_SHA and receipt['jobId']==JOB and receipt['sourceOnly']and not receipt['physicalAccepted']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 corridor=read(G.DOC/'diagnostic.json.gz');assert corridor['allFourStreamBindings']==finite['allFourStreamBindings'];return receipt,scope,worlds,ground,finite,old,corridor

def source_context(world,records):
 # Complete source incidence, not point adjacency or a preselected partial mesh.
 inc=defaultdict(set)
 for i,t in enumerate(world):
  for j in range(3):
   e=tuple(sorted((G.exact(t[j]),G.exact(t[(j+1)%3]))))
   if e[0]!=e[1]:inc[e].add(i)
 seed_edges=[e for e,fs in inc.items()if 153 in fs];assert set().union(*(inc[e]-{153}for e in seed_edges))=={154}
 edges=[]
 for a,b in [(153,154),(154,44545)]:
  es=[e for e,fs in inc.items()if {a,b}<=fs];assert len(es)==1 and inc[es[0]]=={a,b};edges.append(dict(faces=[a,b],exactEndpoints=list(map(G.strings,es[0]))))
 assert not records[154]['strictPositiveFiniteProved']and records[154]['ordinaryFiniteProved']and records[154]['completeProjectionCovered']
 n=list(map(Q,G.P.F.exact_orientation(world[154])['exactNormal']));assert any(n)and 16*n[1]*n[1]<=sum(x*x for x in n)
 n=list(map(Q,G.P.F.exact_orientation(world[44545])['exactNormal']));assert records[44545]['ordinaryFiniteProved']and records[44545]['completeProjectionCovered']and records[44545]['strictPositiveFiniteProved']and n[1]>0 and 16*n[1]*n[1]>sum(x*x for x in n)
 return edges

def membership(world,i,ends):return G.source_segment([G.strings(G.exact(v))for v in world[i]],ends)
def certificate(complete,ends):return complete.segment(ends)
def parts(complete,edge):
 proof=certificate(complete,edge['exactEndpoints']);c=G.classify(proof,expected_ground_sha=G.P.F.GROUND_SHA,expected_ground_faces=3240,expected_endpoints=edge['exactEndpoints']);nom=c['positiveLengthExposedNominees']
 if proof['strictlyExposedWholePositiveInterface']:nom=[dict(exactClosedInteriorParameterInterval=['0','1'],exactEndpoints=edge['exactEndpoints'],representativePoint=G.strings(G.at(*map(G.point,edge['exactEndpoints']),Q(1,2))))]
 rows=[]
 for n in nom:
  p=proof if n['exactClosedInteriorParameterInterval']==['0','1']else certificate(complete,n['exactEndpoints']);rows.append(dict(n,completeGroundSegmentCertificate=p,strictPositive=p['strictlyExposedWholePositiveInterface']))
 return dict(edge=edge,completeWholeEdgeCertificate=proof,exactExposureClassification=c,positiveLengthSubsegments=rows)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');a=parser.parse_args();valid=validation();receipt,scope,worlds,ground,finite,old,corridor=inputs();assert not(DOC/'diagnostic.json.gz').exists()
 if not a.owned:
  c=reservations.claim('westwing-seed153-corridor-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert c['ok'],c;save(LOCAL/'reservation.json',json.loads(json.dumps(c['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);codes=[ref(Path(__file__)),ref(FREEZER),ref(PROPOSAL/'METHOD.md')]+valid;complete=CompleteGround(ground);results={}
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  for e in codes:assert ref(ROOT/e['path'])==e
  before=read(G.P.F.CAP/'protected-state-before.json');assert json.loads(json.dumps(G.P.F.state(before['uids']),default=str))==before['rows']
 fence()
 for mode,world in worlds.items():
  key=finite['allFourStreamBindings'][mode]['proofTupleSHA256']
  if key in results:continue
  fence();assert digest(world.tobytes())==finite['allFourStreamBindings'][mode]['wholeWorldSHA256'];records=finite['distinctCompleteFiniteProofs'][key]['allWholeFacetProofs'];edges=source_context(world,records);seed=next(x for x in old['distinctBoundedRouteDiagnostics'][key]['routes']if x['seedFace']==153);assert seed['genuineExposedGradeDiagnostic']
  eproofs=[parts(complete,e)for e in edges];contacts=sorted({G.at(*map(G.point,v['nominatedInterval']['exactSegmentEndpoints']),Q(1,2))for v in seed['verifiedPositiveUpperGroundIntervals']});attempts=[]
  entries=[p for p in eproofs[0]['positiveLengthSubsegments']if p['strictPositive']];exits=[p for p in eproofs[1]['positiveLengthSubsegments']if p['strictPositive']];assert len(contacts)*len(entries)*len(exits)<=1024
  for contact,entry,exit in itertools.product(contacts,entries,exits):
   fence();start=[G.strings(contact),entry['representativePoint']];middle=[entry['representativePoint'],exit['representativePoint']]
   if G.point(start[0])==G.point(start[1])or G.point(middle[0])==G.point(middle[1]):continue
   sm=membership(world,153,start);mm=membership(world,154,middle);sp=certificate(complete,start);mp=certificate(complete,middle);sc=None;ok=False
   if sp['closedWholeSegmentProjectionCovered']and sp['exactMinimumGapM']is not None and Q(sp['exactMinimumGapM'])==0 and not any(x.get('collapsedProjectionConservative')for x in sp['selectedGroundKernelProof']['allFinitePieces']):
    sc=G.classify(sp,expected_ground_sha=G.P.F.GROUND_SHA,expected_ground_faces=3240,expected_endpoints=start);ok=sc['strictPositiveExceptInitialEndpoint']and sc['initialEndpointGapM']=='0'
   attempts.append(dict(exactGradeStart=G.strings(contact),entrySubsegment=entry,exitSubsegment=exit,seedMembership=sm,corridorOnlyWallMembership=mm,gradeToEntryCertificate=sp,gradeToEntryExposure=sc,gradeConnectorStrictExceptStart=ok,withinWallCertificate=mp,withinWallStrictPositive=mp['strictlyExposedWholePositiveInterface'],boundedDiagnosticRouteFound=ok and mp['strictlyExposedWholePositiveInterface']))
  results[key]=dict(wholeWorldSHA256=finite['allFourStreamBindings'][mode]['wholeWorldSHA256'],sourceContextFaces=[153,154,44545],seedGradeProofReusedVerbatim=seed,ordinaryPassSteepCorridorOnlyFacet154=records[154],strictFullCap44545=records[44545],capOrientation=G.P.F.exact_orientation(world[44545]),edgeDiagnostics=eproofs,allBoundedAttempts=attempts,diagnosticRouteFound=any(x['boundedDiagnosticRouteFound']for x in attempts),wholeFacet154StrictPositiveClaim=False,newGradeRootClaim=False);save(LOCAL/('completed-'+mode+'.json.gz'),results[key]);assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(world=mode,attempts=len(attempts),diagnosticRouteFound=results[key]['diagnosticRouteFound'])),flush=True)
 complete.verify_binding();fence();save(DOC/'diagnostic.json.gz',dict(sourceOnly=True,physicalAccepted=False,gradeRootAccepted=False,installationApproved=False,completeFaces=46918,completeGroundFaces=3240,all118BodyObligationsRetained=True,all42OrdinaryFailuresAnd443StrictUncertifiedRetained=True,currentManifest=scope['currentManifest'],allFourStreamBindings=finite['allFourStreamBindings'],distinctBoundedDiagnostics=results,priorAll24NewAnd17EarlierPathsPreserved=ref(G.DOC/'diagnostic.json.gz'),noFiniteOrGradeArithmeticRerun=True,evidenceRefs=codes+[ref(G.DOC/'result.json')]));subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
