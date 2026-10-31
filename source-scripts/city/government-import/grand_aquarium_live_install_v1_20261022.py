"""Lease-fenced Aquarium publication, rollback, live verification and installed ledger."""
from pathlib import Path
from contextlib import contextmanager
import argparse,hashlib,json,os,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from publication_lock import locked_publication
from aqua_original_image_review_binding_v1_20261014 import MUTABLE_CURRENT
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-original-installed-v1-20261022';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PREP=BASE/'government-xl-grand-aquarium-qualified-stage-v1-20261022';STAGE=HERE/'accepted'/PREP.name;POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';BROWSER=HERE/'manhattan_collision_witness_browser_v1_20261021.mjs';UID='landsd/93424:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def inputs():
 r,pins=authenticate(PREP)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert r['qualifiedForLiveVerification']and r['newVisibleModels']==1 and r['delta']['expectedFixedXLDelta']==1 and r['delta']['previousInstalled']==323
 review=read(PREP/'ROOT-SOURCE-REVIEW.json');assert all(review[k]for k in ['originalSourceReviewAccepted','identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','foreignContactContextAccepted','visualAcceptance']);assert len(review['checkedNativeUids'])==5
 old=read(HERE/'local/government-xl-grand-aquarium-private-browser-v3-20261022/catalogue.json');final=read(STAGE/'catalogue.json');allowed={'sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview'}
 assert {m['uid']:m['sha256']for m in final['models']}==r['sourceSHA256ByUid']
 for a,b in zip(old['models'],final['models']):assert {k:v for k,v in a.items()if k not in allowed}=={k:v for k,v in b.items()if k not in allowed};assert not b.get('supportDependencies')and b['proceduralWindows']is False
 near=BASE/'government-xl-grand-aquarium-final-neighbours-v1-20261022';_,npins=authenticate(near);path=near/'neighbour-inputs.json.gz';assert digest(path.read_bytes())==npins[str(path.relative_to(ROOT))];rows=read(path)['rows'];keys={('building:'if x['building']['uid'].startswith('landsd/')else'form:')+x['building']['uid']for x in rows}|{'building:'+UID,'terrain:city/data/terrain.json','terrain:city/data/government-native-295518-0.json','immutable-source-proof:'+BATCH}
 refs=[ref(ROOT/p)for p in pins]+[ref(PREP/'result.json'),ref(Path(__file__)),ref(BROWSER),ref(near/'result.json'),ref(path)];return r,keys,refs

def restore(saved):
 errors=[]
 for rel,raw in sorted(saved.items(),key=lambda x:x[0]=='3d-viewer/city/data/manifest.json'):
  try:
   p=ROOT/rel
   if raw is None:p.unlink(missing_ok=True)
   else:tmp=p.with_name(p.name+'.aquarium-rollback-'+uuid.uuid4().hex);tmp.write_bytes(raw);os.replace(tmp,p)
  except BaseException as e:errors.append(dict(path=rel,error=repr(e)))
 return errors

