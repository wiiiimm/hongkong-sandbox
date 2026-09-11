"""Write source-bound, resumable final XXL states to the pinned Neon job ledger."""
from collections import Counter
import importlib.util,json,sys,uuid
from pathlib import Path
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE,DOC,LOCAL=s.ROOT,s.HERE,s.DOC,s.LOCAL
read,save,h,rel=s.read,s.save,s.h,s.rel
STAGE='government-xxl-second-pass-v1'

def start():
    assert (DOC/'saxon-install/summary.json').exists(),'Finish the verified Saxon import first'
    resources=set(read(LOCAL/'reservation.json')['resources'])|set(read(LOCAL/'saxon-install/reservation.json')['resources'])
    claim=s.reservations.claim('codex-xxl-final-'+str(uuid.uuid4()),sorted(resources),batch=s.BATCH+'-final');assert claim['ok'];save(LOCAL/'final-reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'final-reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    receipt=read(LOCAL/'final-reservation.json');assert s.reservations.owns(receipt);original=read(s.BASE/'selection.json.gz');frozen=read(DOC/'selection.json.gz');selected={r['modelId']:r for r in frozen['rows']};diag={r['modelId']:r for r in read(DOC/'diagnostics.json')['rows']};adj=read(DOC/'adjacent-terrain-results.json');assert adj['complete'];native={r['modelId']:r['native'] for r in adj['rows']}
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={}
    for url in manifest['officialModelCatalogues']:
        for e in read(ROOT/'3d-viewer'/url)['models']:
            if e['sha256'] in {r['sourceSHA256'] for r in original['rows']}:
                path=(ROOT/'3d-viewer'/url).parent/e['asset'];assert h(path)==e['sha256'];installed[e['sha256']]={'entry':e,'asset':rel(path),'catalogue':url,'catalogueSHA256':h(ROOT/'3d-viewer'/url)}
    pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
    with s.connect() as c:
        c.execute('SET TRANSACTION READ ONLY');reviews=dict(c.execute('SELECT uid,jsonb_build_object(\'state\',review_state,\'sha256\',source_sha256,\'result\',result) FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(pointer['snapshotId'],[v['entry']['uid'] for v in installed.values()])));current=dict(c.execute('SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=ANY(%s)',([r['native']['cacheKey'] for r in original['rows']],)))
    assert all(current[r['native']['cacheKey']]==r['native']['resultSha'] for r in original['rows'])
    rows=[]
    for r in original['rows']:
        mid=r['modelId'];proof=installed.get(r['sourceSHA256']);d=diag.get(mid);row={'modelId':mid,'nativeCacheKey':r['native']['cacheKey'],'nativeResultSHA256':r['native']['resultSha'],'sourceSHA256':r['sourceSHA256'],'uid':r['uid'],'name':r['name'],'humanStatus':'held-unknown','aiCalls':0,'state':'held-for-second-pass','reasons':[],'nextDependency':'unproven engineering/source resolution'}
        if proof:
            e=proof['entry'];review=reviews[e['uid']];assert e['modelId']==mid and review['state']=='installed-verified' and review['sha256']==e['sha256']
            row.update(uid=e['uid'],name=e.get('label') or row['name'],humanStatus='installed',state='installed-verified',installedProof=proof,review=review,nextDependency=None,nextStep=None)
            if not r['uid']:row['classificationCorrection']='Already installed under explicit resolved identity; native matcher UID was absent'
            if e['uid']=='landsd/76364:0':row['newlyInstalledThisPass']=True
        else:
            n=native.get(mid,d['native']);row.update(diagnostics=d,nativeTerrain=n,reasons=list(n.get('reasons',[])))
            if 'strict-identity-fit' in r['reasons'] or not r['uid']:row['reasons'].append('source-component-identity-outside-automatic-contract')
            row['nextStep']='Resolve the recorded source/component or native terrain evidence; preserve the current fallback. No automatic AI work.'
            if r['uid']=='landsd/160070:0':row.update(humanStatus='held-ai',nextDependency='architectural component review; execution authorization pending',nextStep='Proposed one GPT-5.6 Sol review of the source/footprint component mismatch; no geometry edits. Evidence packet is prepared. AI has not started.',aiProposal=read(DOC/'sol-review-proposal/packet.json'))
            elif r['uid']=='landsd/273061:0':row.update(reasons=['current-elements-neighbour-support-unresolved'],existingApproval=read(DOC/'elements/existing-approval.json'),restoration=read(DOC/'elements/restoration.json'),neighbourChecks=read(DOC/'elements/neighbour-checks.json'),supportDiagnostics=read(DOC/'elements/neighbour-support-triangles.json'),nextStep='Preserve prior exact source approval and restored terrain; resolve current neighbour/assembly support before publishing. Seventeen of 38 flagged forms have complete vertex support diagnostics; these are not acceptance.')
            elif r['uid']=='landsd/109467:0':row.update(reasons=['native-terrain-overlapping-height-surfaces'],terrainAttempt=read(DOC/'terrain/result.json'),nextStep='Resolve and verify original overlapping terrain surfaces without moving building geometry.')
        rows.append(row)
    counts={k:sum(r['humanStatus']==k for r in rows) for k in ['installed','to-do','held-human','held-ai','held-unknown','in-process']};assert len(rows)==22 and counts['installed']==6 and counts['in-process']==0
    evidence_paths=[DOC/'diagnostics.json',DOC/'adjacent-terrain-results.json',DOC/'recovery.json',DOC/'metrics.json',DOC/'saxon-support-triangles.json',DOC/'saxon-install/installed-acceptance.json',DOC/'elements/restoration.json',DOC/'elements/neighbour-support-triangles.json',DOC/'terrain/result.json',DOC/'sol-review-proposal/packet.json']
    outputs={rel(p):h(p) for p in evidence_paths};payload={'selectionSHA256':h(DOC/'selection.json.gz'),'snapshot':pointer['snapshotId'],'evidenceHashes':outputs};jobid=s.jobs.enqueue(s.BATCH,STAGE,payload);job=s.jobs.claim(s.BATCH,receipt['owner'],[STAGE],lease_seconds=600);assert job and job['id']==jobid
    report={'batch':s.BATCH,'parentBatch':'government-xxl-20260911','stage':STAGE,'jobId':jobid,'models':22,'humanCounts':counts,'newXXLInstalledThisPass':1,'correctedExistingInstalled':1,'additionalInstalledSupportUids':['landsd/232025:0'],'rows':rows,'evidenceHashes':outputs,'sourceSheets':39,'originalAssetsChecked':18,'snapshot':pointer['snapshotId'],'aiCalls':0,'aiReviewProposalStatus':'not-started; awaiting explicit authorization','modelGeometryChanges':0,'progress':read(ROOT/'3d-viewer/city/data/building-progress.json'),'qualification':'All configured second-pass checks completed. One bounded AI component review is proposed; remaining technical holds require unproven source/engineering resolution, not a demonstrated AI-remodelling need.'}
    save(DOC/'final-results.json.gz',report);report['evidence']={'path':rel(DOC/'final-results.json.gz'),'sha256':h(DOC/'final-results.json.gz')}
    with s.connect() as c:
        c.row_factory=s.dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(s.reservations.LOCK_ID,));group=s.reservations._current(c,receipt);assert group and set(receipt['resources'])<=set(group['resources'])
        assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(s.Jsonb(report),jobid,job['owner'],job['token'])).rowcount==1
    with s.connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==report
    save(DOC/'final-summary.json',{k:v for k,v in report.items() if k!='rows'});save(DOC/'neon-sync.json',{'jobId':jobid,'rows':22,'exactResultMatch':True,'sourceAndJobFenced':True,'existingReviewStatesPreserved':True});print(json.dumps({'humanCounts':counts,'jobId':jobid,'aiCalls':0}),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
