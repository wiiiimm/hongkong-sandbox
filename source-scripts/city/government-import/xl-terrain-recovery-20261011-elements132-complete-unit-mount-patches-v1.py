"""Complete original visual-unit mounting candidates, diagnostic only.

Thirty-one exact original three-body units retain their two boundary loops,
two actual interfaces and free front geometry. The independent 39 bodies keep
every opening/boundary and every associated ORIGINAL patch; no cap is created.
Partial interior failures are not rewritten. No function, root or bridge credit.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_closed_boundary_loop_band_diagnostic_v1_20261011 import loop
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify as edge_verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements132-complete-unit-mount-patches-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1'
ASSOC=BASE/'xl-terrain-recovery-20261011-elements132-four-stream-qualified-host-association-v1'
FINITE=BASE/'xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1'
CONTEXT=BASE/'xl-terrain-recovery-20261011-elements132-remaining-original-bodies-context-v1'
ATTR=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'
UIDS=['landsd/204145:0','landsd/204143:0'];COUNTS=[12129,11680]
MODES=[('providerOriginal',None),('actualLiteral','completeLiteralWorldPosition'),('explicitLeftFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def boundary_groups(world,ids):
 edgefaces=defaultdict(list)
 for i in ids:
  for a,b in zip(world[i],np.roll(world[i],-1,axis=0)):
   if tuple(a)!=tuple(b):edgefaces[tuple(sorted([tuple(a),tuple(b)]))].append(i)
 boundary={e:r for e,r in edgefaces.items()if len(r)==1};adj=defaultdict(set)
 for a,b in boundary:adj[a].add(b);adj[b].add(a)
 remaining=set(adj);groups=[]
 while remaining:
  seen={min(remaining)};todo=list(seen)
  while todo:
   for n in adj[todo.pop()]:
    if n not in seen:seen.add(n);todo.append(n)
  remaining-=seen;edges=sorted(e for e in boundary if e[0]in seen)
  closed=len(edges)>=3 and all(len(adj[v])==2 for v in seen)
  if closed:assert loop(np.asarray(edges,float))==edges
  groups.append(dict(completeOriginalEdges=[[list(p)for p in e]for e in edges],completeIncidenceOneFacetIds=[boundary[e][0]for e in edges],completeVertexDegrees=[dict(vertex=list(v),degree=len(adj[v]))for v in sorted(seen)],closedConnectedDegreeTwoBoundary=closed,simpleOpeningOrAuthoredMountCertified=False))
 return groups
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [GRAPH,ASSOC,FINITE,CONTEXT,ATTR]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,name):
  p=folder/name;assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 graph=bound(GRAPH,'diagnostic.json.gz');assoc=bound(ASSOC,'diagnostic.json.gz');finite=bound(FINITE,'diagnostic.json.gz');ctx=bound(CONTEXT,'diagnostic.json.gz');attrs=bound(ATTR,'actual-render-attributes.json.gz')['rows']
 assert [r['uid']for r in attrs]==UIDS and all(r['unprovedStrictExposureFaces']==[]for r in finite['rows'])
 originals=[]
 for s,a,n in zip(graph['binding']['completeSourceInputs'][:2],attrs,COUNTS):
  p=ROOT/s['asset']['path'];assert ref(p)==s['asset']and digest(p.read_bytes())==s['sourceSHA256']==a['sourceSHA256'];refs.append(ref(p));t=decode_original_world_triangles(p.read_bytes());assert len(t)==n;originals.append(t)
 triplets=[[i-1,i,i+1]for i in range(393,484,3)];assert len(triplets)==31
 triplet_bodies={i for unit in triplets for i in unit};remaining=[r['originalBody']for r in ctx['all132Bodies']];other=sorted(set(remaining)-triplet_bodies);assert len(other)==39 and triplet_bodies<=set(remaining)
 saved_edges={tuple(r['components']):r for r in graph['oneExactPositiveWitnessPerOwnedInvolvingBodyPair']};assert all((u[0],u[1])in saved_edges and(u[1],u[2])in saved_edges for u in triplets)
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_original_edge_any_finite_distance_band_v2_20261010.py','exact_original_edge_any_finite_distance_band_v1_20261010.py','exact_original_perpendicular_any_facet_band_v1_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('elements132-mount-patches-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();out=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  for mode,field in MODES:
   parts=originals if field is None else [np.asarray(a[field],float).reshape(-1,3)[np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3)]for a in attrs]
   world=np.concatenate(parts);ar=next(r for r in assoc['rows']if r['mode']==mode);assert digest(world.tobytes())==ar['completeWorldSHA256'];bybody={r['originalBody']:r for r in ar['all132OriginalBodyAssociations']};assert sorted(bybody)==remaining
   fin={}
   for uid,t,offset in zip(UIDS,parts,[0,12129]):
    r=next(r for r in finite['rows']if r['mode']==mode and r['uid']==uid);assert digest(t.tobytes())==r['completeWorldSHA256'];fin.update({f['sourceFace']+offset:f for f in r['allFaces']})
   assert set(fin)==set(range(23809))and all(f['strictlyExposedWholeFacet']for f in fin.values())
   def loop_proofs(body,groups):
    host_ids=bybody[body]['completeHostSelection']['selectedGlobalHostFaces'];hosts=world[host_ids];answer=[]
    for group in groups:
     proofs=[]
     for edge in group['completeOriginalEdges']:
      if len(hosts):proof=edge_verify(edge,hosts);passed=proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']
      else:proof=dict(noSelectedFiniteHost=True,verifiedCompleteOriginalEdgeFiniteFacadeBand=False);passed=False
      proofs.append(dict(wholeOriginalEdge=edge,actualSubsetWholeEdgeHostProofVerbatim=proof,withinExistingFiniteHostBand=passed));pulse()
     answer.append(dict(**group,completeWholeEdgeHostProofs=proofs,completeFiniteHostBand=group['closedConnectedDegreeTwoBoundary']and all(p['withinExistingFiniteHostBand']for p in proofs),completeHostSelectionVerbatim=bybody[body]['completeHostSelection']))
    return answer
   def contact(a,b):
    saved=saved_edges[(a,b)];ids=saved['globalOriginalFaces'];points=intersection_points(rational_face(world[ids[0]]),rational_face(world[ids[1]]));measure=contact_measure(points)if points else None
    if field is None:assert measure==saved['exactContact'],'Original exact contact ordering must remain unchanged'
    chosen=ids if measure is not None and measure['dimension']>0 else None;attempts=[]
    if chosen is None:
     left=graph['components'][a]['globalOriginalFaces'];right=graph['components'][b]['globalOriginalFaces']
     for i in left:
      for j in right:
       t,u=world[i],world[j]
       if np.any(t.min(0)>u.max(0))or np.any(u.min(0)>t.max(0)):continue
       p=intersection_points(rational_face(t),rational_face(u));m=contact_measure(p)if p else None;attempts.append(dict(globalFaces=[i,j],exactContact=m));pulse()
       if m is not None and m['dimension']>0:chosen=[i,j];measure=m;break
      if chosen is not None:break
    return dict(originalBodies=[a,b],savedOriginalContactVerbatim=saved,savedActualContactVerbatim=contact_measure(points)if points else None,actualPositiveDimensionalContact=chosen is not None,chosenGlobalFaces=chosen,chosenActualExactContact=measure if chosen is not None else None,allSearchedActualFiniteFacePairs=attempts,completeSameBodyPairSearchIfNoWitness=chosen is None,allChosenEndpointFacetsStrictlyExposedByCompleteFiniteProof=chosen is not None and all(fin[i]['strictlyExposedWholeFacet']for i in chosen),rawSavedActualContactAlwaysPreserved=True)
   units=[]
   for unit in triplets:
    ids=sorted(f for b in unit for f in graph['components'][b]['globalOriginalFaces']);assert [len(graph['components'][b]['globalOriginalFaces'])for b in unit]==[2,16,4]and len(ids)==22
    backing=loop_proofs(unit[1],boundary_groups(world,graph['components'][unit[1]]['globalOriginalFaces']));contacts=[contact(unit[0],unit[1]),contact(unit[1],unit[2])]
    candidate=len(backing)==2 and all(len(g['completeOriginalEdges'])==4 and g['closedConnectedDegreeTwoBoundary']for g in backing)and any(g['completeFiniteHostBand']for g in backing)and all(c['actualPositiveDimensionalContact']and c['allChosenEndpointFacetsStrictlyExposedByCompleteFiniteProof']for c in contacts)
    units.append(dict(completeOriginalBodies=unit,completeOriginalFaceIds=ids,all22OriginalFacetsRetained=True,all22FacetsStrictlyExposed=True,allFrameBoundaryGroups=backing,bothBodyInterfaceProofs=contacts,diagnosticCompleteUnitBackingLoopAndContacts=candidate,allPriorPartialInteriorFailuresPreserved=[bybody[b]for b in unit],noUnitStructuralRootOrBridge=True,authoredVisualRoleAccepted=False));pulse()
   independent=[]
   for body in other:
    ids=graph['components'][body]['globalOriginalFaces'];a=bybody[body];groups=loop_proofs(body,boundary_groups(world,ids));patches=[]
    associated=a['completeAssociatedFacetPatchCensus']['sharedEdgeConnectedComponents'];whole=world[ids];bodymin=float(whole[:,:,1].min())
    for patch in associated:
     assert patch and all(next(r for r in a['allActualFacetProofs']if r['globalOriginalFace']==f)['wholeFacetWithinExistingFiniteHostBand']for f in patch)
     patchgroups=loop_proofs(body,boundary_groups(world,patch));t=world[patch]
     patches.append(dict(completeOriginalPatchFacetIds=patch,completePatchCensus=census(world,patch),completePatchBoundaryGroups=patchgroups,allPatchFacetsWithinExistingFiniteBand=True,completePatchBoundaryWithinBand=bool(patchgroups)and all(g['completeFiniteHostBand']for g in patchgroups),actualPatchBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],allPatchVerticesAtExactBodyMinimumY=bool(np.all(t[:,:,1]==bodymin)),patchConsistsOnlyOfUntouchedOriginalFacets=True,noSyntheticClosingFace=True,authoredBackingOrMountRoleAccepted=False));pulse()
    independent.append(dict(originalBody=body,completeOriginalFaceIds=ids,allCompleteBodyBoundaryGroups=groups,allAssociatedOriginalFacetPatches=patches,priorFullFacetAndBoundaryFailuresVerbatim=a,actualSourceWorldSHA256=digest(whole.tobytes()),allOriginalFacetsStrictlyExposed=True,completeAssociatedPatchCount=len(patches),functionOrSimpleOpeningCertified=False,authoredRoleAccepted=False,noStructuralRootOrBridgeCredit=True));pulse()
   assert len(units)==31 and len(independent)==39 and sorted([b for u in units for b in u['completeOriginalBodies']]+[r['originalBody']for r in independent])==remaining
   out.append(dict(mode=mode,completeWorldSHA256=digest(world.tobytes()),all31OriginalThreeBodyUnits=units,all39IndependentOriginalBodies=independent,complete132BodiesAnd3172FacesRetained=True,full23809StrictFacetProofReceipt=ref(FINITE/'result.json'),allPriorInteriorNegativesPreserved=True));pulse(True)
   print(dict(mode=mode,completeBackingLoopAndInterfaces=sum(u['diagnosticCompleteUnitBackingLoopAndContacts']for u in units),units=31,independentBodies=39),flush=True)
  assert all(ref(ROOT/r['path'])==r for r in refs);output=dict(uids=UIDS,rows=out,all132BodiesAccounted=True,all3172OriginalFacesRetained=True,sourceOnly=True,noFreshCurrentReacceptance=True,authoredRoleAccepted=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',output);pulse(True)
  spec=importlib.util.spec_from_file_location('elements132_unit_freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'elements132-complete-triplet-backing-boundaries-and-independent-original-patches-four-stream-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,sourceOnly=True,completeRemainingBodies=132,completeRemainingFaces=3172,threeBodyUnitBackingResults={r['mode']:[u['completeOriginalBodies']for u in r['all31OriginalThreeBodyUnits']if u['diagnosticCompleteUnitBackingLoopAndContacts']]for r in out},currentAcceptance=False,authoredRoleAccepted=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
