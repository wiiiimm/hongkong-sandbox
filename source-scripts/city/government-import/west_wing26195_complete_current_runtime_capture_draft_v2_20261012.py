"""UNEXECUTED existing installed West Wing source-only current capture; no acceptance."""
import argparse,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_ownership import document,graph_reasons
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/26195:0';SOURCE_SHA='50da67a3a009c3c832d2bfdbd08640c89d958ef8cf077d1c172e7059900f8af9';MODEL='B351161568102063C1';CSUID='3511615681P20110704';FACES=46918
MANIFEST_SHA='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540';PLAN=B/'government-xl-west-wing26195-current-capture-proposal-v2-20261012/method.json'
ATTR=HERE/'west_wing26195_complete_actual_render_attributes_draft_v2_20261012.mjs';CLOSURE=HERE/'west_wing26195_capture_module_closures_draft_v2_20261012.mjs';FREEZER=HERE/'west_wing26195_freeze_complete_current_runtime_capture_draft_v2_20261012.py'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def state(uids):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(uids,)).fetchall()
def preflight():
 plan=read(PLAN);assert plan['expectedManifestSHA256']==MANIFEST_SHA and plan['nativeCount']==6649
 for e in plan['executablePins']+plan['sourceProvenanceRefs']+plan['productionModulePins']:assert ref(ROOT/e['path'])==e,e['path']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==MANIFEST_SHA;m=read(manifest);cats=[ROOT/'3d-viewer'/url for url in m['officialModelCatalogues']];installed={}
 for cat in cats:
  for e in read(cat)['models']:assert e['uid']not in installed;installed[e['uid']]=(cat,e)
 assert len(installed)==6649;cat,entry=installed[UID];actor_catalogue=cat;asset=cat.parent/entry['asset'];assert ref(asset)['sha256']==SOURCE_SHA and(entry['modelId'],entry['buildingCSUID'],entry['triangles'])==(MODEL,CSUID,FACES)
 assert not entry.get('variantId')and entry.get('verticalPlacementOffsetHKPD',0)==0 and entry.get('rootTranslation',[-834500,0,816500])==[-834500,0,816500]
 lo,hi=entry['worldBounds'];window=[lo[0]-30,lo[2]-30,hi[0]+30,hi[2]+30];forms={};tiles={}
 for tile in m['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for f in read(path)['buildings']:
   rings=f.get('rings',[]);v=np.asarray([p for ring in rings for p in ring],float)
   hit=f['uid']==UID or(len(v)>0 and v[:,0].max()>=window[0]and v[:,0].min()<=window[2]and v[:,1].max()>=window[1]and v[:,1].min()<=window[3])
   if hit:assert f['uid']not in forms;forms[f['uid']]=(f,tile['url']);tiles[tile['url']]=ref(path)
 assert UID in forms and forms[UID][0]['buildingCSUID']==CSUID
 nominees=[]
 for u,(cat,e)in installed.items():
  l,h=e['worldBounds']
  if u!=UID and h[0]>=window[0]and l[0]<=window[2]and h[2]>=window[1]and l[2]<=window[3]:nominees.append((cat,e))
 dependencies={x if isinstance(x,str)else x['uid']for _,e in [(cat,entry)]+nominees for x in e.get('supportDependencies',[])}
 required={e['uid']for _,e in nominees}|dependencies|{UID}
 for tile in m['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for f in read(path)['buildings']:
   if f['uid']in required and f['uid']not in forms:forms[f['uid']]=(f,tile['url']);tiles[tile['url']]=ref(path)
 assert required<=set(forms);assert ref(manifest)['sha256']==MANIFEST_SHA
 return dict(plan=plan,manifest=ref(manifest),current=m,catalogues=cats,installed=installed,entry=entry,catalogue=actor_catalogue,asset=asset,forms=forms,tiles=tiles,nominees=nominees,dependencies=sorted(dependencies),window=window,resources=['building:'+u for u in sorted(forms)])
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');a=parser.parse_args();p=preflight()
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('westwing-current-capture-'+str(uuid.uuid4()),p['resources'],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();uids=sorted(p['forms']);before=state(uids);pins={}
 def pin(path):e=ref(path);assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_closure');code=set();walker.local_imports(Path(__file__),code);walker.local_imports(FREEZER,code)
 for path in list(code)+[PLAN,ATTR,CLOSURE,HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'acceptance-metrics.mjs',ROOT/'3d-viewer/city/data/manifest.json',ROOT/'3d-viewer/city/data/terrain.json',p['asset']]+p['catalogues']+[ROOT/'3d-viewer'/x['url']for x in p['current']['terrainPatches']]+[ROOT/e['path']for e in p['plan']['sourceProvenanceRefs']+p['plan']['productionModulePins']]:pin(path)
 for e in p['tiles'].values():pin(ROOT/e['path'])
 raw=p['asset'].read_bytes();tri=decode_original_world_triangles(raw);assert tri.shape==(FACES,3,3)and np.isfinite(tri).all();world_sha=digest(tri.astype('<f8').tobytes());g=document(raw);assert not graph_reasons(g,MODEL,FACES)
 raw_entry=p['entry'];catalogue_context=read(p['catalogue']);assert catalogue_context['rootTranslation']==[-834500,0,816500]
 # Same three inherited fields supplied by unchanged prepareModelCatalogue; preserve raw entry separately.
 entry={**raw_entry,'rootTranslation':catalogue_context['rootTranslation'],'coordinatePolicy':catalogue_context.get('coordinatePolicy'),'datasetId':catalogue_context.get('datasetId')};bounds=np.asarray(entry['worldBounds']);assert np.all(tri.min((0,1))>=bounds[0]-1)and np.all(tri.max((0,1))<=bounds[1]+1)
 dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);pin(dest);assert ref(dest)['sha256']==SOURCE_SHA
 f,tile=p['forms'][UID];row=dict(uid=UID,modelId=MODEL,sourceSHA256=SOURCE_SHA,candidate=dict(entry=entry,path=str(dest.relative_to(ROOT))),source=dict(building=f,tile=tile),rawInstalledEntry=raw_entry,actualCatalogue=ref(p['catalogue']),cataloguePreparationContextOnly=True);literal=dict(uid=UID,path=row['candidate']['path'],entry=raw_entry,building=f,role='owned-original');native=[]
 for cat,e in p['nominees']:
  asset=cat.parent/e['asset'];pin(asset);assert ref(asset)['sha256']==e['sha256'];bf,bt=p['forms'][e['uid']];native.append(dict(uid=e['uid'],path=str(asset.relative_to(ROOT)),entry=e,building=bf,role='installed-native-context',catalogue=ref(cat),tile=bt))
 basic=[dict(building=bf,tile=bt,tileSHA256=ref(ROOT/'3d-viewer'/bt)['sha256'])for u,(bf,bt)in p['forms'].items()if u not in p['installed']]
 save(DOC/'protected-state-before.json',dict(uids=uids,rows=before));save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=MANIFEST_SHA));save(DOC/'terrain-candidates.json',[]);save(DOC/'original-full-source-root-context.json.gz',dict(uid=UID,completeOriginalGLTFDocument=g,completeOriginalBinary64WorldTriangles=tri.tolist(),completeOriginalWorldSHA256=world_sha,sourceGeometryChanges=0));save(DOC/'literal-source-inputs.json.gz',dict(rows=[literal],nativeContextRows=native,basicContextRows=basic,completeCurrentForms=[v[0]for v in p['forms'].values()],currentManifest=p['manifest'],expectedNativeCount=6649,currentCatalogueRefs=[ref(x)for x in p['catalogues']],evidenceRefs=[ref(DOC/'selection.json.gz'),ref(p['asset'])]));save(DOC/'native-nomination-inventory.json',dict(nominees=native,catalogueBoundsNominationOnly=True,full6649ActualPositionCensus=False,scopeWindow=p['window'],dependencies=p['dependencies'],allAffectedForms=uids))
 def fence():
  for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
  assert json.loads(json.dumps(state(uids),default=str))==json.loads(json.dumps(before,default=str))and reservations.owns(lease)
 def call(args):fence();assert reservations.heartbeat(lease)['ok'];subprocess.run(args,cwd=ROOT,check=True);fence()
 rel=lambda path:str(path.relative_to(ROOT));call(['node',str(CLOSURE),rel(DOC)+'/']);call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')]);assert len(read(LOCAL/'runtime-geometry.json.gz')['rows'])==1 and not any(x.get('error')for x in read(DOC/'metrics.json')['rows']);call(['node',str(ATTR),rel(DOC/'literal-source-inputs.json.gz'),rel(DOC/'actual-render-geometry.json.gz')]);call(['node',str(CLOSURE),rel(DOC)+'/','--verify'])
 rt=read(LOCAL/'runtime-geometry.json.gz')['rows'];actual=read(DOC/'actual-render-geometry.json.gz');assert len(rt)==len(actual['rows'])==1;t=rt[0];a=actual['rows'][0];assert t['uid']==a['uid']==UID and t['index']==a['completeOriginalIndex']and t['position']==a['completeLiteralWorldPosition']and len(t['index'])//3==FACES
 ground=np.asarray(t['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)>0 and np.isfinite(ground).all()
 for name in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
  v=np.asarray(a[name]).reshape(-1,3);assert np.isfinite(v).all()and np.all(v.min(0)>=bounds[0]-1)and np.all(v.max(0)<=bounds[1]+1)
 for data in [read(LOCAL/'runtime-geometry.json.gz'),actual,read(DOC/'metrics.json')]:
  for path,h in data.get('inputHashes',{}).items():assert digest((ROOT/path).read_bytes())==h;pins[path]=h
 fence();save(DOC/'capture-scope.json',dict(uid=UID,currentManifest=p['manifest'],nativeCount=6649,inputHashes=pins,startEndAllInputsVerified=True,completeFaces=FACES,completeOriginalWorldSHA256=world_sha,completeActualGroundFaces=len(ground),completeActualGroundSHA256=digest(ground.astype('<f8').tobytes()),protectedReviewUIDs=uids,canonicalReservationResources=p['resources'],allCurrentTerrainPatchesPreserved=True,terrainCandidates=[],existingInstalledEntryPreserved=True,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceOnly=True,physicalAccepted=False,installationApproved=False,sourceBodyCensusDeferred=True));call([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')])
if __name__=='__main__':main()
