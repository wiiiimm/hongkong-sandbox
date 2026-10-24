"""UNEXECUTED fresh unchanged Ocean Walk actual geometry/terrain diagnostic input.
Old source bytes are reused, never old rendered/module/current approval evidence.
"""
import copy,importlib.util,json,subprocess,sys,uuid,types
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import'
OLD=BASE/'government-xl-ocean-walk-current-terrain-complete-scope-20261008'
INVENTORY=BASE/'government-xl-ocean-walk-current-grade-paths-draft-v1-20261012/historical-source-and-obligation-inventory.json'
BATCH='government-xl-ocean-walk-current-actual-ground-capture-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JS=HERE/'xl-ocean-walk-81743-current-actual-ground-geometry-v1-20261012.mjs'
UID='landsd/81743:0';SOURCE='52e0d6b6341f664cc18ee8a894e1c4c5e5dbc1b05729bb43deb8c109e0fac8cb';MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
HELPERS=['run.py','exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py','xl-final-script-pass.py','literal_production_module_dependency_closure_20261010.mjs','actual_float32_model_matrix_bounds_20261011.mjs','current_geometry_capture_preflight_20261011.mjs','xl-popcorn-source-investigations-checkpoints-20261009.py']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def imported_local_files(*extra_modules):
 # Pin modules actually imported by the reused form loader/freezer, including
 # explicit spec-loaded module objects that are not registered in sys.modules.
 queue=list(sys.modules.values())+list(extra_modules);seen=set();files=set()
 while queue:
  m=queue.pop()
  if not isinstance(m,types.ModuleType)or id(m)in seen:continue
  seen.add(id(m));name=getattr(m,'__file__',None)
  if not name:continue
  p=Path(name).resolve()
  if ROOT not in p.parents or not p.is_file():continue
  files.add(p);queue.extend(v for v in vars(m).values()if isinstance(v,types.ModuleType))
 return sorted(files)

def preflight():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==MANIFEST
 historical=read(INVENTORY);assert len(historical['sourceActors'])==18 and sum(r['completeFaces']for r in historical['sourceActors'])==28858
 assert len(historical['sixPriorBasicRegressions'])==6 and len(historical['unresolvedInterfaceUIDs'])==11 and len(historical['prior17InterfaceRowsVerbatim'])==17
 refs=[Path(__file__),JS,INVENTORY,OLD/'selection.json.gz',OLD/'result.json']+[HERE/n for n in HELPERS]+[HERE.parent/'shared-modelling'/n for n in ['db.py','jobs.py','reservations.py']]
 for pin in historical['originalSelectionAndReceiptPins']+historical['additionalPriorNegativeEvidencePins']:
  p=ROOT/pin['path'];assert ref(p)==pin;refs.append(p)
 for r in historical['sourceActors']:
  p=ROOT/r['assetPath'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p)
 old_own=[r for r in historical['sourceActors']if r['uid']==UID];assert len(old_own)==1
 source_selection=ROOT/old_own[0]['selectionPath'];saved=[r for r in read(source_selection)['rows']if r['uid']==UID];assert len(saved)==1;row=copy.deepcopy(saved[0])
 assert row['sourceSHA256']==SOURCE and row['triangles']==15484 and row['modelId']=='B146372594202063C0'
 entry=row['candidate']['entry'];assert entry==old_own[0]['originalCandidateEntry'] and old_own[0]['completeFaces']==15484;assert entry['sha256']==SOURCE and entry['uid']==UID and entry['rootTranslation']==[-834500,0,816500]
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE;refs.append(asset)
 original=decode_original_world_triangles(raw);assert original.shape==(15484,3,3)and np.isfinite(original).all();position=packed_world_bounds(raw)
 b=position['originalWholeSourceBounds'];bounds=[b[0][0]-4,b[0][2]-4,b[1][0]+4,b[1][2]+4]
 final=module('ocean_fresh_forms','xl-final-script-pass.py');forms=final.load_forms(bounds);assert len(forms)==len({f['uid']for f,_,_ in forms})
 own=[(f,t)for f,_,t in forms if f['uid']==UID];assert len(own)==1;f,t=own[0];assert f['objectId']==81743 and f['buildingCSUID']=='1463725942P20060311'
 row['source']=dict(building=f,tile=t,tileSHA256=digest((ROOT/'3d-viewer'/t).read_bytes()))
 tile_pins={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms}
 catalogue_refs=[];native=[]
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogue_refs.append(ref(p));native.extend(read(p)['models'])
 assert len(native)==6649 and len({r['uid']for r in native})==6649 and UID not in {r['uid']for r in native}
 freezer_module=module('ocean_capture_freezer_preflight','xl-popcorn-source-investigations-checkpoints-20261009.py');refs.extend(imported_local_files(final,freezer_module))
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 resources=sorted(set(['building:'+r['uid']for r in historical['sourceActors']]+[('building:'+f['uid'])if f['uid'].startswith('landsd/')else('source-form:'+f['uid'])for f,_,_ in forms]+['terrain-patch:'+UID]))
 return before,historical,refs,pins,row,original,position,bounds,forms,tile_pins,catalogue_refs,resources

