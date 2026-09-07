"""Resumable local jobs. First adapter audits trial inputs; it does not upgrade models."""
import argparse
import collections
import concurrent.futures
import json
import pathlib
import sqlite3
import threading
import time
import uuid
from inventory import digest, encode

SCHEMA = """
CREATE TABLE IF NOT EXISTS batch_jobs(
 id TEXT PRIMARY KEY,uid TEXT NOT NULL,stage TEXT NOT NULL,fingerprint TEXT NOT NULL,
 payload TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',attempts INTEGER NOT NULL DEFAULT 0,
 owner TEXT,lease_until REAL NOT NULL DEFAULT 0,next_attempt REAL NOT NULL DEFAULT 0,
 result TEXT,error TEXT);
CREATE TABLE IF NOT EXISTS batch_job_sets(name TEXT NOT NULL,id TEXT NOT NULL REFERENCES batch_jobs(id),
 PRIMARY KEY(name,id));
CREATE TABLE IF NOT EXISTS batch_plans(name TEXT PRIMARY KEY,fingerprint TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS jobs_status ON batch_jobs(status,next_attempt,uid);
"""


def connect(db):
    c = sqlite3.connect(db, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c


def audit_input(payload):
    b = payload['building']
    concerns = []
    if b['height'] is None or b['height'] <= 0:
        concerns.append('non-positive-or-missing-height')
    metadata = json.loads(b['metadata_json'])
    for flag in ('roofWhollyBelowTerrain', 'roofPartlyBelowTerrain', 'baseWhollyAboveTerrain'):
        if metadata.get('terrainAudit', {}).get(flag):
            concerns.append('recorded-'+flag)
    if b['height_source'] != 'landsd':
        concerns.append('height-not-from-government-base-top-pair')
    detail = 'embedded' if b['embedded'] else 'progressive' if payload['model'] else 'basic'
    action = 'review-recorded-placement' if any(c.startswith('recorded-') for c in concerns) else (
        'look-up-available-source-model' if detail == 'basic' else 'reuse-existing-detail')
    return dict(detail=detail, nextAction=action, concerns=concerns,
                qualification='Existing metadata audit only; no new terrain sampling or model conversion.')


def plan(db, selection, dry_run=False):
    c = connect(db)
    try:
        c.executescript(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        selected = c.execute('SELECT * FROM selection_sets WHERE name=?', (selection,)).fetchone()
        if not selected:
            raise ValueError('Run selection first')
        generation = c.execute("SELECT value FROM settings WHERE key='source_manifest_sha256'").fetchone()[0]
        generation = digest(encode([generation, [tuple(r) for r in c.execute('SELECT path,sha256 FROM inputs ORDER BY path')]]).encode())
        if selected['inventory_sha256'] != generation:
            raise ValueError('Selection is stale; refresh it before planning')
        tool = digest(pathlib.Path(__file__).read_bytes())
        rows = c.execute('''SELECT b.* FROM selection_members s JOIN buildings b ON b.uid=s.uid
                            WHERE s.name=? AND b.active=1 ORDER BY s.priority DESC,b.uid''', (selection,)).fetchall()
        jobs = []
        for row in rows:
            model = c.execute('SELECT metadata_json FROM models WHERE uid=?', (row['uid'],)).fetchone()
            payload = encode(dict(building=dict(row), model=json.loads(model[0]) if model else None))
            fingerprint = digest((tool+payload).encode())
            key = digest((row['uid']+'audit-input-v1'+fingerprint).encode())
            jobs.append((key, row['uid'], 'audit-input-v1', fingerprint, payload))
        existing = {r['id']: r['status'] for r in c.execute('SELECT id,status FROM batch_jobs')}
        report = dict(selection=selection, jobs=len(jobs), new=sum(j[0] not in existing for j in jobs),
                      alreadyComplete=sum(existing.get(j[0]) == 'complete' for j in jobs), dryRun=dry_run)
        if dry_run:
            c.rollback()
        else:
            c.execute('DELETE FROM batch_job_sets WHERE name=?', (selection,))
            c.executemany('INSERT OR IGNORE INTO batch_jobs(id,uid,stage,fingerprint,payload) VALUES(?,?,?,?,?)', jobs)
            c.executemany('INSERT INTO batch_job_sets VALUES(?,?)', [(selection, j[0]) for j in jobs])
            c.execute('INSERT OR REPLACE INTO batch_plans VALUES(?,?)',
                      (selection, digest((selected['config_sha256']+generation+tool).encode())))
            c.commit()
        return report
    except BaseException:
        c.rollback()
        raise
    finally:
        c.close()


def claim(db, selection, owner, now=None, lease_seconds=30):
    now = time.time() if now is None else now
    c = connect(db)
    try:
        c.execute('BEGIN IMMEDIATE')
        c.execute("UPDATE batch_jobs SET status='failed',error='retry-limit' WHERE status='running' AND lease_until<? AND attempts>=3", (now,))
        job = c.execute('''SELECT j.* FROM batch_jobs j JOIN batch_job_sets s ON s.id=j.id
             WHERE s.name=? AND j.attempts<3 AND j.next_attempt<=?
             AND (j.status='pending' OR (j.status='running' AND j.lease_until<?)) ORDER BY j.uid LIMIT 1''',
                        (selection, now, now)).fetchone()
        if job:
            c.execute("UPDATE batch_jobs SET status='running',attempts=attempts+1,owner=?,lease_until=? WHERE id=?",
                      (owner, now+lease_seconds, job['id']))
        c.commit()
        return dict(job) if job else None
    finally:
        c.close()


def finish(db, job, owner, result=None, error=None, transient=False):
    c = connect(db)
    try:
        attempts = job['attempts']+1
        status = 'complete' if error is None else 'pending' if transient and attempts < 3 else 'failed'
        with c:
            changed = c.execute('''UPDATE batch_jobs SET status=?,result=?,error=?,owner=NULL,lease_until=0,next_attempt=?
                   WHERE id=? AND status='running' AND owner=?''',
                                (status, encode(result) if result is not None else None, str(error)[:1000] if error else None,
                                 time.time()+min(30, 2**attempts) if status == 'pending' else 0, job['id'], owner)).rowcount
        return bool(changed)
    finally:
        c.close()


def report(db, selection):
    c = connect(db)
    try:
        status = collections.Counter()
        actions = collections.Counter()
        concerns = collections.Counter()
        details = collections.Counter()
        exceptions = []
        for row in c.execute('SELECT j.* FROM batch_jobs j JOIN batch_job_sets s ON j.id=s.id WHERE s.name=? ORDER BY j.uid', (selection,)):
            status[row['status']] += 1
            if row['result']:
                result = json.loads(row['result'])
                actions[result['nextAction']] += 1
                details[result['detail']] += 1
                concerns.update(result['concerns'])
            elif row['error'] and len(exceptions) < 20:
                exceptions.append(dict(uid=row['uid'], error=row['error']))
        return dict(selection=selection, status=dict(status), detail=dict(details), nextActions=dict(actions),
                    concernCounts=dict(concerns), failureExamples=exceptions, newModels=0, aiCalls=0, networkRequests=0,
                    scope='Inventory preflight adapter only. Conversion, terrain validation and publication are separate stages.')
    finally:
        c.close()


def run(db, selection, workers=2, limit=10000):
    if not 1 <= workers <= 4 or limit < 1:
        raise ValueError('Workers must be 1–4 and limit positive')
    c = connect(db)
    try:
        selected = c.execute('SELECT * FROM selection_sets WHERE name=?', (selection,)).fetchone()
        planned = c.execute('SELECT fingerprint FROM batch_plans WHERE name=?', (selection,)).fetchone()
        generation = c.execute("SELECT value FROM settings WHERE key='source_manifest_sha256'").fetchone()[0]
        generation = digest(encode([generation, [tuple(r) for r in c.execute('SELECT path,sha256 FROM inputs ORDER BY path')]]).encode())
        tool = digest(pathlib.Path(__file__).read_bytes())
        if not selected or not planned or selected['inventory_sha256'] != generation or planned[0] != digest((selected['config_sha256']+generation+tool).encode()):
            raise ValueError('Plan is stale; refresh selection and plan before running')
    finally:
        c.close()
    start = time.monotonic()
    stop = threading.Event()
    lock = threading.Lock()
    claimed = 0
    def worker():
        nonlocal claimed
        while not stop.is_set():
            with lock:
                if claimed >= limit:
                    return
                claimed += 1
            owner = str(uuid.uuid4())
            job = claim(db, selection, owner)
            if job is None:
                return
            try:
                if job['stage'] != 'audit-input-v1':
                    raise ValueError('Unsupported stage')
                result = audit_input(json.loads(job['payload']))
                finish(db, job, owner, result=result)
            except Exception as exc:
                finish(db, job, owner, error=exc, transient=isinstance(exc, TimeoutError))
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
    try:
        futures = [executor.submit(worker) for _ in range(workers)]
        for f in futures:
            f.result()
    finally:
        stop.set()
        executor.shutdown(wait=True)
    result = report(db, selection)
    result['seconds'] = round(time.monotonic()-start, 2)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['plan', 'run', 'report'])
    p.add_argument('--db', type=pathlib.Path, default=pathlib.Path(__file__).parent/'local/buildings.sqlite')
    p.add_argument('--selection', default='tourist-trial-v1')
    p.add_argument('--workers', type=int, default=2)
    p.add_argument('--limit', type=int, default=10000)
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    if args.dry_run and args.command != 'plan':
        p.error('--dry-run only applies to plan')
    result = plan(args.db, args.selection, args.dry_run) if args.command == 'plan' else run(args.db, args.selection, args.workers, args.limit) if args.command == 'run' else report(args.db, args.selection)
    print(json.dumps(result, ensure_ascii=False, indent=2))
