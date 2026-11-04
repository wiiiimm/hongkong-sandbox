"""Guarded installation plus terminal per-form outcomes for the 198-model pass."""
import hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageStat
from run import ROOT,HERE,read,save,digest,connect,jobs,reservations,Jsonb,dict_row,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger
spec=importlib.util.spec_from_file_location('direct_integration',HERE/'integrate.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
DOC=ROOT/'docs/astra-city/government-import/government-200-20260911/resolution';LOCAL=HERE/'local/government-198-resolution-20260911';STAGE=HERE/'accepted/government-198-resolution-20260911'

def command(args):subprocess.run(args,cwd=ROOT,check=True)

def verify_images(mode,ids):
    browser=prior.browser_verified(DOC/(mode+'-browser.json'),ids);images=[]
    for view in browser['views']:
        if 'file' not in view:continue
        path=DOC/view['file']
        with Image.open(path) as im:
            im.load();assert im.size==(view['width'],900);std=ImageStat.Stat(im.convert('RGB')).stddev;assert max(std)>1
        images.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'width':view['width'],'height':900,'channelStddev':std})
        assert abs(view['ground']-view['groundSampler'])<=.004
    assert len(images)==4*len(ids)
    report={'images':images,'decoded':len(images),'aiImageReview':False};save(DOC/(mode+'-image-verification.json'),report)
    return report


