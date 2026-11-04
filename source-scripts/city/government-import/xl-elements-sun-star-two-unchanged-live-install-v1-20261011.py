"""Draft ROOT-ONLY two-original Elements installer. Never run by source agent.

Two full current replays precede approved-pending ledger events. One atomic
catalogue addition, exact prior6643 source/terrain preservation and all owned/
retained live views/retries precede installed credit. No terrain/native review.
"""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
UIDS={'landsd/204145:0','landsd/204143:0'};RETAINED={'landsd/273061:0','landsd/204144:0'};NATIVE='landsd/273061:0'
MANIFEST_SHA='de8db939e48be0ed3661a9f3bf59454d92ff27f4a1024f34a401b17612e03e54';PREVIOUS_SNAPSHOT='a5e3689739a0581e'
BATCH='government-xl-elements-sun-star-two-unchanged-installed-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
STAGE_SCRIPT=HERE/'xl-terrain-recovery-20261011-elements-sun-star-two-qualified-native-stage-v2.py';BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ready():
 with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100

def browser(stage,name,retained):
 report=module('elements_live_browser_validator',HERE/'integrate.py').browser_verified(stage.DOC/name,UIDS);assert report['passed']is True and report['errors']==[];views=[v for v in report['views']if 'time'in v]
 assert len(views)==8 and {(v['uid'],v['width'],v['time'])for v in views}=={(u,w,t)for u in UIDS for w in [1280,390]for t in ['15:00','22:00']}
 own=report['retainedNativeOwnViews'];assert len(own)==8 and {(v['uid'],v['width'],v['time'])for v in own}=={(u,w,t)for u in RETAINED for w in [1280,390]for t in ['15:00','22:00']}
 assert all(v['active']and v['visible']and v['fullyFramed']for v in own)
 for v in views:
  assert set(v['nativeSupports'])==RETAINED and v['nativeSupports'][NATIVE]['active']and v['nativeSupports'][NATIVE]['visible']
  for uid,w in v['nativeSupports'].items():
   entry=next(r['entry']for r in retained if r['uid']==uid);assert w['sourceSHA256']==entry['sha256']
   if w['wanted']:assert w['active']and w['visible']
 assert {v['uid']for v in report['views']if v.get('fallbackRetained')}==UIDS
 return report

