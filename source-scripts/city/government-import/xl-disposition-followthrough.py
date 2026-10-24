"""Close detailed batch-receipt gaps in the all-XL disposition audit.

No model approval: source-specific failed tests are filed, while stale-only
and missing installed-verification cases remain explicitly open.
"""
import uuid
from collections import Counter
from pathlib import Path
from run import ROOT,read,save,digest,connect,reservations,Jsonb,dict_row,jobs
from importlib.util import spec_from_file_location,module_from_spec
DIR=Path(__file__).resolve().parent
spec=spec_from_file_location('xl_disposition_audit',DIR/'xl-disposition-audit.py')
audit=module_from_spec(spec);spec.loader.exec_module(audit)
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-all-source-disposition-20261007'
DOC=BASE/'government-xl-all-source-disposition-followthrough-20261007'

def main():
    assert not DOC.exists()
    report=read(PRIOR/'audit.json.gz')
    sync=read(PRIOR/'neon-sync.json')
    rows=report['rows']
    open_uids=report['openUids']
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        saved=con.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',([r['jobId'] for r in sync['rows']],)).fetchall()
        assert {j:audit.canonical_hash(r) for j,s,r in saved if s=='complete'}=={r['jobId']:r['resultSHA256'] for r in sync['rows']}
        failed=con.execute("SELECT DISTINCT ON(x->>'uid') j.id,j.batch,j.stage,x FROM astra_modelling.jobs j CROSS JOIN LATERAL jsonb_array_elements(CASE WHEN jsonb_typeof(j.result->'rows')='array' THEN j.result->'rows' ELSE '[]'::jsonb END) x WHERE j.status='complete' AND x->>'uid'=ANY(%s) AND jsonb_typeof(x->'reasons')='array' AND jsonb_array_length(x->'reasons')>0 AND (x->>'passed'='false' OR (x->'metrics' IS NOT NULL AND x->'validation' IS NOT NULL)) ORDER BY x->>'uid',j.updated_at DESC",(open_uids,)).fetchall()
        successor=con.execute("SELECT id,result FROM astra_modelling.jobs WHERE batch=%s AND status='complete' LIMIT 1",('government-xl-central-pier8-original-successor-diagnostic-20261007',)).fetchone()
        reconciled=con.execute('SELECT id,result FROM astra_modelling.jobs WHERE id=%s AND status=%s',('eb1fe2913054070285a49b4e67987efe01d537f84f11707aa615f9d53c1ea5e7','complete')).fetchone()
    phases={r[3]['uid']:r for r in failed}
    local_path=BASE/'government-xl-remaining-20260923/held-second-pass/results.json.gz'
    local=read(local_path)
    local_by_uid={r['uid']:r for r in local['rows']}
    changed=[]
    for row in rows:
        if row['disposition']=='filed-cannot-install' and row['reasons']==['stale-inputs-require-full-fresh-recheck']:
            row.update(disposition='open',nextStep='Run a fresh full check on current inputs; a stale-input notice is not a source rejection.',reasons=['stale-inputs-require-full-fresh-recheck'])
            changed.append(row)
            continue
        if row['disposition']!='open' or row['uid'] in ['landsd/184076:0','landsd/1307:0']:
            continue
        phase=phases.get(row['uid'])
        if phase:
            jid,batch,stage,outcome=phase
            if outcome['sourceSHA256']!=row['sourceSHA256']:
                assert row['uid']=='landsd/213352:0'
                s=successor[1]
                assert s['sourceSHA256']==outcome['sourceSHA256']
                assert s['successorOf']['sourceSHA256']==row['sourceSHA256'] and s['successorOf']['modelId']==row['modelId']
                row['testedSuccessor']={'jobId':successor[0],'sourceSHA256':s['sourceSHA256'],'modelId':s['modelId'],'successorOf':s['successorOf']}
            row.update(evidence={'jobId':jid,'batch':batch,'stage':stage,'rowSHA256':audit.canonical_hash(outcome),'row':outcome},reasons=outcome['reasons'])
        elif row['uid'] in ['landsd/134332:0','landsd/258419:0']:
            outcome=local_by_uid[row['uid']]
            assert outcome['sourceSHA256']==row['sourceSHA256'] and outcome['metric']['sourcePreserved']
            assert outcome['metric']['minSurfaceGap'] < -0.5
            assert outcome['metric']['sourceSHA256']==row['sourceSHA256']
            reconciled_row=next(r for r in reconciled[1]['rows'] if r['uid']==row['uid'])
            assert str(local_path.relative_to(ROOT)) in reconciled_row['evidence']
            assert reconciled_row['sourceSHA256']==row['sourceSHA256']
            row.update(evidence={'jobId':reconciled[0],'rowSHA256':audit.canonical_hash(reconciled_row),'row':reconciled_row,'physicalReceipt':{'path':str(local_path.relative_to(ROOT)),'sha256':digest(local_path.read_bytes()),'row':outcome}},reasons=['terrain-intersects-source-over-0.5m',*outcome['reasons']])
        else:
            continue
        row.update(disposition='filed-cannot-install',permanentRejection=False,
                   observation='The exact source (or explicitly linked official successor) has completed source-bound validation failures. Filing preserves the tested contract; it does not establish permanent impossibility.',
                   revisitTrigger='A corrected original source/terrain/component match or verified code correction resolving the recorded failures, followed by all acceptance checks.')
        row['reasonGroup']=audit.reason_group(row['reasons'])
        changed.append(row)
    counts=dict(Counter(r['disposition'] for r in rows))
    report.update(counts=counts,openUids=[r['uid'] for r in rows if r['disposition']=='open'],
                  filedReasonGroups=dict(Counter(r['reasonGroup'] for r in rows if r['disposition']=='filed-cannot-install')),
                  previousAudit={'path':str((PRIOR/'audit.json.gz').relative_to(ROOT)),'sha256':digest((PRIOR/'audit.json.gz').read_bytes())},
                  supersededStaleOnlyFilings=1)
    # Confirm the runtime/review state did not change while reading historical evidence.
    for ref in report['evidenceRefs']:
        if ref['path'].endswith('xl-disposition-audit.py'):continue
        assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    save(DOC/'audit.json.gz',report)
    claim=reservations.claim('codex-xl-disposition-followthrough-'+str(uuid.uuid4()),['building:'+r['uid'] for r in changed],batch=DOC.name)
    assert claim['ok'],claim
    lease=claim['reservation'];written=[]
    try:
        with connect() as con:
            con.row_factory=dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
            assert reservations._current(con,lease)
            for row in changed:
                ev=row['evidence']
                old=con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(ev['jobId'],)).fetchone()
                assert old['status']=='complete'
                if 'row' in ev:
                    assert ev['row'] in old['result']['rows'] and audit.canonical_hash(ev['row'])==ev['rowSHA256']
                else:assert old['result']==ev['result']
                payload={'sourceKey':row['sourceKey'],'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'decisionSHA256':audit.canonical_hash(row)}
                jid=audit.canonical_hash([DOC.name,audit.STAGE,payload])
                is_filed=row['disposition']=='filed-cannot-install'
                result={**row,'state':row['disposition'],'deferred':is_filed,'revisitLater':is_filed,'retainCurrentModel':True,'requiresHumanDecision':False,'requiresAI':None,'batch':DOC.name,'stage':audit.STAGE,'jobId':jid}
                con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s) ON CONFLICT(id) DO NOTHING",(jid,DOC.name,audit.STAGE,Jsonb(payload),Jsonb(result)))
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()=={'status':'complete','result':result}
                written.append({'uid':row['uid'],'jobId':jid,'disposition':row['disposition'],'resultSHA256':audit.canonical_hash(result)})
        with connect() as con:
            got=con.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',([r['jobId'] for r in written],)).fetchall()
        assert {j:audit.canonical_hash(r) for j,s,r in got if s=='complete'}=={r['jobId']:r['resultSHA256'] for r in written}
        save(DOC/'neon-sync.json',{'rows':written,'freshReadbackVerified':True,'priorUnchangedFilingsVerified':len(saved),'counts':counts})
        print({k:report[k] for k in ('models','counts','openUids','filedReasonGroups')})
    finally:assert reservations.release(lease)

if __name__=='__main__':main()
