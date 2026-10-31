"""ROOT-only ordinary original-source live installation; immutable geometry/terrain."""
from pathlib import Path
import argparse,sys,json,os,subprocess,uuid
from urllib.request import urlopen
import aqua_marine193086_staged_solid_browser_v1_20261014 as staged
from aqua_original_image_review_binding_v1_20261014 import validate_review,inventory_delta,MUTABLE_CURRENT
from run import ROOT,HERE,read,save,connect,reservations,jobs,Jsonb,dict_row
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
stage=staged.stage;A=stage.A;ref,check,module=stage.ref,stage.check,stage.module
BATCH='government-xl-aqua-marine193086-original-installed-v1-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def browser_verified(doc):
    r=module(HERE/'integrate.py','aqua_original_live_browser_verifier').browser_verified(doc/'live-browser.json',{A.prior.UID});views=[v for v in r['views']if 'time'in v];assert len(views)==4
    for v in views:
        assert v['fullyFramed']and v['selectionClosed']and v['solidAppearance']and v['sourceSHA256']==A.prior.SOURCE_SHA and v['originalTriangles']==22735 and v['fallbackFaces']==0 and all(v['meshVisibility'])and not any(v['wireframeFlags'])and all(x==1 for x in v['materialOpacities']);f=v['retained'][A.prior.FOREIGN];assert f['loaded']and not f['detailedActive']and not f['hidden']
    assert r['unchangedTerrain'];return r

def load(args):
    data,stage_result,adapted,refs=staged.load(args.stage_job);r=read(staged.DOC/'result.json');v=read(staged.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==args.staged_job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];acceptance=read(staged.DOC/'staged-acceptance.json');assert acceptance['passed']and not acceptance['publication']and acceptance['sourceApplicabilityVerbatim']==adapted;report=staged.report()
    review_path=(ROOT/args.staged_review).resolve();assert review_path==staged.DOC/'ROOT-IMAGE-INSPECTION.json';images=[ref(staged.DOC/view['file'])for view in report['views']if 'time'in view];decision=validate_review(read(review_path),job=args.staged_job,report_ref=ref(staged.DOC/'staged-browser.json'),stage_ref=ref(stage.DOC/'result.json'),functional_ref=ref(stage.finite.REVIEW),manifest_sha=A.prior.CURRENT,image_refs=images)
    previous=read(ROOT/args.previous_count);assert previous['counts']==dict(total=521,installedVerified=235,remaining=286);pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');assert pointer['snapshotId']==args.expected_main_snapshot==A.prior.SNAPSHOT
    models=read(stage.STAGE/'catalogue.json')['models'];delta=inventory_delta(previous,models,manifest_sha=A.prior.CURRENT,snapshot=pointer['snapshotId']);assert delta['returnedModels']==delta['expectedFixedXLDelta']==1 and delta['newFixedXLUids']==[A.prior.UID]
    refs=distinct_refs(refs+r['evidenceRefs']+[ref(staged.DOC/'result.json'),ref(staged.DOC/'ROOT-VERIFIED.json'),ref(review_path),ref(ROOT/args.previous_count),ref(Path(__file__))])
    for q in refs:check(q)
    return data,stage_result,r,adapted,acceptance,decision,previous,pointer,models,delta,refs

def schema_only(args):
    data,*_=load(args);return dict(passed=True,caller=ref(Path(__file__)),stageJob=args.stage_job,stagedJob=args.staged_job,stagedImageReview=ref(ROOT/args.staged_review),previousCount=ref(ROOT/args.previous_count),expectedMainSnapshot=args.expected_main_snapshot,scope=data[-1],currentCatalogue6652=True,expectedCatalogue6653=True,expectedFixed521=dict(total=521,installedVerified=236,remaining=285),oneOriginalSourceOnly=True,terrainChanges=0,noPublicationBrowserLedgerProgressDBLeaseWorker=True)

