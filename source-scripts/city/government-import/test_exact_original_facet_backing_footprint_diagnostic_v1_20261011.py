import unittest,numpy as np
from exact_original_facet_backing_footprint_diagnostic_v1_20261011 import verify

class OriginalBackingFootprintTests(unittest.TestCase):
 def source(self,y=.303):return np.array([[.1,y,.1],[.8,y,.1],[.1,y,.8]])
 def host(self):return np.array([[[0,0,0],[1,0,0],[0,0,1]]],float)
 def test_authored_offset_is_footprint_not_point_one_mount(self):
  r=verify(self.source(),self.host());self.assertTrue(r['wholeFiniteBackingFootprintCovered']);self.assertFalse(r['allCompleteFiniteFootRegionRecords'][0]['allSourceVerticesWithinExistingPointOnePlaneBand']);self.assertFalse(r['visualRoleAccepted']);self.assertFalse(r['structuralRootOrBridgeCredit'])
 def test_small_exact_outside_projection_remains_uncovered(self):
  s=self.source();s[1,0]=1.0000000001;r=verify(s,self.host());self.assertFalse(r['wholeFiniteBackingFootprintCovered'])
 def test_true_interior_hole_not_filled_by_corner_witnesses(self):
  s=np.array([[0,1,0],[1,1,0],[0,1,1]],float);h=np.array([[[0,0,0],[.4,0,0],[0,0,.4]],[[1,0,0],[.6,0,0],[.6,0,.4]],[[0,0,1],[0,0,.6],[.4,0,.6]]]);self.assertFalse(verify(s,h)['wholeFiniteBackingFootprintCovered'])
 def test_degenerate_host_supplies_no_coverage(self):
  h=np.array([[[0,0,0],[1,0,0],[2,0,0]]],float);r=verify(self.source(),h);self.assertFalse(r['wholeFiniteBackingFootprintCovered']);self.assertEqual(r['exactZeroAreaHostPatchFaces'],[0])
 def test_collapsed_source_footprint_supplies_no_surface_credit(self):
  s=np.array([[.2,0,.2],[.2,1,.2],[.5,0,.2]],float);r=verify(s,self.host());self.assertFalse(r['wholeFiniteBackingFootprintCovered']);self.assertEqual(r['collapsedOrthogonalProjectionsReceiveNoFootprintCredit'],[0])
 def test_changed_patch_rejects_exact_binding(self):
  h=self.host();r=verify(self.source(),h);h[0,0,0]=.01
  with self.assertRaises(AssertionError):verify(self.source(),h,expected_binding=r['binding'])
 def test_unrelated_planes_cannot_be_unioned_as_backing_patch(self):
  h=np.concatenate((self.host(),self.host()+np.array([0,1,0])));self.assertRaises(AssertionError,verify,self.source(),h)
 def test_exact_boundary_is_included(self):
  s=np.array([[0,1,0],[1,1,0],[0,1,1]],float);self.assertTrue(verify(s,self.host())['wholeFiniteBackingFootprintCovered'])
if __name__=='__main__':unittest.main()
