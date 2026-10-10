import unittest,numpy as np
from exact_original_surface_coordinate_band_20261010 import surface_band
class SurfaceBand(unittest.TestCase):
 def face(self):return np.asarray([[0,0,0],[2,0,0],[0,0,2]],float)
 def test_exact_plane(self):self.assertTrue(surface_band(self.face(),np.asarray([self.face()]),0)['wholeFaceAssociated'])
 def test_parallel_full_facet(self):
  other=self.face();other[:,1]=.01;self.assertTrue(surface_band(self.face(),np.asarray([other]),'.011')['wholeFaceAssociated'])
 def test_real_separation(self):
  other=self.face();other[:,1]=.012;self.assertFalse(surface_band(self.face(),np.asarray([other]),'.011')['wholeFaceAssociated'])
 def test_real_outer_gap(self):
  other=self.face();other[1,0]-=2**-30;self.assertFalse(surface_band(self.face(),np.asarray([other]),'.1')['wholeFaceAssociated'])
 def test_sloped_crossing_only_partial(self):
  other=self.face();other[1,1]=1;self.assertFalse(surface_band(self.face(),np.asarray([other]),'.1')['wholeFaceAssociated'])
 def test_vertical(self):
  face=self.face()[:,[1,0,2]];other=face.copy();other[:,0]=.01;self.assertTrue(surface_band(face,np.asarray([other]),'.011')['wholeFaceAssociated'])
 def test_wrong_plane_projection(self):
  other=self.face()[:,[1,0,2]];self.assertFalse(surface_band(self.face(),np.asarray([other]),'.1')['wholeFaceAssociated'])
 def test_degenerate_unresolved(self):
  face=self.face();face[2]=face[1];self.assertFalse(surface_band(face,np.asarray([self.face()]),'.1')['wholeFaceAssociated'])
 def test_alternate_triangulation(self):
  original=self.face();a,b,c=original;mid=(b+c)/2;other=np.asarray([[a,b,mid],[a,mid,c]]);other[:,:,1]=.01;self.assertTrue(surface_band(original,other,'.011')['wholeFaceAssociated'])
 def test_empty(self):self.assertFalse(surface_band(self.face(),np.empty((0,3,3)),'.1')['wholeFaceAssociated'])
if __name__=='__main__':unittest.main()
