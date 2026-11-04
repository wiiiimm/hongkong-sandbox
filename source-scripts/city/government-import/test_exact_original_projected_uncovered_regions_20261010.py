import unittest,numpy as np
from fractions import Fraction as F
from exact_original_projected_uncovered_regions_20261010 import diagnose
from exact_original_projection_coverage_v2_20261010 import exact_coverage
class Tests(unittest.TestCase):
 def face(self):return np.array([[0.,1.,0.],[1.,1.,0.],[0.,1.,1.]])
 def ground(self,x0=0,x1=1):return np.array([[[x0,0,0],[x1,0,0],[x0,0,1]],[[x1,0,0],[x1,0,1],[x0,0,1]]])
 def test_exact_closed_coverage_no_gap(self):self.assertTrue(diagnose(self.face(),self.ground())['exactProjectionCovered'])
 def test_area_positive_hole_retained(self):
  r=diagnose(self.face(),self.ground(0,.25));self.assertFalse(r['exactProjectionCovered']);self.assertTrue(r['allExactUncoveredRegions']);self.assertGreater(F(r['exactUncoveredAreaOrParameterAmount']),0)
 def test_tiny_genuine_gap_not_waived(self):
  r=diagnose(self.face(),self.ground(0,1-1e-12));self.assertGreater(F(r['exactUncoveredAreaOrParameterAmount']),0)
 def test_interval_all_two_gap_regions(self):
  face=np.array([[0,1,.1],[1,1,.1],[.5,2,.1]],float);r=diagnose(face,np.concatenate([self.ground(.1,.2),self.ground(.5,.8)]));self.assertEqual(len(r['allExactUncoveredRegions']),3)
 def test_point_gap_explicit(self):self.assertEqual(diagnose(np.array([[2,1,2]]*3),self.ground())['method'],'exact-point-gap')
 def test_point_inside_nonzero_ground(self):self.assertTrue(diagnose(np.array([[.1,1,.1]]*3),self.ground())['exactProjectionCovered'])
 def test_collapsed_ground_no_height_field_coverage(self):
  r=diagnose(self.face(),np.array([[[0,0,0],[0,1,0],[0,0,1]]],float));self.assertFalse(r['exactProjectionCovered'])
 def test_old_exact_coverage_agrees(self):
  for g in [self.ground(),self.ground(0,.25),self.ground(0,1-1e-12)]:self.assertEqual(diagnose(self.face(),g)['exactProjectionCovered'],exact_coverage(self.face(),g)['exactProjectionCovered'])
if __name__=='__main__':unittest.main()
