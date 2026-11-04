"""Fresh full Parkview Block11 diagnosis using explicit authentic retained terrain proposal.

Candidate only, no publication flock or live asset edits. Complete current source,
identity, terrain routing, neighbours, native actors and runtime gates remain raw.
"""
import importlib.util,json,os,subprocess,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,reservations,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from terrain_diagnostic_resolution import resolve_global_bottom_warning
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'xl-terrain-recovery-20261011-parkview-block11-current-inputs-v1'
BATCH='government-xl-terrain-recovery-parkview-block11-authentic-retained-current-physical-v2-20261011'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PROPOSAL=BASE/'xl-terrain-recovery-20261011-parkview-authentic-foreign-preserved-terrain-proposal-v4'
UID='landsd/255647:0';SOURCE='c2a4c7342c9edfed5abdd1851fda88a9860d04e2b9b34236faf96e98e828b943'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);installed={};catalogue_start={url:ref(ROOT/'3d-viewer'/url)for url in current['officialModelCatalogues']}
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for m in read(path)['models']:assert m['uid'] not in installed;installed[m['uid']]=(path,m)
 assert UID not in installed
 original=[r for r in read(PRIOR/'check-selection.json.gz')['rows'] if r['uid']==UID];assert len(original)==1 and original[0]['uid']==UID
 row=dict(original[0]);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']==SOURCE
 tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']==row['native']['model']['triangles']==10679
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 entry=row['candidate']['entry'];assert entry['sha256']==SOURCE and not entry.get('suppressesBuildingUids') and not entry.get('footprintScope')
 destination=LOCAL/entry['asset'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
 receipt=read(PROPOSAL/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(PROPOSAL/'diagnostic.json.gz')in receipt['evidenceRefs']
 candidate=read(PROPOSAL/'terrain-candidates.json');assert len(candidate)==1 and candidate[0]['uids']==[UID]
 patch=candidate[0];assert ref(ROOT/patch['path'])['sha256']==patch['sha256']
 terrain=read(PROPOSAL/'terrain.json');assert terrain['sourceBuildingGeometryChanges']==0 and terrain['terrainProposalGeometryChanged']is True
 assert patch['replaces']['url']=='city/data/government-native-255439-0.json' and patch['replaces']['retainedUids']==['landsd/255439:0']
 lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));bounds=patch['bounds'];assert bounds[0]<=lo[0]<=hi[0]<=bounds[2]and bounds[1]<=lo[2]<=hi[2]<=bounds[3];routing=[]
 for p in current['terrainPatches']:
  actual=ROOT/'3d-viewer'/p['url'];other=read(actual);all_bounds=[p.get('bounds'),other.get('bounds')]
  if not any(all_bounds):all_bounds=[module('hkdi_current_patch_bounds','native_patch_resolution.py')._patch_bounds(other)]
  routing.append(dict(entry=p,asset=ref(actual),testedBounds=[b for b in all_bounds if b]))
 parent=ROOT/'3d-viewer/city/data/terrain.json'
 final=module('citic_current_forms','xl-final-script-pass.py');forms=final.load_forms(bounds);form,_,tile=next(f for f in forms if f[0]['uid']==UID);assert form['buildingCSUID']==row['source']['building']['buildingCSUID']
 row.update(source={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())},candidate={**row['candidate'],'path':str(destination.relative_to(ROOT))})
 context=dict(uid=UID,sourceSHA256=SOURCE,identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms})
 identity=verify_files(row,context,LOCAL/'identity-current');assert identity['passed'],'Current exact original identity failed'
 catalogue=dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[entry],counts={'packedModels':1},area='Complete original Parkview Block11 authentic retained-terrain diagnosis')
 save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']})
 save(DOC/'selection.json.gz',dict(rows=[row],batch=BATCH,manifestSHA256=start['sha256']));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'identity-proofs.json',dict(rows=[identity]))
 save(DOC/'terrain-candidates.json',candidate);save(DOC/'terrain.json',terrain)
 save(DOC/'current-source-terrain-preflight.json',dict(currentManifest=start,sourceSHA256=SOURCE,sourceProviderRootAndStreams=source_stream_binding(raw),decodedOriginalWorldSHA256=digest(tri.tobytes()),completeOriginalFaces=len(tri),immutableTerrainProposal=patch,rootTerrain=ref(parent),completeCurrentTerrainRouting=routing,modelGeometryChanges=0,terrainProposalGeometryChanged=True,publication=False))
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[0],existingNative=f['uid'] in installed or bool(f.get('modelGeometry'))) for f,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms},candidateIds=[UID],patches=candidate))
 rel=lambda p:str(p.relative_to(ROOT))
 def call(cmd,allowed=(0,)):
  assert subprocess.run(cmd,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode in allowed;assert reservations.owns(lease) and ref(manifest)==start,'Current manifest changed during candidate-only physical work'
 module_snapshot=DOC/'production-module-closure.json'
 js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure}from'./source-scripts/city/government-import/literal_production_module_dependency_closure_20261010.mjs';const root=new URL('./',import.meta.url);writeFileSync(process.argv[1],JSON.stringify(snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics.mjs',root),root)));"
 call(['node','--input-type=module','-e',js,str(module_snapshot)])
 closure=read(module_snapshot);assert closure['completeAuditedLiteralImportClosure']is True and closure['unsupportedDynamicImports']==0
 native_module_snapshot=DOC/'native-production-module-closure.json'
 native_js=js.replace('acceptance-metrics.mjs','xl-terrain-recovery-20261011-parkview-block11-check-all-current-native-v1.mjs')
 call(['node','--input-type=module','-e',native_js,str(native_module_snapshot)])
 native_closure=read(native_module_snapshot);assert native_closure['completeAuditedLiteralImportClosure']is True and native_closure['unsupportedDynamicImports']==0
 for path,h in native_closure['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
 closure['inputHashes'].update(native_closure['inputHashes'])
 for path,sha in closure['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'xl-terrain-recovery-20261011-parkview-block11-check-all-current-native-v1.mjs'),rel(DOC)+'/'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');assert len(runtime['rows'])==1;g=runtime['rows'][0];assert g['uid']==UID
 drawn=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert drawn.shape==tri.shape and np.max(np.abs(drawn-tri))<=1e-9
 f=final.foundation_context(drawn,ground,Polygon(form['rings'][0],form['rings'][1:]));foundation=dict(uid=UID,sourceSHA256=SOURCE,foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0)
 save(DOC/'foundation.json',dict(rows=[foundation],modelGeometryChanges=0));metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');policy=module('citic_current_policy','acceptance-policy.py');reasons=[]
 if validation['loaderAccepted']!=1 or validation['checksPassed']!=1 or validation['exceptions']:reasons.append('complete-current-loader-validation')
 m=metrics['rows'][0];reasons.extend(policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),m,metrics['profiles']['mobile']))
 if not foundation['strictFoundationAccepted']:reasons.append('whole-source-foundation')
 diagnostic=resolve_global_bottom_warning(validation['results'][0],m,foundation);save(DOC/'diagnostic-resolutions.json',dict(rows=[dict(uid=UID,rawValidation=validation['results'][0],resolution=diagnostic)]));reasons.extend(diagnostic['remaining'])
 for r in read(DOC/'neighbour-checks.json')['rows']:reasons.extend('neighbour:'+r['uid']+':'+reason for reason in r['reasons'])
 native=read(DOC/'native-neighbour-checks.json');reasons.extend('native:'+u for u in set(native['blocked'])-set(native['resolved']))
 for p,h in runtime['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 for path,sha in closure['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 assert ref(manifest)==start and reservations.owns(lease)
 for url,pin in catalogue_start.items():assert ref(ROOT/'3d-viewer'/url)==pin
 refs=[ref(Path(__file__)),ref(PRIOR/'check-selection.json.gz'),ref(PRIOR/'indexed-preflight.json'),ref(destination),ref(LOCAL/'runtime-geometry.json.gz'),ref(LOCAL/'catalogue.json'),ref(parent),start]
 refs.extend([ref(PROPOSAL/'result.json'),ref(PROPOSAL/'diagnostic.json.gz'),ref(PROPOSAL/'terrain-candidates.json'),ref(PROPOSAL/'terrain.json'),ref(ROOT/patch['path'])]);refs.extend(receipt['evidenceRefs']);refs.extend(catalogue_start.values());refs.append(ref(BASE/'government-xl-all-installed-dependency-metadata-applied-v1-20261010/result.json'))
 refs.extend([ref(module_snapshot),ref(native_module_snapshot),ref(HERE/'literal_production_module_dependency_closure_20261010.mjs')]);refs.extend(ref(ROOT/p)for p in closure['inputHashes'])
 refs.extend(ref(HERE/n) for n in ['acceptance-metrics.mjs','check-neighbours.mjs','check-native-neighbours.mjs','xl-terrain-recovery-20261011-parkview-block11-check-all-current-native-v1.mjs','exact_original_georef_cell_identity_20261009.py','xl-final-script-pass.py','acceptance-policy.py','terrain_diagnostic_resolution.py','xl-second-pass.py','native_patch_resolution.py','exact_packed_world_geometry_20261009.py','xl_source_stream_binding_20261009.py'])
 freeze=module('citic_current_physical_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'complete-current-parkview-authentic-foreign-preserved-terrain-physical-v2',[ROOT/r['path'] for r in refs],dict(uids=[UID],completeProductionModuleDependencyClosure=ref(module_snapshot),productionModules=len(closure['modules']),manifestSHA256=start['sha256'],reasons=sorted(set(reasons)),scriptChecksPassed=not reasons,completeOriginalFaces=10679,currentNeighbourForms=len(forms),sourceGeometryChanges=0,terrainProposalChanged=True,publication=False,newlyInstalled=0))
 print(dict(reasons=sorted(set(reasons)),currentNeighbourForms=len(forms),publication=False),flush=True)
def main():
 assert not DOC.exists();final=module('citic_lease_forms','xl-final-script-pass.py');row=next(r for r in read(PRIOR/'check-selection.json.gz')['rows'] if r['uid']==UID);bounds=read(PROPOSAL/'terrain-candidates.json')[0]['bounds'];forms=final.load_forms(bounds);keys=['building:'+u for u in sorted({f['uid'] for f,_,_ in forms}|{UID})]+['terrain-surface:city/data/government-native-255439-0.json']
 claim=reservations.claim('parkview-authentic-terrain-current-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 try:owned()
 finally:assert reservations.release(read(LEASE))['ok']
if __name__=='__main__':main()
