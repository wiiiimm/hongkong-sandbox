"""Guarded live continuation of the source-bound Tung Yat House staged acceptance.

Publication is serialized. Current identity and complete physical wall context
are replayed before ledger approval; live browser failure restores the manifest.
The original compressed model and authored pose are never edited.
"""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
stage=module('tung_yat_staged_adapter',HERE/'xl-terrain-recovery-20261009-163705-stage-install-v2.py')
UID=stage.UID;BATCH='government-xl-terrain-recovery-163705-installed-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LEASE=HERE/'local'/BATCH/'install-reservation.json'
ref=stage.ref

def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(command):
  subprocess.run(command,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();acceptance=read(stage.DOC/'acceptance.json')
 assert acceptance['passed'] and acceptance['checksPassed'] and acceptance['publication'] is False and acceptance['livePublicationRequired']
 assert acceptance['uids']==[UID] and acceptance['newlyInstalled']==acceptance['modelGeometryChanges']==acceptance['scriptExternalAICalls']==0
 for item in acceptance['evidenceRefs']:assert ref(ROOT/item['path'])==item
 assert ref(stage.DOC/'staged-browser.json')==acceptance['stagedBrowser']
 validator=module('tung_yat_live_browser_validator',HERE/'integrate.py');validator.browser_verified(stage.DOC/'staged-browser.json',{UID})
 row,identity,role=stage.recheck(HERE/'local'/BATCH/'identity-recheck')
 save(DOC/'fresh-identity.json',identity);save(DOC/'fresh-wall-role.json.gz',role)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes()
 assert all(UID not in {m['uid'] for m in read(ROOT/'3d-viewer'/url)['models']} for url in read(manifest)['officialModelCatalogues'])
 model=read(stage.STAGE/'catalogue.json')['models'][0];assert model['uid']==UID and model['sha256']==row['sourceSHA256']
 decision={**acceptance,'batch':BATCH,'sourceStagedAcceptance':ref(stage.DOC/'acceptance.json'),'freshIdentity':ref(DOC/'fresh-identity.json'),'freshWallRole':ref(DOC/'fresh-wall-role.json.gz'),'liveInstaller':ref(Path(__file__)),'publication':False}
 save(DOC/'acceptance.json',decision)
 sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
 pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};previous=parts.get(UID,{})
 parts[UID]={'uid':UID,'name':model['label'],'landmarkIds':previous.get('landmarkIds',[]),'objectId':model['objectId'],'csuid':model['buildingCSUID'],'candidate':{'sha256':model['sha256']},'sourceProgress':'prepared-for-review','classification':'verified-unchanged-original-provider-crossing-exterior-wall-role','knownHold':False}
 ordered=sorted(parts.values(),key=lambda p:p['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inventory_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json')
 save(inventory_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Original provider LOD3 tower is unchanged. Complete continuous face context proves only the exact five exposed roof-connected crossing walls have a narrow authored exterior role; ordinary/upward/degenerate faces, full foundation and all 40 neighbours including three retained original natives remain strict. Whole source/current identity/runtime/staged browser pass; live publication remains independently required. No AI geometry modelling.'})
 ledger.seed(inventory_path,inherit=pointer['snapshotId'])
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 effort={'method':'unknown','ai_model':None,'reasoning_effort':'unknown','issue':'HKS-203','run_id':snapshot,'output_ref':ref(DOC/'acceptance.json')['path']}
 ledger.record_many(snapshot,LEASE,[(UID,'approved-for-integration',DOC/'acceptance.json','Complete unchanged original source, source-bound exterior role and staged desktop/mobile browser pass. All independent current identity, foundation, ordinary source faces and neighbours pass; live checks pending.',commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
 publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(stage.STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH]
 call(publication)
 # Revalidate immutable source and current context immediately before apply.
 stage.recheck(HERE/'local'/BATCH/'identity-recheck-before-apply');assert manifest.read_bytes()==before
 save(HERE/'local'/BATCH/'manifest-before-installation.json',read(manifest))
 call(publication+['--apply'])
 try:
  call(['node',str(HERE/'resolution-assembly-browser.mjs'),'live',ref(stage.STAGE/'browser-config.json')['path']]);validator.browser_verified(stage.DOC/'live-browser.json',{UID})
 except BaseException:
  manifest.write_bytes(before);raise
 installed={**decision,'snapshotId':snapshot,'publication':True,'manifest':ref(manifest),'liveBrowser':ref(stage.DOC/'live-browser.json')};save(DOC/'installed-acceptance.json',installed)
 ledger.record_many(snapshot,LEASE,[(UID,'installed-verified',DOC/'installed-acceptance.json','Unchanged original Tung Yat House passes staged/live desktop/mobile day/night, whole-source framing, picking/collision and failed-load retry; all independent original face/foundation/identity/current-neighbour gates passed. Source interpretation only; zero AI geometry modelling.',commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
 assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inventory_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
 call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
 jobstage='tung-yat-unchanged-provider-exterior-installed-v1';payload={'acceptance':ref(DOC/'acceptance.json'),'snapshot':snapshot};jid=jobs.enqueue(BATCH,jobstage,payload);receipt=read(LEASE);job=jobs.claim(BATCH,receipt['owner'],[jobstage],lease_seconds=1800);assert job and job['id']==jid
 final={**installed,'installedUids':[UID],'evidenceRefs':[ref(DOC/p) for p in ['acceptance.json','installed-acceptance.json','fresh-identity.json','fresh-wall-role.json.gz']]+[ref(stage.DOC/'staged-browser.json'),ref(stage.DOC/'live-browser.json')],'jobId':jid,'newlyInstalled':1,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')}
 with connect() as con:
  con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,receipt)
  assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(final),jid,job['owner'],job['token'])).rowcount==1
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',final)
  assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(snapshot,UID)).fetchone()==('installed-verified',row['sourceSHA256'])
 save(DOC/'result.json',final);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True,'snapshotId':snapshot,'installedUids':[UID]})
 print(json.dumps({'installed':[UID],'snapshotId':snapshot,'jobId':jid,'neonVerified':True}),flush=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--owned',action='store_true');args=parser.parse_args()
 if args.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned()
 assert not DOC.exists(),'Fresh immutable installation batch required'
 assert read(stage.DOC/'acceptance.json')['passed']
 forms=read(stage.PHYSICAL/'neighbour-inputs.json.gz')['rows'];scope={r['building']['uid'] for r in forms}|{UID}
 claim=reservations.claim('xl-terrain-recovery-163705-live-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+['terrain-patch:'+UID,'terrain-surface:city/data/government-native-12854-0.json'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
