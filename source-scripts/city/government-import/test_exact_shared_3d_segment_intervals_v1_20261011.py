import unittest
from fractions import Fraction as F
from exact_shared_3d_segment_intervals_v1_20261011 import overlap,covered
class Tests(unittest.TestCase):
 def test_complete(self):self.assertEqual(overlap([0,0,0],[2,2,2],[0,0,0],[2,2,2]),(0,1))
 def test_partial(self):self.assertEqual(overlap([0,0,0],[2,2,2],[1,1,1],[2,2,2]),(F(1,2),1))
 def test_reversed(self):self.assertEqual(overlap([0,0,0],[2,2,2],[2,2,2],[1,1,1]),(F(1,2),1))
 def test_union_complete(self):self.assertTrue(covered([(F(0),F(1,2)),(F(1,2),F(1))]))
 def test_union_partial_rejected(self):self.assertFalse(covered([(F(0),F(1,2))]))
 def test_tiny_gap_rejected(self):self.assertFalse(covered([(F(0),F(1,2)),(F(1,2)+F(1,2**80),F(1))]))
 def test_xz_matching_heightgap_rejected(self):self.assertIsNone(overlap([0,0,0],[2,0,2],[0,1,0],[2,1,2]))
 def test_tiny_3d_heightgap_rejected(self):self.assertIsNone(overlap([0,0,0],[2,0,2],[0,2**-40,0],[2,2**-40,2]))
 def test_single_point_rejected(self):self.assertIsNone(overlap([0,0,0],[2,2,2],[2,2,2],[3,3,3]))
 def test_crossing_rejected(self):self.assertIsNone(overlap([0,0,0],[2,2,2],[0,2,0],[2,0,2]))
 def test_vertical(self):self.assertEqual(overlap([0,0,0],[0,2,0],[0,0,0],[0,1,0]),(0,F(1,2)))
 def test_horizontal(self):self.assertEqual(overlap([0,0,0],[2,0,0],[0,0,0],[1,0,0]),(0,F(1,2)))
 def test_disjoint(self):self.assertIsNone(overlap([0,0,0],[2,2,2],[3,3,3],[4,4,4]))
 def test_collapsed_candidate(self):self.assertIsNone(overlap([0,0,0],[2,2,2],[1,1,1],[1,1,1]))
 def test_collapsed_source(self):
  with self.assertRaisesRegex(AssertionError,'Collapsed source'):overlap([0,0,0],[0,0,0],[1,1,1],[2,2,2])
 def test_overhang_clip(self):self.assertEqual(overlap([0,0,0],[2,2,2],[-1,-1,-1],[3,3,3]),(0,1))
if __name__=='__main__':unittest.main()
