import unittest,numpy as np
from exact_original_body_boundary_group_census_v1_20261011 import census

class OriginalBoundaryCensusTests(unittest.TestCase):
 def test_triangulated_quad_has_one_complete_four_edge_loop(self):
  w=np.array([[[0,0,0],[1,0,0],[1,0,1]],[[0,0,0],[1,0,1],[0,0,1]]],float);r=census(w,[0,1]);self.assertEqual(r['completeIncidenceOneBoundaryEdges'],4);self.assertTrue(r['completeIncidenceOneBoundaryGroups'][0]['closedConnectedDegreeTwoLoop']);self.assertFalse(r['originalHoleCertified'])
 def test_point_shared_triangles_retain_branch_and_no_opening_loop(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[0,0,0],[-1,0,0],[0,0,-1]]],float);r=census(w,[0,1]);self.assertEqual(len(r['completeIncidenceOneBoundaryGroups']),1);self.assertFalse(r['completeIncidenceOneBoundaryGroups'][0]['closedConnectedDegreeTwoLoop'])
 def test_disconnected_loops_never_combined(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[3,0,0],[4,0,0],[3,0,1]]],float);r=census(w,[0,1]);self.assertEqual(len(r['completeIncidenceOneBoundaryGroups']),2)
 def test_zero_original_facet_retained_without_boundary_credit(self):
  w=np.array([[[0,0,0],[1,0,0],[2,0,0]]],float);r=census(w,[0]);self.assertEqual(r['exactZeroAreaOriginalFaces'],[0]);self.assertEqual(r['completeIncidenceOneBoundaryEdges'],0);self.assertEqual(r['completeOriginalFaceIds'],[0])
 def test_duplicate_nonzero_facets_do_not_create_fake_boundary(self):
  a=[[0,0,0],[1,0,0],[0,0,1]];r=census(np.array([a,a,a],float),[0,1,2]);self.assertEqual(len(r['nonmanifoldOriginalEdges']),3);self.assertEqual(r['completeIncidenceOneBoundaryEdges'],0)
 def test_changed_world_rejects_frozen_binding(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]]],float);r=census(w,[0]);v=w.copy();v[0,0,0]=.01
  with self.assertRaises(AssertionError):census(v,[0],expected_binding=r['binding'])
 def test_partial_face_list_rejects_complete_binding(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[0,0,0],[0,0,1],[-1,0,0]]],float);r=census(w,[0,1])
  with self.assertRaises(AssertionError):census(w,[0],expected_binding=r['binding'])
 def test_nonfinite_and_repeated_ids_rejected(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]]],float)
  with self.assertRaises(AssertionError):census(w,[0,0])
  w[0,0,0]=np.nan
  with self.assertRaises(AssertionError):census(w,[0])
if __name__=='__main__':unittest.main()
