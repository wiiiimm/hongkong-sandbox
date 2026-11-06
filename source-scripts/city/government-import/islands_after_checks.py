"""Continue already-authorised island work after the frozen Cheung check pass.

The Peng Chau subset already has ROOT-inspected staged browser evidence. Its
strict guarded installer runs first, then Cheung candidates get staged browser
checks only. Live readback/inspection and all Cheung approvals remain separate.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import time
from islands_direct_stage import ROOT, HERE, read, save, rel
import islands_cheung_chau_resume as campaign


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checks-pid', type=int, required=True)
    args = parser.parse_args()
    state_path = campaign.DOC / 'after-checks-state.json'
    deadline = time.monotonic() + 10800
    while True:
        state = read(campaign.DOC / 'continuation-state.json')
        if state['state'] == 'checks-complete': break
        assert state['state'] != 'check-error', 'Inspect failed source checks; no publisher started'
        proc = Path(f'/proc/{args.checks_pid}/cmdline')
        assert proc.exists() and any(p.endswith(b'islands_checks_after_recovery.py') for p in proc.read_bytes().split(b'\0'))
        assert time.monotonic() < deadline
        save(state_path, {'state': 'waiting-for-completed-source-checks', 'newlyInstalled': 0})
        time.sleep(10)
    steps = [
        ('install-reviewed-peng-three', [sys.executable, HERE / 'islands_direct_worker.py', 'install',
          '--batch', 'government-islands-peng-chau-narrow-clear-20261106-v2']),
        ('stage-cheung-first-clear', [sys.executable, HERE / 'islands_cheung_clear_subset.py',
          '--batch', 'government-islands-cheung-chau-direct-001-20261106-v2', '--limit', '50']),
        ('browser-cheung-first-clear', [sys.executable, HERE / 'islands_direct_worker.py', 'browser-solid',
          '--batch', 'government-islands-cheung-chau-direct-001-20261106-v2']),
    ]
    completed = []
    for phase, command in steps:
        log = campaign.LOCAL / f'after-checks-{phase}.log'
        save(state_path, {'state': phase, 'completed': completed, 'log': rel(log)})
        with log.open('x') as stream:
            code = subprocess.run([str(x) for x in command], cwd=ROOT,
                                  stdout=stream, stderr=subprocess.STDOUT).returncode
        if code:
            save(state_path, {'state': 'script-error', 'phase': phase, 'exitCode': code,
                              'completed': completed, 'log': rel(log)})
            raise RuntimeError('Inspect exact retained worker log before retry')
        completed.append({'phase': phase, 'log': rel(log)})
    save(state_path, {'state': 'awaiting-live-peng-readback-and-cheung-staged-inspection', 'completed': completed,
                     'cheungInstallationApproved': False})


if __name__ == '__main__':
    main()
