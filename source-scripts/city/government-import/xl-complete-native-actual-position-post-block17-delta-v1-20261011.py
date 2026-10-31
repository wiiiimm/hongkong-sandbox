"""Current native actual-bounds rebind: exact 6637 baseline + two independently loaded real deltas.
No catalogue bounds/original-POSITION geographic inference substitutes for
actual full mesh attributes/matrices/literal/declared Float32 arithmetic bounds.
"""
from pathlib import Path
import json,re,subprocess,importlib.util,sys
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from actual_native_bounds_baseline_rebind_20261011 import validate_unchanged_actor
from actual_native_post_block17_census_20261011 import exact_post_block17_census
BATCH='government-xl-complete-native-actual-position-post-block17-delta-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
OLD=DOC.parent/'government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011'
CURRENT=None # Required final installed manifest SHA supplied by root CLI.
EXPORTER=HERE/'xl-complete-native-actual-position-post-block17-delta-v1-20261011.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical_sha(value):return digest(json.dumps(value,sort_keys=True,separators=(',',':')).encode())
def main():
 assert not DOC.exists();manifestpath=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifestpath);assert start['sha256']==CURRENT
 old_receipt=read(OLD/'result.json');old_input=read(OLD/'input.json.gz');old=read(OLD/'inventory.json.gz')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old_receipt['jobId'],)).fetchone()==('complete',old_receipt)
 assert ref(OLD/'inventory.json.gz') in old_receipt['evidenceRefs'] and ref(OLD/'input.json.gz') in old_receipt['evidenceRefs']
 assert old['completeNativeActors']==old['successfullyCapturedActors']==6637 and not old['errors'] and old['startAndEndInputHashesVerified'] is True
 old_rows={r['uid']:r for r in old['rows']};old_inputs={r['uid']:r for r in old_input['rows']};assert len(old_rows)==len(old_inputs)==6637 and set(old_rows)==set(old_inputs)
 # Complete production loader dependency bytes must remain exactly unchanged.
 for path,sha in old['completeRecursiveProductionModuleClosure']['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 for path,sha in old_input['declaredDependencyUIDSourceHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 manifest=read(manifestpath);models={};catalogues=[];sources={};refs=[manifestpath,Path(__file__),EXPORTER,OLD/'result.json',OLD/'input.json.gz',OLD/'inventory.json.gz',HERE/'exact_packed_world_bounds_v3_20261010.py']
 DOC.mkdir(parents=True);(DOC/'captured-manifest.json').write_bytes(manifestpath.read_bytes())
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogues.append(dict(**ref(path),originalPath='3d-viewer/'+url));refs.append(path)
  for e in read(path)['models']:
   assert e['uid'] not in models;models[e['uid']]=e;sources[e['uid']]=path.parent/e['asset']
 assert exact_post_block17_census(list(old_rows),list(models))
 dependency_uids=set(models);dependency_hashes={}
 for dependency in (ROOT/'3d-viewer/city').glob('official-model-*.js'):
  dependency_hashes[str(dependency.relative_to(ROOT))]=digest(dependency.read_bytes());dependency_uids.update(re.findall(r'landsd/\d+:0',dependency.read_text()))
 assert dependency_hashes==old_input['declaredDependencyUIDSourceHashes']
 forms={};tilehashes={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];hits=[b for b in read(path)['buildings'] if b['uid'] in dependency_uids]
  if hits:
   tilehashes[str(path.relative_to(ROOT))]=digest(path.read_bytes());refs.append(path)
   for b in hits:assert b['uid'] not in forms;forms[b['uid']]=b
 assert set(models).issubset(forms)
 reused=[]
 for uid,oldrow in old_rows.items():
  e=models[uid];prior=old_inputs[uid];source=sources[uid];assert e==prior['rawCurrentEntry'] and forms[uid]==prior['currentBuilding'] and e['sha256']==oldrow['sourceSHA256']
  assert ref(source)==prior['source'] and digest(source.read_bytes())==oldrow['sourceSHA256']
  assert oldrow['sourceFacesOmitted']==0 and oldrow['wholeUnusedPositionVerticesIncluded'] is True and oldrow['completeFaces']==e['triangles']
  assert oldrow['completePositionVertices']==prior['completeOriginalPOSITIONProof']['completeOriginalPositionVertices']
  assert all(m['wholePositionVerticesIncludingUnused'] is True for m in oldrow['actualRenderMeshes'])
  assert validate_unchanged_actor(prior,oldrow,e,forms[uid],ref(source),digest(source.read_bytes()))==oldrow
  reused.append(dict(uid=uid,source=ref(source),currentRawEntrySHA256=canonical_sha(e),currentViewerFormSHA256=canonical_sha(forms[uid]),unchangedActualCompleteBoundsRowSHA256=canonical_sha(oldrow),baselineInventory=ref(OLD/'inventory.json.gz')));refs.append(source)
 newrows=[]
 for uid in ['landsd/255438:0','landsd/256116:0']:
  entry=models[uid];source=sources[uid];raw=source.read_bytes();assert digest(raw)==entry['sha256'];proof=packed_world_bounds(raw);assert proof['completeOriginalTriangles']==entry['triangles'] and proof['allOriginalPositionVerticesAccounted'] is True
  newrow=dict(uid=uid,source=ref(source),catalogue=next(r for r in catalogues if any(e['uid']==uid for e in read(ROOT/r['path'])['models'])),rawCurrentEntry=entry,currentBuilding=forms[uid],completeOriginalPOSITIONProof=proof)
  newrows.append(newrow);refs.append(source)
 inp=dict(currentManifest=start,currentActualBoundsDeltaOnly=True,currentCatalogueRefs=catalogues,currentNativeViewerTileHashes=tilehashes,currentAllNativeSourceForms=forms,declaredDependencyUIDSourceHashes=dependency_hashes,completeNativeActors=6639,rows=newrows,evidenceRefs=[ref(OLD/'result.json'),ref(OLD/'inventory.json.gz'),ref(OLD/'input.json.gz')],sourceGeometryChanges=0,terrainGeometryChanges=0)
 save(DOC/'input.json.gz',inp);save(DOC/'complete-unchanged-baseline-bindings.json.gz',dict(currentManifest=start,completeOldActorsRebound=6637,rows=reused,baselineInventory=ref(OLD/'inventory.json.gz'),allCurrentEntrySourceViewerModulePinsExactlyUnchanged=True,sourceGeometryChanges=0,terrainGeometryChanges=0))
 proc=subprocess.run(['node','--expose-gc',str(EXPORTER)],cwd=ROOT,capture_output=True,text=True);save(DOC/'export-log.json',dict(exitCode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr));assert proc.returncode==0,proc.stderr
 delta=read(DOC/'inventory.json.gz');assert delta['currentActualBoundsDeltaOnly'] is True and delta['successfullyCapturedActors']==2 and not delta['errors'] and delta['startAndEndInputHashesVerified'] is True
 assert [r['uid'] for r in delta['rows']]==['landsd/255438:0','landsd/256116:0']
 save(DOC/'composition.json.gz',dict(currentManifest=start,completeCurrentNativeActors=6639,completeOldActorsExactlyRebound=6637,completeActualNewActorUIDs=[r['uid'] for r in newrows],baselineInventory=ref(OLD/'inventory.json.gz'),baselineCurrentExactBinding=ref(DOC/'complete-unchanged-baseline-bindings.json.gz'),actualCurrentDelta=ref(DOC/'inventory.json.gz'),allUnusedPositionVerticesIncluded=True,allDeclaredActualLiteralLeftBalancedBoundsComplete=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0))
 assert ref(manifestpath)==start
 for binding in reused:assert ref(ROOT/binding['source']['path'])==binding['source']
 refs += [source,DOC/'input.json.gz',DOC/'captured-manifest.json',DOC/'inventory.json.gz',DOC/'complete-unchanged-baseline-bindings.json.gz',DOC/'composition.json.gz',DOC/'export-log.json',*[ROOT/p for p in delta['inputHashes']],HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'literal_production_module_dependency_closure_20261010.mjs',HERE/'current_geometry_capture_preflight_20261011.mjs',HERE/'actual_native_bounds_baseline_rebind_20261011.py',HERE/'test_actual_native_bounds_baseline_rebind_20261011.py',HERE/'actual_native_post_block17_census_20261011.py',HERE/'test_actual_native_post_block17_census_20261011.py']
 for path,sha in delta['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 s=importlib.util.spec_from_file_location('lippo_all_current_native_bounds_rebind_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 receipt=m.freeze(BATCH,'post-block17-exact-6637-actual-baseline-plus-two-actual-position-matrix-current-deltas',refs,dict(uids=[],currentManifest=start,completeNativeActors=6639,completeExactlyUnchangedBaselineActors=6637,newActualDeltaUIDs=[r['uid'] for r in newrows],physicalAccepted=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0))
 print(json.dumps(dict(jobId=receipt['jobId'],completeNativeActors=6639)),flush=True)
if __name__=='__main__':
 assert len(sys.argv)==2 and re.fullmatch(r'[a-f0-9]{64}',sys.argv[1]);CURRENT=sys.argv[1];main()
