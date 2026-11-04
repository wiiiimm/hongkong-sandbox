"""After verified source recovery, process all remaining positive originals sequentially."""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'recovery', 'inventory', 'selection']:
        ap.add_argument('--' + key, required=True)
    ap.add_argument('--existing-selection', action='append', required=True)
    ap.add_argument('--recovery-pid', type=int, required=True)
    a = ap.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    doc.mkdir()
    refs = [Path(__file__), HERE / 'recovered_original_current_followthrough_v2.py']
    excluded = set()
    for name in a.existing_selection:
        _, pins = authenticate(base / name)
        p = base / name / 'selection.json.gz'
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        excluded.update(r['uid'] for r in read(p)['rows'])
        refs.extend([base / name / 'result.json', p])
    deadline = time.monotonic() + 7200
    receipt = base / a.recovery / 'result.json'
    while not receipt.exists():
        assert time.monotonic() < deadline, 'Recovery receipt still pending; no worker restart'
        command = Path('/proc') / str(a.recovery_pid) / 'cmdline'
        assert command.exists() and a.recovery in command.read_bytes().replace(b'\0', b' ').decode(), 'Recovery worker stopped without completed receipt; investigate, do not restart automatically'
        time.sleep(20)
    result, pins = authenticate(base / a.recovery)
    p = base / a.recovery / 'summary.json'
    assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
    rows = read(p)['rows']
    assert len(rows) == read(p)['selected'] == len({r['uid'] for r in rows})
    refs.extend([receipt, p])
    positive = [r for r in rows if r['status'] == 'source-terrain-recovered' and r['foundation']['completeTerrainTriangles'] == r['foundation']['triangles'] and r['foundation']['fullyBuriedTriangles'] == 0]
    selected = [r for r in positive if r['uid'] not in excluded]
    save(doc / 'selection.json', dict(rows=selected, excludedAlreadyProcessing=sorted(excluded), sourceRecoveryJob=result['jobId'], qualification='Immediate current-scene diagnostics only; no approval or production queue.'))
    remaining = {r['uid'] for r in selected}
    outcomes = []
    while remaining:
        name = a.batch + '-chunk-' + str(len(outcomes)+1).zfill(2)
        count = min(40, len(remaining))
        command = [sys.executable, str(HERE / 'recovered_original_current_followthrough_v2.py'), '--batch', name, '--recovery', a.recovery, '--inventory', a.inventory, '--selection', a.selection, '--limit', str(count)]
        command += [v for uid in sorted(excluded) for v in ['--exclude-uid', uid]]
        with (doc / ('chunk-' + str(len(outcomes)+1).zfill(2) + '.log')).open('w') as log:
            proc = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        selectionpath = base / name / 'selected-source-checkpoints.json'
        assert selectionpath.exists(), 'Selection failed before source processing; inspect exact child log'
        chosen = {r['uid'] for r in read(selectionpath)['rows']}
        assert len(chosen) == count and chosen <= remaining
        child, _ = authenticate(base / name)
        refs.append(base / name / 'result.json')
        outcomes.append(dict(batch=name, uids=sorted(chosen), exitCode=proc.returncode, jobId=child['jobId'], status=child['status']))
        remaining -= chosen
        excluded |= chosen
        save(doc / 'progress.json', dict(outcomes=outcomes, remaining=sorted(remaining), installationApproved=False))
        print(outcomes[-1], flush=True)
    final = dict(uids=[r['uid'] for r in selected], outcomes=outcomes, remaining=0, installationApproved=False, publication=False, qualification='All additional positive recovered originals processed to current-scene diagnostic outcomes. Holds remain unfinished; no permanent rejection or installation inferred.')
    save(doc / 'summary.json', final)
    module('remaining_recovered_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'remaining-recovered-current-diagnostics-supervisor', refs, final)


if __name__ == '__main__':
    main()
