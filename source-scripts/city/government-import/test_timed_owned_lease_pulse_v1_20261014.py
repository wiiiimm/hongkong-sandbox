import unittest
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
class Tests(unittest.TestCase):
    def setup_pulse(self):
        state=dict(now=0,owned=True,heartbeat=True,ownsCalls=0,heartbeatCalls=0)
        def owns():state['ownsCalls']+=1;return state['owned']
        def heartbeat():state['heartbeatCalls']+=1;return dict(ok=state['heartbeat'])
        return state,TimedOwnedLeasePulse(owns,heartbeat,clock=lambda:state['now'])
    def test_thousand_refs_have_only_mandatory_entry_exit_calls(self):
        s,p=self.setup_pulse();p(force=True)
        for _ in range(1000):p()
        p(force=True);self.assertEqual(s['ownsCalls'],2);self.assertEqual(s['heartbeatCalls'],0)
    def test_exact20seconds_owns_and_heartbeat_once(self):
        s,p=self.setup_pulse();s['now']=19.999;p();self.assertEqual(s['ownsCalls'],0);s['now']=20;p();self.assertEqual((s['ownsCalls'],s['heartbeatCalls']),(1,1));p();self.assertEqual((s['ownsCalls'],s['heartbeatCalls']),(1,1));s['now']=40;p();self.assertEqual((s['ownsCalls'],s['heartbeatCalls']),(2,2))
    def test_force_checks_do_not_mask_due_heartbeat(self):
        s,p=self.setup_pulse();s['now']=10;p(force=True);s['now']=20;p(force=True);self.assertEqual((s['ownsCalls'],s['heartbeatCalls']),(2,1))
    def test_lost_lease_fails_at_interval_before_renewal(self):
        s,p=self.setup_pulse();s.update(now=20,owned=False)
        with self.assertRaisesRegex(AssertionError,'not owned'):p()
        self.assertEqual(s['heartbeatCalls'],0)
    def test_lost_lease_fails_at_mandatory_exit_even_before20seconds(self):
        s,p=self.setup_pulse();p(force=True);s.update(now=1,owned=False)
        with self.assertRaisesRegex(AssertionError,'not owned'):p(force=True)
        self.assertEqual(s['heartbeatCalls'],0)
    def test_failed_heartbeat_fails_closed_without_advancing_clock(self):
        s,p=self.setup_pulse();s.update(now=20,heartbeat=False)
        with self.assertRaisesRegex(AssertionError,'heartbeat failed'):p()
        self.assertEqual(p.last_heartbeat,0)
if __name__=='__main__':unittest.main()
