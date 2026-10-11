"""Four-stream complete podium source-TIN facet/grade/cap diagnostics.

Frozen identical full-world proofs may be reused only after exact world/ground
hash equality and completed Neon receipts. The distinct literal representation
gets fresh complete finite facet contexts, roof paths and exact grade interfaces.
No current availability, root, visual, terrain or installation acceptance.
"""
from pathlib import Path
import importlib.util, json, copy, time, uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse_verify
from exact_original_paired_finite_clearance_v2_20261010 import verify as paired_verify
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_verify
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
BASE=ROOT/'docs/astra-city/government-import'; BATCH='xl-terrain-recovery-20261011-mount-verdant-podium-four-stream-authentic-grade-cap-v1'; DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH
CAPTURE=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1'; GRADE=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v2'; TIN=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-finite-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def main():
 assert not DOC.exists(); refs=[ref(Path(__file__))]; receipts={}
 for folder in [CAPTURE,GRADE,TIN]:
  r=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r; refs.append(ref(folder/'result.json'))
 def bound(folder,p):
  assert ref(p) in receipts[folder.name]['evidenceRefs']; refs.append(ref(p)); return read(p)
 inputs=bound(CAPTURE,CAPTURE/'literal-source-inputs.json.gz'); actual=bound(CAPTURE,CAPTURE/'actual-render-attributes.json.gz'); row=next(r for r in inputs['rows'] if r['uid']=='landsd/75782:0'); record=next(r for r in actual['rows'] if r['uid']==row['uid']); asset=ROOT/row['path']; assert digest(asset.read_bytes())==record['sourceSHA256']==row['entry']['sha256']; refs.append(ref(asset)); index=np.asarray(record['completeOriginalIndex'],np.uint32).reshape(-1,3); assert len(index)==641
 worlds=[decode_original_world_triangles(asset.read_bytes())]+[np.asarray(record[k],float).reshape(-1,3)[index] for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']]; assert all(w.shape==(641,3,3) and np.isfinite(w).all() for w in worlds)
 prior=bound(GRADE,GRADE/'diagnostic.json.gz'); g=bound(TIN,HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz'); ground=np.asarray(g['completeSelectedFacets'],float); gsha=digest(ground.tobytes()); assert gsha==g['completeSelectedFacetSHA256']==prior['completeOriginalGroundSHA256']; mainfaces=prior['completeMainBody576OriginalFaces']; assert len(mainfaces)==576 and digest(worlds[0].tobytes())==prior['completeOriginalWorldSHA256']
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_closed_projection_intersection_20261010.py','original_bound_facet_wall_context_v3_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','exact_original_upper_ground_interfaces_20261009.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']; refs.extend(ref(HERE/n) for n in helpers)
 claim=reservations.claim('mount-podium-four-grade-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600); assert claim['ok']; lease=claim['reservation']; last=time.monotonic(); rows=[]; modes=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20: assert reservations.heartbeat(lease)['ok']; last=time.monotonic(); print(json.dumps(dict(completedStreams=len(rows))),flush=True)
 try:
  for mode,world in zip(modes,worlds):
   wsha=digest(world.tobytes()); inv=census(world,list(range(641))); assert inv['sharedEdgeConnectedComponents'][0]==mainfaces
   if wsha==prior['completeOriginalWorldSHA256']:
    proofrows=prior['complete641FacetProofRows']; ctx=prior['complete641OriginalFacetContexts']; caps=prior['strictClearCapWallPaths']; grade=prior['completeMainBodyOriginalGradeInterfaces']; reused=ref(GRADE/'diagnostic.json.gz')
   else:
    binding=dict(completeWorldSHA256=wsha,completeGroundSHA256=gsha,producer=ref(Path(__file__)),kernels=[ref(HERE/n) for n in helpers]); checkpoint=LOCAL/(mode+'-finite-progress.json.gz'); saved=read(checkpoint) if checkpoint.exists() else None; assert saved is None or saved['binding']==binding; proofrows=[] if saved is None else saved['rows']; assert [r['sourceFace'] for r in proofrows]==list(range(len(proofrows))); pulse(True)
    for i in range(len(proofrows),641):
     coarse=coarse_verify(world[i],ground); paired=None
     if not coarse['existingOrdinaryClearanceBoundProved']:
      raw=paired_verify(world[i],ground); paired=copy.deepcopy(raw); lo=world[i][:,[0,2]].min(0); hi=world[i][:,[0,2]].max(0); xz=ground[:,:,[0,2]]; candidates=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1)).tolist(); assert candidates==coarse['allProjectedBoundingCandidateOriginalGroundFacets']; assert all(p['originalGroundFace'] in candidates for p in raw['allExactFiniteSourceGroundPieces']); paired['priorCompletePairedProofVerbatim']=raw; paired['allProjectedBoundingCandidateOriginalGroundFacets']=candidates; paired['candidateInventoryQualification']='Independent complete closed AABB census; exact paired numerical proof retained verbatim.'
     selected=coarse if coarse['existingOrdinaryClearanceBoundProved'] else paired; assert selected is not None; proofrows.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=dict(sourceFace=i,completeOriginal=coarse),pairedExactOriginalFiniteBound=paired,completeOriginalBoundProved=selected['existingOrdinaryClearanceBoundProved'])); pulse()
     if i%25==0: save(checkpoint,dict(binding=binding,rows=proofrows,complete=False))
    save(checkpoint,dict(binding=binding,rows=proofrows,complete=True)); cb=dict(completeOriginalWorldTrianglesSHA256=wsha,completeDrawnGroundSHA256=gsha,completeFiniteFacetProofRowsSHA256=canonical(proofrows)); ctx=contexts(world,ground,proofrows,expected_binding=cb,current_binding=cb); pulse(True); b=dict(completeOriginalWorldTrianglesSHA256=wsha,completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical([])); caps=cap_verify(world,ctx,[],expected_binding=b,current_binding=b); grade=exact_upper_ground_interfaces(world,mainfaces,ground); reused=None; pulse(True)
   assert len(proofrows)==len(ctx)==641 and all(i in mainfaces for i in caps['affectedOriginalWallFaces']); normal=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]); length=np.linalg.norm(normal,axis=1); ratio=np.divide(normal[:,1],length,out=np.zeros(641),where=length!=0); ordinary_failed=[i for i,c in enumerate(ctx) if c['minimum']['minimumGapM']<-.5]; nonwall=[i for i in ordinary_failed if abs(ratio[i])>.25]; upward=[i for i in ordinary_failed if ratio[i]>.25]
   rows.append(dict(uid=row['uid'],mode=mode,complete641WorldSHA256=wsha,completeAuthenticGroundSHA256=gsha,complete641OriginalEdgeCensus=inv,complete641FacetProofRows=proofrows,complete641FacetContexts=ctx,complete576MainBodyFaces=mainfaces,completeMainBodyGradeInterfaces=grade,strictClearCapWallPaths=caps,allOrdinaryRawFailures=ordinary_failed,nonwallRawFailures=nonwall,upwardRawFailures=upward,byteIdenticalWholeNumericReuseFrom=reused,sourceOnly=True,structuralRootOrBridgeCredit=False)); print(json.dumps(dict(mode=mode,gradeInterfaces=len(grade),wallPaths=caps['allAffectedHavePaths'],nonwallFailures=nonwall,upwardFailures=upward)),flush=True); pulse(True)
  assert all(ref(ROOT/r['path'])==r for r in refs); out=dict(uid=row['uid'],sourceSHA256=row['entry']['sha256'],rows=rows,frozenCapturedManifest=inputs['currentManifest'],all641OriginalFacesAndNonrenderingRetained=True,authenticSourceGroundNotCurrentDrawnGround=True,sourceOnly=True,currentPodiumAvailability=False,structuralRootOrBridgeCredit=False,visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs); save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.freeze(BATCH,'complete641-podium-four-stream-authentic-source-grade-cap-diagnostic-v1',[ROOT/r['path'] for r in refs]+[DOC/'diagnostic.json.gz']+list(LOCAL.glob('*-finite-progress.json.gz')),dict(uids=[row['uid']],sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
