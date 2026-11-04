"""Exact West Wing assembly publication with rollback, live browser and pinned installed ledger."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
from aqua_original_image_review_binding_v1_20261014 import MUTABLE_CURRENT
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-original-installed-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PREP=BASE/'government-xl-west-wing-qualified-publication-plan-v1-20261018';STAGE=HERE/'accepted'/PREP.name;POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';BROWSER=HERE/'west_wing_assembly_browser_v3_20261018.mjs';UIDS=['landsd/26195:0','landsd/322270:0','landsd/315069:0','landsd/319534:0'];REVIEW=BASE/'government-xl-west-wing-source-review-v1-20261018'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def inputs():
 r=read(PREP/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs={q['path']:q for q in r['evidenceRefs']}
 for p in [PREP/'result.json',Path(__file__),BROWSER,HERE/'west_wing_dependency_fallback_browser_v1_20261018.mjs']:refs[str(p.relative_to(ROOT))]=ref(p)
 for q in refs.values():check(q)
 plan=read(PREP/'publication-plan.json');assert r['qualifiedForLiveVerification'] and plan['newVisibleModels']==0 and plan['delta']['expectedFixedXLDelta']>0
 assert plan['newModels']==[] and set(plan['existingModelReverification'])==set(UIDS);assert read(REVIEW/'ROOT-SOURCE-REVIEW.json')['originalSourceReviewAccepted']
 return plan,list(refs.values())
def atomic(p,raw):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.west-wing-'+uuid.uuid4().hex);tmp.write_bytes(raw);os.replace(tmp,p)
def owned():
 with locked_publication(ROOT):
  lease=read(LEASE);assert reservations.owns(lease);assert not DOC.exists();plan,refs=inputs();pointer=read(POINTER);cat=read(STAGE/'catalogue.json');models=cat['models'];sources=plan['sourceSHA256ByUid'];assert {m['uid']:m['sha256'] for m in models}==sources
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=read(manifest);old=[m for url in before['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']];assert len(old)==len({m['uid'] for m in old}) and set(UIDS)<={m['uid'] for m in old}
  for edit in plan['edits']:
   check(edit['source']);p=ROOT/edit['destination'];assert (digest(p.read_bytes()) if p.exists() else None)==edit['beforeSHA256']
  for a in plan['assets']:check(a['source']);assert not (ROOT/a['destination']).exists()
  DOC.mkdir();mutable=set(MUTABLE_CURRENT)|{x['destination'] for x in plan['edits']+plan['assets']};saved={p:(ROOT/p).read_bytes() if (ROOT/p).exists() else None for p in mutable};history=[]
  for p,raw in saved.items():
   if raw is not None:
    archive=LOCAL/'historical-current'/p;archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(raw);history.append(dict(originalPath=p,originalSHA256=digest(raw),savedHistoricalBytes=ref(archive)))
  save(DOC/'historical-input-context.json',dict(preInstallSnapshot=pointer['snapshotId'],mutableCurrentByteSnapshots=history,originalEvidenceRefs=refs))
  config=read(STAGE/'live-browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';save(LOCAL/'browser-config.json',config)
  acceptance=dict(uids=UIDS,sourceSHA256ByUid=sources,sourcePlan=ref(PREP/'result.json'),sourceAcceptanceReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),fixedXLDelta=plan['delta'],newVisibleModels=0,existingModelReverification=UIDS,sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=1,publication=False,newlyInstalled=0);save(DOC/'acceptance.json',acceptance)
  inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']}
  for m in models:
   oldpart=parts.get(m['uid'],{});parts[m['uid']]=dict(uid=m['uid'],name=m.get('label') or m['uid'],landmarkIds=oldpart.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate=dict(sha256=m['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-source',knownHold=False)
  ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=hashlib.sha256(jobs.encode([ordered,acceptance]).encode()).hexdigest()[:16];invpath=POINTER.parent/('source-review-inventory-'+snapshot+'.json');save(invpath,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'West Wing unchanged original assembly; exact source-boundary identity review, strict support/complete foundations, finite terrain and desktop/mobile evidence. Four legacy original entries reverified with reviewed regional terrain.'})
  sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
  ledger.seed(invpath,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path']);ledger.record_many(snapshot,LEASE,[(m['uid'],'approved-for-integration',DOC/'acceptance.json','Exact original West Wing source and full staged acceptance approved; live verification pending.',commit) for m in models],effort=effort,request_id=BATCH+'-approved-'+snapshot)
  def call(cmd):
   assert reservations.owns(lease)
   run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
   save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=cmd,exitCode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0,run.stderr;assert reservations.owns(lease)
  installed_history=False
  try:
   for q in refs:check(q)
   for a in plan['assets']:atomic(ROOT/a['destination'],(ROOT/a['source']['path']).read_bytes())
   for edit in plan['edits']:atomic(ROOT/edit['destination'],(ROOT/edit['source']['path']).read_bytes())
   after=read(manifest);actual=[m for url in after['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']];assert len(actual)==plan['newRuntimeCount']==len(old) and len({m['uid'] for m in actual})==len(actual)
   assert {m['uid']:m for m in actual if m['uid'] not in sources}=={m['uid']:m for m in old if m['uid'] not in sources};assert {m['uid']:m for m in actual if m['uid'] in sources}=={m['uid']:m for m in models};assert after==read(STAGE/'manifest.json') and after['tiles']==before['tiles'] and after['counts']==before['counts']
   for a in plan['assets']:assert digest((ROOT/a['destination']).read_bytes())==a['source']['sha256']
   call(['node',str(BROWSER),'live',str((LOCAL/'browser-config.json').relative_to(ROOT))]);report=read(DOC/'live-browser.json');assert report['passed'] and not report['errors'];views=[v for v in report['views'] if 'time' in v];assert len(views)==16
   for v in views:assert v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces'] and v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==sources[v['uid']]
   assert len(report['jointViews'])==8 and len(report['retainedNativeOwnViews'])==36
   for v in report['jointViews']:
    assert {m['uid']:m['sourceSHA256'] for m in v['models']}==sources
    assert next(m for m in v['models']if m['uid']==v['selectedUid'])['active']
   fallbackconfig={**config,'doc':str((DOC/'fallback').relative_to(ROOT))+'/','viewportWidths':[390],'failureTestUids':UIDS,'fallbackOnly':True,'jointUids':[],'retainedBuildingUidsByModel':{},'nativeSupportUidsByModel':{}};save(LOCAL/'fallback-config.json',fallbackconfig)
   call(['node',str(HERE/'west_wing_dependency_fallback_browser_v1_20261018.mjs'),'live',str((LOCAL/'fallback-config.json').relative_to(ROOT))]);fallback=read(DOC/'fallback/live-browser.json');assert fallback['passed']and not fallback['errors']and len(fallback['views'])==4 and all(v['fallbackRetained']and v['fallbackFaces']>0 for v in fallback['views'])
   installed={**acceptance,'snapshotId':snapshot,'publication':True,'newlyInstalled':plan['delta']['expectedFixedXLDelta'],'newlyVerifiedModels':4,'installedUids':UIDS,'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json'),'completeCurrentCatalogueModels':len(actual)};save(DOC/'installed-acceptance.json',installed)
   ledger.record_many(snapshot,LEASE,[(m['uid'],'installed-verified',DOC/'installed-acceptance.json','West Wing unchanged original assembly: exact source-boundary identity, strict support, foundations, finite clearance, staged/live desktop/mobile and failed-support retry passed.',commit) for m in models],effort=effort,request_id=BATCH+'-installed-'+snapshot);installed_history=True
   assert read(POINTER)==pointer;save(POINTER,{**pointer,'snapshotId':snapshot,'inventory':ref(invpath)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
   call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',str(ROOT/plan['previousXLCount']['path']),'--batch',BATCH]);counts=read(DOC/'full-xl-current-count.json')['counts'];assert counts==dict(total=521,installedVerified=plan['delta']['previousInstalled']+plan['delta']['expectedFixedXLDelta'],remaining=521-plan['delta']['previousInstalled']-plan['delta']['expectedFixedXLDelta'])
   stage='west-wing-four-originals-installed-v1';jid=jobs.enqueue(BATCH,stage,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
   finalrefs={q['path']:q for q in refs if q['path'] not in mutable}
   for p in [*[p for d in [DOC,LOCAL] for p in d.rglob('*') if p.is_file() and p.name!='reservation.json'],*[ROOT/p for p in mutable if (ROOT/p).exists()],invpath]:finalrefs[str(p.relative_to(ROOT))]=ref(p)
   final={**installed,'jobId':jid,'evidenceRefs':list(finalrefs.values()),'historicalMutableByteSnapshots':history,'fullXLCurrentCounts':counts,'scriptExternalAICalls':0,'aiGeometryModelling':False}
   for q in final['evidenceRefs']:check(q)
   with connect() as c:
    c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
    assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
    for u,s in sources.items():assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,u)).fetchone()==('installed-verified',s)
   save(DOC/'result.json',final);save(DOC/'neon-sync.json',dict(jobId=jid,snapshotId=snapshot,resultVerified=True));print(dict(installed=UIDS,newVisibleModels=0,counts=counts,jobId=jid),flush=True)
  except BaseException as e:
   errors=[]
   for path,raw in sorted(saved.items(),key=lambda x:x[0]=='3d-viewer/city/data/manifest.json'):
    try:
     if raw is None:(ROOT/path).unlink(missing_ok=True)
     else:atomic(ROOT/path,raw)
    except BaseException as err:errors.append(dict(path=path,error=repr(err)))
   save(DOC/'failure-recovery.json',dict(error=repr(e),derivedInstalledHistoryRetained=installed_history,currentPointerRestoredNotDerivedCredit=True,rollbackErrors=errors,allPublicDestinationsRestored=not errors));raise

def main():
 if '--owned' in sys.argv:return owned()
 plan,refs=inputs();assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim('west-wing-install-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  lease=read(LEASE)
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
