"""Continue the frozen Cheung Chau source checks after its exact recovery ends.

No installer or publisher. Stops on missing recovery evidence, changed inputs or
failed checks, preserving every attempt. Ordinary subprocesses perform the work.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import time
from islands_direct_stage import HERE, ROOT, read, save, sha, rel
import islands_cheung_chau_resume as campaign


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recovery-pid', type=int, required=True)
    args = parser.parse_args()
    state = campaign.DOC / 'continuation-state.json'
    checkpoint = campaign.DOC / 'recovered-assets.json'
    deadline = time.monotonic() + 10800
    while not checkpoint.exists():
        command = Path(f'/proc/{args.recovery_pid}/cmdline')
        assert command.exists(), 'Recovery ended without its final checkpoint; inspect its preserved log'
        raw = command.read_bytes().split(b'\0')
        assert any(v.endswith(b'islands_cheung_chau_resume.py') for v in raw) and b'recover' in raw
        assert time.monotonic() < deadline, 'Bounded recovery observation expired'
        save(state, {'state': 'waiting-for-original-recovery', 'recoveryPid': args.recovery_pid,
                     'publication': False, 'newlyInstalled': 0})
        time.sleep(10)
    selected = campaign.verify_frozen()
    recovered = read(checkpoint)
    assert 'assets' in recovered and 'missingUids' in recovered
    # This is a mutable coordinator asset index, not a source/acceptance receipt.
    # Preserve its initial bytes and every source recovery attempt, then finish
    # unattempted peers before claiming the four full check-shard leases.
    initial = checkpoint.with_name('recovered-assets-initial.json')
    assert not initial.exists()
    initial.write_bytes(checkpoint.read_bytes())
    repairs = []
    for attempt in (9, 8, 7):
        before = len(recovered['assets'])
        log = campaign.LOCAL / f'continuation-repair-{attempt}.log'
        with log.open('x') as stream:
            code = subprocess.run([sys.executable, '-u', HERE / 'islands_recover_failed_groups.py',
                                   '--attempt', str(attempt)], cwd=ROOT,
                                  stdout=stream, stderr=subprocess.STDOUT).returncode
        assert code == 0, 'Peer repair coordinator failed; keep its exact evidence'
        report = campaign.DOC / f'repair-{attempt}/summary.json'
        repairs.append({'path': rel(report), 'sha256': sha(report)})
        index = campaign.asset_index(selected['rows'])
        recovered = {**recovered, 'assets': index,
            'missingUids': [r['uid'] for r in selected['rows'] if r['sourceSHA256'] not in index],
            'initialIndex': {'path': rel(initial), 'sha256': sha(initial)}, 'peerRecoveryRefs': repairs}
        temporary = checkpoint.with_name('recovered-assets-next.json')
        save(temporary, recovered); os.replace(temporary, checkpoint)
        if len(index) == before:
            break
    save(state, {'state': 'checking-originals', 'models': len(selected['rows']),
                 'recoveryCheckpointSHA256': sha(checkpoint), 'publication': False})
    def one(shard):
        log = campaign.LOCAL / f'continuation-check-{shard}.log'
        with log.open('x') as stream:
            code = subprocess.run([sys.executable, '-u', HERE / 'islands_cheung_chau_resume.py',
                                   'check', '--shard', str(shard)], cwd=ROOT,
                                  stdout=stream, stderr=subprocess.STDOUT).returncode
        return {'shard': shard, 'exitCode': code, 'log': rel(log)}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(one, range(4)))
    save(state, {'state': 'checks-complete' if all(r['exitCode'] == 0 for r in results) else 'check-error',
                 'results': results, 'publication': False, 'newlyInstalled': 0})
    assert all(r['exitCode'] == 0 for r in results), 'Failed check attempt retained; inspect exact logs'
    print({'checksComplete': 3420, 'newlyInstalled': 0, 'publication': False}, flush=True)


if __name__ == '__main__':
    main()
