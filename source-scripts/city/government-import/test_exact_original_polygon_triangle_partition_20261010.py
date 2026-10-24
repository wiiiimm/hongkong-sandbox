import unittest
from fractions import Fraction as F
from exact_original_polygon_triangle_partition_20261010 import exact_partition
S=[[0,0],[2,0],[2,2],[0,2]]
T=[[[0,0],[2,0],[2,2]],[[0,0],[2,2],[0,2]]]
class ExactPartitionTests(unittest.TestCase):
 def reject(self,r,t):
  with self.assertRaises(AssertionError):exact_partition(r,t)
 def test_literal_square(self):self.assertTrue(exact_partition([S],T)['exactPartitionPassed'])
 def test_reversed_triangle_orientation(self):self.assertTrue(exact_partition([S],[list(reversed(t)) for t in T])['exactPartitionPassed'])
 def test_reversed_ring_orientation(self):self.assertTrue(exact_partition([list(reversed(S))],T)['exactPartitionPassed'])
 def test_collinear_boundary_subdivision(self):self.assertTrue(exact_partition([[[0,0],[1,0],[2,0],[2,2],[0,2]]],T)['exactPartitionPassed'])
 def test_area_cancelling_wrong_domain(self):self.reject([S],[[[0,0],[2,0],[2,2]],[[0,0],[2,2],[2,4]]])
 def test_real_small_gap(self):self.reject([S],[T[0],[[0,0],[2,2],[F(1,2**80),2]]])
 def test_overlap_rejected(self):self.reject([S],T+[T[0]])
 def test_missing_facet_rejected(self):self.reject([S],T[:1])
 def test_same_area_gap_overlap(self):self.reject([S],[T[0],T[0]])
 def test_zero_area_record_rejected(self):self.reject([S],T+[[[0,0],[1,0],[2,0]]])
 def test_nonfinite(self):self.reject([S],[T[0],[[0,0],[2,2],[float('nan'),2]]])
 def test_crossed_ring(self):self.reject([[[0,0],[2,2],[0,2],[2,0]]],T)
 def test_retraced_boundary(self):self.reject([[[0,0],[2,0],[1,0],[2,2],[0,2]]],T)
 def test_hole_must_remain(self):self.reject([S,[[.5,.5],[1.5,.5],[1.5,1.5],[.5,1.5]]],T)
 def test_hole_outside(self):self.reject([S,[[3,3],[4,3],[4,4],[3,4]]],T)
 def test_true_hole_partition(self):
  outer=[[0,0],[3,0],[3,3],[0,3]];hole=[[1,1],[2,1],[2,2],[1,2]];quads=[[[0,0],[3,0],[2,1],[1,1]],[[3,0],[3,3],[2,2],[2,1]],[[3,3],[0,3],[1,2],[2,2]],[[0,3],[0,0],[1,1],[1,2]]];ts=[]
  for q in quads:ts.extend([[q[0],q[1],q[2]],[q[0],q[2],q[3]]])
  self.assertEqual(exact_partition([outer,hole],ts)['exactAreaFraction'],'8')
 def test_huge_coordinates_no_int_overflow(self):
  n=2**90;s=[[x+n,y+n] for x,y in S];t=[[[x+n,y+n] for x,y in v] for v in T];self.assertEqual(exact_partition([s],t)['exactAreaFraction'],'4')
if __name__=='__main__':unittest.main()
