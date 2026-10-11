import unittest,numpy as np
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
class EdgeUpperBand(unittest.TestCase):
 def fixture(self):return np.asarray([[0,.025,0],[1,.025,0]]),np.asarray([[[-2,0,-2],[2,0,-2],[2,0,2]],[[-2,0,-2],[2,0,2],[-2,0,2]]],float)
 def test_whole_original_edge_in_existing_band(self):
  r=verify_contact_segment(*self.fixture());self.assertTrue(r['verifiedCompleteOriginalEdgeContactBand']);self.assertFalse(r['endpointOnlyAcceptance']);self.assertFalse(r['structuralRootCredit'])
 def test_gap_over_band_rejects(self):
  a,g=self.fixture();a[:,1]=.10001;self.assertFalse(verify_contact_segment(a,g)['verifiedCompleteOriginalEdgeContactBand'])
 def test_burial_over_band_rejects(self):
  a,g=self.fixture();a[:,1]=-.10001;self.assertFalse(verify_contact_segment(a,g)['verifiedCompleteOriginalEdgeContactBand'])
 def test_missing_finite_middle_rejects(self):
  a,g=self.fixture();g=np.asarray([[[-1,0,-1],[.4,0,-1],[.4,0,1]],[[.6,0,-1],[2,0,-1],[.6,0,1]]]);self.assertFalse(verify_contact_segment(a,g)['verifiedCompleteOriginalEdgeContactBand'])
 def test_higher_interior_island_rejects_endpoint_proxy(self):
  a,g=self.fixture();g=np.concatenate([g,np.asarray([[[.2,.2,-1],[.8,.2,-1],[.8,.2,1]],[[.2,.2,-1],[.8,.2,1],[.2,.2,1]]])]);r=verify_contact_segment(a,g);self.assertFalse(r['verifiedCompleteOriginalEdgeContactBand']);self.assertTrue(r['completeFiniteCoverage'])
 def test_opposed_planes_interior_upper_envelope_gap_rejects(self):
  a,g=self.fixture();a[:,1]=0
  def plane(sign):
   t=g.copy();t[:,:,1]=sign*.5*t[:,:,0]+(.05 if sign<0 else -.45);return t
  r=verify_contact_segment(a,np.concatenate([plane(1),plane(-1)]));self.assertFalse(r['verifiedCompleteOriginalEdgeContactBand']);self.assertGreater(len(r['exactBandAndCoverageBreakpoints']),2)
 def test_covered_diagonal_edge_and_tessellation_seams(self):
  a,g=self.fixture();a[1,2]=1;self.assertTrue(verify_contact_segment(a,g)['verifiedCompleteOriginalEdgeContactBand'])
 def test_changed_contact_band_rejects(self):
  with self.assertRaises(AssertionError):verify_contact_segment(*self.fixture(),band=.11)
 def test_nonfinite_edge_rejects(self):
  a,g=self.fixture();a[0,1]=np.nan
  with self.assertRaises(AssertionError):verify_contact_segment(a,g)
 def test_collapsed_edge_rejects(self):
  a,g=self.fixture();a[1]=a[0]
  with self.assertRaises(AssertionError):verify_contact_segment(a,g)
if __name__=='__main__':unittest.main()
