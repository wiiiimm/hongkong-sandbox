from fractions import Fraction as F
import unittest
import numpy as np
from run import ROOT,read
from exact_closed_two_level_mesh_vertical_ray_20261010 import verify

def cube():
 p=np.array([[0,0,0],[1,0,0],[1,0,1],[0,0,1],[0,1,0],[1,1,0],[1,1,1],[0,1,1]],float)
 i=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
 return p[i]
class Rays(unittest.TestCase):
 def test_exact_inside(self):self.assertTrue(verify(cube(),(F(1,4),F(1,2),F(1,3)))['strictOddParityInterior'])
 def test_reverse_winding_same_finite_result(self):self.assertTrue(verify(cube()[:,::-1],(F(1,4),F(1,2),F(1,3)))['strictOddParityInterior'])
 def test_outside_projection(self):self.assertFalse(verify(cube(),(F(2),F(1,2),F(1,3)))['strictOddParityInterior'])
 def test_above_top(self):self.assertFalse(verify(cube(),(F(1,4),F(2),F(1,3)))['strictOddParityInterior'])
 def test_below_bottom(self):self.assertFalse(verify(cube(),(F(1,4),F(-1),F(1,3)))['strictOddParityInterior'])
 def test_on_actual_top(self):self.assertFalse(verify(cube(),(F(1,4),F(1),F(1,3)))['strictOddParityInterior'])
 def test_cap_internal_edge_rejected(self):self.assertFalse(verify(cube(),(F(1,3),F(1,2),F(1,3)))['strictOddParityInterior'])
 def test_actual_side_boundary_rejected(self):self.assertFalse(verify(cube(),(F(0),F(1,2),F(1,3)))['strictOddParityInterior'])
 def test_missing_face(self):
  with self.assertRaises(AssertionError):verify(cube()[:-1],(F(1,4),F(1,2),F(1,3)))
 def test_duplicate_face(self):
  with self.assertRaises(AssertionError):verify(np.concatenate([cube(),cube()[:1]]),(F(1,4),F(1,2),F(1,3)))
 def test_sloped_side_not_extrusion(self):
  a=cube();a[0,0,1]=.1
  with self.assertRaises(AssertionError):verify(a,(F(1,4),F(1,2),F(1,3)))
 def test_nonfinite(self):
  a=cube();a[0,0,0]=float('nan')
  with self.assertRaises(AssertionError):verify(a,(F(1,4),F(1,2),F(1,3)))
 def test_nonrational_point_rejected(self):
  with self.assertRaises(AssertionError):verify(cube(),(.25,.5,.3))
 def test_actual_all540_faces_mixed_caps_preserved(self):
  r=read(ROOT/'docs/astra-city/government-import/government-xl-one-peking-podium-versus-current-basic-tower-diagnostic-v1-20261010/complete-current-basic-tower-geometry.json')['rows'][0]
  a=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
  p=verify(a,(F(0),F(80),F(0)))
  self.assertEqual(p['completeFaces'],540);self.assertEqual(p['completeOppositeClosedEdgePairs'],810)
  self.assertTrue(p['completeAllFacesAccounted']);self.assertFalse(p['capWindingAssumed']);self.assertEqual(p['zeroAreaFaceOmissions'],0)
  self.assertFalse(p['strictOddParityInterior'])
if __name__=='__main__':unittest.main()
