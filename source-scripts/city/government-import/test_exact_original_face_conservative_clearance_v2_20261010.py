import unittest,numpy as np
from exact_original_face_conservative_clearance_v2_20261010 import verify
class FiniteBound(unittest.TestCase):
 def test_high_ground_vertex_outside_actual_projection_not_used(self):
  f=np.array([[0,1,0],[.1,1,0],[0,1,.1]]);g=np.array([[[-1,-1,-1],[10,10,-1],[-1,-1,10]]]);p=verify(f,g);self.assertTrue(p['existingOrdinaryClearanceBoundProved']);self.assertFalse(p['sourcePlaneInversionUsed'])
 def test_high_ground_inside_finite_projection_fails(self):
  f=np.array([[0,1,0],[.1,1,0],[0,1,.1]]);g=np.array([[[-1,2,-1],[10,2,-1],[-1,2,10]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_nearly_vertical_source_keeps_actual_low_vertex(self):
  f=np.array([[0,60,0],[1,61,1],[.5,62,.500000000000001]]);g=np.array([[[-2,0,-2],[3,0,-2],[3,0,3]],[[-2,0,-2],[3,0,3],[-2,0,3]]]);self.assertEqual(verify(f,g)['exactCertifiedLowerClearanceM'],'60')
 def test_exact_vertical_line_projection(self):
  f=np.array([[0,2,0],[1,2,1],[1,3,1]]);g=np.array([[[-2,0,-2],[3,0,-2],[3,0,3]],[[-2,0,-2],[3,0,3],[-2,0,3]]]);self.assertTrue(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_point_projection(self):
  f=np.array([[0,2,0],[0,3,0],[0,4,0]]);g=np.array([[[-1,0,-1],[2,0,-1],[-1,0,2]]]);self.assertTrue(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_overlap_upper_surface_is_not_omitted(self):
  f=np.array([[0,1,0],[.1,1,0],[0,1,.1]]);g=np.array([[[-1,0,-1],[10,0,-1],[-1,0,10]],[[-1,2,-1],[10,2,-1],[-1,2,10]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_real_burial_cannot_pass(self):
  f=np.array([[0,-.501,0],[.1,1,0],[0,1,.1]]);g=np.array([[[-1,0,-1],[10,0,-1],[-1,0,10]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_no_finite_projection_coverage(self):
  f=np.array([[0,1,0],[1,1,0],[0,1,1]]);g=np.array([[[0,0,0],[.1,0,0],[0,0,.1]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
if __name__=='__main__':unittest.main()
