import copy
import unittest
from ocean_coordinated_full_browser_v2_20261027 import verify_atomic,ATOMIC
from run import ROOT,HERE,read
class AtomicCompositionTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.saved=read(ROOT/'docs/astra-city/government-import'/ATOMIC/'report.json');cls.models=read(HERE/'local/government-xl-ocean-four-atomic-lifecycle-stage-v1-20261027/catalogue.json')['models']
 def test_actual_complete_five_case_evidence(self):self.assertTrue(verify_atomic(self.saved,self.models))
 def test_missing_peer_failure_rejected(self):
  x=copy.deepcopy(self.saved);x['cases'].pop()
  with self.assertRaises(AssertionError):verify_atomic(x,self.models)
 def test_wrong_source_bytes_rejected(self):
  x=copy.deepcopy(self.saved);x['cases'][0]['sources'][0]['sha256']='0'*64
  with self.assertRaises(AssertionError):verify_atomic(x,self.models)
 def test_partial_group_transition_rejected(self):
  x=copy.deepcopy(self.saved);x['cases'][0]['audit']['transitions'].append(dict(active=[self.models[0]['uid']]))
  with self.assertRaises(AssertionError):verify_atomic(x,self.models)
 def test_failure_without_basics_rejected(self):
  x=copy.deepcopy(self.saved);x['cases'][1]['failureKeptAllBasics']=False
  with self.assertRaises(AssertionError):verify_atomic(x,self.models)
 def test_collision_map_violation_rejected(self):
  x=copy.deepcopy(self.saved);x['cases'][0]['audit']['violations'].append(dict(kind='stale-fallback-collision-map'))
  with self.assertRaises(AssertionError):verify_atomic(x,self.models)
if __name__=='__main__':unittest.main()
