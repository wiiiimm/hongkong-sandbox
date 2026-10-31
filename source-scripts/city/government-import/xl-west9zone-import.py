"""Publish the verified unchanged WEST9ZONE government model and bounded source terrain."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;CHECK=s.DOC/'terrain-west9zone';DOC=s.DOC/'west9zone-install';LOCAL=s.LOCAL/'west9zone-install';STAGE=HERE/'accepted/government-xl-west9zone-20260913';UID='landsd/229310:0';SUPPORT='landsd/82897:0';BATCH='government-xl-west9zone-20260913'
read,save,h,rel=s.read,s.save,s.h,s.rel
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
spec=importlib.util.spec_from_file_location('direct',HERE/'integrate.py');direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)

def call(args):subprocess.run(args,cwd=ROOT,check=True)

def start():
    assert read(CHECK/'result.json')['passed']
    resources=read(s.LOCAL/'terrain-west9zone-stage/reservation.json')['resources']
    claim=s.reservations.claim('codex-xl-west9zone-import-'+str(uuid.uuid4()),resources,batch=BATCH);assert claim['ok']
    receipt=LOCAL/'reservation.json';save(receipt,json.loads(json.dumps(claim['reservation'],default=str)))
    call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(receipt),'--',sys.executable,__file__,'owned'])

def owned():
    receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt));result=read(CHECK/'result.json');assert result['passed'] and not result['reasons'] and result['aiCalls']==0
    selection=read(CHECK/'selection.json.gz');row=selection['rows'][0];assert row['uid']==UID
    support=read(CHECK/'source-support.json');assert support['resolved']==[SUPPORT] and support['aiCalls']==0
    neighbours=read(CHECK/'neighbour-checks.json');assert neighbours['patches'][0]['blockedBy']==[SUPPORT]
    metrics=read(CHECK/'metrics.json');metric=metrics['rows'][0];assert metric['uid']==UID and metric['sourcePreserved'] and not metric['missingTerrain']
    validation=read(CHECK/'validation.json');assert validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0 and not validation['results'][0]['concerns']
    catalogue=read(s.LOCAL/'terrain-west9zone-stage/candidates/catalogue.json');assert [e['uid'] for e in catalogue['models']]==[UID]
    entry=catalogue['models'][0];entry.update(label='WEST9ZONE',priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview='Exact unchanged government WEST9ZONE podium matched by object ID and Building CSUID. Bounded original source terrain passes runtime and neighbour checks; Florient Rise Tower 2 remains visible and is supported by the podium roof across 99.998% of its footprint. No AI modelling or model geometry edits.')
    asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s.LOCAL/'terrain-west9zone-stage/candidates'/entry['asset'],asset);assert h(asset)==entry['sha256']
    catalogue.update(area='WEST9ZONE original government model',counts={'packedModels':1},models=[entry]);save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    source=next(x for x in read(s.DOC/'selection.json.gz')['rows'] if x['uid']==UID);form=dict(source['source']['building']);form['tile']=Path(source['source']['tile']).stem;save(STAGE/'source-forms.json',[form])
    patch=result['patch'];src=ROOT/patch['path'];assert h(src)==patch['sha256'];dst=STAGE/src.name;shutil.copyfile(src,dst)
    terrain={'source':rel(dst),'sha256':h(dst),'destination':'city/data/'+dst.name,'resolution':read(dst)['cell'],'area':'WEST9ZONE bounded original government terrain'}
    destination='city/data/official-models/'+BATCH+'/catalogue.json';plan={'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}],'topLevelTerrainPatches':[terrain]};save(STAGE/'plan.json',plan)
    config={'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':[terrain],'fitBox':True,'browserUids':[UID],'failureTestUids':[UID]};save(STAGE/'browser-config.json',config)
    evidence_paths=[CHECK/'result.json',CHECK/'metrics.json',CHECK/'validation.json',CHECK/'neighbour-checks.json',CHECK/'source-support.json',CHECK/'terrain-resolution.json',HERE/'xl-stage-west9zone.py',HERE/'native_patch_resolution.py',HERE/'resolution-browser.mjs']
    evidence={rel(p):h(p) for p in evidence_paths};inputs={**metrics['inputHashes'],**neighbours['sourceInputHashes']}
    for path,sha in inputs.items():assert h(ROOT/path)==sha
    decision={'policy':'original-government-west9zone-supported-podium-v1','uid':UID,'supportedNeighbour':SUPPORT,'sourceSHA256':entry['sha256'],'catalogueSHA256':h(STAGE/'catalogue.json'),'planSHA256':h(STAGE/'plan.json'),'inputHashes':inputs,'evidenceHashes':evidence,'aiCalls':0,'geometryChanges':0};save(DOC/'decision.json',decision)
    call(['node',str(HERE/'resolution-browser.mjs'),'staged',rel(STAGE/'browser-config.json')]);direct.browser_verified(DOC/'staged-browser.json',{UID})
    for path,sha in {**inputs,**evidence}.items():assert h(ROOT/path)==sha,'Input changed during staged browser checks: '+path
    with s.connect() as c:
        c.execute('SET TRANSACTION READ ONLY');states=dict(c.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY uid,updated_at DESC',(UID,)));native=dict(c.execute('SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(source['native']['cacheKey'],)))
    assert states.get(UID) not in ('held','source-unavailable','identity-unresolved','installed-verified');assert native[source['native']['cacheKey']]==source['native']['resultSha']
    pointer_path=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointer_path);inventory=read(ROOT/pointer['inventory']);parts={p['uid']:p for p in inventory['parts']};old=parts.get(UID,{})
    parts[UID]={'uid':UID,'name':entry['label'],'landmarkIds':old.get('landmarkIds',[]),'objectId':entry['objectId'],'csuid':entry['buildingCSUID'],'candidate':{'sha256':entry['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-supported-podium','knownHold':False}
    ordered=sorted(parts.values(),key=lambda x:x['uid']);snapshot=s.digest(s.jobs.encode([ordered,decision]).encode())[:16];inv=pointer_path.parent/f'source-review-inventory-{snapshot}.json';save(inv,{**inventory,'snapshotId':snapshot,'derivedFrom':pointer['snapshotId'],'parts':ordered});ledger.seed(inv,inherit=pointer['snapshotId'])
    approval={**decision,'stagedBrowserSHA256':h(DOC/'staged-browser.json')};save(DOC/'approval.json',approval);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'approval.json')};observation='Exact unchanged WEST9ZONE government podium with bounded source terrain. Florient Rise Tower 2 support, neighbour regression, runtime budget, staged/live browser, picking, collision and fallback/retry checks passed. No AI modelling or model geometry edits.'
    ledger.record_many(snapshot,receipt,[(UID,'approved-for-integration',DOC/'approval.json',observation,commit)],effort=effort,request_id=BATCH+'-approved-'+snapshot)
    pub=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(STAGE/'plan.json'),'--receipt',str(receipt),'--phase',BATCH];call(pub);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before.json').write_bytes(before);call(pub+['--apply'])
    try:call(['node',str(HERE/'resolution-browser.mjs'),'live',rel(STAGE/'browser-config.json')]);direct.browser_verified(DOC/'live-browser.json',{UID})
    except BaseException:manifest.write_bytes(before);raise
    acceptance={**approval,'snapshot':snapshot,'liveBrowserSHA256':h(DOC/'live-browser.json'),'manifestSHA256':h(manifest)};save(DOC/'installed-acceptance.json',acceptance);ledger.record_many(snapshot,receipt,[(UID,'installed-verified',DOC/'installed-acceptance.json',observation,commit)],effort=effort,request_id=BATCH+'-installed-'+snapshot)
    assert read(pointer_path)==pointer;save(pointer_path,{**pointer,'snapshotId':snapshot,'inventory':rel(inv),'previousSnapshots':[*pointer.get('previousSnapshots',[]),pointer['snapshotId']]})
    call([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);call(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')]);save(DOC/'summary.json',{'installedUids':[UID],'supportedNeighbour':SUPPORT,'snapshot':snapshot,'aiCalls':0,'geometryChanges':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')});print(json.dumps({'installed':UID,'supportedNeighbour':SUPPORT,'snapshot':snapshot,'aiCalls':0}),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
