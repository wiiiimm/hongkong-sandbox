"""DRAFT full current original-body finite assembly graph. No body/support/root approval."""
import argparse,json,subprocess,sys,uuid,itertools
from collections import defaultdict,deque
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import west_wing26195_seed153_two_edge_corridor_expansion_draft_v1_20261012 as S
from west_wing26195_complete_cross_body_candidates_draft_v1_20261012 import candidates
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points,dimension
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
BATCH='government-xl-west-wing26195-complete-current-body-contact-graph-v1-20261012';DOC=S.G.P.BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=S.G.P.BASE/'government-xl-west-wing26195-complete-body-current-support-proposal-v1-20261012';FREEZER=HERE/'west_wing26195_freeze_complete_current_body_contact_graph_draft_v1_20261012.py';HELPER=HERE/'west_wing26195_complete_cross_body_candidates_draft_v1_20261012.py';TEST=HERE/'test_west_wing26195_complete_cross_body_candidates_draft_v1_20261012.py';CHUNK=2048;MAX_PAIRS=100000;ref=S.ref

def validation():
 v=read(PROPOSAL/'no-worker-validation.json');assert v['exactTests']==11 and v['testExitCode']==0 and v['noDBQueries']and v['noReservations']and v['noExactContactExecution'];assert v['codeRefs']==[ref(p)for p in [HELPER,TEST,Path(__file__),FREEZER]];assert ref(ROOT/v['testLog']['path'])==v['testLog'];s=(ROOT/v['testLog']['path']).read_text();assert 'Ran 11 tests'in s and s.rstrip().endswith('OK');return [ref(PROPOSAL/'no-worker-validation.json')]+v['codeRefs']+[v['testLog'],ref(PROPOSAL/'METHOD.md')]
def inputs():
 _,scope,worlds,ground,finite,old,corridor=S.inputs();r=read(S.DOC/'result.json');assert r['jobId']=='c074d4029e2a72d26e45c187c524c18f20135c8e038afac5de992848293d164b'and ref(S.DOC/'result.json')['sha256']=='e75adce0044c077f63fde26447fd6fbc820551c9a038541276eb6c5db6acc077'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 sd=read(S.DOC/'diagnostic.json.gz');assert sd['allFourStreamBindings']==finite['allFourStreamBindings']and all(x['diagnosticRouteFound']for x in sd['distinctBoundedDiagnostics'].values());return r,scope,worlds,finite,old,corridor,sd

def record(world,i,j,labels,cache):
 for f in [i,j]:
  if f not in cache:cache[f]=rational_face(world[f])
 a,b=cache[i],cache[j];pts=sorted(finite_intersection_points(a,b))
 if not pts:return None
 na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));da,db=dimension(a),dimension(b);cop=da==db==2 and not any(cross(na,nb))and all(dot(na,sub(p,a[0]))==0 for p in b);mid=tuple(sum(p[k]for p in pts)/len(pts)for k in range(3));m=contact_measure(pts);inside=da==db==2 and not cop and m['dimension']>0 and relative_interior(a,mid)and relative_interior(b,mid)
 return dict(sourceFaces=[i,j],originalBodyLabels=[int(labels[i]),int(labels[j])],actualFinitePrimitiveDimensions=[da,db],coplanar=cop,bothRelativeInteriorSurfaceCrossing=inside,**m)
