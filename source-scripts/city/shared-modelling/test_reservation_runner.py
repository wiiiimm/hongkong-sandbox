import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import reservation_runner as runner
import reservations


class SupervisedRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.receipt = self.root / 'lease.json'
        self.receipt.write_text(json.dumps({'owner':'fixture','token':'fixture'}))

    def tearDown(self): self.temp.cleanup()

    def run_child(self, body, **kwargs):
        return runner.run_reserved(self.receipt, [sys.executable, '-c', body], poll_seconds=0.01, **kwargs)

    def test_policy_defaults(self):
        self.assertEqual(reservations.DEFAULT_TTL, 1800)
        self.assertEqual(runner.HEARTBEAT_SECONDS, 300)

    def test_child_exit_releases_and_propagates_failure(self):
        with patch.object(runner, '_lease_action', return_value=True) as action:
            result = self.run_child('raise SystemExit(7)')
        self.assertEqual(result['exitCode'], 7)
        self.assertTrue(result['released'])
        self.assertEqual([call.args[0] for call in action.call_args_list], ['heartbeat','release'])

    def test_initial_ownership_failure_never_launches(self):
        marker = self.root / 'started'
        with patch.object(runner, '_lease_action', return_value=False), patch.object(runner.subprocess, 'Popen') as popen:
            result = self.run_child(f'open({str(marker)!r}, "w").write("started")')
        popen.assert_not_called()
        self.assertFalse(marker.exists())
        self.assertEqual(result['error'], 'lease-not-owned-or-unreachable')

    def test_heartbeat_only_during_live_child(self):
        with patch.object(runner, '_lease_action', return_value=True) as action:
            result = self.run_child('import time; time.sleep(0.12)', heartbeat_seconds=0.03)
        self.assertTrue(result['ok'])
        actions = [call.args[0] for call in action.call_args_list]
        self.assertGreater(actions.count('heartbeat'), 1)
        self.assertEqual(actions[-1], 'release')
        self.assertEqual(actions.count('release'), 1)

    def test_lost_renewal_stops_child_before_late_write(self):
        marker = self.root / 'late'
        with patch.object(runner, '_lease_action', side_effect=[True, False, False]):
            result = self.run_child(f'import time; time.sleep(0.5); open({str(marker)!r}, "w").write("late")', heartbeat_seconds=0.03)
        time.sleep(0.55)
        self.assertFalse(marker.exists())
        self.assertEqual(result['error'], 'lease-lost-or-renewal-failed')

    def test_descendant_stopped_when_parent_exits(self):
        marker = self.root / 'orphan'
        child = f'import time; time.sleep(0.5); open({str(marker)!r}, "w").write("orphan")'
        body = f'import subprocess,sys; subprocess.Popen([sys.executable,"-c",{child!r}])'
        with patch.object(runner, '_lease_action', return_value=True):
            self.run_child(body)
        time.sleep(0.55)
        self.assertFalse(marker.exists())

    def test_sigterm_ignoring_child_is_killed(self):
        marker = self.root / 'ignored-term'
        body = f'import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(3); open({str(marker)!r}, "w").write("late")'
        with patch.object(runner, '_lease_action', side_effect=[True, False, False]):
            result = self.run_child(body, heartbeat_seconds=0.1)
        time.sleep(1.0)
        self.assertFalse(marker.exists())
        self.assertEqual(result['error'], 'lease-lost-or-renewal-failed')

    def test_database_action_is_bounded_and_sanitised(self):
        import subprocess
        with patch.object(runner.subprocess, 'run', side_effect=subprocess.TimeoutExpired('heartbeat', 20)) as run:
            self.assertFalse(runner._lease_action('heartbeat', self.receipt, 1800))
        self.assertEqual(run.call_args.kwargs['timeout'], 20)


if __name__ == '__main__': unittest.main()
