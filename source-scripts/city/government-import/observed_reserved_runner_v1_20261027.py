"""Same fail-closed reservation runner, with credential-free action diagnostics.

No retry, ownership bypass, TTL change or longer database timeout is introduced.
"""
import json
from pathlib import Path
import subprocess
import sys
import time

SHARED = Path(__file__).resolve().parent.parent / 'shared-modelling'
sys.path.insert(0, str(SHARED))
import reservation_runner


def observed_action(action, lease_file, ttl):
    command = [sys.executable, str(SHARED / 'reservations.py'), action, '--lease-file', str(lease_file)]
    if action == 'heartbeat':
        command += ['--ttl', str(ttl)]
    started = time.monotonic()
    record = {'reservationAction': action, 'ok': False}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        record['exitCode'] = result.returncode
        if result.returncode != 0:
            record['failureClass'] = 'subprocess-nonzero'
        else:
            record['ok'] = json.loads(result.stdout).get('ok') is True
            if not record['ok']:
                record['failureClass'] = 'database-action-not-ok'
    except subprocess.TimeoutExpired:
        record['failureClass'] = 'database-observation-timeout'
    except OSError:
        record['failureClass'] = 'subprocess-launch-error'
    except ValueError:
        record['failureClass'] = 'invalid-action-json'
    finally:
        record['elapsedSeconds'] = round(time.monotonic() - started, 3)
        # Never log stdout, stderr, environment, connection strings or lease IDs.
        print(json.dumps(record), flush=True)
    return record['ok']


def main():
    original = reservation_runner._lease_action
    reservation_runner._lease_action = observed_action
    try:
        result = reservation_runner.run_reserved(sys.argv[1], sys.argv[2:], ttl=3600)
        print(json.dumps(result, indent=2), flush=True)
        return 0 if result['ok'] else result['exitCode']
    finally:
        reservation_runner._lease_action = original


if __name__ == '__main__':
    raise SystemExit(main())
