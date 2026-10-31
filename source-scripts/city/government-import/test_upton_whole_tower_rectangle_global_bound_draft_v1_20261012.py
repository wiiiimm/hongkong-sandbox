"""UNEXECUTED meaningful adverse cases for bounded sufficient proof."""
import unittest,numpy as np
from upton_whole_tower_rectangle_global_bound_draft_v1_20261012 import whole_world_proof
class Cases(unittest.TestCase):
 def setUp(self):
  self.g=np.array([[[0,0,0],[2,0,0],[2,0,2]],[[0,0,0],[2,0,2],[0,0,2]]],float);self.s=self.g.copy();self.s[:,:,1]=5;self.b=np.array([[0,5,0],[2,5,2]],float)
 def test_complete_rectangle_and_positive_global_bound(self):
  p=whole_world_proof(self.s,self.g,self.b);self.assertTrue(p['allWholeSourceFacetsStrictPositiveFiniteProved']);self.assertEqual(p['exactConservativeGlobalLowerM'],'5');self.assertFalse(p['gradeRootProved']);self.assertFalse(p['physicalAccepted'])
 def test_hole_rejects_even_positive_height_bound(self):
  p=whole_world_proof(self.s,self.g[:1],self.b);self.assertFalse(p['wholeRectangleProjectionCovered']);self.assertFalse(p['allWholeSourceFacetsOrdinaryFiniteProved'])
 def test_wrong_height_ground_rejects_global_method(self):
  g=self.g.copy();g[:,:,1]=6;p=whole_world_proof(self.s,g,self.b);self.assertEqual(p['exactConservativeGlobalLowerM'],'-1');self.assertFalse(p['allWholeSourceFacetsStrictPositiveFiniteProved'])
 def test_zero_bound_has_no_strict_or_epsilon_credit(self):
  g=self.g.copy();g[:,:,1]=5;p=whole_world_proof(self.s,g,self.b);self.assertFalse(p['allWholeSourceFacetsStrictPositiveFiniteProved']);self.assertEqual(p['exactConservativeGlobalLowerM'],'0')
 def test_hidden_vertex_outside_nominated_bounds_rejects(self):
  s=self.s.copy();s[0,0,0]=-1
  with self.assertRaises(AssertionError):whole_world_proof(s,self.g,self.b)
 def test_zero_source_facet_retained_without_root_credit(self):
  z=np.array([[[1,5,1],[1,5,1],[1,5,1]]],float);p=whole_world_proof(np.concatenate([self.s,z]),self.g,self.b);self.assertEqual(p['completeSourceFacets'],3);self.assertTrue(p['allWholeSourceFacetsStrictPositiveFiniteProved']);self.assertFalse(p['wholeEdgeOrCapRoleQualified'])
 def test_vertical_ground_high_endpoint_not_dropped(self):
  vertical=np.array([[[1,0,1],[1,6,1],[1,0,2]]],float);p=whole_world_proof(self.s,np.concatenate([self.g,vertical]),self.b);self.assertFalse(p['allWholeSourceFacetsStrictPositiveFiniteProved']);self.assertEqual(p['completeGroundFacets'],3)
 def test_zero_width_rectangle_does_not_fake_area_coverage(self):
  s=np.array([[[1,5,0],[1,5,1],[1,5,2]]],float);b=np.array([[1,5,0],[1,5,2]],float);p=whole_world_proof(s,self.g,b);self.assertFalse(p['wholeRectangleProjectionCovered'])
 def test_one_lower_world_cannot_reuse_clear_world(self):
  low=self.s.copy();low[:,:,1]=-1;b=self.b.copy();b[:,1]=-1
  self.assertTrue(whole_world_proof(self.s,self.g,self.b)['allWholeSourceFacetsStrictPositiveFiniteProved']);self.assertFalse(whole_world_proof(low,self.g,b)['allWholeSourceFacetsStrictPositiveFiniteProved'])
 def test_nonfinite_bound_rejects(self):
  b=self.b.copy();b[0,1]=np.nan
  with self.assertRaises(AssertionError):whole_world_proof(self.s,self.g,b)
if __name__=='__main__':unittest.main()
