"""Recover an exact published original into the current ledger after fresh checks.

No re-publication or geometry changes. Historical installed receipts remain intact;
the current snapshot inherits every other review and gets fresh physical/browser evidence.
"""
import argparse, importlib.util, json, os, shutil, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row

def ref(path):
    path=Path(path);return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['source','batch']:p.add_argument('--'+key,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
    source=(ROOT/a.source).resolve();assert source.parent==ROOT/'docs/astra-city/government-import'
    doc=source.parent/a.batch;local=HERE/'local'/a.batch;leasepath=local/'reservation.json'
    if not a.owned:
        assert not doc.exists(),'Fresh recovery only'
        row=read(source/'selection.json.gz')['rows'][0]
        scope={row['uid']}|{r['building']['uid'] for r in read(source/'neighbour-inputs.json.gz')['rows']}
        claim=reservations.claim('codex-current-installed-recovery-'+str(uuid.uuid4()),
            [('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+['terrain-patch:'+row['uid']],batch=a.batch)
        assert claim['ok'],claim;save(leasepath,json.loads(json.dumps(claim['reservation'],default=str)))
        subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(leasepath),
                        '--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True);return
    lease=read(leasepath);assert reservations.owns(lease)
    def call(command):
        subprocess.run(command,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'})
        assert reservations.owns(lease)
    result=read(source/'result.json');row=read(source/'selection.json.gz')['rows'][0];uid=row['uid']
    assert result['uid']==uid and result['scriptChecksPassed'] and not result['reasons']
    assert read(source/'neon-sync.json')=={'jobId':result['jobId'],'resultVerified':True}
    for evidence in result['evidenceRefs']:assert ref(ROOT/evidence['path'])['sha256']==evidence['sha256']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    pointerpath=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointerpath)
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifestref=ref(manifestpath)
    assert manifestref['sha256']==read(source/'selection.json.gz')['manifestSHA256']
    prior=read(source/'historical-installed-proof.json');assert prior['uid']==uid and prior['sourceSHA256']==row['sourceSHA256']
    cataloguepath=ROOT/'3d-viewer'/prior['catalogueURL'];catalogue=read(cataloguepath)
    assert len(catalogue['models'])==1 and catalogue['models'][0]['uid']==uid
    model=catalogue['models'][0];assert model['sha256']==row['sourceSHA256']
    actualasset=cataloguepath.parent/model['asset'];assert ref(actualasset)['sha256']==model['sha256']
    old=read(ROOT/prior['previousInstalledAcceptance']['path']);assert ref(ROOT/prior['previousInstalledAcceptance']['path'])==prior['previousInstalledAcceptance']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        historic=con.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(prior['historicalSnapshotId'],uid)).fetchone()
        current=con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],uid)).fetchone()
    assert historic and historic[:2]==('installed-verified',model['sha256'])
    assert historic[2]['evidence']==prior['previousInstalledAcceptance']['path'] and historic[2]['sha256']==prior['previousInstalledAcceptance']['sha256']
    assert current is None,'An existing current decision needs explicit reconciliation'
    metrics=read(source/'metrics.json')
    for path,sha in metrics['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha
    stage=HERE/'accepted'/a.batch;save(stage/'catalogue.json',catalogue);save(stage/'source-forms.json',[row['source']['building']])
    asset=stage/model['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(actualasset,asset)
    config={'stage':str(stage.relative_to(ROOT))+'/','doc':str(doc.relative_to(ROOT))+'/',
            'catalogueURL':prior['catalogueURL'],'terrain':[],'fitBox':True,'browserUids':[uid],'failureTestUids':[uid]}
    save(stage/'browser-config.json',config)
    spec=importlib.util.spec_from_file_location('recovery_browser_checks',HERE/'integrate.py');direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)
    for mode in ['staged','live']:
        call(['node',str(HERE/'resolution-recovery-browser.mjs'),mode,str((stage/'browser-config.json').relative_to(ROOT))])
        direct.browser_verified(doc/(mode+'-browser.json'),{uid})
    assert read(pointerpath)==pointer and ref(manifestpath)==manifestref,'Current publication changed during recovery'
    evidence={name:ref(source/(name+'.json')) for name in ['result','metrics','validation','foundation','identity-proof','neighbour-checks','native-neighbour-checks','historical-installed-proof']}
    evidence.update(catalogue=ref(cataloguepath),asset=ref(actualasset),runner=ref(Path(__file__)),runtime=ref(HERE/'resolution-recovery-browser.mjs'))
    decision={'batch':a.batch,'uids':[uid],'sourceSHA256':model['sha256'],'passed':True,'checksPassed':True,'failures':[],
              'publication':True,'runtimeAssetsAdded':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'evidence':evidence,
              'stagedBrowser':ref(doc/'staged-browser.json'),'liveBrowser':ref(doc/'live-browser.json'),'manifest':manifestref,
              'qualification':'Existing original publication recovered with fresh full physical and staged/live browser checks; all other current reviews preserved.'}
    save(doc/'acceptance.json',decision)
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']};previous=parts.get(uid,{})
    parts[uid]={**previous,'uid':uid,'name':model['label'],'objectId':model['objectId'],'csuid':model['buildingCSUID'],
                'candidate':{'sha256':model['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-published-original-current-review-recovery','knownHold':False}
    ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16]
    inventorypath=pointerpath.parent/('source-review-inventory-'+snapshot+'.json');save(inventorypath,{**inventory,'parts':ordered,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId']})
    ledger.seed(inventorypath,inherit=pointer['snapshotId'])
    effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':str((doc/'acceptance.json').relative_to(ROOT))}
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    observation='Exact published original recovered into current ledger after fresh full source, terrain, foundation, neighbours and staged/live desktop/mobile day/night, picking, collision and fallback/retry checks. No asset, geometry or placement changes.'
    ledger.record_many(snapshot,leasepath,[(uid,'approved-for-integration',doc/'acceptance.json',observation,commit)],effort=effort,request_id=a.batch+'-approved-'+snapshot)
    installed={**decision,'snapshotId':snapshot};save(doc/'installed-acceptance.json',installed)
    ledger.record_many(snapshot,leasepath,[(uid,'installed-verified',doc/'installed-acceptance.json',observation,commit)],effort=effort,request_id=a.batch+'-installed-'+snapshot)
    assert read(pointerpath)==pointer;save(pointerpath,{**pointer,'snapshotId':snapshot,'inventory':str(inventorypath.relative_to(ROOT)),
                                                     'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    payload={'uid':uid,'sourceSHA256':model['sha256'],'acceptance':ref(doc/'installed-acceptance.json'),'snapshotId':snapshot}
    stage_name='published-original-current-review-recovery-v1';jobid=jobs.enqueue(a.batch,stage_name,payload);job=jobs.claim(a.batch,lease['owner'],[stage_name],lease_seconds=1800);assert job and job['id']==jobid
    final={**installed,'installedUids':[uid],'newlyInstalled':1,'newlyVerifiedInCurrentSnapshot':1,'recoveredPublishedBatch':Path(prior['catalogueURL']).parent.name,
           'runtimeAssetsAdded':0,'jobId':jobid,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),
           'evidenceRefs':[ref(doc/n) for n in ['acceptance.json','installed-acceptance.json','staged-browser.json','live-browser.json']]}
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                           (Jsonb(final),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',final)
    save(doc/'result.json',final);save(doc/'neon-sync.json',{'installedUids':[uid],'jobId':jobid,'resultVerified':True,'snapshotId':snapshot})
    print(json.dumps({'uid':uid,'snapshotId':snapshot,'jobId':jobid,'currentReviewRecovered':True,'runtimeAssetsAdded':0}),flush=True)

if __name__=='__main__':main()