def owned(args,stage):
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();ready();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==MANIFEST_SHA;original=json.loads(before)
 rows,identities,role=stage.recheck();assert role['currentTypedPhysicalAccepted']and role['reasons']==[]and role['completeOriginalFaces']==23809 and role['completeOriginalNonzeroBodies']==998 and not role['installationApproved']and not role['nativeReacceptance']and role['terrainProposal']==[]
 acceptance=read(stage.DOC/'acceptance.json');assert acceptance['passed']and acceptance['checksPassed']and not acceptance['publication']and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['terrainGeometryChanges']==0
 retained=role['retainedNativeExactEntries'];assert {r['uid']for r in retained}==RETAINED;assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser'];browser(stage,'staged-browser.json',retained)
 for pin in acceptance['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 catalogue=read(stage.STAGE/'catalogue.json');entries=catalogue['models'];assert {e['uid']for e in entries}==UIDS and len(entries)==2
 native=next(r['entry']for r in retained if r['uid']==NATIVE);dep=dict(uid=NATIVE,csuid=native['buildingCSUID'],sha256=native['sha256'],state='installed')
 for e in entries:assert e['supportDependencies']==[dep]and e['proceduralWindows']is False and not e.get('suppressesBuildingUids')and ref(stage.STAGE/e['asset'])['sha256']==e['sha256']
 plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==1 and plan['topLevelTerrainPatches']==[]and set(plan['areas'][0])=={'area','catalogue','destination'};destination=plan['areas'][0]['destination'];assert not(ROOT/'3d-viewer'/destination).exists()
 prior_entries={};prior_pins=[]
 for url in original['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url;prior_pins.append(ref(cp))
  for e in read(cp)['models']:assert e['uid']not in prior_entries;prior_entries[e['uid']]=e;prior_pins.append(ref(cp.parent/e['asset']))
 assert len(prior_entries)==6643 and not UIDS&set(prior_entries)
 for r in retained:assert prior_entries[r['uid']]==r['entry']and ref(ROOT/r['catalogue']['path'])==r['catalogue']and ref(ROOT/r['source']['path'])==r['source']
 previous=read(ROOT/args.previous_count);assert previous['counts']==dict(total=521,installedVerified=228,remaining=293)and len(previous['rows'])==521
 fixed={r['uid']:r for r in previous['rows']if r['uid']in UIDS};assert all(not r['installedVerified']for r in fixed.values());fixed_delta=len(fixed)
 pins=[ref(Path(__file__)),ref(STAGE_SCRIPT),ref(BROWSER),ref(ROOT/args.previous_count),ref(stage.ROLE/'result.json'),ref(stage.ROLE/'typed-role.json.gz'),ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'plan.json'),ref(stage.STAGE/'catalogue.json'),ref(stage.STAGE/'browser-config.json'),*prior_pins]
 required_source={ref(stage.ROLE/p)['path']for p in ['result.json','typed-role.json.gz']};required_stage={ref(stage.DOC/p)['path']for p in ['acceptance.json','staged-browser.json']}|{ref(stage.STAGE/p)['path']for p in ['plan.json','catalogue.json','browser-config.json']};closures=[]
 for path in args.closure:
  cert=read(ROOT/path);assert cert['independentlyVerified']and cert['currentManifestSHA256']==MANIFEST_SHA;closures.append(set(cert['paths']));pins.append(ref(ROOT/path))
 assert any(required_source<=s for s in closures)and any(required_stage<=s for s in closures)
 save(DOC/'complete-current-role.json.gz',role);save(DOC/'original-entries.json',entries);save(DOC/'atomic-plan.json',plan);pins.extend(ref(DOC/p)for p in ['complete-current-role.json.gz','original-entries.json','atomic-plan.json'])
 decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={e['uid']:e['sha256']for e in entries},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainGeometryChanges=0,nativeReacceptance=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=MANIFEST_SHA,evidenceRefs=pins,livePublicationRequired=True);save(DOC/'acceptance.json',decision)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(DOC/'atomic-plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH];call(publication)
 finalrows,finalidentities,final=stage.recheck();assert final==role and finalrows==rows and finalidentities==identities and manifest.read_bytes()==before
 for pin in pins:assert ref(ROOT/pin['path'])==pin
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);pointer_bytes=pointer_path.read_bytes();assert pointer['snapshotId']==PREVIOUS_SNAPSHOT;inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
 for e in entries:
  prior=parts.get(e['uid'],{});parts[e['uid']]=dict(uid=e['uid'],name=e['label'],landmarkIds=prior.get('landmarkIds',[]),objectId=e['objectId'],csuid=e['buildingCSUID'],candidate=dict(sha256=e['sha256']),sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-current-source-role',knownHold=False)
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json');save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Two complete unchanged Elements tower originals;23809 faces/998 nonzero bodies/all47 zeros retained.866 nonvisual exact exposed paths from12 bounded native grade-cap interfaces;132 named nonstructural original visual representations. Native actors remain availability-only, all raw negatives preserved; no geometry/terrain edits.'})
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
 ledger.record_many(snapshot,LEASE,[(u,'approved-for-integration',DOC/'acceptance.json','Complete source/current/stage pass; live pending.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 ready();owns();assert manifest.read_bytes()==before;LOCAL.mkdir(parents=True,exist_ok=True);(LOCAL/'manifest-before-installation.json').write_bytes(before)
 try:
  call(publication+['--apply']);call(['node',str(BROWSER),'live',ref(stage.STAGE/'browser-config.json')['path']]);browser(stage,'live-browser.json',retained)
  expected={**original,'officialModelCatalogues':original['officialModelCatalogues']+[destination]};assert read(manifest)==expected
  published=read(ROOT/'3d-viewer'/destination);assert published==catalogue
  for e in entries:assert ref((ROOT/'3d-viewer'/destination).parent/e['asset'])['sha256']==e['sha256']
  for pin in prior_pins:assert ref(ROOT/pin['path'])==pin
  for pin in role['evidenceRefs']:
   if pin['path']!='3d-viewer/city/data/manifest.json':assert ref(ROOT/pin['path'])==pin
  after={}
  for url in expected['officialModelCatalogues']:
   for e in read(ROOT/'3d-viewer'/url)['models']:assert e['uid']not in after;after[e['uid']]=e
  assert len(after)==6645 and {u:after[u]for u in prior_entries}==prior_entries and {u:after[u]for u in UIDS}=={e['uid']:e for e in entries}
  for r in retained:assert after[r['uid']]==r['entry']
 except BaseException:
  manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False,pendingLedgerHistoryPreserved=True));raise
 try:
  installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':2,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json')};save(DOC/'installed-acceptance.json',installed)
  ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Complete unchanged original passes current/source/staged/live solid views and retry; native/terrain unchanged.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
  assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
  call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH]);counts=read(DOC/'full-xl-current-count.json')['counts'];assert counts==dict(total=521,installedVerified=228+fixed_delta,remaining=293-fixed_delta)
  kind='elements-two-complete-unchanged-source-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));lease=read(LEASE);job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
  result={**installed,'installedUids':sorted(UIDS),'evidenceRefs':[ref(DOC/p)for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(stage.DOC/p)for p in ['staged-browser.json','live-browser.json']],'jobId':jid,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':counts}
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
   for e in entries:assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,e['uid'])).fetchone()==('installed-verified',e['sha256'])
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot,installedUids=sorted(UIDS)));print(json.dumps(dict(installed=sorted(UIDS),snapshotId=snapshot,jobId=jid)),flush=True)
 except BaseException as error:
  recovery=dict(error=repr(error),phase='post-browser-ledger-progress-or-receipt',pendingAndInstalledLedgerHistoryPreserved=True,rootRecoveryAuditRequired=True,rollbackErrors=[])
  try:manifest.write_bytes(before);recovery['manifestRestoredSHA256']=digest(manifest.read_bytes())
  except BaseException as e:recovery['rollbackErrors'].append(dict(step='manifest',error=repr(e)))
  try:
   active=read(pointer_path);assert active==pointer or active['snapshotId']==snapshot;pointer_path.write_bytes(pointer_bytes);recovery['sourcePointerRestoredSHA256']=digest(pointer_path.read_bytes())
  except BaseException as e:recovery['rollbackErrors'].append(dict(step='source-review-pointer',error=repr(e)))
  for cmd in [[sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'],['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]]:
   try:subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
   except BaseException as e:recovery['rollbackErrors'].append(dict(step='progress-restoration',error=repr(e)))
  save(DOC/'post-browser-failure-recovery.json',recovery);raise

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage-script',required=True);p.add_argument('--previous-count',required=True);p.add_argument('--closure',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert (ROOT/a.stage_script).resolve()==STAGE_SCRIPT.resolve();stage=module('elements_private_stage',STAGE_SCRIPT);assert stage.UIDS==UIDS and stage.RETAINED==RETAINED
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned(a,stage)
 assert not DOC.exists()and len(a.closure)==2;ready();assert read(stage.DOC/'acceptance.json')['passed'];forms=read(stage.PHYSICAL/'neighbour-inputs.json.gz')['rows'];keys=sorted({'building:'+r['building']['uid']for r in forms}|{'building:'+u for u in UIDS|RETAINED})
 claim=reservations.claim('elements-two-live-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--stage-script',a.stage_script,'--previous-count',a.previous_count,'--owned']
 for cert in a.closure:cmd.extend(['--closure',cert])
 subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
