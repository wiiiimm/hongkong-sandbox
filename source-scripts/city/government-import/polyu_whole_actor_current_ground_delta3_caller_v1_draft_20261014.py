"""Whole-source ROI ground only and three fresh native bounds; no guards/finite/reapproval."""
from pathlib import Path
import json,sys,time,uuid,subprocess,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha,triangles
import polyu_four_parent_current_production_caller_v3_draft_20261014 as prior
ref,check=prior.ref,prior.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-whole-actor-current-ground-delta3-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'polyu_whole_actor_current_ground_delta3_runtime_v1_draft_20261014.mjs'
CAP=prior.DOC;FEAS=BASE/'government-xl-polyu-nine-complete-parent-restoration-feasibility-v1-20261013'
DELTAS=['landsd/12728:0','landsd/338946:0','landsd/193086:0']
FIELDS=['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
def actor_inputs():
 actors=read(CAP/'complete-fresh-current-native59527-and24-BASIC.json.gz');native=actors['nativeRow'];original=read(CAP/'native59527-unchanged-provider-original-world.json.gz')
 assert native['completeFaces']==original['completeFaces']==59527 and native['wholeUnusedPositionVerticesIncluded']and actors['startEndAllInputsVerified']
 ix=np.asarray(native['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);worlds={MODES[0]:triangles(original['completeWorldTriangles'])};assert sha(worlds[MODES[0]])==original['originalWorldSHA256']
 native_proof_file=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012/inventory.json.gz'
 cached=next(r for r in read(native_proof_file)['rows']if r['uid']==native['uid']);native_proof=cached['completeOriginalPOSITIONProof']
 assert cached['sourceSHA256']==native['sourceSHA256']==native_proof['sourceSHA256']and native_proof['allOriginalPositionVerticesAccounted']and native_proof['completeOriginalPositionVertices']==native['completePositionVertices']and native_proof['completeOriginalTriangles']==59527 and native_proof['worldTrianglesSHA256']==original['originalWorldSHA256']
 bounds=[np.asarray(native_proof['originalWholeSourceBounds'],dtype='<f8')[:,[0,2]]]
 for mode,field in zip(MODES[1:],FIELDS):
  position=np.asarray(native[field],dtype='<f8').reshape(-1,3);assert len(position)==native['completePositionVertices']and np.isfinite(position).all();assert ix.min()>=0 and ix.max()<len(position)
  worlds[mode]=triangles(position[ix]);bounds.append(position[:,[0,2]])
 rows=[dict(uid=native['uid'],sourceSHA256=native['sourceSHA256'],role='retained-native',worlds={m:dict(completeWorldTriangles=w.tolist(),worldSHA256=sha(w))for m,w in worlds.items()})]
 source_ref=read(FEAS/'complete-nine-parent-restoration-feasibility.json.gz')['exactSourceContext'];source=read(check(source_ref));assert len(source['completeWorldStreams'])==4
 owned_raw_file=BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013/complete-current-actual-source-and-ground-305582-0.json.gz';owned_raw=read(owned_raw_file);owned_proof=owned_raw['completeOriginalPOSITIONProof']
 assert owned_proof['sourceSHA256']==source['sourceSHA256']==owned_raw['sourceSHA256']and owned_proof['allOriginalPositionVerticesAccounted']and owned_proof['completeOriginalTriangles']==10536
 assert owned_proof['worldTrianglesSHA256']==source['completeWorldStreams']['providerOriginal']['completeWorldTriangleSHA256']
 bounds.append(np.asarray(owned_proof['originalWholeSourceBounds'],dtype='<f8')[:,[0,2]])
 for b in owned_raw['completeWholeUnusedVertexBounds']:bounds.append(np.asarray(b,dtype='<f8')[:,[0,2]])
 owned={}
 for m,record in source['completeWorldStreams'].items():
  w=triangles(record['completeWorldTriangles']);assert len(w)==10536 and sha(w)==record['completeWorldTriangleSHA256'];owned[m]=dict(completeWorldTriangles=w.tolist(),worldSHA256=sha(w));bounds.append(w[:,:,[0,2]].reshape(-1,2))
 rows.append(dict(uid='landsd/305582:0',sourceSHA256=source['sourceSHA256'],role='complete-owned-original',worlds=owned))
 assert len(actors['basicRows'])==24
 for a in actors['basicRows']:
  index=np.asarray(a['index'],dtype=np.int64).reshape(-1,3);streams={}
  for m,field in zip(MODES[1:],FIELDS):
   position=np.asarray(a[field],dtype='<f8').reshape(-1,3);assert len(position)==a['completePositionVertices']and np.isfinite(position).all()
   if len(index):assert index.min()>=0 and index.max()<len(position)
   w=triangles(position[index]);streams[m]=dict(completeWorldTriangles=w.tolist(),worldSHA256=sha(w))
   if len(position):bounds.append(position[:,[0,2]])
  rows.append(dict(uid=a['uid'],role='current-BASIC',suppressionVerbatim=a['currentSuppressedByNativeUIDs'],emptyConstructorIsAccountedNotFabricated=not len(index),worlds=streams))
 bounds.append(worlds[MODES[0]][:,:,[0,2]].reshape(-1,2));all_points=np.concatenate(bounds);roi=[float(all_points[:,0].min()),float(all_points[:,1].min()),float(all_points[:,0].max()),float(all_points[:,1].max())]
 domain=[2002.5,-2067.5,2212.5,-1927.5];roi=[min(roi[0],domain[0]),min(roi[1],domain[1]),max(roi[2],domain[2]),max(roi[3],domain[3])]
 return rows,roi,source_ref

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 prior.load();receipt=read(CAP/'result.json');cert=read(CAP/'ROOT-VERIFIED.json');assert receipt['jobId']==cert['jobId']=='8957fe78a3009e63d79de2f1e4b56ee5cb440b5c03392fd14483c5edecace320'and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
 assert ref(CAP/'result.json')['sha256']=='fa6c329a0007bea6d0684da99b6dadc00751258e12b7bbc302f934cffeecc80b'
 viability=read(CAP/'guard-first-viability.json');assert not viability['ordinaryGuardFailures']and not viability['allSamplerErrors']and not viability['gridErrors']
 rows,roi,source_ref=actor_inputs();assert roi==pins['completeWholeActorROI']
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');models={};sources={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for e in read(path)['models']:assert e['uid']not in models;models[e['uid']]=e;sources[e['uid']]=path.parent/e['asset']
 assert len(models)==6653;requested=set(DELTAS)
 for uid in DELTAS:
  for dep in models[uid].get('supportDependencies',[]):requested.add(dep if isinstance(dep,str)else dep['uid'])
 assert requested==set(DELTAS) # actual installed entries, no undeclared callback dependency
 forms={}
 for tile in manifest['tiles']:
  for f in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
   if f['uid']in requested:assert f['uid']not in forms;forms[f['uid']]=f
 assert set(forms)==requested
 uids=[f['uid']for f in read(CAP/'input.json.gz')['exact25CurrentForms']]+DELTAS;assert len(set(uids))==28
 resources=sorted([('building:'if u.startswith('landsd/')else'foreign-form:')+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]);assert len(resources)==57 and reservations.normalise(resources)==resources
 return pins,rows,roi,source_ref,forms,models,sources,resources

def schema_only():
 p,rows,roi,_,forms,_,_,resources=load()
 return dict(passed=True,completeWholeActorROI=roi,completeOwnedFaces=10536,nativeFaces=59527,BASICRows=24,actualDeltaUIDs=DELTAS,canonicalResources=resources,noSourceDecodeGroundGuardFiniteDBLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,rows,roi,source_ref,forms,models,sources,resources=load();assert lease['resources']==resources
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(read(CAP/'result.json')['jobId'],)).fetchone()==('complete',read(CAP/'result.json'))
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==prior.binding.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();save(DOC/'complete-saved-actor-worlds.json.gz',dict(rows=rows,completeWholeActorROI=roi,sourceContext=source_ref,noActorSourceReDecode=True,noPhysicalAcceptance=True))
 delta=[]
 for uid in DELTAS:
  source=ref(sources[uid]);assert source['sha256']==models[uid]['sha256'];proof=packed_world_bounds(check(source).read_bytes());assert proof['allOriginalPositionVerticesAccounted']and proof['sourceSHA256']==source['sha256']and proof['completeOriginalTriangles']==models[uid]['triangles']
  delta.append(dict(uid=uid,source=source,rawCurrentEntry=models[uid],currentBuilding=forms[uid],completeOriginalPOSITIONProof=proof));refs=distinct_refs(refs+[source]);pulse()
 save(DOC/'input.json.gz',dict(schema='polyu-full-actor-current-ground-delta3-v1',candidate=ref(CAP/'private-native-terrain-candidate.json.gz'),allInputRefs=refs,completeWholeActorROI=roi,alteredDomain=[2002.5,-2067.5,2212.5,-1927.5],deltaRows=delta,declaredCurrentForms=forms,noGuardFinitePairRayOrApprovalReplay=True,currentManifestSHA256=prior.binding.CURRENT))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))]
 with(DOC/'actual-ground-delta3-runtime.log').open('xb')as log:proc=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(command=command,exitCode=proc.returncode,noLiveChanges=True))
 if proc.returncode==0:
  result=read(DOC/'diagnostic.json.gz');assert result['startEndAllInputsVerified']and result['strictOutsideDrawUnchanged']
  refs=distinct_refs(refs+[dict(path=p,sha256=h)for p,h in result['inputHashes'].items()])
 refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 spec=importlib.util.spec_from_file_location('polyu_whole_ground_freezer',prior.FREEZER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'complete-saved-native-owned-and-BASIC-ROI-actual-current-ground-plus-three-new-native-bounds',[check(q)for q in refs],dict(uids=sorted(set([r['uid']for r in rows]+DELTAS)),sourceOnly=True,privateCandidate=True,newlyInstalled=0,physicalAccepted=False,runtimeExitCode=proc.returncode))
 fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),runtimeExitCode=proc.returncode)),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
 if '--owned'in sys.argv:return owned()
 assert '--capture-whole-actor-ground-delta3-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
 claim=reservations.claim('polyu-whole-ground-delta3-'+str(uuid.uuid4()),load()[-1],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
