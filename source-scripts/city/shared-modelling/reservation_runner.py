"""Supervise a concrete command; never an agent-independent keepalive daemon."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from reservations import DEFAULT_TTL, HERE

HEARTBEAT_SECONDS = 300
DB_TIMEOUT_SECONDS = 20


def _lease_action(action, lease_file, ttl):
    args = [sys.executable, str(HERE / 'reservations.py'), action, '--lease-file', str(lease_file)]
    if action == 'heartbeat':
        args += ['--ttl', str(ttl)]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=DB_TIMEOUT_SECONDS)
        # Do not propagate database/configuration stderr or environment values.
        return result.returncode == 0 and json.loads(result.stdout).get('ok') is True
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return False


def _stop_group(child):
    # Include descendants even when the direct child has just exited.
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    # Signal 0 is not allowed by some macOS sandboxes. Give all descendants a
    # fixed grace period, then send SIGKILL even if the root has already exited.
    time.sleep(2)
    child.poll()
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    child.wait(timeout=5)


def run_reserved(lease_file, command, ttl=DEFAULT_TTL, *, heartbeat_seconds=HEARTBEAT_SECONDS,
                 poll_seconds=0.2):
    """Fail closed on renewal failure; current receipt is released when this command ends."""
    if os.name != 'posix':
        raise ValueError('Supervised process-group cleanup currently requires macOS or Linux')
    if not command:
        raise ValueError('Provide a concrete command after --')
    if isinstance(ttl, bool) or not isinstance(ttl, int) or not 60 <= ttl <= 3600:
        raise ValueError('Supervised TTL must be 60–3600 seconds')
    if not 0 < heartbeat_seconds < ttl - 2 * DB_TIMEOUT_SECONDS - 5 or poll_seconds <= 0:
        raise ValueError('Heartbeat must leave time to stop before the renewed lease expires')
    lease_file = Path(lease_file).resolve()
    if not lease_file.is_file():
        raise ValueError('An existing lease receipt is required')
    # An atomic renewal both verifies ownership and ensures a known safe lifetime before launch.
    if not _lease_action('heartbeat', lease_file, ttl):
        return {'ok': False, 'error': 'lease-not-owned-or-unreachable', 'exitCode': 2}
    child = None
    prior_handlers = {}
    interrupted = False
    result = {'ok': False, 'error': 'command-not-started', 'exitCode': 2}

    def stop_on_signal(signum, frame):
        nonlocal interrupted
        interrupted = True

    try:
        for signum in (signal.SIGTERM, signal.SIGINT):
            prior_handlers[signum] = signal.signal(signum, stop_on_signal)
        child = subprocess.Popen(command, start_new_session=True)
        next_heartbeat = time.monotonic() + heartbeat_seconds
        while True:
            exit_code = child.poll()
            if exit_code is not None:
                result = {'ok': exit_code == 0, 'exitCode': exit_code if exit_code >= 0 else 128 - exit_code}
                break
            if interrupted:
                result = {'ok': False, 'error': 'interrupted', 'exitCode': 130}
                break
            if time.monotonic() >= next_heartbeat:
                # Subprocess timeout bounds network/lock stalls so the child is stopped safely.
                if not _lease_action('heartbeat', lease_file, ttl):
                    result = {'ok': False, 'error': 'lease-lost-or-renewal-failed', 'exitCode': 2}
                    break
                next_heartbeat = time.monotonic() + heartbeat_seconds
            time.sleep(poll_seconds)
    except OSError:
        result = {'ok': False, 'error': 'command-launch-failed', 'exitCode': 2}
    finally:
        try:
            if child is not None:
                _stop_group(child)
        except (OSError, subprocess.TimeoutExpired):
            result = {'ok': False, 'error': 'process-group-cleanup-failed', 'exitCode': 2}
        finally:
            result['released'] = _lease_action('release', lease_file, ttl)
            for signum, previous in prior_handlers.items():
                signal.signal(signum, previous)
    return result
