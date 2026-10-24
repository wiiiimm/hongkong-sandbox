"""Complete unchanged Twin pair facets on frozen actual candidate drawn ground.

Diagnostic only: original/literal/two explicit Float32 streams, all faces and
exact edge bodies retained. Main podium grade/cap witnesses are recomputed on
its actual drawn finite terrain. No source visual proposal supplies a root or
bridge; no acceptance, publication or native reapproval is performed here.
"""
from pathlib import Path
import copy, importlib.util, json, time, uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse_verify
from exact_original_paired_finite_clearance_v3_20261011 import verify as paired_verify
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_verify
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-twin-regency-pair-current-four-stream-finite-grade-v1'
DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-twin-regency-pair-authentic-current-v1-20261011'
CAPTURE=BASE/'xl-terrain-recovery-20261011-twin-regency-two-current-render-attribute-capture-v1'
PROPOSED=BASE/'government-xl-terrain-recovery-twin-regency-pair-proposed-ground-capture-v1-20261011'
GRAPH=BASE/'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2'
UIDS=['landsd/222465:0','landsd/223206:0']; COUNTS=[13063,456]
SOURCES=['812a7583ff6a789ac956154a534a3548c8c6d5bfdff94338d13a79c42051a37c','fd67218f6828e36899e689d071c55bf95fa0df159ac2927643be46eead74d347']
MODES=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']

def ref(p): return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(x): return digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())

