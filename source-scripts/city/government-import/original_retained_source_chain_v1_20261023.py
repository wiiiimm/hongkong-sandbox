"""Serial current-source/retained-terrain diagnostics, without installation credit."""
import argparse
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'uid', 'source', 'inventory']:
        p.add_argument('--' + k, required=True)
    p.add_argument('--retain-patch', action='append', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    authenticate(base / a.source)
    authenticate(base / a.inventory)
    names = {k: a.batch + '-' + k for k in ['selection', 'capture', 'terrain', 'current', 'prephysical']}
    assert all(not (base / n).exists() for n in names.values())
    doc.mkdir()
    refs = [Path(__file__), base / a.source / 'result.json', base / a.inventory / 'result.json']
    retain = [x for url in a.retain_patch for x in ['--retain-patch', url]]
    steps = [
        ('selection', 'selected_original_refresh_selection_v1.py', ['--capture', a.source, '--uid', a.uid]),
        ('capture', 'selected_original_current_capture_v2.py', ['--capture', names['selection'], '--uid', a.uid]),
        ('terrain', 'selected_original_retained_replacement_v7.py', ['--capture', names['capture'], '--terrain-check', a.source, '--uid', a.uid, *retain]),
        ('current', 'selected_retained_patch_followthrough_v1.py', ['--patch', names['terrain'], '--capture', names['capture'], '--inventory', a.inventory, '--uid', a.uid]),
        ('prephysical', 'selected_original_prephysical_suite_v4_20261023.py', ['--runtime', names['current'] + '-runtime', '--uid', a.uid]),
    ]
    result = dict(uids=[a.uid], batches=names, completed=[], sourceGeometryChanges=0,
                  installationApproved=False, permanentRejection=False, newlyInstalled=0)
    for phase, script, tail in steps:
        save(doc / 'running.json', dict(result, currentPhase=phase))
        logpath = doc / (phase + '.log')
        refs.extend([HERE / script, logpath])
        with logpath.open('w') as log:
            code = subprocess.run([sys.executable, '-u', str(HERE / script), '--batch', names[phase], *tail], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        if code:
            result.update(status='script-or-source-investigation', stoppedAt=phase, exitCode=code)
            break
        receipt, _ = authenticate(base / names[phase])
        refs.append(base / names[phase] / 'result.json')
        result['completed'].append(dict(phase=phase, jobId=receipt['jobId']))
        print(result['completed'][-1], flush=True)
        summary = read(base / names[phase] / 'summary.json')
        if phase == 'terrain' and summary['status'] != 'private-terrain-validator-passed':
            result.update(status='retained-terrain-investigation', stoppedAt=phase)
            break
        if phase == 'current' and (summary.get('basicFlags') or
                set(summary.get('nativeResolved', [])) != {r['uid'] for r in summary.get('nativeRows', [])} or
                any(not r['passed'] for r in summary.get('nativeRows', []))):
            result.update(status='current-neighbour-investigation', stoppedAt=phase)
            break
        if phase == 'prephysical':
            result.update(status=summary['status'])
    save(doc / 'summary.json', result)
    module('retained_source_chain_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'serial-original-retained-source-diagnostic-chain', refs, result)


if __name__ == '__main__':
    main()
