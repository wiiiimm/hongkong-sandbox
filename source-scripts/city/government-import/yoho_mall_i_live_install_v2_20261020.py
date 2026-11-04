"""Exact Yoho Mall I and seven Grand Yoho towers assembly publication with rollback, live browser and pinned installed ledger."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
from aqua_original_image_review_binding_v1_20261014 import MUTABLE_CURRENT
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-original-installed-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PREP=BASE/'government-xl-yoho-mall-i-qualified-publication-plan-v1-20261020';STAGE=HERE/'accepted'/PREP.name;POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';BROWSER=HERE/'yoho_mall_i_settled_joint_browser_v1_20261020.mjs';UIDS=['landsd/189427:0','landsd/294811:0','landsd/294810:0','landsd/294854:0','landsd/294855:0','landsd/294857:0','landsd/294856:0','landsd/294858:0'];REVIEW=BASE/'government-xl-yoho-mall-i-qualified-publication-plan-v1-20261020'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def inputs():
 r=read(PREP/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs={q['path']:q for q in r['evidenceRefs']}
 for p in [PREP/'result.json',Path(__file__),BROWSER]:refs[str(p.relative_to(ROOT))]=ref(p)
 for q in refs.values():check(q)
 plan=read(PREP/'publication-plan.json');assert r['qualifiedForLiveVerification'] and plan['newVisibleModels']==8 and plan['delta']['expectedFixedXLDelta']>0
 assert set(plan['newModels'])==set(UIDS) and len(plan['existingModelReverification'])==7;assert read(REVIEW/'ROOT-SOURCE-REVIEW.json')['originalSourceReviewAccepted']

 for width in [390,1280]:
  d=BASE/'government-xl-yoho-mall-i-final-staged-browser-v1-20261020'/str(width);p=d/'staged-browser.json';report=read(p);assert report['passed'] and not report['errors'];refs[str(p.relative_to(ROOT))]=ref(p)
  views=[v for v in report['views'] if 'time' in v];assert len(views)==16
  for v in views:assert v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces'] and v['sourceSHA256']==plan['sourceSHA256ByUid'][v['uid']] and v['pick']==v['collision']==v['uid']
  if width==390:assert {v['uid'] for v in report['views'] if v.get('phase')=='failed-download' and v['fallbackRetained']}==set(UIDS)
  for p in d.glob('*.png'):refs[str(p.relative_to(ROOT))]=ref(p)
 n=BASE/'government-xl-yoho-mall-i-neighbours-v2-20261020';r=read(n/'result.json');p=n/'neighbour-inputs.json.gz';assert ref(p) in r['evidenceRefs']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p in [n/'result.json',p]:refs[str(p.relative_to(ROOT))]=ref(p)
 near=read(BASE/'government-xl-yoho-mall-i-neighbour-review-v3-20261020/ROOT-NEIGHBOUR-REVIEW.json');expected={v['uid']:v['sourceSHA256'] for v in near['verifiedInstalledSources']};found={}
 for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
  catpath=ROOT/'3d-viewer'/url
  for m in read(catpath)['models']:
   if m['uid'] in expected:
    p=catpath.parent/m['asset'];assert m['sha256']==digest(p.read_bytes())==expected[m['uid']];found[m['uid']]=m['sha256'];refs[str(p.relative_to(ROOT))]=ref(p)
 assert found==expected
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for uid,sha in expected.items():assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(near['currentSnapshotId'],uid)).fetchone()==('installed-verified',sha)
 return plan,list(refs.values())
def atomic(p,raw):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.yoho-mall-i-'+uuid.uuid4().hex);tmp.write_bytes(raw);os.replace(tmp,p)
def owned():
 with locked_publication(ROOT):
  lease=read(LEASE);assert reservations.owns(lease);assert not DOC.exists();plan,refs=inputs();assert set(resources(plan))<=set(lease['resources']);pointer=read(POINTER);cat=read(STAGE/'catalogue.json');models=cat['models'];sources=plan['sourceSHA256ByUid'];assert {m['uid']:m['sha256'] for m in models}==sources
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=read(manifest);old=[m for url in before['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']];assert len(old)==len({m['uid'] for m in old}) and set(UIDS)&{m['uid'] for m in old}==set()
  for edit in plan['edits']:
   check(edit['source']);p=ROOT/edit['destination'];assert (digest(p.read_bytes()) if p.exists() else None)==edit['beforeSHA256']
  for a in plan['assets']:check(a['source']);assert not (ROOT/a['destination']).exists()
  DOC.mkdir();mutable=set(MUTABLE_CURRENT)|{x['destination'] for x in plan['edits']+plan['assets']};saved={p:(ROOT/p).read_bytes() if (ROOT/p).exists() else None for p in mutable};history=[]
  for p,raw in saved.items():
   if raw is not None:
    archive=LOCAL/'historical-current'/p;archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(raw);history.append(dict(originalPath=p,originalSHA256=digest(raw),savedHistoricalBytes=ref(archive)))
  save(DOC/'historical-input-context.json',dict(preInstallSnapshot=pointer['snapshotId'],mutableCurrentByteSnapshots=history,originalEvidenceRefs=refs))
  config=read(STAGE/'live-browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';save(LOCAL/'browser-config.json',config)
  acceptance=dict(uids=UIDS,sourceSHA256ByUid=sources,sourcePlan=ref(PREP/'result.json'),sourceAcceptanceReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),fixedXLDelta=plan['delta'],newVisibleModels=8,existingModelReverification=plan['existingModelReverification'],sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=1,publication=False,newlyInstalled=0);save(DOC/'acceptance.json',acceptance)
  inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']}
  for m in models:
   oldpart=parts.get(m['uid'],{});parts[m['uid']]=dict(uid=m['uid'],name=m.get('label') or m['uid'],landmarkIds=oldpart.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate=dict(sha256=m['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-source',knownHold=False)
  ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=hashlib.sha256(jobs.encode([ordered,acceptance]).encode()).hexdigest()[:16];invpath=POINTER.parent/('source-review-inventory-'+snapshot+'.json');save(invpath,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Yoho Mall I and seven Grand Yoho towers unchanged original assembly; exact source-boundary identity review, source-specific wall support/complete foundations, finite terrain and desktop/mobile evidence. Eight immutable originals with exact mall support dependencies; reviewed replacement terrain preserves all retained originals.'})
  sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
  ledger.seed(invpath,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path']);ledger.record_many(snapshot,LEASE,[(m['uid'],'approved-for-integration',DOC/'acceptance.json','Exact original Yoho Mall I and seven Grand Yoho towers source and full staged acceptance approved; live verification pending.',commit) for m in models],effort=effort,request_id=BATCH+'-approved-'+snapshot)
  def call(cmd):
   assert reservations.owns(lease)
   run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
   save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=cmd,exitCode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0,run.stderr;assert reservations.owns(lease)
  installed_history=False
  try:
   for q in refs:check(q)
   for a in plan['assets']:atomic(ROOT/a['destination'],(ROOT/a['source']['path']).read_bytes())
   for edit in plan['edits']:atomic(ROOT/edit['destination'],(ROOT/edit['source']['path']).read_bytes())
   after=read(manifest);actual=[m for url in after['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']];assert len(actual)==plan['newRuntimeCount']==len(old)+8 and len({m['uid'] for m in actual})==len(actual)
   assert {m['uid']:m for m in actual if m['uid'] not in sources}=={m['uid']:m for m in old if m['uid'] not in sources};assert {m['uid']:m for m in actual if m['uid'] in sources}=={m['uid']:m for m in models};assert after==read(STAGE/'manifest.json') and after['tiles']==before['tiles'] and after['counts']==before['counts']
   replacement=plan['terrainReplacement'];oldpatch=[p for p in before['terrainPatches'] if p['url']==replacement['url']];assert len(oldpatch)==1 and oldpatch[0]['sha256']==replacement['sha256']
   assert [p for p in after['terrainPatches'] if p['url']!=plan['terrainDestination']]==[p for p in before['terrainPatches'] if p['url']!=replacement['url']]
   assert len(after['terrainPatches'])==len(before['terrainPatches']) and not any(p['url']==replacement['url'] for p in after['terrainPatches'])
   for a in plan['assets']:assert digest((ROOT/a['destination']).read_bytes())==a['source']['sha256']
   allviews=[];alljoints=[];browserrefs=[]
   for width in [390,1280]:
    cfg={**config,'viewportWidths':[width],'failureTestUids':UIDS,'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};cfgpath=LOCAL/f'live-browser-{width}.json';save(cfgpath,cfg)
    call(['node',str(BROWSER),'live',str(cfgpath.relative_to(ROOT))]);report=read(DOC/str(width)/'live-browser.json');assert report['passed']and not report['errors'];browserrefs.append(ref(DOC/str(width)/'live-browser.json'));views=[v for v in report['views']if 'time'in v];assert len(views)==16
    for v in views:assert v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
    for joint in report['jointViews']:
     assert {m['uid']for m in joint['models']}=={joint['selectedUid'],'landsd/189427:0'}
     for m in joint['models']:assert m['active']and m['visible']and not m['fallbackFaces']and m['sourceSHA256']==sources[m['uid']]
    if width==390:
     failures=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failures)==8 and {v['uid']for v in failures}==set(UIDS)and all(v['fallbackRetained']for v in failures)
    else:assert len(report['jointViews'])==8
    allviews.extend(views);alljoints.extend(report['jointViews'])
   save(DOC/'live-browser.json',dict(passed=True,errors=[],views=allviews,jointViews=alljoints,reports=browserrefs))
   installed={**acceptance,'snapshotId':snapshot,'publication':True,'newlyInstalled':plan['delta']['expectedFixedXLDelta'],'newlyVerifiedModels':8,'installedUids':UIDS,'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json'),'completeCurrentCatalogueModels':len(actual)};save(DOC/'installed-acceptance.json',installed)
   ledger.record_many(snapshot,LEASE,[(m['uid'],'installed-verified',DOC/'installed-acceptance.json','Yoho Mall I and seven Grand Yoho towers unchanged original assembly: exact source-boundary identity, source-specific wall support, foundations, finite clearance, staged/live desktop/mobile and failed-support retry passed.',commit) for m in models],effort=effort,request_id=BATCH+'-installed-'+snapshot);installed_history=True
   assert read(POINTER)==pointer;save(POINTER,{**pointer,'snapshotId':snapshot,'inventory':ref(invpath)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
   call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',str(ROOT/plan['previousXLCount']['path']),'--batch',BATCH]);counts=read(DOC/'full-xl-current-count.json')['counts'];assert counts==dict(total=521,installedVerified=plan['delta']['previousInstalled']+plan['delta']['expectedFixedXLDelta'],remaining=521-plan['delta']['previousInstalled']-plan['delta']['expectedFixedXLDelta'])
   stage='yoho-mall-i-original-tower-installed-v1';jid=jobs.enqueue(BATCH,stage,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
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
   save(DOC/'result.json',final);save(DOC/'neon-sync.json',dict(jobId=jid,snapshotId=snapshot,resultVerified=True));print(dict(installed=UIDS,newVisibleModels=8,counts=counts,jobId=jid),flush=True)
  except BaseException as e:
   errors=[]
   for path,raw in sorted(saved.items(),key=lambda x:x[0]=='3d-viewer/city/data/manifest.json'):
    try:
     if raw is None:(ROOT/path).unlink(missing_ok=True)
     else:atomic(ROOT/path,raw)
    except BaseException as err:errors.append(dict(path=path,error=repr(err)))
   save(DOC/'failure-recovery.json',dict(error=repr(e),derivedInstalledHistoryRetained=installed_history,currentPointerRestoredNotDerivedCredit=True,rollbackErrors=errors,allPublicDestinationsRestored=not errors));raise

def resources(plan):
 rows=read(BASE/'government-xl-yoho-mall-i-neighbours-v2-20261020/neighbour-inputs.json.gz')['rows']
 uids={r['building']['uid'] for r in rows}|set(UIDS)|set(plan['existingModelReverification'])
 return sorted([('building:' if u.startswith('landsd/') else 'form:')+u for u in uids]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH])

def main():
 if '--owned' in sys.argv:return owned()
 plan,refs=inputs();assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim('yoho-mall-i-install-'+str(uuid.uuid4()),resources(plan),batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  lease=read(LEASE)
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
