"""Fresh6661 original-source scalar bounds with current production modules.

Every actor is actually loaded with current source/form/entry/module inputs.
Only identical provider-source POSITION proofs are cached; no old runtime row
or signature is transferred. Full unused vertices, literal+two explicit F32
orders; output scalar bounds/matrix/attribute hashes, not redundant streams.
No scene writes, old native reapproval, source support or installation credit.
"""
from pathlib import Path
import importlib.util,json,re,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds

BATCH='government-xl-complete-current-native-actual-position-matrix-bounds-v6-20261015'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PRIOR=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015'
EXPORTER=HERE/'xl-complete-current-native-actual-position-matrix-bounds-v6-20261015.mjs'
CURRENT='9fa4035f31a218cec04f418b83e7545148f70e4fa966287e7b4eb67d61007c56'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def owned():
 assert reservations.owns(read(LEASE))and not DOC.exists()
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifestpath);assert start['sha256']==CURRENT
 manifest=read(manifestpath);receipt=read(PRIOR/'result.json');inventory_path=PRIOR/'inventory.json.gz'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(inventory_path)in receipt['evidenceRefs']
 kernel=HERE/'exact_packed_world_bounds_v3_20261010.py';assert ref(kernel)in receipt['evidenceRefs']
 prior=read(inventory_path);assert prior['successfullyCapturedActors']==6661 and len(prior['rows'])==6661 and not prior['errors']
 # Reuse only exact immutable provider-source proofs; runtime is freshly captured below.
 method=BASE/(BATCH+'-proposal')/'METHOD.md';assert method.is_file()
 cache={}
 for r in prior['rows']:
  proof=r['completeOriginalPOSITIONProof'];assert proof['sourceSHA256']==r['sourceSHA256']and proof['allOriginalPositionVerticesAccounted']
  if r['sourceSHA256']in cache:assert cache[r['sourceSHA256']]==proof
  cache[r['sourceSHA256']]=proof
 refs=[Path(__file__),EXPORTER,kernel,manifestpath,PRIOR/'result.json',inventory_path,method]
 pins={p['path']:p['sha256']for p in map(ref,refs)}
 models={};catalogues=[];sources={};dependencies=set()
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;pin=ref(path);catalogues.append(dict(**pin,originalPath=pin['path']));refs.append(path);pins[pin['path']]=pin['sha256']
  for e in read(path)['models']:
   assert e['uid']not in models;models[e['uid']]=e;sources[e['uid']]=path.parent/e['asset']
   for dependency in e.get('supportDependencies',[]):
    if isinstance(dependency,str):dependencies.add(dependency)
    else:assert isinstance(dependency,dict);dependencies.add(dependency['uid'])
 assert len(models)==6662
 dependency_source_hashes={}
 for module in (ROOT/'3d-viewer/city').glob('official-model-*.js'):
  p=ref(module);dependency_source_hashes[p['path']]=p['sha256'];refs.append(module);pins[p['path']]=p['sha256']
  dependencies.update(re.findall(r'landsd/\d+:0',module.read_text()))
 requested=set(models)|dependencies;forms={};tilehashes={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();hits=[b for b in read(path)['buildings']if b['uid']in requested]
  if hits:
   tilehashes[str(path.relative_to(ROOT))]=digest(raw);refs.append(path);pins[str(path.relative_to(ROOT))]=digest(raw)
   for b in hits:assert b['uid']not in forms;forms[b['uid']]=b
 assert set(models)<=set(forms)
 rows=[]
 for uid,e in models.items():
  source=sources[uid];raw=source.read_bytes();pin=ref(source);assert pin['sha256']==e['sha256']and e['buildingCSUID']==forms[uid]['buildingCSUID']
  if e['sha256']not in cache:cache[e['sha256']]=packed_world_bounds(raw)
  proof=cache[e['sha256']];assert proof['sourceSHA256']==e['sha256']and proof['completeOriginalTriangles']==e['triangles']and proof['allOriginalPositionVerticesAccounted']
  rows.append(dict(uid=uid,source=pin,rawCurrentEntry=e,currentBuilding=forms[uid],completeOriginalPOSITIONProof=proof));refs.append(source);pins[pin['path']]=pin['sha256']
 DOC.mkdir(parents=True);(DOC/'captured-manifest.json').write_bytes(manifestpath.read_bytes())
 save(DOC/'dependency-form-census.json',dict(completeNativeActors=6662,requestedDependencyUIDs=sorted(dependencies),
  missingDeclaredUIDs=sorted(requested-set(forms)),availableBasicDependencyUIDs=sorted(set(forms)-set(models)),nominationOnlyNotAcceptance=True))
 input=dict(currentBoundOnly=True,currentManifest=start,capturedManifest=ref(DOC/'captured-manifest.json'),
  completeNativeActors=6662,currentCatalogueRefs=catalogues,currentNativeViewerTileHashes=tilehashes,
  currentAllNativeSourceForms=forms,declaredDependencyUIDSourceHashes=dependency_source_hashes,
  rows=rows,evidenceRefs=[ref(Path(__file__)),ref(PRIOR/'result.json'),ref(inventory_path),ref(kernel)],
  cachedProofsAreIdenticalProviderSourceOnly=True,oldActualRuntimeRowsReused=False,sourceGeometryChanges=0,terrainGeometryChanges=0)
 save(DOC/'input.json.gz',input)
 process=subprocess.run(['node','--expose-gc',str(EXPORTER)],cwd=ROOT,capture_output=True,text=True)
 save(DOC/'export-log.json',dict(exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));assert process.returncode==0,process.stderr
 out=read(DOC/'inventory.json.gz');assert out['currentBoundOnly']and out['completeNativeActors']==out['successfullyCapturedActors']==6662 and not out['errors']and out['startAndEndInputHashesVerified']
 assert len(out['rows'])==len({r['uid']for r in out['rows']})==6662 and {r['uid']for r in out['rows']}==set(models)
 assert ref(manifestpath)==start and reservations.owns(read(LEASE))
 for p,h in {**pins,**out['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(ROOT/p for p in out['inputHashes'])
 refs.extend(HERE/h for h in ['actual_float32_model_matrix_bounds_20261011.mjs','test_actual_float32_model_matrix_bounds_20261011.mjs',
  'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','test_exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs',
  'current_geometry_capture_preflight_20261011.mjs','test_current_geometry_capture_preflight_20261011.mjs'])
 refs.extend(p for p in DOC.rglob('*')if p.is_file())
 spec=importlib.util.spec_from_file_location('shared_fresh_native_scalar_bounds_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'shared-fresh6662-current-production-whole-unused-POSITION-scalar-bounds-and-matrices',refs,
  dict(uids=[],currentManifest=start,completeNativeActors=6662,allUnusedPositionVerticesIncluded=True,
   freshEveryActorActualLoad=True,oldActualRuntimeRowsReused=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=result['jobId'],completeNativeActors=6662)),flush=True)

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 claim=reservations.claim('shared-native6662-actual-bounds-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
