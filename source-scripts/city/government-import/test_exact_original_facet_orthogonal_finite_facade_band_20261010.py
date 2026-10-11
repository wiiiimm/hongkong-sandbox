import unittest
import numpy as np
from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify

class BandTests(unittest.TestCase):
 def setUp(self):
  self.h=np.array([[[0,0,0],[2,0,0],[2,2,0]],[[0,0,0],[2,2,0],[0,2,0]]],float)
  self.s=np.array([[.2,.2,.05],[1.8,.2,.05],[.2,1.8,.05]])
 def ok(self,s=None,h=None):return verify(self.s if s is None else s,self.h if h is None else h)['verifiedWholeOriginalFacetFiniteFacadeBand']
 def test_union_crosses_real_triangulation_seam(self):self.assertTrue(self.ok())
 def test_diagonal_host_normal_distance(self):
  r=np.array([[1,0,-1],[0,1,0],[1,0,1]],float)/np.sqrt(2);r[1]=[0,1,0]
  self.assertTrue(self.ok(self.s@r,self.h@r))
 def test_reversed_winding_same_closed_host(self):self.assertTrue(self.ok(h=self.h[:,::-1]))
 def test_distance_above_fixed_band(self):s=self.s.copy();s[:,2]=.10000001;self.assertFalse(self.ok(s))
 def test_one_far_vertex_rejects(self):s=self.s.copy();s[2,2]=.11;self.assertFalse(self.ok(s))
 def test_missing_half_finite_host_rejects(self):self.assertFalse(self.ok(h=self.h[:1]))
 def test_inside_plane_outside_finite_facets(self):self.assertFalse(self.ok(self.s+[3,0,0]))
 def test_offset_parallel_host_not_combined(self):h=self.h.copy();h[1,:,2]=.2;self.assertFalse(self.ok(h=h))
 def test_horizontal_host_not_facade(self):self.assertFalse(self.ok(self.s[:,[0,2,1]],self.h[:,:,[0,2,1]]))
 def test_degenerate_source_rejects(self):
  with self.assertRaises(AssertionError):self.ok(np.zeros((3,3)))
 def test_degenerate_host_cannot_cover(self):self.assertFalse(self.ok(h=np.zeros((1,3,3))))
 def test_no_role_root_or_install_credit(self):
  q=verify(self.s,self.h);self.assertTrue(q['verifiedWholeOriginalFacetFiniteFacadeBand']);self.assertFalse(q['visualRoleAccepted']);self.assertFalse(q['structuralRootCredit']);self.assertFalse(q['installationApproved'])

if __name__=='__main__':unittest.main()
