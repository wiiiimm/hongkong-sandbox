import unittest,math
from upton_saved_guard_source_column_v1_20261012 import assess
class ExistingColumn(unittest.TestCase):
 def face(self,y):return [[0,y,0],[2,y,0],[0,y,2]]
 def test_actual_finite_interior_conflict(self):self.assertTrue(assess(self.face(0),[.5,.5],1)['ordinaryConflictAtSmallestAcceptedHeight'])
 def test_exact_ordinary_boundary(self):self.assertFalse(assess(self.face(.5),[.5,.5],1)['ordinaryConflictAtSmallestAcceptedHeight'])
 def test_next_binary64_below_ordinary_boundary(self):self.assertTrue(assess(self.face(math.nextafter(.5,-math.inf)),[.5,.5],1)['ordinaryConflictAtSmallestAcceptedHeight'])
 def test_aabb_candidate_outside_actual_triangle(self):self.assertFalse(assess(self.face(0),[1.5,1.5],1)['completeClosedSourceColumn']['exactClosedHorizontalProjectionsMeet'])
 def test_vertical_complete_column_minimum(self):
  q=assess([[1,0,0],[1,2,0],[1,2,2]],[1,1],2);self.assertEqual(q['geometricOrientationDescriptorOnly'],'vertical');self.assertEqual(q['completeClosedSourceColumn']['exactMinimumFiniteColumnGapM'],'-1')
 def test_zero_primitive_not_obstruction_or_support(self):
  q=assess([[0,0,0],[1,0,0],[2,0,0]],[1,0],10);self.assertTrue(q['exactSourceNonrendering']);self.assertFalse(q['ordinaryConflictAtSmallestAcceptedHeight'])
 def test_reverse_winding_retains_gap_not_role(self):
  a=assess(self.face(0),[.5,.5],1);b=assess(self.face(0)[::-1],[.5,.5],1);self.assertEqual(a['completeClosedSourceColumn']['exactMinimumFiniteColumnGapM'],b['completeClosedSourceColumn']['exactMinimumFiniteColumnGapM']);self.assertNotEqual(a['geometricOrientationDescriptorOnly'],b['geometricOrientationDescriptorOnly'])
 def test_nonfinite_input_rejected(self):
  with self.assertRaises(AssertionError):assess(self.face(0),[float('nan'),0],1)
if __name__=='__main__':unittest.main()
