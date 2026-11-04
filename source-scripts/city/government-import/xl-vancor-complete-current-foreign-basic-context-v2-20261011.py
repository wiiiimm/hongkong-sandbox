"""Complete current foreign BASIC geometry versus four whole owned streams.
Exact closed finite projection intersection diagnostic; no polygon proxy,
foreign omission, role/root inference, collision waiver or acceptance.
"""
import importlib.util,json,subprocess,time
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_closed_projection_intersection_20261010 import intersection
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011';ACTUAL=BASE/'government-xl-vancor-own-retained-actual-render-capture-v2-20261011';PHYS=BASE/'government-xl-vancor-basic-parent-core-apron-current-physical-v3-20261011'
BATCH='government-xl-vancor-complete-current-foreign-basic-context-v2-20261011';DOC=BASE/BATCH;EXPORTER=HERE/'xl-vancor-complete-current-foreign-basic-geometry-v2-20261011.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);refs=[Path(__file__),EXPORTER,manifest,HERE/'xl-vancor-complete-current-foreign-basic-geometry-v1-20261011.mjs',HERE/'xl-vancor-complete-current-foreign-basic-context-v1-20261011.py',BASE/'government-xl-vancor-complete-current-foreign-basic-context-v1-20261011/export-log.json',BASE/'government-xl-vancor-complete-current-foreign-basic-context-v1-20261011/census-failure.json']
 for folder in [INPUT,ACTUAL,PHYS]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(folder/'result.json')
 assert read(PHYS/'diagnostic.json')['currentManifest']==start;forms=read(INPUT/'complete-proposed-region-current-forms.json.gz')['rows'];assert len(forms)==len({r['building']['uid']for r in forms})==80;assert [r['building']['uid']for r in forms if r['existingNative']]==['landsd/186864:0','landsd/236490:0']
 selected=read(PHYS/'selection.json.gz')['rows'][0];asset=ROOT/selected['candidate']['path'];assert digest(asset.read_bytes())==selected['sourceSHA256'];captured=read(ACTUAL/'complete-actual-render-geometry.json.gz');actor=captured['rows'][0];assert actor['uid']==selected['uid']=='landsd/147956:0'and actor['sourceSHA256']==selected['sourceSHA256']
 index=np.asarray(actor['completeOriginalIndex'],int).reshape(-1,3);streams={'providerOriginal':decode_original_world_triangles(asset.read_bytes())}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:streams[mode]=np.asarray(actor[key],dtype='<f8').reshape(-1,3)[index]
 process=subprocess.run(['node',str(EXPORTER)],cwd=ROOT,capture_output=True,text=True);save(DOC/'export-log.json',dict(exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));assert process.returncode==0,process.stderr
 exported=read(DOC/'complete-current-foreign-basic-geometry.json.gz');assert exported['startAndEndInputsVerified']and exported['completeForeignBasics']==77
 expected={r['building']['uid']:r['building']for r in forms if not r['existingNative']and r['building']['uid']!=selected['uid']};assert {r['uid']for r in exported['rows']}==set(expected)
 trials=[];cache={};clock=time.monotonic()
 for foreign in exported['rows']:
  assert foreign['currentForm']==expected[foreign['uid']];p=np.asarray(foreign['completePosition'],dtype='<f8').reshape(-1,3);ix=np.asarray(foreign['completeIndex'],int).reshape(-1,3);mesh=p[ix];assert len(mesh)==foreign['completeFaces']and len(p)==foreign['completeVertices']
  assert np.array_equal(p,np.asarray(foreign['leftAssociatedPerMultiplyAddFloat32WorldPosition']).reshape(-1,3))and np.array_equal(p,np.asarray(foreign['balancedPerMultiplyAddFloat32WorldPosition']).reshape(-1,3))
  foreign_xz=mesh[:,:,[0,2]];fmin=foreign_xz.min(1);fmax=foreign_xz.max(1);rows=[]
  for mode,world in streams.items():
   key=(digest(world.tobytes()),digest(mesh.tobytes()))
   if key not in cache:
    closed=[];tested=0;ownxz=world[:,:,[0,2]]
    for i,face in enumerate(ownxz):
     ids=np.flatnonzero(np.all(fmax>=face.min(0),axis=1)&np.all(fmin<=face.max(0),axis=1))
     for j in ids:
      tested+=1;points=intersection(face,foreign_xz[j])
      if points:closed.append(dict(sourceFace=i,foreignFace=int(j),completeExactClosedProjectedIntersection=[[str(v)for v in point]for point in points]))
    cache[key]=dict(completeOwnFaces=len(world),completeForeignFaces=len(mesh),completeOwnWorldSHA256=key[0],completeForeignWorldSHA256=key[1],boundingCandidatePairsExamined=tested,allClosedFiniteProjectionIntersections=closed,strictCompleteClosedProjectionsDisjoint=not closed)
   rows.append(dict(arithmetic=mode,**cache[key]))
  trials.append(dict(uid=foreign['uid'],completeCurrentForm=foreign['currentForm'],fourStreamTrials=rows,requiresIndependentCompleteFiniteCollisionContext=any(not r['strictCompleteClosedProjectionsDisjoint']for r in rows)))
  if time.monotonic()-clock>20:print(json.dumps(dict(actors=len(trials),total=77)),flush=True);clock=time.monotonic()
 out=dict(uid=selected['uid'],sourceSHA256=selected['sourceSHA256'],currentManifest=start,completeRegionalActors=80,completeForeignBasics=77,completeForeignNativeActorSeparationRequiredSeparately=True,rows=trials,allFourStreamsAndComplete77BasicsStrictClosedProjectionDisjoint=all(not r['requiresIndependentCompleteFiniteCollisionContext']for r in trials),foreignActorsRequiringFullCollisionProof=[r['uid']for r in trials if r['requiresIndependentCompleteFiniteCollisionContext']],sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,installationApproved=False)
 save(DOC/'diagnostic.json.gz',out)
 refs += [asset,INPUT/'complete-proposed-region-current-forms.json.gz',INPUT/'proposal-input.json',ACTUAL/'complete-actual-render-geometry.json.gz',PHYS/'diagnostic.json',PHYS/'selection.json.gz',DOC/'complete-current-foreign-basic-geometry.json.gz',HERE/'exact_original_closed_projection_intersection_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'literal_production_module_dependency_closure_20261010.mjs',HERE/'actual_float32_model_matrix_bounds_20261011.mjs']
 for capture in [captured,exported]:
  for path,sha in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 assert ref(manifest)==start
 s=importlib.util.spec_from_file_location('vancor_foreign_complete_census_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete77-current-basic-actual-full-geometry-four-owned-stream-exact-closed-projection-diagnostic',refs,dict(uids=[selected['uid']],completeForeignBasics=77,foreignActorsRequiringFullCollisionProof=out['foreignActorsRequiringFullCollisionProof'],currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(foreignActorsRequiringFullCollisionProof=out['foreignActorsRequiringFullCollisionProof'])),flush=True)
if __name__=='__main__':main()
