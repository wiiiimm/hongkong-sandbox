"""Atomic combined-original publication, live checks and installed ledger recording.

--prepare-only is read-only apart from its proposal receipt. Actual installation
requires idle predecessor workers and the publisher's exact current-map evidence.
"""
import argparse,hashlib,json,os,subprocess,sys,uuid
from pathlib import Path
import science_museum_guarded_publish_v1_20261016 as guard
from run import connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
from science_museum_guarded_publish_v1_20261016 import inventory_delta
from aqua_original_image_review_binding_v1_20261014 import MUTABLE_CURRENT
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
stage=guard.stage;ROOT=guard.ROOT;HERE=guard.HERE;BASE=guard.BASE
read=stage.read;save=stage.save;ref=stage.ref;check=guard.check
BATCH=guard.BATCH;DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PUB=HERE/'science_museum_guarded_publish_v1_20261016.py';BROWSER=HERE/'history_museum_private_browser_v1_20261016.mjs'
POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
DEFAULT_PREVIOUS=BASE/'government-xl-history-museum-original-installed-v1-20261016/full-xl-current-count.json'

def load(previous):
 keys=guard.evidence();pointer=read(POINTER);manifest=ROOT/'3d-viewer/city/data/manifest.json';models=read(stage.STAGE/'catalogue.json')['models']
 delta=inventory_delta(read(previous),models,manifest_sha=ref(manifest)['sha256'],snapshot=pointer['snapshotId'])
 receipts=[stage.DOC/'result.json',guard.BROWSER/'result.json',guard.REVIEW/'result.json']
 refs=distinct_refs([q for p in receipts for q in read(p)['evidenceRefs']]+[ref(p)for p in receipts+[previous,POINTER,PUB,BROWSER,Path(__file__),HERE/'fixed_xl_source_binding.py',HERE/'xl-current-installed-count-audit.py',guard.BROWSER/'ROOT-IMAGE-INSPECTION.json']])
 for q in refs:check(q)
 return keys,pointer,models,delta,refs

def restore(saved):
 errors=[]
 for rel,raw in sorted(saved.items(),key=lambda x:x[0]=='3d-viewer/city/data/manifest.json'):
  p=ROOT/rel
  try:
   if raw is None:p.unlink(missing_ok=True)
   else:
    tmp=p.with_name(p.name+'.ets-rollback-'+uuid.uuid4().hex);tmp.write_bytes(raw);os.replace(tmp,p)
  except BaseException as e:errors.append(dict(path=rel,error=repr(e)))
 return errors

