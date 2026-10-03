"""Publish the verified four-part Ocean Park Marriott government assembly."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;BASE=s.DOC;DOC=BASE/'third-pass/ocean-park';LOCAL=s.LOCAL/'ocean-park-import';STAGE=HERE/'accepted/government-xxl-ocean-park-20260912';BATCH='government-xxl-ocean-park-20260912'
read,save,h,rel=s.read,s.save,s.h,s.rel
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
spec=importlib.util.spec_from_file_location('direct',HERE/'integrate.py');direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)
IDS={'landsd/136832:0','landsd/32681:0','landsd/34759:0','landsd/125385:0'}

def call(args):subprocess.run(args,cwd=ROOT,check=True)

def start():
 inputs=read(DOC/'neighbour-inputs.json.gz');resources={('building:' if r['building']['uid'].startswith('landsd/') else 'source-form:')+r['building']['uid'] for r in inputs['rows']}|{'building:'+uid for uid in IDS}
 claim=s.reservations.claim('codex-ocean-park-'+str(uuid.uuid4()),sorted(resources),batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
 receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt));cat=read(STAGE/'catalogue.json');assert {m['uid'] for m in cat['models']}==IDS
 browser=direct.browser_verified(DOC/'staged-browser.json',IDS);assert browser['passed']
 neighbours=read(DOC/'neighbour-checks.json');assert not neighbours['patches'][0]['blockedBy']
 validation=read(DOC/'validation.json');assert validation['loaderAccepted']==4 and validation['checksPassed']==4 and validation['exceptions']==0
 expected_concerns={'landsd/136832:0':['sampled-terrain-above-model-bottom'],'landsd/32681:0':['sampled-ground-gap-below-model-bottom'],'landsd/34759:0':['sampled-ground-gap-below-model-bottom'],'landsd/125385:0':['sampled-ground-gap-below-model-bottom']}
 assert {r['uid']:r['concerns'] for r in validation['results']}==expected_concerns
 for m in cat['models']:assert h(STAGE/m['asset'])==m['sha256']
 plan=read(STAGE/'plan.json');terrain=plan['topLevelTerrainPatches'][0];assert h(ROOT/terrain['source'])==terrain['sha256']
 selection=read(DOC/'selection.json.gz');assert {r['uid'] for r in selection['rows']}==IDS
 with s.connect() as c:
  c.execute('SET TRANSACTION READ ONLY');native=dict(c.execute('SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=ANY(%s)',([r['native']['cacheKey'] for r in selection['rows']],)));states=dict(c.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',(list(IDS),)))
 assert all(native[r['native']['cacheKey']]==r['native']['resultSha'] for r in selection['rows']);assert not any(v in ('held','source-unavailable','identity-unresolved','installed-verified') for v in states.values())
 evidence_paths=[DOC/'metrics.json',DOC/'validation.json',DOC/'neighbour-checks.json',DOC/'staged-browser.json',BASE/'third-pass/ocean-park-assembly-support.json',BASE/'third-pass/landsd-136832/native-overlap-evidence.json',HERE/'native_patch_resolution.py',HERE/'resolution-browser.mjs']
 evidence={rel(p):h(p) for p in evidence_paths};decision={'policy':'original-government-four-part-assembly-v1','uids':sorted(IDS),'catalogueSHA256':h(STAGE/'catalogue.json'),'planSHA256':h(STAGE/'plan.json'),'evidenceHashes':evidence,'aiCalls':0,'geometryChanges':0};save(DOC/'decision.json',decision)
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
 for m in cat['models']:
  old=parts.get(m['uid'],{});parts[m['uid']]={'uid':m['uid'],'name':m['label'],'landmarkIds':old.get('landmarkIds',[]),'objectId':m['objectId'],'csuid':m['buildingCSUID'],'candidate':{'sha256':m['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-assembly','knownHold':False}
 ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=s.digest(s.jobs.encode([ordered,decision]).encode())[:16];inv=pointer_path.parent/f'source-review-inventory-{snapshot}.json';save(inv,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered});ledger.seed(inv,inherit=pointer['snapshotId'])
 effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'decision.json')};commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();observation='Exact unchanged four-part Ocean Park Marriott government assembly; combined source terrain, per-model runtime budgets, neighbour regression, staged/live browser, picking, collision and fallback/retry checks. No AI modelling.'
 ledger.record_many(snapshot,receipt,[(uid,'approved-for-integration',DOC/'decision.json',observation,commit) for uid in sorted(IDS)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 pub=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(STAGE/'plan.json'),'--receipt',str(receipt),'--phase',BATCH];call(pub);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before.json').write_bytes(before);call(pub+['--apply'])
 try:call(['node',str(HERE/'resolution-browser.mjs'),'live',rel(STAGE/'browser-config.json')])
 except BaseException:manifest.write_bytes(before);raise
 direct.browser_verified(DOC/'live-browser.json',IDS);acceptance={**decision,'snapshot':snapshot,'liveBrowserSHA256':h(DOC/'live-browser.json'),'manifestSHA256':h(manifest)};save(DOC/'installed-acceptance.json',acceptance)
 ledger.record_many(snapshot,receipt,[(uid,'installed-verified',DOC/'installed-acceptance.json',observation,commit) for uid in sorted(IDS)],effort=effort,request_id=BATCH+'-installed-'+snapshot);assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inv),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
 call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);save(DOC/'summary.json',{'installedUids':sorted(IDS),'newXXLModels':1,'newSupportingModels':3,'snapshot':snapshot,'aiCalls':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')});print(json.dumps({'installed':sorted(IDS),'snapshot':snapshot,'aiCalls':0}))

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
