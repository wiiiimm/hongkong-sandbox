"""Reconcile two unchanged legacy publications using fresh physical/browser proof.

No runtime publication, model edits or acceptance exceptions. The normal strict
identity fit remains mandatory. Every other current review inherits unchanged.
"""
import os,sys,uuid,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication

BATCH='government-xl-legacy-current-reconciled-20261008-v2'
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-legacy-current-disposition-20261008'
DOC=SOURCE.parent/BATCH
UIDS=['landsd/184076:0','landsd/1307:0']

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}

def main():
    assert not DOC.exists()
    claim=reservations.claim('codex-xl-legacy-reconcile-'+str(uuid.uuid4()),['building:'+u for u in UIDS],ttl=3600,batch=BATCH)
    assert claim['ok'],claim
    lease=claim['reservation'];leasepath=HERE/'local'/BATCH/'reservation.json';save(leasepath,__import__('json').loads(__import__('json').dumps(lease,default=str)))
    try:
        with locked_publication(ROOT):
            physical=read(SOURCE/'result.json')
            with connect() as con:assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(physical['jobId'],)).fetchone()==('complete',physical)
            assert all(r['scriptChecksPassed'] and not r['reasons'] and r['strictFoundationAccepted'] for r in physical['rows'])
            for e in physical['evidenceRefs']:assert ref(ROOT/e['path'])==e
            for path,sha in read(SOURCE/'metrics.json')['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
            selection=read(SOURCE/'selection.json.gz');rows={r['uid']:r for r in selection['rows']}
            pointerpath=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointerpath)
            manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
            assert digest(manifestpath.read_bytes())==selection['manifestSHA256']
            outcomes=[]
            for uid in UIDS:
                row=rows[uid];entry=row['candidate']['entry'];native=row['native']['model'];b=row['source']['building']
                match=[(m,ROOT/'3d-viewer'/url) for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid']==uid]
                assert len(match)==1;deployed,cat=match[0]
                for key in ['uid','objectId','buildingCSUID','sha256','worldBounds','recordedBaseHeight','recordedTopHeight']:
                    assert entry[key]==deployed[key]==native['candidate'][key],key
                assert b['objectId']==entry['objectId'] and b['buildingCSUID']==entry['buildingCSUID']
                assert len(native['matching']['viewerMatches'])==len(native['matching']['officialMatches'])==1
                metric=next(r['metrics'] for r in physical['rows'] if r['uid']==uid)
                assert metric['sourcePreserved'] and metric['identity']['overlap']>=.98 and metric['identity']['centroidDistance']<=1
                assert digest((cat.parent/deployed['asset']).read_bytes())==entry['sha256']
                modeldoc=DOC/uid.replace('/','-').replace(':','-');stage=HERE/'accepted'/BATCH/uid.replace('/','-').replace(':','-')
                catalogue=read(cat);catalogue['models']=[deployed];catalogue['counts']={**catalogue.get('counts',{}),'packedModels':1}
                save(stage/'catalogue.json',catalogue);save(stage/'source-forms.json',[b])
                p=stage/deployed['asset'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((cat.parent/deployed['asset']).read_bytes())
                config={'stage':str(stage.relative_to(ROOT))+'/','doc':str(modeldoc.relative_to(ROOT))+'/',
                        'catalogueURL':str(cat.relative_to(ROOT/'3d-viewer')),'terrain':[],'fitBox':True,
                        'browserUids':[uid],'failureTestUids':[uid]}
                save(stage/'browser-config.json',config)
                for mode in ['staged','live']:
                    env={**os.environ,'CHROME_PATH':'/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'}
                    subprocess.run(['node',str(HERE/'resolution-recovery-browser.mjs'),mode,str((stage/'browser-config.json').relative_to(ROOT))],cwd=ROOT,env=env,check=True)
                    assert reservations.heartbeat(lease,ttl=3600)
                    browser=read(modeldoc/(mode+'-browser.json'));assert browser['passed'] and not browser['errors']
                outcomes.append({'uid':uid,'sourceSHA256':entry['sha256'],'identity':{'exactObjectId':True,'exactBuildingCSUID':True,'uniqueViewerMatch':True,'strictDefaultFit':metric['identity'],'numericalLimitsChanged':False},
                                 'physicalJobId':physical['jobId'],'runtimeCatalogue':ref(cat),'runtimeAsset':ref(cat.parent/deployed['asset']),
                                 'stagedBrowser':ref(modeldoc/'staged-browser.json'),'liveBrowser':ref(modeldoc/'live-browser.json')})
            assert read(pointerpath)==pointer and digest(manifestpath.read_bytes())==selection['manifestSHA256']
            decision={'batch':BATCH,'uids':UIDS,'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in outcomes},'passed':True,'rows':outcomes,
                      'runtimeAssetsAdded':0,'newlyInstalled':0,'newlyVerified':2,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,
                      'qualification':'Two existing original publications reconciled after fresh physical and staged/live desktop/mobile day/night, picking/collision and failed-load/retry checks. No new runtime assets or changes to source geometry, pose, terrain or numerical acceptance limits.'}
            save(DOC/'acceptance.json',decision)
            sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
            inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']}
            for uid in UIDS:
                e=rows[uid]['candidate']['entry'];old=parts.get(uid,{})
                parts[uid]={**old,'uid':uid,'name':e['label'],'objectId':e['objectId'],'csuid':e['buildingCSUID'],'landmarkIds':old.get('landmarkIds',[]),
                            'candidate':{'sha256':e['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-legacy-publication-current-review-recovery','knownHold':False}
            ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16]
            inventorypath=pointerpath.parent/('source-review-inventory-'+snapshot+'.json');save(inventorypath,{**inventory,'parts':ordered,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId']})
            ledger.seed(inventorypath,inherit=pointer['snapshotId'])
            effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-199','run_id':snapshot}
            note='Existing unchanged original publication verified through fresh full source contact/foundation, strict default identity fit and staged/live desktop/mobile day/night, picking/collision and failure/retry checks. Zero new runtime assets.'
            ledger.record_many(snapshot,leasepath,[(u,'installed-verified',DOC/'acceptance.json',note,None) for u in UIDS],effort=effort,request_id=BATCH+'-installed-'+snapshot)
            with connect() as con:
                before=con.execute('SELECT uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND NOT (uid=ANY(%s)) ORDER BY uid',(pointer['snapshotId'],UIDS)).fetchall()
                after=con.execute('SELECT uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND NOT (uid=ANY(%s)) ORDER BY uid',(snapshot,UIDS)).fetchall()
                assert before==after,'Other reviews must be preserved exactly'
            assert read(pointerpath)==pointer
            save(pointerpath,{**pointer,'snapshotId':snapshot,'inventory':str(inventorypath.relative_to(ROOT)),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
            subprocess.run([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'],cwd=ROOT,check=True)
            subprocess.run(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')],cwd=ROOT,check=True)
            payload={'uids':UIDS,'snapshotId':snapshot,'acceptance':ref(DOC/'acceptance.json')};stage='legacy-published-original-current-verification-v1'
            jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
            result={**decision,**payload,'jobId':jid,'stage':stage,'otherReviewsPreserved':len(before)}
            with connect() as con:
                con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
                assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
            with connect() as con:assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
            save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'snapshotId':snapshot,'resultVerified':True})
            print({'snapshotId':snapshot,'jobId':jid,'newlyVerified':2,'newRuntimeAssets':0})
    finally:assert reservations.release(lease)

if __name__=='__main__':main()
