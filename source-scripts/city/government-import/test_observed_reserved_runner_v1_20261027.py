from contextlib import redirect_stdout
import io
import json
from types import SimpleNamespace
import subprocess
import unittest
from unittest.mock import patch

import observed_reserved_runner_v1_20261027 as runner


class FailClosedObservations(unittest.TestCase):
    def check(self, value=None, error=None):
        output = io.StringIO()
        with patch.object(runner.subprocess, 'run', return_value=value, side_effect=error) as call:
            with redirect_stdout(output):
                result = runner.observed_action('heartbeat', '/private/lease.json', 3600)
        record = json.loads(output.getvalue())
        self.assertNotIn('SECRET', output.getvalue())
        self.assertEqual(call.call_args.kwargs['timeout'], 120)
        self.assertEqual(call.call_count, 1, 'No automatic retry is permitted')
        return result, record

    def test_success(self):
        ok, record = self.check(SimpleNamespace(returncode=0, stdout='{"ok":true}', stderr='SECRET'))
        self.assertTrue(ok)
        self.assertTrue(record['ok'])

    def test_database_rejection_is_failure(self):
        ok, record = self.check(SimpleNamespace(returncode=0, stdout='{"ok":false}', stderr='SECRET'))
        self.assertFalse(ok)
        self.assertEqual(record['failureClass'], 'database-action-not-ok')

    def test_nonzero_never_prints_stderr_or_stdout(self):
        ok, record = self.check(SimpleNamespace(returncode=2, stdout='SECRET', stderr='SECRET'))
        self.assertFalse(ok)
        self.assertEqual(record['failureClass'], 'subprocess-nonzero')

    def test_timeout_is_failure(self):
        ok, record = self.check(error=subprocess.TimeoutExpired('SECRET', 120))
        self.assertFalse(ok)
        self.assertEqual(record['failureClass'], 'database-observation-timeout')

    def test_invalid_json_is_failure(self):
        ok, record = self.check(SimpleNamespace(returncode=0, stdout='SECRET', stderr='SECRET'))
        self.assertFalse(ok)
        self.assertEqual(record['failureClass'], 'invalid-action-json')

    def test_launch_failure_is_failure(self):
        ok, record = self.check(error=OSError('SECRET'))
        self.assertFalse(ok)
        self.assertEqual(record['failureClass'], 'subprocess-launch-error')


if __name__ == '__main__':
    unittest.main()
