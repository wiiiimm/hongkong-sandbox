"""DRAFT: one saved unresolved seed, exact original subedge/facet corridors only."""
import argparse,itertools,json,subprocess,sys,uuid
from pathlib import Path
from fractions import Fraction as R
from run import ROOT,HERE,read,save,digest,connect,reservations
import citywalk134332_bounded_whole_facet_grade_cap_draft_v2_20261013 as Q
from west_wing26195_exact_saved_segment_exposure_draft_v1_20261012 import classify,source_segment,point,at
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
BATCH='government-xl-citywalk134332-seed10469-saved-partial-edge-corridor-v1-20261013'
D=Q.C.BASE/BATCH;LOCAL=HERE/'local'/BATCH;P=Q.C.BASE/'government-xl-citywalk134332-seed10469-partial-edge-corridor-proposal-v1-20261013'
FREEZER=HERE/'citywalk134332_freeze_seed10469_saved_partial_edge_corridor_draft_v1_20261013.py'
HELPER=HERE/'west_wing26195_exact_saved_segment_exposure_draft_v1_20261012.py'
TEST=HERE/'test_citywalk134332_seed10469_saved_partial_edge_corridor_draft_v1_20261013.py'
DIAGNOSTIC_SHA='a74144d0df2979d6bebef058880a1c30236d5892acb518a701dcfe7b74ec9cf8'
PATH=[25910,10477,10406,10465,10470,10468];MAX_ATTEMPTS=1024;ref=Q.ref
def exact(p):return [str(R(float(v))) for v in p]
def strings(p):return list(map(str,p))
def shared_edge(world,faces,ends):
 e=tuple(sorted(map(point,ends)));assert e[0]!=e[1]
 for i in faces:
  actual={tuple(sorted((tuple(map(R,exact(world[i,j]))),tuple(map(R,exact(world[i,(j+1)%3])))))) for j in range(3)}
  assert e in actual,'Require complete genuine original edge, not an interior segment'
  membership(world,i,ends)
 return dict(sourceFaces=list(faces),exactOriginalWholeEdge=ends,notPointAdjacency=True)
def select_case(z):
 seeds={s['seed']:s for s in z['all683SeedProofs']};routes={s['seed']:s for s in z['all683Routes']};edges={tuple(e['sourceFaces']):e for e in z['allExaminedWholeSharedEdges']}
 assert len(seeds)==len(routes)==683 and len(z['coverageOnlyFaceIDs'])==1322 and z['all193BodyObligationsRetained']
 for i in [10469,10468]:assert seeds[i]['qualifiedGradeDiagnostic'] and seeds[i]['originalBody']==0
 assert routes[10469]['pathCapToSeed']==[] and routes[10469]['examinedCandidates']==[10466,10468] and not routes[10469]['budgetReached']
 assert routes[10468]['pathCapToSeed']==PATH and routes[10468]['strictUpwardCap']==25910
 cap=routes[10468]['capSavedWholeFacetProof'];assert cap['strictPositiveFiniteProved'] and cap['ordinaryFiniteProved'] and cap['completeProjectionCovered']
 incoming=edges[(10468,10469)];outgoing=edges[(10468,10470)]
 assert incoming['completeGroundProof']['closedWholeSegmentProjectionCovered'] and not incoming['completeGroundProof']['strictlyExposedWholePositiveInterface']
 assert all(edges[tuple(sorted((i,j)))]['completeGroundProof']['strictlyExposedWholePositiveInterface'] for i,j in zip(PATH,PATH[1:]))
 return seeds[10469],routes[10469],routes[10468],incoming,outgoing
def route_found(subedge,grade_connector,within_donor):
 return bool(subedge['strictlyExposedWholePositiveInterface'] and grade_connector['strictPositiveExceptInitialEndpoint'] and grade_connector['initialEndpointGapM']=='0' and within_donor['strictlyExposedWholePositiveInterface'])
