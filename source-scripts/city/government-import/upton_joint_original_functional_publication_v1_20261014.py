"""ROOT-only ordinary staged/live acceptance and atomic two-original installation.
No geometry calculation; raw strict failures/source applicability remain exact.
"""
from pathlib import Path
import argparse,json,os,subprocess,sys,time,uuid
from urllib.request import urlopen
from run import ROOT,HERE,read,save,connect,reservations,jobs,Jsonb,dict_row,digest
import upton_joint_original_functional_private_stage_v1_20261014 as stage
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from upton_preserve_replacement_slot_v1_20261014 import preserve_slot
physical=stage.physical;ref,check=stage.ref,stage.check
BASE=ROOT/'docs/astra-city/government-import';STAGED_BATCH='government-xl-upton-joint-original-functional-staged-browser-v1-20261014';INSTALL_BATCH='government-xl-upton-joint-original-functional-installed-v1-20261014';STAGED=BASE/STAGED_BATCH;INSTALLED=BASE/INSTALL_BATCH;PUB=HERE/'upton_slot_preserving_guarded_publish_v1_20261014.py'

def verified(folder,job):
    r=read(folder/'result.json');v=read(folder/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    for q in distinct_refs(r['evidenceRefs']):check(q)
    return r

def browser_report(doc,name):
    report=physical.module(HERE/'integrate.py','upton_unchanged_browser_verifier').browser_verified(doc/name,set(stage.OWNED));views=[v for v in report['views']if 'time'in v]
    assert len(views)==8 and all(v['fullyFramed']and v['selectionClosed']and v['fallbackFaces']==0 and v['solidAppearance']and all(o==1 for o in v['materialOpacities'])for v in views)
    own=report['retainedNativeOwnViews'];assert len(own)==4 and {(v['uid'],v['width'],v['time'])for v in own}=={(physical.RETAINED,w,t)for w in [1280,390]for t in ['15:00','22:00']}
    assert all(v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0 for v in own)
    for v in views:
        if v['uid']==stage.OWNED[1]:assert v['nativeSupports'][stage.OWNED[0]]['active']and v['nativeSupports'][stage.OWNED[0]]['visible']and v['nativeSupports'][stage.OWNED[0]]['declaredCandidateSupport']
    return report

def owned(args):
    batch=STAGED_BATCH if args.staged_browser_only else INSTALL_BATCH;doc=BASE/batch;local=HERE/'local'/batch;lease=local/'reservation.json';last=time.monotonic()
    def owns():assert reservations.owns(read(lease))
    def call(cmd):
        log=doc/('command-'+str(len(list(doc.glob('command-*.json')))).zfill(3)+'.json');p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':os.environ.get('CHROME_PATH','/opt/google/chrome/chrome')});save(log,dict(command=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));owns();assert p.returncode==0,log
    owns();assert not doc.exists();
    with urlopen('http://127.0.0.1:4176/city.html',timeout=10)as r:assert r.status==200
    source=verified(stage.DOC,args.stage_job);p,adapted,rows,c,patch=stage.load();assert adapted['scriptChecksPassed']and not adapted['remainingActualPhysicalReasons']and not adapted['strictInterfacePassed']
    with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(args.stage_job,)).fetchone()==('complete',source)
    source_refs=distinct_refs(source['evidenceRefs']+[ref(stage.DOC/'result.json'),ref(stage.DOC/'ROOT-VERIFIED.json'),ref(Path(__file__)),ref(PUB),ref(HERE/'upton_preserve_replacement_slot_v1_20261014.py')]);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==physical.CURRENT
    for q in source_refs:check(q)
    doc.mkdir(parents=True);plan=read(stage.STAGE/'plan.json');models=read(stage.STAGE/'catalogue.json')['models'];assert [m['uid']for m in models]==stage.OWNED
    if args.staged_browser_only:
        config={**read(stage.STAGE/'browser-config.json'),'doc':str(doc.relative_to(ROOT))+'/'};save(local/'browser-config.json',config)
        publication=[sys.executable,str(PUB),str((stage.STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(lease),'--phase',batch];call(publication)
        call(['node',str(stage.BROWSER),'staged',str((local/'browser-config.json').relative_to(ROOT))]);report=browser_report(doc,'staged-browser.json')
        save(doc/'acceptance.json',dict(batch=batch,uids=stage.OWNED,sourceSHA256s={m['uid']:m['sha256']for m in models},passed=True,checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,strictInterfacePassed=False,sourceApplicabilityVerbatim=adapted,sourceStage=ref(stage.DOC/'result.json'),stagedBrowser=ref(doc/'staged-browser.json'),browserConfig=ref(local/'browser-config.json'),plan=ref(stage.STAGE/'plan.json'),livePublicationRequired=True))
        assert manifest.read_bytes()==before
        refs=distinct_refs(source_refs+[ref(f)for f in doc.rglob('*')if f.is_file()]+[ref(local/'browser-config.json')])
        for q in refs:check(q)
        physical.module(physical.FREEZER,'upton_joint_staged_freezer').freeze(batch,'original-functional-assembly-ordinary-solid-staged-browser-no-install',[check(q)for q in refs],dict(uids=stage.OWNED,currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,publication=False,newlyInstalled=0));return
    assert args.staged_exports_inspected and args.expected_main_snapshot and args.previous_count and args.staged_job
    staged_result=verified(STAGED,args.staged_job);acceptance=read(STAGED/'acceptance.json');assert acceptance['passed']and not acceptance['publication']and acceptance['sourceApplicabilityVerbatim']==adapted;browser_report(STAGED,'staged-browser.json')
    with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(args.staged_job,)).fetchone()==('complete',staged_result)
    config=read(HERE/'local'/STAGED_BATCH/'browser-config.json');save(local/'browser-config.json',{**config,'doc':str(doc.relative_to(ROOT))+'/'})
    previous=read(ROOT/args.previous_count);assert len(previous['rows'])==previous['counts']['total']==521
    old_models=[m for url in json.loads(before)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(old_models)==len({m['uid']for m in old_models})==6650 and not set(stage.OWNED)&{m['uid']for m in old_models}
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);pointer_bytes=pointer_path.read_bytes();assert pointer['snapshotId']==args.expected_main_snapshot
    decision={**acceptance,'batch':batch,'sourceStage':ref(stage.DOC/'result.json'),'stagedBrowser':ref(STAGED/'staged-browser.json'),'ROOTStagedExportsInspected':True,'evidence':{'physical-result':ref(stage.DOC/'result.json'),'raw-physical':ref(physical.DOC/'result.json'),'functional-review':p['acceptedROOTReview'],'staged-browser':ref(STAGED/'staged-browser.json'),'plan':ref(stage.STAGE/'plan.json'),'runner':ref(Path(__file__))},'evidenceRefs':source_refs};save(doc/'acceptance.json',decision)
    publication=[sys.executable,str(PUB),str((stage.STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(lease),'--phase',batch];call(publication);assert manifest.read_bytes()==before
    inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']}
    for m in models:
        old=parts.get(m['uid'],{});parts[m['uid']]=dict(uid=m['uid'],name=m['label'],landmarkIds=old.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate=dict(sha256=m['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-assembly',knownHold=False)
    ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=digest(jobs.encode([ordered,decision]).encode())[:16];inv_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json');save(inv_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'Two unchanged Upton originals under exact ROOT accepted authored-facade applicability; raw97/138+41/13unmatched preserved. Complete current finite/foundations/neighbours/terrain and actual staged/live original runtime required; no geometry modelling or new engineering gate.'})
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    ledger.seed(inv_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(doc/'acceptance.json')['path'])
    ledger.record_many(snapshot,lease,[(u,'approved-for-integration',doc/'acceptance.json','Exact ROOT source-functional applicability and all current/staged guards pass; raw strict failure preserved; live pending.',commit)for u in stage.OWNED],effort=effort,request_id=batch+'-approved-'+snapshot)
    (local/'manifest-before-installation.json').write_bytes(before)
    try:
        call(publication+['--apply']);call(['node',str(stage.BROWSER),'live',str((local/'browser-config.json').relative_to(ROOT))]);browser_report(doc,'live-browser.json')
        original=json.loads(before);after=read(manifest);destination=plan['areas'][0]['destination'];assert after['officialModelCatalogues']==original['officialModelCatalogues']+[destination]
        terrain=plan['topLevelTerrainPatches'][0];expected={**original,'officialModelCatalogues':after['officialModelCatalogues'],'terrainPatches':after['terrainPatches']};assert after==expected
        reordered=json.loads(json.dumps(after));slot=preserve_slot(original,reordered,terrain['replaces']['url'],terrain['destination']);assert reordered==after and slot['oldIndex']==slot['replacementIndex']
        assert read(ROOT/'3d-viewer'/destination)==read(stage.STAGE/'catalogue.json')and ref(ROOT/'3d-viewer'/terrain['destination'])['sha256']==terrain['sha256']
        new_models=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert new_models==old_models+models and len(new_models)==len({m['uid']for m in new_models})==6652
        for m in models:assert ref((ROOT/'3d-viewer'/destination).parent/m['asset'])['sha256']==m['sha256']
        # Honest post-apply: old manifest/pointer/progress are historical context,
        # never temporarily restored to rerun old not-installed/current gates.
        mutable={'3d-viewer/city/data/manifest.json','docs/astra-city/model-integration-20260909/current-source-review.json','3d-viewer/city/data/building-progress.json'}
        for q in source_refs:
            if q['path']not in mutable:check(q)
        installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':2,'manifest':ref(manifest),'liveBrowser':ref(doc/'live-browser.json')};save(doc/'installed-acceptance.json',installed)
        ledger.record_many(snapshot,lease,[(u,'installed-verified',doc/'installed-acceptance.json','Both unchanged originals pass source-scoped applicability/current guards and solid staged/live desktop/mobile day/night/source picking/collision/sampler/failed-load retry. Raw strict false retained.',commit)for u in stage.OWNED],effort=effort,request_id=batch+'-installed-'+snapshot)
        assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inv_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
        call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',batch]);counts=read(doc/'full-xl-current-count.json')['counts'];delta=sum(r['uid']in stage.OWNED for r in previous['rows']if not r['installedVerified']);assert counts['total']==521 and counts['installedVerified']==previous['counts']['installedVerified']+delta
        kind='upton-two-exact-original-functional-installed-v1';jid=jobs.enqueue(batch,kind,dict(acceptance=ref(doc/'installed-acceptance.json'),snapshot=snapshot));receipt=read(lease);job=jobs.claim(batch,receipt['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
        result={**installed,'uids':stage.OWNED,'installedUids':stage.OWNED,'evidenceRefs':[ref(doc/n)for n in ['acceptance.json','installed-acceptance.json','staged-browser.json']if(doc/n).exists()]+[ref(doc/'live-browser.json'),ref(STAGED/'staged-browser.json')],'jobId':jid,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':counts}
        with connect()as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,receipt)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect()as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
            states=con.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,stage.OWNED)).fetchall();assert {u:s for u,state,s in states if state=='installed-verified'}=={m['uid']:m['sha256']for m in models}
        save(doc/'result.json',result);save(doc/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot,installedUids=stage.OWNED));print(json.dumps(dict(installed=stage.OWNED,snapshotId=snapshot,jobId=jid,counts=counts)),flush=True)
    except BaseException as error:
        recovery=dict(error=repr(error),installedCreditGranted=False,ledgerHistoryPreserved=True,rollbackErrors=[])
        for name,path,raw in [('manifest',manifest,before),('review-pointer',pointer_path,pointer_bytes)]:
            try:path.write_bytes(raw);recovery[name+'RestoredSHA256']=digest(raw)
            except BaseException as e:recovery['rollbackErrors'].append(dict(step=name,error=repr(e)))
        for cmd in [[sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'],['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]]:
            try:subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
            except BaseException as e:recovery['rollbackErrors'].append(dict(step='progress',error=repr(e)))
        save(doc/'failure-recovery.json',recovery);raise

def main():
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True);g.add_argument('--staged-browser-only',action='store_true');g.add_argument('--install-reviewed-stage-only',action='store_true');parser.add_argument('--stage-job',required=True);parser.add_argument('--staged-job');parser.add_argument('--previous-count');parser.add_argument('--expected-main-snapshot');parser.add_argument('--staged-exports-inspected',action='store_true');parser.add_argument('--owned',action='store_true');args=parser.parse_args();batch=STAGED_BATCH if args.staged_browser_only else INSTALL_BATCH;doc=BASE/batch;local=HERE/'local'/batch;lease=local/'reservation.json'
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(args)
    assert not doc.exists()and not local.exists();verified(stage.DOC,args.stage_job);stage.load();uids=stage.functional.review.scope_uids();resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+batch];claim=reservations.claim('upton-publication-'+str(uuid.uuid4()),resources,batch=batch,ttl=3600);assert claim['ok'];reservation=claim['reservation']
    try:save(lease,json.loads(json.dumps(reservation,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(reservation):assert reservations.release(reservation)['ok']
if __name__=='__main__':main()
