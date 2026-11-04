"""Complete current production native POSITION/matrix/arithmetic bounds only."""
from pathlib import Path
import importlib.util,json,subprocess,re
from run import ROOT,HERE,read,save,digest,connect
BATCH='government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INV=DOC.parent/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v6'
EXPORTER=HERE/'xl-complete-current-native-actual-position-matrix-bounds-v2-20261011.mjs'
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
def main():
 assert not DOC.exists();manifestpath=ROOT/'3d-viewer/city/data/manifest.json';baseline=DOC.parent/'government-xl-complete-current-native-actual-position-matrix-bounds-v1-20261011';before=(baseline/'captured-manifest.json').read_bytes();manifest=json.loads(before);inventory=read(INV/'inventory.json.gz');assert inventory['currentManifest']['sha256']==digest(before) and inventory['completeNativeActors']==6637
 receipt=read(INV/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 DOC.mkdir(parents=True);(DOC/'captured-manifest.json').write_bytes(before)
 models={};catalogues=[]
 for url in manifest['officialModelCatalogues']:
  path=baseline/'captured-catalogues'/('3d-viewer/'+url);archived=DOC/'captured-catalogues'/('3d-viewer/'+url);archived.parent.mkdir(parents=True,exist_ok=True);archived.write_bytes(path.read_bytes());catalogues.append(dict(**ref(archived),originalPath='3d-viewer/'+url))
  for e in read(path)['models']:
   assert e['uid'] not in models;models[e['uid']]=e
 assert len(models)==6637 and set(models)=={r['uid'] for r in inventory['rows']}
 forms={};tilehashes={};dependency_source_hashes={};dependency_uids=set(models)
 for dependency in (ROOT/'3d-viewer/city').glob('official-model-*.js'):
  text=dependency.read_text();dependency_source_hashes[str(dependency.relative_to(ROOT))]=digest(dependency.read_bytes());dependency_uids.update(re.findall(r'landsd/\d+:0',text))
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];hits=[b for b in read(path)['buildings'] if b['uid'] in dependency_uids]
  if hits:
   tilehashes[str(path.relative_to(ROOT))]=digest(path.read_bytes())
   for b in hits:assert b['uid'] not in forms;forms[b['uid']]=b
 assert set(models).issubset(forms),'Every actual native must uniquely match its current viewer form';missing_declared=sorted(dependency_uids-set(forms))
 save(DOC/'dependency-form-census.json',dict(requestedNativeUIDs=len(models),literalModuleDependencyUIDs=len(dependency_uids-set(models)),availableBasicDependencyForms=len(set(forms)-set(models)),missingLiteralUIDs=missing_declared,nominationOnlyNotAcceptance=True))
 rows=[]
 for r in inventory['rows']:
  e=models[r['uid']];assert e==r['rawCurrentEntry'] and e['sha256']==r['sourceSHA256'] and e['buildingCSUID']==forms[r['uid']]['buildingCSUID'];assert digest((ROOT/r['source']['path']).read_bytes())==r['sourceSHA256']
  rows.append(dict(uid=r['uid'],source=r['source'],catalogue=r['catalogue'],rawCurrentEntry=e,currentBuilding=forms[r['uid']],completeOriginalPOSITIONProof=r['completeOriginalPOSITIONProof']))
 inp=dict(currentManifest=ref(DOC/'captured-manifest.json'),originalLiveManifestAtCaptureStart=ref(manifestpath),capturedBaselineOnly=True,currentCatalogueRefs=catalogues,currentNativeViewerTileHashes=tilehashes,currentAllNativeSourceForms=forms,declaredDependencyUIDSourceHashes=dependency_source_hashes,completeNativeActors=6637,rows=rows,evidenceRefs=[ref(Path(__file__)),ref(INV/'result.json'),ref(INV/'inventory.json.gz')],sourceGeometryChanges=0,terrainGeometryChanges=0)
 save(DOC/'input.json.gz',inp);process=subprocess.run(['node','--expose-gc',str(EXPORTER)],cwd=ROOT,capture_output=True,text=True);save(DOC/'export-log.json',dict(exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));assert process.returncode==0,process.stderr
 out=read(DOC/'inventory.json.gz');assert out['completeNativeActors']==out['successfullyCapturedActors']==6637 and not out['errors'] and out['startAndEndInputHashesVerified']
 save(DOC/'observed-live-manifest-end.json',dict(originalLiveManifestAtCaptureStart=inp['originalLiveManifestAtCaptureStart'],observedLiveManifestAtCaptureEnd=ref(manifestpath),manifestChangedDuringReadOnlyBaselineCapture=manifestpath.read_bytes()!=before,capturedBaselineOnly=True,finalCurrentRebindRequired=True))
 for path,sha in out['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 refs=[Path(__file__),EXPORTER,INV/'result.json',INV/'inventory.json.gz',DOC/'input.json.gz',DOC/'inventory.json.gz',DOC/'export-log.json',DOC/'observed-live-manifest-end.json',DOC/'captured-manifest.json',DOC/'dependency-form-census.json',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'test_actual_float32_model_matrix_bounds_20261011.mjs',HERE/'literal_production_module_dependency_closure_20261010.mjs',HERE/'test_literal_production_module_dependency_closure_20261010.mjs',HERE/'current_geometry_capture_preflight_20261011.mjs',HERE/'test_current_geometry_capture_preflight_20261011.mjs',*[ROOT/path for path in out['inputHashes']]]
 s=importlib.util.spec_from_file_location('actual_current_native_position_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 receipt=m.freeze(BATCH,'complete6637-current-production-native-whole-position-matrix-literal-left-balanced-bounds-v1',refs,dict(uids=[],capturedBaselineManifest=inp['currentManifest'],completeNativeActors=6637,finalCurrentRebindRequired=True,allUnusedPositionVerticesIncluded=True,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,sourceInventoryOnly=True))
 print(json.dumps(dict(jobId=receipt['jobId'],completeNativeActors=6637)),flush=True)
if __name__=='__main__':main()