def owned(args):
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['stageJob']==args.stage_job and prep['stagedJob']==args.staged_job and prep['stagedImageReview']==ref(ROOT/args.staged_review)and prep['previousCount']==ref(ROOT/args.previous_count)and prep['expectedMainSnapshot']==args.expected_main_snapshot
    data,sr,br,adapted,accepted,image_decision,previous,pointer,models,delta,refs=load(args);refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';before=manifest.read_bytes();pointer_bytes=pointer_path.read_bytes();assert A.prior.digest(before)==A.prior.CURRENT;published_manifest=None;expected_pointer_bytes=pointer_bytes;pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def source_fence(after_apply=False):
        pulse(force=True)
        for q in refs:
            if not after_apply or q['path']not in MUTABLE_CURRENT:check(q)
            pulse()
        if not after_apply:assert manifest.read_bytes()==before and pointer_path.read_bytes()==pointer_bytes
        elif published_manifest is not None:assert manifest.read_bytes()==published_manifest and pointer_path.read_bytes()==expected_pointer_bytes
        pulse(force=True)
    source_fence()
    for job,result in [(args.stage_job,sr),(args.staged_job,br)]:
        with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',result)
    config=read(staged.LOCAL/'browser-config.json')
    for url,sha in [('city/data/manifest.json',config['currentManifest']['sha256']),('city/app.js',config['servedApp']['sha256'])]:
        with urlopen('http://127.0.0.1:4176/'+url,timeout=20)as response:assert response.status==200 and A.prior.digest(response.read())==sha
    original=json.loads(before);old_models=[m for url in original['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(old_models)==len({m['uid']for m in old_models})==6652 and A.prior.UID not in {m['uid']for m in old_models};plan=read(stage.STAGE/'plan.json');assert plan['topLevelTerrainPatches']==[]and len(plan['areas'])==1;destination=plan['areas'][0]['destination'];DOC.mkdir();save(LOCAL/'browser-config.json',{**config,'doc':str(DOC.relative_to(ROOT))+'/'})
    decision={**accepted,**image_decision,'batch':BATCH,'stagedImageReview':ref(ROOT/args.staged_review),'ROOTStagedExportsInspected':True,'sourceStage':ref(stage.DOC/'result.json'),'stagedBrowser':ref(staged.DOC/'staged-browser.json'),'fixedXLDeltaBinding':delta,'evidenceRefs':refs,'rawStrictFoundationPassed':False,'sourceApplicabilityVerbatim':adapted,'publication':False,'newlyInstalled':0};save(DOC/'acceptance.json',decision)
    snapshots=[]
    for rel in sorted(MUTABLE_CURRENT):
        src=ROOT/rel
        if src.exists():
            dest=LOCAL/'historical-current'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes());assert ref(src)['sha256']==ref(dest)['sha256'];snapshots.append(dict(original=ref(src),savedHistoricalBytes=ref(dest)))
    save(DOC/'historical-input-context.json',dict(preInstallManifestSHA256=A.prior.CURRENT,preInstallSnapshot=A.prior.SNAPSHOT,mutableCurrentByteSnapshots=snapshots,sourceEvidenceRefsVerbatim=refs,meaning='Exact pre-install2a4/518 bytes remain immutable historical source context after honest publication. Never restore old current bytes merely to rerun a not-installed/source gate.'))
    def call(command,after_apply=False):
        source_fence(after_apply);process=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':os.environ.get('CHROME_PATH','/opt/google/chrome/chrome')});save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=command,exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));source_fence(after_apply);assert process.returncode==0
    publication=[sys.executable,str(stage.PUB),str((stage.STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(LEASE),'--phase',BATCH];call(publication)
    dry=ROOT/'docs/astra-city/model-integration-20260909'/BATCH/'publication-plan.json';assert not read(dry)['published']and set(read(dry)['after'])=={'3d-viewer/city/data/manifest.json','3d-viewer/'+destination}
    inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']};m=models[0];old=parts.get(A.prior.UID,{});parts[A.prior.UID]=dict(uid=A.prior.UID,name=m['label'],landmarkIds=old.get('landmarkIds',[]),objectId=m['objectId'],csuid=m['buildingCSUID'],candidate=dict(sha256=m['sha256']),sourceProgress='prepared-for-review',classification='script-verified-exact-original-functional-source',knownHold=False);ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=A.prior.digest(jobs.encode([ordered,decision]).encode())[:16];inv_path=pointer_path.parent/('source-review-inventory-'+snapshot+'.json');save(inv_path,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered,'qualification':'One unchanged original Aqua Marine government source under exact ROOT accepted three-face authored lower facade closure applicability; raw strict false/all278/minimum gap remain. Complete current four-world source coverage/zero independent foreign contacts and actual staged/live original runtime required; no geometry modelling or structural/root/watertight gate.'})
    sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
    ledger.seed(inv_path,inherit=pointer['snapshotId']);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort=dict(method='unknown',ai_model=None,reasoning_effort='unknown',issue='HKS-203',run_id=snapshot,output_ref=ref(DOC/'acceptance.json')['path']);ledger.record_many(snapshot,LEASE,[(A.prior.UID,'approved-for-integration',DOC/'acceptance.json','Exact original identity/current guards/ROOT narrow source warning and four staged inspected exports pass; raw strict false preserved; live pending.',commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot);(LOCAL/'manifest-before-installation.json').write_bytes(before);phase=dict(installedReviewsRecorded=False,currentReviewPointerActivated=False)
    try:
        # --apply intentionally changes manifest; old current hashes become history.
        source_fence();process=subprocess.run(publication+['--apply'],cwd=ROOT,capture_output=True,text=True);save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=publication+['--apply'],exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));source_fence(True);assert process.returncode==0
        after=read(manifest);assert after=={**original,'officialModelCatalogues':original['officialModelCatalogues']+[destination]};assert read(ROOT/'3d-viewer'/destination)==read(stage.STAGE/'catalogue.json');published_manifest=manifest.read_bytes();new_models=[m for url in after['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert new_models==old_models+models and len(new_models)==len({m['uid']for m in new_models})==6653
        for m in models:assert ref((ROOT/'3d-viewer'/destination).parent/m['asset'])['sha256']==m['sha256']==A.prior.SOURCE_SHA
        for native in data[10]:assert ref(ROOT/'3d-viewer'/native['url'])==native['source']
        call(['node',str(stage.BROWSER),'live',str((LOCAL/'browser-config.json').relative_to(ROOT))],True);browser_verified(DOC)
        installed={**decision,'snapshotId':snapshot,'publication':True,'newlyInstalled':1,'installedUids':[A.prior.UID],'manifest':ref(manifest),'liveBrowser':ref(DOC/'live-browser.json'),'completeCurrentCatalogueModels':6653};save(DOC/'installed-acceptance.json',installed);ledger.record_many(snapshot,LEASE,[(A.prior.UID,'installed-verified',DOC/'installed-acceptance.json','One immutable government source passes exact identity/ROOT scoped warning/full current coverage/zero independent foreign contacts, ROOT-inspected staged exports and actual solid staged/live desktop/mobile day/night/source picking/collision/sampler/failed-load retry. Raw strict false/all278 remain.',commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot);phase['installedReviewsRecorded']=True
        assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':ref(inv_path)['path'],'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]});phase['currentReviewPointerActivated']=True;expected_pointer_bytes=pointer_path.read_bytes()
        call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'],True);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')],True);call([sys.executable,str(HERE/'xl-current-installed-count-audit.py'),'--previous',args.previous_count,'--batch',BATCH],True);counts=read(DOC/'full-xl-current-count.json')['counts'];assert counts==dict(total=521,installedVerified=236,remaining=285)
        kind='aqua-one-exact-original-functional-installed-v1';jid=jobs.enqueue(BATCH,kind,dict(acceptance=ref(DOC/'installed-acceptance.json'),snapshot=snapshot));receipt=read(LEASE);job=jobs.claim(BATCH,receipt['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
        result={**installed,'uids':[A.prior.UID],'historicalExactInputContextVerbatim':[q for q in refs if q['path']in MUTABLE_CURRENT],'historicalMutableByteSnapshots':snapshots,'evidenceRefs':distinct_refs([q for q in refs if q['path']not in MUTABLE_CURRENT]+[ref(q)for q in DOC.rglob('*')if q.is_file()]+[ref(q)for q in LOCAL.rglob('*')if q.is_file()and q.name!='reservation.json']+[ref(q)for q in (ROOT/'docs/astra-city/model-integration-20260909'/BATCH).rglob('*')if q.is_file()]+[ref(ROOT/q)for q in sorted(MUTABLE_CURRENT)if(ROOT/q).exists()]+[ref(inv_path),ref(ROOT/'3d-viewer'/destination)]+[ref((ROOT/'3d-viewer'/destination).parent/m['asset'])for m in models]),'jobId':jid,'activeWorkers':0,'queuedFollowups':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'fullXLCurrentCounts':counts}
        source_fence(True)
        with connect()as db:
            db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(db,receipt);assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect()as db:
            db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result);rows=db.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,[A.prior.UID])).fetchall();assert rows==[(A.prior.UID,'installed-verified',A.prior.SOURCE_SHA)]
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True,snapshotId=snapshot,installedUids=[A.prior.UID]));print(json.dumps(dict(installed=[A.prior.UID],snapshotId=snapshot,jobId=jid,counts=counts)),flush=True)
    except BaseException as error:
        recovery=dict(error=repr(error),installedReviewsMayPersistInDerivedSnapshot=phase['installedReviewsRecorded'],currentPointerWasActivated=phase['currentReviewPointerActivated'],ledgerHistoryPreserved=True,currentCreditRequiresRestoredPointerAndCountAudit=True,rollbackErrors=[])
        for name,path,raw in [('manifest',manifest,before),('review-pointer',pointer_path,pointer_bytes)]:
            try:path.write_bytes(raw);recovery[name+'RestoredSHA256']=A.prior.digest(raw)
            except BaseException as e:recovery['rollbackErrors'].append(dict(step=name,error=repr(e)))
        for command in [[sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh'],['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]]:
            try:subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
            except BaseException as e:recovery['rollbackErrors'].append(dict(step='progress',error=repr(e)))
        save(DOC/'failure-recovery.json',recovery);raise

def main():
    p=argparse.ArgumentParser();p.add_argument('--schema-only',action='store_true');p.add_argument('--install-reviewed-stage-only',action='store_true');p.add_argument('--stage-job',required=True);p.add_argument('--staged-job',required=True);p.add_argument('--previous-count',required=True);p.add_argument('--expected-main-snapshot',required=True);p.add_argument('--staged-review',required=True);p.add_argument('--owned',action='store_true');args=p.parse_args()
    if args.schema_only:print(json.dumps(schema_only(args)));return
    if args.owned:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(args)
    assert args.install_reviewed_stage_only and not DOC.exists()and not LOCAL.exists();data,*_=load(args);prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));scope=data[-1];resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-original-install-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
