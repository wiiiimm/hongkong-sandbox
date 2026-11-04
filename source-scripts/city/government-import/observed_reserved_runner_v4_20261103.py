"""Bounded retries of the identical fenced action after transport timeouts/shutdowns.

Three20-second attempts plus2/5-second backoff fit within67seconds. A timeout grants no ownership: only a successful repeat of the exact atomic
renewal permits continued work. No claim or token change occurs. Only3600s
leases are supported; the unchanged runner renews every300seconds and still
stops its exact child group on loss, unexpected failures or exhausted retries.
"""
import json
import subprocess
import sys
import time
from pathlib import Path
from run import ROOT, HERE, read, save, reservations
sys.path.insert(0, str(HERE.parent / 'shared-modelling'))
import reservation_runner

TRANSIENT_SHUTDOWN = frozenset(['57P01', '57P02', '57P03'])


def bounded_action(action, lease_file, ttl, *, dispatch=None, sleep=time.sleep, emit=print):
    if ttl != 3600 or action not in ['heartbeat', 'release']:
        return False
    command = [sys.executable, str(HERE / 'reservation_action_diagnostic_v1_20261103.py'), action,
               '--lease-file', str(lease_file), '--ttl', str(ttl)]
    dispatch = dispatch or (lambda args: subprocess.run(args, capture_output=True, text=True, timeout=20))
    for attempt in range(3):
        try:
            result = dispatch(command)
            safe = json.loads(result.stdout)
            assert isinstance(safe, dict)
        except subprocess.TimeoutExpired:
            emit(json.dumps(dict(reservationAction=action, ok=False, attempt=attempt + 1, failureClass='database-observation-timeout')))
            if attempt == 2:
                return False
            sleep([2, 5][attempt])
            continue
        except (OSError, ValueError, AssertionError) as error:
            emit(json.dumps(dict(reservationAction=action, ok=False, attempt=attempt + 1, failureClass=type(error).__name__)))
            return False
        ok = result.returncode == 0 and safe.get('ok') is True
        record = {k: safe[k] for k in ['errorClass', 'sqlstate', 'leaseLost'] if k in safe}
        emit(json.dumps(dict(reservationAction=action, ok=ok, attempt=attempt + 1, **record)))
        if ok:
            return True
        if safe.get('leaseLost') or safe.get('sqlstate') not in TRANSIENT_SHUTDOWN or attempt == 2:
            return False
        sleep([2, 5][attempt])
    return False


def execute_reserved(lease, path, command):
    try:
        save(path, json.loads(json.dumps(lease, default=str)))
        result = subprocess.run([sys.executable, __file__, str(path), *command], cwd=ROOT)
        assert result.returncode == 0, 'Diagnostic failed; preserve evidence, no approval'
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


def main():
    original = reservation_runner._lease_action
    reservation_runner._lease_action = bounded_action
    try:
        result = reservation_runner.run_reserved(sys.argv[1], sys.argv[2:], ttl=3600)
        print(json.dumps(result), flush=True)
        return 0 if result['ok'] else result['exitCode']
    finally:
        reservation_runner._lease_action = original


if __name__ == '__main__':
    raise SystemExit(main())
