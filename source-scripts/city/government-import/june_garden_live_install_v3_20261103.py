"""Atomic original-assembly publication, live checks and installed ledger recording.

--prepare-only is read-only apart from its proposal receipt. Actual installation
requires idle predecessor workers and the publisher's exact current-map evidence.
"""
import argparse,hashlib,json,os,subprocess,sys,uuid,signal,time
from types import SimpleNamespace
from contextlib import contextmanager
import socket,urllib.request
from pathlib import Path
import june_garden_guarded_publish_v3_20261103 as guard
from original_independent_atomic_contract_v1_20261027 import manifest_triple_transition
from june_garden_qualified_stage_v2_20261103 import inspected_exports
from run import connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
from june_garden_reuse_completed_live_v2_20261103 import reuse, preflight_metadata
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
from aqua_original_image_review_binding_v1_20261014 import MUTABLE_CURRENT
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
ROOT=guard.ROOT;HERE=guard.HERE;BASE=guard.BASE
read=guard.read;save=guard.save;ref=guard.ref
stage=SimpleNamespace(DOC=BASE/guard.QUALIFIED,STAGE=guard.STAGE,SOURCES=guard.SOURCES)
BATCH=guard.BATCH;DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PUB=HERE/'june_garden_guarded_publish_v3_20261103.py'
BROWSER=HERE/'ronsdale_three_live_browser_v21_20261103.mjs'
ATOMIC=HERE/'model_atomic_lifecycle_live_browser_v1_20261027.mjs'
POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
DEFAULT_PREVIOUS=BASE/'government-xl-observatory252988-original-retained-original-installed-v11-20261102/full-xl-current-count.json'
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def assert_publication_idle():
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==read(stage.DOC/'qualification.json')['currentManifestSHA256']
def retained_uids():return {r['uid']for r in read(BASE/guard.TERRAIN/'summary.json')['rows']}
def verify_atomic(report):
 assert report['passed'] and not report['pageErrors'] and len(report['cases'])==7
 assert sorted(c['failedUid']for c in report['cases']if c['failedUid'])==sorted(stage.SOURCES)
 for case in report['cases']:
  assert case['baseOnlyRestoredCompleteGroup'] and case['completeGroupEvicted'] and not case['audit']['violations']
  assert {r['uid']:r['sha256']for r in case['sources']}==stage.SOURCES
  if case['failedUid']:assert case['width']==390 and case['failureKeptAllBasics']
 return True

