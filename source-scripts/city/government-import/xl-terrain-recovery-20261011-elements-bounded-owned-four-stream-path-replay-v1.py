"""Bounded owned paths from twelve independently diagnosed native interfaces.

All owned bodies/facets remain present. Native998 is not a blanket seed. Only
the twelve interfaces positive in every saved arithmetic mode nominate roots.
Every new path edge needs actual positive-dimensional contact, strict whole
endpoint facets and the whole exact interface. Alternate face pairs are sought
inside the complete same original body pair, never by a tolerance or welding.
Whole-body finite proof and architecture/body roles remain separate obligations.
"""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as F
import importlib.util,time,uuid
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse_verify
from exact_original_paired_finite_clearance_v3_20261011 import verify as paired_verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements-bounded-owned-four-stream-path-replay-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1'
CAPS=BASE/'xl-terrain-recovery-20261011-elements998-bounded-four-stream-grade-cap-paths-v1'
OWNATTR=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'
NATIVEATTR=BASE/'xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1'
UIDS=['landsd/204145:0','landsd/204143:0'];COUNTS=[12129,11680]
MODES=[('providerOriginal',None),('actualLiteral','completeLiteralWorldPosition'),('explicitLeftFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [GRAPH,CAPS,OWNATTR,NATIVEATTR]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,p):
  assert ref(p) in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');caps=bound(CAPS,CAPS/'diagnostic.json.gz');attrs=bound(OWNATTR,OWNATTR/'actual-render-attributes.json.gz')['rows'];native=bound(NATIVEATTR,NATIVEATTR/'native-render-ground.json.gz')['rows'][0]
 assert [r['uid']for r in attrs]==UIDS and native['uid']=='landsd/273061:0'
 assert [r['mode']for r in caps['rows']]==[m for m,_ in MODES]
 ground=np.asarray(native['drawnGroundGeometry'],float).reshape(-1,3,3);prepared=CompleteGround(ground);assert len(ground)==365886
 sources=graph['binding']['completeSourceInputs'];original=[]
 for row,a,count in zip(sources[:2],attrs,COUNTS):
  assert row['uid']==a['uid'] and row['sourceSHA256']==a['sourceSHA256'];p=ROOT/row['asset']['path'];assert ref(p)==row['asset'];refs.append(ref(p));t=decode_original_world_triangles(p.read_bytes());assert len(t)==count;original.append(t)
 original=np.concatenate(original);bodies=[r['globalOriginalFaces']for r in graph['components'][:998]]
 assert len(original)==23809 and len(bodies)==998
 sourcezero=[i for i in graph['exactNonrenderingGlobalFacesRetained']if i<23809]
 assert sorted([i for body in bodies for i in body]+sourcezero)==list(range(23809))and len(sourcezero)==47
 seeds=set.intersection(*[{r['ownedBody']for r in row['all20OriginalInterfacesAccounted']if r['diagnosticStrictGradeCapPath']}for row in caps['rows']]);assert seeds=={4,499,503,504,506,911,915,916,923,924,925,926}
 edges={tuple(r['components']):r for r in graph['oneExactPositiveWitnessPerOwnedInvolvingBodyPair']if r['components'][1]<998};adj=defaultdict(set)
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 geometric=set(seeds);q=deque(sorted(seeds))
 while q:
  for other in sorted(adj[q.popleft()]):
   if other not in geometric:geometric.add(other);q.append(other)
 assert len(geometric)==866;unreached=sorted(set(range(998))-geometric);assert len(unreached)==132
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_closed_ground_aabb_pruning_v1_20261011.py','exact_original_rational_interface_segment_clearance_20261011.py','exact_original_upper_ground_interfaces_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_closed_projection_intersection_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers);bound(NATIVEATTR,NATIVEATTR/'historical-current-manifest.json')
 claim=reservations.claim('elements-owned-paths-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();out=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  for mode,field in MODES:
   parts= [original[:12129],original[12129:]] if field is None else [np.asarray(a[field],float).reshape(-1,3)[np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3)]for a in attrs]
   world=np.concatenate(parts);assert len(world)==23809 and np.isfinite(world).all();caprow=next(r for r in caps['rows']if r['mode']==mode)
   assert all(digest(p.tobytes())==caprow['completeWorldSHA256'][u]for p,u in zip(parts,UIDS))and prepared.ground_sha==caprow['completeGroundSHA256']
   census_rows=[];eligible=set();actual_members={};nonzero_faces={}
   for i,ids in enumerate(bodies):
    inv=census(world,ids);census_rows.append(dict(originalBody=i,completeActualBodyCensus=inv));groups=inv['sharedEdgeConnectedComponents'];nonzero_faces[i]=sorted(f for group in groups for f in group)
    if len(groups)==1:eligible.add(i)
    for group_id,group in enumerate(groups):
     for f in group:actual_members[f]=(i,group_id)
    if i%50==0:pulse()
   actual_source_zero_census=census(world,sourcezero)
   actor_regions=[];face_actor=np.concatenate([np.zeros(12129,dtype=int),np.ones(11680,dtype=int)])
   for part in parts:
    lo=part.min((0,1));hi=part.max((0,1));capture=native['groundCaptureBounds'];assert capture[0]<=lo[0]<=hi[0]<=capture[2]and capture[1]<=lo[2]<=hi[2]<=capture[3]
    ids,selection=prepared.select([[str(F(float(v)))for v in p]for p in [lo,hi]]);assert len(ids);actor_regions.append((ids,selection,ground[ids]))
   finite_cache={};rational={};trees={};attempts={};tested=0
   def finite(i):
    if i not in finite_cache:
     ids,selection,subset=actor_regions[int(face_actor[i])];coarse=coarse_verify(world[i],subset);paired=None
     if not(coarse['groundProjectionCovered']is True and F(coarse['exactCertifiedLowerClearanceM'])>0):paired=paired_verify(world[i],subset)
     p=paired if paired is not None else coarse;finite_cache[i]=dict(sourceFace=i,wholeActorGroundSelection=selection,selectedGroundSHA256=digest(subset.tobytes()),subsetCoarseProofVerbatim=coarse,subsetPairedProofVerbatim=paired,strictlyExposedWholeFacet=p['groundProjectionCovered']is True and F(p['exactCertifiedLowerClearanceM'])>0);pulse()
    return finite_cache[i]
   def exact(i):
    if i not in rational:rational[i]=rational_face(world[i])
    return rational[i]
   def qualify(a,b):
    nonlocal tested
    key=tuple(sorted([a,b]))
    if key in attempts:return attempts[key]
    saved=edges[key];saved_faces=saved['globalOriginalFaces'];record=dict(originalBodies=list(key),savedOriginalWitness=saved,savedActualContact=None,qualifiedExactInterface=False,alternateSearchComplete=False,actualEndpointBodyContinuity=all(i in eligible for i in key),pointOnlyCandidatePairsExcluded=0)
    if not record['actualEndpointBodyContinuity']:record['reason']='original-body-splits-or-has-no-renderable-actual-edge-body';attempts[key]=record;return record
    def try_pair(i,j):
     nonlocal tested
     if i not in actual_members or j not in actual_members:return None
     tested+=1;pulse();points=intersection_points(exact(i),exact(j));measure=contact_measure(points)if points else None
     if not measure or measure['dimension']<=0:
      if measure:record['pointOnlyCandidatePairsExcluded']+=1
      return None
     if not(finite(i)['strictlyExposedWholeFacet']and finite(j)['strictlyExposedWholeFacet']):return None
     interface=prepared.segment([measure['exactPoints'][0],measure['exactPoints'][-1]])
     if not interface['strictlyExposedWholePositiveInterface']:return None
     return dict(actualGlobalFaces=[i,j],actualExactContact=measure,completeEndpointFacetProofs=[finite(i),finite(j)],wholePositiveInterfaceProof=interface,allPointsExposedByCompleteEndpointFacets=True)
    if all(i in actual_members for i in saved_faces):
     p=intersection_points(exact(saved_faces[0]),exact(saved_faces[1]));record['savedActualContact']=contact_measure(p)if p else None
    if field is None:assert record['savedActualContact']==saved['exactContact'],'Original ordering/value must remain exact'
    witness=try_pair(*saved_faces)
    if witness is None:
     left,right=nonzero_faces[key[0]],nonzero_faces[key[1]];small,large=(left,right)if len(left)<=len(right)else(right,left);large_body=key[0]if large is left else key[1]
     if large_body not in trees:
      ids=np.asarray(large,int);t=world[ids];trees[large_body]=(ids,shapely.STRtree(shapely.box(t[:,:,0].min(1),t[:,:,2].min(1),t[:,:,0].max(1),t[:,:,2].max(1))))
     ids,tree=trees[large_body]
     for i in small:
      t=world[i]
      for k in sorted(map(int,tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())))):
       j=int(ids[k]);u=world[j]
       if np.any(t.min(0)>u.max(0))or np.any(u.min(0)>t.max(0)):continue
       witness=try_pair(i,j)
       if witness:break
      if witness:break
     record['alternateSearchComplete']=witness is None
     record['completeSameOriginalBodyFaceInventory']=[bodies[i]for i in key];record['actualNonzeroCandidateFaceInventory']=[nonzero_faces[i]for i in key]
     record['candidateSearchPolicy']='All nonzero faces of both complete original bodies, closed inclusive actual face bounds; only strictly disjoint boxes excluded.'
    if witness:record.update(qualifiedExactInterface=True,witness=witness)
    else:record['reason']='no-strict-whole-positive-interface-in-complete-actual-body-pair'
    attempts[key]=record;return record
   anchors=[];reached=set();parents={};queue=deque()
   for seed in sorted(seeds):
    r=next(r for r in caprow['all20OriginalInterfacesAccounted']if r['ownedBody']==seed);assert r['diagnosticStrictGradeCapPath']and r['actualPositiveDimensionalContact'];owner_face=r['originalContact']['globalOriginalFaces'][0]
    item=dict(originalBody=seed,wholeBoundedNativePath=r,ownedEndpointWholeFacet=finite(owner_face),actualBodyContinuous=seed in eligible,endpointIsActualNonzeroBodyFace=owner_face in actual_members and actual_members[owner_face][0]==seed)
    item['diagnosticQualifiedSeed']=item['actualBodyContinuous']and item['endpointIsActualNonzeroBodyFace']and item['ownedEndpointWholeFacet']['strictlyExposedWholeFacet'];anchors.append(item)
    if item['diagnosticQualifiedSeed']:reached.add(seed);queue.append(seed)
   while queue:
    parent=queue.popleft()
    for child in sorted(adj[parent]):
     if child in reached or child not in geometric:continue
     proof=qualify(parent,child)
     if proof['qualifiedExactInterface']:parents[child]=dict(parent=parent,proofKey=list(sorted([parent,child])));reached.add(child);queue.append(child)
    pulse()
   qualified_seeds={r['originalBody']for r in anchors if r['diagnosticQualifiedSeed']};assert set(parents)==reached-qualified_seeds
   for child in parents:
    visited=set();cur=child
    while cur not in qualified_seeds:
     assert cur not in visited and cur in parents;visited.add(cur);cur=parents[cur]['parent']
   rows=dict(mode=mode,completeWorldSHA256=digest(world.tobytes()),completeOwnedFacetCount=23809,completeOriginalBodyCount=998,completeActualCensusForEveryOriginalBody=census_rows,sourceOriginalZeroFacetsRetained=sourcezero,actualRepresentationOfSourceZeroFacets=actual_source_zero_census,qualifiedNativeInterfaceNominations=anchors,completeOwnedSourceGraphGeometricCandidates=sorted(geometric),sourceGraphUnreached132OriginalBodies=unreached,qualifiedDiagnosticOwnedBodies=sorted(reached),qualifiedDiagnosticParentForest=parents,unprovedGeometricCandidateBodies=sorted(geometric-reached),allAttemptedOriginalOwnedPairs=list(attempts.values()),uncreditedSavedOriginalOwnedPairs=[list(k)for k in edges if k not in attempts or not attempts[k]['qualifiedExactInterface']],actualFacePairsTested=tested,completeNativeGroundSHA256=prepared.ground_sha,wholeBodyAllFacetFiniteProofSeparateObligation=True,noWholeNativeBodySeed=True,rootOrStructuralCredit=False,currentAcceptance=False);out.append(rows);pulse(True);print(dict(mode=mode,qualifiedDiagnosticBodies=len(reached),sourceCandidates=866,actualPairsTested=tested),flush=True)
  prepared.verify_binding();assert all(ref(ROOT/r['path'])==r for r in refs);output=dict(uids=UIDS,rows=out,completeOwnedOriginalFaces=23809,completeOwnedOriginalBodies=998,all47OriginalZeroFacesPreservedUncredited=True,all132IndependentBodyRolesRemainRequired=True,allUnusedNativeInterfacesPreservedUncredited=True,sourceOnly=True,frozenBaselineManifest=ref(NATIVEATTR/'historical-current-manifest.json'),rootOrStructuralContactCredit=False,nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',output);pulse(True)
  spec=importlib.util.spec_from_file_location('elements_owned_path_freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'elements-bounded866-owned-four-stream-strict-exact-interface-path-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,sourceOnly=True,qualifiedDiagnosticOwnedBodies={r['mode']:len(r['qualifiedDiagnosticOwnedBodies'])for r in out},all132IndependentRolesRemainRequired=True,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
