"""UNEXECUTED Sports source/current-ground capture; no support or placement credit."""
import copy,importlib.util,json,subprocess,sys,types,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';DRAFT=BASE/'government-xl-polyu-sports305582-current-four-world-ground-draft-v1-20261013'
CONTRACT=DRAFT/'input-contract.json';METHOD=DRAFT/'METHOD.md';SCHEMA=DRAFT/'actual-readonly-preparation-v1/closure-schema.json'
BATCH='government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JS=HERE/'xl-polyu-sports305582-current-four-world-ground-geometry-draft-v1-20261013.mjs';UID='landsd/305582:0';PODIUM='landsd/305793:0';BASIC=['landsd/72322:0','landsd/258852:0'];LEE='landsd/305600:0'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';SOURCE='ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15';FACES=10536
NAM=BASE/'government-xl-complete-native-actual-position-post-nam-delta-v1-20261013'
HELPERS=['run.py','exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py','xl-final-script-pass.py','xl-popcorn-source-investigations-checkpoints-20261009.py','exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','actual_float32_model_matrix_bounds_20261011.mjs','current_geometry_capture_preflight_20261011.mjs','dependency-closure-vendor/acorn-8.8.1/acorn.mjs','dependency-closure-vendor/acorn-8.8.1/PROVENANCE.json','dependency-closure-vendor/acorn-8.8.1/COPYRIGHT']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def imported_local_files(*extras):
 queue=list(sys.modules.values())+list(extras);seen=set();files=set()
 while queue:
  m=queue.pop()
  if not isinstance(m,types.ModuleType)or id(m)in seen:continue
  seen.add(id(m));name=getattr(m,'__file__',None)
  if not name:continue
  p=Path(name).resolve()
  if ROOT not in p.parents or not p.is_file():continue
  files.add(p);queue.extend(v for v in vars(m).values()if isinstance(v,types.ModuleType))
 return sorted(files)
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def preflight(require_schema=True):
 assert not DOC.exists()and not(LOCAL/'private-terrain.json').exists()
 before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert digest(before)==CURRENT
 for pin in read(DRAFT/'review-file-pins.json')['filePins']:assert ref(ROOT/pin['path'])==pin
 c=read(CONTRACT);assert c['schema']=='polyu-sports305582-current-four-world-ground-input-v1'and c['currentManifestSHA256']==CURRENT and c['currentNativeActors']==6650
 assert c['uid']==UID and c['sourceSHA256']==SOURCE and c['completeSourceFaces']==FACES and c['currentAcceptance']is False and c['physicalAccepted']is False
 refs=[Path(__file__),JS,CONTRACT,METHOD,DRAFT/'review-file-pins.json']+[HERE/n for n in HELPERS]+[HERE.parent/'shared-modelling'/n for n in ['db.py','jobs.py','reservations.py']]
 for pin in c['historicalPins']:assert ref(ROOT/pin['path'])==pin;refs.append(ROOT/pin['path'])
 row=copy.deepcopy(c['originalSourceRow']);selection=read(ROOT/c['originalSelection']['path']);assert [q for q in selection['rows']if q['uid']==UID]==[row]
 assert row['sourceSHA256']==SOURCE and row['candidate']['entry']['sha256']==SOURCE and row['candidate']['entry']['triangles']==row['native']['model']['triangles']==FACES
 assert row['candidate']['entry']['uid']==UID and row['candidate']['entry']['buildingCSUID']==c['sourceBuildingCSUID']=='3659318508P20181231'and row['modelId']==c['sourceModelId']=='B365931850802063C0'
 assert row['candidate']['entry']['rootTranslation']==[-834500,0,816500];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==SOURCE
 proof=packed_world_bounds(raw);bounds=proof['originalWholeSourceBounds'];region=[bounds[0][0]-4,bounds[0][2]-4,bounds[1][0]+4,bounds[1][2]+4]
 topology=c['exactOriginalTopology'];assert topology['completeOriginalFaceIds']==list(range(FACES));assert len(topology['sharedEdgeConnectedComponents'])==21 and len(topology['exactNonrenderingOriginalFaces'])==4
 assert sorted(f for part in topology['sharedEdgeConnectedComponents']for f in part)==topology['completeRenderableFaceIds'];assert sorted(topology['completeRenderableFaceIds']+topology['exactNonrenderingOriginalFaces'])==list(range(FACES))
 review=read(BASE/'government-xl-polyu-sports305582-root-campus-identity-review-v1-20261013/root-campus-source-identity-review.json');assert review['sourceSHA256']==SOURCE and review['identityAccepted']is True and review['physicalAccepted']is False and review['supportAccepted']is False and review['nativePublicationHoldRetained']is True
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');entries={};paths={};catalogues=[]
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues.append(ref(p))
  for entry in read(p)['models']:assert entry['uid']not in entries;entries[entry['uid']]=entry;paths[entry['uid']]=p.parent/entry['asset']
 assert len(entries)==6650 and UID not in entries and entries[PODIUM]==c['installedPodiumEntry']and entries[PODIUM]['publicationApproved']is False
 assert ref(paths[PODIUM])==c['installedPodiumAsset']and LEE in entries[PODIUM]['suppressesBuildingUids']
 for u in BASIC:assert u not in entries and all(u not in e.get('suppressesBuildingUids',[])for e in entries.values())
 comp=read(NAM/'composition.json.gz');inp=read(NAM/'input.json.gz');binding=read(ROOT/comp['exactBaselineCurrentBinding']['path']);baseline=read(ROOT/comp['baselineInventory']['path'])
 assert comp['completeCurrentNativeActors']==6650 and comp['currentManifest']['sha256']==CURRENT
 a,=[q for q in baseline['rows']if q['uid']==PODIUM];z,=[q for q in binding['rows']if q['uid']==PODIUM]
 assert a==c['installedPodiumActualPositionRecord']and z==c['installedPodiumCurrentBinding'];assert a['wholeUnusedPositionVerticesIncluded']is True and a['sourceFacesOmitted']==0 and a['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']is True
 assert canonical(a)==z['unchangedActualBoundsSHA256']and canonical(entries[PODIUM])==z['currentRawEntrySHA256']and canonical(inp['currentAllNativeSourceForms'][PODIUM])==z['currentViewerFormSHA256']
 assert digest((ROOT/z['source']['path']).read_bytes())==z['source']['sha256']==a['sourceSHA256']
 for p,h in inp['requiredUnchangedProductionClosure'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 final=module('polyu_sports_fresh_forms','xl-final-script-pass.py');forms=final.load_forms(region);assert len(forms)==len({f['uid']for f,_,_ in forms});by={f['uid']:(f,t)for f,_,t in forms}
 for tile in manifest['tiles']:
  for f in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
   if f['uid']in c['requiredActorUIDs']:
    if f['uid']in by:assert by[f['uid']][0]==f
    else:by[f['uid']]=(f,tile['url'])
 assert all(u in by for u in c['requiredActorUIDs']);forms=[(f,None,t)for u,(f,t)in sorted(by.items())];assert by[PODIUM][0]==inp['currentAllNativeSourceForms'][PODIUM]
 row['historicalSourceFormVerbatim']=copy.deepcopy(row['source']);f,t=by[UID];assert f['buildingCSUID']==c['sourceBuildingCSUID']and f['objectId']==305582;row['source']=dict(building=f,tile=t,tileSHA256=digest((ROOT/'3d-viewer'/t).read_bytes()));row['triangles']=FACES
 tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms};refs.extend(ROOT/'3d-viewer'/t for t in tiles);refs.extend(ROOT/p['path']for p in catalogues)
 if require_schema:
  schema=read(SCHEMA);assert schema['schemaValidationPassed']is True and schema['noProductionModuleImported']is True
  for closure in [schema['completeRecursiveLoaderModuleClosure'],schema['completeRecursiveTerrainModuleClosure'],*schema['completeRecursiveCaptureHelperModuleClosures']]:
   assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'and closure['computedImportsRejected']is True and closure['unsupportedDynamicImports']==0 and closure['opaqueResourcesAreNotParsedModules']is True
   for p,h in closure['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  refs.append(SCHEMA)
 freezer=module('polyu_capture_freezer_preflight','xl-popcorn-source-investigations-checkpoints-20261009.py');refs.extend(imported_local_files(final,freezer));pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in sorted(set(refs))}
 resources=sorted(set([('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f,_,_ in forms]+['terrain-patch:'+UID]));assert len(resources)<=1000
 assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 return dict(before=before,contract=c,row=row,proof=proof,region=region,forms=forms,tiles=tiles,catalogues=catalogues,pins=pins,resources=resources,review=review)
def main():
 s=preflight('--source-schema-only'not in sys.argv)
 if '--preflight-only'in sys.argv or '--source-schema-only'in sys.argv:
  print(json.dumps(dict(noDB=True,noLease=True,noProductionModuleImported=True,currentManifestSHA256=CURRENT,currentNatives=6650,sourceFaces=FACES,sourceBodies=21,sourceZeroFaces=4,completeCurrentForms=len(s['forms']),canonicalResources=s['resources'],currentAcceptance=False)),flush=True);return
 assert not DOC.exists()
 if '--owned'not in sys.argv:
  assert not LOCAL.exists();q=reservations.claim('polyu-sports-current-ground-'+str(uuid.uuid4()),s['resources'],batch=BATCH,ttl=3600);assert q['ok'];save(LEASE,json.loads(json.dumps(q['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True);return
 lease=read(LEASE);assert lease['resources']==s['resources']and reservations.owns(lease)
 receipt=read(BASE/'government-xl-polyu-sports305582-root-campus-identity-review-v1-20261013/result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);n=s['row']['native'];assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,n['cacheKey'])).fetchall()==[(n['resultSha'],)]
 DOC.mkdir();(DOC/'captured-manifest.json').write_bytes(s['before']);save(DOC/'whole-original-position-proof-305582-0.json',s['proof'])
 save(DOC/'capture-inputs.json.gz',dict(rows=[s['row']],completeOriginalTopology=s['contract']['exactOriginalTopology'],completeCurrentForms=[f for f,_,_ in s['forms']],completeCurrentFormBounds=s['region'],neighbourTileHashes=s['tiles'],completeCurrentCatalogueRefs=s['catalogues'],installedPodiumDependency=dict(entry=s['contract']['installedPodiumEntry'],asset=s['contract']['installedPodiumAsset'],currentBinding=s['contract']['installedPodiumCurrentBinding'],actualPositionRecord=s['contract']['installedPodiumActualPositionRecord'],publicationHoldPreserved=True),inputHashes=s['pins'],manifestSHA256=CURRENT,validatedClosurePath=str(SCHEMA.relative_to(ROOT)),currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 q=subprocess.run(['node',str(JS),UID],cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-export-log.json',dict(exitCode=q.returncode,stdout=q.stdout,stderr=q.stderr));assert q.returncode==0,q.stderr
 cap=read(DOC/'complete-current-actual-source-and-ground-305582-0.json.gz');assert cap['uid']==UID and cap['sourceSHA256']==SOURCE and cap['entry']==s['row']['candidate']['entry']and cap['completeFaces']==FACES and cap['startAndEndInputsVerified']is True and cap['completeOriginalPOSITIONProof']==s['proof']
 original=decode_original_world_triangles((ROOT/s['row']['candidate']['path']).read_bytes());assert original.shape==(FACES,3,3)and digest(original.astype('<f8').tobytes())==s['contract']['originalWorldSHA256'];ix=np.asarray(cap['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);worlds={'providerOriginal':original}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(cap[key],dtype='<f8').reshape(-1,3)[ix]
 assert all(w.shape==(FACES,3,3)and np.isfinite(w).all()for w in worlds.values());ground=np.asarray(cap['currentDrawnGround']['completeRegionalPosition'],dtype='<f8').reshape(-1,3,3);assert len(ground)==cap['currentDrawnGround']['completeRegionalFaces']and digest(ground.tobytes())==cap['currentDrawnGround']['worldTriangleSHA256']and np.isfinite(ground).all()
 save(DOC/'complete-sports-four-stream-current-ground-inputs.json.gz',dict(uid=UID,sourceSHA256=SOURCE,completeOriginalTopologyVerbatim=s['contract']['exactOriginalTopology'],completeWorldStreams={m:dict(completeFaces=FACES,completeWorldTriangleSHA256=digest(w.astype('<f8').tobytes()),completeWorldTriangles=w.tolist())for m,w in worlds.items()},completeDrawnGround=ground.tolist(),completeDrawnGroundSHA256=digest(ground.tobytes()),allHistoricalContactsAndRootIdentityReviewRetained=s['review'],unrelated235076And114494SupportNotTransferred=True,currentAcceptance=False,physicalAccepted=False))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==s['before']
 for p,h in {**s['pins'],**cap['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p
 refs=[ROOT/p for p in set(s['pins'])|set(cap['inputHashes'])]+[p for p in DOC.rglob('*')if p.is_file()];freezer=module('polyu_sports_current_ground_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');out=freezer.freeze(BATCH,'sports305582-complete-current-four-world-ground-with-held-native-dependency',refs,dict(uids=[UID],completeSourceFaces=FACES,originalBodies=21,originalZeroFaces=4,currentNatives=6650,installedDependency=PODIUM,nativePublicationHoldPreserved=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0));print(json.dumps(dict(jobId=out['jobId'],sourceFaces=FACES,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
