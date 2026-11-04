"""Unchanged Block17 against newly installed current terrain. Read-only diagnostics."""
import json,os,subprocess,importlib.util,argparse
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
from xl_source_stream_binding_20261009 import source_stream_binding
from terrain_diagnostic_resolution import resolve_global_bottom_warning
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-parkview-next-three-original-cap-contacts-v1-20261011';RANK=B/'xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1';GRAPH=B/'government-xl-parkview-block17-complete-original-support-graph-v1-20261011';BATCH='government-xl-parkview-block17-fresh-current-physical-capture-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/256116:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def source_preflight():
 ranked=next(r for r in read(RANK/'diagnostic.json.gz')['rows']if r['uid']==UID);selection=ROOT/ranked['cachedSelection']['path'];assert ref(selection)==ranked['cachedSelection'];row=next(r for r in read(selection)['rows']if r['uid']==UID);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==ranked['sourceSHA256']==row['sourceSHA256']=='d53efca53ef9693232a9ae6ffbf1f3a4596028ad444ed539d96fe1afb407cfb5';tri=decode_original_world_triangles(raw);assert tri.shape==(15614,3,3)and np.isfinite(tri).all();entry=row['candidate']['entry'];building=row['source']['building'];assert entry['uid']==building['uid']==UID and entry['objectId']==building['objectId']==256116 and entry['buildingCSUID']==building['buildingCSUID']=='3849513233T20050430'and entry['modelId']=='B384951323301063C0'and entry['triangles']==15614;graph=read(GRAPH/'diagnostic.json.gz');assert graph['completeOriginalWorldSHA256']==digest(tri.tobytes())and len(graph['completeSourceEdgeBodyFaces'])==93 and graph['completeOriginalDegenerateFaces']==[24,25]and len(graph['completeConditionalParents'])==92 and graph['unreachedBodies']==[62]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()==(row['native']['resultSha'],)
 # The actual generic identity/foundation/stream helpers have no model-global UID.
 final=module('block17_preflight_forms','xl-final-script-pass.py');assert all(callable(getattr(final,n))for n in ['load_forms','identity_context','foundation_context']);assert callable(verify_files)and callable(source_stream_binding);stream=source_stream_binding(raw)
 return row,raw,tri,selection,stream

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest-sha256');parser.add_argument('--source-preflight-only',action='store_true');args=parser.parse_args();row,raw,tri,selection,stream=source_preflight()
 if args.source_preflight_only:print(json.dumps(dict(sourcePreflightPassed=True,uid=UID,faces=15614,genuineNonzeroBodies=93,exactZeroAreaFaces=[24,25],conditionalStructuralBodies=92,openingAssociatedBody=62)),flush=True);return
 assert args.manifest_sha256 and len(args.manifest_sha256)==64,'Root stable current manifest SHA required';assert not DOC.exists(),'Preserve completed or partial capture; use a new version on changed inputs';manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==args.manifest_sha256;current=read(manifest);installed={};catalogues=[ref(ROOT/'3d-viewer'/url)for url in current['officialModelCatalogues']]
 for url in current['officialModelCatalogues']:
  for e in read(ROOT/'3d-viewer'/url)['models']:assert e['uid']not in installed;installed[e['uid']]=e
 expectedRetained={'landsd/254491:0','landsd/255439:0','landsd/255647:0','landsd/256112:0','landsd/256114:0','landsd/255438:0'};assert UID not in installed and expectedRetained<=set(installed)
 entry=row['candidate']['entry'];assert entry['sha256']==digest(raw)and not entry.get('footprintScope')and not entry.get('suppressesBuildingUids');asset=LOCAL/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
 lo,hi=tri.min((0,1)),tri.max((0,1));bounds=[float(lo[0]-30),float(lo[2]-30),float(hi[0]+30),float(hi[2]+30)];final=module('block17_current_forms','xl-final-script-pass.py')
 for u in sorted(expectedRetained):
  bb=installed[u]['worldBounds'];bounds=[min(bounds[0],bb[0][0]-30),min(bounds[1],bb[0][2]-30),max(bounds[2],bb[1][0]+30),max(bounds[3],bb[1][2]+30)]
 forms=final.load_forms(bounds);form,_,tile=next(x for x in forms if x[0]['uid']==UID);assert form['buildingCSUID']==row['source']['building']['buildingCSUID'];row['source']=dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()));row['candidate']={**row['candidate'],'path':str(asset.relative_to(ROOT))};context=dict(uid=UID,sourceSHA256=digest(raw),identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms});identity=verify_files(row,context,LOCAL/'identity-current')
 save(DOC/'selection.json.gz',dict(rows=[row],batch=BATCH,manifestSHA256=start['sha256']));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'identity-proofs.json',dict(rows=[identity]));save(DOC/'terrain-candidates.json',[])
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[entry],counts=dict(packedModels=1)));save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']})
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[],existingNative=f['uid']in installed or bool(f.get('modelGeometry')))for f,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms},candidateIds=[UID],patches=[]))
 save(DOC/'source-preflight.json',dict(currentManifest=start,currentCatalogueRefs=catalogues,sourceBinding=stream,completeOriginalSourceNonzeroBodies=93,completeOriginalZeroAreaFaces=[24,25],completeConditionalStructuralBodyCount=92,originalOpeningAssociatedBody=62,priorExactSourceSelection=ref(selection),priorCompleteOriginalSourceGraph=ref(GRAPH/'diagnostic.json.gz'),currentRelevantInstalledNativeUIDs=sorted(f['uid']for f,_,_ in forms if f['uid']in installed),requiredRetainedNativeUIDs=sorted(expectedRetained),historicalHeldReasonsPreserved=['ground-contact-unresolved','sampled-ground-gap-below-model-bottom','terrain-regresses-neighbour:landsd/256120:0'],completeOriginalWorldSHA256=digest(tri.tobytes()),installedBlock6Receipt=ref(B/'government-xl-parkview-block6-unchanged-installed-v1-20261011/result.json'),completeCurrentForeignFormScope=len(forms),modelGeometryChanges=0,terrainGeometryChanges=0,publication=False))
 rel=lambda p:str(p.relative_to(ROOT))
 def call(args,allowed=(0,)):
  assert subprocess.run(args,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode in allowed;assert ref(manifest)==start
 call(['node',str(HERE/'parkview_block17_capture_module_closures_20261011.mjs'),rel(DOC)+'/'])
 if not (LOCAL/'runtime-geometry.json.gz').exists():call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 if not (DOC/'validation.json').exists():call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'parkview_block17_check_all_current_native_20261011.mjs'),rel(DOC)+'/'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');rt=runtime['rows'][0];index=np.asarray(rt['index']).reshape(-1,3);drawn=np.asarray(rt['position']).reshape(-1,3)[index];ground=np.asarray(rt['drawnGroundGeometry']).reshape(-1,3,3);assert drawn.shape==tri.shape
 f=final.foundation_context(drawn,ground,Polygon(form['rings'][0],form['rings'][1:]));foundation=dict(uid=UID,foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0);save(DOC/'foundation.json',dict(rows=[foundation]));metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');m=metrics['rows'][0];resolution=resolve_global_bottom_warning(validation['results'][0],m,foundation);save(DOC/'diagnostic-resolutions.json',dict(rows=[resolution]));policy=module('block17_current_policy','acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=digest(raw),identityProof=identity.get('proof')),m,metrics['profiles']['mobile']);native=read(DOC/'native-neighbour-checks.json');reasons+=['native:'+u for u in sorted(set(native['blocked'])-set(native['resolved']))];reasons+=resolution['remaining'];
 if not identity['passed']:reasons.append('current-identity')
 if not foundation['strictFoundationAccepted']:reasons.append('whole-source-foundation')
 save(DOC/'current-raw-outcome.json',dict(uid=UID,reasons=sorted(set(reasons)),currentManifest=start,identityPassed=identity['passed'],completeOriginalFaces=15614,completeCurrentDrawnGroundFaces=len(ground),completeCurrentDrawnGroundSHA256=digest(ground.tobytes()),completeLiteralSHA256=digest(drawn.tobytes()),completeOriginalWorldSHA256=digest(tri.tobytes()),rawNativeBlocked=native['blocked'],rawNativeResolved=native['resolved'],installationApproved=False,currentAcceptance=False,newlyInstalled=0))
 save(DOC/'literal-source-inputs.json.gz',dict(rows=[dict(uid=UID,path=row['candidate']['path'],entry=entry,building=form)],currentManifest=start,currentCatalogueRefs=catalogues,evidenceRefs=[ref(DOC/'selection.json.gz'),ref(asset)]));call(['node',str(HERE/'parkview_block17_actual_render_attributes_20261011.mjs'),rel(DOC/'literal-source-inputs.json.gz'),rel(DOC/'actual-render-geometry.json.gz')])
 call(['node',str(HERE/'parkview_block17_capture_module_closures_20261011.mjs'),rel(DOC)+'/','--verify'])
 for p,h in runtime['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 assert ref(manifest)==start
 print(json.dumps(dict(identity=identity['passed'],groundFaces=len(ground),reasons=sorted(set(reasons)),freshFourStreamCapture=True)),flush=True)
if __name__=='__main__':main()
