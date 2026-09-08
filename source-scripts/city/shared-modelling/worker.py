"""Run supported read-only adapters through the shared queue, without local SQLite."""
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


def audit_input(payload):
    # Reuse the existing pure adapter, not its local SQLite queue or planner.
    import sys
    source=HERE.parent/'building-batch'
    if str(source) not in sys.path:sys.path.insert(0,str(source))
    from runner import audit_input as adapter
    return adapter(payload)


def run(batch, workers=2, limit=10000):
    if not 1<=workers<=8 or limit<1:
        raise ValueError('Workers must be 1–8 and limit positive')
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
            job=claim(batch,owner,['audit-input-v1'])
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
                  scope='Existing metadata audit only. No modelling or publication.')
    if errors:raise RuntimeError('Worker failed or lost lease; inspect shared queue')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['plan-audit','run','report'])
    p.add_argument('--batch',required=True)
    p.add_argument('--snapshot')
    p.add_argument('--uid',action='append',default=[])
    p.add_argument('--workers',type=int,default=2)
    p.add_argument('--limit',type=int,default=10000)
    a=p.parse_args()
    if a.command=='plan-audit':
        if not a.snapshot or not a.uid:p.error('plan-audit requires --snapshot and --uid')
        result=plan_audit(a.snapshot,a.batch,a.uid)
    else:result=run(a.batch,a.workers,a.limit) if a.command=='run' else report(a.batch)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
