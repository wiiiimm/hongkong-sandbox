"""Complete pair physical diagnosis on literal unchanged current Elements terrain.

No terrain candidate, source edits, grouping, native reapproval or installation.
Complete ordinary identity, source memberships, foundations, basic/native and
runtime checks remain raw. Retained native availability supplies no root credit.
"""
from pathlib import Path
import importlib.util,json,os,subprocess,sys,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
from terrain_diagnostic_resolution import resolve_global_bottom_warning
BASE=ROOT/'docs/astra-city/government-import'
PROBE=BASE/'government-xl-terrain-recovery-elements-sun-star-two-original-current-probe-v1-20261011'
BATCH='government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/204145:0','landsd/204143:0'];COUNTS=[12129,11680];NATIVES=['landsd/273061:0','landsd/204144:0'];MANIFEST='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 assert not DOC.exists()and not LOCAL.exists();receipt=read(PROBE/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selection=PROBE/'selection.json.gz';assert ref(selection)in receipt['evidenceRefs'];rows=read(selection)['rows'];assert [r['uid']for r in rows]==UIDS
 worlds=[];bounds_list=[];refs=[ref(p)for p in [Path(__file__),selection,PROBE/'result.json',PROBE/'metrics.json']]
 for row,count in zip(rows,COUNTS):
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==row['candidate']['entry']['sha256'];tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']==row['native']['model']['triangles']==count
  proof=packed_world_bounds(raw);lo,hi=proof['originalWholeSourceBounds'];bounds_list.append([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);worlds.append(tri);refs.append(ref(asset))
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 bounds=[min(b[0]for b in bounds_list),min(b[1]for b in bounds_list),max(b[2]for b in bounds_list),max(b[3]for b in bounds_list)];final=module('elements_current_forms','xl-final-script-pass.py');forms=final.load_forms(bounds)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST;current=read(manifest);installed={};catrefs=[]
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catrefs.append(ref(path))
  for entry in read(path)['models']:assert entry['uid']not in installed;installed[entry['uid']]=(path,entry)
 assert not(set(UIDS)&set(installed))and set(NATIVES)<=set(installed);assert not any(e['sha256']==r['sourceSHA256']for _,e in installed.values()for r in rows)
 required=set(NATIVES)|{f['uid']for f,_,_ in forms if f['uid']in installed};pending=list(required)
 while pending:
  for dependency in installed[pending.pop()][1].get('supportDependencies',[]):
   support=installed.get(dependency['uid']);assert dependency['state']=='installed'and support and support[1]['buildingCSUID']==dependency['csuid']
   if dependency.get('sha256'):assert dependency['sha256']==support[1]['sha256']
   if dependency['uid']not in required:required.add(dependency['uid']);pending.append(dependency['uid'])
 native_forms={};tile_refs=[]
 for tile in current['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];tile_ref=ref(path);tile_refs.append(tile_ref)
  for building in read(path)['buildings']:
   if building['uid']in required:
    assert building['uid']not in native_forms,'Native form must be unique across current tiles';assert building['buildingCSUID']==installed[building['uid']][1]['buildingCSUID']
    native_forms[building['uid']]=dict(building=building,tile=tile['url'],tileSHA256=tile_ref['sha256'])
 assert set(native_forms)==required
 for f,_,_ in forms:
  if f['uid']in native_forms:assert native_forms[f['uid']]['building']==f
 refs.extend([start,*catrefs,*tile_refs]);assert ref(manifest)==start and all(ref(ROOT/r['path'])==r for r in refs)
 keys=['building:'+u for u in sorted({f['uid']for f,_,_ in forms}|set(UIDS)|required)];claimed=reservations.claim('elements-current-pair-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claimed['ok'];lease=claimed['reservation']
 try:
  assert ref(manifest)==start and all(ref(ROOT/r['path'])==r for r in refs)
  DOC.mkdir(parents=True);save(DOC/'native-source-form-preflight.json',dict(forcedNativeUids=NATIVES,requiredNativeUids=sorted(required),sourceForms=native_forms,currentManifest=start,catalogueRefs=catrefs,currentTileRefs=tile_refs,publication=False,nativeReacceptance=False));refs.append(ref(DOC/'native-source-form-preflight.json'))
  (DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append(ref(DOC/'historical-current-manifest.json'));contexts=[];identities=[];newrows=[];entries=[]
  for row,tri in zip(rows,worlds):
   uid=row['uid'];form,_,tile=next(f for f in forms if f[0]['uid']==uid);assert form['buildingCSUID']==row['source']['building']['buildingCSUID']and form['objectId']==row['source']['building']['objectId'];entry=row['candidate']['entry'];assert not entry.get('suppressesBuildingUids')and not entry.get('footprintScope')
   destination=LOCAL/entry['asset'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes((ROOT/row['candidate']['path']).read_bytes());refs.append(ref(destination));row={**row,'source':dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes())),'candidate':{**row['candidate'],'path':str(destination.relative_to(ROOT))}};newrows.append(row);entries.append(entry)
   context=dict(uid=uid,sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms});contexts.append(context);identities.append(verify_files(row,context,LOCAL/('identity-current-'+uid.split('/')[1].replace(':','-'))))
  save(DOC/'selection.json.gz',dict(rows=newrows,batch=BATCH,manifestSHA256=MANIFEST));save(DOC/'context.json.gz',dict(rows=contexts));save(DOC/'identity-proofs.json',dict(rows=identities));refs.extend(ref(p)for p in [DOC/'selection.json.gz',DOC/'context.json.gz',DOC/'identity-proofs.json'])
  freeze=module('elements_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py')
  if not all(i['passed']for i in identities):
   freeze.freeze(BATCH,'elements-fresh-ordinary-identity-held-before-physical-v1',[ROOT/r['path']for r in refs],dict(uids=UIDS,rawOrdinaryIdentities=identities,scriptChecksPassed=False,reasons=['fresh-ordinary-identity'],publication=False,newlyInstalled=0));return
  save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=2),area='Two complete original Elements towers unchanged current terrain'))
  save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source']for r in newrows});save(DOC/'terrain-candidates.json',[]);save(DOC/'terrain.json',dict(patches=[],qualification='Literal unchanged current terrain; no proposal/replacement.',modelGeometryChanges=0))
  routing=[]
  for p in current['terrainPatches']:
   actual=ROOT/'3d-viewer'/p['url'];data=read(actual);allbounds=[b for b in [p.get('bounds'),data.get('bounds')]if b]
   if not allbounds:allbounds=[module('elements_patch_bounds','native_patch_resolution.py')._patch_bounds(data)]
   routing.append(dict(entry=p,asset=ref(actual),testedBounds=allbounds));refs.append(ref(actual))
  parent=ROOT/'3d-viewer/city/data/terrain.json';refs.append(ref(parent));save(DOC/'current-source-terrain-preflight.json',dict(currentManifest=start,rootTerrain=ref(parent),completeCurrentTerrainRouting=routing,completeOwnedOriginalPOSITIONProofs=[packed_world_bounds((ROOT/r['candidate']['path']).read_bytes())for r in newrows],completeOwnedSourceProviderBindings=[source_stream_binding((ROOT/r['candidate']['path']).read_bytes())for r in newrows],completeRetainedNativeEntries=[dict(uid=u,catalogue=ref(installed[u][0]),entry=installed[u][1],source=ref(installed[u][0].parent/installed[u][1]['asset']))for u in NATIVES],terrainProposalChanged=False,publication=False))
  save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[],existingNative=f['uid']in installed or bool(f.get('modelGeometry')))for f,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms},candidateIds=UIDS,patches=[]))
  rel=lambda p:str(p.relative_to(ROOT))
  def call(cmd,allowed=(0,)):
   assert subprocess.run(cmd,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode in allowed;assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);assert ref(manifest)==start and all(ref(ROOT/r['path'])==r for r in refs)
  closures=[]
  for filename in ['acceptance-metrics-multi-retained.mjs','xl-terrain-recovery-20261011-elements-sun-star-check-current-native-v1.mjs']:
   snapshot=DOC/(filename+'.module-closure.json');js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure}from'./source-scripts/city/government-import/literal_production_module_dependency_closure_20261010.mjs';const root=new URL('./',import.meta.url);writeFileSync(process.argv[1],JSON.stringify(snapshotModuleClosure(new URL(process.argv[2],root),root)));";call(['node','--input-type=module','-e',js,str(snapshot),'source-scripts/city/government-import/'+filename]);closure=read(snapshot);assert closure['completeAuditedLiteralImportClosure']and closure['unsupportedDynamicImports']==0;closures.append(closure);refs.append(ref(snapshot));refs.extend(ref(ROOT/p)for p in closure['inputHashes'])
  call(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
  call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1));call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'xl-terrain-recovery-20261011-elements-sun-star-check-current-native-v1.mjs'),rel(DOC)+'/'])
  runtime=read(LOCAL/'runtime-geometry.json.gz');assert [r['uid']for r in runtime['rows']]==UIDS;metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');assert [r['uid']for r in metrics['rows']]==[r['uid']for r in validation['results']]==UIDS;foundations=[];resolutions=[];policy=module('elements_policy','acceptance-policy.py');reasons=[]
  if validation['loaderAccepted']!=2 or validation['checksPassed']!=2 or validation['exceptions']:reasons.append('complete-current-loader-validation')
  for row,tri,g,m,identity,v in zip(newrows,worlds,runtime['rows'],metrics['rows'],identities,validation['results']):
   uid=row['uid'];assert g['uid']==m['uid']==uid;drawn=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert drawn.shape==tri.shape and np.max(np.abs(drawn-tri))<=1e-9
   form=row['source']['building'];f=final.foundation_context(drawn,ground,Polygon(form['rings'][0],form['rings'][1:]));foundation=dict(uid=uid,sourceSHA256=row['sourceSHA256'],foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0);foundations.append(foundation);resolution=resolve_global_bottom_warning(v,m,foundation);resolutions.append(dict(uid=uid,rawValidation=v,resolution=resolution))
   reasons.extend(uid+':'+r for r in policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=identity['proof']),m,metrics['profiles']['mobile']));reasons.extend(uid+':'+r for r in resolution['remaining'])
   if not foundation['strictFoundationAccepted']:reasons.append(uid+':whole-source-foundation')
  save(DOC/'foundation.json',dict(rows=foundations,modelGeometryChanges=0));save(DOC/'diagnostic-resolutions.json',dict(rows=resolutions))
  for r in read(DOC/'neighbour-checks.json')['rows']:reasons.extend('neighbour:'+r['uid']+':'+reason for reason in r['reasons'])
  native=read(DOC/'native-neighbour-checks.json');reasons.extend('native:'+u for u in set(native['blocked'])-set(native['resolved']))
  refs.extend(ref(ROOT/p)for p in runtime['inputHashes']);refs.extend(ref(ROOT/p)for p in native['inputHashes']);refs.extend(ref(p)for p in [LOCAL/'runtime-geometry.json.gz',LOCAL/'catalogue.json']);refs.extend(ref(HERE/n)for n in ['xl-final-script-pass.py','acceptance-policy.py','terrain_diagnostic_resolution.py','exact_original_georef_cell_identity_20261009.py','exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py','xl_source_stream_binding_20261009.py','literal_production_module_dependency_closure_20261010.mjs','check-neighbours.mjs','xl-popcorn-source-investigations-checkpoints-20261009.py'])
  assert reservations.heartbeat(lease)['ok']and reservations.owns(lease)and ref(manifest)==start;assert all(ref(ROOT/r['path'])==r for r in refs)
  freeze.freeze(BATCH,'complete-elements-two-original-current-unchanged-terrain-physical-v1',[ROOT/r['path']for r in {r['path']:r for r in refs}.values()],dict(uids=UIDS,completeOriginalFaces=23809,currentNeighbourForms=len(forms),retainedNativeUids=NATIVES,reasons=sorted(set(reasons)),scriptChecksPassed=not reasons,terrainProposalChanged=False,nativeReacceptance=False,publication=False,newlyInstalled=0));print(dict(reasons=sorted(set(reasons)),currentNeighbourForms=len(forms)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
