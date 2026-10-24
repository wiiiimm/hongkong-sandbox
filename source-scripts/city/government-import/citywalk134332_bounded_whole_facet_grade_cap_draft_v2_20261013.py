"""DRAFT: saved complete Citywalk grade/whole-edge/cap diagnostics; no acceptance."""
import argparse,json,subprocess,sys,uuid
from collections import defaultdict,deque
from fractions import Fraction as Q
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
import citywalk134332_saved_failure_source_orientation_context_draft_v2_20261013 as C
import citywalk134332_current_ground_only_supervised_draft_v1_20261013 as G
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from original_bound_facet_wall_context_v2_20261010 import exposure_at_vertex
from exact_original_projection_coverage_v2_20261010 import exact_coverage
BATCH='government-xl-citywalk134332-bounded-whole-facet-grade-cap-v2-20261013'
D=C.BASE/BATCH;LOCAL=HERE/'local'/BATCH;P=C.BASE/'government-xl-citywalk134332-bounded-whole-facet-grade-cap-proposal-v2-20261013';BUDGET=64
ref=C.ref
FREEZER=HERE/'citywalk134332_freeze_bounded_whole_facet_grade_cap_draft_v2_20261013.py'
CHUNK=32

def inputs(a):
 c,d,components,labels,worlds,ground,g=C.inputs()
 contract=read(P/'input-contract.json')
 for e in contract['refs']:assert ref(ROOT/e['path'])==e
 receipt=read(ROOT/c['finiteResult']['path'])
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 before=G.inputs(a);assert before['currentState']['observedProtectedReviewRecords']==1704 and len(before['currentState']['uids'])==19
 assert len(worlds)==4 and len(d['allSourceGroundBindings'])==12 and len(d['distinctCompleteFiniteProofs'])==3
 return c,d,components,labels,worlds,ground,g,before,contract

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args()
 c,d,components,labels,worlds,ground,g,before,contract=inputs(a)
 if a.preflight_only:
  print(json.dumps(dict(noGeometryPredicatesExecuted=True,sourceFaces=41277,originalBodies=193,groundFaces=4215,allBindings=12,distinctTuples=3,belowBoundCandidatesPerTuple=683,coverageOnlyRetained=1322,currentUIDs=19,protectedRows=1704)));return
 if not a.owned:
  assert not LOCAL.exists()and not D.exists();resources=sorted(['building:'+u for u in before['currentState']['uids']]+['native-model:'+before['currentState']['sourceKey'],'source-context:'+BATCH]);claim=reservations.claim('citywalk-grade-cap-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
  try:
   subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
  except BaseException as error:
   save(LOCAL/'failed-terminal-parent-audit.json',dict(errorType=type(error).__name__,error=str(error),noCompletedResultClaim=True));raise
  finally:
   owned=reservations.owns(lease);release=reservations.release(lease)if owned else None;save(LOCAL/'parent-release-audit.json',dict(ownedBeforeCleanup=owned,cleanupRelease=release,ownsAfterCleanup=reservations.owns(lease)))
  return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);save(LOCAL/'immutable-lease-at-start.json',lease);save(LOCAL/'protected-state-before.json',before)
 def fence():
  assert reservations.owns(lease)and G.inputs(a)==before
  for e in contract['refs']:assert ref(ROOT/e['path'])==e
  for path,h in g['inputHashes'].items():assert ref(ROOT/path)['sha256']==h
 complete=CompleteGround(ground);cache={}
 for name,w in worlds.items():
  binding=next(b for b in d['allSourceGroundBindings']if b['sourceWorld']==name and b['groundWorld']=='actualLiteral');key=binding['proofTupleSHA256']
  assert binding['sourceWorldSHA256']==digest(w.tobytes())and binding['groundWorldSHA256']==complete.ground_sha
  if key in cache:continue
  rows=d['distinctCompleteFiniteProofs'][key]['allWholeFacetProofs'];seeds=[i for i,r in enumerate(rows)if r['exactLowerM']is not None and Q(r['exactLowerM'])<Q(-1,2)];assert len(seeds)==683
  normals=[list(map(Q,C.exact_orientation(t)['exactNormal']))for t in w];incidence=defaultdict(set)
  for i,t in enumerate(w):
   if any(normals[i]):
    for j in range(3):
     edge=tuple(sorted((tuple(t[j]),tuple(t[(j+1)%3]))))
     if edge[0]!=edge[1]:incidence[edge].add(i)
  seedproofs={};edgeproofs={}
  for seed_index,seed in enumerate(seeds):
   if seed_index%CHUNK==0:fence()
   assert reservations.owns(lease);path=LOCAL/'grade'/key/f'{seed:05d}.json.gz'
   n=normals[seed];steep=bool(any(n)and 16*n[1]*n[1]<=sum(v*v for v in n));grade=complete.grade(w,seed);intervals=[]
   for group in grade['exactUpperGroundIntervals']:
    for interval in group['exactActiveUpperGroundIntervals']:
     endpoints=interval['exactSegmentEndpoints'];nonzero=endpoints[0]!=endpoints[1]
     proof=complete.segment(endpoints)if nonzero else None
     intervals.append(dict(completeOriginalGroundFace=group['originalGroundFace'],nomination=interval,nonzeroSourceSegment=nonzero,completeMAXSegmentProof=proof,positiveDimensionGradeQualified=bool(proof and proof['closedWholeSegmentProjectionCovered']and proof['exactMinimumGapM']is not None and Q(proof['exactMinimumGapM'])==0)))
   vertices=[]
   for vertex_id,v in enumerate(w[seed]):
    point=np.repeat(v[None,:],3,axis=0);coverage=exact_coverage(point,ground);exposure=exposure_at_vertex(v,ground)if coverage['exactProjectionCovered']else None
    vertices.append(dict(originalVertex=vertex_id,unchangedCoordinates=v.tolist(),completeClosedPointCoverage=coverage,completeMAXExposure=exposure,strictlyAboveCompleteMAX=bool(exposure and Q(exposure['exactExposureLowerBoundM'])>0)))
   result=dict(seed=seed,originalBody=labels[seed],steepWall=steep,closedWholeFacetProjectionCovered=rows[seed]['completeProjectionCovered'],rawFiniteProof=rows[seed],completeGradeNomination=grade,verifiedIntervals=intervals,allOriginalVertexProofs=vertices,qualifiedGradeDiagnostic=steep and any(x['positiveDimensionGradeQualified']for x in intervals)and any(x['strictlyAboveCompleteMAX']for x in vertices),rootAccepted=False)
   assert not path.exists();save(path,result);seedproofs[seed]=result
   if (seed_index+1)%CHUNK==0 or seed_index+1==len(seeds):fence()
   assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(world=name,gradeCandidatesCompleted=len(seedproofs),expected=683)),flush=True)
  routes=[]
  for seed_index,seed in enumerate(seeds):
   if seed_index%CHUNK==0:fence()
   assert reservations.owns(lease);parent={seed:None};queue=deque([seed])if seedproofs[seed]['qualifiedGradeDiagnostic']else deque();examined=set();target=None
   while queue and target is None:
    current=queue.popleft()
    for j in range(3):
     edge=tuple(sorted((tuple(w[current,j]),tuple(w[current,(j+1)%3]))))
     for child in sorted(incidence.get(edge,set())-{current}):
      if child in parent or child in examined or len(examined)>=BUDGET:continue
      examined.add(child);eligible=rows[child]['strictPositiveFiniteProved']or(child in seedproofs and seedproofs[child]['qualifiedGradeDiagnostic'])
      if not eligible or not any(normals[child]):continue
      ek=tuple(sorted((current,child)))
      if ek not in edgeproofs:edgeproofs[ek]=dict(sourceFaces=list(ek),originalWholeSharedEdge=[list(v)for v in edge],completeGroundProof=complete.segment([[str(Q(float(x)))for x in v]for v in edge]))
      if not edgeproofs[ek]['completeGroundProof']['strictlyExposedWholePositiveInterface']:continue
      parent[child]=current;queue.append(child);n=normals[child]
      if rows[child]['strictPositiveFiniteProved']and n[1]>0 and 16*n[1]*n[1]>sum(v*v for v in n):target=child;break
     if target is not None:break
   path=[]
   if target is not None:
    path=[target]
    while parent[path[-1]]is not None:path.append(parent[path[-1]])
   routes.append(dict(seed=seed,pathCapToSeed=path,strictUpwardCap=target,capSavedWholeFacetProof=rows[target]if target is not None else None,examinedCandidates=sorted(examined),budget=BUDGET,budgetReached=len(examined)>=BUDGET,missIsScopedNotNoPathProof=True,rootAccepted=False))
   assert reservations.heartbeat(lease)['ok']
   if (seed_index+1)%CHUNK==0 or seed_index+1==len(seeds):fence()
  cache[key]=dict(sourceWorld=name,wholeWorldSHA256=digest(w.tobytes()),wholeGroundSHA256=complete.ground_sha,completeTrueEdgeIncidenceCount=len(incidence),all683SeedProofs=list(seedproofs.values()),all683Routes=routes,allExaminedWholeSharedEdges=list(edgeproofs.values()),coverageOnlyFaceIDs=[i for i,r in enumerate(rows)if not r['completeProjectionCovered']and i not in seedproofs],all193BodyObligationsRetained=True,bodyLabelsAreOriginalProvenanceOnly=name!='providerOriginal')
  save(LOCAL/('completed-'+name+'.json.gz'),cache[key])
 complete.verify_binding();fence();save(D/'diagnostic.json.gz',dict(uid='landsd/134332:0',sourceOnly=True,currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,gradeRootAccepted=False,completeSourceFaces=41277,originalBodies=193,completeGroundFaces=4215,all12Bindings=d['allSourceGroundBindings'],distinctGradeCapDiagnostics=cache,all683BelowBoundRetained=True,all1322CoverageOnlyRetained=True,sourceGeometryChanges=0,terrainGeometryChanges=0,pointExposureCannotBridge=True,noNewZeroCoverageOrSeamAdmissionRule=True,evidenceRefs=contract['refs']))
 subprocess.run([sys.executable,str(FREEZER),'--expected-manifest',a.expected_manifest],cwd=ROOT,check=True);fence()
 print(json.dumps(dict(savedDiagnostic=ref(D/'diagnostic.json.gz'),gradeQualified=[sum(x['qualifiedGradeDiagnostic']for x in z['all683SeedProofs'])for z in cache.values()],capPaths=[sum(bool(x['pathCapToSeed'])for x in z['all683Routes'])for z in cache.values()])),flush=True)
if __name__=='__main__':main()
