import unittest, numpy as np
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify,inward_sqrt,F,LIMIT
class Cases(unittest.TestCase):
 def setUp(self):self.a=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
 def test_actual_full_finite_parallel(self):self.assertTrue(verify(self.a,np.array([self.a+[0,0,.05]]))['wholeFacetAssociated'])
 def test_exact_band_boundary(self):self.assertTrue(verify(self.a,np.array([self.a+[0,0,.1]]))['wholeFacetAssociated'])
 def test_above_band(self):self.assertFalse(verify(self.a,np.array([self.a+[0,0,np.nextafter(.1,np.inf)]]))['wholeFacetAssociated'])
 def test_finite_foot_outside(self):self.assertFalse(verify(self.a,np.array([self.a+[2,0,0]]))['wholeFacetAssociated'])
 def test_non_axis_host_plane(self):
  m=np.array([[1,0,0],[0,.8,-.6],[0,.6,.8]])
  host=np.array([[-1.,-1.,.04],[3.,-1.,.04],[-1.,3.,.04]])
  self.assertTrue(verify(self.a@m.T,np.array([host@m.T]))['wholeFacetAssociated'])
 def test_transformed_nominally_matching_edges_retain_real_gap(self):
  m=np.array([[1,0,0],[0,.8,-.6],[0,.6,.8]])
  self.assertFalse(verify(self.a@m.T,np.array([(self.a+[0,0,.04])@m.T]))['wholeFacetAssociated'])
 def test_reversed_host_winding(self):self.assertTrue(verify(self.a,np.array([(self.a+[0,0,.05])[::-1]]))['wholeFacetAssociated'])
 def test_two_triangle_full_union(self):
  mid=(self.a[1]+self.a[2])/2
  self.assertFalse(verify(self.a,np.array([[self.a[0],self.a[1],mid],[self.a[0],mid,self.a[2]]])+.04)['wholeFacetAssociated'])
  self.assertTrue(verify(self.a,np.array([[self.a[0],self.a[1],mid],[self.a[0],mid,self.a[2]]])+[0,0,.04])['wholeFacetAssociated'])
 def test_tiny_real_interior_hole_all_outer_edges_present(self):
  a,b,c=self.a;p=np.array([.25,.25,0]);q=p+[2**-35,0,0];r=p+[0,2**-35,0]
  hosts=np.array([[a,b,q],[a,q,p],[b,c,r],[b,r,q],[c,a,p],[c,p,r]])
  result=verify(self.a,hosts);self.assertFalse(result['wholeFacetAssociated']);self.assertIn('uncoveredInteriorWitness',result['sourceBarycentricCoverage'])
 def test_degenerate_host_cannot_credit(self):self.assertFalse(verify(self.a,np.array([[self.a[0],self.a[0],self.a[1]]]))['wholeFacetAssociated'])
 def test_degenerate_source_no_root(self):self.assertFalse(verify(np.array([self.a[0],self.a[0],self.a[1]]),np.array([self.a]))['wholeFacetAssociated'])
 def test_nonfinite(self):
  a=self.a.copy();a[0,0]=float('nan')
  with self.assertRaises(AssertionError):verify(a,np.array([self.a]))
 def test_inward_irrational_square_root(self):
  r=inward_sqrt(F(2));self.assertLess(r*r,F(2));self.assertLess(F(2)-r*r,F(1,1<<120))
 def test_tiny_nonzero_real_surface_retained(self):
  a=self.a*1e-150;self.assertTrue(verify(a,np.array([a]))['wholeFacetAssociated'])
if __name__=='__main__':unittest.main()
