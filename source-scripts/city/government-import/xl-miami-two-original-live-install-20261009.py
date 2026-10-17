"""Root-run atomic Miami tower publication with exact evidence replay and rollback.

The frozen staged catalogue remains untouched. The installation copy changes
only the reviewed publication flag and routing location; original compressed
assets, original poses, current basic podium and all other actors stay intact.
"""
import argparse,importlib.util,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
STAGING=module('miami_original_frozen_stage',HERE/'xl-miami-two-stage-checkpoint-20261009.py')
UIDS=sorted(STAGING.UIDS)
BATCH='government-xl-miami-two-original-installed-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/BATCH
LOCAL=HERE/'local'/BATCH
LEASE=LOCAL/'install-reservation.json'
STAGE_JOB='57fb4bda504515abff5a99e66a6451e86a9ea233a6e016b0dd7f161305187ce2'
SOLID=ROOT/'docs/astra-city/government-import/government-xl-miami-two-solid-preview-20261009'
def ref(path):
 p=Path(path);return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def recheck_staged():
 staged=read(STAGING.DOC/'result.json');assert staged['jobId']==STAGE_JOB and staged['scriptFullAcceptancePassed'] and staged['stagedBrowserPassed']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(STAGE_JOB,)).fetchone()==('complete',staged)
 for item in staged['evidenceRefs']:assert ref(ROOT/item['path'])==item,item['path']
 replay=STAGING.recheck();assert replay==read(STAGING.DOC/'acceptance-ready-handoff.json')
 solid=read(SOLID/'result.json');assert solid['solidOriginalAppearancePassed'] and solid['stagedBrowserPassed'] and set(solid['uids'])==set(UIDS)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(solid['jobId'],)).fetchone()==('complete',solid)
 for item in solid['evidenceRefs']:assert ref(ROOT/item['path'])==item,item['path']
 assert solid['currentManifestSHA256']==replay['currentManifestSHA256']
 return replay