def graph(count,records,*,exclude_interior=False):
 adj={i:set()for i in range(count)}
 for r in records:
  if r['dimension']<=0 or r['actualFinitePrimitiveDimensions']!=[2,2]or exclude_interior and r['bothRelativeInteriorSurfaceCrossing']:continue
  a,b=r['originalBodyLabels'];adj[a].add(b);adj[b].add(a)
 parents={0:None};q=deque([0])
 while q:
  a=q.popleft()
  for b in sorted(adj[a]):
   if b not in parents:parents[b]=a;q.append(b)
 return dict(completeAdjacency={i:sorted(v)for i,v in adj.items()},conditionalParents=parents,unreachedOriginalBodies=sorted(set(adj)-set(parents)),root0IsConditionalNotAccepted=True,positiveSurfaceContactIsNotStructuralSupport=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args();valid=validation();receipt,scope,worlds,finite,old,corridor,sd=inputs();assert not(DOC/'diagnostic.json.gz').exists();cs=finite['originalBodyCensus']['sharedEdgeConnectedComponents'];assert len(cs)==118 and not finite['originalBodyCensus']['exactNonrenderingOriginalFaces']
 if not a.owned:
  c=reservations.claim('westwing-full-body-contact-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert c['ok'],c;save(LOCAL/'reservation.json',json.loads(json.dumps(c['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);walker=S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingbodyclosure');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(FREEZER,paths);codes=[ref(p)for p in sorted(paths)]+valid;results={};chunks=[]
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  for e in codes:assert ref(ROOT/e['path'])==e
  before=read(S.G.P.F.CAP/'protected-state-before.json');assert json.loads(json.dumps(S.G.P.F.state(before['uids']),default=str))==before['rows']
 fence()
 for mode,world in worlds.items():
  binding=finite['allFourStreamBindings'][mode];key=binding['proofTupleSHA256'];assert digest(world.tobytes())==binding['wholeWorldSHA256']
  if key in results:continue
  pairlist,labels=candidates(world,cs);assert len(pairlist)<=MAX_PAIRS;pairhash=digest(json.dumps(pairlist,separators=(',',':')).encode());rows=[];cache={}
  for start in range(0,len(pairlist),CHUNK):
   end=min(start+CHUNK,len(pairlist));path=LOCAL/'chunks'/key/f'{start:06d}-{end:06d}.json.gz';contract=dict(proofTupleSHA256=key,wholeWorldSHA256=binding['wholeWorldSHA256'],completeFaces=46918,completeOriginalBodies=118,completeCandidatePairs=len(pairlist),candidatePairListSHA256=pairhash,firstPair=start,exclusiveLastPair=end,codeRefs=codes);fence()
   if path.exists():chunk=read(path);assert chunk['contract']==contract
   else:
    contacts=[r for i,j in pairlist[start:end]if (r:=record(world,i,j,labels,cache))is not None];chunk=dict(contract=contract,exactCandidatePairIDs=[list(x)for x in pairlist[start:end]],allFiniteContacts=contacts);tmp=path.with_name(path.name+'.pending.json.gz');save(tmp,chunk);assert read(tmp)==chunk;tmp.replace(path)
   assert chunk['exactCandidatePairIDs']==[list(x)for x in pairlist[start:end]];rows+=chunk['allFiniteContacts'];chunks.append(ref(path));fence();assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(world=mode,completePairs=end,totalPairs=len(pairlist),finiteContacts=len(rows))),flush=True)
  assert len({tuple(r['sourceFaces'])for r in rows})==len(rows);pairsummaries=[]
  for b,c in itertools.combinations(range(118),2):
   subset=[r for r in rows if set(r['originalBodyLabels'])=={b,c}];pairsummaries.append(dict(originalBodies=[b,c],pointOnly=sum(r['dimension']==0 for r in subset),positiveDimensional=sum(r['dimension']>0 for r in subset),bothInteriorCrossings=sum(r['bothRelativeInteriorSurfaceCrossing']for r in subset),contactFaces=[r['sourceFaces']for r in subset]))
  results[key]=dict(wholeWorldSHA256=binding['wholeWorldSHA256'],completeOriginalBodyFaces=cs,completeClosed3DAABBCandidatePairs=len(pairlist),completeCandidatePairListSHA256=pairhash,allExactCrossBodyContacts=rows,all6903BodyPairSummaries=pairsummaries,allPositiveSurfaceContextGraph=graph(118,rows),nonInteriorCrossingSurfaceContextGraph=graph(118,rows,exclude_interior=True),all118BodySupportRolesRemainUnqualified=True,mainBody0GroundRoleRemainsConditional=True,currentArithmeticOriginalBodyLabelsAreProvenanceOnly=True);save(LOCAL/('completed-'+mode+'.json.gz'),results[key])
 fence();save(DOC/'diagnostic.json.gz',dict(sourceOnly=True,physicalAccepted=False,bodySupportAccepted=False,gradeRootAccepted=False,installationApproved=False,completeFaces=46918,completeOriginalBodies=118,completeGroundFaces=3240,currentManifest=scope['currentManifest'],allFourStreamBindings=finite['allFourStreamBindings'],distinctCompleteBodyDiagnostics=results,all42OrdinaryFailuresAnd443StrictUncertifiedRetained=True,noFiniteOrGradeOrCorridorArithmeticRerun=True,prior17Plus24PlusSeed153DiagnosticsPreserved=[ref(S.G.P.DOC/'diagnostic.json.gz'),ref(S.G.DOC/'diagnostic.json.gz'),ref(S.DOC/'diagnostic.json.gz')],sourceGeometryChanges=0,terrainGeometryChanges=0,legacyDeliveryAnd15ReviewsUnchanged=True,evidenceRefs=codes+chunks+[ref(S.DOC/'result.json'),ref(S.G.P.F.DOC/'diagnostic.json.gz')]));subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
