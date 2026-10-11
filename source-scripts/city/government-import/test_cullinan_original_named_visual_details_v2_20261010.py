import unittest,copy,importlib.util
from pathlib import Path
import numpy as np
from cullinan_original_named_visual_details_v2_20261010 import verify,sha,canonical
class ActualFixture(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=Path(__file__).with_name('xl-terrain-recovery-20261010-cullinan-west-three-named-original-visual-details-v2.py');s=importlib.util.spec_from_file_location('actual',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);cls.data=m.fixture()
 def run_proof(self,o=None,l=None,f=None,g=None,c=None,b=None):
  a,z,w,x,y,v,_=self.data;return verify(a if o is None else o,z if l is None else l,w if f is None else f,x if g is None else g,frozen_context=y if c is None else c,expected_binding=v,current_binding=v if b is None else b)
 def test_actual_all_three_source_literal_float32(self):self.assertEqual(len(self.run_proof()['rows']),9)
 def test_free_slanted_front_extreme_is_preserved(self):
  o=self.data[0];self.assertLess(o[153582,2,1],o[153582,0,1]);self.assertTrue(self.run_proof()['proposalVerified'])
 def test_changed_source_pose_rejected_even_with_matching_supplied_hash(self):
  o=self.data[0].copy();o[153546]+=[0,0,.01];b=copy.deepcopy(self.data[5]);b['originalWorldSHA256']=sha(o)
  with self.assertRaises(AssertionError):self.run_proof(o=o,b=b)
 def test_face_omission_rejected(self):
  with self.assertRaises(AssertionError):self.run_proof(o=self.data[0][:-1])
 def test_duplicate_winding_change_rejected(self):
  o=self.data[0].copy();o[134580]=o[134580,::-1]
  with self.assertRaises(AssertionError):self.run_proof(o=o)
 def test_changed_literal_host_rejected(self):
  l=self.data[1].copy();l[148749]+=[0,0,.2]
  with self.assertRaises(AssertionError):self.run_proof(l=l)
 def test_float32_projection_changed_rejected(self):
  f=self.data[2].copy();f[153546,0,0]+=.001
  with self.assertRaises(AssertionError):self.run_proof(f=f)
 def test_unrooted_host_rejected(self):
  g=copy.deepcopy(self.data[3]);g['resolvedOriginalComponents'].remove(279)
  with self.assertRaises(AssertionError):self.run_proof(g=g)
 def test_detail_cannot_root_or_bridge(self):
  g=copy.deepcopy(self.data[3]);g['resolvedOriginalComponents'].append(294)
  with self.assertRaises(AssertionError):self.run_proof(g=g)
 def test_changed_actual_ground_receipt_rejected(self):
  c=copy.deepcopy(self.data[4]);c['literalRootProofs'][0]['completeDrawnGroundSHA256']='0'*64
  with self.assertRaises(AssertionError):self.run_proof(c=c)
 def test_omitted_actual_root_rejected(self):
  c=copy.deepcopy(self.data[4]);c['literalRootProofs']=c['literalRootProofs'][:1]
  with self.assertRaises(AssertionError):self.run_proof(c=c)
 def test_native_legacy_reacceptance_never_granted(self):
  r=self.run_proof();self.assertFalse(r['nativeReacceptance']);self.assertFalse(r['fullAcceptance']);self.assertEqual(r['addedGroundRoots'],[]);self.assertEqual(r['addedLoadBearingEdges'],[]);self.assertFalse(r['visualDetailsCanSupportOthers'])
if __name__=='__main__':unittest.main()
