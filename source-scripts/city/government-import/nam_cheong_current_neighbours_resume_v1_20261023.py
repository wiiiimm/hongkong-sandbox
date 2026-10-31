"""Resume only neighbour diagnostics; child owns all building/terrain leases."""
import json
import subprocess
import sys
import uuid
from run import ROOT, HERE, save, reservations

BATCH = 'government-xl-nam-cheong-fu-yun-after-island-neighbours-v1-20261023'


def main():
    path = HERE / 'local' / BATCH / 'supervisor-lease.json'
    assert not path.parent.exists()
    lease = reservations.claim('nam-fu-neighbours-' + str(uuid.uuid4()),
        ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert lease['ok']
    lease = lease['reservation']
    try:
        save(path, json.loads(json.dumps(lease, default=str)))
        command = [sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'), str(path),
                   sys.executable, str(HERE / 'selected_bounded_native_neighbours_v1.py'),
                   '--batch', BATCH,
                   '--scope', 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-scope',
                   '--patch', 'government-xl-nam-cheong-fu-yun-after-island-terrain-v1-20261023',
                   '--inventory', 'government-xl-after-island-current-inventory-v1-20261023']
        code = subprocess.run(command, cwd=ROOT).returncode
        save(path.parent / 'worker-terminal.json', dict(exitCode=code))
        raise SystemExit(code)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
