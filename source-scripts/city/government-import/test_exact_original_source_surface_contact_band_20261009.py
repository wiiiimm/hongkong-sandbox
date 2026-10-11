import unittest,numpy as np
from exact_original_source_surface_contact_band_20261009 import verify_contact
class SourceBandTests(unittest.TestCase):
    def fixture(self):return np.asarray([[0,-.06,0],[1,-.07,0],[0,-.05,1]],float),np.asarray([[[0,0,0],[1,0,0],[0,0,1]]],float)
    def test_whole_tilted_original_facet_in_strict_contact_band(self):
        f,g=self.fixture();r=verify_contact(f,g);self.assertTrue(r['verifiedCompleteFacetContactBand']);self.assertFalse(r['sampledMaximumUsedForAcceptance'])
    def test_real_gap_over_strict_band_rejects(self):
        f,g=self.fixture();f[0,1]=-.10000001;self.assertFalse(verify_contact(f,g)['verifiedCompleteFacetContactBand'])
    def test_real_support_projection_hole_rejects(self):
        f,g=self.fixture();g[0,1,0]=.5;self.assertFalse(verify_contact(f,g)['verifiedCompleteFacetContactBand'])
    def test_all_overlapping_original_planes_retained(self):
        f,g=self.fixture();other=g.copy();other[:,:,1]=.2;self.assertFalse(verify_contact(f,np.concatenate([g,other]))['verifiedCompleteFacetContactBand'])
    def test_source_plane_is_recomputed(self):
        f,g=self.fixture();f[1,1]=1;self.assertFalse(verify_contact(f,g)['verifiedCompleteFacetContactBand'])
    def test_vertical_source_facet_rejects(self):
        f,g=self.fixture();f[:,0]=0
        with self.assertRaises(AssertionError):verify_contact(f,g)
    def test_widened_contact_band_rejects(self):
        f,g=self.fixture()
        with self.assertRaises(AssertionError):verify_contact(f,g,.2)
    def test_nonfinite_band_rejects(self):
        f,g=self.fixture()
        with self.assertRaises(AssertionError):verify_contact(f,g,float('nan'))
if __name__=='__main__':unittest.main()
