"""Persist complete diagnostic runs in Neon, including pending and control outcomes.

This store never grants acceptance. Immutable content hashes make retries idempotent;
complete membership and stored JSON are verified again after the transaction commits.
"""
import argparse
import ast
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
VERSION = 'shape-screening-run-v1'
ACTIONS = {'skip', 'keep-current-candidate', 'import-candidate', 'retain-pending'}


def normalise(value):
    # JSONB normalises -0 and integer-valued floats; hash the numeric value.
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [normalise(v) for v in value]
    if isinstance(value, dict):
        return {k: normalise(v) for k, v in value.items()}
    return value


def encode(value):
    return json.dumps(normalise(value), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def routing_hash(path):
    source = Path(path).read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'route')
    return sha(ast.get_source_segment(source, node).encode())


def package(evidence, summary, results, routing_sha=None):
    raw = Path(evidence).read_bytes()
    e = json.loads(gzip.decompress(raw))
    sample, controls = set(e['sampleUids']), set(e['controlUids'])
    if (len(sample) != len(e['sampleUids']) or len(controls) != len(e['controlUids'])
            or sample & controls or sample | controls != set(e['rows'])):
        raise ValueError('Invalid sample/control membership')
    if len(results) != len(e['rows']) or {r['uid'] for r in results} != set(e['rows']):
        raise ValueError('Incomplete or duplicate screening outcomes')
    if summary['evidenceSHA256'] != sha(raw):
        raise ValueError('Screening input SHA mismatch')
    for field in ('sourceCommit', 'manifestDigest'):
        if summary[field] != e[field]:
            raise ValueError('Screening provenance mismatch: ' + field)
    rows = []
    for result in sorted(results, key=lambda r: r['uid']):
        uid = result['uid']
        if (result['inputHash'] != e['rows'][uid]['inputHash'] or
                result['state'] != e['rows'][uid]['state'] or result['action'] not in ACTIONS):
            raise ValueError('Invalid screening outcome identity/state/action')
        if result['action'] == 'skip' and result['state'] not in ('enhanced', 'good-to-go'):
            raise ValueError('Unaccepted form cannot receive existing-skip credit')
        rows.append({'uid': uid, 'role': 'sample' if uid in sample else 'control',
                     'sha256': sha(encode(result)), 'result': result})
    sampled = [r['result'] for r in rows if r['role'] == 'sample']
    counts = dict(Counter(r['action'] for r in sampled))
    if (summary['sampleSize'] != len(sample) or summary['controlCount'] != len(controls)
            or summary['counts'] != counts
            or summary['comparisons'] != dict(Counter(r['comparison'] or 'unavailable' for r in sampled))
            or summary['reasonCounts'] != dict(Counter(reason for r in sampled for reason in r['reasons']))):
        raise ValueError('Screening summary does not match complete outcomes')
    if any(summary[k] != 0 for k in ('aiCalls', 'modelReviewWrites', 'screeningAcceptanceWrites', 'publishedModels')):
        raise ValueError('Only non-modelling diagnostic runs belong in this store')
    route_sha = summary.get('routingSHA256') or routing_sha
    if not route_sha or len(route_sha) != 64:
        raise ValueError('Routing code fingerprint required (also for historical backfill)')
    manifest = {k: summary[k] for k in ('version', 'mode', 'sampleSize', 'controlCount', 'counts',
        'comparisons', 'reasonCounts', 'aiCalls', 'modelReviewWrites', 'screeningAcceptanceWrites',
        'publishedModels', 'sourceCommit', 'manifestDigest', 'engineSHA256', 'evidenceSHA256', 'policy')}
    manifest.update(storeVersion=VERSION, routingSHA256=route_sha, authoritative=False,
        automaticAcceptanceEnabled=False, nativeRun=e['nativeRun'], contextHash=e['contextHash'],
        seed=e['seed'], population=e['population'], excludedUids=e.get('excludedUids', []),
        outcomesSHA256=sha(encode([{k: r[k] for k in ('uid', 'role', 'sha256')} for r in rows])))
    return sha(encode(manifest)), manifest, rows


def verify(stored_manifest, stored_rows, manifest, rows):
    if stored_manifest != manifest:
        raise ValueError('Immutable screening run disagreement')
    expected = {r['uid']: (r['role'], r['sha256'], r['result']) for r in rows}
    if len(stored_rows) != len(expected):
        raise ValueError('Incomplete shared screening run')
    seen = set()
    for uid, role, action, input_hash, result_sha, result in stored_rows:
        if (uid in seen or uid not in expected or (role, result_sha, result) != expected[uid]
                or sha(encode(result)) != result_sha or action != result['action']
                or input_hash != result['inputHash']):
            raise ValueError('Immutable screening outcome disagreement')
        seen.add(uid)


def sync(evidence, summary, results, routing_sha=None, connect_fn=None):
    from psycopg.types.json import Jsonb
    if connect_fn is None:
        sys.path.insert(0, str(HERE.parent / 'shared-modelling'))
        from db import connect as connect_fn
    run_id, manifest, rows = package(evidence, summary, results, routing_sha)
    def read_back(con):
        stored = con.execute('SELECT manifest FROM astra_modelling.shape_screening_runs WHERE run_id=%s', (run_id,)).fetchone()
        if not stored:
            raise ValueError('Shared screening run missing')
        outcomes = con.execute('''SELECT uid,role,action,input_hash,result_sha,result
            FROM astra_modelling.shape_screening_outcomes WHERE run_id=%s''', (run_id,)).fetchall()
        verify(stored[0], outcomes, manifest, rows)
    with connect_fn() as con:
        # Same schema migration lock as shared-modelling/db.py. Diagnostic tables only.
        con.execute('SELECT pg_advisory_xact_lock(217001)')
        con.execute((HERE / 'shape-schema.sql').read_text())
        con.execute('INSERT INTO astra_modelling.shape_screening_runs(run_id,manifest) VALUES(%s,%s) ON CONFLICT DO NOTHING', (run_id, Jsonb(manifest)))
        with con.cursor() as cursor:
            cursor.executemany('''INSERT INTO astra_modelling.shape_screening_outcomes
                (run_id,uid,role,action,input_hash,result_sha,result) VALUES(%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING''', [(run_id, r['uid'], r['role'], r['result']['action'],
                    r['result']['inputHash'], r['sha256'], Jsonb(r['result'])) for r in rows])
        read_back(con)
    with connect_fn() as con:
        con.execute('SET TRANSACTION READ ONLY')
        read_back(con)
    return {'runId': run_id, 'schema': 'astra_modelling', 'rowsVerified': len(rows),
        'sampleRowsVerified': manifest['sampleSize'], 'controlRowsVerified': manifest['controlCount'],
        'pendingRowsVerified': sum(r['result']['action'] == 'retain-pending' for r in rows),
        'postCommitReadBack': True, 'authoritative': False, 'acceptanceWrites': 0,
        'outcomesSHA256': manifest['outcomesSHA256']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--routing-source', type=Path, help='Exact historical routing source when the saved summary has no routing SHA')
    a = parser.parse_args()
    receipt = sync(a.evidence, json.loads((a.report/'summary.json').read_bytes()),
        json.loads(gzip.decompress((a.report/'results.json.gz').read_bytes())),
        routing_hash(a.routing_source) if a.routing_source else None)
    (a.report/'neon-sync.json').write_bytes(encode(receipt) + b'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
