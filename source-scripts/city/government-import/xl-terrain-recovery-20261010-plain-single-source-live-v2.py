"""Root-run guarded live publication of one independently staged original.

Source-specific current acceptance is replayed immediately before apply. All
live views and failure/retry must pass before any installed credit. Plain new
terrain only; on apply/live failure the one manifest is restored.
"""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
STAGING=module('plain_original_single_source_stage',HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-v1.py');ref=STAGING.ref

def owned(args):
 config_path=ROOT/args.config;cfg=STAGING.configuration(config_path);stage_doc,stage,stage_lease=STAGING.paths(cfg);uids=sorted(cfg['sources']);assert len(uids)==1;uid=uids[0]
 doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch;leasepath=local/'install-reservation.json'
 def owns():assert reservations.owns(read(leasepath))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();before_sha=digest(before);validator=module('plain_source_browser_verifier',HERE/'integrate.py')
 acceptance=read(stage_doc/'acceptance.json');assert acceptance['passed'] and acceptance['checksPassed'] and acceptance['publication'] is False and acceptance['livePublicationRequired'] and acceptance['uids']==uids and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['scriptExternalAICalls']==0
 for r in acceptance['evidenceRefs']:assert ref(ROOT/r['path'])==r
 assert ref(stage_doc/'staged-browser.json')==acceptance['stagedBrowser'];validator.browser_verified(stage_doc/'staged-browser.json',set(uids))
 row,identities,typed=STAGING.recheck(cfg);assert typed['manifestSHA256']==before_sha;save(doc/'current-identities.json',identities);save(doc/'complete-current-role.json.gz',typed)
 models=read(stage/'catalogue.json')['models'];assert len(models)==1 and models[0]['uid']==uid;model=models[0];assert model['sha256']==row['sourceSHA256']==cfg['sources'][uid] and not model.get('suppressesBuildingUids') and not model.get('supportDependencies') and model['proceduralWindows'] is False
 plan=read(stage/'plan.json');assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1;terrain=plan['topLevelTerrainPatches'][0];assert not terrain.get('replaces') and not terrain.get('replacesMany') and ref(ROOT/terrain['source'])['sha256']==terrain['sha256'];patch=read(ROOT/terrain['source']);assert patch.get('nativeMesh') and not patch.get('patches') and patch['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
 current={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};assert uid not in current and manifest.read_bytes()==before
 plan_path=doc/'atomic-plan.json';save(plan_path,plan);prior_count=ROOT/args.previous_count;assert read(prior_count)['counts']['total']==521 and read(prior_count)['counts']['installedVerified']+read(prior_count)['counts']['remaining']==521
 refs=[ref(p) for p in [Path(__file__),config_path,HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-v1.py',stage_doc/'acceptance.json',stage_doc/'staged-browser.json',stage/'plan.json',stage/'browser-config.json',doc/'current-identities.json',doc/'complete-current-role.json.gz',ROOT/cfg['currentRoleRunner']['path'],HERE.parent/'model-integration-20260909/publish.py',HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs',prior_count]]
 decision=dict(batch=args.batch,uids=uids,sourceSHA256s=cfg['sources'],checksPassed=True,passed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,manifestBeforeSHA256=before_sha,stagedAcceptances=[ref(stage_doc/'acceptance.json')],atomicPlan=ref(plan_path),evidenceRefs=refs,livePublicationRequired=True);save(doc/'acceptance.json',decision)
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};previous=parts.get(uid,{})
 parts[uid]=dict(uid=uid,name=model['label'],landmarkIds=previous.get('landmarkIds',[]),objectId=model['objectId'],csuid=model['buildingCSUID'],candidate={'sha256':model['sha256']},sourceProgress='prepared-for-review',classification='verified-unchanged-original-complete-source-current-acceptance',knownHold=False)
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json');save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':cfg['placementReview']+' Complete staged desktop/mobile views passed; actual unchanged source bytes, independent source-specific current acceptance, guarded live verification remain required.'})
 ledger.seed(inventory_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(doc/'acceptance.json')['path'])
 ledger.record_many(snapshot,leasepath,[(uid,'approved-for-integration',doc/'acceptance.json','Complete unchanged source and independently replayed current source-specific physical/support acceptance; staged desktop/mobile pass, live pending.',commit)],effort=effort,request_id=args.batch+'-approved-'+snapshot)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(plan_path)['path'],'--receipt',str(leasepath),'--phase',args.batch];call(publication);STAGING.recheck(cfg);assert manifest.read_bytes()==before
 for r in refs:assert ref(ROOT/r['path'])==r
 (local/'manifest-before-installation.json').write_bytes(before)
 try:
  call(publication+['--apply']);call(['node',str(HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs'),'live',ref(stage/'browser-config.json')['path']]);live=validator.browser_verified(stage_doc/'live-browser.json',set(uids));assert not live.get('retainedNativeOwnViews',[])
 except BaseException:
  manifest.write_bytes(before);save(doc/'live-failure-rollback.json',dict(manifestRestoredSHA256=digest(manifest.read_bytes()),installedCreditGranted=False));raise
 installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'manifest':ref(manifest),'liveBrowsers':[ref(stage_doc/'live-browser.json')]};save(doc/'installed-acceptance.json',installed)
 ledger.record_many(snapshot,leasepath,[(uid,'installed-verified',doc/'installed-acceptance.json','Unchanged complete original passes staged/live desktop/mobile day/night, full framing, picking/collision, failed-load retry and complete source-specific current physics. Zero AI geometry.',commit)],effort=effort,request_id=args.batch+'-installed-'+snapshot)
 assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
 call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',args.batch])
 jobstage='plain-single-unchanged-original-complete-source-installed-v1';jid=jobs.enqueue(args.batch,jobstage,dict(acceptance=ref(doc/'acceptance.json'),snapshot=snapshot));lease=read(leasepath);job=jobs.claim(args.batch,lease['owner'],[jobstage],lease_seconds=1800);assert job and job['id']==jid
 final={**installed,'installedUids':uids,'evidenceRefs':[ref(doc/n) for n in ['acceptance.json','installed-acceptance.json','atomic-plan.json']]+[ref(stage_doc/'staged-browser.json'),ref(stage_doc/'live-browser.json')],'jobId':jid,'newlyInstalled':1,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':read(doc/'full-xl-current-count.json')['counts']}
 with connect() as con:
  con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
  assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final);assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,uid)).fetchone()==('installed-verified',row['sourceSHA256'])
 save(doc/'result.json',final);save(doc/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot,installedUids=uids));print(json.dumps(dict(installed=uids,snapshotId=snapshot,jobId=jid,neonVerified=True)),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--batch',required=True);p.add_argument('--previous-count',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-');cfg=STAGING.configuration(ROOT/a.config);doc,stage,lease=STAGING.paths(cfg);install_doc=ROOT/'docs/astra-city/government-import'/a.batch;install_lease=HERE/'local'/a.batch/'install-reservation.json'
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned(a)
 assert not install_doc.exists() and read(doc/'acceptance.json')['passed'];physical=(ROOT/cfg['physicalReceipt']['path']).parent;forms=read(physical/'neighbour-inputs.json.gz')['rows'];resources={('building:' if r['building']['uid'].startswith('landsd/') else 'foreign-form:')+r['building']['uid'] for r in forms}|{'building:'+u for u in cfg['sources']}|{'terrain-patch:'+u for u in cfg['sources']}
 claim=reservations.claim('plain-single-source-live-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok'],claim;save(install_lease,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(install_lease),'--ttl','3600','--',sys.executable,__file__,'--config',a.config,'--batch',a.batch,'--previous-count',a.previous_count,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
