import unittest
from fractions import Fraction as F
from west_kowloon_auxiliary_basic_interface_band_v1_20261027 import distance_squared, finite_host_bound

class FiniteInterface(unittest.TestCase):
 def test_exact_fraction_interior_distance(self):
  self.assertEqual(distance_squared(['1/2','1/3',0],[0,0,0],[1,0,0]),(F(1,9),F(1,2)))
 def test_no_infinite_line_extrapolation(self):
  self.assertEqual(distance_squared([2,0,0],[0,0,0],[1,0,0]),(F(1),F(1)))
 def test_positive_finite_host_required(self):
  with self.assertRaises(AssertionError):distance_squared([0,0,0],[0,0,0],[0,0,0])
 def test_all_contact_vertices_are_bounded(self):
  contact=dict(exactPoints=[[0,0,0],[1,1,0]])
  hosts=[(4,dict(dimension=1,exactPoints=[[0,0,0],[1,0,0]]))]
  r=finite_host_bound(contact,hosts);self.assertEqual(r['exactMaximumEndpointDistanceSquaredM2'],'1');self.assertFalse(r['thresholdApplied'])

if __name__=='__main__':unittest.main()
