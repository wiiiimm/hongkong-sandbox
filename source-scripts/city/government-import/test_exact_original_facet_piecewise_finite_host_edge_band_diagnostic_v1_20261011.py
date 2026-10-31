import unittest
import numpy as np
from exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011 import verify
class Tests(unittest.TestCase):
 def setUp(self):
  self.src=np.array([[0,.05,0],[2,.05,0],[0,.09,0.]])
  self.hosts=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[1,0,0],[2,0,0],[2,0,1]]],float)
 def test_segmented_line(self):self.assertTrue(verify(self.src,self.hosts)['wholeFacetFiniteEdgeUnionAssociated'])
 def test_clamped_endpoint(self):
  s=np.array([[-.03,.02,0],[-.04,.04,0],[-.01,.05,0]])
  p=verify(s,self.hosts[:1]);self.assertTrue(p['wholeFacetFiniteEdgeUnionAssociated']);self.assertTrue(any(r['closestFootBranch']=='clamped-start'for r in p['allCompleteRegionCertificates']))
 def test_existing_boundary(self):
  s=self.src.copy();s[:2,1]=.1;self.assertTrue(verify(s,self.hosts)['wholeFacetFiniteEdgeUnionAssociated'])
 def test_outside_boundary(self):
  s=self.src.copy();s[:2,1]=np.nextafter(.1,np.inf);self.assertFalse(verify(s,self.hosts)['wholeFacetFiniteEdgeUnionAssociated'])
 def test_missing_middle(self):
  h=self.hosts.copy();h[0,1,0]=.8;h[1,0,0]=1.2;self.assertFalse(verify(self.src,h)['wholeFacetFiniteEdgeUnionAssociated'])
 def test_degenerate_host(self):
  h=np.array([[[0,0,0],[1,0,0],[2,0,0]]]);self.assertFalse(verify(self.src,h)['wholeFacetFiniteEdgeUnionAssociated'])
 def test_nonrendering_source(self):
  with self.assertRaises(AssertionError):verify([[0,0,0],[1,0,0],[2,0,0]],self.hosts)
 def test_nan(self):
  s=self.src.copy();s[0,0]=np.nan
  with self.assertRaises(AssertionError):verify(s,self.hosts)
 def test_changed_source(self):
  p=verify(self.src,self.hosts);binding={k:p[k]for k in ('completeSourceFacetSHA256','completeHostWorldSHA256')};s=self.src.copy();s[0,0]+=.001
  with self.assertRaises(AssertionError):verify(s,self.hosts,expected_input_binding=binding)
 def test_changed_host(self):
  p=verify(self.src,self.hosts);binding={k:p[k]for k in ('completeSourceFacetSHA256','completeHostWorldSHA256')};h=self.hosts.copy();h[0,0,1]+=.001
  with self.assertRaises(AssertionError):verify(self.src,h,expected_input_binding=binding)
 def test_vertex_only_hosts_no_interior(self):
  s=np.array([[0,.05,0],[10,.05,0],[0,.05,10.]])
  h=np.array([[[x,0,z],[x+.01,0,z],[x,0,z+.01]]for x,z in [(0,0),(10,0),(0,10)]])
  self.assertFalse(verify(s,h)['wholeFacetFiniteEdgeUnionAssociated'])
 def test_no_role_credit(self):
  p=verify(self.src,self.hosts)
  for k in ['visualRoleAccepted','physicalContactCredit','structuralRootCredit','structuralBridgeCredit','installationApproved']:self.assertFalse(p[k])
if __name__=='__main__':unittest.main()
