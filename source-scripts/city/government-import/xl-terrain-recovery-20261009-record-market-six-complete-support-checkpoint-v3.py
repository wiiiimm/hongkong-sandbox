"""Fence immutable completed acquisition/identity receipts; no actor state mutation."""
import json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row,NATIVE_RUN
BATCH='xl-terrain-recovery-20261009-market-six-complete-support-checkpoint-v3'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
DIAGNOSTIC=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-complete-support-accounting-v3/diagnostic.json.gz'
SELECTION=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-original-physical-v5-20261009/selection.json.gz'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
    assert not DOC.exists();d=read(DIAGNOSTIC);sources=read(SELECTION)
    assert len(sources['rows'])==6 and d['completeOriginalFaces']==40100 and d['completeOriginalComponentCount']==84
    assert d['manifestSHA256']==sources['manifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
    old_lease_path=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-complete-support-accounting-v3/reservation.json'
    assert {'building:'+r['uid'] for r in sources['rows']}<=set(read(old_lease_path)['resources'])
    refs=d['evidenceRefs']+[ref(p) for p in [DIAGNOSTIC,SELECTION,old_lease_path,Path(__file__)]]
    refs=list({r['path']:r for r in refs}.values())
    claim=reservations.claim('codex-market-support-proof-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH);assert claim['ok'],claim
    lease=json.loads(json.dumps(claim['reservation'],default=str));save(DOC/'reservation.json',lease)
    stage='complete-original-multi-actor-ground-rooted-support-diagnostic-v1'
    payload={'uids':[r['uid'] for r in sources['rows']],'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':BATCH,'supportAccountingAccepted':d['supportAccountingAccepted'],'completeOriginalFaces':40100,'completeOriginalComponentCount':84,'resolvedOriginalComponents':d['resolvedOriginalComponents'],'rawExactGraphReasonsRetained':d['strictGroundRootedOriginalContactGraph']['reasons'],'exactOriginalContacts':len(d['strictGroundRootedOriginalContactGraph']['exactOriginalContacts']),'strictGroundAnchorComponents':d['strictGroundRootedOriginalContactGraph']['genuineGroundAnchorComponents'],'modelGeometryChanges':0,'newlyInstalled':0,'installationApproved':False,'publication':False,'requiresAI':False,'requiresHumanDecision':False,'needsComputeProcessing':True,'qualification':'Complete immutable source-support topology diagnosis. All84 components and40100 original faces remain;82 components exactly ground-rooted;one original exactzeroarea primitive andthree original full±.1band underdeckfacets completely accounted. Full independent physical/source/foreign/browser/publication checks remain mandatory.'}
    try:
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            for row in sources['rows']:
                actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone();assert actual and actual['result_sha']==row['native']['resultSha']
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'supportAccountingAccepted':result['supportAccountingAccepted'],'resolved':len(result['resolvedOriginalComponents']),'resultVerified':True}),flush=True)
    finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
