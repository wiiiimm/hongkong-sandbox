"""Complete641 original/literal/two explicit F32 facets on frozen candidate ground.

Diagnostic only. The real BASIC tower gap and failed roof support are preserved;
no grounded-host, mounting, visual-role, foreign or installation credit.
"""
import importlib.util,json,time,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-mount-verdant-podium-current-four-stream-finite-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-mount-verdant-podium-authentic-current-v1-20261011'
ACTUAL=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1'
UID='landsd/75782:0';SOURCE='4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];bound={}
 for folder in [PHYSICAL,ACTUAL]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  bound.update({p['path']:p for p in r['evidenceRefs']});refs.append(ref(folder/'result.json'))
 selected=read(PHYSICAL/'selection.json.gz');assert len(selected['rows'])==1;row=selected['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE
 runtimepath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtimepath);assert len(runtime['rows'])==1;r=runtime['rows'][0]
 actualpath=ACTUAL/'actual-render-attributes.json.gz';actual=next(p for p in read(actualpath)['rows']if p['uid']==UID);assert r['uid']==actual['uid']==row['uid'];assert actual['sourceSHA256']==r['sourceSHA256']==SOURCE
 index=np.asarray(r['index'],np.uint32).reshape(-1,3);assert len(index)==641 and r['index']==actual['completeOriginalIndex'];position=np.asarray(r['position'],float).reshape(-1,3);assert np.array_equal(position,np.asarray(actual['completeLiteralWorldPosition'],float).reshape(-1,3))
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCE
 worlds=[decode_original_world_triangles(asset.read_bytes()),position[index],np.asarray(actual['completeExplicitLeftAssociatedFloat32WorldPosition'],float).reshape(-1,3)[index],np.asarray(actual['completeExplicitBalancedFloat32WorldPosition'],float).reshape(-1,3)[index]]
 ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)>0 and np.isfinite(ground).all() and all(w.shape==(641,3,3)and np.isfinite(w).all()for w in worlds)
 for p in [PHYSICAL/'selection.json.gz',runtimepath,actualpath,asset]:assert bound[str(p.relative_to(ROOT))]==ref(p);refs.append(ref(p))
 names=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_closed_projection_intersection_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
 refs.extend(ref(p)for p in [PHYSICAL/'historical-current-manifest.json',PHYSICAL/'current-podium-only-physical-diagnostic.json',PHYSICAL/'neighbour-checks.json',HERE/'local'/PHYSICAL.name/'basic-tower-podium-sampled-support-diagnostic.json',HERE/'basic-neighbour-source-support-diagnostic.mjs',HERE/'support-contact.mjs',*[HERE/n for n in helpers]])
 claim=reservations.claim('mount-podium-frozen-current-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  for mode,world in zip(names,worlds):
   binding=dict(producer=ref(Path(__file__)),completeWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),physicalReceipt=ref(PHYSICAL/'result.json'),renderCaptureReceipt=ref(ACTUAL/'result.json'),sourceSHA256=SOURCE,kernels=[ref(HERE/n)for n in helpers]);checkpoint=LOCAL/(mode+'-partial.json.gz');partial=read(checkpoint)if checkpoint.exists()else None;assert partial is None or partial['binding']==binding;faces=[]if partial is None else partial['allFaces'];assert [p['sourceFace']for p in faces]==list(range(len(faces)));pulse(True)
   prior=next((p for p in rows if p['completeWorldSHA256']==binding['completeWorldSHA256']),None)
   if prior is not None:faces=prior['allFaces'];assert len(faces)==641
   else:
    for fi in range(len(faces),641):
     faces.append(dict(sourceFace=fi,proof=verify(world[fi],ground)));pulse()
     if fi%50==0:save(checkpoint,dict(binding=binding,allFaces=faces,complete=False));print(json.dumps(dict(mode=mode,faces=fi,total=641)),flush=True)
   assert all(p['proof']['sourceFaceSHA256']==digest(world[p['sourceFace']].tobytes())and p['proof']['completeCurrentGroundSHA256']==binding['completeGroundSHA256']for p in faces)
   save(checkpoint,dict(binding=binding,allFaces=faces,complete=True));unproved=[p['sourceFace']for p in faces if not p['proof']['existingOrdinaryClearanceBoundProved']];rows.append(dict(uid=UID,mode=mode,completeWorldSHA256=binding['completeWorldSHA256'],completeGroundSHA256=binding['completeGroundSHA256'],completeOriginalFaces=641,allFaces=faces,unprovedFaces=unproved));print(json.dumps(dict(mode=mode,complete641=True,unprovedFaces=unproved)),flush=True)
  pulse(True);assert all(ref(ROOT/p['path'])==p for p in refs)
  out=dict(uid=UID,sourceSHA256=SOURCE,rows=rows,completeActualGroundFaces=len(ground),all641SourceFacesAccounted=True,rawBasicTowerTerrainGapAndRoofSupportFailurePreserved=True,explicitArithmeticNotUniversalGPUCameraGuarantee=True,frozenBaselineManifest=ref(PHYSICAL/'historical-current-manifest.json'),sourceOnlyFrozenCandidateGround=True,noFreshCurrentReacceptance=True,groundedHostNotAccepted=True,visualRoleAccepted=False,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete641-podium-four-stream-frozen-current-candidate-ground-finite-diagnostic-v1',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeOriginalFaces=641,unprovedFaces={r['mode']:r['unprovedFaces']for r in rows},groundedHostNotAccepted=True,visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
