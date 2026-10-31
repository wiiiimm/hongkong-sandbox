import copy,hashlib,json,unittest
import numpy as np
from original_strict_clear_cap_wall_paths_20261009 import verify
class ClearCapPaths(unittest.TestCase):
 def fixture(self):
  # Buried lower wall -> clear downward cap -> exposed upward roof.
  t=np.array([[[0,-1,0],[0,1,0],[1,1,0]],[[0,1,0],[1,1,0],[0,1,1]],[[0,1,1],[1,1,1],[1,1,0]]],float)
  c=[dict(sourceFace=i,groundProjectionCovered=True,minimum=dict(minimumGapM=g),maximumObservedGapM=m) for i,(g,m) in enumerate([(-1,1),(.2,.2),(.2,.2)])]
  b=dict(completeOriginalWorldTrianglesSHA256=hashlib.sha256(t.tobytes()).hexdigest())
  return t,c,b
 def binding(self,t,c,b,contacts=()):
  canonical=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
  return {**b,'completeCurrentFacetContextsSHA256':canonical(c),'exactOriginalContactListSHA256':canonical(list(contacts))}
 def call(self,t,c,b,contacts=()):
  bound=self.binding(t,c,b,contacts);return verify(t,c,contacts,expected_binding=bound,current_binding=bound)
 def test_original_clear_downward_cap_bridges(self):
  t,c,b=self.fixture();r=self.call(t,c,b);self.assertTrue(r['allAffectedHavePaths']);self.assertEqual(r['paths'][0]['originalPath'],[0,1,2]);self.assertFalse(r['groundRootCredit']);self.assertFalse(r['burialRoleAccepted'])
 def test_buried_downward_cap_rejected(self):
  t,c,b=self.fixture();c[1]['minimum']['minimumGapM']=-.5001
  with self.assertRaises(AssertionError):self.call(t,c,b)
 def test_buried_upward_roof_rejected(self):
  t,c,b=self.fixture();c[2]['minimum']['minimumGapM']=-.5001
  with self.assertRaises(AssertionError):self.call(t,c,b)
 def test_detached_wall_no_path(self):
  t,c,b=self.fixture();t[0,:,0]+=10;b['completeOriginalWorldTrianglesSHA256']=hashlib.sha256(t.tobytes()).hexdigest();self.assertFalse(self.call(t,c,b)['allAffectedHavePaths'])
 def test_missing_ground_rejected(self):
  t,c,b=self.fixture();c[1]['groundProjectionCovered']=False
  with self.assertRaises(AssertionError):self.call(t,c,b)
 def test_source_changed_rejected(self):
  t,c,b=self.fixture();t[0,0,1]-=.001
  with self.assertRaises(AssertionError):self.call(t,c,b)
 def test_missing_face_rejected(self):
  t,c,b=self.fixture()
  with self.assertRaises(AssertionError):self.call(t,c[:2],b)
 def test_repeated_face_rejected(self):
  t,c,b=self.fixture();c[1]['sourceFace']=0
  with self.assertRaises(AssertionError):self.call(t,c,b)
 def test_point_contact_rejected(self):
  t,c,b=self.fixture();t[0]=[[0,1,0],[-1,-1,0],[-1,1,0]];b['completeOriginalWorldTrianglesSHA256']=hashlib.sha256(t.tobytes()).hexdigest()
  with self.assertRaisesRegex(AssertionError,'Point-only'):self.call(t,c,b,[[0,1]])
 def test_positive_contact_replayed(self):
  t,c,b=self.fixture();r=self.call(t,c,b,[[0,1]]);self.assertEqual(r['replayedOriginalContacts'][0]['dimension'],1)
 def test_duplicate_contact_rejected(self):
  t,c,b=self.fixture()
  with self.assertRaises(AssertionError):self.call(t,c,b,[[0,1],[1,0]])
 def test_bad_contact_indices_rejected(self):
  t,c,b=self.fixture()
  for contacts in [[[0,1.0]],[[0,4]],[[True,1]]]:
   with self.assertRaises(AssertionError):self.call(t,c,b,contacts)
 def test_raw_fully_buried_wall_exposure_retained(self):
  t,c,b=self.fixture();c[0]['maximumObservedGapM']=-.2;r=self.call(t,c,b);self.assertTrue(r['allAffectedHavePaths']);self.assertEqual(r['rawExposureFailures'],[0]);self.assertFalse(r['fullAcceptance'])
 def test_context_changed_rejected(self):
  t,c,b=self.fixture()
  with self.assertRaises(AssertionError):verify(t,c,[],expected_binding={**b,'currentGroundSHA256':'a'*64},current_binding={**b,'currentGroundSHA256':'b'*64})
 def test_clearance_mutated_without_new_context_binding_rejected(self):
  t,c,b=self.fixture();bound=self.binding(t,c,b);c[1]['minimum']['minimumGapM']+=.01
  with self.assertRaisesRegex(AssertionError,'contexts differ'):verify(t,c,[],expected_binding=bound,current_binding=bound)
 def test_exposure_mutated_without_new_context_binding_rejected(self):
  t,c,b=self.fixture();bound=self.binding(t,c,b);c[0]['maximumObservedGapM']+=.01
  with self.assertRaisesRegex(AssertionError,'contexts differ'):verify(t,c,[],expected_binding=bound,current_binding=bound)
 def test_contact_inventory_mutated_without_new_binding_rejected(self):
  t,c,b=self.fixture();bound=self.binding(t,c,b)
  with self.assertRaisesRegex(AssertionError,'contact inventory differs'):verify(t,c,[[0,1]],expected_binding=bound,current_binding=bound)
 def test_ground_coverage_requires_true_boolean(self):
  t,c,b=self.fixture();c[1]['groundProjectionCovered']=1
  with self.assertRaises(AssertionError):self.call(t,c,b)
if __name__=='__main__':unittest.main()
