import unittest,numpy as np
from exact_original_shared_edge_component_census_20261011 import census
class Tests(unittest.TestCase):
 def test_shared_edge(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[0,0,0],[0,-1,0]]],float);self.assertEqual(census(t,[0,1])['sharedEdgeConnectedComponents'],[[0,1]])
 def test_point_only(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[0,0,0],[-1,0,0],[0,-1,0]]],float);self.assertEqual(census(t,[0,1])['sharedEdgeConnectedComponents'],[[0],[1]])
 def test_partial_collinear_edge_not_full_edge(self):
  t=np.array([[[0,0,0],[2,0,0],[0,1,0]],[[0,0,0],[1,0,0],[0,-1,0]]],float);self.assertEqual(census(t,[0,1])['sharedEdgeConnectedComponents'],[[0],[1]])
 def test_tiny_separation(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[1e-12,0,0],[0,-1,0]]]);self.assertEqual(census(t,[0,1])['sharedEdgeConnectedComponents'],[[0],[1]])
 def test_winding_conflict_retained(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[0,0,0],[1,0,0],[0,-1,0]]],float);self.assertEqual(census(t,[0,1])['twoFaceOrientationConflicts'],1)
 def test_nonmanifold_retained(self):
  t=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[0,0,0],[0,-1,0]],[[0,0,0],[1,0,0],[0,0,1]]],float);self.assertEqual(census(t,[0,1,2])['nonmanifoldEdges'],1)
 def test_collapsed_point_no_glue(self):
  t=np.array([[[0,0,0]]*3,[[0,0,0],[1,0,0],[0,1,0]]],float);r=census(t,[0,1]);self.assertEqual(r['sharedEdgeConnectedComponents'],[[0],[1]]);self.assertEqual(len(r['originalCollapsedEdgeIncidences']),3)
 def test_invalid_ids(self):
  t=np.zeros((2,3,3))
  for ids in [[0,0],[1,0],[1.0],[2]]:
   with self.assertRaises(AssertionError):census(t,ids)
 def test_no_solid_or_support_credit(self):
  r=census(np.array([[[0,0,0],[1,0,0],[0,1,0]]],float),[0]);self.assertFalse(r['rootOrContactCredit']);self.assertFalse(r['closedSolidCertification'])
if __name__=='__main__':unittest.main()
