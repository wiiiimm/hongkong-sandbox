"""UNEXECUTED three complete Upton originals/current ground+attribute capture.
All geometry unchanged; no source-specific identity can discharge physical gates.
"""
import argparse,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from original_source_ownership import document,graph_reasons
from upton_exact_actual_history_archive_bindings_draft_v1_20261011 import load_contract,exact_ref
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/338946:0','landsd/12728:0','landsd/12662:0'];PROTECTED='landsd/254809:0'
MANIFEST_SHA='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
PLAN=B/'government-xl-upton-post-integration-literal-dynamic-capture-proposal-v1-20261012/method.json'
INPUTS=[B/'government-xl-upton338946-podium12728-fresh-identity-proposal-v1-20261011/source-inputs.json',B/'government-xl-upton-podium12728-12662-original-foreign-conflict-proposal-v1-20261011/source-inputs.json']
ATTR=HERE/'upton_three_original_complete_actual_render_attributes_draft_v4_20261012.mjs';CLOSURE=HERE/'upton_three_original_capture_module_closures_draft_v4_20261012.mjs';FREEZER=HERE/'upton_three_original_freeze_complete_current_runtime_capture_draft_v4_20261012.py'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def state(uids):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(uids,)).fetchall()
def native(sources):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');rows=c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND m->>'modelId'=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,[r['modelId']for r in sources])).fetchall()
 assert len(rows)==3
 for r in sources:assert next(x for x in rows if x[1]['modelId']==r['modelId'])==(r['native']['cacheKey'],r['native']['model'],r['native']['sheet'],r['native']['resultSha'])
 return rows
def verified_source_certificate(path,expected_sha):
 certificate=read(path);assert ref(path)['sha256']==expected_sha
 required=dict(reviewer='ROOT',independentlyVerified=True,sourceIdentificationOnly=True,identityAccepted=True,currentManifestSHA256=MANIFEST_SHA,currentNativeCount=6649,physicalAccepted=False,installationApproved=False,canStartTerrainWork=False,all23ProperOriginalCrossingsPreserved=True)
 for key,value in required.items():assert key in certificate and type(certificate[key])is type(value) and certificate[key]==value, 'ROOT source certificate contract: '+key
 history_ref=read(PLAN)['integrationHistoryContract'];history=load_contract(ROOT,history_ref['path'],history_ref['sha256'])
 # Reverify every literal actual-file binding with exact existing historical bytes.
 # Original refs remain untouched; changed live modules cannot satisfy old hashes.
 for binding in certificate['bindings']:exact_ref(ROOT,binding['actualVerifiedFile'],history)
 source_id=B/'government-xl-upton12728-12662-current-source-identification-rebind-v1-20261011/source-identification-only.json'
 source_ref=ref(source_id);assert any(b['originalEvidenceRef']==source_ref and b['actualVerifiedFile']==source_ref for b in certificate['bindings']), 'Actual current source identity missing from ROOT literal closure'
 identified=read(source_id);assert identified['identityAccepted']is True and identified['physicalAccepted']is False and identified['installationApproved']is False
 assert len(identified['identityContext']['complete23ProperInteriorCrossingsRetained'])==23
 return ref(path)
def verified_integration_history(expected_head):
 plan=read(PLAN);assert expected_head==plan['expectedIntegratedCommit'];contract_ref=plan['integrationHistoryContract'];contract_path=ROOT/contract_ref['path'];assert ref(contract_path)==contract_ref
 contract=read(contract_path);assert contract['actualHistoricalBytesOnly']is True and len(contract['historicalArchives'])==12
 for item in contract['historicalArchives']:
  actual=item['actualArchive'];assert actual['sha256']==item['historicalSHA256'] and ref(ROOT/actual['path'])==actual
 assert ref(ROOT/contract['integrationInventory']['path'])==contract['integrationInventory']
 for item in plan['expectedIntegratedProductionFiles']:assert ref(ROOT/item['path'])==item
 assert len(expected_head)==40 and all(c in '0123456789abcdef'for c in expected_head)
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==expected_head
 subprocess.run(['git','merge-base','--is-ancestor',plan['requiredIntegrationAncestor'],expected_head],cwd=ROOT,check=True)
 subprocess.run(['git','merge-base','--is-ancestor','436910642649c723158f43d8bf0ba940c2be7924',expected_head],cwd=ROOT,check=True)
 return contract_ref

