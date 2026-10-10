import unittest,numpy as np
from exact_original_facet_finite_edge_band_diagnostic_v1_20261011 import verify
class Tests(unittest.TestCase):
 def setUp(self):self.host=np.asarray([[[0.,0.,0.],[2.,0.,0.],[0.,2.,0.]]]);self.source=np.asarray([[.2,-.04,0.],[1.8,-.04,0.],[1.,-.08,0.]])
 def test_finite_edge_certifies_outside_plane_foot(self):
  r=verify(self.source,self.host);self.assertTrue(r['wholeFacetFiniteEdgeAssociated']);self.assertTrue(r['noDifferentEdgeCombinationCredit']);self.assertFalse(r['physicalContactCredit']);self.assertFalse(r['structuralRootCredit'])
 def test_host_vertex_region(self):self.assertTrue(verify(np.asarray([[-.02,-.02,0.],[-.04,-.02,0.],[-.02,-.04,0.]]),self.host)['wholeFacetFiniteEdgeAssociated'])
 def test_exact_fixed_band_boundary(self):self.assertTrue(verify(np.asarray([[.2,-.1,0.],[1.8,-.1,0.],[1.,-.08,0.]]),self.host)['wholeFacetFiniteEdgeAssociated'])
 def test_just_outside_unchanged_band(self):self.assertFalse(verify(self.source+np.asarray([0.,-.07,0.]),self.host)['wholeFacetFiniteEdgeAssociated'])
 def test_finite_endpoint_clamp_rejects_infinite_line(self):self.assertFalse(verify(self.source+np.asarray([3.,0.,0.]),self.host)['wholeFacetFiniteEdgeAssociated'])
 def test_no_different_edge_combination(self):self.assertFalse(verify(np.asarray([[.1,-.01,0.],[1.9,-.01,0.],[-.01,1.9,0.]]),self.host)['wholeFacetFiniteEdgeAssociated'])
 def test_nonzero_small_source_remains_real_surface(self):
  r=verify(np.asarray([[.2,-.04,0.],[.2000000001,-.04,0.],[.2,-.0400000001,0.]]),self.host);self.assertTrue(r['wholeFacetFiniteEdgeAssociated']);self.assertEqual(r['sourceGeometryChanges'],0)
 def test_degenerate_host_does_not_supply_surface_credit(self):self.assertFalse(verify(self.source,np.asarray([[[0.,0.,0.],[2.,0.,0.],[1.,0.,0.]]]))['wholeFacetFiniteEdgeAssociated'])
 def test_zero_source_is_not_surface(self):
  with self.assertRaises(AssertionError):verify(np.zeros((3,3)),self.host)
 def test_nan_fails(self):
  s=self.source.copy();s[0,0]=np.nan
  with self.assertRaises(AssertionError):verify(s,self.host)
 def test_changed_pose_changes_sha_and_rejects(self):
  a=verify(self.source,self.host);b=verify(self.source+np.asarray([0.,0.,1.]),self.host);self.assertNotEqual(a['completeSourceFacetSHA256'],b['completeSourceFacetSHA256']);self.assertFalse(b['wholeFacetFiniteEdgeAssociated'])
 def test_changed_host_changes_sha_and_rejects(self):
  a=verify(self.source,self.host);b=verify(self.source,self.host+np.asarray([0.,0.,1.]));self.assertNotEqual(a['completeHostWorldSHA256'],b['completeHostWorldSHA256']);self.assertFalse(b['wholeFacetFiniteEdgeAssociated'])
 def test_stale_source_binding_rejects_even_inside_band(self):
  r=verify(self.source,self.host);binding={k:r[k]for k in ['completeSourceFacetSHA256','completeHostWorldSHA256']}
  with self.assertRaises(AssertionError):verify(self.source+np.asarray([0.,.001,0.]),self.host,expected_input_binding=binding)
 def test_stale_host_binding_rejects_even_inside_band(self):
  r=verify(self.source,self.host);binding={k:r[k]for k in ['completeSourceFacetSHA256','completeHostWorldSHA256']}
  with self.assertRaises(AssertionError):verify(self.source,self.host+np.asarray([0.,.001,0.]),expected_input_binding=binding)
 def test_exact_binding_replays(self):
  r=verify(self.source,self.host);binding={k:r[k]for k in ['completeSourceFacetSHA256','completeHostWorldSHA256']};self.assertEqual(r,verify(self.source,self.host,expected_input_binding=binding))
 def test_incomplete_binding_rejects(self):
  with self.assertRaises(AssertionError):verify(self.source,self.host,expected_input_binding={})
if __name__=='__main__':unittest.main()
