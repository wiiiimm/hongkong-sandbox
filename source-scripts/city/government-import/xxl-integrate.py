"""Guarded publication of the passing XXL subset and a complete 22-source Neon handoff."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
from PIL import Image,ImageStat
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN,jobs,reservations,dict_row,Jsonb
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
spec=importlib.util.spec_from_file_location('prior_integration',HERE/'integrate.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
BATCH='government-xxl-20260911';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;STAGE=HERE/'accepted'/BATCH

def h(p):return digest(Path(p).read_bytes())
def rel(p):return str(Path(p).relative_to(ROOT))
def command(args):subprocess.run(args,cwd=ROOT,check=True)

def images(mode,ids):
    report=prior.browser_verified(DOC/(mode+'-browser.json'),ids);rows=[]
    for v in report['views']:
        if 'file' not in v:continue
        assert v['fullyFramed'] and abs(v['ground']-v['groundSampler'])<=.004
        p=DOC/v['file']
        with Image.open(p) as im:
            im.load();assert im.size==(v['width'],900);sd=ImageStat.Stat(im.convert('RGB')).stddev;assert max(sd)>1
        rows.append({'path':rel(p),'sha256':h(p),'width':v['width'],'height':900,'channelStddev':sd})
    assert len(rows)==4*len(ids)
    save(DOC/(mode+'-images.json'),{'images':rows,'decoded':len(rows),'aiImageReview':False})


def owned():
    receipt_path=LOCAL/'integration-reservation.json';receipt=read(receipt_path);assert reservations.owns(receipt)
    report=read(DOC/'results.json.gz');frozen=read(DOC/'selection.json.gz');source={r['uid']:r for r in frozen['rows'] if r['uid']};checked={r['uid']:r for r in read(DOC/'check-selection.json.gz')['rows']}
    passing={r['uid'] for r in report['rows'] if r['humanStatus']=='in-process'};assert passing=={'landsd/227428:0'}
    for p,sha in report['inputHashes'].items():assert h(ROOT/p)==sha,'Checked inputs changed: '+p
    for row in source.values():
        assert h(ROOT/'3d-viewer'/row['source']['tile'])==row['source']['tileSHA256']
        if row['installedProof']:assert h(ROOT/row['installedProof']['path'])==row['sourceSHA256']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        native=dict(c.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=ANY(%s)',(NATIVE_RUN,[r['native']['cacheKey'] for r in frozen['rows']])))
        states=dict(c.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',(list(passing),)))
    assert all(native[r['native']['cacheKey']]==r['native']['resultSha'] for r in frozen['rows'])
    assert not any(s in ('held','source-unavailable','identity-unresolved','installed-verified') for s in states.values())
    catalogue=read(LOCAL/'recovered/catalogue.json');catalogue['area']='Government XXL original-source imports';catalogue['models']=[]
    for uid in sorted(passing):
        row=checked[uid];e=dict(row['candidate']['entry']);p=Path(row['candidate']['path']);assert h(p)==e['sha256']
        target=STAGE/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        e.update(label=row['source']['building'].get('name') or e['label'],priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview='Scripted original-government-import-v1; all-vertex/centre/low-rim drawn terrain, source identity/hash, unchanged HKPD and mobile budget checks. No AI architectural review.')
        catalogue['models'].append(e)
    catalogue['counts']['packedModels']=len(passing);save(STAGE/'catalogue.json',catalogue)
    forms=[]
    for uid in sorted(passing):
        b=dict(source[uid]['source']['building']);b['tile']=Path(source[uid]['source']['tile']).stem;forms.append(b)
    save(STAGE/'source-forms.json',forms)
    destination='city/data/official-models/'+BATCH+'/catalogue.json'
    plan={'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}]};save(STAGE/'plan.json',plan)
    config={'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':[],'fitBox':True};save(STAGE/'browser-config.json',config)
    decision={'policy':'original-government-import-v1','checkedResultSHA256':h(DOC/'results.json.gz'),'metricsSHA256':h(DOC/'metrics.json'),'policySHA256':h(HERE/'acceptance-policy.py'),'browserRunnerSHA256':h(HERE/'resolution-browser.mjs'),'catalogueSHA256':h(STAGE/'catalogue.json'),'planSHA256':h(STAGE/'plan.json'),'selectedUids':sorted(passing),'aiCalls':0}
    save(DOC/'decision.json',decision)
    command(['node',str(HERE/'resolution-browser.mjs'),'staged',rel(STAGE/'browser-config.json')]);images('staged',passing)
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';previous=read(pointer);inventory=read(ROOT/previous['inventory']);parts={p['uid']:p for p in inventory['parts']}
    for e in catalogue['models']:
        old=parts.get(e['uid'],{});parts[e['uid']]={'uid':e['uid'],'name':e['label'],'landmarkIds':old.get('landmarkIds',[]),'objectId':e['objectId'],'csuid':e['buildingCSUID'],'candidate':{'sha256':e['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-import','knownHold':False}
    new_parts=sorted(parts.values(),key=lambda r:r['uid']);snapshot=digest(jobs.encode([new_parts,decision]).encode())[:16]
    inv=pointer.parent/f'source-review-inventory-{snapshot}.json';save(inv,{**inventory,'snapshotId':snapshot,'derivedFrom':previous['snapshotId'],'parts':new_parts});ledger.seed(inv,inherit=previous['snapshotId'])
    approval={**decision,'stagedBrowserSHA256':h(DOC/'staged-browser.json'),'stagedImagesSHA256':h(DOC/'staged-images.json'),'models':[{'uid':m['uid'],'sha256':m['sha256']} for m in catalogue['models']]};save(DOC/'approval.json',approval)
    effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'approval.json')}
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();observation='Unchanged original XXL source verified through strict source/contact/runtime gates and staged/installed desktop/mobile day/night full-bound framing, picking/collision, terrain rays and fallback/retry. No AI architectural review or whole-landmark completion.'
    ledger.record_many(snapshot,receipt_path,[(uid,'approved-for-integration',DOC/'approval.json',observation,commit) for uid in sorted(passing)],effort=effort,request_id=BATCH+'-approve-'+snapshot)
    pub=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(STAGE/'plan.json'),'--receipt',str(receipt_path),'--phase',BATCH];command(pub)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before-publication.json').write_bytes(before);command(pub+['--apply'])
    try:
        command(['node',str(HERE/'resolution-browser.mjs'),'live',rel(STAGE/'browser-config.json')]);images('live',passing)
    except BaseException:
        manifest.write_bytes(before);raise
    acceptance={**approval,'installedBrowserSHA256':h(DOC/'live-browser.json'),'installedImagesSHA256':h(DOC/'live-images.json'),'manifestSHA256':h(manifest)};save(DOC/'installed-acceptance.json',acceptance)
    ledger.record_many(snapshot,receipt_path,[(uid,'installed-verified',DOC/'installed-acceptance.json',observation,commit) for uid in sorted(passing)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer)==previous;save(pointer,{**previous,'snapshotId':snapshot,'inventory':rel(inv),'previousSnapshots':[*previous.get('previousSnapshots',[]),previous['snapshotId']]})
    command([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);command(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    rows=[]
    for row in report['rows']:
        row=dict(row)
        if row['uid'] in passing:row.update(humanStatus='installed',state='installed-verified',nextStep=None,newlyInstalled=True,installedEvidence=rel(DOC/'installed-acceptance.json'))
        elif row['humanStatus']=='installed':row['reusedVerifiedInstallation']=True
        rows.append(row)
    counts={key:sum(r['humanStatus']==key for r in rows) for key in ['installed','to-do','held-human','held-ai','held-unknown','in-process']};assert sum(counts.values())==22 and counts['in-process']==0
    result={**report,'stage':'government-xxl-first-pass-v1','rows':rows,'humanCounts':counts,'newlyInstalled':len(passing),'snapshotId':snapshot,'installedEvidenceSHA256':h(DOC/'installed-acceptance.json'),'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')}
    job_id=jobs.enqueue(BATCH,result['stage'],{'decisionSHA256':h(DOC/'decision.json'),'snapshot':snapshot});job=jobs.claim(BATCH,receipt['owner'],[result['stage']],lease_seconds=600);assert job and job['id']==job_id
    result['jobId']=job_id;save(DOC/'final-results.json.gz',result);result['evidence']={'path':rel(DOC/'final-results.json.gz'),'sha256':h(DOC/'final-results.json.gz')}
    with connect() as c:
        c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));group=reservations._current(c,receipt);assert group and {'building:'+u for u in source}<=set(group['resources'])
        assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),job_id,job['owner'],job['token'])).rowcount==1
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()[0]==result
        assert dict(c.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,list(passing))))=={uid:'installed-verified' for uid in passing}
    save(DOC/'final-neon-sync.json',{'jobId':job_id,'verifiedRows':22,'exactResultMatch':True,'sourceAndJobFenced':True,'installedReviewVerified':True})
    save(DOC/'final-summary.json',{k:v for k,v in result.items() if k not in ('rows','inputHashes')});print(json.dumps({'newlyInstalled':len(passing),'humanCounts':counts,'neonJob':job_id}),flush=True)


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='owned':owned()
    else:
        frozen=read(DOC/'selection.json.gz');receipt=reservations.claim('codex-xxl-integration-'+str(uuid.uuid4()),['building:'+r['uid'] for r in frozen['rows'] if r['uid']],batch=BATCH+'-integration');assert receipt['ok']
        p=LOCAL/'integration-reservation.json';save(p,json.loads(json.dumps(receipt['reservation'],default=str)))
        command([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--',sys.executable,__file__,'owned'])
