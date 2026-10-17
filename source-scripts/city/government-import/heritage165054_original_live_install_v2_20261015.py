"""Install the reviewed Museum atomically after PolyU's pinned job has finished.
Original government geometry unchanged; failure restores every mutable public file.
"""
from pathlib import Path
from contextlib import nullcontext
import argparse,hashlib,json,os,subprocess,sys,time,uuid
import heritage165054_joint_staged_browser_v2_20261015 as staged
from run import connect,reservations,jobs,Jsonb,dict_row
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
from aqua_original_image_review_binding_v1_20261014 import MUTABLE_CURRENT as PROGRESS_MUTABLE
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
stage=staged.stage;ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE;read=stage.read;save=stage.save;ref=stage.ref;check=stage.check;UID=stage.UID
BATCH='government-xl-heritage165054-original-installed-v2-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PUB=HERE/'heritage165054_guarded_publish_v2_20261015.py'
PREVIOUS=BASE/'government-xl-aqua-marine193086-original-installed-v1-20261014/full-xl-current-count.json';POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
STAGED_JOB='711e338a0cc8ae28c5c99f2d9157538170780061e248cea3bfaf5dfe1b0158e5'
POLYU='government-xl-polyu-complete-saved-actor-finite-v2-20261014'

def replace_pointer(path, value):
 temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
 try:
  temporary.write_text(json.dumps(value,indent=2)+'\n')
  os.replace(temporary,path)
 finally:
  temporary.unlink(missing_ok=True)


def polyu_ready():
 lease=read(HERE/'local'/POLYU/'reservation.json')
 alive=[]
 for pid in [1132389,1136726,1136786]:
  p=Path('/proc')/str(pid)/'cmdline'
  if p.exists()and b'polyu_complete_saved_actor_finite_v2_draft_20261014.py'in p.read_bytes():alive.append(pid)
 if alive or reservations.owns(lease):return False
 result=read(BASE/POLYU/'result.json')
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for q in result['evidenceRefs']:check(q)
 return True

def load():
 result=read(staged.DOC/'result.json');v=read(staged.DOC/'ROOT-VERIFIED.json');assert result['jobId']==v['jobId']==STAGED_JOB and v['allEvidenceHashesVerified']and v['leaseReleased']and v['exactNeonReadback']
 review=read(staged.DOC/'ROOT-IMAGE-INSPECTION.json');report=read(staged.DOC/'staged-browser.json');views=[x for x in report['views']if 'time'in x]
 assert report['passed']and not report['errors']and len(views)==4
 assert review['uid']==UID and review['sourceSHA256']==stage.original.SOURCE and review['visualAcceptance']and review['allFourExportedImagesActuallyInspected']and review['reviewer']=='Codex ROOT'
 assert review['stagedJob']==STAGED_JOB and review['stagedBrowser']==ref(staged.DOC/'staged-browser.json')and review['sourceStage']==ref(stage.DOC/'result.json')and review['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')
 assert review['imagesActuallyViewed']==[ref(staged.DOC/x['file'])for x in views]
 previous=read(PREVIOUS);pointer=read(POINTER);assert pointer['snapshotId']=='be5f7671a989392d'and previous['counts']==dict(total=521,installedVerified=236,remaining=285)
 models=read(stage.STAGE/'catalogue.json')['models'];delta=inventory_delta(previous,models,manifest_sha=stage.original.CURRENT,snapshot=pointer['snapshotId']);assert delta['expectedFixedXLDelta']==1 and delta['newFixedXLUids']==[UID]
 refs=distinct_refs(result['evidenceRefs']+[ref(staged.DOC/'result.json'),ref(staged.DOC/'ROOT-VERIFIED.json'),ref(staged.DOC/'ROOT-IMAGE-INSPECTION.json'),ref(PREVIOUS),ref(POINTER),ref(PUB),ref(Path(__file__))])
 for q in refs:check(q)
 return result,review,pointer,models,delta,refs

