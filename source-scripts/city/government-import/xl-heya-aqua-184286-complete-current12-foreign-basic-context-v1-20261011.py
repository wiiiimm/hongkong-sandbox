"""Unexecuted exact expanded14 current census -> complete12 BASIC collisions.
All four complete owned streams and closed finite projections. Any touch remains
an independent full finite collision obligation, without name/ownership waivers.
"""
import importlib.util,json,subprocess,sys,uuid,time
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_closed_projection_intersection_20261010 import intersection
BASE=ROOT/'docs/astra-city/government-import';ACTUAL=BASE/'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011';FINITE=BASE/'government-xl-heya-aqua-184286-184285-complete-four-stream-current-finite-v1-20261011';PHYS=BASE/'government-xl-heya-aqua-184286-unchanged-current-ordinary-physical-v1-20261011'
BATCH='government-xl-heya-aqua-184286-complete-current12-foreign-basic-context-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/184286:0'
EXPORTER=HERE/'xl-heya-aqua-184286-current12-foreign-basic-geometry-v1-20261011.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);refs=[Path(__file__),EXPORTER,HERE/'exact_original_closed_projection_intersection_20261010.py'];pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 for folder in [ACTUAL,FINITE,PHYS]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for pin in r['evidenceRefs']:
   p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p);pins[pin['path']]=pin['sha256']
 assert start['sha256']=='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
 proposal=read(ACTUAL/'capture-inputs.json.gz');forms=proposal['completeCurrentForms'];assert len(forms)==len({r['uid']for r in forms})==14
 registry=[m for pin in proposal['completeCurrentCatalogueRefs']for m in read(ROOT/pin['path'])['models']];assert len(registry)==len({m['uid']for m in registry})==6648;native={m['uid']for m in registry}
 assert {f['uid']for f in forms if f['uid']in native}=={'landsd/184285:0'}
 expected={f['uid']:f for f in forms if f['uid']!=UID and f['uid']not in native};assert len(expected)==12 and {'landsd/184287:0','landsd/184519:0'}<=set(expected)
 source=read(ACTUAL/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'][UID];streams={mode:np.asarray(s['completeWorldTriangles'],dtype='<f8')for mode,s in source['completeWorldStreams'].items()};assert len(streams)==4
 for mode,w in streams.items():assert w.shape==(17910,3,3)and np.isfinite(w).all()and digest(w.tobytes())==source['completeWorldStreams'][mode]['completeWorldTriangleSHA256']==next(r for r in read(FINITE/'diagnostic.json.gz')['rows']if r['uid']==UID and r['arithmetic']==mode)['completeWholeWorldSHA256']
 process=subprocess.run(['node',str(EXPORTER)],cwd=ROOT,capture_output=True,text=True);save(DOC/'export-log.json',dict(exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));assert process.returncode==0,process.stderr
 exported=read(DOC/'complete-current-foreign-basic-geometry.json.gz');assert exported['startAndEndInputsVerified']and exported['completeForeignBasics']==12 and exported['completeRegionalForms']==14
 assert len(exported['rows'])==12 and {r['uid']for r in exported['rows']}==set(expected)
 trials=[];cache={}
 for foreign in exported['rows']:
  assert foreign['currentForm']==expected[foreign['uid']];p=np.asarray(foreign['completePosition'],dtype='<f8').reshape(-1,3);ix=np.asarray(foreign['completeIndex'],dtype=np.int64).reshape(-1,3);mesh=p[ix];assert len(mesh)==foreign['completeFaces']and len(p)==foreign['completeVertices']and np.isfinite(p).all()
  assert np.array_equal(p,np.asarray(foreign['leftAssociatedPerMultiplyAddFloat32WorldPosition']).reshape(-1,3))and np.array_equal(p,np.asarray(foreign['balancedPerMultiplyAddFloat32WorldPosition']).reshape(-1,3))
  foreign_xz=mesh[:,:,[0,2]];fmin=foreign_xz.min(1);fmax=foreign_xz.max(1);rows=[];foreign_sha=digest(mesh.tobytes())
  for mode,w in streams.items():
   key=(digest(w.tobytes()),foreign_sha)
   if key not in cache:
    closed=[];tested=0
    for i,face in enumerate(w[:,:,[0,2]]):
     ids=np.flatnonzero(np.all(fmax>=face.min(0),axis=1)&np.all(fmin<=face.max(0),axis=1))
     for j in ids:
      tested+=1;points=intersection(face,foreign_xz[j])
      if points:closed.append(dict(sourceFace=i,foreignFace=int(j),completeExactClosedProjectedIntersection=[[str(v)for v in point]for point in points]))
    cache[key]=dict(completeOwnFaces=len(w),completeForeignFaces=len(mesh),completeOwnWorldSHA256=key[0],completeForeignWorldSHA256=key[1],boundingCandidatePairsExamined=tested,allClosedFiniteProjectionIntersections=closed,strictCompleteClosedProjectionsDisjoint=not closed)
   rows.append(dict(arithmetic=mode,**cache[key]))
  trials.append(dict(uid=foreign['uid'],completeCurrentForm=foreign['currentForm'],fourStreamTrials=rows,requiresIndependentCompleteFiniteCollisionContext=any(not r['strictCompleteClosedProjectionsDisjoint']for r in rows)));print(json.dumps(dict(foreign=foreign['uid'],completed=len(trials),needsFullCollision=trials[-1]['requiresIndependentCompleteFiniteCollisionContext'])),flush=True)
 out=dict(uids=[UID],sourceSHA256=source['sourceSHA256'],currentManifest=start,completeRegionalActors=14,ownedActors=[UID],installedNativeActors=['landsd/184285:0'],completeForeignBasics=12,rows=trials,allFourStreamsAndComplete12BasicsStrictClosedProjectionDisjoint=all(not r['requiresIndependentCompleteFiniteCollisionContext']for r in trials),foreignActorsRequiringFullCollisionProof=[r['uid']for r in trials if r['requiresIndependentCompleteFiniteCollisionContext']],currentNativeSourceCollisionObligationsNotWaived=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,installationApproved=False)
 save(DOC/'diagnostic.json.gz',out)
 for p,h in exported['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert ref(manifest)==start and reservations.owns(lease)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(HERE/h for h in ['literal_production_module_dependency_closure_20261010.mjs','actual_float32_model_matrix_bounds_20261011.mjs']);refs.extend(p for p in DOC.rglob('*')if p.is_file())
 s=importlib.util.spec_from_file_location('heya_complete_foreign_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);result=m.freeze(BATCH,'heya-complete12-current-BASIC-actual-geometry-four-owned-world-closed-projection-diagnostic',refs,dict(uids=[UID],completeForeignBasics=12,foreignActorsRequiringFullCollisionProof=out['foreignActorsRequiringFullCollisionProof'],currentAcceptance=False))
 print(json.dumps(dict(jobId=result['jobId'],foreignActorsRequiringFullCollisionProof=out['foreignActorsRequiringFullCollisionProof'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 for folder in [ACTUAL,FINITE,PHYS]:
  for pin in read(folder/'result.json')['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 forms=read(ACTUAL/'capture-inputs.json.gz')['completeCurrentForms'];assert len(forms)==len({f['uid']for f in forms})==14
 claim=reservations.claim('heya-complete12-current-foreign-'+str(uuid.uuid4()),[('building:'if f['uid'].startswith('landsd/')else'foreign-form:')+f['uid']for f in forms],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
