import unittest,numpy as np
from exact_original_facet_piecewise_finite_facade_band_20261010 import verify
from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify as coplanar

def rectangle(x0,x1,z):return np.array([[[x0,0,z],[x1,0,z],[x1,2,z]],[[x0,0,z],[x1,2,z],[x0,2,z]]],float)
S=np.array([[0,0,0],[2,0,0],[0,2,0]],float)
class TestPiecewise(unittest.TestCase):
 def test_actual_non_coplanar_seam(self):
  h=np.concatenate([rectangle(0,1,.05),rectangle(1,2,-.05)])
  self.assertFalse(coplanar(S,h)['verifiedWholeOriginalFacetFiniteFacadeBand']);self.assertTrue(verify(S,h)['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_exact_existing_limit(self):self.assertTrue(verify(S,rectangle(0,2,.1))['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_outside_limit(self):self.assertFalse(verify(S,rectangle(0,2,np.nextafter(.1,np.inf)))['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_tiny_finite_gap(self):self.assertFalse(verify(S,np.concatenate([rectangle(0,1,.05),rectangle(1+1e-8,2,-.05)]))['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_source_pose_change(self):self.assertFalse(verify(S+[0,0,.2],rectangle(0,2,0))['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_missing_host_half(self):self.assertFalse(verify(S,rectangle(0,1,.05))['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_distant_host(self):self.assertFalse(verify(S,rectangle(0,2,1))['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_reversed_host_surface(self):self.assertTrue(verify(S,rectangle(0,2,.05)[:,::-1])['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_zero_host_accounted(self):
  d=verify(S,np.concatenate([rectangle(0,2,.05),np.zeros((1,3,3))]));self.assertTrue(d['verifiedWholeOriginalFacetFiniteFacadeBand']);self.assertEqual(d['exactZeroAreaCandidateHostFaces'],[2])
 def test_zero_source_rejected(self):
  with self.assertRaises(AssertionError):verify(np.zeros((3,3)),rectangle(0,2,0))
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):verify(S*np.nan,rectangle(0,2,0))
 def test_no_role_credit(self):
  d=verify(S,rectangle(0,2,0));self.assertFalse(d['visualRoleAccepted']);self.assertFalse(d['structuralRootCredit']);self.assertFalse(d['installationApproved'])
 def test_host_hash_changes(self):self.assertNotEqual(verify(S,rectangle(0,2,0))['completeHostSHA256'],verify(S,rectangle(0,2,.01))['completeHostSHA256'])
if __name__=='__main__':unittest.main()
