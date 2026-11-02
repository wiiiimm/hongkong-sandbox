import subprocess,sys,unittest
from reattach_owned_process_supervisor_v1_20261103 import process_identity,same_process,stop_exact

class ConcreteProcessSupervision(unittest.TestCase):
    def setUp(self):
        self.child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],start_new_session=True)
        self.addCleanup(self.cleanup)
        self.identity=process_identity(self.child.pid)
    def cleanup(self):
        if self.child.poll()is None:self.child.kill()
        self.child.wait()
    def test_exact_process_matches(self):self.assertTrue(same_process(process_identity(self.child.pid),self.identity))
    def test_reused_pid_start_time_rejected(self):
        other={**self.identity,'startTicks':self.identity['startTicks']+1};self.assertFalse(same_process(process_identity(self.child.pid),other))
    def test_changed_command_rejected_without_signalling(self):
        other={**self.identity,'argv':['wrong']};stop_exact(other,grace=.1);self.assertIsNone(self.child.poll())
    def test_changed_session_rejected_without_signalling(self):
        other={**self.identity,'sid':self.identity['sid']+1};stop_exact(other,grace=.1);self.assertIsNone(self.child.poll())
    def test_stop_exact_process_group(self):
        stop_exact(self.identity,grace=.5);self.child.wait(timeout=2);self.assertIsNone(process_identity(self.child.pid))
    def test_missing_process_is_not_same(self):self.assertFalse(same_process(None,self.identity))

if __name__=='__main__':unittest.main()