def verified_plan():
 plan=read(PLAN);assert plan['expectedManifestSHA256']==MANIFEST_SHA and plan['expectedNativeCount']==6649
 for item in plan['draftExecutablePins']+[plan[k]for k in ['dependencyHelper','dependencyTests','parserProvenance','preservedFailedV3Audit']]:assert ref(ROOT/item['path'])==item
 provenance=read(ROOT/plan['parserProvenance']['path'])
 for item in [provenance['parser'],provenance['copyright']]:assert ref(ROOT/item['path'])==item
 assert plan['sourceAcquisitionSelections']==[ref(p)for p in INPUTS], 'Plan exact acquisition selection path/SHA contract changed'
 return plan
def main():
 p=argparse.ArgumentParser();p.add_argument('--root-source-certificate',required=True);p.add_argument('--expected-root-certificate-sha',required=True);p.add_argument('--expected-integrated-head',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();history_ref=verified_integration_history(a.expected_integrated_head);cert=ROOT/a.root_source_certificate;verified_source_certificate(cert,a.expected_root_certificate_sha);verified_plan()
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('upton-three-original-runtime-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));code=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned','--root-source-certificate',a.root_source_certificate,'--expected-root-certificate-sha',a.expected_root_certificate_sha,'--expected-integrated-head',a.expected_integrated_head],cwd=ROOT).returncode;assert code==0,code;return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();plan=verified_plan()
 source_map={}
 for f in INPUTS:
  for row in read(f)['sources']:
   if row['uid']in source_map:assert source_map[row['uid']]['sourceSHA256']==row['sourceSHA256'] and source_map[row['uid']]['native']==row['native']
   source_map[row['uid']]=row
 assert set(source_map)==set(UIDS);sources=[source_map[u]for u in UIDS];expected={r['uid']:r for r in plan['actors']};tri={};roots=[];pins={}
 def pin(p):
  e=ref(p);assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST_SHA;current=read(manifest);catalogues=[ROOT/'3d-viewer'/x for x in current['officialModelCatalogues']];terrain=[ROOT/'3d-viewer'/x['url']for x in current['terrainPatches']]
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','reviewed_current_source_closure');code=set();walker.local_imports(Path(__file__),code);walker.local_imports(FREEZER,code)
 for p in list(code)+INPUTS+[ROOT/history_ref['path'],PLAN,cert,B/'government-xl-upton12728-12662-current-source-identification-rebind-v1-20261011/source-identification-only.json',ATTR,CLOSURE,HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'acceptance-metrics.mjs',HERE/'xl-final-script-pass.py',manifest,ROOT/'3d-viewer/city/data/terrain.json']+catalogues+terrain:pin(p)
 installed={}
 for cat in catalogues:
  for e in read(cat)['models']:assert e['uid']not in installed;installed[e['uid']]=(cat,e)
 assert len(installed)==6649 and not set(UIDS)&set(installed)
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
 basic=[dict(building=f,tile=t,tileSHA256=ref(ROOT/'3d-viewer'/t)['sha256'])for f,_,t in forms if f['uid']not in installed and f['uid']not in UIDS]
 save(DOC/'protected-state-before.json',dict(uids=state_uids,rows=before));save(DOC/'native-source-state-before.json',dict(rows=native_before));save(DOC/'selection.json.gz',dict(rows=fresh,manifestSHA256=MANIFEST_SHA));save(DOC/'terrain-candidates.json',[]);save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='diagnostic-original-support-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[r['candidate']['entry']for r in fresh]));save(DOC/'original-full-source-root-context.json.gz',dict(rows=roots,sourceGeometryChanges=0));save(DOC/'complete-current-forms.json.gz',dict(rows=[dict(building=f,tile=t,installedNative=f['uid']in installed)for f,_,t in forms]));save(DOC/'literal-source-inputs.json.gz',dict(rows=literal,nativeContextRows=native_context,basicContextRows=basic,completeCurrentForms=[f for f,_,_ in forms],currentManifest=start,expectedNativeCount=6649,currentCatalogueRefs=[ref(p)for p in catalogues],evidenceRefs=[ref(DOC/'selection.json.gz')]+[ref(ROOT/x['path'])for x in literal]));save(DOC/'native-nomination-inventory.json',dict(currentCatalogueCount=6649,scopeWindow=window,nominees=native_context,catalogueBoundsNominationOnly=True,notFull6649ActualPositionCensus=True,noNativeReapproval=True,protected254809Form=form_map[PROTECTED][0]))
 def fence():
  verified_integration_history(a.expected_integrated_head)
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  assert state(state_uids)==before and native(sources)==native_before and reservations.owns(lease)
 def call(args):fence();assert reservations.heartbeat(lease)['ok'];subprocess.run(args,cwd=ROOT,check=True);fence()
 rel=lambda p:str(p.relative_to(ROOT));call(['node',str(CLOSURE),rel(DOC)+'/']);call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')]);call(['node',str(ATTR),rel(DOC/'literal-source-inputs.json.gz'),rel(DOC/'actual-render-geometry.json.gz')]);call(['node',str(CLOSURE),rel(DOC)+'/','--verify'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');actual=read(DOC/'actual-render-geometry.json.gz');assert[r['uid']for r in runtime['rows']]==[r['uid']for r in actual['rows']]==UIDS;proofs=[]
 for r,attrs,row in zip(runtime['rows'],actual['rows'],fresh):
  uid=r['uid'];assert r['index']==attrs['completeOriginalIndex']and r['position']==attrs['completeLiteralWorldPosition']and len(r['index'])//3==expected[uid]['completeFaces'];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)>0;bounds=np.asarray(row['candidate']['entry']['worldBounds'])
  for name in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   v=np.asarray(attrs[name]).reshape(-1,3);assert np.isfinite(v).all()and np.all(v.min(0)>=bounds[0]-1)and np.all(v.max(0)<=bounds[1]+1)
  proofs.append(dict(uid=uid,completeFaces=expected[uid]['completeFaces'],completeOriginalWorldSHA256=expected[uid]['wholeWorldSHA256'],completeActualGroundFaces=len(ground),completeActualGroundSHA256=digest(ground.astype('<f8').tobytes())))
 for data in [runtime,actual,read(DOC/'metrics.json')]:
  for p,h in data.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h;pins[p]=h
 fence();save(DOC/'capture-scope.json',dict(uids=UIDS,currentManifest=start,expectedNativeCount=6649,inputHashes=pins,startEndAllInputsVerified=True,completeFaces=13704,completeGroundByActor=proofs,allCurrentTerrainPatchesPreserved=True,terrainCandidates=[],allWorldVerticesContainedWithinCapturedGroundBroadphase=True,protectedReviewUIDs=state_uids,sourceGeometryChanges=0,terrainGeometryChanges=0,identityInterpretationIsNotPhysicalApproval=True,preservedOriginalProperCrossings=23,rootSourceCertificate=ref(cert),historicalSourceCertificateOnly=True,integrationHistoryContract=history_ref,expectedIntegratedHead=a.expected_integrated_head,sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 call([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')]);print(json.dumps(dict(captureBatch=BATCH,completeFaces=13704,currentAcceptance=False)))
if __name__=='__main__':main()
