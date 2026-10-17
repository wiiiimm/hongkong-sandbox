"""Guarded publication of the mechanically verified original Saxon tower/podium pair."""
import importlib.util,json,sys,uuid,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageStat
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE,DOC,LOCAL=s.ROOT,s.HERE,s.DOC/'saxon-install',s.LOCAL/'saxon-install';CHECK=s.DOC/'saxon-terrain-local';STAGE=HERE/'accepted/government-xxl-saxon-20260911';read,save,h,rel=s.read,s.save,s.h,s.rel
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
spec=importlib.util.spec_from_file_location('direct_import',HERE/'integrate.py');direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)
IDS={'landsd/76364:0','landsd/232025:0'};BATCH='government-xxl-saxon-20260911'

def images(mode):
    report=direct.browser_verified(DOC/(mode+'-browser.json'),IDS);out=[]
    for v in report['views']:
        if 'file' not in v:continue
        assert v['fullyFramed'] and abs(v['ground']-v['groundSampler'])<=.004
        p=DOC/v['file']
        with Image.open(p) as im:im.load();assert im.size==(v['width'],900);sd=ImageStat.Stat(im.convert('RGB')).stddev;assert max(sd)>1
        out.append({'path':rel(p),'sha256':h(p),'width':v['width'],'height':900,'stddev':sd})
    assert len(out)==8;save(DOC/(mode+'-images.json'),{'images':out,'aiImageReview':False})

