"""Atomic original-assembly publication, live checks and installed ledger recording.

--prepare-only is read-only apart from its proposal receipt. Actual installation
requires idle predecessor workers and the publisher's exact current-map evidence.
"""
import argparse,hashlib,json,os,subprocess,sys,uuid,signal
from pathlib import Path
import kowloon_civic_guarded_publish_v2_20261030 as guard
from run import connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
from aqua_original_image_review_binding_v1_20261014 import MUTABLE_CURRENT as SHARED_MUTABLE_CURRENT
PROTECTED_SNAPSHOT='docs/astra-city/landmark-completion-audit/neon-snapshot.json'
MUTABLE_CURRENT=set(SHARED_MUTABLE_CURRENT)-{PROTECTED_SNAPSHOT}
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
stage=guard.stage;ROOT=guard.ROOT;HERE=guard.HERE;BASE=guard.BASE
read=stage.read;save=stage.save;ref=stage.ref;check=guard.check
BATCH=guard.BATCH;DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PUB=HERE/'kowloon_civic_guarded_publish_v2_20261030.py';BROWSER=HERE/'ronsdale_three_live_browser_v19_20261028.mjs'
FOCUSED=HERE/'ronsdale_three_live_browser_v19_20261028.mjs'
ATOMIC=HERE/'kowloon_civic_live_atomic_lifecycle_v1_20261030.mjs'
POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
DEFAULT_PREVIOUS=BASE/stage.CONFIG['previousCountReport']

