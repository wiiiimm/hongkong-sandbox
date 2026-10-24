"""Sequential tiers, bounded leased workers, independent full readback per tier."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import batch


def run(folder, staging, workers):
    snapshot_path = folder / 'sources.json'
    snap = json.loads(snapshot_path.read_bytes())
    if snap.get('selectionPolicy') != 'installed-v1' or snap['held']:
        raise ValueError('This runner requires the explicit complete installed-source policy')
    for tier in ('original', 'high', 'balanced', 'lightweight'):
        name = folder.name + '-' + tier
        recipe_path = folder / (tier + '-recipe.json')
        print(json.dumps({'tier': tier, 'action': 'launch', 'sourceCount': len(snap['selected'])}), flush=True)
        subprocess.run([sys.executable, '-u', str(batch.HERE/'batch.py'), 'launch',
            '--snapshot', str(snapshot_path), '--recipe', str(recipe_path),
            '--output', str(staging/tier), '--batch', name, '--workers', str(workers)], check=True, cwd=batch.ROOT)
        report = folder / tier / ('readback-' + str(time.time_ns()) + '.json')
        subprocess.run([sys.executable, '-u', str(batch.HERE/'audit.py'),
            '--snapshot', str(snapshot_path), '--recipe', str(recipe_path),
            '--output', str(report), '--batch', name+'-audit', '--apply'], check=True, cwd=batch.ROOT)
        print(json.dumps({'tier':tier, 'action':'verified', 'report':str(report.relative_to(batch.ROOT))}), flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder', type=Path, required=True)
    p.add_argument('--staging', type=Path, required=True)
    p.add_argument('--workers', type=int, default=16)
    args=p.parse_args()
    run(args.folder.resolve(), args.staging.resolve(), args.workers)
