import json
import subprocess
import unittest
from types import SimpleNamespace
from observed_reserved_runner_v3_20261103 import bounded_action


class FencedRetryTests(unittest.TestCase):
    def run_case(self, replies):
        commands, sleeps = [], []
        def dispatch(command):
            commands.append(command[:])
            value = replies[len(commands) - 1]
            if isinstance(value, Exception): raise value
            return SimpleNamespace(returncode=0 if value.get('ok') else 1, stdout=json.dumps(value))
        ok = bounded_action('heartbeat', '/tmp/exact-lease.json', 3600, dispatch=dispatch, sleep=sleeps.append, emit=lambda text: None)
        self.assertTrue(all(c == commands[0] for c in commands))
        return ok, commands, sleeps

    def test_admin_shutdown_retries_same_fenced_action(self):
        ok, commands, sleeps = self.run_case([dict(ok=False, sqlstate='57P01'), dict(ok=True)])
        self.assertTrue(ok); self.assertEqual(len(commands), 2); self.assertEqual(sleeps, [2])
        self.assertIn('/tmp/exact-lease.json', commands[0]); self.assertNotIn('claim', commands[0])

    def test_lease_loss_is_immediate_even_with_transient_sqlstate(self):
        ok, commands, sleeps = self.run_case([dict(ok=False, leaseLost=True, sqlstate='57P01')])
        self.assertFalse(ok); self.assertEqual(len(commands), 1); self.assertEqual(sleeps, [])

    def test_retry_exhaustion_stops_after_three(self):
        ok, commands, sleeps = self.run_case([dict(ok=False, sqlstate='57P01')] * 3)
        self.assertFalse(ok); self.assertEqual(len(commands), 3); self.assertEqual(sleeps, [2, 5])

    def test_recovery_then_expired_token_still_fails(self):
        ok, commands, sleeps = self.run_case([dict(ok=False, sqlstate='57P03'), dict(ok=False, leaseLost=True)])
        self.assertFalse(ok); self.assertEqual(len(commands), 2)

    def test_unknown_failures_and_timeouts_do_not_retry(self):
        for reply in [dict(ok=False, sqlstate='23505'), dict(ok=False), subprocess.TimeoutExpired('action', 20)]:
            ok, commands, sleeps = self.run_case([reply])
            self.assertFalse(ok); self.assertEqual(len(commands), 1); self.assertEqual(sleeps, [])

    def test_unsafe_ttl_never_dispatches(self):
        self.assertFalse(bounded_action('heartbeat', 'lease', 60, dispatch=lambda c: self.fail('must not dispatch')))


if __name__ == '__main__':
    unittest.main()