def owned():
 with locked_publication(ROOT):
  lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prepared,keys,refs=inputs();assert keys<=set(lease['resources']);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=read(manifest);pointer=read(POINTER);oldmodels=[m for url in before['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];models=read(STAGE/'catalogue.json')['models'];assert len(oldmodels)==6840 and UID not in {m['uid']for m in oldmodels};assert len(models)==1;plan=read(STAGE/'plan.json');dry=read(PREP/'publisher-dry-run/publication-plan.json');assert not dry['published'];destination=plan['areas'][0]['destination'];assetDest=(ROOT/'3d-viewer'/destination).parent/models[0]['asset'];mutable=set(dry['after'])|set(MUTABLE_CURRENT)|{str(assetDest.relative_to(ROOT))};saved={p:(ROOT/p).read_bytes()if(ROOT/p).exists()else None for p in mutable};history=[];DOC.mkdir()
  for p,raw in saved.items():
   if raw is not None:
    archive=LOCAL/'historical-current'/p;archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(raw);history.append(dict(originalPath=p,originalSHA256=digest(raw),savedHistoricalBytes=ref(archive)))
  save(DOC/'historical-input-context.json',dict(preInstallSnapshot=pointer['snapshotId'],mutableCurrentByteSnapshots=history,originalEvidenceRefs=refs));sources=prepared['sourceSHA256ByUid'];acceptance=dict(uids=[UID],sourceSHA256ByUid=sources,sourcePlan=ref(PREP/'result.json'),sourceAcceptanceReview=prepared['sourceReview'],fixedXLDelta=prepared['delta'],newVisibleModels=1,existingModelReverification=prepared['existingModelReverification'],sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=1,rawWarningsRetained=True,publication=False,newlyInstalled=0);save(DOC/'acceptance.json',acceptance)
  inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']};m=models[0];old=parts.get(UID,{});parts[UID]=dict(uid=UID,name=m['label'],landmarkIds=old.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate=dict(sha256=m['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-source',knownHold=False);ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=hashlib.sha256(jobs.encode([ordered,acceptance]).encode()).hexdigest()[:16];invpath=POINTER.parent/('source-review-inventory-'+snapshot+'.json');save(invpath,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Original Grand Aquarium unchanged at1x/source pose; exact terrain coverage, four-stream exposed/hidden wall and bounded contact review, original plaza interface and complete current native/base scope, staged/live desktop/mobile review. No model geometry edits.'})
  sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
  ledger.seed(invpath,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path']);ledger.record_many(snapshot,LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json','Immutable original Aquarium source and scoped contact/hidden-face/current-neighbour reviews approved; live checks pending.',commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
  def call(command):
   assert reservations.owns(lease);run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200);save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=command,exitCode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0,run.stderr;assert reservations.owns(lease)
  installed_history=False
  try:
   for q in refs:check(q)
   @contextmanager
   def guard():
    with connect()as db:
     db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and keys<=set(live['resources']);check(prepared['currentManifest']);yield
   pub=module('aquarium_guarded_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/BATCH;pub.PUBLICATION_GUARD=guard;sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT)),'--apply'];pub.main()
   for rel,h in dry['after'].items():assert ref(ROOT/rel)['sha256']==h
   after=read(manifest);actual=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert actual==oldmodels+models and len(actual)==6841;assert after['tiles']==before['tiles']and after['counts']==before['counts'];assert digest(assetDest.read_bytes())==sources[UID];assert len(after['terrainPatches'])==len(before['terrainPatches']);assert not any(p['url']==prepared['terrainReplacement']['url']for p in after['terrainPatches']);assert [p for p in after['terrainPatches']if p['url']!=prepared['terrainDestination']]==[p for p in before['terrainPatches']if p['url']!=prepared['terrainReplacement']['url']]
   config=read(STAGE/'live-browser-config.json');reports=[];views=[]
   for width in [390,1280]:
    cfg={**config,'viewportWidths':[width],'failureTestUids':[UID],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};cfgpath=LOCAL/f'live-browser-{width}.json';save(cfgpath,cfg);call(['node',str(BROWSER),'live',str(cfgpath.relative_to(ROOT))]);report=read(DOC/str(width)/'live-browser.json');assert report['passed']and not report['errors'];v=[r for r in report['views']if 'time'in r];assert len(v)==2
    for r in v:assert r['fullyFramed']and r['solidAppearance']and r['active']and r['visible']and not r['fallbackFaces']and r['pick']==r['collision']==UID and r['sourceSHA256']==sources[UID]
    assert report['localJointViews']and all({r['uid']for r in j['models']}=={UID,'landsd/295518:0'}and all(r['active']and r['visible']and not r['fallbackFaces']for r in j['models'])for j in report['localJointViews'])
    if width==390:assert any(r.get('phase')=='failed-download'and r['fallbackRetained']for r in report['views'])
    reports.append(ref(DOC/str(width)/'live-browser.json'));views.extend(v)
   save(DOC/'live-browser.json',dict(passed=True,errors=[],views=views,reports=reports));installed={**acceptance,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'installedUids':[UID],'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json'),'completeCurrentCatalogueModels':6841};save(DOC/'installed-acceptance.json',installed);ledger.record_many(snapshot,LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json','Original Grand Aquarium installed unchanged; exact four-stream terrain coverage/hidden-wall/contact review, whole current actor scope and original plaza interface, staged/live desktop/mobile day/night, picking/collision and failure recovery pass.',commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot);installed_history=True
   assert read(POINTER)==pointer;save(POINTER,{**pointer,'snapshotId':snapshot,'inventory':ref(invpath)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]});call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',prepared['previousXLCount']['path'],'--batch',BATCH]);counts=read(DOC/'full-xl-current-count.json')['counts'];assert counts==dict(total=521,installedVerified=324,remaining=197)
   kind='grand-aquarium-original-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid;finalrefs={q['path']:q for q in refs if q['path']not in mutable}
   for p in [*[p for folder in [DOC,LOCAL,pub.DOC]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json'],*[ROOT/p for p in mutable if(ROOT/p).exists()],invpath]:finalrefs[str(p.relative_to(ROOT))]=ref(p)
   final={**installed,'jobId':jid,'evidenceRefs':list(finalrefs.values()),'historicalMutableByteSnapshots':history,'fullXLCurrentCounts':counts,'scriptExternalAICalls':0,'aiGeometryModelling':False}
   for q in final['evidenceRefs']:check(q)
   with connect()as db:
    db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(db,lease);assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
   with connect()as db:
    db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final);assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,UID)).fetchone()==('installed-verified',sources[UID])
   save(DOC/'result.json',final);save(DOC/'neon-sync.json',dict(jobId=jid,snapshotId=snapshot,resultVerified=True));print(dict(installed=UID,counts=counts,jobId=jid,snapshotId=snapshot),flush=True)
  except BaseException as e:
   errors=restore(saved);save(DOC/'failure-recovery.json',dict(error=repr(e),derivedInstalledHistoryRetained=installed_history,allPublicDestinationsRestored=not errors,rollbackErrors=errors));raise

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--owned',action='store_true');a=ap.parse_args()
 if a.owned:return owned()
 r,keys,refs=inputs()
 if not a.apply:print(dict(readyForGuardedApplication=True,newModels=[UID],publication=False));return
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('aquarium-install-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  lease=read(LEASE)
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
