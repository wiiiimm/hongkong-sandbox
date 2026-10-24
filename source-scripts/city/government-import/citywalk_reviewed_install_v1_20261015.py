"""Install one reviewed unchanged Citywalk source with guarded dependency migration."""
from pathlib import Path
import sys,json,subprocess,uuid,copy
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from primrose_compound_foundation_v2_20261015 import module
from publication_lock import locked_publication
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-reviewed-installed-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PREP=BASE/'government-xl-citywalk-reviewed-private-stage-v1-20261015';CHECKS=BASE/'government-xl-citywalk-reviewed-stage-checks-v2-20261015';STAGE=HERE/'accepted'/PREP.name
PUB=HERE/'citywalk_slot_preserving_guarded_publish_v1_20261015.py';BROWSER=HERE/'citywalk_joint_resolution_browser_v2_20261015.mjs';UID='landsd/134332:0'
PREVIOUS=BASE/'government-xl-polyu-original-installed-v1-20261015/full-xl-current-count.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify_browser(path):
 r=module('citywalk_installed_browser_guard',HERE/'integrate.py').browser_verified(path,{UID});v=[x for x in r['views']if 'time'in x];assert len(v)==4 and len(r['retainedNativeOwnViews'])==36
 assert all(x['selectionClosed']and x['fullyFramed']and x['fallbackFaces']==0 and all(o==1 for o in x['materialOpacities'])for x in v)
 assert all(x['active']and x['visible']and x['fullyFramed']and x['fallbackFaces']==0 for x in r['retainedNativeOwnViews']);return r

