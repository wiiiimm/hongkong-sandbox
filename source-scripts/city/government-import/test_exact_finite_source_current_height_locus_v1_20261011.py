import unittest
from fractions import Fraction as F
from exact_finite_source_current_height_locus_v1_20261011 import locus
A=[[0,0,0],[2,0,0],[0,0,2]]
def face(heights):return [[0,heights[0],0],[2,heights[1],0],[0,heights[2],2]]
class Cases(unittest.TestCase):
 def test_equal(self):self.assertEqual(locus(A,A)['classification'],'equal-plane-finite-overlay')
 def test_reversal(self):self.assertEqual(locus(A,A[::-1])['classification'],'equal-plane-finite-overlay')
 def test_nonzero_gap(self):self.assertEqual(locus(A,face([2**-40]*3))['classification'],'no-equal-height-locus')
 def test_crossing(self):
  r=locus(A,face([-1,1,1]));self.assertEqual(r['exactSegment'],[(F(0),F(0),F(1)),(F(1),F(0),F(0))]);self.assertFalse(r['qualifiedRetainedFrontier'])
 def test_point_only(self):self.assertFalse(locus(A,face([0,1,1]))['positiveDimensionalSeam'])
 def test_whole_edge(self):self.assertEqual(locus(A,face([0,0,1]))['classification'],'finite-positive-3D-equal-height-segment')
 def test_disjoint(self):self.assertFalse(locus(A,[[3,0,0],[4,0,0],[3,0,1]])['positiveAreaOverlay'])
 def test_touching_only(self):self.assertFalse(locus(A,[[2,0,0],[3,0,0],[2,0,1]])['positiveAreaOverlay'])
 def test_vertical(self):self.assertEqual(locus(A,[[0,0,0],[0,1,0],[0,1,1]])['classification'],'degenerate-projection-unqualified')
 def test_nonfinite(self):
  for val in [float('inf'),float('-inf'),float('nan')]:
   with self.assertRaises(AssertionError):locus(A,face([val,0,0]))
 def test_schema(self):
  with self.assertRaises(AssertionError):locus(A,[[0,0,0]])
 def test_clipped_plane(self):
  r=locus(A,[[0,0,0],[1,0,0],[0,0,1]]);self.assertEqual(r['exactAreaM2'],F(1,2))
 def test_two_endpoint_height(self):
  r=locus(face([0,2,0]),face([1,1,-1]));self.assertEqual(r['classification'],'finite-positive-3D-equal-height-segment');self.assertTrue(all(p[1]==p[0]for p in r['exactSegment']))
if __name__=='__main__':unittest.main()
