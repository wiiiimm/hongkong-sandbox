"""UNEXECUTED root-only atomic Twin2+Evangel1 original publication draft.

Two canonical replay rounds precede pending ledger state. After the single
apply, unchanged numeric tuples replay under their original canonical binding
and the new scene is checked separately as exactly two catalogues/two patches.
"""
import argparse,copy,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from urllib.request import urlopen
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
import twin_evangel_atomic_three_separation_replay_v1_20261011 as guards
UIDS={'landsd/222465:0','landsd/223206:0','landsd/91306:0'}
TWIN_UIDS={'landsd/222465:0','landsd/223206:0'};EVANGEL='landsd/91306:0';PODIUM='landsd/223206:0'
CURRENT='df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e';PREVIOUS_SNAPSHOT='d1e8ae25a53de08b'
TWIN_SCRIPT=HERE/'xl-terrain-recovery-20261011-twin-regency-two-private-stage-v1.py'
EVANGEL_SCRIPT=HERE/'xl-evangel-college-91306-unchanged-private-stage-v3-20261011.py'
BROWSER=HERE/'xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs'
BATCH='government-xl-twin-regency-evangel-three-atomic-installed-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
SUPPLEMENT=ROOT/'docs/astra-city/government-import/government-xl-twin-regency-supplementary-podium-camera-v1-20261011'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ready():
 with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200 and len(r.read())>100

def browser(doc,name,uids,config):
 report=module('atomic_three_browser_validator',HERE/'integrate.py').browser_verified(doc/name,uids)
 assert report['passed']is True and report['errors']==[] and not report.get('retainedNativeOwnViews')
 normal=[v for v in report['views']if 'time'in v];failed=[v for v in report['views']if v.get('phase')=='failed-download']
 assert len(report['views'])==5*len(uids) and len(normal)==4*len(uids)
 assert {(v['uid'],v['width'],v['time'])for v in normal}=={(u,w,t)for u in uids for w in [1280,390]for t in ['15:00','22:00']}
 assert len(failed)==len(uids) and {v['uid']for v in failed}==uids
 assert all(v['width']==390 and v['fallbackRetained']is True for v in failed)
 for uid in uids:
  f=next(i for i,v in enumerate(report['views'])if v['uid']==uid and v.get('phase')=='failed-download')
  retry=[(i,v)for i,v in enumerate(report['views'])if v['uid']==uid and v['width']==390 and 'time'in v]
  assert len(retry)==2 and all(i>f and v['active']and v['visible']for i,v in retry)
 for v in normal:
  assert set(v['nativeSupports'])==set(config.get('nativeSupportUidsByModel',{}).get(v['uid'],[]))
  assert all(s['active']and s['visible']and s.get('declaredCandidateSupport')and s['fallbackFaces']==0 for s in v['nativeSupports'].values())
 return report

def recheck(twin,evangel,folder):
 rows,identities,tr=twin.recheck(folder/'twin');er,entry,row=evangel.recheck(folder/'evangel')
 assert {r['uid']for r in rows}==TWIN_UIDS and row['uid']==EVANGEL
 assert tr['currentManifest']['sha256']==er['currentManifest']['sha256']==CURRENT
 assert tr['currentTypedPhysicalAccepted']and er['currentTypedPhysicalAccepted']and tr['reasons']==er['reasons']==[]
 assert tr['completeOriginalFaces']==13519 and tr['completeOriginalNonzeroBodies']==1120
 assert er['completeOriginalFaces']==13960 and er['completeRealComponents']==226
 assert not tr['installationApproved']and not er['installationApproved']and tr['nativeReacceptance']is False
 return rows,entry,row,tr,er

