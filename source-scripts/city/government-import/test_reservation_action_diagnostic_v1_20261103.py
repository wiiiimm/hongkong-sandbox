"""Renewal diagnostics must expose no secrets and never convert failures to success."""
import io,json,subprocess,unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch
import reservation_action_diagnostic_v1_20261103 as action
import observed_reserved_runner_v2_20261103 as runner


class Diagnostics(unittest.TestCase):
    def test_heartbeat_once_with_original_ttl(self):
        with patch.object(action.reservations,'heartbeat',return_value={'ok':True}) as call:
            self.assertTrue(action.action_result('heartbeat',{'token':'private'},3600)['ok'])
        call.assert_called_once_with({'token':'private'},3600)
    def test_lost_lease_stays_false(self):
        with patch.object(action.reservations,'heartbeat',return_value={'ok':False,'error':'lease-lost'}):
            r=action.action_result('heartbeat',{},3600);self.assertFalse(r['ok']);self.assertTrue(r['leaseLost'])
    def test_exception_class_without_secret_text(self):
        class DatabaseError(Exception): sqlstate='08006'
        with patch.object(action.reservations,'heartbeat',side_effect=DatabaseError('SECRET_CONNECTION_URI')) as call:
            r=action.action_result('heartbeat',{},3600)
        self.assertFalse(r['ok']);self.assertEqual(r['sqlstate'],'08006');self.assertNotIn('SECRET',json.dumps(r));call.assert_called_once()
    def test_release_once(self):
        with patch.object(action.reservations,'release',return_value={'ok':True}) as call:
            self.assertTrue(action.action_result('release',{},3600)['ok'])
        call.assert_called_once_with({})
    def run_action(self,result=None,error=None):
        out=io.StringIO()
        with patch.object(runner.subprocess,'run',return_value=result,side_effect=error) as call,redirect_stdout(out):
            ok=runner.observed_action('heartbeat','/tmp/lease',3600)
        call.assert_called_once();self.assertEqual(call.call_args.kwargs['timeout'],120)
        return ok,out.getvalue()
    def test_nonzero_cannot_pass(self):
        ok,output=self.run_action(SimpleNamespace(returncode=1,stdout='{"ok":true}',stderr='SECRET'))
        self.assertFalse(ok);self.assertNotIn('SECRET',output)
    def test_zero_with_false_cannot_pass(self):
        ok,_=self.run_action(SimpleNamespace(returncode=0,stdout='{"ok":false}',stderr=''));self.assertFalse(ok)
    def test_invalid_json_cannot_pass_or_leak(self):
        ok,output=self.run_action(SimpleNamespace(returncode=0,stdout='SECRET',stderr='SECRET'))
        self.assertFalse(ok);self.assertNotIn('SECRET',output)
    def test_observation_timeout_stays_failure(self):
        ok,_=self.run_action(error=subprocess.TimeoutExpired('safe',120));self.assertFalse(ok)
    def test_success_still_requires_zero_and_true(self):
        ok,_=self.run_action(SimpleNamespace(returncode=0,stdout='{"ok":true}',stderr=''));self.assertTrue(ok)


if __name__=='__main__':unittest.main()
