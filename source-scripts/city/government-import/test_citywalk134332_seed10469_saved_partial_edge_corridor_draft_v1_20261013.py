"""DRAFT ten geometry/upper-envelope counterexamples; no actual-source execution."""
import unittest
from fractions import Fraction as R
import numpy as np
import citywalk134332_seed10469_saved_partial_edge_corridor_draft_v1_20261013 as Q
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from west_wing26195_exact_saved_segment_exposure_draft_v1_20261012 import classify,source_segment
class Cases(unittest.TestCase):
 def setUp(self):
  self.w=np.array([[[0,0,0],[2,2,0],[0,0,2]],[[2,2,0],[0,0,0],[2,0,-2]]],dtype=float)
  self.g=CompleteGround(np.array([[[-4,0,-4],[4,0,-4],[4,0,4]],[[-4,0,-4],[4,0,4],[-4,0,4]]],dtype=float))
 def test_complete_shared_edge(self):self.assertTrue(Q.shared_edge(self.w,[0,1],[['0','0','0'],['2','2','0']])['notPointAdjacency'])
 def test_reversed_edge(self):self.assertTrue(Q.shared_edge(self.w,[0,1],[['2','2','0'],['0','0','0']])['notPointAdjacency'])
 def test_interior_segment_not_whole_edge(self):
  with self.assertRaises(AssertionError):Q.shared_edge(self.w,[0,1],[['1/2','1/2','0'],['1','1','0']])
 def test_point_edge_cannot_bridge(self):
  with self.assertRaises(AssertionError):Q.shared_edge(self.w,[0,1],[['0','0','0'],['0','0','0']])
 def test_wrong_incident_triangle(self):
  with self.assertRaises(AssertionError):Q.shared_edge(self.w,[0,1],[['0','0','0'],['0','0','2']])
 def test_original_facet_membership_rejects_outside(self):
  with self.assertRaises(AssertionError):Q.membership(self.w,0,[['0','0','0'],['4','4','0']])
 def test_partial_edge_retains_whole_negative(self):
  e=[['0','-1','0'],['2','1','0']];p=self.g.segment(e);c=classify(p,expected_ground_sha=self.g.ground_sha,expected_ground_faces=2,expected_endpoints=e)
  self.assertFalse(p['strictlyExposedWholePositiveInterface']);self.assertTrue(c['positiveLengthExposedNominees']);self.assertTrue(all(self.g.segment(n['exactEndpoints'])['strictlyExposedWholePositiveInterface'] for n in c['positiveLengthExposedNominees']))
 def test_grade_zero_start_strict_remainder(self):
  e=[['0','0','0'],['1','1','0']];p=self.g.segment(e);c=classify(p,expected_ground_sha=self.g.ground_sha,expected_ground_faces=2,expected_endpoints=e);s=self.g.segment([['1','1','0'],['1','1','1']]);self.assertTrue(Q.route_found(s,c,s))
 def test_lower_branch_cannot_ignore_higher_ground(self):
  g=CompleteGround(np.concatenate([self.g.ground,np.array([[[-4,2,-4],[4,2,-4],[4,2,4]],[[-4,2,-4],[4,2,4],[-4,2,4]]],dtype=float)]));self.assertFalse(g.segment([['0','1','0'],['1','1','0']])['strictlyExposedWholePositiveInterface'])
 def test_corridor_burial_or_nonzero_anchor_rejects(self):
  good={'strictlyExposedWholePositiveInterface':True};bad={'strictlyExposedWholePositiveInterface':False};anchor={'strictPositiveExceptInitialEndpoint':True,'initialEndpointGapM':'0'};self.assertFalse(Q.route_found(good,anchor,bad));self.assertFalse(Q.route_found(bad,anchor,good));self.assertFalse(Q.route_found(good,dict(anchor,initialEndpointGapM='1'),good))
if __name__=='__main__':unittest.main()
