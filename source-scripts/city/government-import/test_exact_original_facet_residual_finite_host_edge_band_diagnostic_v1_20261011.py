import unittest
import numpy as np
from exact_original_facet_residual_finite_host_edge_band_diagnostic_v1_20261011 import verify,LIMIT
from exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011 import verify as old_edge_verify
class ResidualFiniteBandTests(unittest.TestCase):
 def setUp(self):
  self.source=np.array([[0,0,.05],[.15,0,.05],[0,.2,.05]],float)
  self.host=np.array([[[0,0,0],[.1,0,0],[0,.2,0]]],float)
 def test_actual_finite_plane_and_clamped_edge_union(self):
  p=verify(self.source,self.host)
  self.assertFalse(p['priorCompleteOrthogonalProofVerbatim']['wholeFacetAssociated'])
  self.assertFalse(old_edge_verify(self.source,self.host)['wholeFacetFiniteEdgeUnionAssociated'])
  self.assertTrue(p['wholeFacetWithinExistingFiniteHostBand']);self.assertTrue(p['allExactCertifiedResidualFiniteEdgePieces'])
 def test_clamped_endpoint_witness_is_genuine(self):
  p=verify(self.source,self.host);self.assertTrue(any(r['closestFootBranch']!='interior'for r in p['allExactCertifiedResidualFiniteEdgePieces']))
 def test_true_positive_area_gap_rejects(self):
  s=self.source.copy();s[1,0]=.25;self.assertFalse(verify(s,self.host)['wholeFacetWithinExistingFiniteHostBand'])
 def test_exact_boundary_limit(self):
  s=np.array([[0,0,.1],[.1,0,.1],[0,.2,.1]]);self.assertTrue(verify(s,self.host)['wholeFacetWithinExistingFiniteHostBand'])
 def test_next_float_outside_limit_rejects(self):
  s=np.array([[0,0,np.nextafter(.1,np.inf)],[.1,0,np.nextafter(.1,np.inf)],[0,.2,np.nextafter(.1,np.inf)]]);self.assertFalse(verify(s,self.host)['wholeFacetWithinExistingFiniteHostBand'])
 def test_remote_host_rejects(self):self.assertFalse(verify(self.source,self.host+5)['wholeFacetWithinExistingFiniteHostBand'])
 def test_empty_host_rejects(self):self.assertFalse(verify(self.source,np.empty((0,3,3)))['wholeFacetWithinExistingFiniteHostBand'])
 def test_zero_host_no_credit(self):
  h=self.host.copy();h[0,2]=h[0,1];self.assertFalse(verify(self.source,h)['wholeFacetWithinExistingFiniteHostBand'])
 def test_zero_source_rejected(self):
  s=self.source.copy();s[2]=s[1]
  with self.assertRaises(AssertionError):verify(s,self.host)
 def test_nonfinite_rejected(self):
  s=self.source.copy();s[0,0]=float('nan')
  with self.assertRaises(AssertionError):verify(s,self.host)
 def test_exact_input_binding_rejects_changed_pose(self):
  p=verify(self.source,self.host);binding={k:p[k]for k in ['completeSourceFacetSHA256','completeHostWorldSHA256']}
  with self.assertRaises(AssertionError):verify(self.source+.001,self.host,expected_input_binding=binding)
 def test_exact_input_binding_rejects_changed_host(self):
  p=verify(self.source,self.host);binding={k:p[k]for k in ['completeSourceFacetSHA256','completeHostWorldSHA256']}
  with self.assertRaises(AssertionError):verify(self.source,self.host+.001,expected_input_binding=binding)
 def test_closed_whole_facet_and_fixed_band_preserved(self):
  p=verify(self.source,self.host);self.assertEqual(p['strictBandExact'],str(LIMIT));self.assertFalse(p['visualRoleAccepted']);self.assertFalse(p['structuralRootOrBridgeCredit']);self.assertFalse(p['installationApproved'])
 def test_triangle_winding_does_not_invent_role(self):self.assertTrue(verify(self.source[::-1],self.host[:,::-1])['wholeFacetWithinExistingFiniteHostBand'])
if __name__=='__main__':unittest.main()
