"""Original callable identity and real dynamic-import proxy recursion boundary."""
import importlib,sys,unittest
from types import SimpleNamespace
from unittest.mock import patch
import exact_cell_replay_with_original_routed_callable_20261011 as replay
class Tests(unittest.TestCase):
 def test_original_callable_passes(self):self.assertTrue(replay.require_original_callable(replay.ORIGINAL_ROUTED_VERIFY))
 def test_named_self_call_rejected(self):
  def recursive(row,context,local):return replay.verify_files(row,context,local,routed_verifier=recursive)
  with self.assertRaises(AssertionError):replay.require_original_callable(recursive)
 def test_lambda_wrapper_rejected(self):
  with self.assertRaises(AssertionError):replay.require_original_callable(lambda *a:replay.ORIGINAL_ROUTED_VERIFY(*a))
 def test_different_function_same_module_claim_rejected(self):
  def other(*args):pass
  other.__module__='routed_original_cell_identity'
  with self.assertRaises(AssertionError):replay.require_original_callable(other)
 def test_missing_callback_rejected(self):
  with self.assertRaises(AssertionError):replay.require_original_callable(None)
 def test_dynamic_proxy_cannot_replace_captured_original(self):
  prior=sys.modules['routed_original_cell_identity'];counter=[]
  def proxy(*args):counter.append(True);return replay.verify_files(*args,routed_verifier=proxy)
  try:
   sys.modules['routed_original_cell_identity']=SimpleNamespace(verify_files=proxy)
   self.assertIs(importlib.import_module('routed_original_cell_identity').verify_files,proxy)
   self.assertTrue(replay.require_original_callable(replay.ORIGINAL_ROUTED_VERIFY))
   with self.assertRaises(AssertionError):replay.require_original_callable(importlib.import_module('routed_original_cell_identity').verify_files)
   self.assertEqual(counter,[])
  finally:sys.modules['routed_original_cell_identity']=prior
 def test_changed_original_module_hash_rejected(self):
  with patch.object(replay,'ORIGINAL_ROUTED_SHA','0'*64):
   with self.assertRaises(AssertionError):replay.require_original_callable(replay.ORIGINAL_ROUTED_VERIFY)
if __name__=='__main__':unittest.main()
