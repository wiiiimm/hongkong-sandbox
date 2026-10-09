"""Fresh complete Ying Hoi tower plus unchanged installed original podium.

Candidate-only full physical diagnosis; no terrain/review/publication writes.
The retained podium is explicitly included as a complete original actor, not
treated as a proxy or omitted foreign actor. Every source gate remains raw.
"""
import importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from terrain_diagnostic_resolution import resolve_global_bottom_warning
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-ying-hoi-original-assembly-current-20261007'
BATCH='government-xl-terrain-recovery-ying-hoi-existing-terrain-current-v1-20261010'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
SOURCES={'landsd/205663:0':'97f824a1699c079e1d0e98962dd76175e384500340bbf22a732f5b92730ac502','landsd/207957:0':'82e6a654d9ac5451271f8fce1cf82c0a234dd9e67649a47f4e51bfffeb2088be'}
RETAINED='landsd/205663:0';CANDIDATE='landsd/207957:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);catalogues={};installed={}
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogues[str(path.relative_to(ROOT))]=ref(path)
  for m in read(path)['models']:assert m['uid'] not in installed;installed[m['uid']]=(path,m)
 assert RETAINED in installed and CANDIDATE not in installed
 native_path,native_entry=installed[RETAINED];native_asset=native_path.parent/native_entry['asset'];assert digest(native_asset.read_bytes())==native_entry['sha256']==SOURCES[RETAINED]
 pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],RETAINED)).fetchone()==('installed-verified',SOURCES[RETAINED])
 final=module('ying_hoi_current_forms','xl-final-script-pass.py');rows=[];contexts=[];identities=[];entries=[];sources=[];refs=[ref(Path(__file__)),ref(PRIOR/'selection.json.gz'),start,ref(native_path),ref(native_asset)]
 originals=read(PRIOR/'selection.json.gz')['rows'];assert {r['uid'] for r in originals}==set(SOURCES)
 for original in originals:
  row=dict(original);row['triangles']=row['native']['model']['triangles'];uid=row['uid'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']==SOURCES[uid]
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles'];lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);form,_,tile=next(f for f in forms if f[0]['uid']==uid);assert form['buildingCSUID']==row['source']['building']['buildingCSUID']
  entry=native_entry if uid==RETAINED else row['candidate']['entry'];assert entry['sha256']==SOURCES[uid] and not entry.get('suppressesBuildingUids') and not entry.get('footprintScope')
  destination=LOCAL/entry['asset'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
  row.update(source={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())},candidate={**row['candidate'],'path':str(destination.relative_to(ROOT)),'entry':entry},sourceRole='retained-installed-unchanged-original' if uid==RETAINED else 'pending-original-tower')
  context={'uid':uid,'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms}}
  identity=verify_files(row,context,LOCAL/'identity-current'/uid.split('/')[1].replace(':','-'));identities.append(identity);contexts.append(context);rows.append(row);entries.append(entry);sources.append(dict(uid=uid,originalSourceSHA256=digest(raw),providerRootAndStreams=source_stream_binding(raw),completeOriginalFaces=len(tri),completeDecodedOriginalWorldSHA256=digest(tri.tobytes()),retainedInstalled=uid==RETAINED));refs.append(ref(destination))
 catalogue=read(HERE/'local'/PRIOR.name/'catalogue.json');catalogue.update(models=entries,counts={'packedModels':2},area='Complete original Ying Hoi tower and unchanged retained podium diagnostic')
 save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in rows})
 save(DOC/'selection.json.gz',dict(rows=rows,batch=BATCH,manifestSHA256=start['sha256']));save(DOC/'context.json.gz',dict(rows=contexts));save(DOC/'identity-proofs.json',dict(rows=identities));save(DOC/'retained-original-source-context.json',dict(retainedUID=RETAINED,pendingCandidateUID=CANDIDATE,currentNativeCatalogue=ref(native_path),currentNativeSource=ref(native_asset),currentNativeEntry=native_entry,currentReviewSnapshot=pointer['snapshotId'],allOriginalSources=sources,currentManifest=start,terrainChanged=False,publication=False))
 save(DOC/'terrain-candidates.json',[]);save(DOC/'terrain.json',dict(patches=[],sourceFiles=[],modelGeometryChanges=0,terrainGeometryChanges=0));save(DOC/'existing-terrain-only.json',dict(manifestSHA256=start['sha256'],retainedInstalledUIDs=[RETAINED],candidateUIDs=[CANDIDATE],allSourcesRequireWholeCurrentPhysicalChecks=True))
 alltri=[decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in rows];lo=np.concatenate(alltri).min(axis=(0,1));hi=np.concatenate(alltri).max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[],existingNative=f['uid'] in installed or bool(f.get('modelGeometry'))) for f,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms},candidateIds=list(SOURCES),completeOwnedOriginalUIDs=list(SOURCES),retainedInstalledOriginalUIDs=[RETAINED],patches=[]))
 rel=lambda p:str(p.relative_to(ROOT))
 def call(cmd,allowed=(0,)):
  assert subprocess.run(cmd,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode in allowed;assert reservations.owns(lease) and ref(manifest)==start,'Current manifest changed during candidate-only physical work'
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');foundations=[]
 for g in runtime['rows']:
  row=next(r for r in rows if r['uid']==g['uid']);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);decoded=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert tri.shape==decoded.shape and np.max(np.abs(tri-decoded))<=1e-9
  b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));foundations.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0))
 save(DOC/'foundation.json',dict(rows=foundations,modelGeometryChanges=0));metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');policy=module('ying_hoi_current_policy','acceptance-policy.py');reasons=[];diagnostic_resolutions=[]
 if validation['loaderAccepted']!=len(SOURCES) or validation['checksPassed']!=len(SOURCES) or validation['exceptions']:reasons.append('complete-current-loader-validation')
 for row in rows:
  uid=row['uid'];m=next(m for m in metrics['rows'] if m['uid']==uid);i=next(i for i in identities if i['uid']==uid);f=next(f for f in foundations if f['uid']==uid)
  reasons.extend(uid+':'+r for r in policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=i['proof']),m,metrics['profiles']['mobile']))
  if not i['passed']:reasons.append(uid+':current-original-identity')
  if not f['strictFoundationAccepted']:reasons.append(uid+':whole-source-foundation')
  original_validation=next(v for v in validation['results'] if v['uid']==uid);diagnostic=resolve_global_bottom_warning(original_validation,m,f);diagnostic_resolutions.append(dict(uid=uid,rawValidation=original_validation,resolution=diagnostic));reasons.extend(uid+':'+r for r in diagnostic['remaining'])
 save(DOC/'diagnostic-resolutions.json',dict(rows=diagnostic_resolutions))
 for r in read(DOC/'neighbour-checks.json')['rows']:reasons.extend(r['uid']+':'+reason for reason in r['reasons']);assert r['maxGroundChange']==0
 native=read(DOC/'native-neighbour-checks.json');reasons.extend('native:'+u for u in set(native['blocked'])-set(native['resolved']))
 for p,h in runtime['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 assert ref(manifest)==start and reservations.owns(lease)
 refs.extend(ref(p) for p in DOC.glob('*') if p.is_file());refs.extend([ref(LOCAL/'runtime-geometry.json.gz'),ref(LOCAL/'catalogue.json'),ref(HERE/'acceptance-metrics.mjs'),ref(HERE/'check-neighbours.mjs'),ref(HERE/'check-native-neighbours.mjs'),ref(HERE/'exact_original_georef_cell_identity_20261009.py'),ref(HERE/'xl-final-script-pass.py'),ref(HERE/'acceptance-policy.py'),ref(HERE/'terrain_diagnostic_resolution.py')])
 spec=importlib.util.spec_from_file_location('ying_hoi_current_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-current-unchanged-terrain-retained-ying-hoi-original-assembly-v1',[ROOT/r['path'] for r in refs],dict(uids=list(SOURCES),retainedInstalledOriginalUIDs=[RETAINED],pendingCandidateUIDs=[CANDIDATE],manifestSHA256=start['sha256'],reasons=sorted(set(reasons)),scriptChecksPassed=not reasons,terrainGeometryChanges=0,sourceGeometryChanges=0,publication=False,newlyInstalled=0))
 print(dict(reasons=sorted(set(reasons)),retainedPodiumUnchanged=True,publication=False),flush=True)
def main():
 assert not DOC.exists();claim=reservations.claim('ying-hoi-existing-terrain-current-'+str(uuid.uuid4()),['building:'+u for u in SOURCES],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 try:owned()
 finally:assert reservations.release(read(LEASE))['ok']
if __name__=='__main__':main()