def owned():
 from publication_lock import locked_publication
 with locked_publication(ROOT):
  lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();assert polyu_ready(),'PolyU pinned-source computation still live'
  result,review,pointer,models,delta,refs=load();manifest=ROOT/'3d-viewer/city/data/manifest.json';original=read(manifest);plan=read(stage.STAGE/'plan.json');destination=plan['areas'][0]['destination'];old_models=[m for url in original['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(old_models)==len({m['uid']for m in old_models})==6653 and UID not in {m['uid']for m in old_models}
  DOC.mkdir();config=read(staged.LOCAL/'browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';save(LOCAL/'browser-config.json',config)
  def call(command):
   assert reservations.owns(lease);p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':os.environ.get('CHROME_PATH','/opt/google/chrome/chrome')});save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr;assert reservations.owns(lease)
  publication=[sys.executable,str(PUB),str((stage.STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(LEASE),'--phase',BATCH];call(publication);pubdoc=ROOT/'docs/astra-city/model-integration-20260909'/BATCH;dry=read(pubdoc/'publication-plan.json');expected=read(stage.DOC/'publisher-dry-run/publication-plan.json');assert dry['after']==expected['after']and dry['before']==expected['before']and not dry['published']
  mutable=set(dry['after'])|set(PROGRESS_MUTABLE);asset=(ROOT/'3d-viewer'/destination).parent/models[0]['asset'];mutable.add(str(asset.relative_to(ROOT)))
  saved={rel:(ROOT/rel).read_bytes()if(ROOT/rel).exists()else None for rel in mutable};snapshots=[]
  for rel,raw in saved.items():
   if raw is not None:
    path=LOCAL/'historical-current'/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);snapshots.append(dict(originalPath=rel,originalSHA256=hashlib.sha256(raw).hexdigest(),savedHistoricalBytes=ref(path)))
  save(DOC/'historical-input-context.json',dict(preInstallSnapshot=pointer['snapshotId'],preInstallManifestSHA256=stage.original.CURRENT,mutableCurrentByteSnapshots=snapshots,allMutableDestinations=sorted(mutable),originalEvidenceRefs=refs))
  decision=dict(installationAttempt=BATCH,uid=UID,sourceSHA256=stage.original.SOURCE,sourceStage=ref(stage.DOC/'result.json'),stagedBrowser=ref(staged.DOC/'result.json'),ROOTStagedImageReview=ref(staged.DOC/'ROOT-IMAGE-INSPECTION.json'),fixedXLDelta=delta,sourceGeometryChanges=0,exact19LowerClosureApplicability=ref(stage.DOC/'qualified-existing-source-applicability.json'),strictFoundationPassed=True,publication=False,newlyInstalled=0)
  save(DOC/'acceptance.json',decision);inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']};m=models[0];old=parts.get(UID,{})
  parts[UID]=dict(uid=UID,name=m['label'],landmarkIds=old.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate=dict(sha256=m['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-source',knownHold=False)
  ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=hashlib.sha256(jobs.encode([ordered,decision]).encode()).hexdigest()[:16];inv_path=POINTER.parent/('source-review-inventory-'+snapshot+'.json');save(inv_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Retry v2: Heritage immutable original with exact source lower-closure review, full current guards and joint authentic terrain/unsurveyed BASIC estimate; raw numeric negatives preserved.'})
  sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
  ledger.seed(inv_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
  ledger.record_many(snapshot,LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json','Exact original source/whole guards and four ROOT-inspected staged exports pass; joint terrain and estimated BASIC base; live pending.',commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
  applied=False;ledger_installed=False
  try:
   for q in refs:check(q)
   assert polyu_ready();call(publication+['--apply']);applied=True
   for rel,h in dry['after'].items():assert ref(ROOT/rel)['sha256']==h
   after=read(manifest);new_models=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert new_models==old_models+models and len(new_models)==6654 and ref(asset)['sha256']==stage.original.SOURCE
   assert len(after['terrainPatches'])==len(original['terrainPatches'])+1 and after['terrainPatches'][:-1]==original['terrainPatches']
   call(['node',str(staged.BROWSER),'live',str((LOCAL/'browser-config.json').relative_to(ROOT))]);browser=stage.original.prior.module(HERE/'integrate.py','heritage_live_browser_contract').browser_verified(DOC/'live-browser.json',{UID});liveviews=[v for v in browser['views']if 'time'in v];assert len(liveviews)==4
   for v in liveviews:assert v['fullyFramed']and v['solidAppearance']and v['sourceSHA256']==stage.original.SOURCE and v['originalTriangles']==15140 and v['fallbackFaces']==0 and v['retained']['landsd/128971:0']['base']==5.199032035191232
   installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'installedUids':[UID],'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json'),'completeCurrentCatalogueModels':6654};save(DOC/'installed-acceptance.json',installed)
   ledger.record_many(snapshot,LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json','Unchanged original, exact lower-closure source review, whole current terrain/neighbours, inspected staged exports and live desktop/mobile day/night picking/collision/retry pass. Terrain and estimated shelter base applied together.',commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot);ledger_installed=True
   assert read(POINTER)==pointer;replace_pointer(POINTER,{**pointer,'snapshotId':snapshot,'inventory':ref(inv_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
   call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',str(PREVIOUS.relative_to(ROOT)),'--batch',BATCH]);counts=read(DOC/'full-xl-current-count.json')['counts'];assert counts==dict(total=521,installedVerified=237,remaining=284)
   kind='heritage-original-joint-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
   finalrefs=distinct_refs([q for q in refs if q['path']not in mutable]+[ref(p)for folder in [DOC,LOCAL,pubdoc]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json']+[ref(ROOT/p)for p in sorted(mutable)if(ROOT/p).exists()]+[ref(inv_path)])
   final={**installed,'jobId':jid,'uids':[UID],'evidenceRefs':finalrefs,'historicalMutableByteSnapshots':snapshots,'fullXLCurrentCounts':counts,'scriptExternalAICalls':0,'aiGeometryModelling':False}
   for q in finalrefs:check(q)
   with connect()as db:
    db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(db,lease);assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
   with connect()as db:
    db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final);assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,UID)).fetchone()==('installed-verified',stage.original.SOURCE)
   save(DOC/'result.json',final);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot));print(json.dumps(dict(installed=UID,snapshot=snapshot,jobId=jid,counts=counts)),flush=True)
  except BaseException as error:
   failures=[]
   for rel,raw in sorted(saved.items(),key=lambda x:x[0]=='3d-viewer/city/data/manifest.json'):
    p=ROOT/rel
    try:
     if raw is None:p.unlink(missing_ok=True)
     else:
      tmp=p.with_name(p.name+'.heritage-rollback-'+uuid.uuid4().hex);tmp.write_bytes(raw);os.replace(tmp,p)
    except BaseException as e:failures.append(dict(path=rel,error=repr(e)))
   save(DOC/'failure-recovery.json',dict(error=repr(error),applyCompleted=applied,derivedInstalledReviewHistoryRetained=ledger_installed,currentPointerRestoredNotDerivedCredit=True,allPublicDestinationsRestored=not failures,rollbackErrors=failures));raise

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--after-polyu',action='store_true');ap.add_argument('--owned',action='store_true');args=ap.parse_args()
 if args.prepare_only:
  *_,delta,refs=load();save(BASE/(BATCH+'-proposal')/'preflight.json',dict(passed=True,caller=ref(Path(__file__)),publisher=ref(PUB),expectedDelta=delta,evidenceRefs=refs,publication=False,awaitingPolyUCompletion=True));print(json.dumps(dict(preflightPassed=True,expectedCounts=dict(installed=237,remaining=284),awaitingPolyUCompletion=True)));return
 if args.owned:return owned()
 assert args.after_polyu and not DOC.exists()and not LOCAL.exists();prep=read(BASE/(BATCH+'-proposal')/'preflight.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['publisher']==ref(PUB)
 while not polyu_ready():print('Waiting for verified PolyU completion; no publication or source lease claimed.',flush=True);time.sleep(30)
 load();forms=read(stage.shelter.capture.DOC/'input.json.gz')['currentForms'];keys=reservations.normalise([r for r in stage.shelter.capture.resources([f['building']['uid']for f in forms])if not r.startswith('immutable-source-proof:')]+['immutable-source-proof:'+BATCH]);c=reservations.claim('heritage-original-install-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
