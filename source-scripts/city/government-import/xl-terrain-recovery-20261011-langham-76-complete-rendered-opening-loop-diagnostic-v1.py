"""Complete 76 original panels and literal/two F32 authored host loops.

Every loop is reconstituted by original face/vertex correspondence; exact
global rendered incidence and whole source finite proofs are independently
bound. Native and host grounded-path approval remains a separate prerequisite.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_triangular_opening_panel_source_role_v1_20261011 import verify,canonical
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-langham-76-complete-rendered-opening-loop-diagnostic-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PROPOSAL=BASE/'xl-terrain-recovery-20261011-langham-original-76-opening-panel-source-proposal-v1'
LOOPS=BASE/'xl-terrain-recovery-20261011-langham-single-panel-original-host-boundary-loops-v1'
ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
FINITE=BASE/'xl-terrain-recovery-20261011-langham-owned-current-four-stream-finite-v1'
HOSTS=BASE/'xl-terrain-recovery-20261011-langham-565-complete-literal-rooted-host-search-v1'
BOUNDED=BASE/'xl-terrain-recovery-20261011-langham-native963-bounded-exposed-paths-v1'
UID='landsd/79318:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PROPOSAL,LOOPS,ACTUAL,FINITE,HOSTS,BOUNDED]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).exists())
 proposal=read(PROPOSAL/'diagnostic.json.gz');assert proposal['completeOriginalFaces']==18086
 loops=read(LOOPS/'diagnostic.json.gz');actual=next(r for r in read(ACTUAL/'actual-render-attributes.json.gz')['rows']if r['uid']==UID)
 assert actual['uid']==UID and actual['sourceSHA256']==proposal['sourceSHA256']
 asset=next(ROOT/r['path']for r in proposal['evidenceRefs']if r['sha256']==proposal['sourceSHA256'])
 assert digest(asset.read_bytes())==proposal['sourceSHA256'];original=decode_original_world_triangles(asset.read_bytes())
 assert digest(original.tobytes())==proposal['completeOriginalWorldSHA256']
 index=np.asarray(actual['completeOriginalIndex'],int).reshape(-1,3)
 names=['actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
 keys=['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']
 worlds=[np.asarray(actual[k]).reshape(-1,3)[index]for k in keys]
 assert all(w.shape==(18086,3,3)and np.isfinite(w).all()for w in worlds)
 completefinite=read(FINITE/'diagnostic.json.gz');assert completefinite['uid']==UID and completefinite['allOwnedFullFiniteBoundsProved']
 hostset=set(read(HOSTS/'diagnostic.json.gz')['completeAllowedLiteralGeometricHostBodies'])
 refs.extend(ref(p)for p in [asset,ACTUAL/'actual-render-attributes.json.gz',
  HERE/'original_triangular_opening_panel_source_role_v1_20261011.py',HERE/'test_original_triangular_opening_panel_source_role_v1_20261011.py',
  HERE/'exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',
  HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 claim=reservations.claim('langham76-complete-actual-loops-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];records=[];last=time.monotonic()
 try:
  for mode,world in zip(names,worlds):
   finite=next(r for r in completefinite['rows']if r['mode']==mode)
   assert not finite['unprovedFaces']and finite['completeWorldSHA256']==digest(world.tobytes())and len(finite['allFaces'])==18086
   assert all(r['proof']['groundProjectionCovered']and r['proof']['existingOrdinaryClearanceBoundProved']and r['proof']['sourceFaceSHA256']==digest(world[r['sourceFace']].tobytes())for r in finite['allFaces'])
   checkpoint=LOCAL/(mode+'-partial.json.gz');binding=dict(producer=ref(Path(__file__)),worldSHA256=digest(world.tobytes()),proposal=ref(PROPOSAL/'diagnostic.json.gz'),actual=ref(ACTUAL/'actual-render-attributes.json.gz'),kernel=ref(HERE/'original_triangular_opening_panel_source_role_v1_20261011.py'))
   old=read(checkpoint)if checkpoint.exists()else None;assert old is None or old['binding']==binding
   rows=[]if old is None else old['rows'];assert len(rows)<=76
   for r in proposal['complete76ConditionalSourcePanelProposals'][len(rows):]:
    group=loops['completeOriginalHostBoundaryGroups'][r['originalHostBoundaryGroup']];edges=[];correspondences=[]
    for e in group['allOriginalHostBoundaryEdges']:
     assert len(e['completeOriginalHostIncidences'])==1;face=e['completeOriginalHostIncidences'][0]['originalHostFace'];pair=[];indices=[]
     for point in e['originalEdge']:
      found=np.flatnonzero(np.all(original[face]==np.asarray(point),axis=1));assert len(found)==1
      i=int(found[0]);pair.append(world[face,i].tolist());indices.append(i)
     edges.append(pair);correspondences.append(dict(originalHostFace=face,originalFacetVertexIndices=indices))
    f=r['sourceFace'];expected=dict(completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalFaces=18086,sourceFace=f,completeOriginalSourceFacetSHA256=digest(world[f].tobytes()),completeClaimedHostLoopSHA256=canonical(edges))
    try:
     proof=verify(world,source_face=f,host_loop_edges=edges,expected_source_binding=expected);failure=None
    except AssertionError as error:proof=None;failure=str(error)
    rows.append(dict(sourceFace=f,originalPanelBody=r['originalBody'],originalHostBody=r['proof']['hostOriginalBody'],completeOriginalFacetEdgeCorrespondence=correspondences,
     recomputedActualCompleteOpeningLoopProof=proof,rawActualLoopFailure=failure,
     originalHostHasIndependentPositiveLiteralBodyPathToOnlyBoundedCarrier=r['proof']['hostOriginalBody']in hostset,
     groundedHostApprovalStillRequired=True))
    if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];save(checkpoint,dict(binding=binding,rows=rows));print(dict(mode=mode,panels=len(rows),total=76,unproved=sum(r['recomputedActualCompleteOpeningLoopProof']is None for r in rows)),flush=True);last=time.monotonic()
   assert len(rows)==76;save(checkpoint,dict(binding=binding,rows=rows,complete=True));records.append(dict(mode=mode,completeWorldSHA256=digest(world.tobytes()),rows=rows,
    actualLoopFailures=[r['sourceFace']for r in rows if r['recomputedActualCompleteOpeningLoopProof']is None],
    hostLiteralPathUnresolved=[r['sourceFace']for r in rows if not r['originalHostHasIndependentPositiveLiteralBodyPathToOnlyBoundedCarrier']]))
  assert reservations.heartbeat(lease)['ok'];assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[UID],sourceSHA256=proposal['sourceSHA256'],completeOriginalPanelProposal=ref(PROPOSAL/'diagnostic.json.gz'),allThreeLiteralAndExplicitF32LoopInventories=records,
   completeOwnedFourStreamFiniteProof=ref(FINITE/'diagnostic.json.gz'),boundedNativeSourceAndLiteralGradePaths=ref(BOUNDED/'diagnostic.json.gz'),
   originalContact565LiteralNegativeAndAllUnmatchedDetailsPreserved=True,
   groundedActualHostApprovalStillRequired=True,sourceOnlyFrozenBaseline=True,noFreshCurrentReacceptance=True,
   visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-langham76-three-literal-render-opening-loops-and-independent-host-path-census-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeOriginalPanels=76,
    actualFailuresByMode={r['mode']:r['actualLoopFailures']for r in records},unresolvedHostPathsByMode={r['mode']:r['hostLiteralPathUnresolved']for r in records},
    groundedHostStillRequired=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
