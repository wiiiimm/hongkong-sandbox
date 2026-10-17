"""Unchanged Block6 against newly installed current terrain. Read-only diagnostics."""
import json,os,subprocess,importlib.util
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
from xl_source_stream_binding_20261009 import source_stream_binding
from terrain_diagnostic_resolution import resolve_global_bottom_warning
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-parkview-block6-bounded-original-clear-cap-probe-v1-20261011';BATCH='government-xl-parkview-block6-fresh-current-physical-capture-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/255438:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 resume=DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);installed={};catalogues=[ref(ROOT/'3d-viewer'/url)for url in current['officialModelCatalogues']]
 for url in current['officialModelCatalogues']:
  for e in read(ROOT/'3d-viewer'/url)['models']:assert e['uid']not in installed;installed[e['uid']]=e
 assert UID not in installed and 'landsd/255647:0'in installed
 old=read(OLD/'diagnostic.json.gz');sel=ROOT/next(x['path']for x in old['evidenceRefs']if x['path'].endswith('check-selection.json.gz'));row=next(x for x in read(sel)['rows']if x['uid']==UID);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']=='363c8df82ecf39c7a9d1f6948e2b2aec06af28820642fdeeab45f9d08da36bae';tri=decode_original_world_triangles(raw);assert len(tri)==11041
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()==(row['native']['resultSha'],)
 entry=row['candidate']['entry'];assert entry['sha256']==digest(raw)and not entry.get('footprintScope')and not entry.get('suppressesBuildingUids');asset=LOCAL/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
 lo,hi=tri.min((0,1)),tri.max((0,1));bounds=[float(lo[0]-30),float(lo[2]-30),float(hi[0]+30),float(hi[2]+30)];final=module('block6_current_forms','xl-final-script-pass.py')
 for u in ['landsd/254491:0','landsd/255439:0','landsd/255647:0']:
  bb=installed[u]['worldBounds'];bounds=[min(bounds[0],bb[0][0]-30),min(bounds[1],bb[0][2]-30),max(bounds[2],bb[1][0]+30),max(bounds[3],bb[1][2]+30)]
 forms=final.load_forms(bounds);form,_,tile=next(x for x in forms if x[0]['uid']==UID);assert form['buildingCSUID']==row['source']['building']['buildingCSUID'];row['source']=dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()));row['candidate']={**row['candidate'],'path':str(asset.relative_to(ROOT))};context=dict(uid=UID,sourceSHA256=digest(raw),identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms});identity=verify_files(row,context,LOCAL/'identity-current')
 save(DOC/'selection.json.gz',dict(rows=[row],batch=BATCH,manifestSHA256=start['sha256']));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'identity-proofs.json',dict(rows=[identity]));save(DOC/'terrain-candidates.json',[])
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[entry],counts=dict(packedModels=1)));save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']})
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[],existingNative=f['uid']in installed or bool(f.get('modelGeometry')))for f,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms},candidateIds=[UID],patches=[]))
 save(DOC/'source-preflight.json',dict(currentManifest=start,currentCatalogueRefs=catalogues,sourceBinding=source_stream_binding(raw),completeOriginalWorldSHA256=digest(tri.tobytes()),installedBlock11Receipt=ref(B/'government-xl-parkview-block11-unchanged-installed-v1-20261011/result.json'),completeCurrentForeignFormScope=len(forms),modelGeometryChanges=0,terrainGeometryChanges=0,publication=False))
 rel=lambda p:str(p.relative_to(ROOT))
 def call(args,allowed=(0,)):
  assert subprocess.run(args,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode in allowed;assert ref(manifest)==start
 if not (LOCAL/'runtime-geometry.json.gz').exists():call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 if not (DOC/'validation.json').exists():call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'parkview_block6_check_all_current_native_20261011.mjs'),rel(DOC)+'/'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');rt=runtime['rows'][0];index=np.asarray(rt['index']).reshape(-1,3);drawn=np.asarray(rt['position']).reshape(-1,3)[index];ground=np.asarray(rt['drawnGroundGeometry']).reshape(-1,3,3);assert drawn.shape==tri.shape
 f=final.foundation_context(drawn,ground,Polygon(form['rings'][0],form['rings'][1:]));foundation=dict(uid=UID,foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0);save(DOC/'foundation.json',dict(rows=[foundation]));metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');m=metrics['rows'][0];resolution=resolve_global_bottom_warning(validation['results'][0],m,foundation);save(DOC/'diagnostic-resolutions.json',dict(rows=[resolution]));policy=module('block6_current_policy','acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=digest(raw),identityProof=identity.get('proof')),m,metrics['profiles']['mobile']);native=read(DOC/'native-neighbour-checks.json');reasons+=['native:'+u for u in sorted(set(native['blocked'])-set(native['resolved']))];reasons+=resolution['remaining'];
 if not identity['passed']:reasons.append('current-identity')
 if not foundation['strictFoundationAccepted']:reasons.append('whole-source-foundation')
 save(DOC/'current-raw-outcome.json',dict(uid=UID,reasons=sorted(set(reasons)),currentManifest=start,identityPassed=identity['passed'],completeOriginalFaces=11041,completeCurrentDrawnGroundFaces=len(ground),completeCurrentDrawnGroundSHA256=digest(ground.tobytes()),completeLiteralSHA256=digest(drawn.tobytes()),completeOriginalWorldSHA256=digest(tri.tobytes()),rawNativeBlocked=native['blocked'],rawNativeResolved=native['resolved'],installationApproved=False,currentAcceptance=False,newlyInstalled=0))
 save(DOC/'literal-source-inputs.json.gz',dict(rows=[dict(uid=UID,path=row['candidate']['path'],entry=entry,building=form)],currentManifest=start,currentCatalogueRefs=catalogues,evidenceRefs=[ref(DOC/'selection.json.gz'),ref(asset)]));call(['node',str(HERE/'parkview_block6_actual_render_attributes_20261011.mjs'),rel(DOC/'literal-source-inputs.json.gz'),rel(DOC/'actual-render-geometry.json.gz')])
 for p,h in runtime['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 assert ref(manifest)==start
 print(json.dumps(dict(identity=identity['passed'],groundFaces=len(ground),reasons=sorted(set(reasons)),freshFourStreamCapture=True)),flush=True)
if __name__=='__main__':main()
