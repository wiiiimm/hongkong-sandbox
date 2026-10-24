"""Immediately check an explicit first group of recovered originals against current map."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'recovery', 'inventory', 'selection']:
        ap.add_argument('--' + k, required=True)
    ap.add_argument('--limit', type=int, default=10)
    a = ap.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and 1 <= a.limit <= 40
    doc = BASE / a.batch
    assert not doc.exists()
    refs = [Path(__file__)]
    progress = read(BASE / a.recovery / 'progress.json')
    selected = []
    for row in progress['rows']:
        if row['status'] != 'source-terrain-recovered':
            continue
        f = row['foundation']
        if f['completeTerrainTriangles'] != f['triangles'] or f['fullyBuriedTriangles']:
            continue
        receipt, pins = authenticate(BASE / row['batch'])
        assert receipt['jobId'] == row['jobId']
        p = BASE / row['batch'] / 'summary.json'
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        source = read(p)['rows'][0]
        assert source['uid'] == row['uid'] and source['sourceSHA256'] == row['sourceSHA256'] and source['originalTerrainFoundation'] == f
        selected.append(row)
        refs.extend([BASE / row['batch'] / 'result.json', p])
        if len(selected) == a.limit:
            break
    assert len(selected) == a.limit, 'Not enough completed positive source terrain diagnostics'
    inventory, pins = authenticate(BASE / a.inventory)
    assert pins['3d-viewer/city/data/manifest.json'] == digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes())
    refs.append(BASE / a.inventory / 'result.json')
    doc.mkdir()
    save(doc / 'selected-source-checkpoints.json', dict(rows=selected, qualification='Full original terrain coverage/zero burial only; all current placement and identity checks remain.'))
    names = {k: a.batch + '-' + k for k in ['selection', 'capture', 'candidates']}
    commands = [
        ('selection', 'selected_original_refresh_selection_v1.py', ['--capture', a.selection, *[v for r in selected for v in ['--uid', r['uid']]]]),
        ('capture', 'selected_original_current_capture_v2.py', ['--capture', names['selection'], *[v for r in selected for v in ['--uid', r['uid']]]]),
        ('candidates', 'selected_original_bounded_candidate_batch_v2.py', ['--capture', names['capture'], '--inventory', a.inventory, '--workers', '1', *[v for r in selected for v in ['--candidate', r['uid'] + ',' + r['batch']]]]),
    ]
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'OPENBLAS_NUM_THREADS': '1'}
    result = dict(uids=[r['uid'] for r in selected], batches=names, installationApproved=False, publication=False)
    for phase, script, tail in commands:
        with (doc / (phase + '.log')).open('w') as log:
            proc = subprocess.run([sys.executable, str(HERE / script), '--batch', names[phase], *tail], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        if proc.returncode:
            result.update(status='script-investigation', failedPhase=phase, exitCode=proc.returncode)
            break
        receipt, _ = authenticate(BASE / names[phase])
        refs.append(BASE / names[phase] / 'result.json')
        print(dict(phase=phase, jobId=receipt['jobId']), flush=True)
    else:
        result.update(status='current-candidate-checks-complete', rows=read(BASE / names['candidates'] / 'summary.json')['rows'])
    save(doc / 'summary.json', result)
    module('recovered_current_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'recovered-original-current-followthrough', refs, result)


if __name__ == '__main__':
    main()
