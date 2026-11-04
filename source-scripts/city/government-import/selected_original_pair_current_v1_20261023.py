"""Run all current-scene diagnostics for an explicit unchanged original assembly."""
import argparse, subprocess, sys
from pathlib import Path
from run import ROOT, HERE, read, save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'patch', 'capture', 'inventory']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    patch, _ = authenticate(base / a.patch)
    assert patch['status'] == 'private-terrain-validator-passed'
    assert 2 <= len(patch['uids']) == len(set(patch['uids'])) <= 8
    steps = [
        ('runtime', 'selected_original_patch_runtime_v2.py', ['--patch', a.patch, '--capture', a.capture]),
        ('identity', 'selected_original_identity_v3.py', ['--capture', a.batch + '-runtime']),
        ('scope', 'selected_original_patch_scope_v1.py', ['--patch', a.patch, '--inventory', a.inventory]),
        ('neighbours', 'selected_bounded_native_neighbours_v1.py', ['--scope', a.batch + '-scope', '--inventory', a.inventory, '--patch', a.patch]),
    ]
    doc.mkdir()
    refs, phases = [Path(__file__), base / a.patch / 'result.json'], []
    result = dict(uids=patch['uids'], patch=a.patch, capture=a.capture, installationApproved=False,
                  sourceGeometryChanges=0, status='script-investigation')
    for phase, script, tail in steps:
        logfile = doc / (phase + '.log')
        with logfile.open('w') as log:
            code = subprocess.run([sys.executable, str(HERE / script), '--batch', a.batch + '-' + phase, *tail], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        refs += [HERE / script, logfile]
        if code:
            result.update(failedPhase=phase, exitCode=code)
            break
        receipt, _ = authenticate(base / (a.batch + '-' + phase))
        refs.append(base / (a.batch + '-' + phase) / 'result.json')
        phases.append(dict(phase=phase, batch=a.batch + '-' + phase, jobId=receipt['jobId']))
        print(phases[-1], flush=True)
    else:
        result['status'] = 'current-evidence-complete-awaiting-identity-and-assembly-review'
    result.update(completed=phases, qualification='Complete explicit assembly diagnostic execution only. Raw identity, support, foundation, current-neighbour and runtime failures remain authoritative. No approval, source edits, publication or installation credit.')
    save(doc / 'summary.json', result)
    module('original_pair_current_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'explicit-original-assembly-current-diagnostics', refs, result)


if __name__ == '__main__':
    main()
