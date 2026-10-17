import unittest
from fractions import Fraction as F
from exact_original_boundary_vertical_join_feasibility_v1_20261011 import nominate
class JoinTests(unittest.TestCase):
 def test_positive_gap(self):
  r=nominate((0,0,0),(1,0,0),(0,1,0),(1,1,0));self.assertEqual(len(r['allPositiveGeneratedJoinFaces']),2)
 def test_zero_gap_no_area(self):
  r=nominate((0,0,0),(1,0,0),(0,0,0),(1,0,0));self.assertFalse(r['allPositiveGeneratedJoinFaces'])
 def test_one_equal_corner(self):
  r=nominate((0,0,0),(1,0,0),(0,0,0),(1,1,0));self.assertEqual(len(r['allPositiveGeneratedJoinFaces']),1)
 def test_tiny_gap_retained(self):
  r=nominate((0,0,0),(1,0,0),(0,F(1,2**100),0),(1,F(1,2**100),0));self.assertEqual(r['exactEndpointHeightGaps'],[F(1,2**100)]*2);self.assertEqual(len(r['allPositiveGeneratedJoinFaces']),2)
 def test_crossing_splits_exact(self):
  r=nominate((0,0,0),(3,0,0),(0,-1,0),(3,2,0));self.assertEqual(r['allGapSignSplitParameters'],[F(0),F(1,3),F(1)]);self.assertEqual(len(r['allPositiveGeneratedJoinFaces']),2)
 def test_wrong_xy_rejected(self):
  with self.assertRaises(AssertionError):nominate((0,0,0),(1,0,0),(0,1,1),(1,1,0))
 def test_point_bridge_rejected(self):
  with self.assertRaises(AssertionError):nominate((0,0,0),(0,0,0),(0,1,0),(0,2,0))
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):nominate((0,0,0),(1,0,0),(0,float('nan'),0),(1,1,0))
 def test_original_heights_preserved(self):
  r=nominate((2,F(4,7),3),(5,F(9,13),8),(2,F(11,17),3),(5,F(18,23),8));self.assertEqual(r['exactOriginalOldEndpoints'][0],(F(2),F(4,7),F(3)));self.assertEqual(r['exactOriginalNewEndpoints'][1],(F(5),F(18,23),F(8)))
if __name__=='__main__':unittest.main()
