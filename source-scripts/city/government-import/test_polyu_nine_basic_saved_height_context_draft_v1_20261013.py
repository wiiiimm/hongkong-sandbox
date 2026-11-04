"""Unexecuted exact closed-projection scheduling/context cases."""
import unittest
from fractions import Fraction as F
import polyu_nine_basic_saved_height_context_draft_v1_20261013 as m
class Closed(unittest.TestCase):
 def test_triangle_boundary_retained(self):self.assertTrue(m.complete_closed_projection_member((F(1),F(0)),[(0,2,0),(2,2,0),(0,2,2)]))
 def test_outside_projection_rejected(self):self.assertFalse(m.complete_closed_projection_member((F(3),F(0)),[(0,2,0),(2,2,0),(0,2,2)]))
 def test_vertical_segment_and_point_retained_without_height(self):
  t=[(0,0,0),(0,2,0),(0,2,2)];self.assertTrue(m.complete_closed_projection_member((F(0),F(1)),t));self.assertIsNone(m.exact_plane_height((F(0),F(1)),t));self.assertFalse(m.complete_closed_projection_member((F(1),F(1)),t))
 def test_zero_projected_point_no_false_bridge(self):
  t=[(0,0,0),(0,1,0),(0,2,0)];self.assertTrue(m.complete_closed_projection_member((F(0),F(0)),t));self.assertFalse(m.complete_closed_projection_member((F(0),F(1)),t))
 def test_original_plane_fraction_and_winding(self):
  t=[(0,0,0),(2,2,0),(0,4,2)];p=(F(1,2),F(1,2));self.assertEqual(m.exact_plane_height(p,t),F(3,2));self.assertEqual(m.exact_plane_height(p,t[::-1]),F(3,2))
if __name__=='__main__':unittest.main(verbosity=2)
