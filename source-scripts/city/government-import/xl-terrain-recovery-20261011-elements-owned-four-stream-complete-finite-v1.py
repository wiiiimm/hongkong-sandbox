"""Every unchanged owned facet on frozen complete actual Elements ground.

Diagnostic only. An exact enclosing whole-POSITION region permits strictly
disjoint ground pruning. Every nested finite proof names its real subset; the
complete ground, IDs and separation certificate remain independently bound.
Neither native availability nor soil clearance supplies a structural root.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse_verify
from exact_original_paired_finite_clearance_v3_20261011 import verify as paired_verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011'
OWNATTR=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'
NATIVEATTR=BASE/'xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1'
GRAPH=BASE/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1'
UIDS=['landsd/204145:0','landsd/204143:0'];COUNTS=[12129,11680]
MODES=[('providerOriginal',None),('actualLiteral','completeLiteralWorldPosition'),('explicitLeftFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [PHYSICAL,OWNATTR,NATIVEATTR,GRAPH]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  receipts[folder.name]=receipt;refs.append(ref(folder/'result.json'))
 def bound(folder,p):
  assert ref(p) in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 rows=bound(PHYSICAL,PHYSICAL/'selection.json.gz')['rows']
 runtime=bound(PHYSICAL,HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz')['rows']
 attrs=bound(OWNATTR,OWNATTR/'actual-render-attributes.json.gz')['rows']
 graph=bound(GRAPH,GRAPH/'diagnostic.json.gz')
 native=bound(NATIVEATTR,NATIVEATTR/'native-render-ground.json.gz')['rows'][0]
 assert native['uid']=='landsd/273061:0';ground=np.asarray(native['drawnGroundGeometry'],float).reshape(-1,3,3)
 assert len(ground)==365886;prepared=CompleteGround(ground)
 assert [r['uid']for r in rows]==[r['uid']for r in runtime]==[r['uid']for r in attrs]==UIDS
 archive=NATIVEATTR/'historical-current-manifest.json';bound(NATIVEATTR,archive)
 for name in ['metrics.json','foundation.json','validation.json','native-neighbour-checks.json','neighbour-checks.json']:bound(PHYSICAL,PHYSICAL/name)
 helpers=['exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_closed_ground_aabb_pruning_v1_20261011.py','exact_original_rational_interface_segment_clearance_20261011.py','exact_original_upper_ground_interfaces_20261009.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_closed_projection_intersection_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
 refs.extend(ref(HERE/n)for n in helpers);inputs=[]
 for row,rt,a,count in zip(rows,runtime,attrs,COUNTS):
  assert row['uid']==rt['uid']==a['uid'];asset=ROOT/row['candidate']['path'];refs.append(ref(asset));raw=asset.read_bytes()
  assert digest(raw)==row['sourceSHA256']==rt['sourceSHA256']==a['sourceSHA256'];index=np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3)
  assert len(index)==count and a['completeOriginalIndex']==rt['index']
  assert np.array_equal(np.asarray(a['completeLiteralWorldPosition'],float),np.asarray(rt['position'],float))
  original=decode_original_world_triangles(raw);position_proof=packed_world_bounds(raw)
  assert position_proof['sourceSHA256']==row['sourceSHA256'] and position_proof['worldTrianglesSHA256']==digest(original.tobytes())
  positions={field:np.asarray(a[field],float).reshape(-1,3)for _,field in MODES if field}
  assert all(np.isfinite(v).all()and index.max()<len(v)for v in positions.values())
  worlds={mode:original if field is None else positions[field][index]for mode,field in MODES}
  assert all(w.shape==(count,3,3)and np.isfinite(w).all()for w in worlds.values())
  bounds=np.asarray([position_proof['originalWholeSourceBounds']]+[[v.min(0).tolist(),v.max(0).tolist()]for v in positions.values()]);lo=bounds[:,0].min(0);hi=bounds[:,1].max(0)
  capture=native['groundCaptureBounds'];assert capture[0]<=lo[0]<=hi[0]<=capture[2]and capture[1]<=lo[2]<=hi[2]<=capture[3]
  ids,selection=prepared.select([[str(F(float(v)))for v in p]for p in [lo,hi]]);assert len(ids)>0
  selected=ground[ids];assert all(np.all(w>=lo)and np.all(w<=hi)for w in worlds.values())
  inputs.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],worlds=worlds,selected=selected,selection=selection,positionProof=position_proof))
 claim=reservations.claim('elements-owned-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();outrows=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  for inp,count in zip(inputs,COUNTS):
   selected=inp['selected'];selected_sha=digest(selected.tobytes())
   for mode,_ in MODES:
    world=inp['worlds'][mode];wsha=digest(world.tobytes());inv=census(world,list(range(count)))
    assert sorted(inv['exactNonrenderingOriginalFaces']+[i for part in inv['sharedEdgeConnectedComponents']for i in part])==list(range(count))
    binding=dict(uid=inp['uid'],mode=mode,completeWorldSHA256=wsha,fullGroundSHA256=prepared.ground_sha,subsetGroundSHA256=selected_sha,wholePOSITIONSelectionSHA256=canonical(inp['selection']),producer=ref(Path(__file__)),kernels=[ref(HERE/n)for n in helpers])
    checkpoint=LOCAL/(inp['uid'].replace('/','-').replace(':','-')+'-'+mode+'-progress.json.gz')
    saved=read(checkpoint)if checkpoint.exists()else None;assert saved is None or saved['binding']==binding
    faces=[]if saved is None else saved['allFaces'];assert [r['sourceFace']for r in faces]==list(range(len(faces)));pulse(True)
    previous=next((r for r in outrows if r['uid']==inp['uid']and r['completeWorldSHA256']==wsha and r['selectedGroundSHA256']==selected_sha),None)
    if previous is not None:faces=previous['allFaces']
    else:
     for i in range(len(faces),count):
      coarse=coarse_verify(world[i],selected);paired=None
      if not coarse['existingOrdinaryClearanceBoundProved']:paired=paired_verify(world[i],selected)
      proof=paired if paired is not None else coarse
      assert proof['sourceFaceSHA256']==digest(world[i].tobytes())and proof['completeCurrentGroundSHA256']==selected_sha
      faces.append(dict(sourceFace=i,subsetCoarseProofVerbatim=coarse,subsetPairedProofVerbatim=paired,existingOrdinaryClearanceBoundProved=proof['existingOrdinaryClearanceBoundProved'],closedProjectionCovered=proof['groundProjectionCovered'],exactCertifiedLowerClearanceM=proof['exactCertifiedLowerClearanceM'],strictlyExposedWholeFacet=proof['groundProjectionCovered']is True and F(proof['exactCertifiedLowerClearanceM'])>0));pulse()
      if i%100==0:save(checkpoint,dict(binding=binding,allFaces=faces,complete=False));print(dict(uid=inp['uid'],mode=mode,faces=i,total=count),flush=True)
    assert len(faces)==count;save(checkpoint,dict(binding=binding,allFaces=faces,complete=True));pulse(True)
    outrows.append(dict(uid=inp['uid'],mode=mode,sourceSHA256=inp['sourceSHA256'],completeWorldSHA256=wsha,completeOriginalFaces=count,completeOriginalPOSITIONProof=inp['positionProof'],completeNonzeroEdgeCensus=inv,wholePOSITIONGroundSelection=inp['selection'],selectedGroundSHA256=selected_sha,allFaces=faces,unprovedOrdinaryFaces=[r['sourceFace']for r in faces if not r['existingOrdinaryClearanceBoundProved']],unprovedStrictExposureFaces=[r['sourceFace']for r in faces if not r['strictlyExposedWholeFacet']],exactNumericReuseFromEarlierOutputRow=previous is not None,nestedProofsUseTheirActualSubsetOnly=True))
  prepared.verify_binding();assert all(ref(ROOT/r['path'])==r for r in refs);output=dict(uids=UIDS,rows=outrows,completeOwnedOriginalFaces=23809,completeCapturedNativeGroundSHA256=prepared.ground_sha,completeCapturedNativeGroundFaces=len(ground),frozenBaselineManifest=ref(archive),allRawPhysicalFailuresPreserved=True,sourceOnly=True,noFreshCurrentReacceptance=True,nativeReacceptance=False,rootOrStructuralContactCredit=False,sourceGeometryChanges=0,terrainChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',output);pulse(True)
  spec=importlib.util.spec_from_file_location('elements_owned_finite_freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete23809-owned-four-stream-frozen-native-ground-finite-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz']+list(LOCAL.glob('*-progress.json.gz')),dict(uids=UIDS,sourceOnly=True,completeOwnedOriginalFaces=23809,unprovedOrdinaryFaces={r['uid']+':'+r['mode']:r['unprovedOrdinaryFaces']for r in outrows},currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