def validation():
 v=read(P/'test-validation.json');assert v['exactTests']==10 and v['exitCode']==0
 assert v['codeRefs']==[ref(p) for p in [Path(__file__),FREEZER,HELPER,TEST]] and ref(ROOT/v['testLog']['path'])==v['testLog']
 log=(ROOT/v['testLog']['path']).read_text();assert 'Ran 10 tests' in log and log.rstrip().endswith('OK');return [ref(P/'test-validation.json')]+v['codeRefs']+[v['testLog']]
def inputs(a):
 *prefix,before,oldcontract=Q.inputs(a);c,finite,components,labels,worlds,ground,g=prefix
 contract=read(P/'input-contract.json')
 for e in contract['refs']:assert ref(ROOT/e['path'])==e
 assert ref(Q.D/'diagnostic.json.gz')['sha256']==DIAGNOSTIC_SHA
 receipt=read(Q.D/'result.json');assert ref(Q.D/'result.json')['sha256']==a.expected_grade_result_sha
 assert receipt['sourceOnly'] and not any(receipt[k] for k in ['currentAcceptance','identityAccepted','physicalAccepted','installationApproved','gradeRootAccepted'])
 assert receipt['completeSourceFaces']==41277 and receipt['originalBodies']==193 and receipt['completeGroundFaces']==4215 and receipt['currentManifest']==before['currentState']['currentManifest']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 old=read(Q.D/'diagnostic.json.gz');assert old['all12Bindings']==finite['allSourceGroundBindings'] and len(old['distinctGradeCapDiagnostics'])==3
 assert all(labels[i]==0 for i in [10469]+PATH)
 for z in old['distinctGradeCapDiagnostics'].values():select_case(z)
 return finite,labels,worlds,ground,before,old,receipt,contract