def inventory_part(model,old):
 return dict(uid=model['uid'],name=model.get('label')or old.get('name')or model['uid'],landmarkIds=old.get('landmarkIds',[]),objectId=model['objectId'],csuid=model['buildingCSUID'],candidate=dict(sha256=model['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-source',knownHold=False)

def browser_config(width,focused=False):
 cfg=read(stage.STAGE/'live-browser-config.json')
 assert set(cfg['additionalRetainedUids'])==retained_uids() and len(retained_uids())==69
 cfg.update(viewportWidths=[width],autoVisibleCamera=True,jointUids=sorted(stage.SOURCES),
  browserUids=sorted(stage.SOURCES),failureTestUids=[],keepSelectedForRetainedCapture=['landsd/160070:0']if width==390 else[])
 return cfg

def load(previous):
 keys,surface,originals,manifest,pins=guard.evidence();keys.add('server:127.0.0.1:4197');pointer=read(POINTER);models=read(stage.STAGE/'catalogue.json')['models']
 assert not DOC.exists() and read(previous)['counts']==dict(total=521,installedVerified=426,remaining=95)
 delta=inventory_delta(read(previous),models,manifest_sha=manifest['sha256'],snapshot=pointer['snapshotId'])
 assert delta['previousInstalled']==426 and delta['expectedFixedXLDelta']==1 and set(delta['newFixedXLUids'])=={guard.P}
 paths=[previous,POINTER,PUB,BROWSER,ATOMIC,Path(__file__),HERE/'june_garden_publisher_hooks_v3_20261103.py',HERE/'june_garden_reuse_completed_live_v2_20261103.py',HERE/'validated_browser_checkpoint_v1_20261103.mjs',HERE/'june_garden_qualified_stage_v4_20261103.py',HERE/'observed_reserved_runner_v3_20261103.py',HERE.parent/'shared-modelling/reservation_runner.py',HERE.parent/'building-progress/export.py']
 refs=distinct_refs([dict(path=p,sha256=h)for p,h in pins.items()]+[ref(p)for p in paths])
 for q in refs:check(q)
 subprocess.run(['node',str(BROWSER),'preflight',str((stage.STAGE/'live-browser-config.json').relative_to(ROOT))],cwd=ROOT,check=True)
 atomic=read(stage.STAGE/'live-browser-config.json');atomic.update(liveInstalled=True,diagnosticOnly=True,publication=False)
 preflight_metadata(browser_config(390),atomic,verify_atomic)
 return keys,pointer,models,delta,refs

def wait_for_root_inspection(report,lease):
 expected={str((DOC/r['file']).relative_to(ROOT)):ref(DOC/r['file'])['sha256']for r in [*report['views'],*report['retainedNativeOwnViews']]if 'time'in r}
 atomic=sorted((DOC/'atomic-live').glob('*.png'));assert len(expected)==300 and len(atomic)==7
 expected.update({str(p.relative_to(ROOT)):ref(p)['sha256']for p in atomic})
 save(DOC/'live-export-inspection-request.json',dict(images=[dict(path=p,sha256=s)for p,s in sorted(expected.items())],imagesRequired=307,publication=True,installedVerified=False))
 path=DOC/'ROOT-LIVE-EXPORT-INSPECTION.json';deadline=time.monotonic()+1800
 print('All live software checks passed; waiting for actual ROOT inspection of307 exports. No installed credit.',flush=True)
 while not path.exists():
  if time.monotonic()>deadline:raise TimeoutError('Actual export review missing; rollback publication, do not award installed credit')
  time.sleep(2)
 assert reservations.owns(lease)
 inspection=read(path);assert inspection['reviewer']=='ROOT'
 inspected_exports(inspection,expected,root=ROOT)
 return ref(path)

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

@contextmanager
def owned_server():
 lease=read(LEASE);assert reservations.owns(lease) and 'server:127.0.0.1:4197'in lease['resources']
 with socket.socket() as probe:probe.bind(('127.0.0.1',4197))
 with (LOCAL/'server.log').open('w') as log:
  server=subprocess.Popen([sys.executable,'-m','http.server','4197','--bind','127.0.0.1','--directory',str(ROOT/'3d-viewer')],stdout=log,stderr=subprocess.STDOUT)
  try:
   for attempt in range(50):
    assert server.poll()is None
    try:
     with urllib.request.urlopen('http://127.0.0.1:4197/city.html',timeout=1)as response:assert response.status==200
     break
    except OSError:time.sleep(.1)
   else:raise RuntimeError('Owned installation server did not start')
   yield
  finally:
   server.terminate()
   try:server.wait(timeout=10)
   except subprocess.TimeoutExpired:server.kill();server.wait(timeout=10)

def owned(previous):
 with owned_server(),locked_publication(ROOT):
  assert_publication_idle();lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
  keys,pointer,models,delta,refs=load(previous);assert keys<=set(lease['resources'])
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=read(manifest)
  old_models=[m for url in before['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
  assert len(old_models)==len({m['uid']for m in old_models})and not(set(stage.SOURCES)&{m['uid']for m in old_models})
  DOC.mkdir();config=browser_config(390);config['doc']=str(DOC.relative_to(ROOT))+'/';save(LOCAL/'browser-config.json',config)
  def call(command):
   assert reservations.owns(lease)
   p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
   save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr;assert reservations.owns(lease)
  command=[sys.executable,str(PUB),'--receipt',str(LEASE)];call(command)
  pubdoc=ROOT/'docs/astra-city/model-integration-20260909'/BATCH;dry=read(pubdoc/'publication-plan.json');assert not dry['published']
  destination=read(stage.STAGE/'plan.json')['areas'][0]['destination'];assets=[(ROOT/'3d-viewer'/destination).parent/m['asset']for m in models]
  mutable=set(dry['after'])|set(MUTABLE_CURRENT)|{str(p.relative_to(ROOT))for p in assets}
  saved={r:(ROOT/r).read_bytes()if(ROOT/r).exists()else None for r in mutable};history=[]
  for rel,raw in saved.items():
   if raw is not None:
    p=LOCAL/'historical-current'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);history.append(dict(originalPath=rel,originalSHA256=hashlib.sha256(raw).hexdigest(),savedHistoricalBytes=ref(p)))
  save(DOC/'historical-input-context.json',dict(preInstallSnapshot=pointer['snapshotId'],mutableCurrentByteSnapshots=history,allMutableDestinations=sorted(mutable),originalEvidenceRefs=refs))
  acceptance=dict(transactionBatch=BATCH,uids=list(stage.SOURCES),sourceSHA256ByUid=stage.SOURCES,sourceStage=ref(stage.DOC/'result.json'),stagedBrowser=ref(BASE/guard.BROWSER/'result.json'),ROOTStagedImageReview=ref(stage.DOC/'qualification.json'),fixedXLDelta=delta,sourceGeometryChanges=0,sourcePoseChanges=0,rawPhysicalFailuresPreserved=True,publication=False,newlyInstalled=0)
  save(DOC/'acceptance.json',acceptance);inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']}
  for m in models:
   old=parts.get(m['uid'],{});parts[m['uid']]=inventory_part(m,old)
  ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=__import__('installation_snapshot_identity_v1_20261031').identity(ordered,acceptance,BATCH);invpath=POINTER.parent/('source-review-inventory-'+snapshot+'.json')
  assert not invpath.exists(), 'Do not reseed an existing installation snapshot'
  with connect() as db:
   db.execute('SET TRANSACTION READ ONLY');assert not db.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE snapshot_id=%s LIMIT 1',(snapshot,)).fetchone(), 'Do not reseed existing snapshot rows'
  save(invpath,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Unchanged independent original sources with verified bounded terrain, exact-source interpretation, four-mode foundations, complete neighbours and reviewed desktop/mobile exports.'})
  sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
  ledger.seed(invpath,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='scripted',ai_model=None,reasoning_effort='not-applicable',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
  ledger.record_many(snapshot,LEASE,[(m['uid'],'approved-for-integration',DOC/'acceptance.json','Exact unchanged assembly and current source/physical/browser evidence approved; live checks pending.',commit)for m in models],effort=effort,request_id=BATCH+'-approved-'+snapshot)
  installed_history=False
  def interrupted(signum, frame):
   raise RuntimeError('Original installation interrupted by lease supervisor')
  signal.signal(signal.SIGTERM,interrupted)
  try:
   for q in refs:check(q)
   assert_publication_idle();call(command+['--apply'])
   for rel,h in dry['after'].items():assert ref(ROOT/rel)['sha256']==h
   after=read(manifest);all_models=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert all_models==old_models+models
   for m,p in zip(models,assets):assert ref(p)['sha256']==m['sha256']
   planned=read(stage.STAGE/'plan.json')['topLevelTerrainPatches'];manifest_triple_transition(before,after,planned)
   for entry in planned:
    assert ref(ROOT/'3d-viewer'/entry['destination'])['sha256']==entry['sha256']
    assert ref(ROOT/'3d-viewer'/entry['replaces']['url'])['sha256']==entry['replaces']['sha256']
   for url in before['officialModelCatalogues']:
    path=ROOT/'3d-viewer'/url
    for model in read(path)['models']:assert ref(path.parent/model['asset'])['sha256']==model['sha256']
   atomic=read(stage.STAGE/'live-browser-config.json')
   atomic.update(liveInstalled=True,diagnosticOnly=True,publication=False)
   atomicpath=LOCAL/'atomic-live-config.json';save(atomicpath,atomic)
   reused=reuse(DOC,browser_config(390),atomic,lease,verify_atomic);save(DOC/'reused-complete-live.json',reused);refs.append(reused['proofReceipt'])
   assert verify_atomic(read(DOC/'atomic-live/report.json'))

   report=dict(mode='live',passed=True,errors=[],views=[],jointViews=[],retainedNativeOwnViews=[])
   for width in [390,1280]:
    cfg=browser_config(width);subdir=DOC/('viewport-'+str(width));cfg['doc']=str(subdir.relative_to(ROOT))+'/';cfgpath=LOCAL/('browser-config-'+str(width)+'.json')
    if width==1280:
     bindings={q['path']:dry['after'].get(q['path'],q['sha256'])for q in refs}
     for path,sha in bindings.items():assert ref(ROOT/path)['sha256']==sha,path
     cfg['checkpointInputRefs']=[dict(path=path,sha256=sha)for path,sha in sorted(bindings.items())]
    save(cfgpath,cfg)
    if width==1280:call(['node',str(BROWSER),'live',str(cfgpath.relative_to(ROOT))])
    part=read(subdir/'live-browser.json');assert part['passed']and not part['errors']
    for key in ['views','jointViews','retainedNativeOwnViews']:
     for item in part.get(key,[]):
      if 'file'in item:item['file']='viewport-'+str(width)+'/'+item['file']
      report[key].append(item)
   save(DOC/'live-browser.json',report);views=[v for v in report['views']if 'time'in v]
   assert report['passed']and not report['errors']and len(views)==4*len(stage.SOURCES) and len(report['jointViews'])>=2
   retained=retained_uids()
   originals={m['uid']:m for m in old_models}
   nativeviews=report['retainedNativeOwnViews']
   assert retained and len(nativeviews)==4*len(retained)
   assert {(v['uid'],v['width'],v['time']) for v in nativeviews}=={(uid,width,time) for uid in retained for width in [390,1280] for time in ['15:00','22:00']}
   for v in nativeviews:
    assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
    assert v['sourceSHA256']==originals[v['uid']]['sha256'] and v['originalTriangles']==originals[v['uid']]['triangles']
    assert all(v['meshVisibility']) and not any(v['wireframeFlags'])
   for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['active']and v['visible']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==stage.SOURCES[v['uid']]
   failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert failed==[] and verify_atomic(read(DOC/'atomic-live/report.json'))
   for joint in report['jointViews']:assert {m['uid']:m['sourceSHA256']for m in joint['models']}==stage.SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in joint['models'])
   inspection=wait_for_root_inspection(report,lease)
   installed={**acceptance,'ROOTLiveVisualInspection':inspection,'snapshotId':snapshot,'publication':True,'newlyInstalled':delta['expectedFixedXLDelta'],'installedUids':list(stage.SOURCES),'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json'),'completeCurrentCatalogueModels':len(all_models)};save(DOC/'installed-acceptance.json',installed)
   ledger.record_many(snapshot,LEASE,[(m['uid'],'installed-verified',DOC/'installed-acceptance.json','Unchanged original assembly; source-specific physical review, current complete guards and staged/live joint desktop/mobile day/night picking/collision checks pass.',commit)for m in models],effort=effort,request_id=BATCH+'-installed-'+snapshot);installed_history=True
   assert read(POINTER)==pointer;save(POINTER,{**pointer,'snapshotId':snapshot,'inventory':ref(invpath)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
   call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh','--snapshot-path',str((DOC/'progress/neon-snapshot.json').relative_to(ROOT))]);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',str(previous.relative_to(ROOT)),'--batch',BATCH])
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
 assert_publication_idle();keys,*_=load(previous);assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('selected-independent-original-install-'+str(uuid.uuid4()),sorted(keys|{'immutable-source-proof:'+BATCH}),batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE/'observed_reserved_runner_v3_20261103.py'),str(LEASE),sys.executable,__file__,'--owned','--previous',str(previous)],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
