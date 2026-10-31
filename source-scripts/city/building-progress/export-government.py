"""Freeze exact prepared government UID/CSUID matches from read-only Neon for static builds.

Availability is a source relationship, not placement approval or an AI modelling job.
The build intersects this proof with current displayed identities and accepted reviews.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
RUN = 'e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', default=RUN)
    parser.add_argument('--out', type=Path, default=ROOT/'3d-viewer/scripts/building-progress/government-source-proof.json.gz')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT/'source-scripts/city/shared-modelling'))
    from db import connect
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        captured = con.execute('SELECT now()::text').fetchone()[0]
        # Only successfully prepared, uniquely matched candidates. Held/corrupt sources
        # remain outside this denominator; source availability does not waive validation.
        rows = con.execute("""SELECT x->'candidate'->>'uid', x->'candidate'->>'buildingCSUID'
            FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
            WHERE m.run_id=%s AND x->>'state'='packed-needs-placement-review' ORDER BY 1""", (args.run_id,)).fetchall()
    if not rows or len({r[0] for r in rows}) != len(rows) or any(not all(r) for r in rows):
        raise ValueError('Empty, ambiguous or incomplete government source identity proof')
    proof = {'version': 1, 'runId': args.run_id, 'capturedAt': captured,
        'source': 'Hong Kong Lands Department non-textured building model inventory', 'rows': rows}
    raw = gzip.compress(json.dumps(proof, separators=(',', ':')).encode(), mtime=0)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.out.with_suffix('.tmp'); tmp.write_bytes(raw); tmp.replace(args.out)
    print(json.dumps({'matchedForms': len(rows), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'databaseWrites': 0, 'aiCalls': 0}))


if __name__ == '__main__':
    main()
