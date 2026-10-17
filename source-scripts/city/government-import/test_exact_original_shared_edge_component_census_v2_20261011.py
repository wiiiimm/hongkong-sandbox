import unittest,numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
class Tests(unittest.TestCase):
 def test_real_shared_edge(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[0,0,0],[0,-1,0]]],float);self.assertEqual(census(t,[0,1])['sharedEdgeConnectedComponents'],[[0,1]])
 def test_point_only(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[0,0,0],[-1,0,0],[0,-1,0]]],float);self.assertEqual(census(t,[0,1])['sharedEdgeConnectedComponents'],[[0],[1]])
 def test_zeroarea_bridge_forbidden(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[2,0,0],[1,-1,0]],[[0,0,0],[1,0,0],[2,0,0]]],float);r=census(t,[0,1,2]);self.assertEqual(r['sharedEdgeConnectedComponents'],[[0],[1]]);self.assertEqual(r['exactNonrenderingOriginalFaces'],[2]);self.assertEqual(r['completeOriginalFaceIds'],[0,1,2])
 def test_minuscule_real_area_kept(self):self.assertFalse(exact_nonrendering(np.array([[0,0,0],[1,0,0],[2,1e-300,0]])))
 def test_collinear_exact(self):self.assertTrue(exact_nonrendering(np.array([[1/8,1/4,1/2],[1/4,1/2,1],[3/8,3/4,3/2]])))
 def test_point_retained_no_credit(self):
  r=census(np.zeros((1,3,3)),[0]);self.assertEqual(r['exactNonrenderingOriginalFaces'],[0]);self.assertEqual(r['sharedEdgeConnectedComponents'],[]);self.assertFalse(r['rootOrContactCredit'])
 def test_invalid_ids(self):
  for ids in [[0,0],[1,0],[1.0]]:
   with self.assertRaises(AssertionError):census(np.zeros((2,3,3)),ids)
 def test_winding_no_solid(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[0,0,0],[1,0,0],[0,-1,0]]],float);r=census(t,[0,1]);self.assertEqual(r['twoFaceOrientationConflicts'],1);self.assertFalse(r['closedSolidCertification'])
 def test_source_nan_rejected(self):
  with self.assertRaises(AssertionError):census(np.full((1,3,3),np.nan),[0])
if __name__=='__main__':unittest.main()
