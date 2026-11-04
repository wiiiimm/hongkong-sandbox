"""Diagnostic-only actual Twin assembly paths from independently measured P363 grade.
All original bodies/zeros remain accounted. Each credited original body must
remain one nonzero shared-edge body in the actual arithmetic mode. Each path
interface needs an exact positive-dimensional contact, two strictly exposed
complete endpoint facets, and whole finite-ground interface exposure against
both actor captures. Original graph nominations never supply automatic roots.
"""
from pathlib import Path
from collections import defaultdict, deque
from fractions import Fraction as F
import copy, importlib.util, time, uuid
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-twin-regency-bounded-four-stream-current-podium-paths-v1';DOC=BASE/BATCH
CROSS=BASE/'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2'
GRAPH=BASE/'xl-terrain-recovery-20261011-twin-regency-complete-internal-original-contact-graph-v1'
FINITE=BASE/'xl-terrain-recovery-20261011-twin-regency-pair-current-four-stream-finite-grade-v1'
ATTR=BASE/'xl-terrain-recovery-20261011-twin-regency-two-current-render-attribute-capture-v1'
PROPOSED=BASE/'government-xl-terrain-recovery-twin-regency-pair-proposed-ground-capture-v1-20261011'
UIDS=['landsd/222465:0','landsd/223206:0'];COUNTS=[13063,456];SEED=1091
MODES=[('providerOriginal',None),('capturedLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [CROSS,GRAPH,FINITE,ATTR,PROPOSED]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,p):
  assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 cross=bound(CROSS,CROSS/'diagnostic.json.gz');graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');finite=bound(FINITE,FINITE/'diagnostic.json.gz');attrs=bound(ATTR,ATTR/'actual-render-attributes.json.gz')['rows'];runtime=bound(PROPOSED,HERE/'local'/PROPOSED.name/'runtime-geometry.json.gz')['rows']
 assert [r['uid']for r in attrs]==[r['uid']for r in runtime]==UIDS
 sourceparts=[]
 for src,a,count in zip(cross['completeSourceInputs'],attrs,COUNTS):
  assert src['uid']==a['uid'] and src['asset']['sha256']==src['wholePOSITION']['sourceSHA256']==a['sourceSHA256'];asset=ROOT/src['asset']['path'];assert ref(asset)==src['asset'];refs.append(ref(asset));w=decode_original_world_triangles(asset.read_bytes());assert len(w)==count;sourceparts.append(w)
 original=np.concatenate(sourceparts);assert digest(original.tobytes())==cross['completeOriginalWorldSHA256']==graph['fullOriginalWorldSHA256']
 bodies=[b['globalOriginalFaces']for b in cross['bodies']];zeros=cross['exactNonrenderingGlobalFacesRetainedUncredited'];assert len(bodies)==1120 and len(zeros)==8
 assert sorted([i for b in bodies for i in b]+zeros)==list(range(13519)) and len(bodies[SEED])==363
 edges={tuple(r['components']):r for r in graph['oneExactPositiveNominationPerWithinActorBodyPair']+cross['oneExactPositiveNominationPerCrossActorBodyPair']};assert len(edges)==1305;adj=defaultdict(set)
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 candidates=set(graph['purelyGeometricConnectivityFromNamedMainBodies']);assert len(candidates)==877 and SEED in candidates
 unconnected=graph['remainingBodiesOutsideThatGeometricGraph'];assert len(unconnected)==243 and candidates|set(unconnected)==set(range(1120))
 grounds=[np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3)for r in runtime];prepared=[CompleteGround(g)for g in grounds]
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_closed_ground_aabb_pruning_v1_20261011.py','exact_original_rational_interface_segment_clearance_20261011.py','exact_original_upper_ground_interfaces_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('twin-current-paths-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[];pure_cache={}
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  for mode,field in MODES:
   parts=sourceparts if field is None else [np.asarray(a[field],float).reshape(-1,3)[np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3)]for a in attrs];world=np.concatenate(parts);wsha=digest(world.tobytes());fr=[next(r for r in finite['rows']if r['uid']==u and r['mode']==mode)for u in UIDS]
   assert all(digest(w.tobytes())==r['completeWorldSHA256'] and p.ground_sha==r['completeActualDrawnGroundSHA256'] and not r['unprovedOrdinaryFaces']for w,r,p in zip(parts,fr,prepared))
   cachekey=(wsha,tuple(p.ground_sha for p in prepared))
   if cachekey in pure_cache:
    reused=copy.deepcopy(pure_cache[cachekey]);reused['mode']=mode;reused['exactNumericReuseFromWorldAndGroundHashes']=True;rows.append(reused);pulse(True);continue
   ctx=fr[0]['completeAllOriginalFacetContexts']+fr[1]['completeAllOriginalFacetContexts'];eligible=set();members={};nonzero={};censuses=[]
   for i,ids in enumerate(bodies):
    inv=census(world,ids);groups=inv['sharedEdgeConnectedComponents'];censuses.append(dict(originalBody=i,completeActualEdgeCensus=inv));nonzero[i]=[f for g in groups for f in g]
    if len(groups)==1:eligible.add(i)
    for k,group in enumerate(groups):
     for f in group:members[f]=(i,k)
    pulse()
   zero_census=census(world,zeros);grade=fr[1]['complete363MainPodiumGradeInterfaces'];cap=fr[1]['strictPodiumClearCapWallPaths']
   assert len(grade)==30 and all(13063+i['sourceFace'] in bodies[SEED] for i in grade)
   assert all(i['exactActiveUpperGroundIntervals']and all(j['upperEnvelopeCertifiedOnOpenInterval']for j in i['exactActiveUpperGroundIntervals'])for i in grade)
   seed_ok=SEED in eligible and cap['allAffectedHavePaths'] is True and not cap['rawExposureFailures'] and all(fr[1]['allFaces'][i-13063]['completeOriginalBoundProved']for i in bodies[SEED])
   seed=dict(originalBody=SEED,completeActualMainPodiumBodyCensus=censuses[SEED],complete363FacetProofReceipt=ref(FINITE/'result.json'),exactGenuineGradeIntervals=grade,strictCapPathsVerbatim=cap,capAffectedCount=len(cap['affectedOriginalWallFaces']),vacuousCapIsNotIndependentCapCredit=not cap['affectedOriginalWallFaces'],diagnosticGradeSeedQualified=seed_ok)
   rational={};trees={};attempts={};tested=0
   def exact(i):
    if i not in rational:rational[i]=rational_face(world[i])
    return rational[i]
   def strict(i):return ctx[i]['groundProjectionCovered']is True and F(ctx[i]['exactCertifiedLowerClearanceM'])>0
   def qualify(a,b):
    nonlocal tested
    key=tuple(sorted([a,b]))
    if key in attempts:return attempts[key]
    saved=edges[key];sf=saved['globalOriginalFaces'];record=dict(originalBodies=list(key),savedOriginalWitness=saved,savedActualContact=None,qualifiedExactInterface=False,alternateSearchComplete=False,actualEndpointBodiesContinuous=all(i in eligible for i in key),pointOnlyCandidatePairsExcluded=0)
    if not record['actualEndpointBodiesContinuous']:record['reason']='original-body-not-one-nonzero-actual-edge-body';attempts[key]=record;return record
    def pair(i,j):
     nonlocal tested
     if i not in members or j not in members:return None
     assert {members[i][0],members[j][0]}==set(key);tested+=1;pulse();points=intersection_points(exact(i),exact(j));measure=contact_measure(points)if points else None
     if not measure or measure['dimension']<=0:
      if measure:record['pointOnlyCandidatePairsExcluded']+=1
      return None
     if not(strict(i)and strict(j)):return None
     actorids=sorted({0 if f<13063 else 1 for f in [i,j]});interfaces=[dict(actor=UIDS[k],proof=prepared[k].segment([measure['exactPoints'][0],measure['exactPoints'][-1]]))for k in actorids]
     if not all(r['proof']['strictlyExposedWholePositiveInterface']for r in interfaces):return None
     return dict(actualGlobalFaces=[i,j],actualEndpointBodyMembership=[members[i],members[j]],actualExactContact=measure,completeStrictEndpointFacetContexts=[ctx[i],ctx[j]],wholeInterfaceAgainstBothActorGrounds=interfaces,allPointsExposedByCompleteEndpointFacets=True)
    if all(i in members for i in sf):
     p=intersection_points(exact(sf[0]),exact(sf[1]));record['savedActualContact']=contact_measure(p)if p else None
    if field is None:assert record['savedActualContact']==saved['exactContact'],'Exact original point ordering/value retained'
    witness=pair(*sf)
    if witness is None:
     left,right=nonzero[key[0]],nonzero[key[1]];small,large=(left,right)if len(left)<=len(right)else(right,left);largebody=key[0]if large is left else key[1]
     if largebody not in trees:
      ids=np.asarray(large,int);t=world[ids];trees[largebody]=(ids,shapely.STRtree(shapely.box(t[:,:,0].min(1),t[:,:,2].min(1),t[:,:,0].max(1),t[:,:,2].max(1))))
     ids,tree=trees[largebody]
     for i in small:
      t=world[i]
      for k in sorted(map(int,tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())))):
       j=int(ids[k]);u=world[j]
       if np.any(t.min(0)>u.max(0))or np.any(u.min(0)>t.max(0)):continue
       witness=pair(i,j)
       if witness:break
      if witness:break
     record['alternateSearchComplete']=witness is None;record['completeSameOriginalBodyFaceInventory']=[bodies[i]for i in key]
    if witness:record.update(qualifiedExactInterface=True,witness=witness)
    else:record['reason']='no-strict-whole-positive-interface-in-complete-actual-body-pair'
    attempts[key]=record;return record
   reached={SEED}if seed_ok else set();parents={};q=deque(sorted(reached))
   while q:
    parent=q.popleft()
    for child in sorted(adj[parent]):
     if child in reached or child not in candidates:continue
     proof=qualify(parent,child)
     if proof['qualifiedExactInterface']:parents[child]=dict(parent=parent,proofKey=list(sorted([parent,child])));reached.add(child);q.append(child)
    pulse()
   assert set(parents)==reached-({SEED}if seed_ok else set())
   for child in parents:
    seen=set();cur=child
    while cur!=SEED:assert cur not in seen and cur in parents;seen.add(cur);cur=parents[cur]['parent']
   row=dict(mode=mode,completeWorldSHA256=wsha,completeActorGroundSHA256=[p.ground_sha for p in prepared],completeOriginalFaces=13519,completeOriginalBodies=1120,completeActualCensusForEveryOriginalBody=censuses,all8SourceZeroFacetsRetainedUncredited=zeros,actualSourceZeroRepresentation=zero_census,mainPodiumGenuineGradeSeed=seed,qualifiedDiagnosticBodyIDs=sorted(reached),qualifiedDiagnosticParentForest=parents,unprovedGeometricCandidates=sorted(candidates-reached),all243SourceGraphUnconnectedBodyIDs=unconnected,allAttemptedOriginalPairs=list(attempts.values()),allUncreditedOriginalPairs=[list(k)for k in edges if k not in attempts or not attempts[k]['qualifiedExactInterface']],actualFacePairsTested=tested,exactNumericReuseFromWorldAndGroundHashes=False,noVisualRootOrBridgeCredit=True,currentAcceptance=False)
   rows.append(row);pure_cache[cachekey]=row;pulse(True);print(dict(mode=mode,qualifiedDiagnosticBodies=len(reached),unprovedGeometricCandidates=len(candidates-reached),actualFacePairsTested=tested),flush=True)
  for p in prepared:p.verify_binding()
  assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=UIDS,rows=rows,all1120OriginalBodiesAccounted=True,all8OriginalZerosUncredited=True,all243IndependentResidualRolesRequired=True,sourceOnlyFrozenCandidateGroundDiagnostic=True,currentAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);pulse(True)
  spec=importlib.util.spec_from_file_location('twin_path_freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete1120-original-body-four-stream-qualified-podium-path-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,qualifiedDiagnosticBodies={r['mode']:len(r['qualifiedDiagnosticBodyIDs'])for r in rows},currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
