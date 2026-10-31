import unittest
from villa_canopy_exact_projection_separation_v2_20261015 import separate,integerize
class SeparationTests(unittest.TestCase):
 def test_contained_triangle_is_not_clear(self):
  self.assertFalse(separate([(0,0),(10,0),(0,10)],[(1,1),(2,1),(1,2)]))
 def test_edge_touch_is_not_strictly_clear(self):
  self.assertFalse(separate([(0,0),(2,0),(0,2)],[(2,0),(3,0),(2,1)]))
 def test_crossed_zero_area_walls_are_not_clear(self):
  self.assertFalse(separate([(0,0),(2,2),(1,1)],[(0,2),(2,0),(1,1)]))
 def test_collinear_disjoint_walls_clear(self):
  self.assertTrue(separate([(0,0),(1,1),(0,0)],[(2,2),(3,3),(2,2)]))
 def test_overlapping_boxes_but_separated_triangles(self):
  self.assertTrue(separate([(0,0),(3,0),(0,3)],[(3,3),(3,1),(1,3)]))
 def test_tiny_exact_gap_at_large_origin(self):
  k=2**60;a=[(k,k),(k+3,k),(k,k+3)];b=[(k+4,k),(k+7,k),(k+4,k+3)];self.assertTrue(separate(a,b));self.assertTrue(separate(b,a))
 def test_exact_dyadic_conversion(self):
  self.assertEqual(integerize([[(.5,.25),(1.,-.5),(0.,0.)]],4),[[(2,1),(4,-2),(0,0)]])
if __name__=='__main__':unittest.main()