def start():
    assert read(CHECK/'result.json')['passed'];resources=read(s.LOCAL/'saxon-terrain-local/reservation.json')['resources'];claim=s.reservations.claim('codex-xxl-saxon-import-'+str(uuid.uuid4()),resources,batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt));result=read(CHECK/'result.json');assert result['passed'];source=read(CHECK/'selection.json.gz');assert {r['uid'] for r in source['rows']}==IDS
    metrics=read(CHECK/'metrics.json');neighbours=read(CHECK/'neighbour-checks.json');support=read(CHECK/'unchanged-support.json');assert not support['remaining'];assert support['checksSHA256']==h(CHECK/'neighbour-checks.json') and support['inputSHA256']==h(CHECK/'neighbour-inputs.json.gz')
    inputs={**metrics['inputHashes'],**neighbours['sourceInputHashes']};evidence={rel(p):h(p) for p in [CHECK/'result.json',CHECK/'metrics.json',CHECK/'validation.json',CHECK/'unchanged-support.json',s.DOC/'saxon-support-triangles.json',HERE/'xxl-saxon-stage.py',HERE/'unchanged_support.py',HERE/'resolve-pass.py',HERE/'xxl-stage-local-saxon.py']}
    for p,sha in {**inputs,**evidence}.items():assert h(ROOT/p)==sha
    with s.connect() as c:
        c.execute('SET TRANSACTION READ ONLY');pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');states=dict(c.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(pointer['snapshotId'],list(IDS))));native=dict(c.execute('SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=ANY(%s)',([r['native']['cacheKey'] for r in source['rows']],)))
    assert not any(x in ('held','source-unavailable','identity-unresolved','installed-verified') for x in states.values());assert all(native[r['native']['cacheKey']]==r['native']['resultSha'] for r in source['rows'])
    cat=read(s.LOCAL/'saxon-terrain-local/candidates/catalogue.json');forms=[]
    for e in cat['models']:
        src=s.LOCAL/'saxon-terrain-local/candidates'/e['asset'];assert h(src)==e['sha256'];dst=STAGE/e['asset'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        e.update(priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview='Unchanged original government pair. Podium passes direct source/terrain checks; tower lower rim fully covered by actual native podium surfaces. Current neighbour/support, stage/live runtime and source guards required. No new AI architectural review.')
        if e['uid']=='landsd/76364:0':e['supportDependencies']=[{'uid':'landsd/232025:0','state':'candidate'}]
        b=dict(next(r['source']['building'] for r in source['rows'] if r['uid']==e['uid']));b['tile']=Path(next(r['source']['tile'] for r in source['rows'] if r['uid']==e['uid'])).stem;forms.append(b)
    save(STAGE/'catalogue.json',cat);save(STAGE/'source-forms.json',forms);patch=result['patch'];src=ROOT/patch['path'];assert h(src)==patch['sha256'];dst=STAGE/src.name;shutil.copyfile(src,dst)
    terrain={'source':rel(dst),'sha256':h(dst),'destination':'city/data/'+dst.name,'resolution':read(dst)['cell'],'area':'Saxon original native terrain'};plan={'areas':[{'area':'Saxon original tower and podium','catalogue':rel(STAGE/'catalogue.json'),'destination':'city/data/official-models/'+BATCH+'/catalogue.json'}],'topLevelTerrainPatches':[terrain]};save(STAGE/'plan.json',plan);save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':plan['areas'][0]['destination'],'terrain':[terrain],'fitBox':True})
    decision={'policy':'original-government-supported-pair-v1','inputHashes':inputs,'evidenceHashes':evidence,'catalogueSHA256':h(STAGE/'catalogue.json'),'planSHA256':h(STAGE/'plan.json'),'browserSHA256':h(HERE/'resolution-browser.mjs'),'sourceModels':[{'uid':e['uid'],'sha256':e['sha256']} for e in cat['models']],'aiCalls':0};save(DOC/'decision.json',decision)
    s.call(['node',str(HERE/'resolution-browser.mjs'),'staged',rel(STAGE/'browser-config.json')]);images('staged')
    for p,sha in {**inputs,**evidence}.items():assert h(ROOT/p)==sha,'Input changed during browser checks'
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer_path)==pointer;inventory=read(ROOT/pointer['inventory']);parts={r['uid']:r for r in inventory['parts']}
    for e in cat['models']:
        old=parts.get(e['uid'],{});parts[e['uid']]={'uid':e['uid'],'name':e.get('label'),'landmarkIds':old.get('landmarkIds',[]),'objectId':e['objectId'],'csuid':e['buildingCSUID'],'candidate':{'sha256':e['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-supported-government-pair','knownHold':False}
    ordered=sorted(parts.values(),key=lambda r:r['uid']);snapshot=s.digest(s.jobs.encode([ordered,decision]).encode())[:16];inv=pointer_path.parent/f'source-review-inventory-{snapshot}.json';save(inv,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered});ledger.seed(inv,inherit=pointer['snapshotId'])
    approval={**decision,'models':decision['sourceModels'],'stagedBrowserSHA256':h(DOC/'staged-browser.json'),'stagedImagesSHA256':h(DOC/'staged-images.json')};save(DOC/'approval.json',approval);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'approval.json')};observation='Original supported government pair, native source terrain and unchanged neighbouring podium support verified by script; stage/live desktop/mobile day/night, picking/collision, terrain ray and fallback/retry checks. No AI model generation, architectural review or source elevation changes.'
    ledger.record_many(snapshot,receipt,[(uid,'approved-for-integration',DOC/'approval.json',observation,commit) for uid in sorted(IDS)],effort=effort,request_id=BATCH+'-approve-'+snapshot)
    pub=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(STAGE/'plan.json'),'--receipt',str(receipt),'--phase',BATCH];s.call(pub);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before.json').write_bytes(before);s.call(pub+['--apply'])
    try:s.call(['node',str(HERE/'resolution-browser.mjs'),'live',rel(STAGE/'browser-config.json')]);images('live')
    except BaseException:manifest.write_bytes(before);raise
    acceptance={**approval,'installedBrowserSHA256':h(DOC/'live-browser.json'),'installedImagesSHA256':h(DOC/'live-images.json'),'manifestSHA256':h(manifest)};save(DOC/'installed-acceptance.json',acceptance)
    ledger.record_many(snapshot,receipt,[(uid,'installed-verified',DOC/'installed-acceptance.json',observation,commit) for uid in sorted(IDS)],effort=effort,request_id=BATCH+'-installed-'+snapshot);assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inv),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    s.call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);s.call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    save(DOC/'summary.json',{'installedUids':sorted(IDS),'newXXLModels':1,'newSupportingModels':1,'snapshot':snapshot,'aiCalls':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')});print(json.dumps({'installed':sorted(IDS),'snapshot':snapshot,'aiCalls':0}),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
