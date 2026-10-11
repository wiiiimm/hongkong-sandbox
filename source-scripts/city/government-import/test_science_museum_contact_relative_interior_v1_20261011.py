"""Exact source face interior adverse tests; no solid-penetration approval."""
import unittest
from fractions import Fraction as F
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
class Interior(unittest.TestCase):
 def setUp(self):self.face=((F(0),F(0),F(0)),(F(2),F(0),F(0)),(F(0),F(2),F(0)))
 def test_strict_interior(self):self.assertTrue(relative_interior(self.face,(F(1,2),F(1,2),F(0))))
 def test_edge_only_not_interior(self):self.assertFalse(relative_interior(self.face,(F(1),F(1),F(0))))
 def test_point_only_not_interior(self):self.assertFalse(relative_interior(self.face,self.face[0]))
 def test_off_plane_not_interior(self):self.assertFalse(relative_interior(self.face,(F(1,2),F(1,2),F(1,1000000))))
 def test_outside_rejected(self):self.assertFalse(relative_interior(self.face,(F(3),F(1),F(0))))
 def test_reversed_winding_same_interior(self):self.assertTrue(relative_interior(tuple(reversed(self.face)),(F(1,2),F(1,2),F(0))))
if __name__=='__main__':unittest.main()
