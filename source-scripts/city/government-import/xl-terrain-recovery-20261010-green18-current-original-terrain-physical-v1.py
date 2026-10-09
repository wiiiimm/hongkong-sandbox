"""Fresh full Green18 physical diagnosis using its immutable original terrain proposal.

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
PRIOR=BASE/'government-xl-green18-original-parent-local-rim-20261007'
BATCH='government-xl-terrain-recovery-green18-original-terrain-current-v1-20261010'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UID='landsd/6462:0';SOURCE='d2d2c62ed2d29ffbf7ec4060c108f1c53eb784558120cb153a5d9482d60d493f'
TERRAIN_SHA='a092210b53f0d4a7286a9a1d10b262c8094058f9c14f6b8a6007cde73d3b6077'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);installed={}
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for m in read(path)['models']:assert m['uid'] not in installed;installed[m['uid']]=(path,m)
 assert UID not in installed
 original=read(PRIOR/'selection.json.gz')['rows'];assert len(original)==1 and original[0]['uid']==UID
 row=dict(original[0]);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']==SOURCE
 tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']==row['native']['model']['triangles']==11088
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 entry=row['candidate']['entry'];assert entry['sha256']==SOURCE and not entry.get('suppressesBuildingUids') and not entry.get('footprintScope')
 destination=LOCAL/entry['asset'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
 candidate=read(PRIOR/'terrain-candidates.json');assert len(candidate)==1 and candidate[0]['uids']==[UID] and candidate[0]['sha256']==TERRAIN_SHA
 patch=candidate[0];assert digest((ROOT/patch['path']).read_bytes())==TERRAIN_SHA and not patch.get('replaces')
 bounds=patch['bounds'];proposed=read(ROOT/patch['path']);assert len(proposed['nativeMesh']['index'])//3==patch['triangles']==5803
 terrain=read(PRIOR/'terrain.json');assert terrain['patch']==patch and terrain['modelGeometryChanges']==0
 for r in terrain['sourceFiles']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 # Full bounds fallback is deliberately conservative for nested/wrapper terrains.
 routing=[]
 for p in current['terrainPatches']:
  actual=ROOT/'3d-viewer'/p['url'];other=read(actual)
  all_bounds=[p.get('bounds'),other.get('bounds')]
  if not any(all_bounds):
   helper=module('green18_current_patch_bounds','native_patch_resolution.py');all_bounds=[helper._patch_bounds(other)]
  assert all(not box(*b).intersects(box(*bounds)) for b in all_bounds if b),'Current retained terrain overlaps original proposal: '+p['url']
  routing.append(dict(entry=p,asset=ref(actual),testedBounds=[b for b in all_bounds if b]))
 second=module('green18_current_patch_validate','xl-second-pass.py');parent=ROOT/'3d-viewer/city/data/terrain.json';second.resolution.validate_patch(proposed,read(parent))
 final=module('green18_current_forms','xl-final-script-pass.py');forms=final.load_forms(bounds);form,_,tile=next(f for f in forms if f[0]['uid']==UID);assert form['buildingCSUID']==row['source']['building']['buildingCSUID']
 row.update(source={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())},candidate={**row['candidate'],'path':str(destination.relative_to(ROOT))})
 context=dict(uid=UID,sourceSHA256=SOURCE,identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms})
 identity=verify_files(row,context,LOCAL/'identity-current');assert identity['passed'],'Current exact original identity failed'
 catalogue=read(HERE/'local'/PRIOR.name/'catalogue.json');catalogue.update(models=[entry],counts={'packedModels':1},area='Complete original Green18 current immutable terrain diagnostic')
 save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']})
 save(DOC/'selection.json.gz',dict(rows=[row],batch=BATCH,manifestSHA256=start['sha256']));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'identity-proofs.json',dict(rows=[identity]))
 save(DOC/'terrain-candidates.json',candidate);save(DOC/'terrain.json',terrain)
 save(DOC/'current-source-terrain-preflight.json',dict(currentManifest=start,sourceSHA256=SOURCE,sourceProviderRootAndStreams=source_stream_binding(raw),decodedOriginalWorldSHA256=digest(tri.tobytes()),completeOriginalFaces=len(tri),immutableTerrainProposal=patch,rootTerrain=ref(parent),completeCurrentTerrainRouting=routing,modelGeometryChanges=0,newTerrainGeometryChanges=0,publication=False))
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[0],existingNative=f['uid'] in installed or bool(f.get('modelGeometry'))) for f,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms},candidateIds=[UID],patches=candidate))
 rel=lambda p:str(p.relative_to(ROOT))
 def call(cmd,allowed=(0,)):
  assert subprocess.run(cmd,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode in allowed;assert reservations.owns(lease) and ref(manifest)==start,'Current manifest changed during candidate-only physical work'
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');assert len(runtime['rows'])==1;g=runtime['rows'][0];assert g['uid']==UID
 drawn=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert drawn.shape==tri.shape and np.max(np.abs(drawn-tri))<=1e-9
 f=final.foundation_context(drawn,ground,Polygon(form['rings'][0],form['rings'][1:]));foundation=dict(uid=UID,sourceSHA256=SOURCE,foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0)
 save(DOC/'foundation.json',dict(rows=[foundation],modelGeometryChanges=0));metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');policy=module('green18_current_policy','acceptance-policy.py');reasons=[]
 if validation['loaderAccepted']!=1 or validation['checksPassed']!=1 or validation['exceptions']:reasons.append('complete-current-loader-validation')
 m=metrics['rows'][0];reasons.extend(policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),m,metrics['profiles']['mobile']))
 if not foundation['strictFoundationAccepted']:reasons.append('whole-source-foundation')
 diagnostic=resolve_global_bottom_warning(validation['results'][0],m,foundation);save(DOC/'diagnostic-resolutions.json',dict(rows=[dict(uid=UID,rawValidation=validation['results'][0],resolution=diagnostic)]));reasons.extend(diagnostic['remaining'])
 for r in read(DOC/'neighbour-checks.json')['rows']:reasons.extend('neighbour:'+r['uid']+':'+reason for reason in r['reasons'])
 native=read(DOC/'native-neighbour-checks.json');reasons.extend('native:'+u for u in set(native['blocked'])-set(native['resolved']))
 for p,h in runtime['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 assert ref(manifest)==start and reservations.owns(lease)
 refs=[ref(Path(__file__)),ref(PRIOR/'selection.json.gz'),ref(PRIOR/'terrain-candidates.json'),ref(PRIOR/'terrain.json'),ref(destination),ref(ROOT/patch['path']),ref(LOCAL/'runtime-geometry.json.gz'),ref(LOCAL/'catalogue.json'),ref(parent),start]
 refs.extend(ref(HERE/n) for n in ['acceptance-metrics.mjs','check-neighbours.mjs','check-native-neighbours.mjs','exact_original_georef_cell_identity_20261009.py','xl-final-script-pass.py','acceptance-policy.py','terrain_diagnostic_resolution.py','xl-second-pass.py','native_patch_resolution.py','exact_packed_world_geometry_20261009.py','xl_source_stream_binding_20261009.py'])
 freeze=module('green18_current_physical_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'complete-current-green18-original-terrain-physical-v1',[ROOT/r['path'] for r in refs],dict(uids=[UID],manifestSHA256=start['sha256'],reasons=sorted(set(reasons)),scriptChecksPassed=not reasons,completeOriginalFaces=11088,currentNeighbourForms=len(forms),sourceGeometryChanges=0,terrainProposalChanged=False,publication=False,newlyInstalled=0))
 print(dict(reasons=sorted(set(reasons)),currentNeighbourForms=len(forms),publication=False),flush=True)
def main():
 assert not DOC.exists();final=module('green18_lease_forms','xl-final-script-pass.py');bounds=read(PRIOR/'terrain-candidates.json')[0]['bounds'];forms=final.load_forms(bounds);keys=['building:'+u for u in sorted({f['uid'] for f,_,_ in forms}|{UID})]
 claim=reservations.claim('green18-original-terrain-current-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 try:owned()
 finally:assert reservations.release(read(LEASE))['ok']
if __name__=='__main__':main()