def membership(world,i,ends):return source_segment([exact(v) for v in world[i]],ends)
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--expected-grade-result-sha',required=True);p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args();finite,labels,worlds,ground,before,old,receipt,contract=inputs(a)
 if a.preflight_only:print(json.dumps(dict(savedCaseOnly=True,noNewGroundPredicates=True,sourceFaces=41277,originalBodies=193,groundFaces=4215,all12Bindings=12,distinctTuples=3,seed=10469,donor=10468,priorCap=25910)));return
 valid=validation()
 if not a.owned:
  assert not LOCAL.exists() and not D.exists();resources=sorted(['building:'+u for u in before['currentState']['uids']]+['native-model:'+before['currentState']['sourceKey'],'source-context:'+BATCH+'-compute']);claim=reservations.claim('citywalk-seed10469-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
  try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
  except BaseException as e:save(LOCAL/'failed-parent-audit.json',dict(errorType=type(e).__name__,error=str(e),noAcceptance=True));raise
  finally:
   owned=reservations.owns(lease);released=reservations.release(lease) if owned else None;save(LOCAL/'parent-release-audit.json',dict(ownedBeforeCleanup=owned,cleanupRelease=released,ownsAfterCleanup=reservations.owns(lease)))
  return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);save(LOCAL/'immutable-lease-at-start.json',lease);save(LOCAL/'protected-state-before.json',before);codes=[ref(Path(__file__)),ref(FREEZER),ref(HELPER),ref(P/'METHOD.md')]+valid;complete=CompleteGround(ground);results={}
 def fence():
  assert reservations.owns(lease) and inputs(a)[4]==before
  for e in codes+contract['refs']:assert ref(ROOT/e['path'])==e
 fence()
 for mode,world in worlds.items():
  b=next(b for b in old['all12Bindings'] if b['sourceWorld']==mode and b['groundWorld']=='actualLiteral');key=b['proofTupleSHA256']
  assert digest(world.tobytes())==b['sourceWorldSHA256'] and complete.ground_sha==b['groundWorldSHA256']
  if key in results:continue
  z=old['distinctGradeCapDiagnostics'][key];seed,miss,donor,incoming,outgoing=select_case(z)
  ends=[exact(v) for v in incoming['originalWholeSharedEdge']];exitends=[exact(v) for v in outgoing['originalWholeSharedEdge']]
  shared_edge(world,[10469,10468],ends);shared_edge(world,[10468,10470],exitends);ex=classify(incoming['completeGroundProof'],expected_ground_sha=complete.ground_sha,expected_ground_faces=4215,expected_endpoints=ends)
  exitpoint=strings(at(*map(point,exitends),R(1,2)));parts=[]
  for n in ex['positiveLengthExposedNominees']:
   proof=complete.segment(n['exactEndpoints']);parts.append(dict(n,completeGroundSegmentCertificate=proof,strictPositive=proof['strictlyExposedWholePositiveInterface']))
  anchors=sorted({at(*map(point,v['nomination']['exactSegmentEndpoints']),R(1,2)) for v in seed['verifiedIntervals'] if v['positiveDimensionGradeQualified']});eligible=[n for n in parts if n['strictPositive']]
  assert len(anchors)*len(eligible)<=MAX_ATTEMPTS;attempts=[]
  for index,(anchor,n) in enumerate(itertools.product(anchors,eligible)):
   if index%8==0:fence()
   assert reservations.owns(lease);start=[strings(anchor),n['representativePoint']];middle=[n['representativePoint'],exitpoint]
   if point(start[0])==point(start[1]) or point(middle[0])==point(middle[1]):attempts.append(dict(pointOnlyRejected=True,gradeAnchor=strings(anchor),incomingSubsegment=n));continue
   sm=membership(world,10469,start);mm=membership(world,10468,middle);sp=complete.segment(start);mp=complete.segment(middle);sx=None;ok=False
   if sp['closedWholeSegmentProjectionCovered'] and sp['exactMinimumGapM'] is not None and R(sp['exactMinimumGapM'])==0 and not any(v.get('collapsedProjectionConservative') for v in sp['selectedGroundKernelProof']['allFinitePieces']):
    sx=classify(sp,expected_ground_sha=complete.ground_sha,expected_ground_faces=4215,expected_endpoints=start);ok=route_found(n['completeGroundSegmentCertificate'],sx,mp)
   attempts.append(dict(exactGradeAnchor=strings(anchor),incomingSubsegment=n,seedFacetMembership=sm,donorFacetMembership=mm,gradeToSubedgeCertificate=sp,gradeToSubedgeExposure=sx,withinDonorCertificate=mp,routeFound=ok,wholeFacetStrictCredit=False));assert reservations.heartbeat(lease)['ok']
  results[key]=dict(sourceWorld=mode,sourceWorldSHA256=b['sourceWorldSHA256'],groundSHA256=complete.ground_sha,seedGradeReusedVerbatim=seed,priorUnresolvedRouteReusedVerbatim=miss,donorPathReusedVerbatim=donor,wholeEdgeNegativePreservedVerbatim=incoming,outgoingWholeEdgePositiveReusedVerbatim=outgoing,exactSubedgeExposure=ex,allSubedgeCertificates=parts,allBoundedAttempts=attempts,routeFound=any(v.get('routeFound',False) for v in attempts),allOther682SeedObligationsUnchanged=True,all1322CoverageOnlyUnchanged=True,all193BodyRolesUnqualified=True,rootAccepted=False);save(LOCAL/('completed-'+mode+'.json.gz'),results[key]);print(json.dumps(dict(world=mode,attempts=len(attempts),routeFound=results[key]['routeFound'])),flush=True);fence()
 complete.verify_binding();fence();save(D/'diagnostic.json.gz',dict(uids=['landsd/134332:0'],sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,gradeRootAccepted=False,completeSourceFaces=41277,originalBodies=193,completeGroundFaces=4215,all12Bindings=old['all12Bindings'],distinctBoundedCorridorDiagnostics=results,all683RawFailuresPreserved=True,all1322CoverageOnlyPreserved=True,all193BodyObligationsPreserved=True,sourceGeometryChanges=0,terrainGeometryChanges=0,noGradeFiniteOrContactReplay=True,evidenceRefs=codes+contract['refs']+[ref(Q.D/'result.json'),ref(Q.D/'diagnostic.json.gz')]));subprocess.run([sys.executable,str(FREEZER),'--expected-manifest',a.expected_manifest,'--expected-grade-result-sha',a.expected_grade_result_sha],cwd=ROOT,check=True)
if __name__=='__main__':main()
