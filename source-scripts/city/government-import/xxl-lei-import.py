"""Publish unchanged Lei Yue Mun Park Block 10 with its source-derived terrain."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;BASE=s.DOC;DOC=BASE/'lei-install';LOCAL=s.LOCAL/'lei-install';STAGE=HERE/'accepted/government-xxl-lei-20260912';UID='landsd/109467:0';BATCH='government-xxl-lei-20260912'
read,save,h,rel=s.read,s.save,s.h,s.rel
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
spec=importlib.util.spec_from_file_location('direct',HERE/'integrate.py');direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)

def call(args):subprocess.run(args,cwd=ROOT,check=True)

def start():
 inputs=read(DOC/'neighbour-inputs.json.gz');resources={('building:' if r['building']['uid'].startswith('landsd/') else 'source-form:')+r['building']['uid'] for r in inputs['rows']}|{'building:'+UID}
 claim=s.reservations.claim('codex-lei-import-'+str(uuid.uuid4()),sorted(resources),batch=BATCH);assert claim['ok'];save(LOCAL/'import-reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'import-reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
 receipt=LOCAL/'import-reservation.json';assert s.reservations.owns(read(receipt));cat=read(STAGE/'catalogue.json');assert [m['uid'] for m in cat['models']]==[UID];model=cat['models'][0];assert h(STAGE/model['asset'])==model['sha256']
 direct.browser_verified(DOC/'staged-browser.json',{UID});neighbours=read(DOC/'neighbour-checks.json');assert not neighbours['patches'][0]['blockedBy']
 validation=read(DOC/'validation.json');assert validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0
 assert validation['results'][0]['concerns']==['sampled-terrain-above-model-bottom','sampled-ground-gap-below-model-bottom']
 metrics=read(DOC/'metrics.json');metric=metrics['rows'][0];assert metric['uid']==UID and metric['sourcePreserved'] and not metric['missingTerrain']
 plan=read(STAGE/'plan.json');terrain=plan['topLevelTerrainPatches'][0];assert h(ROOT/terrain['source'])==terrain['sha256']
 source=next(r for r in read(BASE/'runtime-selection.json.gz')['rows'] if r['uid']==UID)
 with s.connect() as c:
  c.execute('SET TRANSACTION READ ONLY');native=c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(source['native']['cacheKey'],)).fetchone();state=c.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(UID,)).fetchone()
 assert native and native[0]==source['native']['resultSha'];assert not state or state[0]!='installed-verified'
 evidence_paths=[DOC/'metrics.json',DOC/'validation.json',DOC/'neighbour-checks.json',DOC/'staged-browser.json',HERE/'xxl-stage-lei.py',HERE/'resolution-browser.mjs']
 decision={'policy':'original-government-model-derived-terrain-v1','uid':UID,'catalogueSHA256':h(STAGE/'catalogue.json'),'planSHA256':h(STAGE/'plan.json'),'evidenceHashes':{rel(p):h(p) for p in evidence_paths},'terrainContext':'The government source spans a steep site. Model and derived terrain are unchanged; browser framing, picking and collision pass across desktop/mobile day/night.','aiCalls':0,'geometryChanges':0};save(DOC/'decision.json',decision)
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};old=parts.get(UID,{})
 parts[UID]={'uid':UID,'name':model['label'],'landmarkIds':old.get('landmarkIds',[]),'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-source','knownHold':False}
 ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=s.digest(s.jobs.encode([ordered,decision]).encode())[:16];inv=pointer_path.parent/f'source-review-inventory-{snapshot}.json';save(inv,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered});ledger.seed(inv,inherit=pointer['snapshotId'])
 effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'decision.json')};commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();observation='Exact unchanged Lei Yue Mun Park Block 10 government model with deterministic source-TIN-derived terrain. Eighteen neighbour guards, source preservation, loader, staged/live browser, picking, collision and fallback/retry checks pass. No AI modelling or geometry edits.'
 ledger.record_many(snapshot,receipt,[(UID,'approved-for-integration',DOC/'decision.json',observation,commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 pub=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(STAGE/'plan.json'),'--receipt',str(receipt),'--phase',BATCH];call(pub);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before.json').write_bytes(before);call(pub+['--apply'])
 try:call(['node',str(HERE/'resolution-browser.mjs'),'live',rel(STAGE/'browser-config.json')])
 except BaseException:manifest.write_bytes(before);raise
 direct.browser_verified(DOC/'live-browser.json',{UID});acceptance={**decision,'snapshot':snapshot,'liveBrowserSHA256':h(DOC/'live-browser.json'),'manifestSHA256':h(manifest)};save(DOC/'installed-acceptance.json',acceptance)
 ledger.record_many(snapshot,receipt,[(UID,'installed-verified',DOC/'installed-acceptance.json',observation,commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot);assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inv),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
 call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);save(DOC/'summary.json',{'installedUids':[UID],'snapshot':snapshot,'aiCalls':0,'geometryChanges':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')});print(json.dumps({'installed':UID,'snapshot':snapshot,'aiCalls':0}))

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
