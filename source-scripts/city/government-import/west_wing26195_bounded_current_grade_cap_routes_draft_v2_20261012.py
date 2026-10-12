"""DRAFT: bounded grade/whole-exposed-edge/strict-cap context, no root or role approval."""
import argparse,json,subprocess,sys,uuid,copy
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from fractions import Fraction as Q
from run import ROOT,HERE,read,save,digest,connect,reservations
import west_wing26195_complete_current_finite_ground_draft_v3_20261012 as F
import west_wing26195_bounded_current_grade_cap_routes_draft_v1_20261012 as H
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing26195-bounded-current-grade-cap-routes-v2-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;FREEZER=HERE/'west_wing26195_freeze_bounded_current_grade_cap_routes_draft_v2_20261012.py';BUDGET=64
RESULT_SHA='0a4485ffe26c1242a91fb5e2040f7a886db775e459790f7e5f0baa8328e67449';JOB='a0f08846d525ebbcde49b6b62151d031fd73a41f4633c5455fcaeac4d06ffcac'
GRADE_RESULT_SHA='cb5f838eb3819688ddf9c46c34b7b8c3a0ae210cb5135dc59d511915be4174a6';GRADE_JOB='67d864fee9afae8041e836fb1245f1ee4024c391ada67e1efe059ea7a42fac85'
ref=F.ref
PROPOSAL=BASE/'government-xl-west-wing26195-next-grade-path-method-v3-20261012'

def canon(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def inputs():
 assert ref(F.DOC/'result.json')['sha256']==RESULT_SHA;r=read(F.DOC/'result.json');assert r['jobId']==JOB and r['sourceOnly']and not r['physicalAccepted']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 _,scope,_,worlds,ground,_=F.load_inputs();d=read(F.DOC/'diagnostic.json.gz');assert d['genuineBodyObligations']==118 and d['zeroFaceObligations']==0 and not d['gradeRootProved'];assert set(d['allFourStreamBindings'])==F.NAMES
 assert json.loads(json.dumps(F.state(read(F.CAP/'protected-state-before.json')['uids']),default=str))==read(F.CAP/'protected-state-before.json')['rows']
 assert ref(H.DOC/'result.json')['sha256']==GRADE_RESULT_SHA;gr=read(H.DOC/'result.json');assert gr['jobId']==GRADE_JOB and gr['sourceOnly']and not gr['physicalAccepted']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(GRADE_JOB,)).fetchone()==('complete',gr)
 for e in gr['evidenceRefs']:assert ref(ROOT/e['path'])==e
 gd=read(H.DOC/'diagnostic.json.gz');assert gd['currentManifest']==scope['currentManifest']and gd['wholeGroundSHA256']==F.GROUND_SHA and gd['allFourStreamBindings']==d['allFourStreamBindings']and not gd['gradeRootAccepted']and not gd['physicalAccepted']
 return gr,scope,worlds,ground,d