def main():
    receipt_path=LOCAL/'reservation.json';receipt=read(receipt_path);assert reservations.owns(receipt)
    decision=read(DOC/'decision.json');catalogue=read(STAGE/'catalogue.json');ids={m['uid'] for m in catalogue['models']};assert ids==set(decision['selectedUids'])
    verify_images('staged',ids)
    for p,h in {**decision['inputHashes'],**decision['evidenceHashes']}.items():assert digest((ROOT/p).read_bytes())==h,'Evidence/input changed: '+p
    assert digest((STAGE/'catalogue.json').read_bytes())==decision['catalogueSHA256'] and digest((STAGE/'plan.json').read_bytes())==decision['planSHA256']
    assert digest((HERE/'acceptance-policy.py').read_bytes())==decision['policySHA256']
    sources=read(DOC/'selection.json.gz')['rows'];source_by_uid={r['uid']:r for r in sources}
    for r in sources:assert digest((ROOT/'3d-viewer'/r['source']['tile']).read_bytes())==r['source']['tileSHA256']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');states=dict(c.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',(sorted(ids),)))
        native=dict(c.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=ANY(%s)',(NATIVE_RUN,sorted({r['native']['cacheKey'] for r in sources}))))
    assert not any(s in ('held','source-unavailable','identity-unresolved','installed-verified') for s in states.values())
    assert all(native.get(r['native']['cacheKey'])==r['native']['resultSha'] for r in sources)
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';previous=read(pointer);inventory=read(ROOT/previous['inventory']);parts={p['uid']:p for p in inventory['parts']}
    for r in sources:
        uid=r['uid'];e=r['candidate']['entry']
        parts[uid]={'uid':uid,'name':e.get('label'),'landmarkIds':parts.get(uid,{}).get('landmarkIds',[]),'objectId':e['objectId'],'csuid':e['buildingCSUID'],'candidate':{'sha256':e['sha256']},'sourceProgress':'prepared-for-review','classification':'script-verified-original-government-import' if uid in ids else 'script-blocked-original-government-import','knownHold':uid not in ids}
    new_parts=sorted(parts.values(),key=lambda p:p['uid']);snapshot=hashlib.sha256(jobs.encode([new_parts,decision['policy'],decision['planSHA256']]).encode()).hexdigest()[:16]
    inv=pointer.parent/f'source-review-inventory-{snapshot}.json';save(inv,{**inventory,'snapshotId':snapshot,'derivedFrom':previous['snapshotId'],'parts':new_parts,'qualification':'Original source ports and explicit blocked outcomes for the 198-form resolution pass; no whole-building architecture claim.'});ledger.seed(inv,inherit=previous['snapshotId'])
    approval={'policy':decision['policy'],'models':[{'uid':m['uid'],'sha256':m['sha256']} for m in catalogue['models']],'decisionSHA256':digest((DOC/'decision.json').read_bytes()),'stagedBrowserSHA256':digest((DOC/'staged-browser.json').read_bytes()),'stagedImagesSHA256':digest((DOC/'staged-image-verification.json').read_bytes()),'planSHA256':decision['planSHA256'],'aiCalls':0,'architectureReconstruction':False};save(DOC/'approval.json',approval)
    effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':str((DOC/'approval.json').relative_to(ROOT))};commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    observation='Unchanged original government source verified by current identity/native contact, stitched source terrain, conservative neighbour regression guards, mobile budgets, staged desktop/mobile day/night picking/collision/ground-ray and fallback/retry checks. No AI architecture judgement.'
    ledger.record_many(snapshot,receipt_path,[(uid,'approved-for-integration',DOC/'approval.json',observation,commit) for uid in sorted(ids)],effort=effort,request_id='government-resolution-approve-'+snapshot)
    publication=[sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),str((STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(receipt_path),'--phase','government-resolution-20260911'];command(publication)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();(LOCAL/'manifest-before-publication.json').write_bytes(before)
    command(publication+['--apply'])
    try:
        command(['node',str(HERE/'resolution-browser.mjs'),'live']);verify_images('live',ids)
    except BaseException:
        manifest.write_bytes(before);raise
    approval.update(installedBrowserSHA256=digest((DOC/'live-browser.json').read_bytes()),installedImagesSHA256=digest((DOC/'live-image-verification.json').read_bytes()),manifestSHA256=digest(manifest.read_bytes()));save(DOC/'installed-acceptance.json',approval)
    ledger.record_many(snapshot,receipt_path,[(uid,'installed-verified',DOC/'installed-acceptance.json',observation,commit) for uid in sorted(ids)],effort=effort,request_id='government-resolution-installed-'+snapshot)
    # Finish every other form with its concrete observed blockers, not an unexplained queue.
    resolution=read(DOC/'source-resolution.json');neighbours=read(DOC/'neighbour-checks.json');support={r['uid']:r for r in read(DOC/'support-triangle-checks.json')['rows']};metrics={r['uid']:r for r in read(DOC/'staged-metrics.json')['rows']};outcomes=[]
    for row in resolution['rows']:
        uid=row['uid'];reasons=list(row['reasons'])
        for patch in neighbours['patches']:
            if uid in patch['uids'] and patch['blockedBy']:reasons.append('terrain-correction-regresses-neighbours')
        if uid not in ids and not reasons:reasons.append('automatic-integration-proof-incomplete')
        outcomes.append({**row,'state':'installed-verified' if uid in ids else 'held','humanStatus':'installed' if uid in ids else 'held-unknown','reasons':[] if uid in ids else sorted(set(reasons)),'nextDependency':None if uid in ids else 'unknown','nextStep':None if uid in ids else 'Resolve the recorded technical blocker with new source or validated engineering evidence; no AI or human decision requirement established','supportDiagnostics':support[uid]['hints'],'published':uid in ids,'aiCalls':0})
    held=[r for r in outcomes if r['humanStatus']=='held-unknown'];assert len(outcomes)==198 and len(held)+len(ids)==198
    report={'batch':'government-200-20260911','pass':'government-198-resolution-20260911','modelsProcessed':198,'newlyInstalled':len(ids),'previouslyInstalled':2,'originalBatch':200,'humanCounts':{'installed':len(ids)+2,'to-do':0,'held-human':0,'held-ai':0,'held-unknown':len(held),'in-process':0},'rows':outcomes,'snapshotId':snapshot,'aiCalls':0,'modelGeometryChanges':0,'terrainPatches':len(read(STAGE/'plan.json')['topLevelTerrainPatches']),'qualification':'Available configured scripted checks completed. Technical holds have measured blockers whose safe resolution path is unproven. No established AI or human-decision requirement; no worker or queued work remains in this bounded pass.'}
    save(DOC/'final-results.json.gz',report)
    held_observation='Scripted resolution pass completed. Safe automatic integration remains unproven for the recorded technical blocker. Human-facing status held-unknown; no AI or human decision requirement established. Existing fallback retained.'
    ledger.record_many(snapshot,receipt_path,[(r['uid'],'held',DOC/'final-results.json.gz',held_observation+' Reasons: '+', '.join(r['reasons']),commit) for r in held],effort={**effort,'output_ref':str((DOC/'final-results.json.gz').relative_to(ROOT))},request_id='government-resolution-held-'+snapshot)
    assert read(pointer)==previous,'Review pointer changed';save(pointer,{'snapshotId':snapshot,'inventory':str(inv.relative_to(ROOT)),'previousSnapshots':[*previous.get('previousSnapshots',[]),previous['snapshotId']],'qualification':previous['qualification']})
    command([sys.executable,str(HERE.parent/'building-progress/export.py'),'--refresh']);command(['node',str(ROOT/'3d-viewer/scripts/build_progress.mjs')])
    job_id=jobs.enqueue('government-198-resolution-20260911','government-resolution-v1',{'decisionSHA256':digest((DOC/'decision.json').read_bytes()),'snapshot':snapshot});job=jobs.claim('government-198-resolution-20260911',receipt['owner'],['government-resolution-v1'],lease_seconds=600);assert job and job['id']==job_id
    evidence={'path':str((DOC/'final-results.json.gz').relative_to(ROOT)),'sha256':digest((DOC/'final-results.json.gz').read_bytes())};result={**report,'evidence':evidence}
    with connect() as c:
        c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));group=reservations._current(c,receipt);assert group and {'building:'+r['uid'] for r in sources}<=set(group['resources'])
        assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),job_id,job['owner'],job['token'])).rowcount==1
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()[0]==result
        actual=dict(c.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,[r['uid'] for r in sources])))
        assert all(actual[r['uid']]==r['state'] for r in outcomes)
    save(DOC/'neon-sync.json',{'jobId':job_id,'verifiedRows':198,'sourceAndJobFenced':True,'exactResultMatch':True,'reviewStatesVerified':True})
    save(DOC/'summary.json',{k:v for k,v in report.items() if k!='rows'}|{'jobId':job_id,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json')})
    print(json.dumps({'newlyInstalled':len(ids),'humanCounts':report['humanCounts'],'neonVerified':True,'snapshot':snapshot}),flush=True)

if __name__=='__main__':main()
