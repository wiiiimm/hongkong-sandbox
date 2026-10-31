"""Distinct finite rectangle/retained-facet cases, not prior box-test repeats."""
import unittest
import numpy as np
from sparkle_packed_closed_projection_protection_20261011 import closed_pair,audit

def xyz(points):return np.array([[[x,0,z]for x,z in points]],float)
class Protection(unittest.TestCase):
 def test_diagonal_box_nomination_is_separated(self):
  result=closed_pair([(0,2),(2,0),(2,2)],[(0,0),(.5,0),(.5,.5),(0,.5)])
  self.assertTrue(result['strictlySeparated']);self.assertIn('axis',result)
 def test_corner_touch_fails(self):
  self.assertFalse(closed_pair([(1,1),(2,1),(1,2)],[(0,0),(1,0),(1,1),(0,1)])['strictlySeparated'])
 def test_edge_touch_fails(self):
  self.assertFalse(closed_pair([(1,0),(2,0),(1,1)],[(0,0),(1,0),(1,1),(0,1)])['strictlySeparated'])
 def test_area_overlap_fails(self):
  self.assertFalse(closed_pair([(.5,.5),(2,.5),(.5,2)],[(0,0),(1,0),(1,1),(0,1)])['strictlySeparated'])
 def test_exact_binary64_gap_not_epsilon(self):
  near=np.nextafter(1.,2.)
  self.assertTrue(closed_pair([(near,0),(2,0),(near,1)],[(0,0),(1,0),(1,1),(0,1)])['strictlySeparated'])
 def test_collinear_disjoint_with_overlapping_boxes(self):
  self.assertTrue(closed_pair([(0,0),(1,1),(1,1)],[(0,.25),(.25,.5),(.25,.5)])['strictlySeparated'])
 def test_collapsed_point_touch_fails(self):
  self.assertFalse(closed_pair([(1,1)]*3,[(0,0),(1,0),(1,1),(0,1)])['strictlySeparated'])
 def test_complete_rect_and_facet_nominations(self):
  out=audit(xyz([(0,2),(2,0),(2,2)]),np.array([[0,0,.5,.5]]),xyz([(0,0),(.5,0),(0,.5)]))
  self.assertEqual(out['completePairs'],2);self.assertEqual(out['completeInclusiveAABBNominations'],2)
  self.assertEqual(out['actualClosedIntersectionPairs'],0)
 def test_retained_facet_contact_without_rect_contact_fails(self):
  out=audit(xyz([(0,2),(2,0),(2,2)]),np.array([[-2,-2,-1,-1]]),xyz([(1,1),(2,1),(1,2)]))
  self.assertEqual(out['actualClosedIntersectionPairs'],1)
 def test_duplicate_facets_preserve_multiplicity(self):
  n=np.repeat(xyz([(1,1),(2,1),(1,2)]),2,axis=0)
  out=audit(n,np.array([[0,0,1,1]]),xyz([(-2,-2),(-1,-2),(-2,-1)]))
  self.assertEqual(out['actualClosedIntersectionPairs'],2)
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):audit(xyz([(0,0),(float('nan'),1),(1,0)]),np.array([[0,0,1,1]]),xyz([(2,2),(3,2),(2,3)]))
 def test_nonpacked_new_geometry_rejected(self):
  with self.assertRaises(AssertionError):audit(xyz([(0,0),(.1,1),(1,0)]),np.array([[2,2,3,3]]),xyz([(4,4),(5,4),(4,5)]))
 def test_bad_rectangle_rejected(self):
  with self.assertRaises(AssertionError):audit(xyz([(0,0),(1,1),(1,0)]),np.array([[1,0,0,1]]),xyz([(4,4),(5,4),(4,5)]))
if __name__=='__main__':unittest.main()
