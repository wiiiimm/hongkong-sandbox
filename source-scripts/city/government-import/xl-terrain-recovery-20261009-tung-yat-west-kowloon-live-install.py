"""Atomic guarded publication of two independently staged unchanged towers.

Replays both complete source roles/current physics before one apply. Both live
browser checks must pass before installed credit; either failure rolls back the
single manifest. Root agent owns execution of this publisher.
"""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
STAGES=[module('tung_yat_stage',HERE/'xl-terrain-recovery-20261009-163705-stage-install-v2.py'),module('west_kowloon_stage',HERE/'xl-terrain-recovery-20261009-272986-stage-install.py')]
UIDS=[s.UID for s in STAGES]
BATCH='government-xl-tung-yat-west-kowloon-atomic-installed-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'install-reservation.json'
ref=STAGES[0].ref

def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(command):
  subprocess.run(command,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();before_sha=digest(before)
 validator=module('atomic_browser_validator',HERE/'integrate.py');accepted=[];models=[];rows=[];roles=[];areas=[];terrains=[];refs=[ref(Path(__file__))]
 for stage in STAGES:
  acceptance=read(stage.DOC/'acceptance.json')
  assert acceptance['passed'] and acceptance['checksPassed'] and acceptance['publication'] is False and acceptance['livePublicationRequired']
  assert acceptance['uids']==[stage.UID] and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['scriptExternalAICalls']==0
  for item in acceptance['evidenceRefs']:assert ref(ROOT/item['path'])==item
  assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser'];validator.browser_verified(stage.DOC/'staged-browser.json',{stage.UID})
  row,identity,role=stage.recheck(LOCAL/('identity-'+stage.UID.replace('/','-').replace(':','-')))
  assert read(stage.PHYSICAL/'selection.json.gz')['manifestSHA256']==before_sha
  identity_path=DOC/(stage.UID.split('/')[1].replace(':','-')+'-identity.json');save(identity_path,identity)
  role_path=DOC/(stage.UID.split('/')[1].replace(':','-')+'-wall-role.json.gz');save(role_path,role)
  model=read(stage.STAGE/'catalogue.json')['models'][0];assert model['uid']==stage.UID and model['sha256']==row['sourceSHA256']
  plan=read(stage.STAGE/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
  areas.extend(plan['areas']);terrains.extend(plan['topLevelTerrainPatches']);accepted.append(acceptance);models.append(model);rows.append(row);roles.append(role)
  refs.extend([ref(stage.DOC/'acceptance.json'),ref(stage.DOC/'staged-browser.json'),ref(stage.STAGE/'plan.json'),ref(stage.STAGE/'browser-config.json'),ref(identity_path),ref(role_path),ref(Path(stage.__file__))])
 assert manifest.read_bytes()==before
 current={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};assert not(set(UIDS)&current)
 assert len({a['destination'] for a in areas})==2 and len({t['destination'] for t in terrains})==2
 bounds=[]
 for terrain in terrains:
  assert ref(ROOT/terrain['source'])['sha256']==terrain['sha256'];patch=read(ROOT/terrain['source']);assert patch.get('nativeMesh') and not patch.get('patches')
  geometry=patch['meta']['georef'];x0=geometry['bE']-834500;z0=816500-geometry['bN']
  end_x=x0+(patch['w']-1)*geometry['aE'];end_z=z0-(patch['h']-1)*geometry['aN']
  bounds.append([min(x0,end_x),min(z0,end_z),max(x0,end_x),max(z0,end_z)])
  if terrain.get('replaces'):
   replacement=terrain['replaces'];assert ref(ROOT/'3d-viewer'/replacement['url'])['sha256']==replacement['sha256']
   assert ref(ROOT/terrain['nativeReview']['path'])==terrain['nativeReview'];review=read(ROOT/terrain['nativeReview']['path'])
   assert review['status']=='approved-for-integration' and review['replacementSHA256']==terrain['sha256'] and review['sourceGeometryChanged'] is False
 b,c=bounds;assert b[2]<c[0] or c[2]<b[0] or b[3]<c[1] or c[3]<b[1],'Atomic terrain domains must be strictly disjoint'
 plan_path=DOC/'atomic-plan.json';save(plan_path,{'areas':areas,'topLevelTerrainPatches':terrains})
 decision={'batch':BATCH,'uids':UIDS,'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in rows},'checksPassed':True,'passed':True,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'manifestBeforeSHA256':before_sha,'stagedAcceptances':[ref(s.DOC/'acceptance.json') for s in STAGES],'atomicPlan':ref(plan_path),'evidenceRefs':refs,'livePublicationRequired':True}
 save(DOC/'acceptance.json',decision)
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
 for model in models:
  previous=parts.get(model['uid'],{})
  parts[model['uid']]={'uid':model['uid'],'name':model['label'],'landmarkIds':previous.get('landmarkIds',[]),'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},'sourceProgress':'prepared-for-review','classification':'verified-unchanged-original-provider-crossing-exterior-wall-role','knownHold':False}
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
 save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Two complete unchanged original LOD3 towers. Independently bound exposed wall roles and exact whole sample/rim accounting retain ordinary clearance limits and genuine strict anchors. Complete current identity, source, foundation, ordinary/native neighbours and staged desktop/mobile browser checks pass independently for each source. Atomic disjoint terrain plans, live verification and original compressed bytes remain required; no AI geometry modelling.'})
 ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 effort={'method':'unknown','ai_model':None,'reasoning_effort':'unknown','issue':'HKS-203','run_id':snapshot,'output_ref':ref(DOC/'acceptance.json')['path']}
 ledger.record_many(snapshot,LEASE,[(uid,'approved-for-integration',DOC/'acceptance.json','Complete unchanged original source, narrow independently bound wall/rim role and staged desktop/mobile browser pass. All current physical gates pass; live checks pending.',commit) for uid in UIDS],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(plan_path)['path'],'--receipt',str(LEASE),'--phase',BATCH]
 call(publication)
 for stage in STAGES:stage.recheck(LOCAL/('identity-before-apply-'+stage.UID.split('/')[1].replace(':','-')))
 assert manifest.read_bytes()==before
 for item in refs:assert ref(ROOT/item['path'])==item
 save(LOCAL/'manifest-before-installation.json',read(manifest));call(publication+['--apply'])
 try:
  for stage in STAGES:
   call(['node',str(HERE/'resolution-assembly-browser.mjs'),'live',ref(stage.STAGE/'browser-config.json')['path']]);validator.browser_verified(stage.DOC/'live-browser.json',{stage.UID})
 except BaseException:
  manifest.write_bytes(before);save(DOC/'live-failure-rollback.json',{'manifestRestoredSHA256':digest(manifest.read_bytes()),'installedCreditGranted':False});raise
 installed={**decision,'snapshotId':snapshot,'publication':True,'manifest':ref(manifest),'liveBrowsers':[ref(s.DOC/'live-browser.json') for s in STAGES]};save(DOC/'installed-acceptance.json',installed)
 ledger.record_many(snapshot,LEASE,[(uid,'installed-verified',DOC/'installed-acceptance.json','Complete unchanged original tower passes staged/live desktop/mobile day/night, whole-source framing, picking/collision and failed-load retry. Complete independent source/current physics pass; source interpretation only, zero AI geometry modelling.',commit) for uid in UIDS],effort=effort,request_id=BATCH+'-installed-'+snapshot)
 assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
 call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
 jobstage='atomic-two-unchanged-provider-exterior-towers-installed-v1';payload={'acceptance':ref(DOC/'acceptance.json'),'snapshot':snapshot};jid=jobs.enqueue(BATCH,jobstage,payload);receipt=read(LEASE);job=jobs.claim(BATCH,receipt['owner'],[jobstage],lease_seconds=1800);assert job and job['id']==jid
 final={**installed,'installedUids':UIDS,'evidenceRefs':[ref(DOC/p) for p in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(s.DOC/'staged-browser.json') for s in STAGES]+[ref(s.DOC/'live-browser.json') for s in STAGES],'jobId':jid,'newlyInstalled':2,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')}
 with connect() as con:
  con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,receipt)
  assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
  for row in rows:assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,row['uid'])).fetchone()==('installed-verified',row['sourceSHA256'])
 save(DOC/'result.json',final);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True,'snapshotId':snapshot,'installedUids':UIDS});print(json.dumps({'installed':UIDS,'snapshotId':snapshot,'jobId':jid,'neonVerified':True}),flush=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--owned',action='store_true');args=parser.parse_args()
 if args.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned()
 assert not DOC.exists(),'Fresh immutable atomic installation batch required'
 assert all(read(s.DOC/'acceptance.json')['passed'] for s in STAGES)
 scope=set(UIDS);terrain_resources=set()
 for stage in STAGES:
  scope.update(r['building']['uid'] for r in read(stage.PHYSICAL/'neighbour-inputs.json.gz')['rows']);terrain_resources.add('terrain-patch:'+stage.UID)
  for t in read(stage.STAGE/'plan.json')['topLevelTerrainPatches']:
   if t.get('replaces'):terrain_resources.add('terrain-surface:'+t['replaces']['url'])
 claim=reservations.claim('xl-tung-yat-west-kowloon-atomic-'+str(uuid.uuid4()),[('building:' if uid.startswith('landsd/') else 'source-form:')+uid for uid in sorted(scope)]+sorted(terrain_resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
