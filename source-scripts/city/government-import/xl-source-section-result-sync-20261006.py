"""Recover the finished section evidence after a result-sync row-factory error.

The original process is confirmed terminal and its source lease released. Reuse
its exact queued payload hashes under new source ownership; do not rerun meshes.
"""
import importlib.util
import json
import subprocess
import sys
import uuid
from collections import Counter
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row,NATIVE_RUN

BATCH='government-xl-source-sections-196-sync-20261006'
PREVIOUS='government-xl-source-sections-196-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH


def module():
    spec=importlib.util.spec_from_file_location('original_section_stage',HERE/'xl-source-section-diagnostic-20261006.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    prior=read(HERE/'local'/PREVIOUS/'reservation.json')
    assert not reservations.owns(prior),'Previous source worker still owns sources'
    original=module();checkpoint,held,sources,contexts,_=original.inputs()
    with connect() as con:
        con.row_factory=dict_row;con.execute('SET TRANSACTION READ ONLY')
        pending=con.execute('SELECT * FROM astra_modelling.jobs WHERE batch=%s',(PREVIOUS,)).fetchall()
    assert len(pending)==1
    old=pending[0];assert old['status']=='running' and old['owner']==prior['owner']
    payload=old['payload'];assert payload['runnerSHA256']==digest((HERE/'xl-source-section-diagnostic-20261006.py').read_bytes())
    assert payload['algorithmSHA256']==digest((HERE/'source_sections.py').read_bytes())
    for ref in payload['evidenceRefs']:
        assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    old_doc=ROOT/'docs/astra-city/government-import'/PREVIOUS
    rows=[read(old_doc/(uid.split('/')[1].replace(':','-')+'.json.gz')) for uid in sources]
    assert len(rows)==196 and {r['uid'] for r in rows}==set(held)
    for r in rows:
        source=sources[r['uid']]
        assert r['sourceSHA256']==source['sourceSHA256']==digest((ROOT/source['candidate']['path']).read_bytes())
        assert r['nativeResultSHA256']==source['native']['resultSha']
        assert r['previousFullProjection']==contexts[r['uid']]['identity']
        assert not r['publication'] and r['modelGeometryChanges']==0
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');original.verify_native(con,sources)
    assert jobs.finish(old,error='Result-sync native verification used dict_row with tuple conversion; process terminal, all 196 immutable evidence rows recovered by '+BATCH)
    save(DOC/'recovered-attempt.json',{'previousJobId':old['id'],'previousSourceOwner':prior['owner'],
        'previousSourceToken':prior['token'],'previousSourceReservationReleased':True,
        'previousPayload':payload,'completedSourceRows':196,'qualification':'Original process exited 1 after all mesh diagnostics, at the result sync fence. No source computation or acceptance repeated.'})
    refs=payload['evidenceRefs']+[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
                                 for p in [Path(__file__),DOC/'recovered-attempt.json']]
    new_payload={'evidenceRefs':refs,'previousAttempt':old['id'],'sourceCheckpoint':checkpoint['jobId'],
                 'runnerSHA256':digest(Path(__file__).read_bytes())}
    stage='verified-original-source-section-result-recovery-v1';jobid=jobs.enqueue(BATCH,stage,new_payload)
    job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
    result={**new_payload,'batch':BATCH,'jobId':jobid,'rows':rows,'sourcesChecked':196,
        'diagnosticGroups':dict(Counter(r['diagnosticGroup'] for r in rows)),
        'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'activeWorkers':0,'queuedFollowups':0,'widerXLInstalled':50,'widerXLHeld':302,
        'qualification':'Recovered exact section evidence only; full source-fit, support and all installation gates remain required. The 100-installation goal remains incomplete.'}
    for ref in refs:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    with connect() as con:
        # Keep tuple rows during native verification, then enable named rows
        # for the existing source-ownership fence.
        con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        original.verify_native(con,sources);con.row_factory=dict_row
        assert reservations._current(con,lease)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True,'sourceRowsRecoveredWithoutRerun':196})
    print(json.dumps({'jobId':jobid,'groups':result['diagnosticGroups'],'newlyInstalled':0,'neonVerified':True}),flush=True)


def start():
    assert not DOC.exists(),'Completed recovery is immutable'
    _,held,_,_,_=module().inputs()
    claim=reservations.claim('codex-xl-section-sync-'+str(uuid.uuid4()),['building:'+u for u in held],batch=BATCH)
    assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)


if __name__=='__main__':(owned if sys.argv[1:]==['owned'] else start)()
