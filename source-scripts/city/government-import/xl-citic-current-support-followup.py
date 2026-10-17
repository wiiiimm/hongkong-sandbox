"""File exact CITIC current-support evidence without changing reviews or assets."""
from pathlib import Path
import uuid
from run import ROOT,HERE,read,save,digest,connect,jobs,reservations,Jsonb,dict_row,NATIVE_RUN
BATCH='government-xl-citic-current-support-followup-20261008'
UID='landsd/278303:0';SUPPORT='landsd/232579:0'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}

def main():
    assert not DOC.exists()
    old=next(r for r in read(BASE/'government-xl-held-second-pass-dispositions-20261008/dispositions.json.gz')['rows'] if r['uid']==UID)
    tower=BASE/'government-xl-citic-current-installed-support-20261008'
    podium=BASE/'government-xl-citic-podium-current-disposition-20261008'
    assembly=BASE/'government-xl-citic-complete-original-assembly-20261008'
    p=read(podium/'result.json');a=read(assembly/'result.json')
    assert a['sourceSHA256s'][UID]==old['sourceSHA256'] and not a['identityPassed']
    assert a['reasons']==['compound-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2']
    assert a['measures']['sourceExcessCoveredByUnrelatedFormsM2']>1
    assert read(tower/'owned-source-identity.json')['passed']
    assert read(tower/'validation.json')['checksPassed']==1
    assert all(not r['reasons'] and r['maxGroundChange']==0 for r in read(tower/'neighbour-checks.json')['rows'])
    assert not read(tower/'native-neighbour-checks.json')['blocked']
    body=p['rows'][0];assert body['uid']==SUPPORT and body['strictFoundationAccepted'] and body['reasons']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for folder,result in [(podium,p),(assembly,a)]:
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
            for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
        assert con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=ANY(%s) LIMIT 1',([UID,SUPPORT],)).fetchone() is None
        assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,old['nativeCacheKey'])).fetchone()==(old['nativeResultSHA256'],)
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    matches=[(m,ROOT/'3d-viewer'/u) for u in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models'] if m['uid']==SUPPORT]
    assert len(matches)==1;entry,cat=matches[0]
    assert not entry.get('publicationApproved') and not entry.get('sourceIdentityReviewed')
    assert digest((cat.parent/entry['asset']).read_bytes())==entry['sha256']==a['sourceSHA256s'][SUPPORT]
    save(DOC/'current-support.json',{'uid':SUPPORT,'catalogue':ref(cat),'entry':entry,'noInstalledVerification':True,'publication':False})
    refs=[ref(Path(__file__)),ref(BASE/'government-xl-held-second-pass-dispositions-20261008/dispositions.json.gz'),ref(DOC/'current-support.json')]
    for folder in [tower,podium,assembly]:refs.extend(ref(p) for p in sorted(folder.iterdir()) if p.is_file() and p.name!='README.md')
    claim=reservations.claim('codex-citic-followup-'+str(uuid.uuid4()),['building:'+UID,'building:'+SUPPORT],batch=BATCH);assert claim['ok'],claim
    lease=claim['reservation']
    try:
        payload={'uid':UID,'sourceKey':old['sourceKey'],'sourceSHA256':old['sourceSHA256'],'evidenceRefs':refs,'previousDispositionJobId':old['jobId']}
        stage='citic-current-original-support-followup-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':BATCH,'reasons':['support-not-installed-verified:'+SUPPORT,*a['reasons']],
            'previousReasons':old['reasons'],'completedCurrentTowerChecks':['full-original-identity','runtime-loader','seven-clear-basic-neighbours','native-neighbours'],
            'towerFoundationCompleted':False,'supportPodiumFoundationPassed':True,'completeOriginalAssemblyIdentity':a['measures'],
            'supportPhysicalJobId':p['jobId'],'assemblyIdentityJobId':a['jobId'],
            'humanStatus':'held-unknown','state':'held-for-second-pass','retainCurrentModel':True,'revisitLater':True,'permanentRejection':False,
            'needsAIProcessing':None,'needsComputeProcessing':None,'needsHumanDecision':False,
            'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'activeWorkers':0,'queuedFollowups':0,
            'nextStep':'Changed authoritative component/footprint evidence resolving the 16.096964m2 unrelated overlap, then full support verification and fresh complete tower acceptance. Reuse completed source/contact checks; no identity or physical waiver.',
            'qualification':'Older trial support is visible but unverified. Current tower neighbours are clear without terrain replacement; the support/complete-assembly identity still blocks acceptance. No corruption, permanent impossibility or AI necessity is established.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for e in refs:assert ref(ROOT/e['path'])==e
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print({'uid':UID,'jobId':jid,'neonVerified':True,'reasons':result['reasons']})
    finally:assert reservations.release(lease)
if __name__=='__main__':main()
