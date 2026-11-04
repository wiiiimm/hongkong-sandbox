import unittest
from fractions import Fraction as F
import numpy as np
from exact_original_projection_coverage_20261009 import exact_coverage as old,subtract as old_subtract
from exact_original_projection_coverage_v2_20261010 import exact_coverage as new,subtract as new_subtract
class ExactPruning(unittest.TestCase):
 def compare(self,face,ground):self.assertEqual(old(np.asarray(face,float),np.asarray(ground,float)),new(np.asarray(face,float),np.asarray(ground,float)))
 def test_strict_disjoint_positive_polygon(self):
  p=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))];q=[(F(2),F(2)),(F(3),F(2)),(F(2),F(3))]
  self.assertEqual(new_subtract(p,q),[p]);self.assertEqual(sum(abs(__import__('exact_original_projection_coverage_20261009').signed_area(x)) for x in old_subtract(p,q)),F(1,2))
 def test_touching_bounds_no_shortcut(self):
  p=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))];q=[(F(1),F(0)),(F(2),F(0)),(F(1),F(1))];self.assertEqual(old_subtract(p,q),new_subtract(p,q))
 def test_arbitrarily_small_actual_overlap_retained(self):
  e=F(1,2**80);p=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))];q=[(F(1)-e,F(0)),(F(2),F(0)),(F(1)-e,F(1))];self.assertEqual(old_subtract(p,q),new_subtract(p,q))
 def test_area_union_same_ground_order(self):self.compare([[0,2,0],[2,2,0],[0,2,2]],[[[0,0,0],[2,0,0],[2,0,2]],[[0,0,0],[2,0,2],[0,0,2]]])
 def test_reversed_winding(self):self.compare([[0,2,0],[0,2,2],[2,2,0]],[[[0,0,0],[2,0,2],[2,0,0]],[[0,0,0],[0,0,2],[2,0,2]]])
 def test_real_area_hole_rejects(self):self.compare([[0,2,0],[2,2,0],[0,2,2]],[[[0,0,0],[1,0,0],[0,0,1]]])
 def test_point_and_vertical_projection_preserved(self):
  g=[[[0,0,0],[2,0,0],[0,0,2]]]
  self.compare([[.5,0,.5],[.5,1,.5],[.5,2,.5]],g);self.compare([[0,0,0],[1,1,1],[1,2,1]],g)
 def test_interval_gap_preserved(self):self.compare([[0,0,0],[2,1,0],[2,2,0]],[[[0,0,0],[.5,0,0],[0,0,1]],[[1,0,0],[2,0,0],[2,0,1]]])
if __name__=='__main__':unittest.main()
