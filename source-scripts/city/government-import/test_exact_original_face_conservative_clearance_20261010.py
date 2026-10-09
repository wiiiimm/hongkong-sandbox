import unittest,numpy as np
from exact_original_face_conservative_clearance_20261010 import verify
class Clearance(unittest.TestCase):
 def ground(self,y=0):return np.array([[[-2,y,-2],[3,y,-2],[3,y,3]],[[-2,y,-2],[3,y,3],[-2,y,3]]],float)
 def test_nearly_vertical_finite_source_cannot_extrapolate_below_vertex_height(self):
  f=np.array([[0,60,0],[1,61,1],[.5,62,.500000000000001]]);p=verify(f,self.ground());self.assertTrue(p['existingOrdinaryClearanceBoundProved']);self.assertEqual(p['exactCertifiedLowerClearanceM'],'60');self.assertFalse(p['rawPriorDiagnosticChanged'])
 def test_exact_vertical_projection_kept(self):
  f=np.array([[0,2,0],[1,2,1],[1,3,1]]);self.assertTrue(verify(f,self.ground())['existingOrdinaryClearanceBoundProved'])
 def test_point_projection_kept(self):
  f=np.array([[0,2,0],[0,3,0],[0,4,0]]);self.assertTrue(verify(f,self.ground())['existingOrdinaryClearanceBoundProved'])
 def test_true_burial_fails(self):
  f=np.array([[0,-.51,0],[1,2,0],[0,2,1]]);self.assertFalse(verify(f,self.ground())['existingOrdinaryClearanceBoundProved'])
 def test_fixed_boundary_is_exact(self):
  f=np.array([[0,-.5,0],[1,2,0],[0,2,1]]);self.assertTrue(verify(f,self.ground())['existingOrdinaryClearanceBoundProved'])
 def test_high_intersecting_terrain_is_retained(self):
  f=np.array([[0,2,0],[1,2,0],[0,2,1]]);g=np.concatenate([self.ground(),self.ground(4)]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_missing_finite_coverage_fails(self):
  f=np.array([[0,2,0],[1,2,0],[0,2,1]]);g=np.array([[[0,0,0],[.1,0,0],[0,0,.1]]]);self.assertFalse(verify(f,g)['existingOrdinaryClearanceBoundProved'])
 def test_nonfinite_rejects(self):
  with self.assertRaises(AssertionError):verify([[0,2,0],[1,2,0],[0,np.nan,1]],self.ground())
if __name__=='__main__':unittest.main()