def owned(args,twin,evangel):
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();ready();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==CURRENT;original=json.loads(before)
 rows,eentry,erow,tr,er=recheck(twin,evangel,LOCAL/'initial-current-recheck')
 stages=[twin,evangel];configs=[read(s.STAGE/'browser-config.json')for s in stages]
 stagecats=[read(s.STAGE/'catalogue.json')for s in stages];plans=[read(s.STAGE/'plan.json')for s in stages]
 assert {e['uid']for c in stagecats for e in c['models']}==UIDS
 assert stagecats[1]['models']==[eentry]and not eentry['supportDependencies']
 acceptance_pins=[]
 for s,uids,config in zip(stages,[TWIN_UIDS,{EVANGEL}],configs):
  acceptance=read(s.DOC/'acceptance.json')
  assert acceptance['passed']and acceptance['checksPassed']and not acceptance['publication']
  assert acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==0 and acceptance['terrainProposalGeometryChanged']is True
  assert acceptance['stagedBrowser']==ref(s.DOC/'staged-browser.json');browser(s.DOC,'staged-browser.json',uids,config)
  for pin in acceptance['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
  acceptance_pins += acceptance['evidenceRefs']+[ref(s.DOC/'acceptance.json'),ref(s.DOC/'staged-browser.json')]
  assert len(plans[stages.index(s)]['areas'])==len(plans[stages.index(s)]['topLevelTerrainPatches'])==1
 supplementary=read(SUPPLEMENT/'supplementary-witness.json');assert supplementary['passed']and not supplementary['publication']and supplementary['originalStageReceiptUnchanged']
 for pin in supplementary['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 # Both original stage catalogues stay byte-identical. Only the recorded Twin
 # candidate support state becomes installed in a separate publication clone.
 publication_root=LOCAL/'publication-twin-catalogue';publication_cat=copy.deepcopy(stagecats[0]);te=next(e for e in publication_cat['models']if e['uid']=='landsd/222465:0');pe=next(e for e in publication_cat['models']if e['uid']==PODIUM)
 expected_dependency=dict(uid=PODIUM,csuid=pe['buildingCSUID'],sha256=pe['sha256'],state='candidate')
 assert te['supportDependencies']==[expected_dependency]and pe['supportDependencies']==[]
 te['supportDependencies'][0]['state']='installed';normalized=copy.deepcopy(publication_cat)
 next(e for e in normalized['models']if e['uid']=='landsd/222465:0')['supportDependencies'][0]['state']='candidate'
 assert normalized==stagecats[0]
 for e in publication_cat['models']:
  source=twin.STAGE/e['asset'];target=publication_root/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());assert ref(target)['sha256']==e['sha256']
 save(publication_root/'catalogue.json',publication_cat)
 (publication_root/'source-forms.json').write_bytes((twin.STAGE/'source-forms.json').read_bytes())
 save(DOC/'exact-candidate-support-state-publication.json',dict(stageCatalogue=ref(twin.STAGE/'catalogue.json'),publicationCatalogue=ref(publication_root/'catalogue.json'),onlyChangedField='models/T2/supportDependencies/0/state',before='candidate',after='installed',uid=PODIUM,csuid=pe['buildingCSUID'],sourceSHA256=pe['sha256'],allOtherFieldsExact=True))
 atomic=dict(areas=[{**plans[0]['areas'][0],'catalogue':ref(publication_root/'catalogue.json')['path']},plans[1]['areas'][0]],topLevelTerrainPatches=[p['topLevelTerrainPatches'][0]for p in plans])
 destinations=[a['destination']for a in atomic['areas']];assert len(set(destinations))==2
 assert all(not(ROOT/'3d-viewer'/d).exists()for d in destinations+[p['destination']for p in atomic['topLevelTerrainPatches']])
 separation=guards.separation(twin,evangel,rows,erow);save(DOC/'complete-mutual-source-and-routing-domain-separation.json',separation)
 math=guards.prepare_math(tr,er);save(DOC/'preapply-immutable-math-replay.json',dict(bothCanonicalReplaysPassed=True,originalManifestSHA256=CURRENT,exactTwinResult=tr['completeFourStreamRoleComposition'],exactEvangelResult=math['evangelExpected']))
 old_entries={};old_pins=[ref(manifest),ref(ROOT/'3d-viewer/city/data/terrain.json')]
 for url in original['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;old_pins.append(ref(path))
  for e in read(path)['models']:
   assert e['uid']not in old_entries;old_entries[e['uid']]=e;old_pins.append(ref(path.parent/e['asset']))
 assert len(old_entries)==6645 and not UIDS&set(old_entries)
 for item in original.get('terrainPatches',[]):old_pins.append(ref(ROOT/'3d-viewer'/item['url']))
 for tile in original['tiles']:old_pins.append(ref(ROOT/'3d-viewer'/tile['url']))
 roles=[tr,er];role_receipts=[read(s.ROLE/'result.json')for s in stages]
 for receipt in role_receipts:
  for pin in receipt['evidenceRefs']:
   assert ref(ROOT/pin['path'])==pin;old_pins.append(pin)
 for role in roles:
  old_pins+=role.get('completeCurrentCatalogueRefs',[])
 for pin in old_pins:assert ref(ROOT/pin['path'])==pin
 old_pins=list({(p['path'],p['sha256']):p for p in old_pins}.values())
 save(DOC/'complete-preapply-source-catalogue-form-terrain-module-pins.json',old_pins)
 required=[{ref(twin.ROLE/p)['path']for p in ['result.json','typed-role.json.gz']},{ref(evangel.ROLE/p)['path']for p in ['result.json','acceptance.json','staged-original-entry.json']}]
 required +=[{ref(s.DOC/p)['path']for p in ['acceptance.json','staged-browser.json']}|{ref(s.STAGE/p)['path']for p in ['plan.json','catalogue.json','browser-config.json']}for s in stages]
 cert_pins=[];closures=[]
 for path in args.closure:
  cert=read(ROOT/path);assert cert['independentlyVerified']is True and cert['currentManifestSHA256']==CURRENT
  cert_pins.append(ref(ROOT/path));closures.append(set(cert['paths']))
 assert len(closures)==4 and all(any(paths<=c for c in closures)for paths in required)
 previous=read(ROOT/args.previous_count);assert previous['counts']==dict(total=521,installedVerified=230,remaining=291)and len(previous['rows'])==521
 fixed={r['uid']:r for r in previous['rows']};assert UIDS&set(fixed)=={'landsd/222465:0',EVANGEL}and all(not fixed[u]['installedVerified']for u in UIDS&set(fixed))
 save(DOC/'complete-current-twin-role.json.gz',tr);save(DOC/'complete-current-evangel-role.json',er);save(DOC/'atomic-plan.json',atomic)
 live_configs=[]
 for number,(s,cfg)in enumerate(zip(stages,configs)):
  cfg=copy.deepcopy(cfg);cfg['doc']=str((DOC/('live-twin'if number==0 else'live-evangel')).relative_to(ROOT))+'/'
  if number==0:cfg['stage']=str(publication_root.relative_to(ROOT))+'/'
  path=LOCAL/('live-twin-browser-config.json'if number==0 else'live-evangel-browser-config.json');save(path,cfg);live_configs.append(path)
 entries=publication_cat['models']+[eentry];assert len(entries)==3 and {e['uid']for e in entries}==UIDS and all(e['proceduralWindows']is False and not e.get('suppressesBuildingUids')and not e.get('footprintScope')for e in entries)
 pins=old_pins+acceptance_pins+cert_pins+[ref(p)for p in [Path(__file__),Path(guards.__file__),TWIN_SCRIPT,EVANGEL_SCRIPT,BROWSER,ROOT/args.previous_count,DOC/'atomic-plan.json',DOC/'complete-mutual-source-and-routing-domain-separation.json',DOC/'preapply-immutable-math-replay.json',DOC/'exact-candidate-support-state-publication.json',SUPPLEMENT/'supplementary-witness.json',*live_configs]]
 decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={e['uid']:e['sha256']for e in entries},checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,terrainProposalGeometryChanged=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,nativeReacceptance=False,manifestBeforeSHA256=CURRENT,evidenceRefs=pins,livePublicationRequired=True)
 save(DOC/'acceptance.json',decision)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(DOC/'atomic-plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH];call(publication)
 r2,e2,_,tr2,er2=recheck(twin,evangel,LOCAL/'final-current-recheck');assert r2==rows and e2==eentry and tr2==tr and er2==er and manifest.read_bytes()==before
 assert guards.separation(twin,evangel,rows,erow)==separation
 for pin in pins:assert ref(ROOT/pin['path'])==pin
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer_bytes=pointer_path.read_bytes();pointer=read(pointer_path);assert pointer['snapshotId']==PREVIOUS_SNAPSHOT
 inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
 for entry in entries:
  prior=parts.get(entry['uid'],{});parts[entry['uid']]=dict(uid=entry['uid'],name=entry['label'],landmarkIds=prior.get('landmarkIds',[]),objectId=entry['objectId'],csuid=entry['buildingCSUID'],candidate=dict(sha256=entry['sha256']),sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-current-source-role',knownHold=False)
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
 save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Three byte-identical originals; two independently qualified current assemblies and strictly disjoint complete routing domains. Terminal visual roles never root or bridge. Native reacceptance false; all6645 prior source/current tuples preserved.'})
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path'])
 ledger.record_many(snapshot,LEASE,[(u,'approved-for-integration',DOC/'acceptance.json','Complete two-assembly source/current/stage pass; atomic live pending.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 ready();owns();assert manifest.read_bytes()==before;LOCAL.mkdir(parents=True,exist_ok=True);(LOCAL/'manifest-before-installation.json').write_bytes(before)
 expected_terrain=[]
 for terrain in atomic['topLevelTerrainPatches']:
  raw=(ROOT/terrain['source']).read_bytes();patch=read(ROOT/terrain['source']);assert digest(raw)==terrain['sha256']
  expected_terrain.append(dict(url=terrain['destination'],resolution=terrain['resolution'],area=terrain['area'],source=patch['meta'].get('source'),sha256=terrain['sha256'],bytes=len(raw)))
 expected={**original,'officialModelCatalogues':original['officialModelCatalogues']+destinations,'terrainPatches':original.get('terrainPatches',[])+expected_terrain}
 try:
  call(publication+['--apply'])
  assert read(manifest)==expected
  for path,uids in zip(live_configs,[TWIN_UIDS,{EVANGEL}]):
   call(['node',str(BROWSER),'live',ref(path)['path']]);browser(ROOT/read(path)['doc'],'live-browser.json',uids,read(path))
  # Everything except the explicitly planned manifest delta stays exact before
  # ledger/progress mutation. No old role's manifest hash is rewritten.
  for pin in pins:
   if pin['path']!='3d-viewer/city/data/manifest.json':assert ref(ROOT/pin['path'])==pin
  for url,cat in zip(destinations,[publication_cat,stagecats[1]]):
   path=ROOT/'3d-viewer'/url;assert read(path)==cat
   for entry in cat['models']:assert ref(path.parent/entry['asset'])['sha256']==entry['sha256']
  for terrain in atomic['topLevelTerrainPatches']:assert (ROOT/'3d-viewer'/terrain['destination']).read_bytes()==(ROOT/terrain['source']).read_bytes()
  all_entries=[e for url in expected['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']]
  assert len(all_entries)==len({e['uid']for e in all_entries})==6648
  assert {e['uid']:e for e in all_entries if e['uid']not in UIDS}==old_entries
  assert {e['uid']:e for e in all_entries if e['uid']in UIDS}=={e['uid']:e for e in entries}
  assert guards.separation(twin,evangel,rows,erow)==separation
  post=guards.replay_math(math)
  assert read(manifest)==expected
  for pin in pins:
   if pin['path']!='3d-viewer/city/data/manifest.json':assert ref(ROOT/pin['path'])==pin
  save(DOC/'postapply-immutable-math-and-exact-scene-delta.json',{**post,'manifestBeforeSHA256':CURRENT,'manifestAfter':ref(manifest),'exactPriorActorsPreserved':6645,'exactNewActors':3,'exactPostActors':6648,'exactCatalogueDeltas':destinations,'exactTerrainDeltas':expected_terrain,'completeMutualSeparation':ref(DOC/'complete-mutual-source-and-routing-domain-separation.json'),'freshCanonicalManifestRebindingClaim':False})
 except BaseException:
  manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False,pendingLedgerHistoryPreserved=True));raise
 try:
  live_refs=[ref(ROOT/read(path)['doc']/'live-browser.json')for path in live_configs]
  installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':3,'fixedXLDelta':2,'manifest':ref(manifest),'liveBrowsers':live_refs,'postApplyGuard':ref(DOC/'postapply-immutable-math-and-exact-scene-delta.json')};save(DOC/'installed-acceptance.json',installed)
  ledger.record_many(snapshot,LEASE,[(u,'installed-verified',DOC/'installed-acceptance.json','Byte-identical original source; complete bounded typed/current/stage/live/fallback and mutual terrain-domain checks. No native reacceptance.',commit)for u in sorted(UIDS)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
  assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
  call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH])
  count=read(DOC/'full-xl-current-count.json');counts=count['counts'];assert counts==dict(total=521,installedVerified=232,remaining=289)
  assert all(next(r for r in count['rows']if r['uid']==u)['installedVerified']for u in UIDS&set(fixed))
  assert all(next(r for r in count['rows']if r['uid']==old['uid'])['installedVerified']for old in previous['rows']if old['installedVerified'])
  kind='twin-evangel-three-complete-unchanged-source-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));lease=read(LEASE);job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
  result={**installed,'installedUids':sorted(UIDS),'evidenceRefs':[ref(DOC/p)for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json','postapply-immutable-math-and-exact-scene-delta.json']]+live_refs,'jobId':jid,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':counts,'completeCurrentNativeActors':6648}
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
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
 p=argparse.ArgumentParser();p.add_argument('--previous-count',required=True);p.add_argument('--closure',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 twin=module('atomic_twin_stage',TWIN_SCRIPT);evangel=module('atomic_evangel_stage',EVANGEL_SCRIPT)
 assert twin.UIDS==TWIN_UIDS and evangel.UID==EVANGEL
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned(a,twin,evangel)
 assert not DOC.exists()and not LOCAL.exists()and len(a.closure)==4;ready()
 assert read(twin.DOC/'acceptance.json')['passed']and read(evangel.DOC/'acceptance.json')['passed']
 tf=read(twin.PHYSICAL/'neighbour-inputs.json.gz')['rows'];ef=read(evangel.BASE/'government-xl-evangel-college-91306-authentic-tin-candidate-input-v1-20261011/complete-protected-current-forms.json.gz')['rows']
 assert len(tf)==107 and len(ef)==17
 keys=sorted({('building:'if r['building']['uid'].startswith('landsd/')else'foreign-form:')+r['building']['uid']for r in tf+ef}|{'terrain-patch:'+u for u in UIDS})
 claim=reservations.claim('root-twin-evangel-atomic3-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 cmd=[sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--previous-count',a.previous_count,'--owned']
 for c in a.closure:cmd.extend(['--closure',c])
 subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
