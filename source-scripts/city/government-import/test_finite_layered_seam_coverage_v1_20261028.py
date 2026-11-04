import unittest
from fractions import Fraction as F
from finite_layered_seam_coverage_v1_20261028 import bidirectional_layer_coverage as verify

def segment(a,b,y0,y1=None,face=0):return tuple(map(F,[a,b,y0,y0 if y1 is None else y1]))+(face,)
class LayerCoverageTests(unittest.TestCase):
 def test_matching_lower_layers_and_duplicates(self):
  self.assertTrue(verify([segment(0,1,0),segment(0,1,10)],[segment(0,1,10),segment(0,1,0),segment(0,1,0)])['passed'])
 def test_same_upper_surface_cannot_hide_missing_lower_layer(self):
  self.assertFalse(verify([segment(0,1,0),segment(0,1,10)],[segment(0,1,10)])['passed'])
 def test_matched_endpoints_cannot_hide_interior_gap(self):
  self.assertFalse(verify([segment(0,1,0)],[segment(0,F(1,4),0),segment(F(3,4),1,0)])['passed'])
 def test_isolated_spike_requires_finite_mate(self):
  self.assertFalse(verify([segment(0,1,0),segment(F(1,2),F(1,2),3)],[segment(0,1,0)])['passed'])
 def test_exact_threshold_and_rejection_above_it(self):
  self.assertTrue(verify([segment(0,1,0)],[segment(0,1,F(999,100000))])['passed'])
  self.assertFalse(verify([segment(0,1,0)],[segment(0,1,F(1,100))])['passed'])
  self.assertFalse(verify([segment(0,1,0)],[segment(0,1,F(101,10000))])['passed'])
 def test_piecewise_coverage_joins_without_gap(self):
  self.assertTrue(verify([segment(0,1,0,1)],[segment(0,F(1,2),0,F(1,2)),segment(F(1,2),1,F(1,2),1)])['passed'])
 def test_cannot_raise_tolerance(self):
  with self.assertRaises(AssertionError):verify([segment(0,1,0)],[segment(0,1,0)],F(1,99))
if __name__=='__main__':unittest.main()
