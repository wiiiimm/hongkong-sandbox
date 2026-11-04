"""Complete owned facets against final captured drawn ground, four streams.

Original provider, literal production and both explicit Float32 model-matrix
arithmetic orders remain separately bound. No GPU camera/FMA or support credit.
"""
import importlib.util,json,uuid,time
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-owned-current-four-stream-finite-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011';ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1';PRIOR=BASE/'xl-terrain-recovery-20261011-langham-original-literal-complete-current-finite-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PHYSICAL,ACTUAL,PRIOR]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
 selected=read(PHYSICAL/'selection.json.gz');assert len(selected['rows'])==2;row=next(p for p in selected['rows']if p['uid']=='landsd/79318:0');assert row['uid']=='landsd/79318:0';asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 runtimepath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtimepath);assert len(runtime['rows'])==2;r=next(p for p in runtime['rows']if p['uid']==row['uid']);actual=next(p for p in read(ACTUAL/'actual-render-attributes.json.gz')['rows']if p['uid']==row['uid']);assert r['uid']==actual['uid']==row['uid'];assert actual['sourceSHA256']==row['sourceSHA256'];index=np.asarray(r['index']).reshape(-1,3);assert r['index']==actual['completeOriginalIndex'];position=np.asarray(r['position']).reshape(-1,3);assert np.array_equal(position,np.asarray(actual['completeLiteralWorldPosition']).reshape(-1,3))
 worlds=[decode_original_world_triangles(asset.read_bytes()),position[index],np.asarray(actual['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3)[index],np.asarray(actual['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)[index]];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);assert all(w.shape==(18086,3,3)and np.isfinite(w).all()for w in worlds)and len(ground)>0
 names=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'];refs.extend(ref(p)for p in [asset,runtimepath,PHYSICAL/'selection.json.gz',PHYSICAL/'historical-current-manifest.json',PRIOR/'diagnostic.json.gz',PRIOR/'result.json',ACTUAL/'actual-render-attributes.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_original_closed_projection_intersection_20261010.py'])
 claim=reservations.claim('langham-owned-current-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];rows=[];old=next(p for p in read(PRIOR/'diagnostic.json.gz')['rows']if p['uid']==row['uid']);assert old['sourceSHA256']==row['sourceSHA256']and old['completeGroundSHA256']==digest(ground.tobytes());last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  for mode,world in zip(names,worlds):
   binding=dict(producer=ref(Path(__file__)),physical=ref(PHYSICAL/'result.json'),actual=ref(ACTUAL/'result.json'),completeWorldSHA256=digest(world.tobytes()),completeGroundSHA256=digest(ground.tobytes()),sourceSHA256=row['sourceSHA256'],kernels=[ref(HERE/'exact_original_face_conservative_clearance_v5_20261010.py'),ref(HERE/'exact_original_projection_coverage_v2_20261010.py')]);checkpoint=LOCAL/(mode+'-partial.json.gz');partial=read(checkpoint)if checkpoint.exists()else None;assert partial is None or partial['binding']==binding;faces=[]if partial is None else partial['allFaces'];assert [p['sourceFace']for p in faces]==list(range(len(faces)))
   pulse(True);previousField='completeOriginal'if binding['completeWorldSHA256']==old['completeOriginalWorldSHA256']else'actualRendered'if binding['completeWorldSHA256']==old['completeActualRenderedWorldSHA256']else None
   if previousField is not None:
    faces=[dict(sourceFace=p['sourceFace'],proof=p[previousField])for p in old['allFaces']];assert len(faces)==18086;assert all(p['proof']['sourceFaceSHA256']==digest(world[p['sourceFace']].tobytes())and p['proof']['completeCurrentGroundSHA256']==digest(ground.tobytes())for p in faces);print(json.dumps(dict(mode=mode,unchangedFencedCompleteOriginalOrLiteralNumericsReused=True)),flush=True)
   same=next((p for p in rows if p['completeWorldSHA256']==binding['completeWorldSHA256']),None)
   if same is not None:faces=same['allFaces'];assert len(faces)==18086;print(json.dumps(dict(mode=mode,all18086ExactWorldAndGroundEqualReused=True)),flush=True)
   else:
    for i in range(len(faces),18086):
     proof=verify(world[i],ground);faces.append(dict(sourceFace=i,proof=proof));pulse()
     if i%200==0:save(checkpoint,dict(binding=binding,allFaces=faces,complete=False));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(mode=mode,faces=i,total=18086)),flush=True)
   save(checkpoint,dict(binding=binding,allFaces=faces,complete=True));unproved=[p['sourceFace']for p in faces if not p['proof']['existingOrdinaryClearanceBoundProved']];rows.append(dict(mode=mode,completeWorldSHA256=binding['completeWorldSHA256'],completeGroundSHA256=binding['completeGroundSHA256'],completeOriginalFaces=18086,allFaces=faces,unprovedFaces=unproved));print(json.dumps(dict(mode=mode,completeFaces=18086,unprovedFaces=unproved)),flush=True)
  pulse(True);result=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],rows=rows,allOwnedFullFiniteBoundsProved=all(not r['unprovedFaces']for r in rows),completeActualGroundFaces=len(ground),explicitArithmeticNotUniversalGPUCameraGuarantee=True,actualHostRootStillRequired=True,rawPriorFailuresPreserved=True,frozenBaselineManifest=ref(PHYSICAL/'historical-current-manifest.json'),noFreshCurrentReacceptance=True,sourceOnlyFrozenCurrentBaseline=True,nativeReacceptance=False,currentAcceptance=False,fullAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  for p in refs:assert ref(ROOT/p['path'])==p
  s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-current-langham-all18086-finite-facets-provider-literal-two-explicit-render-F32-orders-v1',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[row['uid']],completeOriginalFaces=18086,allFourStreamFiniteBoundsProved=result['allOwnedFullFiniteBoundsProved'],unprovedFaces={r['mode']:r['unprovedFaces']for r in rows},actualHostRootStillRequired=True,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
