"""Fresh unchanged-current tower/BASIC/terrain inputs, never a terrain proposal."""
from pathlib import Path
import importlib.util,json,subprocess,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-lippo-tower-only-current-complete-inputs-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
IDENTITY=DOC.parent/'government-xl-lippo-tower-current-complete-original-identity-diagnostic-v3-20261011'
INVENTORY=DOC.parent/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v6'
EXPORTER=HERE/'xl-lippo-tower-only-current-complete-geometry-v2-20261011.mjs'
UID='landsd/239465:0';PODIUM='landsd/231645:0';SCOPE=[947.5,-1087.5,1087.5,-962.5]
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
def main():
 assert not DOC.exists();manifestpath=ROOT/'3d-viewer/city/data/manifest.json';before=manifestpath.read_bytes();manifest=json.loads(before)
 for folder in [IDENTITY,INVENTORY]:
  receipt=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert read(IDENTITY/'identity.json')['passed'] and read(IDENTITY/'identity.json')['reasons']==[]
 selected=read(IDENTITY/'selection.json.gz');assert selected['manifestSHA256']==digest(before) and len(selected['rows'])==1;row=selected['rows'][0];assert row['uid']==UID and row['triangles']==3597
 original=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
 assert np.all(original[:,:,[0,2]].min((0,1))>=np.array(SCOPE[:2])) and np.all(original[:,:,[0,2]].max((0,1))<=np.array(SCOPE[2:]))
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 spec=importlib.util.spec_from_file_location('lippo_tower_all_current_forms',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final)
 forms=final.load_forms(SCOPE);assert len({b['uid'] for b,_,_ in forms})==len(forms)
 scope_uids={b['uid'] for b,_,_ in forms};assert {UID,PODIUM,'landsd/237843:0','landsd/233997:0'}.issubset(scope_uids)
 inv=read(INVENTORY/'inventory.json.gz');assert inv['currentManifest']==ref(manifestpath) and inv['completeNativeActors']==6637
 catalogue_refs=[];entries={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogue_refs.append(ref(path))
  for entry in read(path)['models']:
   assert entry['uid'] not in entries;entries[entry['uid']]=dict(entry=entry,path=str((path.parent/entry['asset']).relative_to(ROOT)),catalogue=str(path.relative_to(ROOT)))
 assert len(entries)==6637 and not ({UID,PODIUM,'landsd/237843:0'}&set(entries))
 assert {r['uid'] for r in inv['rows']}==set(entries)
 # A generous read-only geographic capture, never a separation certificate.
 # All 6637 original-POSITION rows remain in the explicit census. Any final
 # foreign separation must independently bind actual required render bounds.
 nearby=[];native_census=[]
 for item in inv['rows']:
  entry=entries[item['uid']];assert item['rawCurrentEntry']==entry['entry'] and item['sourceSHA256']==entry['entry']['sha256']
  lo,hi=np.array(item['completeOriginalPOSITIONProof']['originalWholeSourceBounds'])
  hit=not (hi[0]<SCOPE[0]-10 or lo[0]>SCOPE[2]+10 or hi[2]<SCOPE[1]-10 or lo[2]>SCOPE[3]+10)
  native_census.append(dict(uid=item['uid'],sourceSHA256=item['sourceSHA256'],originalWholePOSITIONBounds=[lo.tolist(),hi.tolist()],capturedAsNearbyActualActor=hit,geographicCaptureSelectionOnlyNotSeparationProof=True))
  if hit:nearby.append(dict(uid=item['uid'],**entry))
 all_forms={b['uid']:b for b,_,_ in forms};tilehashes={str((ROOT/'3d-viewer'/url).relative_to(ROOT)):digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}
 for native in nearby:
  if native['uid'] not in all_forms:
   found=[]
   for tile in manifest['tiles']:
    path=ROOT/'3d-viewer'/tile['url'];matches=[b for b in read(path)['buildings'] if b['uid']==native['uid']]
    if matches:found.extend(matches);tilehashes[str(path.relative_to(ROOT))]=digest(path.read_bytes())
   assert len(found)==1,'Nearby installed actor must uniquely match the current viewer';all_forms[native['uid']]=found[0]
  native['building']=all_forms[native['uid']];assert native['entry']['buildingCSUID']==native['building']['buildingCSUID'] and digest((ROOT/native['path']).read_bytes())==native['entry']['sha256']
 claim=reservations.claim('lippo-tower-unchanged-current-inputs-'+str(uuid.uuid4()),['building:'+u for u in sorted(scope_uids|{n['uid'] for n in nearby})],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  evidence=[ref(Path(__file__)),ref(ROOT/row['candidate']['path']),ref(IDENTITY/'result.json'),ref(IDENTITY/'identity.json'),ref(IDENTITY/'selection.json.gz'),ref(IDENTITY/'context.json.gz'),ref(INVENTORY/'result.json'),ref(INVENTORY/'inventory.json.gz')]
  inp=dict(rows=[row],currentManifest=ref(manifestpath),currentCatalogueRefs=catalogue_refs,completeCurrentForms=[dict(building=b,existingNative=b['uid'] in entries,tile=url) for b,native,url in forms],currentAllSourceForms=all_forms,currentTileHashes=tilehashes,completeCurrentNativeOriginalPOSITIONCensus=native_census,nearbyCurrentNativeActors=nearby,geographicScope=SCOPE,evidenceRefs=evidence,terrainProposal=None,terrainGeometryChanges=0,originalGovernmentPodiumUsedAsSupport=False)
  native_forms=[r for r in inp['completeCurrentForms'] if r['existingNative']];basic_forms=[r for r in inp['completeCurrentForms'] if not r['existingNative']]
  assert len(forms)==21 and len(basic_forms)==20 and [r['building']['uid'] for r in native_forms]==['landsd/21915:0']
  assert all(entries[r['building']['uid']]['entry']['buildingCSUID']==r['building']['buildingCSUID'] for r in native_forms)
  assert len({r['building']['uid'] for r in native_forms+basic_forms})==21
  save(DOC/'input.json.gz',inp)
  process=subprocess.run(['node',str(EXPORTER)],cwd=ROOT,capture_output=True,text=True)
  save(DOC/'export-log.json',dict(exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));assert process.returncode==0,process.stderr
  output=read(DOC/'complete-current-geometry.json.gz');assert output['startAndEndInputHashesVerified'] and output['sourceGeometryChanges']==output['terrainGeometryChanges']==0
  assert output['row']['uid']==UID and output['row']['completeFaces']==3597 and output['completeCurrentBasicPodiumFaces']==284
  assert manifestpath.read_bytes()==before and reservations.owns(claim['reservation'])
  refs=[Path(__file__),EXPORTER,HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'test_actual_float32_model_matrix_bounds_20261011.mjs',HERE/'literal_production_module_dependency_closure_20261010.mjs',HERE/'test_literal_production_module_dependency_closure_20261010.mjs',DOC/'input.json.gz',DOC/'complete-current-geometry.json.gz',DOC/'export-log.json',*[ROOT/r['path'] for r in evidence],*[ROOT/path for path in output['inputHashes']]]
  sp=importlib.util.spec_from_file_location('lippo_current_no_terrain_capture_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  receipt=m.freeze(BATCH,'tower-only-unchanged-current-complete-actual-basic-native-terrain-and-model-matrix-inputs-v2-native-census',refs,dict(uids=[UID,PODIUM],currentManifest=ref(manifestpath),completeTowerFaces=3597,completeCurrentBasicPodiumFaces=284,completeCurrentNeighbourForms=len(forms),completeCurrentNativeOriginalPOSITIONActors=len(native_census),actualCapturedNearbyNativeActors=len(nearby),terrainGeometryChanges=0,originalGovernmentPodiumUsedAsSupport=False,physicalAccepted=False,installationApproved=False))
  print(json.dumps(dict(jobId=receipt['jobId'],currentForms=len(forms),allNativeOriginalPOSITIONActors=len(native_census),capturedNearbyNativeActors=len(nearby),terrainGeometryChanges=0)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
