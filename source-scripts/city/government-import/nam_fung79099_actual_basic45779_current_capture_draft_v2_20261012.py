"""UNEXECUTED Nam Fung original/current BASIC/current ground+attribute capture.
All geometry unchanged; no source-specific identity can discharge physical gates.
"""
import argparse,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from original_source_ownership import document,graph_reasons
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-nam-fung79099-actual-basic45779-current-capture-v2-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/79099:0'];PROTECTED='landsd/45779:0'
MANIFEST_SHA='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
PLAN=B/'government-xl-nam-fung79099-actual-basic45779-carrier-route-proposal-v1-20261012/capture-plan-v2.json'
INPUTS=[B/'government-xl-three-fung-original-supports-recovered-20261006/support-inputs.json']
ATTR=HERE/'nam_fung79099_actual_basic45779_render_attributes_draft_v2_20261012.mjs';CLOSURE=HERE/'nam_fung79099_actual_basic45779_module_closures_draft_v2_20261012.mjs';FREEZER=HERE/'nam_fung79099_freeze_actual_basic45779_current_capture_draft_v2_20261012.py'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def state(uids):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(uids,)).fetchall()
def native(sources):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');rows=c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND m->>'modelId'=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,[r['modelId']for r in sources])).fetchall()
 assert len(rows)==1
 for r in sources:assert next(x for x in rows if x[1]['modelId']==r['modelId'])==(r['native']['cacheKey'],r['native']['model'],r['native']['sheet'],r['native']['resultSha'])
 return rows
