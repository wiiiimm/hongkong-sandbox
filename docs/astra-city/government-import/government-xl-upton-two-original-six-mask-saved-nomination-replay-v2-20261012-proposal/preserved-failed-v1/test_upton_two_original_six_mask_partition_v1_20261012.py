"""UNEXECUTED meaningful exact partition/adversarial fixtures."""
import unittest
from fractions import Fraction as F
from upton_two_original_six_mask_partition_v1_20261012 import *

def area_xz(poly):return abs(sum(a[0]*b[2]-a[2]*b[0]for a,b in zip(poly,poly[1:]+poly[:1])))
class Partition(unittest.TestCase):
 def setUp(self):self.p=[point(x)for x in [(0,2,0),(4,6,0),(0,2,4)]];self.m=mask([(0,0),(2,0),(0,2)])
 def test_mask_plane_preserved(self):
  q=split_union(self.p,[self.m]);self.assertTrue(all(x[1]==x[0]+2 for p in q['unprotected']+[t['polygon']for t in q['protected']]for x in p))
 def test_exact_total_area(self):
  q=split_union(self.p,[self.m]);self.assertEqual(sum(area_xz(t)for t in q['unprotected'])+sum(area_xz(t['polygon'])for t in q['protected']),area_xz(self.p))
 def test_duplicate_mask_no_double_area(self):
  q=split_union(self.p,[self.m,self.m]);self.assertEqual(len(q['protected']),1)
 def test_overlapping_masks_disjoint_accounting(self):
  q=split_union(self.p,[self.m,mask([(1,0),(3,0),(1,2)])]);self.assertEqual(sum(area_xz(t)for t in q['unprotected'])+sum(area_xz(t['polygon'])for t in q['protected']),16)
 def test_outside_mask_whole_unchanged(self):
  q=split_union(self.p,[mask([(10,10),(11,10),(10,11)])]);self.assertEqual(q['unprotected'],[self.p]);self.assertFalse(q['protected'])
 def test_boundary_touch_not_area_duplicate(self):
  q=split_union(self.p,[mask([(4,0),(5,0),(4,1)])]);self.assertEqual(sum(area_xz(t)for t in q['unprotected']),16);self.assertTrue(all(area_xz(t['polygon'])==0 for t in q['protected']))
 def test_reversed_mask_same_partition(self):
  q=split_union(self.p,[mask([(0,0),(0,2),(2,0)])]);self.assertEqual(sum(area_xz(t['polygon'])for t in q['protected']),4)
 def test_collapsed_mask_reject(self):
  with self.assertRaises(AssertionError):mask([(0,0),(1,0),(2,0)])
 def test_zero_original_not_support(self):self.assertFalse(nonzero([(0,0,0),(1,1,1),(2,2,2)]))
 def test_vertical_positive_area_retained(self):
  p=[point(x)for x in [(0,0,0),(0,2,0),(0,0,2)]];q=split_union(p,[self.m]);self.assertTrue(q['protected']);self.assertTrue(nonzero(p))
 def test_complete_cover_no_source_inside(self):
  q=split_union(self.p,[mask([(0,0),(5,0),(0,5)])]);self.assertFalse(q['unprotected'])
 def test_natural_edge_not_automatic_join(self):self.assertFalse(list(interface_edges(self.p,[-10,-10,10,10],[])))
 def test_named_mask_edges_only(self):self.assertEqual(len(list(interface_edges([point(x)for x in [(0,0,0),(2,1,0),(0,0,2)]],[-10,-10,10,10],[self.m]))),3)
if __name__=='__main__':unittest.main()
