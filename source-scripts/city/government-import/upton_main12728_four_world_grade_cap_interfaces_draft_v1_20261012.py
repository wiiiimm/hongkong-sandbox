"""UNEXECUTED bounded main-body grade/cap/interface diagnostic; no whole-pair role."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict,deque
import json,sys,time,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import upton_six_basic_preserved_ground_feasibility_draft_v1_20261012 as inputs
from upton_geometry_bound_inherited_overlap_replay_draft_v1_20261012 import ref,check,module,CURRENT,UIDS,FOREIGN,FREEZER
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha,triangles,MODES
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import nonzero
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-main12728-four-world-grade-cap-interfaces-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json'
def normal(t):
 a,b,c=[tuple(F(float(v))for v in p)for p in t];u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)];return(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
def load_inputs():
 _,_,worlds,_,_=inputs.load_inputs();replay=read(inputs.NOM/'actual-production-replay.json.gz');ground=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3);assert len(ground)==10770 and sha(ground)=='739eefcca874c64ee7c9a295b54c07935c8fda4e4c5f880b459eff6c44aacfb2'
 assert replay['currentManifestSHA256']==CURRENT and replay['startEndAllInputsVerified'];assert all(p['candidateCompleteGroundSHA256']==sha(ground)for _,_,_,_,p in worlds)
 return worlds,ground

def schema_only():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['inputRefs']+pins['codeRefs']:check(q)
 worlds,g=load_inputs()
 for uid,mode,w,c,p in worlds:
  main=c['sharedEdgeConnectedComponents'][0];assert len(main)=={UIDS[0]:1500,UIDS[1]:1560,UIDS[2]:368}[uid]
  records={r['face']:r['candidate']for r in p['findings']['rows']};assert set(main)<=set(records)
  for i in main:assert records[i]['sourceFaceSHA256']==sha(w[i])and records[i]['ordinaryBoundProved']and records[i]['projectionCovered']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),actualCandidateGroundFaces=len(g),fourWorlds=4,completeMainFaces=[1500,1560,368],noDBLeaseGradeOrContactMath=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic();refs=[ref(p)for p in inputs.code_paths(Path(__file__))]+[ref(Path(__file__)),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'schema-preflight.json')]
 refs+=read(PROPOSAL/'draft-pins.json')['codeRefs']+read(PROPOSAL/'draft-pins.json')['inputRefs']
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic();print(json.dumps(dict(heartbeat=True)),flush=True)
 schema_only()
 for folder in inputs.FOLDERS:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for q in r['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();worlds,ground=load_inputs();complete=CompleteGround(ground);DOC.mkdir(parents=True);output=[];cache={}
 for mode in MODES:
  rows={uid:(w,c,p)for uid,m,w,c,p in worlds if m==mode};pworld,pcensus,pproof=rows[UIDS[1]];pmain=pcensus['sharedEdgeConnectedComponents'][0];tuplekey=tuple(sha(rows[u][0])for u in UIDS[:3])
  if tuplekey in cache:output.append(dict(mode=mode,exactCompleteWorldTupleReuseOfMode=cache[tuplekey]['mode'],diagnostic=cache[tuplekey]['diagnostic']));pulse(True);continue
  inventories={u:census(w,list(range(len(w))))for u,(w,c,p)in rows.items()};maincontinuity={u:any(set(group)==set(c['sharedEdgeConnectedComponents'][0])for group in inventories[u]['sharedEdgeConnectedComponents'])for u,(w,c,p)in rows.items()}
  grade=exact_upper_ground_interfaces(pworld,[i for i in pmain if nonzero(pworld[i])],ground);pulse(True);proofs={r['face']:r['candidate']for r in pproof['findings']['rows']};normals={i:normal(pworld[i])for i in pmain};caps={i for i in pmain if any(normals[i])and normals[i][1]>0 and 16*normals[i][1]**2>sum(v*v for v in normals[i])and F(proofs[i]['exactLowerM'])>0}
  incidence=defaultdict(set)
  for i in pmain:
   if not nonzero(pworld[i]):continue
   for k in range(3):
    edge=tuple(sorted((tuple(pworld[i,k]),tuple(pworld[i,(k+1)%3]))))
    if edge[0]!=edge[1]:incidence[edge].add(i)
  gradefaces=sorted({q['sourceFace']for q in grade});parent={i:None for i in gradefaces};todo=deque(gradefaces);edgeproofs={}
  while todo:
   i=todo.popleft()
   for k in range(3):
    edge=tuple(sorted((tuple(pworld[i,k]),tuple(pworld[i,(k+1)%3]))))
    for j in sorted(incidence.get(edge,set())-{i}):
     if j in parent:continue
     assert proofs[j]['ordinaryBoundProved']and proofs[j]['projectionCovered']
     if edge not in edgeproofs:edgeproofs[edge]=complete.segment([[str(F(float(v)))for v in p]for p in edge]);pulse()
     if not edgeproofs[edge]['strictlyExposedWholePositiveInterface']:continue
     parent[j]=i;todo.append(j)
  def route(i):
   if i not in parent:return []
   path=[i]
   while parent[path[-1]]is not None:path.append(parent[path[-1]])
   return list(reversed(path))
  interfaces=[]
  for uid in[UIDS[0],UIDS[2]]:
   world,c,p=rows[uid];main=c['sharedEdgeConnectedComponents'][0];a=[i for i in pmain if nonzero(pworld[i])];b=[i for i in main if nonzero(world[i])];contacts=exact_component_contacts(pworld,a,world,b);assert contacts['allPairsExamined'];endpoint={r['face']:r['candidate']for r in p['findings']['rows']};qualified=[]
   for q in contacts['contacts']:
    i,j=q['sourceFaceA'],q['sourceFaceB'];positive=q['dimension']>0;fullstrict=F(proofs[i]['exactLowerM'])>0 and F(endpoint[j]['exactLowerM'])>0;path=route(i);capids=[k for k in path if k in caps]
    qualified.append(dict(actualContact=q,podiumGradeWholeEdgePath=path,strictExposedCapsOnPath=capids,completeEndpointFacetStrictExposure=fullstrict,positiveDimensional=positive,boundedGradeCapToInterfaceDiagnostic=bool(positive and fullstrict and path and capids and maincontinuity[UIDS[1]]and maincontinuity[uid]),supportRootRoleOrBridgeAccepted=False))
   interfaces.append(dict(uid=uid,mainFaceIDs=main,wholeWorldSHA256=sha(world),completeExactMainBodyContacts=contacts,qualifiedDiagnostics=qualified,noResidualBodyCredit=True));pulse(True)
  diagnostic=dict(completeActualWorldEdgeCensus=inventories,actualMainBodiesStillSingleTrueEdgeBodies=maincontinuity,main12728Faces=pmain,genuineActualUpperGroundInterfaces=grade,completeMain12728StrictPositiveCapFaces=sorted(caps),allExaminedWholeSharedEdgeExposure=[dict(edge=[list(p)for p in e],proof=q)for e,q in edgeproofs.items()],restrictedGradeParents=[dict(face=i,parent=j)for i,j in sorted(parent.items())],mainInterfaces=interfaces,allResidualAndZeroObligationsRemain=True,all23OriginalCrossingsRemain=True,bodyRoleOrWholePairAcceptance=False)
  cache[tuplekey]=dict(mode=mode,diagnostic=diagnostic);output.append(dict(mode=mode,exactCompleteWorldTupleReuseOfMode=None,diagnostic=diagnostic));save(LOCAL/(mode+'-completed-main-diagnostic.json.gz'),output[-1]);pulse(True)
 complete.verify_binding();save(DOC/'diagnostic.json.gz',dict(rows=output,actualCandidateGroundSHA256=sha(ground),completeGroundFaces=len(ground),all13704SourceFacesAnd749BodiesAnd17ZerosPreserved=True,fullOrdinaryClearanceReusedByRef=ref(inputs.AUD/'complete-candidate-clearance.json.gz'),sixBasicSupportGapFailuresStillHold=ref(inputs.RAW/'neighbour-checks.json'),gradeRootAccepted=False,wholePairRoleAccepted=False,physicalAccepted=False,newlyInstalled=0))
 refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]+[ref(p)for p in LOCAL.glob('*completed*.json.gz')];fence();module(FREEZER,'upton_main_grade_cap_freezer').freeze(BATCH,'bounded-actual-main12728-grade-cap-two-main-source-interfaces',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS[:3],currentManifestSHA256=CURRENT,sourceOnly=True,newlyInstalled=0,physicalAccepted=False,sourceGeometryChanges=0,terrainGeometryChanges=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-bounded-main-grade-cap-only'in sys.argv and not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-main-grade-cap-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
