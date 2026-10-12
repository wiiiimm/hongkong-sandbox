"""ROOT-only Nam original publication after complete source/stage closure.

Full current replay precedes the approved-pending ledger row. Post-apply checks
bind the honest sole-catalogue delta, never temporarily restore the manifest.
"""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
import nam_fung79099_unchanged_private_stage_draft_v1_20261013 as stage
UID=stage.UID;P=stage.P;MANIFEST_SHA='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
BATCH='government-xl-nam-fung79099-unchanged-installed-v1-20261013';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
BROWSER=stage.BROWSER
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def ready():
 with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100

def browser(stage,name):
 report=module('nam_live_validator',HERE/'integrate.py').browser_verified(stage.DOC/name,{UID});views=[v for v in report['views']if 'time'in v]
 assert len(views)==4 and {(v['uid'],v['width'],v['time'])for v in views}=={(UID,w,t)for w in [1280,390]for t in ['15:00','22:00']}
 for v in views:
  support=v['namBasicSupport'];assert support['actualSupportAvailable']and support['tileWanted']and support['fallbackFaces']==432 and not support['detailedActive']and not support['hidden'];assert support['sourceForm']==read(stage.STAGE/'browser-config.json')['namExactBasicSupport']['sourceForm'];assert support['buildingCSUID']=='3777116537P20060312'and support['tile']=='1_-1'
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}=={UID}
 return report

