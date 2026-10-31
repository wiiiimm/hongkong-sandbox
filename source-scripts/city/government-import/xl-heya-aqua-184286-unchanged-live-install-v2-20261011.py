"""Root-only guarded Heya Aqua original publication after source/stage closure.

Full current replay precedes the approved-pending ledger row. Post-apply checks
bind the honest sole-catalogue delta, never temporarily restore the manifest.
"""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
from heya_aqua_exact_rollback_recovery_20261011 import verify_historical_completed_receipt,current_scene_and_history,ENTRY_APPROVAL,HISTORY,OLD
from heya_aqua_supplementary_recovery_camera_20261011 import supplementary
UID='landsd/184286:0';P='landsd/184285:0';MANIFEST_SHA='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6';PREVIOUS_SNAPSHOT='87728085a588c731'
BATCH='government-xl-heya-aqua-184286-unchanged-installed-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def ready():
 with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100

def browser(stage,name):
 report=module('heya_live_validator',HERE/'integrate.py').browser_verified(stage.DOC/name,{UID});views=[v for v in report['views']if 'time'in v]
 assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(UID,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 retained=report['retainedNativeOwnViews'];assert len(retained)==4 and {(v['uid'],v['width'],v['time'])for v in retained}=={(P,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 support=read(stage.DOCS['identity']/'installed-support-entry.json')['entry']
 assert all(v['sourceSHA256']==support['sha256']and v['originalTriangles']==3844 and v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0 for v in retained)
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}=={UID}
 return report

def owned(args,stage):
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();ready();preserved_history=current_scene_and_history();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==MANIFEST_SHA
 role,entry,row=stage.recheck(LOCAL/'initial-current-role-recheck');assert role['scriptChecksPassed'] and role['stagingReady'] and role['reasons']==[] and role['completeTypedOriginalRoleAccount']['completeOriginalFaces']==17910 and role['completeTypedOriginalRoleAccount']['completeOriginalComponents']==574 and not role['installationApproved']
 acceptance=read(stage.DOC/'acceptance.json');assert acceptance['passed'] and acceptance['checksPassed'] and not acceptance['publication'] and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['terrainGeometryChanges']==0
 assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser'];browser(stage,'staged-browser.json')
 for pin in acceptance['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 assert entry['sourceIdentityReviewed']is True and entry['publicationApproved']is True and entry['priority']=='approved-unchanged-original-root-reviewed'
 assert read(stage.STAGE/'catalogue.json')['models']==[entry] and len(entry['supportDependencies'])==1 and entry['supportDependencies'][0]['uid']==P and entry['supportDependencies'][0]['state']=='installed'
 assert ref(stage.STAGE/entry['asset'])['sha256']==entry['sha256'];plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==1 and plan['topLevelTerrainPatches']==[] and set(plan['areas'][0])=={'area','catalogue','destination'}
 original=json.loads(before);destination=plan['areas'][0]['destination'];assert not(ROOT/'3d-viewer'/destination).exists()
 previous=read(ROOT/args.previous_count);assert previous['counts']==dict(total=521,installedVerified=232,remaining=289)and len(previous['rows'])==521
 fixed=next((r for r in previous['rows']if r['uid']==UID),None);assert fixed is None or not fixed['installedVerified']
 pins=[ref(Path(__file__)),ref(Path(stage.__file__)),ref(BROWSER),ref(ROOT/args.previous_count),ref(stage.ROLE/'result.json'),ref(stage.ROLE/'complete-current-role.json.gz'),ref(stage.ROLE/'private-stage-entry.json'),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'plan.json'),ref(stage.STAGE/'catalogue.json'),ref(stage.STAGE/'browser-config.json'),ref(ENTRY_APPROVAL),ref(HISTORY),ref(OLD/'post-browser-failure-recovery.json'),ref(OLD/'installed-acceptance.json'),ref(stage.DOC/'supplementary/staged-browser.json')]
 required_source={ref(stage.ROLE/p)['path']for p in ['result.json','complete-current-role.json.gz','private-stage-entry.json']}|{ref(p)['path']for p in [ENTRY_APPROVAL,HISTORY,HERE/'heya_aqua_exact_rollback_recovery_20261011.py',HERE/'test_heya_aqua_exact_rollback_recovery_20261011.py',HERE/'xl-heya-aqua-exact-v1-rollback-factual-entry-recovery-v2-20261011.py',HERE/'heya_aqua_supplementary_recovery_camera_20261011.py',HERE/'xl-heya-aqua-retained-podium-high-camera-browser-v1-20261011.mjs',ROOT/'docs/astra-city/government-import/government-xl-heya-aqua-exact-v1-rollback-factual-entry-recovery-v2-20261011/result.json']};required_stage={ref(stage.DOC/p)['path']for p in ['acceptance.json','staged-browser.json','supplementary/staged-browser.json','supplementary-camera-config.json']}|{ref(stage.STAGE/p)['path']for p in ['plan.json','catalogue.json','browser-config.json']}
 closures=[]
 for path in args.closure:
  cert=read(ROOT/path);assert cert['independentlyVerified'] and cert['currentManifestSHA256']==MANIFEST_SHA;closures.append(set(cert['paths']));pins.append(ref(ROOT/path))
 assert any(required_source<=s for s in closures) and any(required_stage<=s for s in closures)
 save(DOC/'preserved-v1-rollback-history.json',preserved_history);save(DOC/'complete-current-role.json',role);save(DOC/'original-entry.json',entry);save(DOC/'atomic-plan.json',plan)
 pins.extend(ref(DOC/p)for p in ['complete-current-role.json','original-entry.json','atomic-plan.json','preserved-v1-rollback-history.json'])
 decision=dict(batch=BATCH,uids=[UID],sourceSHA256s={UID:entry['sha256']},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,evidenceRefs=pins,livePublicationRequired=True);save(DOC/'acceptance.json',decision)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(DOC/'atomic-plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]
 call(publication)
 # Do the final no-review current recheck BEFORE creating approved-pending.
 final,finalentry,_=stage.recheck(LOCAL/'final-current-role-recheck');assert final==role and finalentry==entry and manifest.read_bytes()==before
 for pin in pins:assert ref(ROOT/pin['path'])==pin
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);pointer_before_bytes=pointer_path.read_bytes();assert pointer['snapshotId']==PREVIOUS_SNAPSHOT
 inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};prior=parts.get(UID,{})
 parts[UID]=dict(uid=UID,name=entry['label'],landmarkIds=prior.get('landmarkIds',[]),objectId=entry['objectId'],csuid=entry['buildingCSUID'],candidate=dict(sha256=entry['sha256']),sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-current-source-role',knownHold=False)
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];assert snapshot!='fdab0ed5aee2a9cc';inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
 save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Complete unchanged Heya Aqua Tower1 original17910 facets/574 components:516 original attached-envelope components rooted through genuine current installed podium grade/exposed-original path;58 separately interpreted terminal facade visual components never supply roots/bridges. All85 proper original T/P crossings remain explicitly recorded as the reviewed exact source-owned lower-assembly join, without boundary-only, solid-clearance or engineering claims. Both old rim residuals/runtime negative history preserved. All current BASIC12 and installed-native6647 exclusions, full four-world finite/source identity/runtime checks retained. Installed podium184285 source/entry and all terrain unchanged; no AI geometry modelling.'})
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
 ledger.record_many(snapshot,LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json','Complete source/current/stage pass; live pending.',commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 ready();owns();assert manifest.read_bytes()==before;LOCAL.mkdir(parents=True,exist_ok=True);(LOCAL/'manifest-before-installation.json').write_bytes(before)
 try:
  call(publication+['--apply']);call(['node',str(BROWSER),'live',ref(stage.STAGE/'browser-config.json')['path']]);browser(stage,'live-browser.json');supplementary(stage,'live');owns()
  expected={**original,'officialModelCatalogues':original['officialModelCatalogues']+[destination]};assert read(manifest)==expected
  current=read(ROOT/'3d-viewer'/destination);assert current==read(stage.STAGE/'catalogue.json') and current['models']==[entry]
  assert ref((ROOT/'3d-viewer'/destination).parent/entry['asset'])['sha256']==entry['sha256']
  # Honest post-publication scene delta: only one appended catalogue/model.
  # Do not replay the old not-installed/current-manifest gate after apply.
  verify_historical_completed_receipt() # Exact archived historical proof, never old-current acceptance.
  support=read(stage.DOCS['identity']/'installed-support-entry.json')
  assert ref(ROOT/support['catalogue']['path'])==support['catalogue']and ref(ROOT/support['asset']['path'])==support['asset']
  assert [e for e in read(ROOT/support['catalogue']['path'])['models']if e['uid']==P]==[support['entry']]
  old_entries=[e for url in original['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']]
  entries=[e for url in expected['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']]
  assert len(old_entries)==len({e['uid']for e in old_entries})==6648 and all(e['uid']!=UID for e in old_entries)
  assert len(entries)==len({e['uid']for e in entries})==6649 and entries==old_entries+[entry]
 except BaseException:
  manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False,pendingLedgerHistoryPreserved=True));raise
 try:
  installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json'),'supplementaryLiveBrowser':ref(stage.DOC/'supplementary/live-browser.json'),'v1RollbackHistory':ref(DOC/'preserved-v1-rollback-history.json')};save(DOC/'installed-acceptance.json',installed)
  ledger.record_many(snapshot,LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json','Unchanged whole original passes source/current/staged/live original views, framing, picking/collision and failed-load retry; terrain untouched.',commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
  assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
  call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
  counts=read(DOC/'full-xl-current-count.json')['counts'];delta=int(fixed is not None);assert counts==dict(total=521,installedVerified=previous['counts']['installedVerified']+delta,remaining=previous['counts']['remaining']-delta)
  kind='heya-complete-unchanged-source-installed-v2';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));lease=read(LEASE);job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
  result={**installed,'installedUids':[UID],'evidenceRefs':[ref(DOC/p)for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(stage.DOC/p)for p in ['staged-browser.json','live-browser.json','supplementary/staged-browser.json','supplementary/live-browser.json']],'jobId':jid,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':counts}
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
   assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,UID)).fetchone()==('installed-verified',entry['sha256'])
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot,installedUids=[UID]));print(json.dumps(dict(installed=[UID],snapshotId=snapshot,jobId=jid)),flush=True)
 except BaseException as error:
  # Preserve all ledger events; restore the active pre-publication pointers and
  # log every best-effort recovery error rather than hide post-browser failure.
  recovery=dict(error=repr(error),phase='post-browser-ledger-progress-or-receipt',pendingAndInstalledLedgerHistoryPreserved=True,rootRecoveryAuditRequired=True,rollbackErrors=[])
  try:manifest.write_bytes(before);recovery['manifestRestoredSHA256']=digest(manifest.read_bytes())
  except BaseException as restore_error:recovery['rollbackErrors'].append(dict(step='manifest',error=repr(restore_error)))
  try:
   active=read(pointer_path);assert active==pointer or active['snapshotId']==snapshot
   pointer_path.write_bytes(pointer_before_bytes);recovery['sourcePointerRestoredSHA256']=digest(pointer_path.read_bytes())
  except BaseException as restore_error:recovery['rollbackErrors'].append(dict(step='source-review-pointer',error=repr(restore_error)))
  for command in [[sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'],['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]]:
   try:subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
   except BaseException as restore_error:recovery['rollbackErrors'].append(dict(step='progress-restoration',error=repr(restore_error)))
  save(DOC/'post-browser-failure-recovery.json',recovery);raise

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage-script',required=True);p.add_argument('--previous-count',required=True);p.add_argument('--closure',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();stage=module('heya_private_stage',ROOT/a.stage_script);assert stage.UID==UID
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned(a,stage)
 assert not DOC.exists()and len(a.closure)==2;assert stage.BATCH=='government-xl-heya-aqua-184286-unchanged-private-stage-v2-20261011'and ENTRY_APPROVAL.is_file();ready();assert read(stage.DOC/'acceptance.json')['passed'];forms=read(stage.DOCS['actual']/'capture-inputs.json.gz')['completeCurrentForms'];keys=sorted({'building:'+r['uid']for r in forms}|{'building:'+UID})
 claim=reservations.claim('heya-live-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--stage-script',a.stage_script,'--previous-count',a.previous_count,'--owned']
 for c in a.closure:cmd.extend(['--closure',c])
 subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
