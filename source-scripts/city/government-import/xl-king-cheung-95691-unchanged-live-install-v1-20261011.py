"""Root-only guarded King original publication after source/stage closure.

Full current replay precedes the approved-pending ledger row. Post-apply checks
bind the honest sole-catalogue delta, never temporarily restore the manifest.
"""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
UID='landsd/95691:0';MANIFEST_SHA='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43';PREVIOUS_SNAPSHOT='9fe6762f9efee79e'
BATCH='government-xl-king-cheung-95691-unchanged-installed-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def ready():
 with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100

def browser(stage,name):
 report=module('king_live_validator',HERE/'integrate.py').browser_verified(stage.DOC/name,{UID});views=[v for v in report['views']if 'time'in v]
 assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(UID,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}=={UID}
 return report

def owned(args,stage):
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();ready();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==MANIFEST_SHA
 role,entry,row=stage.recheck();assert role['currentTypedPhysicalAccepted'] and role['reasons']==[] and role['completeOriginalFaces']==18742 and role['completeOriginalRealComponents']==908 and not role['installationApproved']
 acceptance=read(stage.DOC/'acceptance.json');assert acceptance['passed'] and acceptance['checksPassed'] and not acceptance['publication'] and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['terrainGeometryChanges']==0
 assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser'];browser(stage,'staged-browser.json')
 for pin in acceptance['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 assert read(stage.STAGE/'catalogue.json')['models']==[entry] and not entry['supportDependencies'] and entry['proceduralWindows']is False
 assert ref(stage.STAGE/entry['asset'])['sha256']==entry['sha256'];plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==1 and plan['topLevelTerrainPatches']==[] and set(plan['areas'][0])=={'area','catalogue','destination'}
 original=json.loads(before);destination=plan['areas'][0]['destination'];assert not(ROOT/'3d-viewer'/destination).exists()
 previous=read(ROOT/args.previous_count);assert previous['counts']['total']==len(previous['rows'])==521
 fixed=next((r for r in previous['rows']if r['uid']==UID),None);assert fixed is None or not fixed['installedVerified']
 pins=[ref(Path(__file__)),ref(Path(stage.__file__)),ref(BROWSER),ref(ROOT/args.previous_count),ref(stage.ROLE/'result.json'),ref(stage.ROLE/'acceptance.json'),ref(stage.ROLE/'staged-original-entry.json'),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'plan.json'),ref(stage.STAGE/'catalogue.json'),ref(stage.STAGE/'browser-config.json')]
 required_source={ref(stage.ROLE/p)['path']for p in ['result.json','acceptance.json','staged-original-entry.json']};required_stage={ref(stage.DOC/p)['path']for p in ['acceptance.json','staged-browser.json']}|{ref(stage.STAGE/p)['path']for p in ['plan.json','catalogue.json','browser-config.json']}
 closures=[]
 for path in args.closure:
  cert=read(ROOT/path);assert cert['independentlyVerified'] and cert['currentManifestSHA256']==MANIFEST_SHA;closures.append(set(cert['paths']));pins.append(ref(ROOT/path))
 assert any(required_source<=s for s in closures) and any(required_stage<=s for s in closures)
 save(DOC/'complete-current-role.json',role);save(DOC/'original-entry.json',entry);save(DOC/'atomic-plan.json',plan)
 pins.extend(ref(DOC/p)for p in ['complete-current-role.json','original-entry.json','atomic-plan.json'])
 decision=dict(batch=BATCH,uids=[UID],sourceSHA256s={UID:entry['sha256']},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,evidenceRefs=pins,livePublicationRequired=True);save(DOC/'acceptance.json',decision)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(DOC/'atomic-plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]
 call(publication)
 # Do the final no-review current recheck BEFORE creating approved-pending.
 final,finalentry,_=stage.recheck();assert final==role and finalentry==entry and manifest.read_bytes()==before
 for pin in pins:assert ref(ROOT/pin['path'])==pin
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);pointer_before_bytes=pointer_path.read_bytes();assert pointer['snapshotId']==PREVIOUS_SNAPSHOT
 inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};prior=parts.get(UID,{})
 parts[UID]=dict(uid=UID,name=entry['label'],landmarkIds=prior.get('landmarkIds',[]),objectId=entry['objectId'],csuid=entry['buildingCSUID'],candidate=dict(sha256=entry['sha256']),sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-current-source-role',knownHold=False)
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
 save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Complete unchanged King Cheung18742 facets/908 components.714 positive-source envelope paths, three independently graded original ancillary canopy/post skins,177 full-boundary visual associations and14 reviewed named intrinsic roof/facade placements. Source visual parts give no roots/bridges or mechanical function claims. Original zero1149 retained. All current foreign/finite/foundation/runtime checks, source transforms and terrain preserved; no AI geometry modelling.'})
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
 ledger.record_many(snapshot,LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json','Complete source/current/stage pass; live pending.',commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 ready();owns();assert manifest.read_bytes()==before;LOCAL.mkdir(parents=True,exist_ok=True);(LOCAL/'manifest-before-installation.json').write_bytes(before)
 try:
  call(publication+['--apply']);call(['node',str(BROWSER),'live',ref(stage.STAGE/'browser-config.json')['path']]);browser(stage,'live-browser.json')
  expected={**original,'officialModelCatalogues':original['officialModelCatalogues']+[destination]};assert read(manifest)==expected
  current=read(ROOT/'3d-viewer'/destination);assert current==read(stage.STAGE/'catalogue.json') and current['models']==[entry]
  assert ref((ROOT/'3d-viewer'/destination).parent/entry['asset'])['sha256']==entry['sha256']
  # Every prior actual source/catalogue/tile/terrain/module hash remains exact.
  for path,h in role['completeCurrentInputHashes'].items():
   if path!='3d-viewer/city/data/manifest.json':assert digest((ROOT/path).read_bytes())==h
  for pin in role['completeCurrentCatalogueRefs']:assert ref(ROOT/pin['path'])==pin
  entries=[e for url in expected['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']];assert len(entries)==len({e['uid']for e in entries})==6643 and [e for e in entries if e['uid']==UID]==[entry]
 except BaseException:
  manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False,pendingLedgerHistoryPreserved=True));raise
 try:
  installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json')};save(DOC/'installed-acceptance.json',installed)
  ledger.record_many(snapshot,LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json','Unchanged whole original passes source/current/staged/live solid views, framing, picking/collision and failed-load retry; terrain untouched.',commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
  assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
  call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
  counts=read(DOC/'full-xl-current-count.json')['counts'];delta=int(fixed is not None);assert counts==dict(total=521,installedVerified=previous['counts']['installedVerified']+delta,remaining=previous['counts']['remaining']-delta)
  kind='king-complete-unchanged-source-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));lease=read(LEASE);job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
  result={**installed,'installedUids':[UID],'evidenceRefs':[ref(DOC/p)for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(stage.DOC/p)for p in ['staged-browser.json','live-browser.json']],'jobId':jid,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':counts}
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
 p=argparse.ArgumentParser();p.add_argument('--stage-script',required=True);p.add_argument('--previous-count',required=True);p.add_argument('--closure',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();stage=module('king_private_stage',ROOT/a.stage_script);assert stage.UID==UID
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned(a,stage)
 assert not DOC.exists()and len(a.closure)==2;ready();assert read(stage.DOC/'acceptance.json')['passed'];forms=read(stage.DOCS['input']/'complete-current-actual-source-and-ground.json.gz')['completeCurrentForms'];keys=sorted({'building:'+r['uid']for r in forms}|{'building:'+UID})
 claim=reservations.claim('king-live-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--stage-script',a.stage_script,'--previous-count',a.previous_count,'--owned']
 for c in a.closure:cmd.extend(['--closure',c])
 subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
