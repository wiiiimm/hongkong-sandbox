"""Publish the script-verified XL surface-clear group; no AI or geometry edits."""
import collections,importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;read,save,h,rel=s.read,s.save,s.h,s.rel
BATCH='government-xl-held-surface-20260914';CHECK=ROOT/'docs/astra-city/government-import/government-xl-50-20260913/final-compute-pass/surface-clear';LOCAL=s.LOCAL/'held-surface-install';STAGE=HERE/'accepted'/BATCH;DOC=CHECK/'installation'
UIDS=['landsd/270867:0','landsd/148321:0','landsd/253890:0','landsd/253891:0','landsd/270427:0','landsd/21915:0','landsd/109530:0','landsd/337014:0','landsd/304700:0','landsd/307295:0','landsd/229481:0','landsd/175935:0','landsd/60113:0']
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
spec=importlib.util.spec_from_file_location('direct',HERE/'integrate.py');direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)
def call(args):subprocess.run(args,cwd=ROOT,check=True)
def start():
 result=read(CHECK/'result.json');assert result['passed'] and result['models']==len(UIDS)
 claim=s.reservations.claim('codex-xl-held-surface-import-'+str(uuid.uuid4()),['building:'+uid for uid in UIDS],batch=BATCH);assert claim['ok']
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])
def owned():
 receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt))
 result=read(CHECK/'result.json');assert result['passed'] and result['models']==len(UIDS) and result['failures']==[] and result['aiCalls']==result['modelGeometryChanges']==0
 catalogue=read(STAGE/'catalogue.json');assert [m['uid'] for m in catalogue['models']]==UIDS and all(h(STAGE/m['asset'])==m['sha256'] for m in catalogue['models'])
 metrics=read(CHECK/'metrics.json');assert {r['uid'] for r in metrics['rows']}==set(UIDS) and all(r['sourcePreserved'] and not r['missingTerrain'] and r['budget']['residentBytes']<=metrics['profiles']['mobile']['residentBytes'] for r in metrics['rows'])
 validation=read(CHECK/'validation.json');assert validation['loaderAccepted']==validation['checksPassed']==len(UIDS) and validation['exceptions']==0
 assembly=read(CHECK/'assembly-map.json');assert {r['uid'] for r in assembly['rows']}==set(UIDS) and assembly['aiCalls']==assembly['modelGeometryChanges']==0
 direct.browser_verified(CHECK/'staged-browser.json',set(UIDS))
 decision={'policy':result['policy'],'uids':UIDS,'sourceSHA256s':{m['uid']:m['sha256'] for m in catalogue['models']},'catalogueSHA256':h(STAGE/'catalogue.json'),'planSHA256':h(STAGE/'plan.json'),'resultSHA256':h(CHECK/'result.json'),'assemblyMapSHA256':h(CHECK/'assembly-map.json'),'metricsSHA256':h(CHECK/'metrics.json'),'validationSHA256':h(CHECK/'validation.json'),'stagedBrowserSHA256':h(CHECK/'staged-browser.json'),'aiCallsThisImport':0,'geometryChanges':0};save(DOC/'decision.json',decision)
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};models={m['uid']:m for m in catalogue['models']}
 for uid in UIDS:
  model=models[uid];previous=parts.get(uid,{});parts[uid]={'uid':uid,'name':model['label'],'landmarkIds':previous.get('landmarkIds',[]),'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-surface-clear','knownHold':False}
 ordered=sorted(parts.values(),key=lambda row:row['uid']);snapshot=s.digest(s.jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/f'source-review-inventory-{snapshot}.json';save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Thirteen unchanged government XL sources accepted through exact identity, complete terrain, assembly, runtime and browser checks; no AI review or geometry edits.'});ledger.seed(inventory_path,inherit=pointer['snapshotId'])
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'decision.json')}
 by_assembly={r['uid']:r for r in assembly['rows']};observations={uid:f"Exact unchanged government source. Complete terrain/foundation and mobile budget checks passed. {len(by_assembly[uid]['suppressions'])} covered low basic forms are reversibly suppressed and {len(by_assembly[uid]['retainedForms'])} adjacent/taller forms remain visible. Staged/live desktop and mobile day/night, picking, collision, fallback and retry checks passed. No AI modelling, review or geometry edits." for uid in UIDS}
 ledger.record_many(snapshot,receipt,[(uid,'approved-for-integration',DOC/'decision.json',observations[uid],commit) for uid in UIDS],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 publish=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(STAGE/'plan.json'),'--receipt',str(receipt),'--phase',BATCH];call(publish);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before.json').write_bytes(before);call(publish+['--apply'])
 try:call(['node',str(HERE/'resolution-browser.mjs'),'live',rel(STAGE/'browser-config.json')]);direct.browser_verified(CHECK/'live-browser.json',set(UIDS))
 except BaseException:
  manifest.write_bytes(before);shutil.rmtree(ROOT/'3d-viewer/city/data/official-models'/BATCH,ignore_errors=True);shutil.rmtree(ROOT/'docs/astra-city/model-integration-20260909'/BATCH,ignore_errors=True);raise
 acceptance={**decision,'snapshot':snapshot,'liveBrowserSHA256':h(CHECK/'live-browser.json'),'manifestSHA256':h(manifest)};save(DOC/'installed-acceptance.json',acceptance);ledger.record_many(snapshot,receipt,[(uid,'installed-verified',DOC/'installed-acceptance.json',observations[uid],commit) for uid in UIDS],effort=effort,request_id=BATCH+'-installed-'+snapshot)
 assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inventory_path),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]});call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
 save(DOC/'summary.json',{'installedUids':UIDS,'assemblyCounts':dict(collections.Counter(('suppressed' if r['suppressions'] else 'retained-only') for r in assembly['rows'])),'snapshot':snapshot,'aiCalls':0,'geometryChanges':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')});print(json.dumps({'installed':UIDS,'snapshot':snapshot,'aiCalls':0}),flush=True)
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
