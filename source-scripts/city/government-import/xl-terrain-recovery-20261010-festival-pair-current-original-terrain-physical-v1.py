"""Fresh full Festival Walk complete original pair physical diagnosis using its immutable original terrain proposal.

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
PRIOR=BASE/'government-xl-festival-two-originals-full-physical-20261007'
BATCH='government-xl-terrain-recovery-festival-pair-original-terrain-current-v1-20261010'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UID='landsd/91827:0';UIDS={UID,'landsd/104302:0'};SOURCE='786e89452ba921ce3b16ba1b899919d4965f829ea5fb7b1756cd6ab5ed4c2ef8'
TERRAIN_SHA='1ea21a409100a085a620cec7d1b403e98c2b4ee5b2b51c8946f95e2cd06334e0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);installed={}
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for m in read(path)['models']:assert m['uid'] not in installed;installed[m['uid']]=(path,m)
 assert not UIDS.intersection(installed)
 original=read(PRIOR/'selection.json.gz')['rows'];assert {r['uid'] for r in original}==UIDS and len(original)==2
 rows=[];assets=[];source_tri={}
 for source in original:
  row=dict(source);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']==row['native']['model']['triangles']
  assert row['sourceSHA256']=={UID:SOURCE,'landsd/104302:0':'4fc3b065399321f7a0a05d8b6c8f47fe813c2924677e009104f13cc7b1d2f0fe'}[row['uid']]
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  entry=row['candidate']['entry'];assert entry['sha256']==row['sourceSHA256'] and not entry.get('suppressesBuildingUids') and not entry.get('footprintScope')
  destination=LOCAL/entry['asset'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw);assets.append(destination);row['candidate']={**row['candidate'],'path':str(destination.relative_to(ROOT))};rows.append(row);source_tri[row['uid']]=tri
 historical_candidate=read(PRIOR/'terrain-candidates.json');assert len(historical_candidate)==1 and set(historical_candidate[0]['uids'])=={UID,'landsd/104302:0'} and historical_candidate[0]['sha256']==TERRAIN_SHA;candidate=historical_candidate
 patch=candidate[0];assert digest((ROOT/patch['path']).read_bytes())==TERRAIN_SHA and not patch.get('replaces')
 bounds=patch['bounds'];proposed=read(ROOT/patch['path']);assert len(proposed['nativeMesh']['index'])//3==patch['triangles']==14914
 terrain=read(PRIOR/'terrain.json');assert {k:v for k,v in terrain['patch'].items() if k!='uids'}=={k:v for k,v in patch.items() if k!='uids'} and terrain['patch']['uids']==[UID] and terrain['modelGeometryChanges']==0;terrain={**terrain,'patch':patch,'historicalTerrainRegistrationExpandedToOriginalPair':True,'terrainGeometryChanged':False}
 for r in terrain['sourceFiles']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 # Full bounds fallback is deliberately conservative for nested/wrapper terrains.
 routing=[]
 for p in current['terrainPatches']:
  actual=ROOT/'3d-viewer'/p['url'];other=read(actual)
  all_bounds=[p.get('bounds'),other.get('bounds')]
  if not any(all_bounds):
   helper=module('festival-podium_current_patch_bounds','native_patch_resolution.py');all_bounds=[helper._patch_bounds(other)]
  assert all(not box(*b).intersects(box(*bounds)) for b in all_bounds if b),'Current retained terrain overlaps original proposal: '+p['url']
  routing.append(dict(entry=p,asset=ref(actual),testedBounds=[b for b in all_bounds if b]))
 second=module('festival-podium_current_patch_validate','xl-second-pass.py');parent=ROOT/'3d-viewer/city/data/terrain.json';second.resolution.validate_patch(proposed,read(parent))
 final=module('festival_pair_current_forms','xl-final-script-pass.py');forms=final.load_forms(bounds);identities=[];contexts=[]
 for row in rows:
  uid=row['uid'];tri=source_tri[uid];form,_,tile=next(f for f in forms if f[0]['uid']==uid);assert form['buildingCSUID']==row['source']['building']['buildingCSUID'];row['source']={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())}
  context=dict(uid=uid,sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms});identity=verify_files(row,context,LOCAL/'identity-current'/uid.split('/')[1]);assert identity['passed'],'Current exact original identity failed: '+uid;identities.append(identity);contexts.append(context)
 catalogue=read(HERE/'local'/PRIOR.name/'catalogue.json');assert {r['uid'] for r in catalogue['models']}==UIDS;catalogue.update(counts={'packedModels':2},area='Complete original Festival pair current immutable terrain diagnostic')
 save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in rows})
 save(DOC/'selection.json.gz',dict(rows=rows,batch=BATCH,manifestSHA256=start['sha256']));save(DOC/'context.json.gz',dict(rows=contexts));save(DOC/'identity-proofs.json',dict(rows=identities))
 save(DOC/'terrain-candidates.json',candidate);save(DOC/'terrain.json',terrain)
 save(DOC/'current-source-terrain-preflight.json',dict(currentManifest=start,completeOriginalSources=[dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],sourceProviderRootAndStreams=source_stream_binding(p.read_bytes()),decodedOriginalWorldSHA256=digest(source_tri[r['uid']].tobytes()),completeOriginalFaces=len(source_tri[r['uid']])) for r,p in zip(rows,assets)],immutableTerrainProposal=patch,rootTerrain=ref(parent),completeCurrentTerrainRouting=routing,modelGeometryChanges=0,newTerrainGeometryChanges=0,publication=False))
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[0],existingNative=f['uid'] in installed or bool(f.get('modelGeometry'))) for f,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms},candidateIds=sorted(UIDS),patches=candidate))
 rel=lambda p:str(p.relative_to(ROOT))
 def call(cmd,allowed=(0,)):
  assert subprocess.run(cmd,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode in allowed;assert reservations.owns(lease) and ref(manifest)==start,'Current manifest changed during candidate-only physical work'
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');assert {r['uid'] for r in runtime['rows']}==UIDS;foundations=[];decisions=[];metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');policy=module('festival_pair_current_policy','acceptance-policy.py');reasons=[]
 if validation['loaderAccepted']!=2 or validation['checksPassed']!=2 or validation['exceptions']:reasons.append('complete-current-loader-validation')
 for row in rows:
  uid=row['uid'];g=next(r for r in runtime['rows'] if r['uid']==uid);tri=source_tri[uid];drawn=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert drawn.shape==tri.shape and np.max(np.abs(drawn-tri))<=1e-9;form=row['source']['building']
  f=final.foundation_context(drawn,ground,Polygon(form['rings'][0],form['rings'][1:]));foundation=dict(uid=uid,sourceSHA256=row['sourceSHA256'],foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0);foundations.append(foundation);m=next(r for r in metrics['rows'] if r['uid']==uid);identity=next(r for r in identities if r['uid']==uid)
  reasons.extend(uid+':'+x for x in policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=identity['proof']),m,metrics['profiles']['mobile']))
  if not foundation['strictFoundationAccepted']:reasons.append(uid+':whole-source-foundation')
  v=next(r for r in validation['results'] if r['uid']==uid);diagnostic=resolve_global_bottom_warning(v,m,foundation);decisions.append(dict(uid=uid,rawValidation=v,resolution=diagnostic));reasons.extend(uid+':'+x for x in diagnostic['remaining'])
 save(DOC/'foundation.json',dict(rows=foundations,modelGeometryChanges=0));save(DOC/'diagnostic-resolutions.json',dict(rows=decisions))
 for r in read(DOC/'neighbour-checks.json')['rows']:reasons.extend('neighbour:'+r['uid']+':'+reason for reason in r['reasons'])
 native=read(DOC/'native-neighbour-checks.json');reasons.extend('native:'+u for u in set(native['blocked'])-set(native['resolved']))
 for p,h in runtime['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 assert ref(manifest)==start and reservations.owns(lease)
 refs=[ref(Path(__file__)),ref(PRIOR/'selection.json.gz'),ref(PRIOR/'terrain-candidates.json'),ref(PRIOR/'terrain.json'),*[ref(p) for p in assets],ref(ROOT/patch['path']),ref(LOCAL/'runtime-geometry.json.gz'),ref(LOCAL/'catalogue.json'),ref(parent),start]
 refs.extend(ref(HERE/n) for n in ['acceptance-metrics.mjs','check-neighbours.mjs','check-native-neighbours.mjs','exact_original_georef_cell_identity_20261009.py','xl-final-script-pass.py','acceptance-policy.py','terrain_diagnostic_resolution.py','xl-second-pass.py','native_patch_resolution.py','exact_packed_world_geometry_20261009.py','xl_source_stream_binding_20261009.py'])
 freeze=module('festival-podium_current_physical_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'complete-current-festival-podium-original-terrain-physical-v1',[ROOT/r['path'] for r in refs],dict(uids=sorted(UIDS),manifestSHA256=start['sha256'],reasons=sorted(set(reasons)),scriptChecksPassed=not reasons,completeOriginalFaces=sum(len(t) for t in source_tri.values()),currentNeighbourForms=len(forms),sourceGeometryChanges=0,terrainProposalChanged=False,publication=False,newlyInstalled=0))
 print(dict(reasons=sorted(set(reasons)),currentNeighbourForms=len(forms),publication=False),flush=True)
def main():
 assert not DOC.exists();final=module('festival-podium_lease_forms','xl-final-script-pass.py');bounds=read(PRIOR/'terrain-candidates.json')[0]['bounds'];forms=final.load_forms(bounds);keys=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted({f['uid'] for f,_,_ in forms}|UIDS)]
 claim=reservations.claim('festival-podium-original-terrain-current-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 try:owned()
 finally:assert reservations.release(read(LEASE))['ok']
if __name__=='__main__':main()