def owned(args,stage):
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();ready();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==MANIFEST_SHA
 receipt,role,entry,row,current_before,carrier,source_cert=stage.recheck(args);assert role['acceptanceReadyForStaging']and not role['remainingActualBlockers']and not role['installationApproved'];save(DOC/'initial-source-current-recheck.json',dict(qualification=ref(stage.R.Q.DOC/'qualification.json'),receipt=ref(stage.R.DOC/'result.json'),sourceCertificate=ref(source_cert)))
 acceptance=read(stage.DOC/'acceptance.json');assert acceptance['passed'] and not acceptance['publication'] and acceptance['newlyInstalled']==acceptance['sourceGeometryChanges']==acceptance['terrainGeometryChanges']==0
 assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser'];browser(stage,'staged-browser.json')
 assert entry['sourceIdentityReviewed']is True and entry['publicationApproved']is True
 assert read(stage.STAGE/'catalogue.json')['models']==[entry] and len(entry['supportDependencies'])==1 and entry['supportDependencies'][0]['uid']==P and entry['supportDependencies'][0]['state']=='surveyed-footprint-fallback'
 assert ref(stage.STAGE/entry['asset'])['sha256']==entry['sha256'];plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==1 and plan['topLevelTerrainPatches']==[] and set(plan['areas'][0])=={'area','catalogue','destination'}
 original=json.loads(before);destination=plan['areas'][0]['destination'];assert not(ROOT/'3d-viewer'/destination).exists()
 previous=read(ROOT/args.previous_count);assert previous['counts']==dict(total=521,installedVerified=233,remaining=288)and len(previous['rows'])==521
 fixed=next((r for r in previous['rows']if r['uid']==UID),None);assert fixed is None or not fixed['installedVerified']
 pins=[ref(Path(__file__)),ref(Path(stage.__file__)),ref(BROWSER),ref(ROOT/args.previous_count),ref(stage.R.DOC/'result.json'),ref(stage.R.Q.DOC/'qualification.json'),ref(stage.R.Q.DOC/'proposed-staged-entry.json'),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'plan.json'),ref(stage.STAGE/'catalogue.json'),ref(stage.STAGE/'browser-config.json'),ref(source_cert)]
 required_source={ref(stage.R.DOC/'result.json')['path'],ref(stage.R.Q.DOC/'qualification.json')['path'],ref(stage.R.Q.DOC/'proposed-staged-entry.json')['path']}
 required_stage={ref(stage.DOC/p)['path']for p in ['acceptance.json','staged-browser.json']}|{ref(stage.STAGE/p)['path']for p in ['plan.json','catalogue.json','browser-config.json']}
 closures=[]
 for path in args.closure:
  cert=read(ROOT/path);assert cert['independentlyVerified'] and cert['currentManifestSHA256']==MANIFEST_SHA;closures.append(set(cert['paths']));pins.append(ref(ROOT/path))
 assert any(required_source<=s for s in closures) and any(required_stage<=s for s in closures)
 save(DOC/'complete-current-role.json',role);save(DOC/'original-entry.json',entry);save(DOC/'atomic-plan.json',plan);pins.extend(ref(DOC/p)for p in ['complete-current-role.json','original-entry.json','atomic-plan.json'])
 decision=dict(batch=BATCH,uids=[UID],sourceSHA256s={UID:entry['sha256']},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,evidenceRefs=pins,livePublicationRequired=True);save(DOC/'acceptance.json',decision)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(DOC/'atomic-plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]
 call(publication)
 # Do the final no-review current recheck BEFORE creating approved-pending.
 _,final,finalentry,_,_,_,_=stage.recheck(args);assert final==role and finalentry==entry and manifest.read_bytes()==before
 for pin in pins:assert ref(ROOT/pin['path'])==pin
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);pointer_before_bytes=pointer_path.read_bytes();assert pointer['snapshotId']==args.expected_main_snapshot
 inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};prior=parts.get(UID,{})
 parts[UID]=dict(uid=UID,name=entry['label'],landmarkIds=prior.get('landmarkIds',[]),objectId=entry['objectId'],csuid=entry['buildingCSUID'],candidate=dict(sha256=entry['sha256']),sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-current-source-role',knownHold=False)
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
 save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Complete unchanged Nam Fung original13061 facets/569 components/75 authored zeros. Exact actual BASIC45779 availability-only support:41 qualified main1601-face body0 interfaces and109 grade/cap routes;457 complete source assembly paths and112 ROOT-reviewed descriptive terminal facade/roof details nonbridging. All four-world finite/identity/current6649 native/runtime/neighbour/foundation checks pass. BASIC325 ordinary warnings remain retained without whole-BASIC reapproval. Original government podium45779 remains held/unpublished. No source/pose/terrain edits or AI geometry modelling.'})
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
 ledger.record_many(snapshot,LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json','Complete source/current/stage pass; live pending.',commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 ready();owns();assert manifest.read_bytes()==before;LOCAL.mkdir(parents=True,exist_ok=True);(LOCAL/'manifest-before-installation.json').write_bytes(before)
 try:
  call(publication+['--apply']);call(['node',str(BROWSER),'live',ref(stage.STAGE/'browser-config.json')['path']]);browser(stage,'live-browser.json');owns()
  expected={**original,'officialModelCatalogues':original['officialModelCatalogues']+[destination]};assert read(manifest)==expected
  current=read(ROOT/'3d-viewer'/destination);assert current==read(stage.STAGE/'catalogue.json') and current['models']==[entry]
  assert ref((ROOT/'3d-viewer'/destination).parent/entry['asset'])['sha256']==entry['sha256']
  # Honest post-publication scene delta: only one appended catalogue/model.
  # Do not replay the old not-installed/current-manifest gate after apply.
  # Honest after-apply proof: skip only the intentionally changed manifest.
  scope=read(stage.R.Q.Q.CAP/'capture-scope.json');native_inventory=read(stage.R.Q.NATIVE/'inventory.json.gz');postpins={**scope['inputHashes'],**native_inventory['inputHashes']}
  for path,h in postpins.items():
   if path!='3d-viewer/city/data/manifest.json':assert digest((ROOT/path).read_bytes())==h,path
  assert all(entry['uid']!=P for url in expected['officialModelCatalogues']for entry in read(ROOT/'3d-viewer'/url)['models']);assert carrier==read(stage.R.Q.Q.CAP/'complete-current-forms.json.gz')['rows'][next(i for i,r in enumerate(read(stage.R.Q.Q.CAP/'complete-current-forms.json.gz')['rows'])if r['building']['uid']==P)]['building']
  old_entries=[e for url in original['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']]
  entries=[e for url in expected['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']]
  assert len(old_entries)==len({e['uid']for e in old_entries})==6649 and all(e['uid']!=UID for e in old_entries)
  assert len(entries)==len({e['uid']for e in entries})==6650 and entries==old_entries+[entry]
 except BaseException:
  manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False,pendingLedgerHistoryPreserved=True));raise
 try:
  installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json')};save(DOC/'installed-acceptance.json',installed)
  ledger.record_many(snapshot,LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json','Unchanged whole original passes source/current/staged/live original views, framing, picking/collision and failed-load retry; terrain untouched.',commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
  assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
  call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
  counts=read(DOC/'full-xl-current-count.json')['counts'];delta=int(fixed is not None);assert delta==1 and counts==dict(total=521,installedVerified=234,remaining=287)
  kind='nam-complete-unchanged-source-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));lease=read(LEASE);job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
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
 p=argparse.ArgumentParser();p.add_argument('--previous-count',required=True);p.add_argument('--expected-main-snapshot',required=True);p.add_argument('--expected-result-sha',required=True);p.add_argument('--source-certificate',required=True);p.add_argument('--expected-source-certificate-sha',required=True);p.add_argument('--closure',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned(a,stage)
 assert not DOC.exists()and len(a.closure)==2;ready();assert read(stage.DOC/'acceptance.json')['passed'];_,_,_,_,before,_,_=stage.recheck(a)
 claim=reservations.claim('nam-live-'+str(uuid.uuid4()),['building:'+u for u in before['uids']],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
