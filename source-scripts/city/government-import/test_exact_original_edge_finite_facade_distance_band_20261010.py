import unittest
import numpy as np
from exact_original_edge_finite_facade_distance_band_20261010 import verify
class Tests(unittest.TestCase):
 def wall(self):return np.array([[[0,0,0],[0,1,0],[0,1,1]],[[0,0,0],[0,1,1],[.00001,0,1]]],float)
 def passed(self,line,tri):return verify(line,tri)['verifiedCompleteOriginalEdgeFiniteFacadeBand']
 def test_shared_edge_fold(self):self.assertTrue(self.passed([[.001,0,.001],[.001,1,.999]],self.wall()))
 def test_original_edge_at_limit(self):self.assertTrue(self.passed([[.1,0,0],[.1,1,0]],self.wall()))
 def test_next_float_beyond_limit(self):self.assertFalse(self.passed([[np.nextafter(.1,1),0,0],[np.nextafter(.1,1),1,0]],self.wall()[:1]))
 def test_finite_vertex_branch(self):self.assertTrue(self.passed([[0,-.05,-.05],[0,-.04,-.04]],self.wall()))
 def test_finite_vertex_far(self):self.assertFalse(self.passed([[0,-.08,-.08],[0,-.09,-.09]],self.wall()))
 def test_finite_edge_extension_not_infinite(self):self.assertFalse(self.passed([[0,1.2,0],[0,1.3,0]],self.wall()))
 def test_partial_only_rejects(self):self.assertFalse(self.passed([[0,0,0],[0,2,0]],self.wall()))
 def test_roof_no_facade(self):self.assertFalse(self.passed([[0,0,0],[1,0,1]],self.wall()[:,:,[1,0,2]]))
 def test_degenerate_line_no_credit(self):self.assertFalse(self.passed([[0,0,0],[0,1,0]],np.array([[[0,0,0],[0,1,0],[0,2,0]]])))
 def test_no_acceptance(self):
  r=verify([[0,0,0],[0,1,0]],self.wall());self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['visualRoleAccepted']);self.assertFalse(r['installationApproved'])
 def test_nonfinite(self):
  with self.assertRaises(AssertionError):verify([[float('inf'),0,0],[0,1,0]],self.wall())
if __name__=='__main__':unittest.main()
