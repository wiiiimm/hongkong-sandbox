"""Freeze and fence a ten-form AI evidence review; source meshes remain unchanged."""
import json,uuid,sys,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BASE=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC=BASE/'sol-pilot-20261002'
LEASE=HERE/'local/sol-pilot-20261002/reservation.json'
UIDS=['landsd/91827:0','landsd/104302:0','landsd/255917:0','landsd/255647:0','landsd/255539:0','landsd/264206:0','landsd/336430:0','landsd/273672:0','landsd/134332:0','landsd/273839:0']
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def prepare():
    if (DOC/'packet.json').exists():
        packet=read(DOC/'packet.json');assert packet['uids']==UIDS
        for item in packet['inputRefs']:
            assert digest((ROOT/item['path']).read_bytes())==item['sha256'],item['path']
        print({'packet':ref(DOC/'packet.json'),'reused':True});return
    if LEASE.exists() and reservations.owns(read(LEASE)):
        reservations.heartbeat(read(LEASE))
    else:
        claim=reservations.claim('codex-sol-pilot-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch='sol-pilot-20261002')
        assert claim['ok'],claim
        save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    original={r['uid']:r for r in read(BASE/'reconciliation.json.gz')['rows']}
    context={r['uid']:r for p in [BASE/'context.json',BASE/'context-held.json'] for r in read(p)['rows']}
    for name in ('http-retry-check-20260924/results.json.gz','revision-check-20260924/results.json.gz'):
        for row in read(BASE/name)['rows']:
            context.setdefault(row['uid'],row)
    cached=read(BASE/'cached-terrain-foundations-20260929.json')['rows']
    rows=[]
    for uid in UIDS:
        row=original[uid];assert row['humanStatus']!='installed'
        rows.append({'uid':uid,'name':row['name'],'sourceSHA256':row['sourceSHA256'],'priorState':row,'identity':context[uid]['identity'],
            'cachedFoundation':[{k:v for k,v in r.items() if k not in ('foundation',)}|{'foundation':{k:v for k,v in r.get('foundation',{}).items() if k!='components'}} for r in cached if r['uid']==uid]})
    packet={'batch':'sol-pilot-20261002','uids':UIDS,'rows':rows,'reviewScope':'AI evidence interpretation, component/support routing and reusable code improvements; no geometry generation, geometry edits or installation approval.',
        'requestedModel':'gpt-6.1-sol','requestedReasoningEffort':'high','executor':'Codex root','actualTokenUsage':None,
        'inputRefs':[ref(BASE/n) for n in ('reconciliation.json.gz','context.json','context-held.json','cached-terrain-foundations-20260929.json','http-retry-check-20260924/results.json.gz','revision-check-20260924/results.json.gz')]}
    save(DOC/'packet.json',packet)
    for r in rows:print(json.dumps({'uid':r['uid'],'name':r['name'],'identity':r['identity'],'foundations':r['cachedFoundation']}))
def sync():
    report=read(DOC/'review.json');assert {r['uid'] for r in report['rows']}==set(UIDS)
    for item in report['evidenceRefs']:
        assert digest((ROOT/item['path']).read_bytes())==item['sha256'],item['path']
    if (DOC/'neon-sync.json').exists():
        previous=read(DOC/'neon-sync.json')
        assert previous['review']==ref(DOC/'review.json')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(previous['jobId'],)).fetchone()[0]==report
        print({'jobId':previous['jobId'],'verified':True,'reused':True});return
    receipt=read(LEASE);assert reservations.owns(receipt)
    reservations.heartbeat(receipt)
    stage='sol-evidence-review-v1';job_id=jobs.enqueue('sol-pilot-20261002',stage,{'review':ref(DOC/'review.json')})
    with connect() as c:
        c.row_factory=dict_row;c.execute('SET TRANSACTION READ ONLY')
        existing=c.execute('SELECT * FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()
    if existing and existing['status']=='complete':
        assert existing['result']==report
        save(DOC/'neon-sync.json',{'jobId':job_id,'resultVerified':True,'review':ref(DOC/'review.json')})
        reservations.release(receipt);print({'jobId':job_id,'verified':True,'reused':True});return
    if existing and existing['status']=='running' and existing['owner']==receipt['owner']:
        job=existing;assert jobs.heartbeat(job,lease_seconds=1800)
    else:
        job=jobs.claim('sol-pilot-20261002',receipt['owner'],[stage],lease_seconds=1800)
    assert job and job['id']==job_id
    # These forms are primarily tracked in the import job ledger. Mirror only
    # exact existing members of the current architectural review snapshot;
    # do not manufacture new preflight membership or overwrite source plans.
    snapshot=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        sources=dict(c.execute('SELECT uid,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,UIDS)).fetchall())
    by_uid={r['uid']:r for r in report['rows']}
    assert all(by_uid[uid]['sourceSHA256']==sha for uid,sha in sources.items())
    if sources:
        spec=importlib.util.spec_from_file_location('pilot_review_ledger',HERE.parent/'model-review-ledger/ledger.py')
        ledger=importlib.util.module_from_spec(spec);spec.loader.exec_module(ledger)
        effort={'method':'scripted','ai_model':'gpt-6.1-sol','reasoning_effort':'high','job_id':job_id,'issue':'HKS-203','output_ref':str((DOC/'review.json').relative_to(ROOT))}
        recorded=ledger.record_many(snapshot,LEASE,[(uid,'held',DOC/'review.json',by_uid[uid]['observation']+' '+by_uid[uid]['nextWork'],None) for uid in sources],effort=effort,request_id='sol-pilot-20261002-'+job_id)
        save(DOC/'ledger-sync.json',{'snapshotId':snapshot,'rows':recorded,'notPlannedHere':sorted(set(UIDS)-set(sources)),'qualification':'All ten reviews are retained in the append-only import job. Existing review-snapshot membership is unchanged.'})
    with connect() as c:
        c.row_factory=dict_row
        c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,receipt)
        assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(report),job_id,job['owner'],job['token'])).rowcount==1
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()[0]==report
    save(DOC/'neon-sync.json',{'jobId':job_id,'resultVerified':True,'review':ref(DOC/'review.json')})
    reservations.release(receipt);print({'jobId':job_id,'verified':True})
if __name__=='__main__':sync() if len(sys.argv)>1 and sys.argv[1]=='sync' else prepare()
