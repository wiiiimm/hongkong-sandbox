"""Finish the audit after verified per-source writes, without repeating checks."""
import uuid
from collections import Counter
from pathlib import Path
from run import ROOT, read, save, digest, connect, jobs, reservations, Jsonb, dict_row, NATIVE_RUN

BATCH = 'government-xl-held-second-pass-dispositions-20261008'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
def canonical(value): return digest(jobs.encode(value).encode())
def ref(path): return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

def main():
    assert not (DOC/'result.json').exists()
    report = read(DOC/'dispositions.json.gz'); rows = report['rows']
    assert len(rows) == 331 and len({r['sourceKey'] for r in rows}) == 331
    assert sum(r['installed'] for r in rows) == 4
    resources = ['native-model:'+r['sourceKey'] for r in rows] + ['xl-disposition-inventory:'+NATIVE_RUN]
    resources += ['building:'+u for u in sorted({r['uid'] for r in rows if r['uid']})]
    claim = reservations.claim('codex-xl-held-audit-finalize-'+str(uuid.uuid4()),resources,ttl=3600,batch=BATCH)
    assert claim['ok'],claim
    lease=claim['reservation']
    try:
        for evidence in report['evidenceRefs']: assert ref(ROOT/evidence['path'])==evidence
        with connect() as con:
            got=con.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',([r['jobId'] for r in rows],)).fetchall()
        assert {j:canonical(r) for j,s,r in got if s=='complete'}=={r['jobId']:canonical(r) for r in rows}
        display_group=lambda r: 'runtime-footprint-fit' if r['reasons']==['runtime-original-footprint-fit-failed'] else r['reasonGroup']
        stage='all-xl-explicit-held-second-pass-audit-v1'
        payload={'nativeRun':NATIVE_RUN,'scope':331,'report':ref(DOC/'dispositions.json.gz'),'finalizer':ref(Path(__file__).resolve())}
        jid=canonical([BATCH,stage,payload])
        result={k:v for k,v in report.items() if k not in ['rows','evidenceRefs']}
        result.update(jobId=jid,batch=BATCH,stage=stage,report=payload['report'],finalizer=payload['finalizer'],
            heldReasonGroups=dict(Counter(display_group(r) for r in rows if not r['installed'])),
            perSourceReadbackVerified=True,
            qualification=report['qualification']+' Runtime footprint-fit failures are displayed separately from runtime performance budgets; original receipt fields remain immutable.')
        with connect() as con:
            con.row_factory=dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s) ON CONFLICT(id) DO NOTHING",
                (jid,BATCH,stage,Jsonb(payload),Jsonb(result)))
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()=={'status':'complete','result':result}
        with connect() as con:assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'freshReadbackVerified':True,'sourceDispositionsVerified':331})
        print(result,flush=True)
    finally:assert reservations.release(lease)

if __name__=='__main__':main()
