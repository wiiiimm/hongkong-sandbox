"""Freeze full original support proof and raw diagnostics, no install credit."""
import json
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BATCH='government-xl-hoi-yu-attached-support-proof-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
    assert not (DOC/'result.json').exists()
    proof=read(DOC/'proof.json');assert proof['supportInterfaceAccepted'] and not proof['fullAcceptance']
    refs=[*proof['evidenceRefs'],ref(DOC/'proof.json'),ref(Path(__file__))]
    for batch in ['government-xl-hoi-yu-component-interfaces-20261009','government-xl-hoi-yu-exact-component-attachment-20261009','government-xl-hoi-yu-positive-contact-attachment-20261009']:
        refs += [ref(p) for p in sorted((ROOT/'docs/astra-city/government-import'/batch).glob('*')) if p.is_file()]
    refs += [ref(HERE/p) for p in ['hoi-yu-component-interfaces-20261009.mjs','xl-hoi-yu-exact-component-attachment-20261009.py','xl-hoi-yu-positive-contact-attachment-20261009.py']]
    refs=list({r['path']:r for r in refs}.values())
    claim=reservations.claim('hoi-yu-support-checkpoint-'+str(uuid.uuid4()),['building:landsd/177604:0','building:landsd/177605:0'],batch=BATCH,ttl=1800)
    assert claim['ok'],claim;lease=claim['reservation']
    try:
        stage='complete-original-attached-component-support-v1'
        payload={'uids':[proof['supportUid'],proof['uid']],'sourceSHA256':proof['sourceSHA256'],'evidenceRefs':refs}
        jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'proof':proof,
            'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'aiGeometryModelling':False,
            'supportInterfaceAccepted':True,'fullAcceptance':False,
            'nextStep':'Independently accept current grounded original podium and full physical/browser/publication gates. Legacy global-bottom failures retained; all source components preserved.'}
        with connect() as c:
            c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'jobId':jid,'supportAccepted':True,'neonVerified':True}),flush=True)
    finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
