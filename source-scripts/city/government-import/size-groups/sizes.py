"""Indexed government mesh cost groups. Metadata only; never creates import queues."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'shared-modelling'))
from db import connect
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

POLICY = 'government-size-v1'
DEFAULT_RUN = 'e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec'
GROUPS = {'xs': [0, 100], 'small': [100, 500], 'medium': [500, 2000],
          'large': [2000, 10000], 'xl': [10000, 50000], 'xxl': [50000, None],
          'unmeasured': [None, None]}
SORTS = {'complexity': 'triangles', 'download': 'compressed_bytes', 'memory': 'geometry_bytes'}
COLUMNS = ('run_id cache_key model_id policy source_result_sha sheet source_entry '
           'source_state viewer_uid building_csuid source_hold_reason source_error triangles '
           'source_vertices indexed_vertices compressed_bytes glb_bytes geometry_bytes '
           'width_m height_m depth_m').split()
COLUMN_SQL = sql.SQL(', ').join(map(sql.Identifier, COLUMNS))
TABLE = sql.SQL('astra_modelling.native_model_sizes')


def read_groups(c, run_id):
    c.row_factory = dict_row
    rows = c.execute('''SELECT size_group, count(*) AS models,
        count(viewer_uid) AS prepared_viewer_matches,
        min(triangles) AS min_triangles, max(triangles) AS max_triangles,
        sum(triangles)::bigint AS total_triangles, sum(compressed_bytes)::bigint AS compressed_bytes,
        sum(geometry_bytes)::bigint AS geometry_bytes
        FROM astra_modelling.native_model_sizes WHERE run_id=%s GROUP BY size_group''',
        (run_id,)).fetchall()
    return sorted(rows, key=lambda r: list(GROUPS).index(r['size_group']))


def listing(c, run_id, group=None, order='complexity', limit=20, sheet=None, explain=False):
    where = ['run_id=%s']; params = [run_id]
    if group:
        where.append('size_group=%s'); params.append(group)
    if sheet:
        where.append('sheet=%s'); params.append(sheet)
    columns = ('model_id', 'sheet', 'viewer_uid', 'building_csuid', 'size_group', 'triangles',
               'compressed_bytes', 'geometry_bytes', 'width_m', 'height_m', 'depth_m',
               'source_state', 'source_hold_reason', 'source_error', 'cache_key', 'source_result_sha')
    query = sql.SQL('SELECT {} FROM {} WHERE {} ORDER BY {} DESC NULLS LAST, cache_key, model_id LIMIT %s').format(
        sql.SQL(', ').join(map(sql.Identifier, columns)), TABLE,
        sql.SQL(' AND ').join(map(sql.SQL, where)), sql.Identifier(SORTS[order]))
    params.append(limit)
    c.row_factory = dict_row
    if explain:
        row = c.execute(sql.SQL('EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ') + query, params).fetchone()
        return row['QUERY PLAN'][0]
    return c.execute(query, params).fetchall()


def sync(run_id, dry_run=False):
    started = time.monotonic()
    with connect() as c:
        c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
        c.execute("SET LOCAL lock_timeout='15s'")
        c.execute("SET LOCAL statement_timeout='180s'")
        c.execute('SELECT pg_advisory_xact_lock(5449217)')
        proof = c.execute('''SELECT r.expected_count, count(m.cache_key), count(s.cache_key)
            FROM astra_modelling.native_stage_runs r
            LEFT JOIN astra_modelling.native_stage_members m USING(run_id)
            LEFT JOIN astra_modelling.native_stage_results s USING(cache_key)
            WHERE r.run_id=%s GROUP BY r.expected_count''', (run_id,)).fetchone()
        if not proof or not (proof[0] == proof[1] == proof[2]):
            raise ValueError('Run is missing frozen source outcomes; no partial classification written')
        fingerprints = c.execute('''SELECT m.cache_key,r.result_sha
            FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            WHERE m.run_id=%s ORDER BY m.cache_key''', (run_id,)).fetchall()
        source_digest = hashlib.sha256(json.dumps(fingerprints, separators=(',', ':')).encode()).hexdigest()
        c.execute((HERE/'schema.sql').read_text())
        c.execute('CREATE TEMP TABLE size_expected ON COMMIT DROP AS ' + (HERE/'projection.sql').read_text(), (run_id,))
        expected_count = c.execute('SELECT count(*) FROM size_expected').fetchone()[0]
        inserted = c.execute(sql.SQL('INSERT INTO {} ({}) SELECT {} FROM size_expected ON CONFLICT DO NOTHING').format(
            TABLE, COLUMN_SQL, COLUMN_SQL)).rowcount
        # Verify every persisted field, not merely aggregate counts. Never overwrite drift.
        differences = c.execute(sql.SQL('''SELECT count(*) FROM (
            (SELECT {} FROM size_expected EXCEPT ALL SELECT {} FROM {} WHERE run_id=%s)
            UNION ALL
            (SELECT {} FROM {} WHERE run_id=%s EXCEPT ALL SELECT {} FROM size_expected)
            ) differences''').format(COLUMN_SQL, COLUMN_SQL, TABLE, COLUMN_SQL, TABLE, COLUMN_SQL),
            (run_id, run_id)).fetchone()[0]
        if differences:
            raise ValueError('Persisted profiles differ from immutable sources; transaction rolled back')
        groups = read_groups(c, run_id)
        assert sum(r['models'] for r in groups) == expected_count
        for r in groups:
            lo, hi = GROUPS[r['size_group']]
            if lo is None:
                assert r['min_triangles'] is None and r['max_triangles'] is None
            else:
                assert r['min_triangles'] >= lo and (hi is None or r['max_triangles'] < hi)
        # Check boundary behaviour using the actual generated-column expression.
        expression = c.execute('''SELECT pg_get_expr(d.adbin,d.adrelid) AS expr
            FROM pg_attrdef d JOIN pg_attribute a ON a.attrelid=d.adrelid AND a.attnum=d.adnum
            WHERE d.adrelid='astra_modelling.native_model_sizes'::regclass AND a.attname='size_group' ''').fetchone()['expr']
        boundaries = [(None,'unmeasured'),(0,'xs'),(99,'xs'),(100,'small'),(499,'small'),
                      (500,'medium'),(1999,'medium'),(2000,'large'),(9999,'large'),
                      (10000,'xl'),(49999,'xl'),(50000,'xxl'),(333434,'xxl')]
        for value, label in boundaries:
            got = c.execute(sql.SQL('SELECT {} AS label FROM (SELECT %s::bigint AS triangles) t').format(sql.SQL(expression)), (value,)).fetchone()['label']
            assert got == label, (value, got, label)
        c.execute('ANALYZE astra_modelling.native_model_sizes')
        query_checks = {}
        for name, group, order in [('xxl', 'xxl', 'complexity'), ('small', 'small', 'complexity'),
                                   ('largest', None, 'complexity'), ('download', None, 'download'), ('memory', None, 'memory')]:
            plan = listing(c, run_id, group, order, explain=True)
            def indexes(node):
                return ([node['Index Name']] if 'Index Name' in node else []) + [i for child in node.get('Plans',[]) for i in indexes(child)]
            used = indexes(plan['Plan'])
            if not used: raise ValueError('Representative lookup did not use an index: '+name)
            query_checks[name] = {'executionMs': plan['Execution Time'], 'indexes': used}
        states = c.execute('''SELECT source_state,count(*) AS models FROM astra_modelling.native_model_sizes
            WHERE run_id=%s GROUP BY source_state ORDER BY source_state''', (run_id,)).fetchall()
        summary = {'runId': run_id, 'policy': POLICY, 'sourceDigest': source_digest,
                   'sourceSheets': proof[0], 'models': expected_count, 'groups': groups,
                   'sourceStates': states, 'boundariesInclusiveExclusive': GROUPS,
                   'exactSourceProjectionVerified': True, 'boundaryCasesVerified': len(boundaries),
                   'aiCalls': 0, 'modelDownloads': 0, 'modelChanges': 0, 'queuesCreated': 0,
                   'qualification': 'Triangle complexity groups from frozen government source metadata. Not quality, importance, FPS, AI effort or installation readiness. Physical dimensions and byte costs remain separate.'}
        c.execute('''INSERT INTO astra_modelling.native_model_size_runs(run_id,policy,source_digest,summary)
            VALUES(%s,%s,%s,%s) ON CONFLICT(run_id) DO UPDATE SET summary=excluded.summary,
            source_digest=excluded.source_digest,recorded_at=clock_timestamp()
            WHERE native_model_size_runs.summary IS DISTINCT FROM excluded.summary''',
            (run_id, POLICY, source_digest, Jsonb(summary)))
        report = {**summary, 'insertedRows': inserted, 'dryRun': dry_run,
                  'queryChecks': query_checks, 'seconds': round(time.monotonic()-started, 3)}
        if dry_run: c.rollback()
    if not dry_run:
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            actual = c.execute('SELECT summary FROM astra_modelling.native_model_size_runs WHERE run_id=%s', (run_id,)).fetchone()[0]
            if actual != summary: raise ValueError('Fresh connection summary readback mismatch')
            assert sum(r['models'] for r in read_groups(c, run_id)) == expected_count
        report['freshReadbackVerified'] = True
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-id', default=DEFAULT_RUN)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('sync'); s.add_argument('--dry-run', action='store_true'); s.add_argument('--out', type=Path)
    sub.add_parser('summary')
    ls = sub.add_parser('list'); ls.add_argument('--group', choices=GROUPS)
    ls.add_argument('--sort', choices=SORTS, default='complexity'); ls.add_argument('--limit', type=int, default=20)
    ls.add_argument('--sheet')
    args = p.parse_args()
    if args.command == 'sync':
        report = sync(args.run_id, args.dry_run)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(report, indent=2, default=str)+'\n')
    else:
        if args.command == 'list' and not 1 <= args.limit <= 1000: p.error('limit must be 1–1000')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            if args.command == 'summary': report = read_groups(c, args.run_id)
            else: report = listing(c, args.run_id, args.group, args.sort, args.limit, args.sheet)
    print(json.dumps(report, indent=2, default=str))


if __name__ == '__main__': main()
