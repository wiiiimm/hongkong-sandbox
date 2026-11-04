"""Shared leased jobs: stable IDs, server-clock leases and stale-worker fencing."""
import hashlib
import json
import uuid
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from db import connect


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def enqueue(batch, stage, payload):
    if not batch or not stage:
        raise ValueError('Batch and stage are required')
    identity = hashlib.sha256(encode([batch, stage, payload]).encode()).hexdigest()
    with connect() as con:
        con.execute('''INSERT INTO astra_modelling.jobs(id,batch,stage,payload)
            VALUES(%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING''', (identity,batch,stage,Jsonb(payload)))
    return identity


def claim(batch, owner, stages, lease_seconds=60):
    if not owner or not stages or not 1 <= lease_seconds <= 3600:
        raise ValueError('Owner, explicit supported stages and lease of 1–3600 seconds required')
    with connect() as con:
        con.row_factory = dict_row
        # Expired final attempts are terminal. Scope to this batch and worker capability.
        con.execute('''UPDATE astra_modelling.jobs SET status='failed',error='lease-expired-retry-limit',
            owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp()
            WHERE batch=%s AND stage=ANY(%s) AND status='running'
            AND lease_until<=clock_timestamp() AND attempts>=max_attempts''', (batch,list(stages)))
        row = con.execute('''WITH picked AS (
            SELECT id FROM astra_modelling.jobs WHERE batch=%s AND stage=ANY(%s)
              AND attempts<max_attempts AND ready_at<=clock_timestamp()
              AND (status='pending' OR (status='running' AND lease_until<=clock_timestamp()))
            ORDER BY ready_at,id FOR UPDATE SKIP LOCKED LIMIT 1
          ) UPDATE astra_modelling.jobs j SET status='running',owner=%s,token=%s,
              lease_until=clock_timestamp()+make_interval(secs=>%s),attempts=attempts+1,
              updated_at=clock_timestamp()
            FROM picked WHERE j.id=picked.id RETURNING j.*''',
            (batch,list(stages),owner,uuid.uuid4(),lease_seconds)).fetchone()
    return row


def heartbeat(job, lease_seconds=60):
    if not 1 <= lease_seconds <= 3600:
        raise ValueError('Invalid lease duration')
    with connect() as con:
        return con.execute('''UPDATE astra_modelling.jobs SET
            lease_until=clock_timestamp()+make_interval(secs=>%s),updated_at=clock_timestamp()
            WHERE id=%s AND owner=%s AND token=%s AND status='running'
              AND lease_until>clock_timestamp()''',
            (lease_seconds,job['id'],job['owner'],job['token'])).rowcount == 1


def finish(job, result=None, error=None, retry=False):
    # Results must contain metadata/immutable object keys, never credentials or mutable shared paths.
    status = 'complete' if error is None else ('pending' if retry and job['attempts']<job['max_attempts'] else 'failed')
    with connect() as con:
        return con.execute('''UPDATE astra_modelling.jobs SET status=%s,result=%s,error=%s,
            owner=NULL,token=NULL,lease_until=NULL,
            ready_at=clock_timestamp()+make_interval(secs=>%s),updated_at=clock_timestamp()
            WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()''',
            (status,Jsonb(result) if result is not None else None,str(error)[:1000] if error else None,
             min(30,2**job['attempts']) if status=='pending' else 0,job['id'],job['owner'],job['token'])).rowcount == 1


def report(batch):
    with connect() as con:
        counts = dict(con.execute('SELECT status,count(*) FROM astra_modelling.jobs WHERE batch=%s GROUP BY status',(batch,)))
    return {'batch':batch,'status':counts,'qualification':'Job completion is not model acceptance or publication.'}