def inventory_part(model,old):
 return dict(uid=model['uid'],name=model.get('label')or old.get('name')or model['uid'],landmarkIds=old.get('landmarkIds',[]),objectId=model['objectId'],csuid=model['buildingCSUID'],candidate=dict(sha256=model['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-source',knownHold=False)

def browser_config(width,focused=False):
 cfg=read(stage.STAGE/'live-browser-config.json');cfg['stage']=str(stage.STAGE.relative_to(ROOT))+'/';cfg['catalogueURL']=read(stage.STAGE/'plan.json')['areas'][0]['destination'];cfg['terrain']=read(stage.STAGE/'plan.json')['topLevelTerrainPatches'];cfg['viewportWidths']=[width];cfg['failureTestUids']=[];return cfg

def load(previous):
 failed=BASE/(stage.CONFIG['prefix']+'-original-installed-v4-'+stage.CONFIG['date'])
 rollback=read(failed/'failure-recovery.json');assert rollback['allPublicDestinationsRestored'] and rollback['currentPointerRestoredNotDerivedCredit'] and not rollback['derivedInstalledReviewHistoryRetained'] and not rollback['rollbackErrors']
 assert not (failed/'result.json').exists() and not (failed/'installed-acceptance.json').exists()
 assert PROTECTED_SNAPSHOT not in MUTABLE_CURRENT and MUTABLE_CURRENT==set(SHARED_MUTABLE_CURRENT)-{PROTECTED_SNAPSHOT}
 predecessor=BASE/(stage.CONFIG['prefix']+'-original-installed-v1-'+stage.CONFIG['date'])
 if predecessor.exists():
  assert not (predecessor/'result.json').exists() and not (predecessor/'installed-acceptance.json').exists()
  r=read(predecessor/'failure-recovery.json')
  assert r['allPublicDestinationsRestored'] and r['currentPointerRestoredNotDerivedCredit'] and not r['derivedInstalledReviewHistoryRetained'] and not r['rollbackErrors']
  for row in r['verifiedExpectedStatesAndRestoration']:
   path=ROOT/row['path'];assert (ref(path)['sha256'] if path.exists()else None)==row['restoredSHA256']
 keys=guard.evidence();pointer=read(POINTER);manifest=ROOT/'3d-viewer/city/data/manifest.json';models=read(stage.STAGE/'catalogue.json')['models']
 delta=inventory_delta(read(previous),models,manifest_sha=ref(manifest)['sha256'],snapshot=pointer['snapshotId'])
 receipts=[stage.DOC/'result.json',guard.BROWSER/'result.json',guard.REVIEW/'result.json']
 refs=distinct_refs([q for p in receipts for q in read(p)['evidenceRefs']]+[ref(p)for p in receipts+[previous,POINTER,PUB,BROWSER,FOCUSED,ATOMIC,Path(__file__),HERE.parent/'building-progress/export.py',failed/'failure-recovery.json',stage.DOC/'qualification.json']])
 for q in refs:check(q)
 for model in models:inventory_part(model,{})
 subprocess.run(['node',str(BROWSER),'preflight',str((stage.STAGE/'live-browser-config.json').relative_to(ROOT)),str((stage.PREVIOUS/'source-forms.json').relative_to(ROOT))],cwd=ROOT,check=True)
 return keys,pointer,models,delta,refs

def restore(saved):
 errors=[]
 for rel,raw in sorted(saved.items(),key=lambda x:x[0]=='3d-viewer/city/data/manifest.json'):
  p=ROOT/rel
  try:
   if raw is None:p.unlink(missing_ok=True)
   else:
    tmp=p.with_name(p.name+'.pacifica-rollback-'+uuid.uuid4().hex);tmp.write_bytes(raw);os.replace(tmp,p)
  except BaseException as e:errors.append(dict(path=rel,error=repr(e)))
 return errors

def owned(previous):
 with locked_publication(ROOT):
  guard.assert_publication_idle();lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
  keys,pointer,models,delta,refs=load(previous);assert keys<=set(lease['resources'])
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=read(manifest)
  old_models=[m for url in before['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
  assert len(old_models)==len({m['uid']for m in old_models})and not(set(stage.SOURCES)&{m['uid']for m in old_models})
  DOC.mkdir();config=browser_config(390);config['doc']=str(DOC.relative_to(ROOT))+'/';save(LOCAL/'browser-config.json',config)
  def call(command):
   assert reservations.owns(lease)
   p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
   save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr;assert reservations.owns(lease)
  command=[sys.executable,str(PUB),str((stage.STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(LEASE),'--phase',BATCH];call(command)
  pubdoc=ROOT/'docs/astra-city/model-integration-20260909'/BATCH;dry=read(pubdoc/'publication-plan.json');assert not dry['published']
  destination=read(stage.STAGE/'plan.json')['areas'][0]['destination'];assets=[(ROOT/'3d-viewer'/destination).parent/m['asset']for m in models]
  mutable=set(dry['after'])|set(MUTABLE_CURRENT)|{str(p.relative_to(ROOT))for p in assets}
  saved={r:(ROOT/r).read_bytes()if(ROOT/r).exists()else None for r in mutable};history=[]
  for rel,raw in saved.items():
   if raw is not None:
    p=LOCAL/'historical-current'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);history.append(dict(originalPath=rel,originalSHA256=hashlib.sha256(raw).hexdigest(),savedHistoricalBytes=ref(p)))
  save(DOC/'historical-input-context.json',dict(preInstallSnapshot=pointer['snapshotId'],mutableCurrentByteSnapshots=history,allMutableDestinations=sorted(mutable),originalEvidenceRefs=refs))
  acceptance=dict(uids=list(stage.SOURCES),sourceSHA256ByUid=stage.SOURCES,sourceStage=ref(stage.DOC/'result.json'),stagedBrowser=ref(guard.BROWSER/'result.json'),ROOTStagedImageReview=ref(stage.DOC/'qualification.json'),fixedXLDelta=delta,sourceGeometryChanges=0,sourcePoseChanges=0,rawPhysicalFailuresPreserved=True,publication=False,newlyInstalled=0)
  save(DOC/'acceptance.json',acceptance);inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']}
  for m in models:
   old=parts.get(m['uid'],{});parts[m['uid']]=inventory_part(m,old)
  ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=hashlib.sha256(jobs.encode([ordered,acceptance]).encode()).hexdigest()[:16];invpath=POINTER.parent/('source-review-inventory-'+snapshot+'.json')
  save(invpath,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Unchanged independent original sources with verified bounded terrain, exact-source interpretation, four-mode foundations, complete neighbours and reviewed desktop/mobile exports.'})
  sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
  ledger.seed(invpath,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
  ledger.record_many(snapshot,LEASE,[(m['uid'],'approved-for-integration',DOC/'acceptance.json','Exact unchanged assembly and current source/physical/browser evidence approved; live checks pending.',commit)for m in models],effort=effort,request_id=BATCH+'-approved-'+snapshot)
  installed_history=False
  def interrupted(signum,frame):
   raise RuntimeError('Original installation interrupted by lease supervisor')
  signal.signal(signal.SIGTERM,interrupted)
  try:
   for q in refs:check(q)
   guard.assert_publication_idle();call(command+['--apply'])
   for rel,h in dry['after'].items():assert ref(ROOT/rel)['sha256']==h
   after=read(manifest);all_models=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert all_models==old_models+models
   for m,p in zip(models,assets):assert ref(p)['sha256']==m['sha256']
   planned=read(stage.STAGE/'plan.json')['topLevelTerrainPatches'];assert len(planned)==1
   assert after['terrainPatches'][:-1]==before['terrainPatches'] and after['terrainPatches'][-1]['url']==planned[0]['destination']
   assert ref(ROOT/'3d-viewer'/planned[0]['destination'])['sha256']==planned[0]['sha256']
   assert after['counts']==before['counts']
   assert after['tiles']==before['tiles']

   report=dict(mode='live',passed=True,errors=[],views=[],jointViews=[],retainedNativeOwnViews=[])
   for width in [390,1280]:
    cfg=browser_config(width);subdir=DOC/('viewport-'+str(width));cfg['doc']=str(subdir.relative_to(ROOT))+'/';cfgpath=LOCAL/('browser-config-'+str(width)+'.json');save(cfgpath,cfg)
    call(['node',str(BROWSER),'live',str(cfgpath.relative_to(ROOT))]);part=read(subdir/'live-browser.json');assert part['passed']and not part['errors']
    for key in ['views','jointViews','retainedNativeOwnViews']:
     for item in part.get(key,[]):
      if 'file'in item:item['file']='viewport-'+str(width)+'/'+item['file']
      report[key].append(item)
   save(DOC/'live-browser.json',report);views=[v for v in report['views']if 'time'in v]
   assert report['passed']and not report['errors']and len(views)==4*len(stage.SOURCES) and len(report['jointViews'])>=2
   assert not report['retainedNativeOwnViews']
   for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['active']and v['visible']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==stage.SOURCES[v['uid']]
   atomiccfg={**browser_config(390),'liveInstalled':True,'diagnosticOnly':True,'publication':False,'expectedUids':sorted(stage.SOURCES)}
   atomicpath=LOCAL/'atomic-config.json';save(atomicpath,atomiccfg)
   call(['node',str(ATOMIC),str(atomicpath.relative_to(ROOT)),str((DOC/'atomic-lifecycle').relative_to(ROOT))])
   atomic=read(DOC/'atomic-lifecycle/report.json');assert atomic['passed']and not atomic['pageErrors']and atomic['liveInstalledHTTP']and atomic['catalogueAndTerrainSubstitution']is False
   assert len(atomic['cases'])==6 and {c['failedUid']for c in atomic['cases']}=={None,*stage.SOURCES}
   for c in atomic['cases']:
    assert c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and c['audit']['frames']>0 and not c['audit']['violations']
    assert {s['uid']:s['sha256']for s in c['sources']}==stage.SOURCES
    assert [r['phase']for r in c['basicLifecycle']]==(['failed-download']if c['failedUid']else[])+['original-active','base-only','auto-restored','evicted-return-base-only']
    if c['failedUid']:assert c['failureKeptAllBasics']
   save(DOC/'atomic-lifecycle-acceptance.json',dict(passed=True,report=ref(DOC/'atomic-lifecycle/report.json'),allOriginalPeerFailuresTested=True,completeBasicCounterpartLifecycleVerified=True))
   for joint in report['jointViews']:assert {m['uid']:m['sourceSHA256']for m in joint['models']}==stage.SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in joint['models'])
   installed={**acceptance,'snapshotId':snapshot,'publication':True,'newlyInstalled':delta['expectedFixedXLDelta'],'installedUids':list(stage.SOURCES),'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json'),'completeCurrentCatalogueModels':len(all_models)};save(DOC/'installed-acceptance.json',installed)
   ledger.record_many(snapshot,LEASE,[(m['uid'],'installed-verified',DOC/'installed-acceptance.json','Unchanged original assembly; source-specific physical review, current complete guards and staged/live joint desktop/mobile day/night picking/collision checks pass.',commit)for m in models],effort=effort,request_id=BATCH+'-installed-'+snapshot);installed_history=True
   assert read(POINTER)==pointer;save(POINTER,{**pointer,'snapshotId':snapshot,'inventory':ref(invpath)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
   call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh','--snapshot-path',str((DOC/'private-progress-export/neon-snapshot.json').relative_to(ROOT))]);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',str(previous.relative_to(ROOT)),'--batch',BATCH])
   counts=read(DOC/'full-xl-current-count.json')['counts'];n=delta['previousInstalled']+delta['expectedFixedXLDelta'];assert counts==dict(total=521,installedVerified=n,remaining=521-n)
   kind='selected-independent-original-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
   finalrefs=distinct_refs([q for q in refs if q['path']not in mutable]+[ref(p)for folder in [DOC,LOCAL,pubdoc]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json']+[ref(ROOT/p)for p in sorted(mutable)if(ROOT/p).exists()]+[ref(invpath)])
   final={**installed,'jobId':jid,'evidenceRefs':finalrefs,'historicalMutableByteSnapshots':history,'fullXLCurrentCounts':counts,'scriptExternalAICalls':0,'aiGeometryModelling':False}
   for q in finalrefs:check(q)
   with connect()as db:
    db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(db,lease)
    assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
   with connect()as db:
    db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
    for uid,sha in stage.SOURCES.items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,uid)).fetchone()==('installed-verified',sha)
   save(DOC/'result.json',final);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot))
   try:print(json.dumps(dict(installed=list(stage.SOURCES),counts=counts,jobId=jid)),flush=True)
   except BrokenPipeError:pass
  except BaseException as error:
   errors=restore(saved);save(DOC/'failure-recovery.json',dict(error=repr(error),derivedInstalledReviewHistoryRetained=installed_history,currentPointerRestoredNotDerivedCredit=True,allPublicDestinationsRestored=not errors,rollbackErrors=errors));raise

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--install',action='store_true');ap.add_argument('--owned',action='store_true');ap.add_argument('--previous',default=str(DEFAULT_PREVIOUS));a=ap.parse_args();previous=Path(a.previous).resolve()
 assert sum([a.prepare_only,a.install,a.owned])==1
 if a.prepare_only:
  keys,pointer,models,delta,refs=load(previous);save(BASE/(BATCH+'-proposal')/'installer-preflight.json',dict(passed=True,caller=ref(Path(__file__)),publisher=ref(PUB),delta=delta,resources=sorted(keys),evidenceRefs=refs,publication=False));print(json.dumps(dict(preflightPassed=True,delta=delta)));return
 if a.owned:return owned(previous)
 guard.assert_publication_idle();keys,*_=load(previous);assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('selected-independent-original-install-'+str(uuid.uuid4()),sorted(keys|{'immutable-source-proof:'+BATCH}),batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned','--previous',str(previous)],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':
 if '--owned' not in sys.argv:main()
 else:
  import functools,http.server,threading
  # The child holding the installation lease owns only this private loopback
  # server; all normal publication, rollback, dependency and ledger gates stay.
  class PrivateHandler(http.server.SimpleHTTPRequestHandler):
   def log_message(self,fmt,*args):pass
  server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(PrivateHandler,directory=str(ROOT/'3d-viewer')))
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:main()
  finally:server.shutdown();server.server_close();thread.join(timeout=5)