def main():
 assert not DOC.exists(); refs=[ref(Path(__file__))]; receipts={}
 for folder in [PHYSICAL,CAPTURE,GRAPH,PROPOSED]:
  r=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r; refs.append(ref(folder/'result.json'))
 def bound(folder,p):
  assert ref(p) in receipts[folder.name]['evidenceRefs']; refs.append(ref(p)); return read(p)
 selection=bound(PHYSICAL,PHYSICAL/'selection.json.gz')['rows']
 runtime=bound(PROPOSED,HERE/'local'/PROPOSED.name/'runtime-geometry.json.gz')['rows']
 actual=bound(CAPTURE,CAPTURE/'actual-render-attributes.json.gz')['rows']
 graph=bound(GRAPH,GRAPH/'diagnostic.json.gz')
 assert [r['uid'] for r in selection]==[r['uid'] for r in runtime]==[r['uid'] for r in actual]==UIDS
 archive=PHYSICAL/'historical-current-manifest.json'; refs.append(ref(archive))
 assert ref(archive)['sha256']=='df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e'
 bound(PHYSICAL,PHYSICAL/'current-pair-physical-diagnostic.json')
 for name in ['metrics.json','foundation.json','validation.json','native-neighbour-checks.json','neighbour-checks.json']: bound(PHYSICAL,PHYSICAL/name)
 candidates=bound(PHYSICAL,PHYSICAL/'terrain-candidates.json'); assert len(candidates)==1 and candidates[0]['uids']==UIDS
 terrain=ROOT/candidates[0]['path']; assert ref(terrain)['sha256']==candidates[0]['sha256']; refs.append(ref(terrain))
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_closed_projection_intersection_20261010.py','original_bound_facet_wall_context_v3_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','exact_original_upper_ground_interfaces_20261009.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
 refs.extend(ref(HERE/n) for n in helpers)
 inputs=[]
 for k,(row,rt,a,count,sha) in enumerate(zip(selection,runtime,actual,COUNTS,SOURCES)):
  assert rt['uid']==a['uid']==row['uid']==UIDS[k]
  asset=ROOT/row['candidate']['path']; assert digest(asset.read_bytes())==row['sourceSHA256']==rt['sourceSHA256']==a['sourceSHA256']==sha; refs.append(ref(asset))
  index=np.asarray(rt['index'],np.uint32).reshape(-1,3); assert len(index)==count and rt['index']==a['completeOriginalIndex']
  position=np.asarray(rt['position'],float).reshape(-1,3); assert np.array_equal(position,np.asarray(a['completeLiteralWorldPosition'],float).reshape(-1,3))
  worlds=[decode_original_world_triangles(asset.read_bytes()),position[index],np.asarray(a['completeExplicitLeftAssociatedFloat32WorldPosition'],float).reshape(-1,3)[index],np.asarray(a['completeExplicitBalancedFloat32WorldPosition'],float).reshape(-1,3)[index]]
  ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
  assert len(ground)>0 and np.isfinite(ground).all() and all(w.shape==(count,3,3) and np.isfinite(w).all() for w in worlds)
  inputs.append((row,worlds,ground))
 claim=reservations.claim('twin-pair-frozen-current-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600); assert claim['ok']; lease=claim['reservation']; last=time.monotonic(); rows=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:
   assert reservations.heartbeat(lease)['ok']; last=time.monotonic(); print(json.dumps(dict(completedRows=len(rows))),flush=True)
 try:
  for k,(row,worlds,ground) in enumerate(inputs):
   count=COUNTS[k]; gsha=digest(ground.tobytes()); offset=0 if k==0 else 13063
   expected=[c['globalOriginalFaces'] for c in graph['bodies'] if all(offset<=i<offset+count for i in c['globalOriginalFaces'])]
   expected=[[i-offset for i in ids] for ids in expected]
   for mode,world in zip(MODES,worlds):
    wsha=digest(world.tobytes()); inv=census(world,list(range(count)))
    if mode=='providerOriginal':
     assert inv['sharedEdgeConnectedComponents']==expected
     assert [offset+i for i in inv['exactNonrenderingOriginalFaces']]==[i for i in graph['exactNonrenderingGlobalFacesRetainedUncredited'] if offset<=i<offset+count]
    binding=dict(uid=row['uid'],completeWorldSHA256=wsha,completeGroundSHA256=gsha,producer=ref(Path(__file__)),kernels=[ref(HERE/n) for n in helpers],physicalReceipt=ref(PHYSICAL/'result.json'),actualCaptureReceipt=ref(CAPTURE/'result.json'),actualProposedGroundReceipt=ref(PROPOSED/'result.json'))
    checkpoint=LOCAL/(str(k)+'-'+mode+'-finite-progress.json.gz'); saved=read(checkpoint) if checkpoint.exists() else None
    assert saved is None or saved['binding']==binding; proofrows=[] if saved is None else saved['allFaces']; assert [r['sourceFace'] for r in proofrows]==list(range(len(proofrows))); pulse(True)
    previous=next((r for r in rows if r['uid']==row['uid'] and r['completeWorldSHA256']==wsha and r['completeActualDrawnGroundSHA256']==gsha),None)
    if previous is not None: proofrows=previous['allFaces']
    else:
     for i in range(len(proofrows),count):
      coarse=coarse_verify(world[i],ground); paired=None
      if not coarse['existingOrdinaryClearanceBoundProved']:
       raw=paired_verify(world[i],ground); paired=copy.deepcopy(raw); lo=world[i][:,[0,2]].min(0); hi=world[i][:,[0,2]].max(0); xz=ground[:,:,[0,2]]
       candidates=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1)).tolist()
       assert candidates==coarse['allProjectedBoundingCandidateOriginalGroundFacets'] and all(p['originalGroundFace'] in candidates for p in raw['allExactFiniteSourceGroundPieces'])
       paired['priorCompletePairedProofVerbatim']=raw; paired['allProjectedBoundingCandidateOriginalGroundFacets']=candidates
      proof=coarse if coarse['existingOrdinaryClearanceBoundProved'] else paired; assert proof is not None
      assert proof['sourceFaceSHA256']==digest(world[i].tobytes()) and proof['completeCurrentGroundSHA256']==gsha
      proofrows.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=dict(sourceFace=i,completeOriginal=coarse),pairedExactOriginalFiniteBound=paired,completeOriginalBoundProved=proof['existingOrdinaryClearanceBoundProved'])); pulse()
      if i%100==0: save(checkpoint,dict(binding=binding,allFaces=proofrows,complete=False)); print(json.dumps(dict(uid=row['uid'],mode=mode,faces=i,total=count)),flush=True)
    assert len(proofrows)==count; save(checkpoint,dict(binding=binding,allFaces=proofrows,complete=True)); pulse(True)
    grade=None; caps=None
    cb=dict(completeOriginalWorldTrianglesSHA256=wsha,completeDrawnGroundSHA256=gsha,completeFiniteFacetProofRowsSHA256=canonical(proofrows))
    ctx=previous['completeAllOriginalFacetContexts'] if previous is not None else contexts(world,ground,proofrows,expected_binding=cb,current_binding=cb); pulse(True)
    if k==1:
     capbinding=dict(completeOriginalWorldTrianglesSHA256=wsha,completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical([]))
     caps=previous['strictPodiumClearCapWallPaths'] if previous is not None else cap_verify(world,ctx,[],expected_binding=capbinding,current_binding=capbinding); pulse(True)
     mainfaces=expected[0]; assert len(mainfaces)==363; grade=previous['complete363MainPodiumGradeInterfaces'] if previous is not None else exact_upper_ground_interfaces(world,mainfaces,ground); pulse(True)
    rows.append(dict(uid=row['uid'],mode=mode,completeWorldSHA256=wsha,completeActualDrawnGroundSHA256=gsha,completeActualDrawnGroundFaces=len(ground),completeOriginalFaces=count,allFaces=proofrows,unprovedOrdinaryFaces=[r['sourceFace'] for r in proofrows if not r['completeOriginalBoundProved']],completeNonzeroEdgeCensus=inv,completeAllOriginalFacetContexts=ctx,strictPodiumClearCapWallPaths=caps,complete363MainPodiumGradeInterfaces=grade,exactNumericReuseFromEarlierOutputRow=previous is not None,sourceBodyCensusMatchesThisMode=inv['sharedEdgeConnectedComponents']==expected)); pulse(True)
  assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=UIDS,completeOriginalFaces=13519,completeOriginalNonzeroBodies=1120,completeOriginalZerosRetained=graph['exactNonrenderingGlobalFacesRetainedUncredited'],rows=rows,frozenBaselineManifest=ref(archive),frozenActualCandidateDrawnGround=True,noFreshCurrentReacceptance=True,allRawPhysicalFailuresPreserved=ref(PHYSICAL/'current-pair-physical-diagnostic.json'),explicitArithmeticNotUniversalGPUCameraGuarantee=True,sourceGeometryChanges=0,visualRolesAccepted=False,structuralRootOrBridgeCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out); pulse(True)
  spec=importlib.util.spec_from_file_location('freeze_twin_pair_finite',HERE/helpers[-1]); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
  m.freeze(BATCH,'twin-complete13519-four-stream-frozen-actual-candidate-finite-podium-grade-cap-diagnostic-v1',[ROOT/r['path'] for r in refs]+[DOC/'diagnostic.json.gz']+list(LOCAL.glob('*-finite-progress.json.gz')),dict(uids=UIDS,completeOriginalFaces=13519,unprovedOrdinaryFaces={r['uid']+':'+r['mode']:r['unprovedOrdinaryFaces'] for r in rows},sourceOnlyFrozenCandidateBaseline=True,currentAcceptance=False,newlyInstalled=0))
 finally: assert reservations.release(lease)['ok']

if __name__=='__main__': main()
