"""Acceptance ledger and input-hash reuse; only current accepted forms skip enhancement.

No geometry-comparison pass is part of this entry point.
Planning and hash checks make zero AI calls. Recording adequacy requires evidence
from a human/agent review or an explicitly validated mechanical acceptance rule.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
POLICY = 'good-enough-v1'
PROOF = ROOT / '3d-viewer/scripts/building-progress/screening-proof.json'


def read_plan(path):
    with gzip.open(path, 'rt') as stream:
        plan = json.load(stream)
    if plan.get('version') != 1 or plan.get('policy') != POLICY:
        raise ValueError('Unsupported screening plan')
    rows = plan['rows']
    if len({r['uid'] for r in rows}) != len(rows):
        raise ValueError('Duplicate screening UID')
    for row in rows:
        if not re.fullmatch(r'[a-f0-9]{64}', row.get('inputHash', '')):
            raise ValueError('Invalid screening fingerprint')
    return plan


def partition(rows):
    groups = {'skip': [], 'enhance': [], 'assess': []}
    states = {'enhanced': 'skip', 'good-to-go': 'skip',
              'enhancement-required': 'enhance', 'unassessed': 'assess'}
    for row in rows:
        if row.get('state') not in states:
            raise ValueError('Unknown assessment state')
        groups[states[row['state']]].append(row)
    return groups


def prepare_entries(entries, plan):
    by_uid = {r['uid']: r for r in plan['rows']}
    prepared, seen = [], set()
    for entry in entries:
        uid = entry['uid']
        if uid in seen or uid not in by_uid:
            raise ValueError('Duplicate or unknown current source UID')
        seen.add(uid)
        if entry['inputHash'] != by_uid[uid]['inputHash']:
            raise ValueError('Rendered inputs changed; rescreen ' + uid)
        if entry['decision'] not in ('good-to-go', 'enhancement-required'):
            raise ValueError('Unsupported decision')
        if not isinstance(entry.get('reason'), str) or not entry['reason'].strip():
            raise ValueError('Name the adequacy criterion or missing visible feature')
        evidence = (ROOT / entry['evidence']).resolve()
        if not evidence.is_relative_to(ROOT) or not evidence.is_file():
            raise ValueError('Evidence must be a repository file')
        actual = hashlib.sha256(evidence.read_bytes()).hexdigest()
        if entry.get('evidenceHash') != actual:
            raise ValueError('Evidence changed or missing pinned evidence hash')
        prepared.append((uid, entry['inputHash'], POLICY, entry['decision'],
                         entry['reason'].strip(), str(evidence.relative_to(ROOT)), actual))
    if not prepared:
        raise ValueError('At least one decision is required')
    return prepared


def database():
    sys.path.insert(0, str(ROOT / 'source-scripts/city/shared-modelling'))
    from db import connect
    import reservations
    return connect, reservations


def migrate():
    connect, reservations = database()
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        con.execute((HERE / 'schema.sql').read_text())


def export_proof():
    connect, _ = database()
    with connect() as con:
        # Latest decision per UID: never resurrect older acceptance after rework.
        rows = con.execute('''SELECT DISTINCT ON (uid) uid,input_hash,policy,
          decision,reason,evidence,evidence_hash,reviewed_at
          FROM astra_modelling.enhancement_screening_events
          ORDER BY uid,id DESC''').fetchall()
        captured = con.execute('SELECT clock_timestamp()').fetchone()[0].isoformat()
    keys = ['uid', 'inputHash', 'policy', 'decision', 'reason', 'evidence', 'evidenceHash', 'reviewedAt']
    proof = {'version': 1, 'policy': POLICY, 'capturedAt': captured,
             'rows': [dict(zip(keys, [*row[:-1], row[-1].isoformat()])) for row in rows]}
    temporary = PROOF.with_suffix('.tmp')
    temporary.write_text(json.dumps(proof, indent=2) + '\n')
    temporary.replace(PROOF)
    return len(rows)


def build_plan(path):
    subprocess.run(['node', str(ROOT / '3d-viewer/scripts/building-progress/generate.mjs'),
                    '--plan', str(path)], cwd=ROOT, check=True)
    return read_plan(path)


def record(entries, receipt_path, request_id, plan):
    if not request_id or not request_id.strip():
        raise ValueError('Stable request ID required')
    prepared = prepare_entries(entries, plan)
    receipt = json.loads(Path(receipt_path).read_text())
    connect, reservations = database()
    from psycopg.rows import dict_row
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        group = reservations._current(con, receipt)
        if not group or not {'building:' + r[0] for r in prepared} <= set(group['resources']):
            raise ValueError('Live source reservation required for every decision')
        previous = con.execute('''SELECT uid,input_hash,policy,decision,reason,evidence,evidence_hash
          FROM astra_modelling.enhancement_screening_events WHERE request_id=%s''', (request_id,)).fetchall()
        if previous:
            actual = sorted(tuple(r[k] for k in ['uid','input_hash','policy','decision','reason','evidence','evidence_hash']) for r in previous)
            if actual != sorted(prepared):
                raise ValueError('Request ID reused with changed decisions')
            return {'reused': len(prepared)}
        with con.cursor() as cur:
            cur.executemany('''INSERT INTO astra_modelling.enhancement_screening_events
              (uid,input_hash,policy,decision,reason,evidence,evidence_hash,owner,token,request_id)
              VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
              [(*r, group['owner'], group['token'], request_id) for r in prepared])
    return {'recorded': len(prepared)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['migrate', 'export', 'plan', 'record'])
    parser.add_argument('--offline', action='store_true', help='Preview committed proof only; not an authoritative work plan')
    parser.add_argument('--out', type=Path, default=HERE / 'local')
    parser.add_argument('--entries', type=Path)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--request-id')
    args = parser.parse_args()
    if args.command == 'migrate':
        migrate(); print('Additive screening ledger ready'); return
    if args.command == 'export':
        print(json.dumps({'exported': export_proof()})); return
    if args.offline and args.command == 'record':
        parser.error('Recording requires the shared database')
    if not args.offline:
        export_proof()  # A failed refresh aborts, never silently schedules from stale state.
    args.out.mkdir(parents=True, exist_ok=True)
    plan = build_plan(args.out / 'inputs.json.gz')
    if args.command == 'record':
        if not all((args.entries, args.receipt, args.request_id)):
            parser.error('record requires entries, receipt and request-id')
        print(json.dumps(record(json.loads(args.entries.read_text()), args.receipt, args.request_id, plan)))
        export_proof(); plan = build_plan(args.out / 'inputs.json.gz')
    groups = partition(plan['rows'])
    for action, rows in groups.items():
        with gzip.open(args.out / (action + '.json.gz'), 'wt') as stream:
            json.dump({'policy': POLICY, 'authoritative': not args.offline, 'rows': rows}, stream)
    summary = {'policy': POLICY, 'aiCalls': 0, 'authoritative': not args.offline,
               'counts': {action: len(rows) for action, rows in groups.items()},
               'limits': 'Skip applies to enhancement only, not source refresh, dependencies or whole-region acceptance. Assess is not an enhancement queue.'}
    (args.out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
