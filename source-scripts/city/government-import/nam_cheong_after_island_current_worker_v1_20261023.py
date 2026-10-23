"""Lease-supervised current-scene diagnostics for the two unchanged originals."""
import subprocess
import sys
import uuid
from run import ROOT, HERE, save, reservations

BATCH = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023'


def main():
    local = HERE / 'local' / BATCH
    assert not local.exists()
    claim = reservations.claim('nam-fu-current-' + str(uuid.uuid4()),
        ['building:landsd/268867:0', 'building:landsd/270874:0', 'immutable-source-proof:' + BATCH],
        batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    path = local / 'reservation.json'
    save(path, lease)
    command = [sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'), str(path),
               sys.executable, str(HERE / 'selected_original_pair_current_v1_20261023.py'),
               '--batch', BATCH,
               '--patch', 'government-xl-nam-cheong-fu-yun-after-island-terrain-v1-20261023',
               '--capture', 'government-xl-nam-cheong-fu-yun-after-island-capture-v1-20261023',
               '--inventory', 'government-xl-after-island-current-inventory-v1-20261023']
    code = subprocess.run(command, cwd=ROOT).returncode
    save(local / 'worker-terminal.json', dict(exitCode=code, installationApproved=False))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
