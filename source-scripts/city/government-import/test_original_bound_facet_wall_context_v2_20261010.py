"""Finite source vertex exposure, grazing and adverse completeness tests."""
import unittest
from fractions import Fraction as F
import numpy as np
from original_bound_facet_wall_context_v2_20261010 import exposure_at_vertex
class FiniteVertex(unittest.TestCase):
 def test_distant_high_vertex_cannot_hide_actual_exposure(self):
  g=np.array([[[0,0,0],[10,10,0],[0,0,10]]],float);p=exposure_at_vertex([1,2,1],g);self.assertEqual(F(p['exactExposureLowerBoundM']),1)
 def test_all_overlapping_finite_surfaces_must_count(self):
  g=np.array([[[0,0,0],[10,0,0],[0,0,10]],[[0,3,0],[10,3,0],[0,3,10]]],float);p=exposure_at_vertex([1,2,1],g);self.assertEqual(F(p['exactExposureLowerBoundM']),-1)
 def test_exact_edge_ground_coverage(self):
  g=np.array([[[0,0,0],[1,0,0],[0,0,1]]],float);self.assertEqual(F(exposure_at_vertex([.5,1,.5],g)['exactExposureLowerBoundM']),1)
 def test_outside_grazing_cannot_get_tolerance_credit(self):
  g=np.array([[[0,0,0],[1,0,0],[0,0,1]]],float)
  with self.assertRaises(AssertionError):exposure_at_vertex([.5,1,np.nextafter(.5,1)],g)
 def test_collapsed_ground_high_endpoint_at_point_counts(self):
  g=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[.25,0,.25],[.25,3,.25],[.5,3,.5]]],float);self.assertEqual(F(exposure_at_vertex([.25,2,.25],g)['exactExposureLowerBoundM']),-1)
 def test_no_ground_coverage_rejected(self):
  with self.assertRaises(AssertionError):exposure_at_vertex([2,1,2],np.array([[[0,0,0],[1,0,0],[0,0,1]]],float))
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):exposure_at_vertex([0,float('nan'),0],np.array([[[0,0,0],[1,0,0],[0,0,1]]],float))
if __name__=='__main__':unittest.main()
