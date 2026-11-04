"""Wait for the live mobile controller, then inspect eight exact source faces.

No competing model lease, takeover, worker restart, geometry change or approval.
The original controller's evidence remains independent of this diagnostic.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

from run import ROOT, HERE, read, save, reservations

PREFIX = 'government-xl-west-kowloon-north-pair-after-ocean-'
BATCH = PREFIX + 'nonwall-exact-edge-context-v1-20261027'


def execute_reserved(lease, path, command):
    try:
        # Database leases contain datetimes/UUIDs. Keep serialization inside
        # cleanup scope so a failed local write never strands our own lease.
        save(path, json.loads(json.dumps(lease, default=str)))
        result = subprocess.run([sys.executable, str(HERE / 'observed_reserved_runner_v1_20261027.py'),
                                 str(path), *command], cwd=ROOT)
        assert result.returncode == 0, 'Diagnostic failed; preserve evidence, no approval'
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


def process_identity(pid):
    path = Path('/proc') / str(pid)
    try:
        # Fields after the final ')' begin with process state (field 3).
        fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
        command = (path / 'cmdline').read_bytes()
        if fields[0] == 'Z':
            return None
        return fields[19], command
    except FileNotFoundError:
        return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--after-pid', type=int, required=True)
    a = p.parse_args()
    identity = process_identity(a.after_pid)
    assert identity and b'north_pair_remaining_mobile_v1_20261027.py' in identity[1]
    assert a.after_pid != os.getpid()
    base = ROOT / 'docs/astra-city/government-import'
    local = HERE / 'local' / BATCH
    assert not (base / BATCH).exists() and not local.exists()
    local.mkdir()
    save(local / 'predecessor.json', dict(pid=a.after_pid, startTicks=identity[0],
                                       command='north_pair_remaining_mobile_v1_20261027.py'))
    print('Waiting for the exact live mobile controller; no model lease claimed.', flush=True)
    while process_identity(a.after_pid) == identity:
        time.sleep(30)
    print('Predecessor terminal or identity changed; acquiring a fresh source-only lease.', flush=True)
    claim = reservations.claim('north-nonwall-topology-' + str(uuid.uuid4()),
                               ['building:landsd/182397:0'], batch=BATCH, ttl=3600)
    assert claim['ok'], 'Source still reserved; no takeover permitted'
    lease = claim['reservation']
    path = local / 'reservation.json'
    command = [sys.executable, str(HERE / 'original_face_edge_context_v1_20261027.py'),
               '--batch', BATCH, '--runtime', PREFIX + 'three-member-runtime-v2-20261027',
               '--low-faces', PREFIX + '182397-0-low-faces-v1-20261027',
               '--uid', 'landsd/182397:0', '--faces', '5255,5284,5285,9268,9269,9270,9306,9307',
               '--lease', str(path)]
    execute_reserved(lease, path, command)
    assert (base / BATCH / 'result.json').exists()
    print('Exact eight-face topology saved; architectural and installation decisions remain pending.', flush=True)


if __name__ == '__main__':
    main()
