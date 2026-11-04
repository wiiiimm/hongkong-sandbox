"""Complete14938 original/literal/two explicit F32 facets on authentic source TIN.

Diagnostic only. The real BASIC tower gap and source root negatives are preserved;
no grounded-host, mounting, visual-role, foreign or installation credit.
"""
import importlib.util,json,time,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-mount-verdant-tower-authentic-four-stream-finite-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
TIN=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-finite-v1'
ACTUAL=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1'
UID='landsd/261717:0';SOURCE='c8e54f42cd1f52ce94d1112a5c51bd58674fdbe38d8af6ac0de2b9498fbddec1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];bound={}
 for folder in [TIN,ACTUAL]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  bound.update({p['path']:p for p in r['evidenceRefs']});refs.append(ref(folder/'result.json'))
 inputs=read(ACTUAL/'literal-source-inputs.json.gz');row=next(p for p in inputs['rows']if p['uid']==UID);assert row['entry']['sha256']==SOURCE
 actualpath=ACTUAL/'actual-render-attributes.json.gz';actual=next(p for p in read(actualpath)['rows']if p['uid']==UID);assert actual['uid']==row['uid'] and actual['sourceSHA256']==SOURCE
 index=np.asarray(actual['completeOriginalIndex'],np.uint32).reshape(-1,3);assert len(index)==14938;position=np.asarray(actual['completeLiteralWorldPosition'],float).reshape(-1,3);asset=ROOT/row['path'];assert digest(asset.read_bytes())==SOURCE
 worlds=[decode_original_world_triangles(asset.read_bytes()),position[index],np.asarray(actual['completeExplicitLeftAssociatedFloat32WorldPosition'],float).reshape(-1,3)[index],np.asarray(actual['completeExplicitBalancedFloat32WorldPosition'],float).reshape(-1,3)[index]]
 groundpath=HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz';g=read(groundpath);ground=np.asarray(g['completeSelectedFacets'],float);assert digest(ground.tobytes())==g['completeSelectedFacetSHA256'] and len(ground)==510 and np.isfinite(ground).all();assert all(w.shape==(14938,3,3)and np.isfinite(w).all()for w in worlds)
 # Every rendered source/arithmetic triangle lies inside the independently
 # selected original podium bounds; every intersecting whole TIN facet retained.
 box=np.asarray(g['wholeOriginalSourceBounds'],float)
 for world in worlds:assert np.all(world[:,:,[0,2]].min((0,1))>=box[0,[0,2]])and np.all(world[:,:,[0,2]].max((0,1))<=box[1,[0,2]])
 for file in [ACTUAL/'literal-source-inputs.json.gz',actualpath,asset,groundpath]:assert bound[str(file.relative_to(ROOT))]==ref(file);refs.append(ref(file))
 names=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_closed_projection_intersection_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
 refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('mount-tower-source-tin-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  for mode,world in zip(names,worlds):
   binding=dict(producer=ref(Path(__file__)),completeWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),sourceAuthenticTerrainReceipt=ref(TIN/'result.json'),renderCaptureReceipt=ref(ACTUAL/'result.json'),sourceSHA256=SOURCE,kernels=[ref(HERE/n)for n in helpers]);checkpoint=LOCAL/(mode+'-partial.json.gz');partial=read(checkpoint)if checkpoint.exists()else None;assert partial is None or partial['binding']==binding;faces=[]if partial is None else partial['allFaces'];assert [p['sourceFace']for p in faces]==list(range(len(faces)));pulse(True)
   prior=next((p for p in rows if p['completeWorldSHA256']==binding['completeWorldSHA256']),None)
   if prior is not None:faces=prior['allFaces'];assert len(faces)==14938
   else:
    for fi in range(len(faces),14938):
     faces.append(dict(sourceFace=fi,proof=verify(world[fi],ground)));pulse()
     if fi%500==0:save(checkpoint,dict(binding=binding,allFaces=faces,complete=False));print(json.dumps(dict(mode=mode,faces=fi,total=14938)),flush=True)
   assert all(p['proof']['sourceFaceSHA256']==digest(world[p['sourceFace']].tobytes())and p['proof']['completeCurrentGroundSHA256']==binding['completeGroundSHA256']for p in faces)
   save(checkpoint,dict(binding=binding,allFaces=faces,complete=True));unproved=[p['sourceFace']for p in faces if not p['proof']['existingOrdinaryClearanceBoundProved']];rows.append(dict(uid=UID,mode=mode,completeWorldSHA256=binding['completeWorldSHA256'],completeGroundSHA256=binding['completeGroundSHA256'],completeOriginalFaces=14938,allFaces=faces,unprovedFaces=unproved));print(json.dumps(dict(mode=mode,complete14938=True,unprovedFaces=unproved)),flush=True)
  pulse(True);assert all(ref(ROOT/p['path'])==p for p in refs)
  out=dict(uid=UID,sourceSHA256=SOURCE,rows=rows,completeAuthenticGroundFacets=len(ground),all14938SourceFacesAccounted=True,rawBasicTowerTerrainGapAndRoofSupportFailurePreserved=True,explicitArithmeticNotUniversalGPUCameraGuarantee=True,frozenCapturedManifest=inputs['currentManifest'],authenticSourceGroundNeverCurrentDrawnGround=True,sourceOnly=True,noFreshCurrentReacceptance=True,groundedHostNotAccepted=True,visualRoleAccepted=False,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete14938-tower-four-stream-authentic-source-tin-finite-diagnostic-v1',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeOriginalFaces=14938,unprovedFaces={r['mode']:r['unprovedFaces']for r in rows},groundedHostNotAccepted=True,visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