def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(command):
  subprocess.run(command,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();before_sha=digest(before);replay=recheck_staged();assert replay['currentManifestSHA256']==before_sha
 current={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};assert not(set(UIDS)&current)
 original=read(STAGING.STAGE/'catalogue.json');catalogue=json.loads(json.dumps(original));assert sorted(m['uid'] for m in catalogue['models'])==UIDS
 for m in catalogue['models']:
  prior=next(v for v in original['models'] if v['uid']==m['uid']);assert prior['publicationApproved'] is False
  m['publicationApproved']=True;assert {k:v for k,v in m.items() if k!='publicationApproved'}=={k:v for k,v in prior.items() if k!='publicationApproved'}
  assert not m.get('suppressesBuildingUids') and not m.get('supportDependencies') and m['proceduralWindows'] is False
  p=STAGE/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(STAGING.STAGE/m['asset'],p);assert ref(p)['sha256']==m['sha256']==replay['sourceSHA256s'][m['uid']]
 save(STAGE/'catalogue.json',catalogue);shutil.copyfile(STAGING.STAGE/'source-forms.json',STAGE/'source-forms.json');shutil.copyfile(STAGING.STAGE/'catalogue-index.json',STAGE/'catalogue-index.json')
 old_plan=read(STAGING.STAGE/'plan.json');assert len(old_plan['areas'])==len(old_plan['topLevelTerrainPatches'])==1
 terrain=dict(old_plan['topLevelTerrainPatches'][0]);assert not terrain.get('replaces') and not terrain.get('replacesMany');p=STAGE/Path(terrain['source']).name;shutil.copyfile(ROOT/terrain['source'],p);assert ref(p)['sha256']==terrain['sha256'];terrain['source']=ref(p)['path']
 assert not (ROOT/'3d-viewer'/terrain['destination']).exists();destination='city/data/official-models/'+BATCH+'/catalogue.json'
 plan={'areas':[{'area':catalogue['area'],'catalogue':ref(STAGE/'catalogue.json')['path'],'destination':destination}],'topLevelTerrainPatches':[terrain]};save(STAGE/'plan.json',plan)
 config=read(STAGING.STAGE/'browser-config-v2.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain]);save(STAGE/'browser-config.json',config)
 dependencies=module('miami_current_dependencies',HERE/'dependency_preflight.py').from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers'] for r in dependencies['rows']);save(DOC/'dependencies.json',dependencies)
 evidence=[ref(Path(__file__)),ref(STAGING.DOC/'result.json'),ref(STAGING.DOC/'acceptance-ready-handoff.json'),ref(STAGING.DOC/'browser-v2/staged-browser.json'),ref(STAGING.DOC/'basic-podium-exact-original-contacts.json.gz'),ref(SOLID/'result.json'),ref(SOLID/'browser-solid-v3/staged-browser.json'),ref(SOLID/'appearance-check/staged-browser.json'),ref(HERE/'xl-miami-two-solid-browser-20261009.mjs'),ref(STAGE/'catalogue.json'),ref(STAGE/'plan.json'),ref(STAGE/'browser-config.json'),ref(DOC/'dependencies.json')]
 decision={**replay,'batch':BATCH,'passed':True,'checksPassed':True,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'evidenceRefs':evidence,'manifestBeforeSHA256':before_sha,'livePublicationRequired':True,'soleCatalogueFieldChange':'publicationApproved:false→true','currentBasicPodiumAndAllOtherActorsRetained':True};save(DOC/'acceptance.json',decision)
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
 for model in catalogue['models']:
  previous=parts.get(model['uid'],{});parts[model['uid']]={'uid':model['uid'],'name':model['label'],'landmarkIds':previous.get('landmarkIds',[]),'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},'sourceProgress':'prepared-for-review','classification':'verified-complete-unchanged-original-tower-explicit-related-podium','knownHold':False}
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json');save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Two complete unchanged original Miami towers, authored poses preserved, sole related original podium identity independently proven. Current basic podium and every other actor retained; all full-source current physical/runtime/neighbour and desktop/mobile staged gates passed. No source edits or AI geometry modelling. Live acceptance required.'})
 ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort={'method':'unknown','ai_model':None,'reasoning_effort':'unknown','issue':'HKS-203','run_id':snapshot,'output_ref':ref(DOC/'acceptance.json')['path']}
 ledger.record_many(snapshot,LEASE,[(uid,'approved-for-integration',DOC/'acceptance.json','Complete original source identity and independently passing current source/terrain/foundation/runtime/all18 neighbour rows; eight staged views, two503retries, picking/collision pass. Raw current podium line contacts retained with no physical exemption. Live installation pending.',commit) for uid in UIDS],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH];call(publication);recheck_staged();assert manifest.read_bytes()==before
 for item in evidence:assert ref(ROOT/item['path'])==item
 (LOCAL/'manifest-before-installation.json').write_bytes(before);call(publication+['--apply'])
 validator=module('miami_live_browser_validator',HERE/'integrate.py')
 try:
  call(['node',str(HERE/'xl-miami-two-solid-browser-20261009.mjs'),'live',ref(STAGE/'browser-config.json')['path']]);live=validator.browser_verified(DOC/'live-browser.json',set(UIDS))
  for v in live['views']:
   if 'time' in v:assert v['fullyFramed'] and abs(v['ground']-v['groundSampler'])<=.004 and v['retained']['landsd/232089:0']=={'loaded':True,'detailedActive':False,'hidden':False}
 except BaseException:
  manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',{'manifestRestoredSHA256':digest(manifest.read_bytes()),'installedCreditGranted':False,'liveFailurePreserved':True});raise
 installed={**decision,'snapshotId':snapshot,'publication':True,'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json')};save(DOC/'installed-acceptance.json',installed)
 ledger.record_many(snapshot,LEASE,[(uid,'installed-verified',DOC/'installed-acceptance.json','Complete unchanged original tower passed staged/live desktop/mobile day/night, full-source framing, picking/collision, bothfailedloadretries and strict current physics. Basic related podium retained, allotheractors checked, no geometry edits or AI modelling.',commit) for uid in UIDS],effort=effort,request_id=BATCH+'-installed-'+snapshot)
 assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]});call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
 jobstage='atomic-two-complete-unchanged-miami-original-towers-installed-v1';payload={'acceptance':ref(DOC/'acceptance.json'),'snapshot':snapshot};jid=jobs.enqueue(BATCH,jobstage,payload);lease=read(LEASE);job=jobs.claim(BATCH,lease['owner'],[jobstage],lease_seconds=1800);assert job and job['id']==jid
 final={**installed,'installedUids':UIDS,'jobId':jid,'newlyInstalled':2,'activeWorkers':0,'queuedFollowups':0,'evidenceRefs':[ref(p) for p in [DOC/'acceptance.json',DOC/'installed-acceptance.json',STAGE/'plan.json',DOC/'live-browser.json',STAGING.DOC/'result.json']],'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')}
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
  for uid in UIDS:assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,uid)).fetchone()==('installed-verified',replay['sourceSHA256s'][uid])
 save(DOC/'result.json',final);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True,'snapshotId':snapshot,'installedUids':UIDS});print(json.dumps({'installed':UIDS,'snapshotId':snapshot,'jobId':jid,'neonVerified':True}),flush=True)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');args=p.parse_args()
 if args.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned()
 assert not DOC.exists() and not STAGE.exists(),'Fresh immutable atomic installation scope required'
 assert read(STAGING.DOC/'result.json')['jobId']==STAGE_JOB
 scope={r['building']['uid'] for r in read(STAGING.BASE/'government-xl-miami-two-complete-original-physical-20261009/neighbour-inputs.json.gz')['rows']}|set(UIDS)
 resources=['building:'+u for u in sorted(scope)]+['terrain-patch:'+u for u in UIDS]+['terrain-surface:city/data/terrain.json'];claim=reservations.claim('miami-two-original-atomic-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