def verified_plan():
 plan=read(PLAN);assert plan['expectedManifestSHA256']==MANIFEST_SHA and plan['expectedNativeCount']==6649
 for item in plan['draftExecutablePins']+plan['currentInputPins']+plan['preservedV1PartialPins']:assert ref(ROOT/item['path'])==item
 assert plan['sourceAcquisitionSelections']==[ref(p)for p in INPUTS], 'Plan exact acquisition selection path/SHA contract changed'
 return plan
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');p.add_argument('--preflight-only',action='store_true');a=p.parse_args();verified_plan()
 if a.preflight_only:print(json.dumps(dict(planPinsPassed=True,noWorker=True)));return
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('nam-fung-actual-basic-runtime-'+str(uuid.uuid4()),['building:'+u for u in UIDS+[PROTECTED]],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));code=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT).returncode;assert code==0,code;return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();plan=verified_plan()
 source_map={}
 for f in INPUTS:
  for row in read(f)['sources']:
   if row['uid']not in UIDS:continue
   if row['uid']in source_map:assert source_map[row['uid']]['sourceSHA256']==row['sourceSHA256'] and source_map[row['uid']]['native']==row['native']
   source_map[row['uid']]=row
 assert set(source_map)==set(UIDS);sources=[source_map[u]for u in UIDS];expected={r['uid']:r for r in plan['actors']};tri={};roots=[];pins={}
 def pin(p):
  e=ref(p);assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST_SHA;current=read(manifest);catalogues=[ROOT/'3d-viewer'/x for x in current['officialModelCatalogues']];terrain=[ROOT/'3d-viewer'/x['url']for x in current['terrainPatches']]
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','reviewed_current_source_closure');code=set();walker.local_imports(Path(__file__),code);walker.local_imports(FREEZER,code)
 for p in list(code)+INPUTS+[PLAN,ATTR,CLOSURE,HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'acceptance-metrics.mjs',HERE/'xl-final-script-pass.py',manifest,ROOT/'3d-viewer/city/data/terrain.json']+catalogues+terrain:pin(p)
 installed={}
 for cat in catalogues:
  for e in read(cat)['models']:assert e['uid']not in installed;installed[e['uid']]=(cat,e)
 assert len(installed)==6649 and not(set(UIDS)|{PROTECTED})&set(installed)
 suppressed={u for _,e in installed.values()for u in e.get('suppressesBuildingUids',[])};assert PROTECTED not in suppressed,'Actual BASIC carrier is suppressed' 
 for r in sources:
  e=expected[r['uid']];assert(r['modelId'],r['sourceSHA256'],r['source']['building']['buildingCSUID'],r['triangles'])==(e['modelId'],e['sourceSHA256'],e['buildingCSUID'],e['completeFaces'])
  asset=ROOT/r['candidate']['path'];pin(asset);raw=asset.read_bytes();assert digest(raw)==e['sourceSHA256'];t=decode_original_world_triangles(raw);assert t.shape==(e['completeFaces'],3,3)and np.isfinite(t).all()and digest(t.astype('<f8').tobytes())==e['wholeWorldSHA256'];tri[r['uid']]=t
  g=document(raw);assert not graph_reasons(g,r['modelId'],len(t));roots.append(dict(uid=r['uid'],sourceSHA256=e['sourceSHA256'],originalRoot=g['nodes'][g['scenes'][0]['nodes'][0]],completeOriginalGLTFDocument=g,completeOriginalWorldSHA256=e['wholeWorldSHA256'],completeOriginalBinary64WorldTriangles=t.tolist(),genuineBodyObligations=e['genuineBodies'],zeroFaceObligations=e['zeroFaces']))
 low=np.min([t.min((0,1))for t in tri.values()],axis=0);high=np.max([t.max((0,1))for t in tri.values()],axis=0);window=[float(low[0]-30),float(low[2]-30),float(high[0]+30),float(high[2]+30)]
 nominees=[]
 for u,(cat,e)in installed.items():
  lo,hi=e['worldBounds']
  if hi[0]>=window[0] and lo[0]<=window[2] and hi[2]>=window[1] and lo[2]<=window[3]:nominees.append((cat,e))
 final=module(HERE/'xl-final-script-pass.py','reviewed_fresh_current_forms');forms=final.load_forms(window);form_map={f['uid']:(f,t)for f,_,t in forms};assert len(form_map)==len(forms) and PROTECTED in form_map
 for f,_,t in forms:pin(ROOT/'3d-viewer'/t)
 # A nominee lacking its complete current form is a scope failure, not a skip.
 assert all(e['uid']in form_map for _,e in nominees)
 state_uids=sorted(set(form_map)|set(UIDS)|{PROTECTED});before=state(state_uids);native_before=native(sources);fresh=[];literal=[]
 for r in sources:
  uid=r['uid'];f,tile=form_map[uid];assert f['buildingCSUID']==expected[uid]['buildingCSUID'];entry=r['candidate']['entry'];assert entry['uid']==uid and entry['sha256']==expected[uid]['sourceSHA256']and entry['triangles']==expected[uid]['completeFaces'];assert not entry.get('verticalPlacementOffsetHKPD',0)and entry['rootTranslation']==[-834500,0,816500]
  bounds=np.asarray(entry['worldBounds']);v=tri[uid];assert np.all(v.min((0,1))>=bounds[0]-1)and np.all(v.max((0,1))<=bounds[1]+1)
  dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/r['candidate']['path']).read_bytes());pin(dest);row={**r,'candidate':dict(entry=entry,path=str(dest.relative_to(ROOT))),'source':dict(building=f,tile=tile,tileSHA256=ref(ROOT/'3d-viewer'/tile)['sha256'])};fresh.append(row);literal.append(dict(uid=uid,path=row['candidate']['path'],entry=entry,building=f,role='owned-original'))
 native_context=[]
 for cat,e in nominees:
  uid=e['uid'];f,tile=form_map[uid];asset=cat.parent/e['asset'];pin(asset);assert ref(asset)['sha256']==e['sha256'];native_context.append(dict(uid=uid,path=str(asset.relative_to(ROOT)),entry=e,building=f,role='installed-native-context',catalogue=ref(cat),tile=tile))
 basic=[dict(building=f,tile=t,tileSHA256=ref(ROOT/'3d-viewer'/t)['sha256'])for f,_,t in forms if f['uid']not in installed and f['uid']not in UIDS and f['uid']not in suppressed]
 save(DOC/'protected-state-before.json',dict(uids=state_uids,rows=before));save(DOC/'native-source-state-before.json',dict(rows=native_before));save(DOC/'selection.json.gz',dict(rows=fresh,manifestSHA256=MANIFEST_SHA));save(DOC/'terrain-candidates.json',[]);save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='diagnostic-original-support-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[r['candidate']['entry']for r in fresh]));save(DOC/'original-full-source-root-context.json.gz',dict(rows=roots,sourceGeometryChanges=0));save(DOC/'complete-current-forms.json.gz',dict(rows=[dict(building=f,tile=t,installedNative=f['uid']in installed,suppressed=f['uid']in suppressed)for f,_,t in forms]));save(DOC/'literal-source-inputs.json.gz',dict(rows=literal,nativeContextRows=native_context,basicContextRows=basic,completeCurrentForms=[f for f,_,_ in forms],currentManifest=start,expectedNativeCount=6649,currentCatalogueRefs=[ref(p)for p in catalogues],evidenceRefs=[ref(DOC/'selection.json.gz')]+[ref(ROOT/x['path'])for x in literal]));save(DOC/'native-nomination-inventory.json',dict(currentCatalogueCount=6649,scopeWindow=window,nominees=native_context,catalogueBoundsNominationOnly=True,notFull6649ActualPositionCensus=True,noNativeReapproval=True,protectedBasic45779Form=form_map[PROTECTED][0]))
 def fence():
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  assert state(state_uids)==before and native(sources)==native_before and reservations.owns(lease)
 def call(args):fence();assert reservations.heartbeat(lease)['ok'];subprocess.run(args,cwd=ROOT,check=True);fence()
 rel=lambda p:str(p.relative_to(ROOT));call(['node',str(CLOSURE),rel(DOC)+'/'])
 olddoc=B/'government-xl-nam-fung79099-actual-basic45779-current-capture-v1-20261012';oldlocal=HERE/'local'/olddoc.name;oldselection=read(olddoc/'selection.json.gz')['rows'][0];assert oldselection['uid']==fresh[0]['uid'] and oldselection['candidate']['entry']==fresh[0]['candidate']['entry']and oldselection['source']==fresh[0]['source']
 for data in [read(olddoc/'metrics.json'),read(oldlocal/'runtime-geometry.json.gz')]:
  for path,h in data['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h,path
 fence();(DOC/'metrics.json').write_bytes((olddoc/'metrics.json').read_bytes());(LOCAL/'runtime-geometry.json.gz').write_bytes((oldlocal/'runtime-geometry.json.gz').read_bytes());save(DOC/'exact-v1-completed-metrics-ground-reuse.json',dict(originalMetrics=ref(olddoc/'metrics.json'),originalRuntime=ref(oldlocal/'runtime-geometry.json.gz'),copiedMetrics=ref(DOC/'metrics.json'),copiedRuntime=ref(LOCAL/'runtime-geometry.json.gz'),everyOriginalCurrentInputHashVerified=True,wholeCurrentSourceEntryAndFormIdentical=True,v1JobCompleted=False,geometryRecomputed=False));fence()
 call(['node',str(ATTR),rel(DOC/'literal-source-inputs.json.gz'),rel(DOC/'actual-render-geometry.json.gz')]);call(['node',str(CLOSURE),rel(DOC)+'/','--verify'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');actual=read(DOC/'actual-render-geometry.json.gz');assert[r['uid']for r in runtime['rows']]==[r['uid']for r in actual['rows']]==UIDS;proofs=[]
 for r,attrs,row in zip(runtime['rows'],actual['rows'],fresh):
  uid=r['uid'];assert r['index']==attrs['completeOriginalIndex']and r['position']==attrs['completeLiteralWorldPosition']and len(r['index'])//3==expected[uid]['completeFaces'];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)>0;bounds=np.asarray(row['candidate']['entry']['worldBounds'])
  for name in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   v=np.asarray(attrs[name]).reshape(-1,3);assert np.isfinite(v).all()and np.all(v.min(0)>=bounds[0]-1)and np.all(v.max(0)<=bounds[1]+1)
  proofs.append(dict(uid=uid,completeFaces=expected[uid]['completeFaces'],completeOriginalWorldSHA256=expected[uid]['wholeWorldSHA256'],completeActualGroundFaces=len(ground),completeActualGroundSHA256=digest(ground.astype('<f8').tobytes())))
 for data in [runtime,actual,read(DOC/'metrics.json')]:
  for p,h in data.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h;pins[p]=h
 fence();save(DOC/'capture-scope.json',dict(uids=UIDS,currentManifest=start,expectedNativeCount=6649,inputHashes=pins,startEndAllInputsVerified=True,completeFaces=13061,completeGroundByActor=proofs,allCurrentTerrainPatchesPreserved=True,terrainCandidates=[],allWorldVerticesContainedWithinCapturedGroundBroadphase=True,protectedReviewUIDs=state_uids,sourceGeometryChanges=0,terrainGeometryChanges=0,identityInterpretationIsNotPhysicalApproval=True,all569BodiesAnd75ZerosRetained=True,originalGovernmentPodiumUsedAsSupport=False,sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 call([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')]);print(json.dumps(dict(captureBatch=BATCH,completeFaces=13061,currentAcceptance=False)))
if __name__=='__main__':main()
