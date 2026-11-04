"""Exact refinement of EVERY raw641-face four-stream clearance warning.

Frozen candidate ground only; source/runtime distinct, full failures retained.
No body/mount/foreign/support/terrain acceptance or installation.
"""
from pathlib import Path
import importlib.util,time,uuid,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v2_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-podium-current-paired-refinement-v1';DOC=BASE/BATCH
COARSE=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-current-four-stream-finite-v1';PHYSICAL=BASE/'government-xl-terrain-recovery-mount-verdant-podium-authentic-current-v1-20261011';ACTUAL=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1';UID='landsd/75782:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipt=read(COARSE/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 bound={p['path']:p for p in receipt['evidenceRefs']};diag=read(COARSE/'diagnostic.json.gz');assert bound[str((COARSE/'diagnostic.json.gz').relative_to(ROOT))]==ref(COARSE/'diagnostic.json.gz')and diag['uid']==UID
 row=read(PHYSICAL/'selection.json.gz')['rows'][0];runtimepath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtimepath)['rows'][0];actual=next(p for p in read(ACTUAL/'actual-render-attributes.json.gz')['rows']if p['uid']==UID);assert runtime['uid']==actual['uid']==row['uid']==UID
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==runtime['sourceSHA256']==actual['sourceSHA256'];idx=np.asarray(runtime['index'],np.uint32).reshape(-1,3);assert runtime['index']==actual['completeOriginalIndex']and len(idx)==641
 worlds=[decode_original_world_triangles(asset.read_bytes()),np.asarray(runtime['position'],float).reshape(-1,3)[idx],np.asarray(actual['completeExplicitLeftAssociatedFloat32WorldPosition'],float).reshape(-1,3)[idx],np.asarray(actual['completeExplicitBalancedFloat32WorldPosition'],float).reshape(-1,3)[idx]];ground=np.asarray(runtime['drawnGroundGeometry'],float).reshape(-1,3,3)
 for p in [asset,runtimepath,PHYSICAL/'selection.json.gz',ACTUAL/'actual-render-attributes.json.gz']:assert bound[str(p.relative_to(ROOT))]==ref(p);refs.append(ref(p))
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(p)for p in [COARSE/'result.json',COARSE/'diagnostic.json.gz',*[HERE/n for n in helpers]])
 claim=reservations.claim('mount-frozen-current-paired-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];rows=[];cache={};last=time.monotonic()
 try:
  for coarse,world in zip(diag['rows'],worlds):
   assert world.shape==(641,3,3)and np.isfinite(world).all()and digest(world.tobytes())==coarse['completeWorldSHA256']and digest(ground.tobytes())==coarse['completeGroundSHA256'];faces=coarse['unprovedFaces'];assert faces==[p['sourceFace']for p in coarse['allFaces']if not p['proof']['existingOrdinaryClearanceBoundProved']];key=digest(world.tobytes());assert reservations.heartbeat(lease)['ok']
   if key in cache:records=cache[key]
   else:
    records=[];normals=np.cross(world[:,1]-world[:,0],world[:,2]-world[:,0]);length=np.linalg.norm(normals,axis=1);ny=np.divide(normals[:,1],length,out=np.zeros(len(world)),where=length!=0)
    for fi in faces:
     prior=coarse['allFaces'][fi]['proof'];assert prior['sourceFaceSHA256']==digest(world[fi].tobytes())and prior['completeCurrentGroundSHA256']==coarse['completeGroundSHA256'];proof=verify(world[fi],ground);records.append(dict(sourceFace=fi,normalY=float(ny[fi]),rawConservativeProofVerbatim=prior,independentExactPairedFiniteProof=proof))
     if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(json.dumps(dict(mode=coarse['mode'],refinedFaces=len(records),total=len(faces))),flush=True)
    cache[key]=records
   remaining=[p['sourceFace']for p in records if not p['independentExactPairedFiniteProof']['existingOrdinaryClearanceBoundProved']];rows.append(dict(mode=coarse['mode'],completeWorldSHA256=key,completeGroundSHA256=coarse['completeGroundSHA256'],all641CoarseFacesPreserved=True,everyRawWarningRefined=True,refinedFaces=records,remainingFaces=remaining,upwardFailures=[p['sourceFace']for p in records if p['normalY']>.5 and p['sourceFace']in remaining],downwardFailures=[p['sourceFace']for p in records if p['normalY']<-.5 and p['sourceFace']in remaining]));print(json.dumps(dict(mode=coarse['mode'],warnings=len(faces),remaining=len(remaining),upward=rows[-1]['upwardFailures'],downward=rows[-1]['downwardFailures'])),flush=True)
  assert reservations.heartbeat(lease)['ok']and all(ref(ROOT/p['path'])==p for p in refs);save(DOC/'diagnostic.json.gz',dict(uid=UID,rows=rows,frozenCandidateGround=True,rawForeignTowerTerrainAndRoofSupportFailuresPreserved=True,sourceOnly=True,currentAcceptance=False,groundedHostAccepted=False,visualRoleAccepted=False,newlyInstalled=0,evidenceRefs=refs))
  spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'all641-podium-four-stream-current-frozen-ground-every-warning-exact-paired-refinement-v1',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],remainingFaces={r['mode']:r['remainingFaces']for r in rows},currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
