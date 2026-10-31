"""Recover and export a large sample in sequential, at-most-1,000-form source leases."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import subprocess
import time
from shape_prepare import HERE, ROOT, prepare, save, read


def batches(evidence, limit=1000):
    if not 1 <= limit <= 1000:
        raise ValueError('Source batch limit must be 1..1000')
    native = defaultdict(list)
    for outcome in evidence['native']:
        for uid in {v['uid'] for v in outcome['model'].get('matching', {}).get('viewerMatches', [])}:
            native[uid].append(outcome)
    chosen, errors = [], {}
    for uid in evidence['rows']:
        matches = native[uid]
        if len(matches) == 1 and matches[0]['model'].get('asset'):
            chosen.append(uid)
        else:
            errors[uid] = 'native-source-ambiguous' if len(matches) > 1 else 'native-source-unavailable'
    # Neighbouring sheet work stays together as far as the lease bound allows.
    chosen.sort(key=lambda uid: (native[uid][0]['sheet'], uid))
    return [chosen[i:i+limit] for i in range(0, len(chosen), limit)], errors


def run(evidence, cache, out, allow_source=False, workers=4, env_file=None):
    started = time.perf_counter()
    e = json.loads(gzip.decompress(Path(evidence).read_bytes()))
    out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    groups, errors = batches(e)
    rows, methods, receipts = [], Counter(), []
    for i, group in enumerate(groups):
        ids = set(group)
        subset = {**e, 'rows': {uid: e['rows'][uid] for uid in group}}
        source = out / f'acquisition-inputs-{i+1}.json.gz'
        source.write_bytes(gzip.compress(json.dumps(subset, separators=(',', ':')).encode(), mtime=0))
        print(json.dumps({'batch': i+1, 'batches': len(groups), 'sourceForms': len(ids)}), flush=True)
        result = prepare(source, cache, allow_source, workers, env_file)
        rows.extend(result['rows']); errors.update(result['errors']); methods.update(result['methods'])
        receipts.append({k: v for k, v in result.items() if k != 'rows'})
    if len({r['uid'] for r in rows}) != len(rows) or set(errors) & {r['uid'] for r in rows}:
        raise ValueError('Duplicate or inconsistent acquisition outcomes')
    if set(e['rows']) != set(errors) | {r['uid'] for r in rows}:
        raise ValueError('Incomplete acquisition outcomes')
    save(out/'geometry-inputs.json', {'rows': rows, 'errors': errors})
    subprocess.run(['node', str(HERE/'shape_geometry.mjs'), str(out/'geometry-inputs.json'), str(out/'geometry')], cwd=ROOT, check=True)
    index = read(out/'geometry/index.json')
    index['rows'].extend({'uid': uid, 'error': error} for uid, error in sorted(errors.items()))
    save(out/'geometry/index.json', index)
    report = {'sourceForms': len(e['rows']), 'recovered': len(rows), 'acquisitionErrors': errors,
        'geometryPairs': sum('file' in r for r in index['rows']),
        'geometryErrors': {r['uid']: r['error'] for r in index['rows'] if 'error' in r},
        'methods': dict(methods), 'batches': receipts, 'seconds': round(time.perf_counter()-started, 3),
        'aiCalls': 0, 'publication': False}
    save(out/'acquisition.json', report)
    print(json.dumps({k: v for k, v in report.items() if k not in ('acquisitionErrors', 'geometryErrors', 'batches')}), flush=True)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--cache', type=Path, default=HERE/'local/shapes')
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--allow-source-download', action='store_true')
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--env-file', type=Path)
    a = p.parse_args()
    run(a.evidence, a.cache, a.out, a.allow_source_download, a.workers, a.env_file)


if __name__ == '__main__':
    main()
