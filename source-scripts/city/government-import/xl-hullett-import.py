"""Publish the verified unchanged Hullett House government compound."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;read,save,h,rel=s.read,s.save,s.h,s.rel
UID='landsd/73140:0';SUPPRESSED='landsd/211916:0';BATCH='government-xl-hullett-house-20260914'
CHECK=s.DOC/'third-pass/central-nested';STAGED=s.LOCAL/'third-pass-central-nested';LOCAL=s.LOCAL/'third-pass-central-nested-install';ACCEPTED=HERE/'accepted'/BATCH;DOC=s.DOC/'third-pass/central-nested-install'
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
direct_spec=importlib.util.spec_from_file_location('direct',HERE/'integrate.py');direct=importlib.util.module_from_spec(direct_spec);direct_spec.loader.exec_module(direct)
def call(args):subprocess.run(args,cwd=ROOT,check=True)
def start():
 result=read(CHECK/'result.json');assert result['passed'] and result['uids']==[UID] and result['aiCalls']==result['modelGeometryChanges']==0
 resources=read(STAGED/'reservation.json')['resources'];claim=s.reservations.claim('codex-xl-hullett-import-'+str(uuid.uuid4()),resources,batch=BATCH);assert claim['ok']
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])
def owned():
 receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt))
 result=read(CHECK/'result.json');assert result['passed'] and result['uids']==[UID] and not result['reasons'] and result['aiCalls']==result['modelGeometryChanges']==0
 selection=read(CHECK/'selection.json.gz');assert [row['uid'] for row in selection['rows']]==[UID];source=selection['rows'][0]
 suppression=read(CHECK/'assembly-suppression.json');assert suppression['aiCalls']==suppression['modelGeometryChanges']==0 and len(suppression['rows'])==1
 suppression_row=suppression['rows'][0];assert suppression_row['sourceUid']==UID and suppression_row['suppressedUid']==SUPPRESSED and suppression_row['footprintCoverage']>=.999 and suppression_row['sharedParentFields'] and suppression_row['nameContextAccepted']
 metrics=read(CHECK/'metrics.json');metric=metrics['rows'][0];assert metric['uid']==UID and metric['sourcePreserved'] and metric['missingTerrain']==0 and metric['maxSamplerDelta']<=.004 and metrics['aiCalls']==metrics['geometryChanges']==0
 foundation=read(CHECK/'foundation-resolution.json')['rows'][0];assert foundation['uid']==UID and foundation['accepted'] and foundation['completeFaceFoundation']['fullyBuriedUpwardTriangles']==0
 validation=read(CHECK/'validation.json');assert validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0 and set(validation['results'][0]['concerns'])<={'sampled-terrain-above-model-bottom'}
 neighbours=read(CHECK/'neighbour-checks.json');native=read(CHECK/'native-neighbour-checks.json');assert set(neighbours['patches'][0]['blockedBy'])-set(native['resolved'])-{SUPPRESSED}==set()
 source_catalogue=read(STAGED/'candidates/catalogue.json');assert [model['uid'] for model in source_catalogue['models']]==[UID];entry=dict(source_catalogue['models'][0])
 assert entry['suppressesBuildingUids']==[SUPPRESSED] and h(STAGED/'candidates'/entry['asset'])==entry['sha256']
 entry.update(priority='landmark',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,publicationApproved=True,proceduralWindows=False,placementReview='Exact unchanged Hullett House government compound matched by object ID and Building CSUID. Its source projection completely covers the same-parent 1881 Heritage fallback component, which the runtime suppresses only while this source is active. Exact nested terrain, neighbour, runtime, picking, collision and fallback checks pass.')
 asset=ACCEPTED/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(STAGED/'candidates'/entry['asset'],asset);assert h(asset)==entry['sha256']
 catalogue={**source_catalogue,'area':'Hullett House original government compound','loadingPolicy':'Published after deterministic source, terrain, neighbour, assembly-suppression, runtime and browser checks','models':[entry]};save(ACCEPTED/'catalogue.json',catalogue);save(ACCEPTED/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
 form=dict(source['source']['building']);form['tile']=Path(source['source']['tile']).stem;save(ACCEPTED/'source-forms.json',[form])
 patch=result['patch'];patch_source=ROOT/patch['path'];assert h(patch_source)==patch['sha256'];patch_destination=ACCEPTED/'terrain-central-with-hullett.json';shutil.copyfile(patch_source,patch_destination)
 review={'path':rel(CHECK/'terrain-resolution.json'),'sha256':h(CHECK/'terrain-resolution.json')}
 terrain={'source':rel(patch_destination),'sha256':h(patch_destination),'destination':'city/data/terrain-central-with-hullett.json','resolution':read(patch_destination)['cell'],'area':'Hullett House exact nested government terrain','replaces':patch['replaces'],'nativeReview':review}
 catalogue_url='city/data/official-models/'+BATCH+'/catalogue.json';plan={'areas':[{'area':catalogue['area'],'catalogue':rel(ACCEPTED/'catalogue.json'),'destination':catalogue_url}],'topLevelTerrainPatches':[terrain]};save(ACCEPTED/'plan.json',plan)
 browser={'stage':rel(ACCEPTED)+'/','doc':rel(DOC)+'/','catalogueURL':catalogue_url,'terrain':[terrain],'fitBox':True,'browserUids':[UID],'failureTestUids':[UID]};save(ACCEPTED/'browser-config.json',browser)
 evidence_paths=[CHECK/name for name in ('result.json','metrics.json','validation.json','foundation-resolution.json','identity-resolution.json','terrain-resolution.json','assembly-suppression.json','neighbour-checks.json','native-neighbour-checks.json')]+[HERE/'xl-stage-central-nested.py',HERE/'native_patch_resolution.py',HERE/'check-native-neighbours.mjs',HERE/'resolution-browser.mjs',HERE/'xl-hullett-import.py',ROOT/'3d-viewer/city/tests/official-models.test.js']
 inherited=read(CHECK/'inherited-overlap-rebind.json');evidence_paths.append(CHECK/'inherited-overlap-rebind.json');evidence_paths.extend(ROOT/row['reboundEvidencePath'] for row in inherited['rows'])
 evidence={rel(path):h(path) for path in evidence_paths};inputs={**metrics['inputHashes'],**neighbours['sourceInputHashes'],**native['inputHashes']}
 for path,sha in inputs.items():assert h(ROOT/path)==sha
 decision={'policy':result['policy'],'uid':UID,'suppressedFallbackUid':SUPPRESSED,'sourceSHA256':entry['sha256'],'catalogueSHA256':h(ACCEPTED/'catalogue.json'),'planSHA256':h(ACCEPTED/'plan.json'),'inputHashes':inputs,'evidenceHashes':evidence,'aiCalls':0,'modelGeometryChanges':0};save(DOC/'decision.json',decision)
 call(['node','--test','3d-viewer/city/tests/official-models.test.js','3d-viewer/city/tests/native-terrain.test.js','3d-viewer/city/tests/terrain-nested.test.js'])
 call(['node',str(HERE/'resolution-browser.mjs'),'staged',rel(ACCEPTED/'browser-config.json')]);direct.browser_verified(DOC/'staged-browser.json',{UID})
 for path,sha in {**inputs,**evidence}.items():assert h(ROOT/path)==sha
 with s.connect() as connection:
  connection.execute('SET TRANSACTION READ ONLY');rows=dict(connection.execute('SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(source['native']['cacheKey'],)))
 assert rows[source['native']['cacheKey']]==source['native']['resultSha']
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={part['uid']:part for part in inventory['parts']};previous=parts.get(UID,{})
 parts[UID]={'uid':UID,'name':entry['label'],'landmarkIds':previous.get('landmarkIds',[]),'objectId':entry['objectId'],'csuid':entry['buildingCSUID'],'candidate':{'sha256':entry['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-compound-with-nested-terrain','knownHold':False}
 ordered=sorted(parts.values(),key=lambda row:row['uid']);snapshot=s.digest(s.jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/f'source-review-inventory-{snapshot}.json';save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered});ledger.seed(inventory_path,inherit=pointer['snapshotId'])
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'decision.json')}
 observation='Exact unchanged Hullett House government compound. The active source suppresses one fully covered same-parent 1881 Heritage fallback and restores it on eviction. Exact nested terrain, neighbour, source integrity, runtime, staged/live browser, picking, collision and fallback/retry checks passed. No AI modelling, review or model geometry edits.'
 ledger.record_many(snapshot,receipt,[(UID,'approved-for-integration',DOC/'decision.json',observation,commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 publish=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(ACCEPTED/'plan.json'),'--receipt',str(receipt),'--phase',BATCH];call(publish)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before.json').write_bytes(before);terrain_live=ROOT/'3d-viewer'/terrain['destination'];terrain_existed=terrain_live.exists();terrain_before=terrain_live.read_bytes() if terrain_existed else None;call(publish+['--apply'])
 try:call(['node',str(HERE/'resolution-browser.mjs'),'live',rel(ACCEPTED/'browser-config.json')]);direct.browser_verified(DOC/'live-browser.json',{UID})
 except BaseException:
  manifest.write_bytes(before)
  if terrain_existed:terrain_live.write_bytes(terrain_before)
  elif terrain_live.exists():terrain_live.unlink()
  shutil.rmtree(ROOT/'3d-viewer/city/data/official-models'/BATCH,ignore_errors=True);shutil.rmtree(ROOT/'docs/astra-city/model-integration-20260909'/BATCH,ignore_errors=True);raise
 acceptance={**decision,'snapshot':snapshot,'stagedBrowserSHA256':h(DOC/'staged-browser.json'),'liveBrowserSHA256':h(DOC/'live-browser.json'),'manifestSHA256':h(manifest)};save(DOC/'installed-acceptance.json',acceptance)
 ledger.record_many(snapshot,receipt,[(UID,'installed-verified',DOC/'installed-acceptance.json',observation,commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot);assert read(pointer_path)==pointer
 save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inventory_path),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]});call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
 save(DOC/'summary.json',{'installedUids':[UID],'suppressedFallbackUid':SUPPRESSED,'snapshot':snapshot,'aiCalls':0,'modelGeometryChanges':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')});print(json.dumps({'installed':UID,'snapshot':snapshot,'aiCalls':0}),flush=True)
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
