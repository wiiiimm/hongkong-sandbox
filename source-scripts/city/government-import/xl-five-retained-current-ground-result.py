"""Fenced physical-result recorder for five exact original sources blocked by retained terrain construction.

This compatibility entry point records current-terrain preflight evidence only;
it builds no terrain, changes no model reviews and grants no installation credit.
"""
import json
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row, NATIVE_RUN

SCOPED_UIDS=frozenset({'landsd/255415:0','landsd/88343:0','landsd/89613:0','landsd/11093:0','landsd/264206:0'})


def finish(args, row, doc, local, reasons):
    assert row['uid']==args.uid and args.uid in SCOPED_UIDS
    assert row['currentReview'] is None
    receipt=read(local/'reservation.json');assert reservations.owns(receipt)
    assert read(doc/'terrain-candidates.json')==[]
    assert read(doc/'terrain.json')['terrainGeometryChanges']==0
    assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
    refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
          for p in sorted(doc.iterdir()) if p.is_file() and p.name not in ('result.json','neon-sync.json','README.md')]
    refs.append({'path':str(Path(__file__).relative_to(ROOT)),'sha256':digest(Path(__file__).read_bytes())})
    payload={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'evidenceRefs':refs,
             'runnerSHA256':digest(Path(__file__).read_bytes())}
    stage='five-retained-full-cell-original-current-ground-physical-v1'
    jobid=jobs.enqueue(args.batch,stage,payload)
    job=jobs.claim(args.batch,receipt['owner'],[stage],lease_seconds=1800)
    assert job and job['id']==jobid
    result={**payload,'jobId':jobid,'batch':args.batch,'reasons':sorted(set(reasons)),
        'humanStatus':'held-compute' if reasons else 'in-process','scriptChecksPassed':not reasons,
        'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'requiresAI':False,'requiresHumanDecision':False,'activeWorkers':0,'queuedFollowups':0,
        'nextStep':'Resolve recorded physical blockers using original sources.' if reasons else 'Complete staged/live browser checks and guarded installed publication.'}
    with connect() as con:
        con.row_factory=dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        assert reservations._current(con,receipt)
        assert con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=%s LIMIT 1',(row['uid'],)).fetchone() is None
        actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()
        assert actual and actual['result_sha']==row['native']['resultSha']
        for ref in refs:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',result)
    save(doc/'result.json',result)
    save(doc/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
    print(json.dumps({'uid':row['uid'],'checksPassed':not reasons,'reasons':result['reasons'],'jobId':jobid,'neonVerified':True}),flush=True)
