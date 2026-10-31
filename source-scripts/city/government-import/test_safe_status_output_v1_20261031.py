"""Exercise real closed OS pipes, normal output and non-pipe failures."""
import subprocess,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent

class SafeStatusTests(unittest.TestCase):
    def run_child(self,code):
        return subprocess.run([sys.executable,'-c',code],cwd=HERE,capture_output=True,text=True)
    def test_normal_output_retained(self):
        p=self.run_child("from safe_status_output_v1_20261031 import status; assert status('installed') is True")
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(p.stdout,'installed\n')
    def test_closed_pipe_does_not_fail_completed_work_or_exit_flush(self):
        code="import os,sys; from safe_status_output_v1_20261031 import status; r,w=os.pipe(); os.close(r); os.dup2(w,sys.stdout.fileno()); os.close(w); completed=True; assert status('completed') is False; assert completed; status('later status')"
        p=self.run_child(code);self.assertEqual(p.returncode,0,p.stderr)
    def test_real_failures_are_not_hidden(self):
        code="import sys; from safe_status_output_v1_20261031 import status\nclass Bad:\n def write(self,s):raise RuntimeError('real-error')\n def flush(self):pass\nsys.stdout=Bad()\ntry:status('x')\nexcept RuntimeError as e:assert str(e)=='real-error'\nelse:raise AssertionError('error hidden')"
        p=self.run_child(code);self.assertEqual(p.returncode,0,p.stderr)

if __name__=='__main__':unittest.main()
