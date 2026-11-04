"""Install the final compute-only XL-50 group after deterministic terrain and runtime review."""
import collections,importlib.util,json,os,shutil,subprocess,sys,uuid
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xl-second-pass.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;read,save,h,rel=s.read,s.save,s.h,s.rel
BATCH='government-xl-held-terrain-20260914'
CHECK=ROOT/'docs/astra-city/government-import/government-xl-50-20260913/final-compute-pass/terrain-complete'
LOCAL=s.LOCAL/'held-terrain-install';STAGE=HERE/'accepted'/BATCH;DOC=CHECK/'installation'
UIDS=['landsd/273000:0','landsd/100745:0','landsd/225173:0','landsd/266063:0','landsd/224024:0','landsd/232096:0','landsd/185148:0','landsd/258884:0','landsd/233970:0','landsd/228431:0','landsd/295518:0']
CHROME='/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'

sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
spec=importlib.util.spec_from_file_location('direct',HERE/'integrate.py')
direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)

def call(args):
 env={**os.environ,'CHROME_PATH':CHROME}
 subprocess.run(args,cwd=ROOT,check=True,env=env)

def start():
 result=read(CHECK/'result.json')
 assert result['passed'] and result['models']==len(UIDS) and result['terrainPatches']==9
 claim=s.reservations.claim('codex-xl-held-terrain-import-'+str(uuid.uuid4()),['building:'+uid for uid in UIDS],ttl=1800,batch=BATCH)
 assert claim['ok']
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
 receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt))
 result=read(CHECK/'result.json')
 assert result=={**result,'passed':True}
 assert result['models']==len(UIDS) and result['terrainPatches']==9
 assert result['failures']==[] and result['unresolvedNeighbours']==[]
 assert result['aiCalls']==result['modelGeometryChanges']==0 and result['publication'] is False

 catalogue=read(STAGE/'catalogue.json');models={m['uid']:m for m in catalogue['models']}
 assert list(models)==UIDS and all(h(STAGE/m['asset'])==m['sha256'] for m in catalogue['models'])

 metrics=read(CHECK/'metrics.json')
 assert {r['uid'] for r in metrics['rows']}==set(UIDS)
 assert metrics['aiCalls']==metrics['geometryChanges']==0 and metrics['architectureReconstruction'] is False
 assert all(r['sourcePreserved'] and not r['missingTerrain'] and r['budget']['residentBytes']<=metrics['profiles']['mobile']['residentBytes'] for r in metrics['rows'])

 validation=read(CHECK/'validation.json')
 assert validation['models']==validation['loaderAccepted']==len(UIDS)
 assert validation['checksPassed']==10 and validation['exceptions']==1
 exceptions=[r for r in validation['results'] if r.get('outcome')=='validation-exception']
 assert exceptions==[{'uid':'landsd/295518:0','outcome':'validation-exception','loaderAccepted':True,'error':'Sampler differs from rendered terrain or overlapping surfaces disagree'}]
 overlap=read(CHECK/'ocean-square-overlap-resolution.json')
 assert overlap['accepted'] and overlap['uid']=='landsd/295518:0' and overlap['validationError']==exceptions[0]['error']
 assert overlap['aiCalls']==overlap['modelGeometryChanges']==0

 assembly=read(CHECK/'assembly-map.json')
 assert {r['uid'] for r in assembly['rows']}==set(UIDS) and assembly['aiCalls']==assembly['modelGeometryChanges']==0
 neighbours=read(CHECK/'neighbour-checks.json')
 assert neighbours['aiCalls']==0 and not [r for r in neighbours['rows'] if r.get('flags')]
 native=read(CHECK/'native-neighbour-checks.json')
 assert native['aiCalls']==native['modelGeometryChanges']==0 and len(native['rows'])==4
 assert all(r['passed'] and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['rows'])
 direct.browser_verified(CHECK/'staged-browser.json',set(UIDS))

 plan=read(STAGE/'plan.json');patches=plan['topLevelTerrainPatches']
 assert len(patches)==9 and sum('replaces' in p for p in patches)==2
 for patch in patches:
  assert h(ROOT/patch['source'])==patch['sha256']
  if 'replaces' in patch:
   review=patch['nativeReview'];decision=read(ROOT/review['path'])
   assert h(ROOT/review['path'])==review['sha256'] and decision['aiCalls']==decision['modelGeometryChanges']==0

 decision={
  'policy':'Install unchanged exact government models after deterministic identity, assembly, source terrain, retained-neighbour, runtime and browser acceptance.',
  'uids':UIDS,'sourceSHA256s':{uid:models[uid]['sha256'] for uid in UIDS},
  'catalogueSHA256':h(STAGE/'catalogue.json'),'planSHA256':h(STAGE/'plan.json'),
  'resultSHA256':h(CHECK/'result.json'),'assemblyMapSHA256':h(CHECK/'assembly-map.json'),
  'metricsSHA256':h(CHECK/'metrics.json'),'validationSHA256':h(CHECK/'validation.json'),
  'neighbourChecksSHA256':h(CHECK/'neighbour-checks.json'),'nativeNeighbourChecksSHA256':h(CHECK/'native-neighbour-checks.json'),
  'parentPreservationSHA256':h(CHECK/'parent-preservation.json'),'overlapResolutionSHA256':h(CHECK/'ocean-square-overlap-resolution.json'),
  'stagedBrowserSHA256':h(CHECK/'staged-browser.json'),'aiCallsThisImport':0,'geometryChanges':0
 }
 save(DOC/'decision.json',decision)

 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
 pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
 for uid in UIDS:
  model=models[uid];previous=parts.get(uid,{})
  parts[uid]={'uid':uid,'name':model['label'],'landmarkIds':previous.get('landmarkIds',[]),'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-terrain-complete','knownHold':False}
 ordered=sorted(parts.values(),key=lambda row:row['uid'])
 snapshot=s.digest(s.jobs.encode([ordered,decision]).encode())[:16]
 inventory_path=pointer_path.parent/f'source-review-inventory-{snapshot}.json'
 save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Eleven unchanged XL government sources accepted by deterministic identity, assembly, exact terrain, retained-neighbour, runtime and browser gates; no AI review or model geometry edits.'})
 ledger.seed(inventory_path,inherit=pointer['snapshotId'])

 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'decision.json')}
 by_assembly={r['uid']:r for r in assembly['rows']}
 observations={uid:f"Exact unchanged government source installed after deterministic identity, assembly, source-terrain, full-mesh neighbour, mobile runtime and staged/live browser checks. {len(by_assembly[uid]['suppressions'])} covered low fallback forms are reversibly suppressed and {len(by_assembly[uid]['retainedForms'])} adjacent or support forms remain visible. No AI modelling, review, simplification or model geometry edit." for uid in UIDS}
 ledger.record_many(snapshot,receipt,[(uid,'approved-for-integration',DOC/'decision.json',observations[uid],commit) for uid in UIDS],effort=effort,request_id=BATCH+'-approved-'+snapshot)

 publish=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(STAGE/'plan.json'),'--receipt',str(receipt),'--phase',BATCH]
 call(publish)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before.json').write_bytes(before)
 call(publish+['--apply'])
 new_catalogue=ROOT/'3d-viewer/city/data/official-models'/BATCH
 new_terrain=[ROOT/'3d-viewer'/p['destination'] for p in patches]
 try:
  call(['node',str(HERE/'resolution-browser.mjs'),'live',rel(STAGE/'browser-config.json')])
  direct.browser_verified(CHECK/'live-browser.json',set(UIDS))
 except BaseException:
  manifest.write_bytes(before)
  shutil.rmtree(new_catalogue,ignore_errors=True)
  shutil.rmtree(ROOT/'docs/astra-city/model-integration-20260909'/BATCH,ignore_errors=True)
  for p in new_terrain:p.unlink(missing_ok=True)
  raise

 acceptance={**decision,'snapshot':snapshot,'liveBrowserSHA256':h(CHECK/'live-browser.json'),'manifestSHA256':h(manifest)}
 save(DOC/'installed-acceptance.json',acceptance)
 ledger.record_many(snapshot,receipt,[(uid,'installed-verified',DOC/'installed-acceptance.json',observations[uid],commit) for uid in UIDS],effort=effort,request_id=BATCH+'-installed-'+snapshot)
 assert read(pointer_path)==pointer
 save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inventory_path),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
 call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'])
 call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])

 with direct.connect() as con:
  con.execute('SET TRANSACTION READ ONLY')
  rows=con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,UIDS)).fetchall()
 state_by_uid=dict(rows);assert set(state_by_uid)==set(UIDS) and set(state_by_uid.values())=={'installed-verified'}
 neon={'snapshot':snapshot,'states':dict(collections.Counter(state_by_uid.values())),'inProcess':0,'uids':state_by_uid,'verified':True}
 save(DOC/'neon-sync.json',neon)
 progress=read(ROOT/'3d-viewer/city/data/building-progress.json')
 summary={'installedUids':UIDS,'installed':len(UIDS),'originalHeldResolved':31,'xlBatchInstalled':50,'xlBatchHeld':0,'terrainPatches':9,'snapshot':snapshot,'neonVerified':True,'inProcess':0,'aiCalls':0,'geometryChanges':0,'progress':progress}
 save(DOC/'summary.json',summary)
 print(json.dumps(summary),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