def owned(previous):
 with locked_publication(ROOT):
  guard.assert_publication_idle();lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
  keys,pointer,models,delta,refs=load(previous);assert keys<=set(lease['resources'])
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=read(manifest)
  old_models=[m for url in before['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
  assert len(old_models)==len({m['uid']for m in old_models})and not(set(stage.SOURCES)&{m['uid']for m in old_models})
  DOC.mkdir();config=read(stage.STAGE/'browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';save(LOCAL/'browser-config.json',config)
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
  acceptance=dict(uids=list(stage.SOURCES),sourceSHA256ByUid=stage.SOURCES,sourceStage=ref(stage.DOC/'result.json'),stagedBrowser=ref(guard.BROWSER/'result.json'),ROOTStagedImageReview=ref(guard.BROWSER/'ROOT-IMAGE-INSPECTION.json'),fixedXLDelta=delta,sourceGeometryChanges=0,sourcePoseChanges=0,rawPhysicalFailuresPreserved=True,publication=False,newlyInstalled=0)
  save(DOC/'acceptance.json',acceptance);inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']}
  for m in models:
   old=parts.get(m['uid'],{});parts[m['uid']]=dict(uid=m['uid'],name=m['label'],landmarkIds=old.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate=dict(sha256=m['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-source',knownHold=False)
  ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=hashlib.sha256(jobs.encode([ordered,acceptance]).encode()).hexdigest()[:16];invpath=POINTER.parent/('source-review-inventory-'+snapshot+'.json')
  save(invpath,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Exact unchanged Science Museum original and retained canopy foundation, exact government identifiers and standard strict spatial identity checks, complete current placement/neighbour evidence and desktop/mobile exports.'})
  sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
  ledger.seed(invpath,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
  ledger.record_many(snapshot,LEASE,[(m['uid'],'approved-for-integration',DOC/'acceptance.json','Exact unchanged Science Museum original and current source/physical/browser evidence approved; live checks pending.',commit)for m in models],effort=effort,request_id=BATCH+'-approved-'+snapshot)
  installed_history=False
  try:
   for q in refs:check(q)
   guard.assert_publication_idle();call(command+['--apply'])
   for rel,h in dry['after'].items():assert ref(ROOT/rel)['sha256']==h
   after=read(manifest);all_models=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert all_models==old_models+models
   for m,p in zip(models,assets):assert ref(p)['sha256']==m['sha256']
   replaced={t['replaces']['url']for t in read(stage.STAGE/'plan.json')['topLevelTerrainPatches']};assert after['terrainPatches'][:-1]==[t for t in before['terrainPatches']if t['url']not in replaced] and len(after['terrainPatches'])==len(before['terrainPatches'])
   call(['node',str(BROWSER),'live',str((LOCAL/'browser-config.json').relative_to(ROOT))]);report=read(DOC/'live-browser.json');views=[v for v in report['views']if 'time'in v]
   assert report['passed']and not report['errors']and len(views)==4
   assert len(report['retainedNativeOwnViews'])==8 and all(v['fullyFramed']and v['active']and v['visible']and not v['fallbackFaces']for v in report['retainedNativeOwnViews'])
   for v in views:assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['active']and v['visible']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==stage.SOURCES[v['uid']]
   failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['fallbackRetained']
   for joint in report.get('jointViews',[]):assert {m['uid']:m['sourceSHA256']for m in joint['models']}==stage.SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in joint['models'])
   installed={**acceptance,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'installedUids':list(stage.SOURCES),'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json'),'completeCurrentCatalogueModels':len(all_models)};save(DOC/'installed-acceptance.json',installed)
   ledger.record_many(snapshot,LEASE,[(m['uid'],'installed-verified',DOC/'installed-acceptance.json','Unchanged Science Museum original; exact source identity, complete current physical/neighbour checks and staged/live desktop/mobile day/night picking/collision checks pass.',commit)for m in models],effort=effort,request_id=BATCH+'-installed-'+snapshot);installed_history=True
   assert read(POINTER)==pointer;save(POINTER,{**pointer,'snapshotId':snapshot,'inventory':ref(invpath)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
   call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',str(previous.relative_to(ROOT)),'--batch',BATCH])
   counts=read(DOC/'full-xl-current-count.json')['counts'];n=delta['previousInstalled']+delta['expectedFixedXLDelta'];assert counts==dict(total=521,installedVerified=n,remaining=521-n)
   kind='science-museum-original-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
   finalrefs=distinct_refs([q for q in refs if q['path']not in mutable]+[ref(p)for folder in [DOC,LOCAL,pubdoc]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json']+[ref(ROOT/p)for p in sorted(mutable)if(ROOT/p).exists()]+[ref(invpath)])
   final={**installed,'jobId':jid,'evidenceRefs':finalrefs,'historicalMutableByteSnapshots':history,'fullXLCurrentCounts':counts,'scriptExternalAICalls':0,'aiGeometryModelling':False}
   for q in finalrefs:check(q)
   with connect()as db:
    db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(db,lease)
    assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
   with connect()as db:
    db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
    for uid,sha in stage.SOURCES.items():assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,uid)).fetchone()==('installed-verified',sha)
   save(DOC/'result.json',final);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot));print(json.dumps(dict(installed=list(stage.SOURCES),counts=counts,jobId=jid)),flush=True)
  except BaseException as error:
   errors=restore(saved);save(DOC/'failure-recovery.json',dict(error=repr(error),derivedInstalledReviewHistoryRetained=installed_history,currentPointerRestoredNotDerivedCredit=True,allPublicDestinationsRestored=not errors,rollbackErrors=errors));raise

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--install',action='store_true');ap.add_argument('--owned',action='store_true');ap.add_argument('--previous',default=str(DEFAULT_PREVIOUS));a=ap.parse_args();previous=Path(a.previous).resolve()
 assert sum([a.prepare_only,a.install,a.owned])==1
 if a.prepare_only:
  keys,pointer,models,delta,refs=load(previous);save(BASE/(BATCH+'-proposal')/'installer-preflight.json',dict(passed=True,caller=ref(Path(__file__)),publisher=ref(PUB),delta=delta,resources=sorted(keys),evidenceRefs=refs,publication=False));print(json.dumps(dict(preflightPassed=True,delta=delta)));return
 if a.owned:return owned(previous)
 guard.assert_publication_idle();keys,*_=load(previous);assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('science-museum-original-install-'+str(uuid.uuid4()),sorted(keys|{'immutable-source-proof:'+BATCH}),batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned','--previous',str(previous)],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
