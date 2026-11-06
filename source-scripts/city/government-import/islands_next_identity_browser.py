"""Stage/browser the next disjoint original subset after an installed predecessor.

Waits for exact installed readback and actual lease release. Never approves or
publishes the next cohort; ROOT must inspect its saved staged exports first.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import time
from islands_direct_stage import ROOT, HERE, read, save, rel, sha
from run import connect


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--after-batch', required=True)
    p.add_argument('--batch', required=True)
    a = p.parse_args()
    assert all(s.startswith('government-islands-cheung-chau-') and '/' not in s for s in (a.after_batch, a.batch))
    local = HERE / 'local' / a.batch
    control = HERE / 'local' / (a.batch + '-continuation')
    assert not control.exists(); control.mkdir(parents=True)
    prior = ROOT / 'docs/astra-city/government-import' / a.after_batch
    receipt_path = HERE / 'local' / a.after_batch / 'install-reservation.json'
    deadline = time.monotonic() + 14400
    while True:
        if (prior / 'integration.json').exists() and receipt_path.exists():
            installed = read(prior / 'integration.json'); receipt = read(receipt_path)
            assert installed['neonVerified']
            with connect() as db:
                db.execute('SET TRANSACTION READ ONLY')
                row = db.execute('SELECT released_at FROM astra_modelling.reservation_groups WHERE token=%s AND owner=%s',
                                 (receipt['token'], receipt['owner'])).fetchone()
            assert row is not None
            if row[0] is not None: break
        assert time.monotonic() < deadline
        save(control / 'state.json', {'state': 'waiting-for-installed-predecessor-and-release', 'afterBatch': a.after_batch})
        time.sleep(10)
    assert installed['manifestSHA256'] == sha(ROOT / '3d-viewer/city/data/manifest.json')
    identities = [ROOT / f'docs/astra-city/government-import/government-islands-cheung-chau-identity-{part}-20261106-v1/identities.json.gz'
                  for part in ('part3', 'rest')]
    commands = [('stage', [sys.executable, HERE / 'islands_cheung_identity_subset.py', '--batch', a.batch,
                 '--limit', '50', *[v for path in identities for v in ('--identity', path)]]),
                ('browser', [sys.executable, HERE / 'islands_direct_worker.py', 'browser-solid', '--batch', a.batch])]
    for phase, command in commands:
        log = control / f'{phase}.log'
        save(control / 'state.json', {'state': phase, 'log': rel(log)})
        with log.open('x') as stream:
            code = subprocess.run([str(v) for v in command], cwd=ROOT,
                                  stdout=stream, stderr=subprocess.STDOUT).returncode
        if code:
            save(control / 'state.json', {'state': 'script-error', 'phase': phase, 'exitCode': code, 'log': rel(log)})
            raise RuntimeError('Retain and inspect the exact attempt; no next publication occurred')
    save(control / 'state.json', {'state': 'awaiting-staged-image-inspection', 'publicationApproved': False})


if __name__ == '__main__':
    main()
