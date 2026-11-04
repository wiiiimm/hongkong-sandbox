"""DRAFT adverse scratch-union and runtime-MAX boundary nomination tests."""
import unittest
from fractions import Fraction as F
from exact_faithful_multisurface_transition_domain_v1_20261011 import partition,planar_boundary,upper_anchors,closed_pairs
from exact_original_projection_coverage_v2_20261010 import signed_area
T=[(F(0),F(0)),(F(2),F(0)),(F(0),F(2))]
def face(poly,y):return [(x,F(y),z)for x,z in poly]
class Tests(unittest.TestCase):
 def test_exact_closed_bucket_point_boundary_not_excluded(self):
  self.assertEqual(closed_pairs([[(F(0),F(0)),(F(5),F(0)),(F(0),F(5))]],[[(F(5),F(0)),(F(6),F(0)),(F(5),F(1))]]),[(0,0)])
 def test_fraction_intersection_denominators_do_not_require_global_lcm(self):
  q=[(F(1,999983),F(1,999979)),(F(1),F(0)),(F(0),F(1))];self.assertEqual(closed_pairs([T],[q]),[(0,0)])
 def test_provably_disjoint_buckets_are_excluded(self):
  q=[(x+100,z+100)for x,z in T];self.assertEqual(closed_pairs([T],[q]),[])
 def test_duplicate_projection_keeps_union_once_not_source_deletion(self):
  p,r=partition([T,T]);self.assertEqual(sum(signed_area(q)for q in p),F(2));self.assertEqual(len(r),2);self.assertFalse(r[1]['allExactRemainingPositiveCells'])
 def test_distinct_height_projection_same_scratch_union(self):
  p,_=partition([T,T]);a=upper_anchors([dict(start=T[0],end=T[1])],[face(T,1),face(T,9)]);self.assertEqual(a[0]['originalUpperPlane'],1);self.assertEqual(a[0]['exactEndpointY'],[9,9]);self.assertEqual(len(p),1)
 def test_partial_overlap_exact_area(self):
  q=[(F(1),F(0)),(F(3),F(0)),(F(1),F(2))];p,_=partition([T,q]);self.assertEqual(sum(signed_area(v)for v in p),F(7,2))
 def test_disjoint_preserved(self):
  q=[(x+10,z)for x,z in T];p,_=partition([T,q]);self.assertEqual(len(p),2);_,b=planar_boundary(p);self.assertEqual(len(b['completePositiveEdgeComponentCycles']),2)
 def test_point_touch_does_not_bridge(self):
  q=[(x+2,z)for x,z in T];p,_=partition([T,q]);_,b=planar_boundary(p);self.assertEqual(len(b['completePositiveEdgeComponentCycles']),2)
 def test_diagonal_shared_union(self):
  q=[(F(2),F(0)),(F(2),F(2)),(F(0),F(2))];p,_=partition([T,q]);e,b=planar_boundary(p);self.assertEqual(len(b['completePositiveEdgeComponentCycles']),1);self.assertEqual(len(e),4)
 def test_contained_projection(self):
  q=[(F(1,4),F(1,4)),(F(1,2),F(1,4)),(F(1,4),F(1,2))];p,_=partition([T,q]);self.assertEqual(sum(signed_area(v)for v in p),2)
 def test_wrong_winding_rejected(self):
  with self.assertRaises(AssertionError):partition([T[::-1]])
 def test_zero_projection_rejected(self):
  with self.assertRaises(AssertionError):partition([[(0,0),(1,0),(2,0)]])
 def test_upper_envelope_crossing_partitions(self):
  a=[(0,0,0),(2,2,0),(0,0,2)];b=[(0,2,0),(2,0,0),(0,2,2)];r=upper_anchors([dict(start=(F(0),F(0)),end=(F(2),F(0)))],[a,b]);self.assertEqual(len(r),2);self.assertEqual([q['originalUpperPlane']for q in r],[1,0]);self.assertEqual(r[0]['end'],(F(1),F(0)))
 def test_closed_higher_point_only_actor_discontinuity_reject(self):
  b=[(2,9,0),(3,9,0),(2,9,1)]
  with self.assertRaises(AssertionError):upper_anchors([dict(start=(F(0),F(0)),end=(F(2),F(0)))],[face(T,0),b])
 def test_lower_projected_layer_not_snap(self):
  r=upper_anchors([dict(start=T[0],end=T[1])],[face(T,F(1,3)),face(T,F(2,3))]);self.assertEqual(r[0]['exactEndpointY'],[F(2,3)]*2)
if __name__=='__main__':unittest.main()