def owned():
 leasepath=LOCAL/'lease.json';lease=read(leasepath);assert reservations.owns(lease);paths=[Path(__file__),PUB,BROWSER,PREVIOUS];pins={}
 for folder in [PREP,CHECKS]:
  r=read(folder/'result.json');paths.append(folder/'result.json')
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 accepted=read(CHECKS/'acceptance.json');assert accepted['passed']and not accepted['publication'];verify_browser(CHECKS/'staged-browser.json')
 manifestp=ROOT/'3d-viewer/city/data/manifest.json';pointerp=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';before=manifestp.read_bytes();pointerbytes=pointerp.read_bytes();manifest=json.loads(before);pointer=json.loads(pointerbytes);assert digest(before)==accepted['currentManifestSHA256']
 plan=read(STAGE/'plan.json');assert ref(STAGE/'plan.json')==accepted['plan'];cat=read(STAGE/'catalogue.json');assert len(cat['models'])==1;model=cat['models'][0];assert model['uid']==UID
 old_models=[m for url in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(old_models)==6661 and UID not in {m['uid']for m in old_models}
 dep=read(ROOT/plan['dependencyReviews'][0]['path']);backups={ROOT/c['source']:(ROOT/c['source']).read_bytes()for c in dep['catalogues']};expected_old=copy.deepcopy(old_models);changes={c['uid']:c for c in dep['changes']}
 for m in expected_old:
  if m['uid']in changes:assert m.get('supportDependencies',[])==changes[m['uid']]['oldSupportDependencies'];m['supportDependencies']=changes[m['uid']]['supportDependencies']
 DOC.mkdir();save(LOCAL/'manifest-before.json',manifest);save(LOCAL/'pointer-before.json',pointer)
 for i,(p,raw)in enumerate(backups.items()):(LOCAL/f'catalogue-before-{i}.json').write_bytes(raw)
 def call(cmd):
  i=len(list(DOC.glob('command-*.log')))
  with(DOC/f'command-{i}.log').open('w')as log:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=2400)
  assert reservations.owns(lease);assert r.returncode==0,(i,r.returncode)
 decision={**accepted,'batch':BATCH,'evidence':{'review':ref(PREP/'ROOT-functional-review.json'),'stage':ref(PREP/'result.json'),'checks':ref(CHECKS/'result.json'),'browser':ref(CHECKS/'staged-browser.json'),'plan':ref(STAGE/'plan.json')},'sourceSHA256':model['sha256'],'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'modelGeometryChanges':0,'scriptExternalAICalls':0};save(DOC/'acceptance.json',decision)
 publication=[sys.executable,str(PUB),str((STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(leasepath),'--phase',BATCH];call(publication);assert manifestp.read_bytes()==before
 inv=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inv['parts']};old=parts.get(UID,{})
 parts[UID]=dict(uid=UID,name=model['label'],landmarkIds=old.get('landmarkIds',[]),objectId=model['objectId'],csuid=model['buildingCSUID'],candidate={'sha256':model['sha256']},sourceProgress='prepared-for-review',classification='script-verified-original-source-functional-assembly',knownHold=False)
 ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];invpath=pointerp.parent/('source-review-inventory-'+snapshot+'.json');save(invpath,{**inv,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Original Citywalk, full current foundation/runtime/parent-neighbour checks and exact source-functional tower-junction review. Original294 strict failures preserved, no threshold or model geometry changes.'})
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 ledger.seed(invpath,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=str((DOC/'acceptance.json').relative_to(ROOT)))
 ledger.record_many(snapshot,leasepath,[(UID,'approved-for-integration',DOC/'acceptance.json','Exact original source accepted with source-functional junction review; current geometry/runtime/staged checks pass; live pending.',commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 cfg=read(HERE/'local'/CHECKS.name/'browser-config.json');cfg['doc']=str(DOC.relative_to(ROOT))+'/';save(LOCAL/'browser-config.json',cfg)
 try:
  call(publication+['--apply']);call(['node',str(BROWSER),'live',str((LOCAL/'browser-config.json').relative_to(ROOT))]);verify_browser(DOC/'live-browser.json')
  after=read(manifestp);destination=plan['areas'][0]['destination'];assert after['officialModelCatalogues']==manifest['officialModelCatalogues']+[destination];new_models=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert new_models==expected_old+[model]and len(new_models)==6662
  terrain=plan['topLevelTerrainPatches'][0];slot=next(i for i,r in enumerate(manifest['terrainPatches'])if r['url']==terrain['replaces']['url']);assert after['terrainPatches'][slot]['url']==terrain['destination'];assert [r for i,r in enumerate(after['terrainPatches'])if i!=slot]==[r for i,r in enumerate(manifest['terrainPatches'])if i!=slot]
  assert ref(ROOT/'3d-viewer'/terrain['destination'])['sha256']==terrain['sha256'];assert ref((ROOT/'3d-viewer'/destination).parent/model['asset'])['sha256']==model['sha256']
  mutable={str(p.relative_to(ROOT))for p in backups}|{'3d-viewer/city/data/manifest.json','docs/astra-city/model-integration-20260909/current-source-review.json','3d-viewer/city/data/building-progress.json'}
  for p,h in pins.items():
   if p not in mutable:assert digest((ROOT/p).read_bytes())==h,p
  installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'manifest':ref(manifestp),'liveBrowser':ref(DOC/'live-browser.json')};save(DOC/'installed-acceptance.json',installed)
  ledger.record_many(snapshot,leasepath,[(UID,'installed-verified',DOC/'installed-acceptance.json','Original Citywalk installed unchanged; all current and staged/live checks pass. Five existing dependencies updated; raw294 lower-facade junction failures remain exact under scoped review. No AI geometry modelling.',commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
  assert pointerp.read_bytes()==pointerbytes;save(pointerp,{**pointer,'snapshotId':snapshot,'inventory':str(invpath.relative_to(ROOT)),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
  call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',str(PREVIOUS.relative_to(ROOT)),'--batch',BATCH]);counts=read(DOC/'full-xl-current-count.json')['counts'];assert counts=={'total':521,'installedVerified':243,'remaining':278},counts
  kind='citywalk-reviewed-original-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
  result={**installed,'jobId':jid,'uids':[UID],'installedUids':[UID],'fullXLCurrentCounts':counts,'totalOriginalCatalogueModels':6662,'dependencyChanges':5,'evidenceRefs':[ref(p)for p in [DOC/'acceptance.json',DOC/'installed-acceptance.json',DOC/'live-browser.json',DOC/'full-xl-current-count.json',PREP/'result.json',CHECKS/'result.json',invpath,manifestp,ROOT/'3d-viewer'/destination,ROOT/'3d-viewer'/terrain['destination'],Path(__file__)]]}
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(db,lease)
   assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result);assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,UID)).fetchone()==('installed-verified',model['sha256'])
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot));print(dict(installed=UID,snapshotId=snapshot,jobId=jid,counts=counts),flush=True)
 except BaseException as e:
  manifestp.write_bytes(before);pointerp.write_bytes(pointerbytes)
  for p,raw in backups.items():p.write_bytes(raw)
  save(DOC/'failure-recovery.json',dict(error=repr(e),manifestRestored=True,dependencyCataloguesRestored=True,reviewPointerRestored=True,ledgerHistoryPreserved=True,installedCreditGranted=False))
  for cmd in [[sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'],['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]]:subprocess.run(cmd,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
  raise

def main():
 if '--owned'in sys.argv:
  with locked_publication(ROOT):return owned()
 assert not DOC.exists()and not LOCAL.exists();assert read(CHECKS/'acceptance.json')['passed'];scope=read(BASE/'government-xl-citywalk-complete-current-scope-v1-20261015/scope.json.gz');uids=[UID]+[r['uid']for r in scope['nominatedNativeActors']];claim=reservations.claim('citywalk-install-'+str(uuid.uuid4()),['building:'+u for u in uids]+['terrain-patch:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'lease.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'lease.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
