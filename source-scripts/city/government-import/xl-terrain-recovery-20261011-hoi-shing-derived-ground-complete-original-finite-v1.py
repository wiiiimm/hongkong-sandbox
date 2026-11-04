"""Whole original Hoi Shing pair versus the explicit undeployed derived TIN.

Every original source/terrain facet stays bound. Fresh complete conservative
and paired finite math, then complete source contexts; no current/host/root,
visual-role, terrain deployment or installed acceptance from this diagnostic.
"""
from pathlib import Path
import copy,importlib.util,json,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse_verify
from exact_original_paired_finite_clearance_v2_20261010 import verify as paired_verify
from original_bound_facet_wall_context_v3_20261010 import contexts
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-derived-ground-complete-original-finite-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
DERIVED=BASE/'xl-terrain-recovery-20261011-hoi-shing-whole-authentic-tin-derived-step-candidate-v1'
TIN=BASE/'xl-terrain-recovery-20261011-hoi-shing-two-original-authentic-tin-finite-v1'
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in[PROBE,DERIVED,TIN,GRAPH]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,p):assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 selected=bound(TIN,HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz')
 d=bound(DERIVED,DERIVED/'diagnostic.json.gz');assert d['derivedTerrainGeometryChanged']and not d['currentAcceptance']
 artifact=ROOT/d['explicitDerivedTerrainArtifact']['path'];assert ref(artifact)==d['explicitDerivedTerrainArtifact'];g=read(artifact);refs.append(ref(artifact))
 whole=np.asarray(g['triangles'],float);assert whole.shape==(177048,3,3)and digest(whole.tobytes())==g['derivedGroundSHA256']
 ids=selected['sourceCoveringWholeFacetIds'];assert len(ids)==len(set(ids))and all(0<=i<len(whole)for i in ids)
 ground=whole[ids];groundsha=digest(ground.tobytes());old=np.asarray(selected['completeSelectedFacets'],float)
 assert ground.shape==old.shape==(11554,3,3)and np.array_equal(ground[:,:,[0,2]],old[:,:,[0,2]])and np.all(ground[:,:,1]<=old[:,:,1])
 groundfile=LOCAL/'complete-selected-derived-ground.json.gz';save(groundfile,dict(complete11554DerivedFacets=ground.tolist(),completeDerivedGroundSHA256=groundsha,whole177048DerivedArtifact=ref(artifact),sameExactWholeOriginalFacetIDs=ids,originalUndeployedTerrainEdited=True,currentDrawnGround=False));refs.append(ref(groundfile))
 rows=bound(PROBE,PROBE/'selection.json.gz')['rows'];assert[r['uid']for r in rows]==['landsd/318801:0','landsd/318830:0'];sources=[]
 for row,count in zip(rows,[13841,5533]):
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256'];world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(count,3,3);sources.append(world);refs.append(ref(asset))
 graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');assert digest(np.concatenate(sources).tobytes())==graph['binding']['completeOriginalWorldSHA256']
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_closed_projection_intersection_20261010.py','original_bound_facet_wall_context_v3_20261010.py','original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('hoi-complete-derived-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();outputs=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  for row,world in zip(rows,sources):
   binding=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeWorldSHA256=digest(world.tobytes()),completeGroundSHA256=groundsha,producer=ref(Path(__file__)),kernels=[ref(HERE/n)for n in helpers])
   checkpoint=LOCAL/(row['uid'].replace('/','-').replace(':','-')+'-finite-progress.json.gz');saved=read(checkpoint)if checkpoint.exists()else None;assert saved is None or saved['binding']==binding;proofs=[]if saved is None else saved['allFaces'];assert[p['sourceFace']for p in proofs]==list(range(len(proofs)));pulse(True)
   for i in range(len(proofs),len(world)):
    coarse=coarse_verify(world[i],ground);paired=None
    if not coarse['existingOrdinaryClearanceBoundProved']:
     raw=paired_verify(world[i],ground);paired=copy.deepcopy(raw);lo=world[i][:,[0,2]].min(0);hi=world[i][:,[0,2]].max(0);xz=ground[:,:,[0,2]];candidate=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1)).tolist()
     assert candidate==coarse['allProjectedBoundingCandidateOriginalGroundFacets']and all(p['originalGroundFace']in candidate for p in raw['allExactFiniteSourceGroundPieces']);paired['priorCompletePairedProofVerbatim']=raw;paired['allProjectedBoundingCandidateOriginalGroundFacets']=candidate
    proof=coarse if coarse['existingOrdinaryClearanceBoundProved']else paired;assert proof['sourceFaceSHA256']==digest(world[i].tobytes())and proof['completeCurrentGroundSHA256']==groundsha
    proofs.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=dict(sourceFace=i,completeOriginal=coarse),pairedExactOriginalFiniteBound=paired,completeOriginalBoundProved=proof['existingOrdinaryClearanceBoundProved']));pulse()
    if(i+1)%100==0:save(checkpoint,dict(binding=binding,allFaces=proofs,complete=False));print(dict(uid=row['uid'],faces=i+1,total=len(world)),flush=True)
   assert len(proofs)==len(world);save(checkpoint,dict(binding=binding,allFaces=proofs,complete=True));pulse(True)
   cb=dict(completeOriginalWorldTrianglesSHA256=digest(world.tobytes()),completeDrawnGroundSHA256=groundsha,completeFiniteFacetProofRowsSHA256=canonical(proofs));ctx=contexts(world,ground,proofs,expected_binding=cb,current_binding=cb);pulse(True)
   outputs.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(world),completeOriginalWorldSHA256=digest(world.tobytes()),completeUndeployedDerivedGroundSHA256=groundsha,allFaces=proofs,completeAllOriginalFacetContexts=ctx,unprovedOriginalFaces=[p['sourceFace']for p in proofs if not p['completeOriginalBoundProved']]))
  pulse(True);assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[r['uid']for r in rows],rows=outputs,complete19374OriginalFaces=True,complete145NonzeroBodiesAnd14ZeroFacesRemainRequired=True,whole177048DerivedTerrainPinned=True,completeSelectedDerivedFacets11554=True,allOriginalNegativesPreserved=True,explicitTerrainChangedUndeployed=True,sourceOnly=True,currentAcceptance=False,hostQualification=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze_hoi_derived',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-hoi19374-original-paired-finite-contexts-undeployed-derived-TIN-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,unprovedFacesByUID={r['uid']:len(r['unprovedOriginalFaces'])for r in outputs},structuralRootOrBridgeCredit=False,explicitTerrainChangedUndeployed=True,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
