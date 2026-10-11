"""Shared immutable per-sheet preparation stages, using existing fenced job leases.

register(label, items) -> runId/cached/pending; cache_key(item) freezes every input.
claim_many(runId, owner, limit=1..8, lease_seconds=300) -> owned rows.
claim(runId, owner, lease_seconds=300) -> one owned row or None.
heartbeat_many(jobs); finish_group([{'job': job, 'result': result}, ...]).
fail(job, error_code, retry=True); report(runId); cached_results(runId).

Artifacts must be uploaded and independently read back by the caller BEFORE finish.
This module validates reference syntax and atomic ownership, not remote file contents.
It writes no viewer, geometry, source archive or model-review records.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'shared-modelling'))
from db import connect
import jobs as shared_jobs
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

STAGE = 'citywide-native-stage-v1'
BATCH = 'citywide-native-shared-v1'
LOCK_ID = 22120260910
SHA = re.compile(r'^[0-9a-f]{64}$')
QUALIFICATION = 'Mechanical preparation only; not publication or architectural acceptance'


def digest(value):
    return hashlib.sha256(shared_jobs.encode(value).encode()).hexdigest()


def normalise(item):
    fields = {'sheet', 'stage', 'sourceSha256', 'pipelineSha256', 'footprintSha256', 'terrainSha256', 'inputs'}
    if not isinstance(item, dict) or set(item) - fields:
        raise ValueError('Unknown stage input fields; place frozen parameters in inputs')
    value = json.loads(shared_jobs.encode(item))
    for field in ('sheet', 'stage'):
        if not isinstance(value.get(field), str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}', value[field]):
            raise ValueError('Invalid sheet or stage')
    for field in ('sourceSha256', 'pipelineSha256', 'footprintSha256'):
        if not isinstance(value.get(field), str) or not SHA.fullmatch(value[field]):
            raise ValueError('Missing or invalid frozen input SHA')
    value.setdefault('terrainSha256', None)
    if value['terrainSha256'] is not None and (not isinstance(value['terrainSha256'], str) or not SHA.fullmatch(value['terrainSha256'])):
        raise ValueError('Invalid terrain SHA')
    if not isinstance(value.get('inputs'), dict):
        raise ValueError('Frozen source references required')
    return value


def cache_key(item):
    return digest([STAGE, normalise(item)])


def _job(key):
    payload = {'cacheKey': key}
    return digest([BATCH, STAGE, payload]), payload


def migrate():
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
        con.execute((HERE / 'schema.sql').read_text())


def register(label, items):
    if not isinstance(label, str) or not label.strip():
        raise ValueError('Run label required')
    frozen = [normalise(item) for item in items]
    if not frozen or len({(v['sheet'], v['stage']) for v in frozen}) != len(frozen):
        raise ValueError('One frozen input per sheet/stage is required')
    by_key = {cache_key(v): v for v in frozen}
    run_id = digest(['native-stage-run-v1', sorted(by_key)])
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
        con.execute('CREATE TEMP TABLE native_input_stage (LIKE astra_modelling.native_stage_inputs INCLUDING DEFAULTS) ON COMMIT DROP')
        with con.cursor().copy('COPY native_input_stage(cache_key,sheet,stage,source_sha,pipeline_sha,footprint_sha,terrain_sha,input_json) FROM STDIN') as copy:
            for key, v in by_key.items():
                copy.write_row((key, v['sheet'], v['stage'], v['sourceSha256'], v['pipelineSha256'], v['footprintSha256'], v['terrainSha256'], Jsonb(v)))
        con.execute('INSERT INTO astra_modelling.native_stage_inputs SELECT * FROM native_input_stage ON CONFLICT DO NOTHING')
        conflict = con.execute('SELECT 1 FROM native_input_stage n JOIN astra_modelling.native_stage_inputs i USING(cache_key) WHERE n.input_json<>i.input_json LIMIT 1').fetchone()
        if conflict:
            raise ValueError('Immutable stage input conflict')
        con.execute('INSERT INTO astra_modelling.native_stage_runs(run_id,expected_count,labels) VALUES(%s,%s,%s) ON CONFLICT(run_id) DO UPDATE SET labels=ARRAY(SELECT DISTINCT unnest(native_stage_runs.labels||EXCLUDED.labels))', (run_id, len(by_key), [label]))
        con.execute('CREATE TEMP TABLE native_member_stage(run_id text,cache_key text,job_id text) ON COMMIT DROP')
        with con.cursor().copy('COPY native_member_stage FROM STDIN') as copy:
            for key in by_key:
                copy.write_row((run_id, key, _job(key)[0]))
        con.execute('INSERT INTO astra_modelling.native_stage_members SELECT * FROM native_member_stage ON CONFLICT DO NOTHING')
        con.execute('''INSERT INTO astra_modelling.jobs(id,batch,stage,payload)
            SELECT m.job_id,%s,%s,jsonb_build_object('cacheKey',m.cache_key)
            FROM native_member_stage m LEFT JOIN astra_modelling.native_stage_results r USING(cache_key)
            WHERE r.cache_key IS NULL ON CONFLICT DO NOTHING''', (BATCH, STAGE))
    return report(run_id)


def claim(run_id, owner, lease_seconds=300):
    rows = claim_many(run_id, owner, 1, lease_seconds)
    return rows[0] if rows else None


def claim_many(run_id, owner, limit, lease_seconds=300):
    """Claim up to eight sheets in one transaction; overlapping runs share jobs."""
    if not isinstance(owner, str) or not owner.strip() or not 1 <= lease_seconds <= 3600:
        raise ValueError('Owner and bounded lease required')
    if type(limit) is not int or not 1 <= limit <= 8:
        raise ValueError('Claim limit must be an integer from 1 to 8')
    with connect() as con:
        con.row_factory = dict_row
        con.execute('''UPDATE astra_modelling.jobs j SET status='failed',error='lease-expired-retry-limit',
            owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp()
            FROM astra_modelling.native_stage_members m WHERE m.run_id=%s AND m.job_id=j.id
            AND j.stage=%s AND j.status='running' AND j.lease_until<=clock_timestamp()
            AND j.attempts>=j.max_attempts''', (run_id, STAGE))
        rows = con.execute('''WITH picked AS (
            SELECT j.id FROM astra_modelling.jobs j
            JOIN astra_modelling.native_stage_members m ON m.job_id=j.id
            LEFT JOIN astra_modelling.native_stage_results r ON r.cache_key=m.cache_key
            WHERE m.run_id=%s AND j.stage=%s AND r.cache_key IS NULL
            AND j.attempts<j.max_attempts AND j.ready_at<=clock_timestamp()
            AND (j.status='pending' OR (j.status='running' AND j.lease_until<=clock_timestamp()))
            ORDER BY j.ready_at,j.id FOR UPDATE OF j SKIP LOCKED LIMIT %s),
            claimed AS (UPDATE astra_modelling.jobs j SET status='running',owner=%s,token=gen_random_uuid(),
            lease_until=clock_timestamp()+make_interval(secs=>%s),attempts=j.attempts+1,
            updated_at=clock_timestamp() FROM picked WHERE j.id=picked.id RETURNING j.*)
            SELECT j.*,i.input_json AS item FROM claimed j
            JOIN astra_modelling.native_stage_inputs i ON i.cache_key=j.payload->>'cacheKey' ''',
            (run_id, STAGE, limit, owner, lease_seconds)).fetchall()
        for row in rows:
            if cache_key(row['item']) != row['payload']['cacheKey']:
                raise ValueError('Frozen stage input checksum mismatch')
        if rows:
            # Start the full deadline after input validation; all rows remain locked.
            deadlines = con.execute('''UPDATE astra_modelling.jobs SET
                lease_until=clock_timestamp()+make_interval(secs=>%s),updated_at=clock_timestamp()
                WHERE id=ANY(%s) RETURNING id,lease_until''',
                (lease_seconds, [row['id'] for row in rows])).fetchall()
            by_id = {r['id']: r['lease_until'] for r in deadlines}
            for row in rows:
                row['lease_until'] = by_id[row['id']]
    return rows


def _owners(jobs):
    if not jobs or len({j['id'] for j in jobs}) != len(jobs):
        raise ValueError('Distinct owned jobs required')
    return ([j['id'] for j in jobs], [j['owner'] for j in jobs], [j['token'] for j in jobs])


def heartbeat_many(jobs, lease_seconds=300):
    if not jobs:
        return True
    if not 1 <= lease_seconds <= 3600:
        raise ValueError('Bounded lease required')
    with connect() as con:
        changed = con.execute('''UPDATE astra_modelling.jobs j SET
            lease_until=clock_timestamp()+make_interval(secs=>%s),updated_at=clock_timestamp()
            FROM unnest(%s::text[],%s::text[],%s::uuid[]) e(id,owner,token)
            WHERE j.id=e.id AND j.owner=e.owner AND j.token=e.token AND j.stage=%s
            AND j.status='running' AND j.lease_until>clock_timestamp()''',
            (lease_seconds, *_owners(jobs), STAGE)).rowcount
        if changed != len(jobs):
            raise ValueError('Stage ownership lost')
    return True


def validate_result(result):
    value = json.loads(shared_jobs.encode(result))
    if not isinstance(value, dict) or value.get('status') not in ('prepared', 'exceptions', 'source-empty'):
        raise ValueError('Explicit preparation outcome required')
    if value.get('qualification') != QUALIFICATION:
        raise ValueError('Mechanical-only qualification required')
    if any(value.get(k) not in (None, False) for k in ('publicationApproved', 'liveReplacement', 'architecturalAcceptance')):
        raise ValueError('Preparation cannot approve publication or architecture')
    counts = value.get('counts')
    if not isinstance(counts, dict) or any(type(n) is not int or n < 0 for n in counts.values()):
        raise ValueError('Non-negative integer counts required')
    artifacts = value.get('artifacts')
    if not isinstance(artifacts, list):
        raise ValueError('Explicit artifact references required')
    if value['status'] == 'prepared' and not artifacts:
        raise ValueError('Prepared outputs require retained artifact references')
    if len({a.get('key') for a in artifacts if isinstance(a, dict)}) != len(artifacts):
        raise ValueError('Artifact keys must be unique')
    for a in artifacts:
        if not isinstance(a, dict) or not isinstance(a.get('key'), str):
            raise ValueError('Invalid artifact reference')
        path = PurePosixPath(a['key'])
        if not a['key'].startswith('astra-modelling/') or '..' in path.parts or '\\' in a['key'] or '?' in a['key'] or '#' in a['key']:
            raise ValueError('Artifact must be a private modelling object key')
        if not isinstance(a.get('sha256'), str) or not SHA.fullmatch(a['sha256']) or type(a.get('bytes')) is not int or a['bytes'] < 0 or not isinstance(a.get('kind'), str) or not a['kind']:
            raise ValueError('Artifact checksum, byte count and kind required')
    if not isinstance(value.get('models', []), list) or any(not isinstance(m, dict) for m in value.get('models', [])):
        raise ValueError('Compact per-model metadata must be a list of objects')
    return value


def finish_group(entries):
    if not entries:
        raise ValueError('Stage results required')
    jobs = [entry['job'] for entry in entries]
    prepared = {entry['job']['id']: validate_result(entry['result']) for entry in entries}
    owners = _owners(jobs)
    with connect() as con:
        live = con.execute('''SELECT j.id,j.payload FROM astra_modelling.jobs j
            JOIN unnest(%s::text[],%s::text[],%s::uuid[]) e(id,owner,token)
            ON j.id=e.id AND j.owner=e.owner AND j.token=e.token
            WHERE j.stage=%s AND j.status='running' AND j.lease_until>clock_timestamp()
            FOR UPDATE OF j''', (*owners, STAGE)).fetchall()
        if len(live) != len(jobs):
            raise ValueError('Stale stage owner')
        con.execute('CREATE TEMP TABLE native_result_stage (LIKE astra_modelling.native_stage_results INCLUDING DEFAULTS) ON COMMIT DROP')
        with con.cursor().copy('COPY native_result_stage(cache_key,result_sha,result) FROM STDIN') as copy:
            for job_id, payload in live:
                result = prepared[job_id]
                copy.write_row((payload['cacheKey'], digest(result), Jsonb(result)))
        con.execute('INSERT INTO astra_modelling.native_stage_results SELECT * FROM native_result_stage ON CONFLICT DO NOTHING')
        if con.execute('SELECT 1 FROM native_result_stage n JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE n.result_sha<>r.result_sha OR n.result<>r.result LIMIT 1').fetchone():
            raise ValueError('Immutable stage result conflict')
        count = con.execute('''UPDATE astra_modelling.jobs j SET status='complete',
            result=jsonb_build_object('cacheKey',j.payload->>'cacheKey','stage',%s::text),
            owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp()
            FROM unnest(%s::text[],%s::text[],%s::uuid[]) e(id,owner,token)
            WHERE j.id=e.id AND j.owner=e.owner AND j.token=e.token AND j.stage=%s
            AND j.status='running' AND j.lease_until>clock_timestamp()''', (STAGE, *owners, STAGE)).rowcount
        if count != len(jobs):
            raise ValueError('Stage expired during result publication')
    return {'accepted': len(entries), 'cacheKeys': [payload['cacheKey'] for _, payload in live]}


def fail(job, error_code, retry=True):
    if not isinstance(error_code, str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,99}', error_code):
        raise ValueError('Sanitised error code required')
    if job.get('stage') != STAGE:
        raise ValueError('Unexpected job stage')
    return shared_jobs.finish(job, error=error_code, retry=retry)


def cached_results(run_id):
    with connect() as con:
        rows = con.execute('''SELECT i.cache_key,i.sheet,i.stage,r.result_sha,r.result
            FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_inputs i USING(cache_key)
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            WHERE m.run_id=%s ORDER BY i.sheet,i.stage''', (run_id,)).fetchall()
    if any(digest(value) != sha for _, _, _, sha, value in rows):
        raise ValueError('Stored stage result checksum mismatch')
    return [{'cacheKey': k, 'sheet': sheet, 'stage': stage, 'resultSha256': sha, 'result': value}
            for k, sheet, stage, sha, value in rows]


def report(run_id):
    with connect() as con:
        expected = con.execute('SELECT expected_count FROM astra_modelling.native_stage_runs WHERE run_id=%s', (run_id,)).fetchone()
        if not expected:
            raise ValueError('Unknown native stage run')
        cached = con.execute('''SELECT count(*) FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE m.run_id=%s''', (run_id,)).fetchone()[0]
        statuses = dict(con.execute('''SELECT j.status,count(*) FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.jobs j ON j.id=m.job_id LEFT JOIN astra_modelling.native_stage_results r USING(cache_key)
            WHERE m.run_id=%s AND r.cache_key IS NULL GROUP BY j.status''', (run_id,)))
        outcomes = dict(con.execute('''SELECT r.result->>'status',count(*) FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE m.run_id=%s GROUP BY 1''', (run_id,)))
    return {'runId': run_id, 'expected': expected[0], 'cached': cached, 'pending': expected[0]-cached,
            'jobs': statuses, 'outcomes': outcomes, 'qualification': QUALIFICATION}