def main():
 a=argparse.ArgumentParser();a.add_argument('--owned',action='store_true');a=a.parse_args();r,scope,worlds,ground,d=inputs();assert not(DOC/'diagnostic.json.gz').exists()
 if not a.owned:
  claim=reservations.claim('westwing-grade-cap-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);complete=CompleteGround(ground);cache={};bindings={};gd=read(H.DOC/'diagnostic.json.gz');walker=F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_grade_code_closure');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(FREEZER,paths);codes=[ref(p)for p in sorted(paths)];validation=read(PROPOSAL/'no-worker-schema-hash-validation.json');assert validation['schemaAndSyntaxPassed']and validation['noNumericalExecution'];assert validation['codeRefs']==[ref(Path(__file__)),ref(FREEZER)];codes+=[ref(PROPOSAL/'no-worker-schema-hash-validation.json'),ref(PROPOSAL/'METHOD.md')]
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  for e in codes:assert ref(ROOT/e['path'])==e
  before=read(F.CAP/'protected-state-before.json');assert json.loads(json.dumps(F.state(before['uids']),default=str))==before['rows']
 fence()
 for name,world in worlds.items():
  sh=digest(world.tobytes());binding=d['allFourStreamBindings'][name];assert binding['wholeWorldSHA256']==sh and binding['wholeGroundSHA256']==complete.ground_sha;bindings[name]=binding
  if binding['proofTupleSHA256']in cache:continue
  prior=d['distinctCompleteFiniteProofs'][binding['proofTupleSHA256']];records=prior['allWholeFacetProofs'];assert len(records)==46918 and len(prior['ordinaryFailingFaces'])==42 and len(prior['strictUncertifiedFaces'])==443 and not prior['coverageFailingFaces']
  incidence=defaultdict(set);normals=[]
  for i,t in enumerate(world):
   normal=list(map(Q,F.exact_orientation(t)['exactNormal']));normals.append(normal)
   if any(normal):
    for j in range(3):
     edge=tuple(sorted((tuple(t[j]),tuple(t[(j+1)%3]))))
     if edge[0]!=edge[1]:incidence[edge].add(i)
  def cap(i):
   n=normals[i];return records[i]['strictPositiveFiniteProved']and n[1]>0 and 16*n[1]*n[1]>sum(v*v for v in n)
  previous=gd['distinctBoundedRouteDiagnostics'][binding['proofTupleSHA256']];assert previous['wholeWorldSHA256']==sh and previous['all42FailingSteepFaces']==prior['ordinaryFailingFaces'];oldrows={x['seedFace']:x for x in previous['routes']};assert len(oldrows)==42
  qualified=set()
  for i,x in oldrows.items():
   assert x['genuineExposedGradeDiagnostic']and x['verifiedPositiveUpperGroundIntervals']and Q(x['completeUnchangedVertexExposure']['exactExposureLowerBoundM'])>0
   for interval in x['verifiedPositiveUpperGroundIntervals']:
    proof=interval['completeUpperEnvelopeSegmentProof'];assert proof['selection']['completeGroundSHA256']==complete.ground_sha and proof['selection']['completeGroundFacetCount']==3240 and proof['closedWholeSegmentProjectionCovered']and Q(proof['exactMinimumGapM'])==0 and proof['selection']['everyNoncandidateStrictlyDisjoint'];assert len(proof['selectedGroundKernelProof']['exactEndpoints'])==2 and proof['selectedGroundKernelProof']['exactEndpoints'][0]!=proof['selectedGroundKernelProof']['exactEndpoints'][1]
   qualified.add(i)
  edges={tuple(x['faces']):copy.deepcopy(x)for x in previous['allExaminedWholeEdgeProofs']};routes=[]
  for key,x in edges.items():
   assert key==tuple(sorted(key))and len(key)==2;edge=tuple(map(tuple,x['unchangedOriginalWholeSharedEdge']));assert edge[0]!=edge[1]and set(key)<=incidence[tuple(sorted(edge))];assert x['completeFiniteEdgeProof']['selection']['completeGroundSHA256']==complete.ground_sha
  for seed in prior['ordinaryFailingFaces']:
   fence();n=normals[seed];assert any(n)and 16*n[1]*n[1]<=sum(v*v for v in n)
   old=oldrows[seed]
   if old['boundedOriginalPath']:
    routes.append(dict(copy.deepcopy(old),priorCompleteRouteReusedVerbatim=True,priorExactGradeAndExposureReused=True));continue
   grade=copy.deepcopy(old['completeGradeNomination']);verified=copy.deepcopy(old['verifiedPositiveUpperGroundIntervals']);exposure=copy.deepcopy(old['completeUnchangedVertexExposure']);genuine=seed in qualified;parent={seed:None};queue=deque([seed])if genuine else deque();examined=set();target=None
   while queue and target is None:
    current=queue.popleft()
    for j in range(3):
     edge=tuple(sorted((tuple(world[current,j]),tuple(world[current,(j+1)%3]))))
     for child in sorted(incidence.get(edge,set())-{current}):
      if child in parent or child in examined:continue
      if len(examined)>=BUDGET:continue
      examined.add(child)
      if not(records[child]['strictPositiveFiniteProved']or child in qualified)or not any(normals[child]):continue
      key=tuple(sorted((current,child)))
      if key not in edges:edges[key]=dict(faces=list(key),unchangedOriginalWholeSharedEdge=[list(p)for p in edge],completeFiniteEdgeProof=complete.segment([[str(Q(float(v)))for v in p]for p in edge]))
      if not edges[key]['completeFiniteEdgeProof']['strictlyExposedWholePositiveInterface']:continue
      parent[child]=current;queue.append(child)
      if cap(child):target=child;break
     if target is not None:break
   path=[];capcheck=None
   if target is not None:
    path=[target]
    while parent[path[-1]]is not None:path.append(parent[path[-1]])
    contexts=[dict(sourceFace=k,groundProjectionCovered=records[i]['completeProjectionCovered'],minimum=dict(minimumGapM=float(Q(records[i]['exactLowerM']))),maximumObservedGapM=float(Q(oldrows[i]['completeUnchangedVertexExposure']['exactExposureLowerBoundM']))if i in qualified else None)for k,i in enumerate(path)];t=world[path];b=dict(completeOriginalWorldTrianglesSHA256=digest(t.tobytes()),completeCurrentFacetContextsSHA256=canon(contexts),exactOriginalContactListSHA256=canon([]));capcheck=cap_paths(t,contexts,[],expected_binding=b,current_binding=b);assert capcheck['allAffectedHavePaths'];assert all(edges[tuple(sorted((x,y)))]['completeFiniteEdgeProof']['strictlyExposedWholePositiveInterface']for x,y in zip(path,path[1:]))
   routes.append(dict(seedFace=seed,completeGradeNomination=grade,verifiedPositiveUpperGroundIntervals=verified,completeUnchangedVertexExposure=exposure,genuineExposedGradeDiagnostic=genuine,boundedOriginalPath=path,exactStrictPositiveCap=target,independentExistingCapKernelDiagnostic=capcheck,examinedCandidateFaces=sorted(examined),boundedFaceBudget=BUDGET,budgetReached=len(examined)>=BUDGET,allTraversedWholeEdgesStrictlyExposed=target is not None,allNonseedPathFacesStrictPositive=target is not None and all(records[i]['strictPositiveFiniteProved']for i in path if i!=seed),allNonseedPathFacesStrictPositiveOrIndependentlyQualifiedGrade=target is not None and all(records[i]['strictPositiveFiniteProved']or i in qualified for i in path if i!=seed),priorExactGradeAndExposureReused=True,priorCompleteRouteReusedVerbatim=False))
  cache[binding['proofTupleSHA256']]=dict(wholeWorldSHA256=sh,complete46918TrueEdgeIncidenceCount=len(incidence),all42FailingSteepFaces=prior['ordinaryFailingFaces'],all443StrictUncertifiedFacesRetained=prior['strictUncertifiedFaces'],routes=routes,allExaminedWholeEdgeProofs=list(edges.values()),all42BoundedGradeCapPathsFound=all(x['boundedOriginalPath']for x in routes),other117OriginalBodyObligationsUndischarged=True,originalBodyCensusIsProvenanceOnlyForOtherWorlds=name!='original');save(LOCAL/('completed-'+name+'.json.gz'),cache[binding['proofTupleSHA256']]);print(json.dumps(dict(world=name,paths=sum(bool(x['boundedOriginalPath'])for x in routes))),flush=True)
 complete.verify_binding();fence();save(DOC/'diagnostic.json.gz',dict(uid=F.UID,sourceOnly=True,currentManifest=scope['currentManifest'],nativeCount=6649,completeFaces=46918,completeGroundFaces=3240,wholeGroundSHA256=complete.ground_sha,allFourStreamBindings=bindings,distinctBoundedRouteDiagnostics=cache,originalBodyCensus=d['originalBodyCensus'],all118OriginalBodyObligationsRetained=True,allOrdinaryAndStrictFailuresRetained=True,sourceGeometryChanges=0,terrainGeometryChanges=0,gradeRootAccepted=False,burialRoleAccepted=False,physicalAccepted=False,installationApproved=False,all42PriorGradeExposureProofsReusedWithoutRecomputation=True,existing17CompletePathsRetainedVerbatim=True,qualifiedGradeIntermediateNodesAllowed=True,evidenceRefs=[ref(F.DOC/'result.json'),ref(F.DOC/'diagnostic.json.gz'),ref(H.DOC/'result.json'),ref(H.DOC/'diagnostic.json.gz')]+codes));subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
