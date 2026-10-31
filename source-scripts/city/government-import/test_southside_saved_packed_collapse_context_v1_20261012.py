"""UNEXECUTED exact saved-packing diagnostic counterexamples."""
import unittest
from fractions import Fraction as F
import southside_saved_packed_collapse_context_v1_20261012 as h
T=[[0,0,0],[1,0,0],[0,0,1]]
def row(t,i=0):return dict(outputFacet=i,packedPoints=t)
class Tests(unittest.TestCase):
 def test_exact_same_triangle(self):self.assertTrue(h.coverage(T,[row(T)])['wholeClosedProjectionCovered'])
 def test_tiny_real_gap(self):
  small=[[0,0,0],[1,0,0],[0,0,F(1)-F(1,10**50)]]
  self.assertNotEqual(h.coverage(T,[row(small)])['exactUncoveredProjectedAreaM2'],'0')
 def test_collapsed_triangle_no_area_credit(self):
  self.assertEqual(h.coverage(T,[row([[0,0,0],[1,0,0],[1,0,0]])])['exactUncoveredProjectedAreaM2'],'1/2')
 def test_closed_touch_not_full_coverage(self):
  self.assertFalse(h.coverage(T,[row([[1,0,0],[2,0,0],[1,0,1]])])['wholeClosedProjectionCovered'])
 def test_complete_two_triangle_union(self):
  a=[[0,0,0],[1,0,0],[F(1,2),0,F(1,2)]];b=[[0,0,0],[F(1,2),0,F(1,2)],[0,0,1]]
  self.assertTrue(h.coverage(T,[row(a),row(b,1)])['wholeClosedProjectionCovered'])
 def test_missing_half(self):self.assertFalse(h.coverage(T,[row([[0,0,0],[1,0,0],[F(1,2),0,F(1,2)]])])['wholeClosedProjectionCovered'])
 def test_duplicate_id_rejected(self):
  with self.assertRaises(AssertionError):h.coverage(T,[row(T),row(T)])
 def test_winding_does_not_change_coverage(self):self.assertTrue(h.coverage(T,[row(list(reversed(T)))])['wholeClosedProjectionCovered'])
 def test_projection_not_height_credit(self):
  high=[[x,9,z]for x,y,z in T];self.assertTrue(h.coverage(T,[row(high)])['wholeClosedProjectionCovered']);self.assertFalse(h.plane_context(T,row(high))['agreesOnWholeClosedIntersection'])
 def test_exact_matching_plane(self):self.assertTrue(h.plane_context(T,row(T))['agreesOnWholeClosedIntersection'])
 def test_sloping_residual_extrema(self):
  q=h.plane_context(T,row([[0,0,0],[1,1,0],[0,0,1]]));self.assertEqual(q['exactHeightDifferenceRangeM'],['0','1'])
 def test_real_interval_gap(self):self.assertFalse(h.edge_account((F(0),F(0)),(F(1),F(0)),[[(F(0),F(0)),(F(1,2),F(0)),(F(0),F(1))]])['exactClosedEdgeCovered'])
 def test_singular_closed_endpoint_preserved(self):
  q=h.interval((F(0),F(0)),(F(1),F(0)),[(F(1),F(0)),(F(2),F(0)),(F(1),F(1))]);self.assertEqual(q,(F(1),F(1)))
if __name__=='__main__':unittest.main()
