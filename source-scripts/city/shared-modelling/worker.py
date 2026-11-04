"""Run supported audit/candidate adapters through the shared queue, without local SQLite."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import threading
import uuid
from db import connect, CONFIG
from jobs import enqueue, claim, heartbeat, finish, report
from inventory_sync import lookup_row

HERE = Path(__file__).resolve().parent


def source_record(con, snapshot, table, key):
    raw = lookup_row(con, snapshot, table, key)
    if raw is None:
        return None
    metadata = con.execute('''SELECT metadata_json FROM astra_modelling.inventory_tables
        WHERE snapshot_id=%s AND table_name=%s''',(snapshot,table)).fetchone()
    info=json.loads(metadata[0])
    columns=([info['rowid_alias']] if info['rowid_alias'] else [])+info['columns']
    return dict(zip(columns,raw))


def plan_audit(snapshot, batch, uids):
    # Freeze each input in the job. Source changes produce a new ID and cannot rewrite a running job.
    payloads=[]
    with connect() as con:
        for uid in uids:
            building=source_record(con,snapshot,'buildings',{'primary_key':[['uid',uid]]})
            if not building:
                raise ValueError('Building absent from requested snapshot: '+uid)
            model=source_record(con,snapshot,'models',{'primary_key':[['uid',uid]]})
            payloads.append({'snapshot':snapshot,'building':building,
                             'model':json.loads(model['metadata_json']) if model else None})
    ids=[enqueue(batch,'audit-input-v1',p) for p in payloads]
    return {'batch':batch,'jobs':len(set(ids)),'snapshot':snapshot}



def plan_models(snapshot, batch, selection, job_ids):
    from model_adapter import code_hashes
    payloads=[]
    with connect() as con:
        for job_id in job_ids:
            membership=source_record(con,snapshot,'batch_job_sets',{'primary_key':[['name',selection],['id',job_id]]})
            job=source_record(con,snapshot,'batch_jobs',{'primary_key':[['id',job_id]]})
            if not membership or not job or job['stage']!='cached-model-v1':
                raise ValueError('Requested source job is not a model job in the selected current set')
            payloads.append({'snapshot':snapshot,'sourceJobId':job_id,'sourceSelection':selection,
                             'adapterPayload':json.loads(job['payload']),'adapterCode':code_hashes(HERE.parents[2])})
    ids=[enqueue(batch,'cached-model-r2-v1',payload) for payload in payloads]
    return {'batch':batch,'jobs':len(set(ids)),'snapshot':snapshot,'sourceSelection':selection}


def audit_input(payload):
    # Reuse the existing pure adapter, not its local SQLite queue or planner.
    import sys
    source=HERE.parent/'building-batch'
    if str(source) not in sys.path:sys.path.insert(0,str(source))
    from runner import audit_input as adapter
    return adapter(payload)


def run(batch, workers=2, limit=10000, model_store=None):
    if not 1<=workers<=8 or limit<1:
        raise ValueError('Workers must be 1–8 and limit positive')
    stages=['audit-input-v1']+(['cached-model-r2-v1'] if model_store is not None else [])
    remaining=limit
    lock=threading.Lock()
    errors=[]
    def worker():
        nonlocal remaining
        owner=str(uuid.uuid4())
        while True:
            with lock:
                if remaining<=0:return
                remaining-=1
            job=claim(batch,owner,stages)
            if not job:return
            stop=threading.Event()
            lost=threading.Event()
            def pulse():
                while not stop.wait(15):
                    try:
                        if not heartbeat(job):
                            lost.set();return
                    except Exception:
                        lost.set();return
            thread=threading.Thread(target=pulse,daemon=True)
            thread.start()
            try:
                if job['stage']=='cached-model-r2-v1':
                    from model_adapter import process
                    result=process(job['payload'],HERE.parents[2],model_store)
                else:
                    result=audit_input(job['payload'])
                if lost.is_set() or not finish(job,result=result):
                    with lock:errors.append('Lease lost before result acceptance: '+job['id'])
            except Exception as exc:
                # Do not persist exception text; external adapters may include credentials in errors.
                with lock:errors.append('Adapter failed: '+type(exc).__name__)
                if not finish(job,error=type(exc).__name__):
                    with lock:errors.append('Lease lost while recording failure: '+job['id'])
            finally:
                stop.set();thread.join()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(lambda _:worker(),range(workers)))
    result=report(batch)
    result.update(branch=CONFIG['branch_name'],workerErrors=errors,
                  scope='Metadata audit or source-preserving candidate preparation only. No architectural acceptance or publication.')
    if errors:raise RuntimeError('Worker failed or lost lease; inspect shared queue')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['plan-audit','plan-model','run','report'])
    p.add_argument('--batch',required=True)
    p.add_argument('--snapshot')
    p.add_argument('--uid',action='append',default=[])
    p.add_argument('--job-id',action='append',default=[])
    p.add_argument('--selection')
    p.add_argument('--enable-models',action='store_true')
    p.add_argument('--r2-env',type=Path)
    p.add_argument('--workers',type=int,default=2)
    p.add_argument('--limit',type=int,default=10000)
    a=p.parse_args()
    if a.command=='plan-audit':
        if not a.snapshot or not a.uid:p.error('plan-audit requires --snapshot and --uid')
        result=plan_audit(a.snapshot,a.batch,a.uid)
    elif a.command=='plan-model':
        if not a.snapshot or not a.selection or not a.job_id:p.error('plan-model requires --snapshot, --selection and --job-id')
        result=plan_models(a.snapshot,a.batch,a.selection,a.job_id)
    else:
        store=None
        if a.enable_models:
            import os,sys
            from dotenv import dotenv_values
            if a.r2_env:
                for key,value in dotenv_values(a.r2_env).items():
                    if key.startswith('R2_') and value:os.environ.setdefault(key,value)
            sys.path.insert(0,str(HERE.parent/'landmark-resume'))
            from r2_snapshot import R2Store
            store=R2Store('hk-sandbox-assets')
        result=run(a.batch,a.workers,a.limit,model_store=store) if a.command=='run' else report(a.batch)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