def main():
 assert not DOC.exists(),'Immutable completed/failed attempt';state=preflight()
 if '--owned'not in sys.argv:
  assert not LOCAL.exists();claim=reservations.claim('ocean-current-actual-ground-'+str(uuid.uuid4()),state[-1],batch=BATCH,ttl=3600);assert claim['ok'],claim
  save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True);return
 before,historical,refs,pins,row,original,position,bounds,forms,tile_pins,catalogue_refs,resources=state;lease=read(LEASE);assert lease['resources']==resources and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');n=row['native'];found=c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,n['cacheKey'])).fetchall();assert found==[(n['resultSha'],)]
 DOC.mkdir()
 # Archive raw manifest bytes, not a JSON re-encoding claimed byte-identical.
 (DOC/'captured-manifest.json').write_bytes(before)
 save(DOC/'selection.json.gz',dict(batch=BATCH,manifestSHA256=MANIFEST,rows=[row],currentIdentityAccepted=False))
 save(DOC/'context.json.gz',dict(manifestSHA256=MANIFEST,currentAcceptance=False,completeCurrentForms=[f for f,_,_ in forms]))
 save(DOC/'all-current-catalogues.json',dict(rows=catalogue_refs,completeNativeActors=6649))
 save(DOC/'capture-inputs.json.gz',dict(rows=[row],completeCurrentForms=[f for f,_,_ in forms],completeCurrentFormBounds=bounds,neighbourTileHashes=tile_pins,completeCurrentCatalogueRefs=catalogue_refs,inputHashes=pins,manifestSHA256=MANIFEST,canonicalResources=resources,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 save(DOC/'whole-original-position-proof-81743-0.json',position)
 status=subprocess.run(['node',str(JS),UID],cwd=ROOT,capture_output=True,text=True);save(DOC/'export-81743-0-log.json',dict(exitCode=status.returncode,stdout=status.stdout,stderr=status.stderr));assert status.returncode==0,status.stderr
 capture=read(DOC/'complete-current-actual-source-and-ground-81743-0.json.gz');assert capture['uid']==UID and capture['sourceSHA256']==SOURCE and capture['entry']==row['candidate']['entry']and capture['completeFaces']==15484 and capture['startAndEndInputsVerified']and capture['completeOriginalPOSITIONProof']==position
 index=np.asarray(capture['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);worlds={'providerOriginal':original}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(capture[key],dtype='<f8').reshape(-1,3)[index]
 assert all(w.shape==(15484,3,3)and np.isfinite(w).all()for w in worlds.values())
 ground=np.asarray(capture['currentDrawnGround']['completeRegionalPosition'],dtype='<f8').reshape(-1,3,3);assert len(ground)==capture['currentDrawnGround']['completeRegionalFaces']and np.isfinite(ground).all()and digest(ground.tobytes())==capture['currentDrawnGround']['worldTriangleSHA256']
 save(DOC/'complete-four-stream-ground-inputs.json.gz',dict(uid=UID,sourceSHA256=SOURCE,completeWorldStreams={m:dict(completeFaces=15484,completeWorldTriangleSHA256=digest(w.astype('<f8').tobytes()),completeWorldTriangles=w.tolist())for m,w in worlds.items()},completeDrawnGround=ground.tolist(),completeDrawnGroundSHA256=digest(ground.tobytes()),allSlopesAndZeroProjectionGroundRetained=True,noHistoricalRuntimeProofTransfer=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 for p,h in {**pins,**capture['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h
 for t,h in tile_pins.items():assert digest((ROOT/'3d-viewer'/t).read_bytes())==h
 for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 refs.extend(ROOT/p for p in capture['inputHashes']);refs.extend(p for p in DOC.rglob('*')if p.is_file())
 freezer=module('ocean_capture_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');out=freezer.freeze(BATCH,'ocean-walk-fresh-whole-original-four-world-current-ground-no-role-credit',refs,dict(uids=[UID],completeSourceFaces=15484,completeHistoricalActors=18,historicalFaces=28858,currentNativeActors=6649,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
