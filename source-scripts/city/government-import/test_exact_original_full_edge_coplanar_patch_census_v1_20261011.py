import unittest,numpy as np
from exact_original_full_edge_coplanar_patch_census_v1_20261011 import verify

class OriginalCoplanarPatchTests(unittest.TestCase):
 def quad(self):return np.array([[[0,0,0],[0,0,1],[1,0,1]],[[0,0,0],[1,0,1],[1,0,0]]],float)
 def test_complete_source_quad_is_one_four_boundary_patch(self):
  r=verify(self.quad(),[0,1]);self.assertEqual(len(r['allSourceDefinedFullEdgeCoplanarPatches']),1);self.assertTrue(r['allSourceDefinedFullEdgeCoplanarPatches'][0]['allPatchFacesExactUpward']);self.assertEqual(r['allSourceDefinedFullEdgeCoplanarPatches'][0]['completePatchBoundaryInventory']['completeIncidenceOneBoundaryEdges'],4)
 def test_exact_non_coplanar_shared_edge_splits(self):
  w=self.quad();w[1,2,1]=.01;r=verify(w,[0,1]);self.assertEqual(len(r['allSourceDefinedFullEdgeCoplanarPatches']),2)
 def test_nextafter_plane_difference_never_welded(self):
  w=self.quad();w[1,2,1]=np.nextafter(0.,1.);r=verify(w,[0,1]);self.assertEqual(len(r['allSourceDefinedFullEdgeCoplanarPatches']),2)
 def test_point_contact_is_not_full_edge_patch(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[0,0,0],[-1,0,0],[0,0,-1]]],float);r=verify(w,[0,1]);self.assertEqual(len(r['allSourceDefinedFullEdgeCoplanarPatches']),2)
 def test_zero_area_original_retained_outside_patches(self):
  w=np.concatenate((self.quad(),np.array([[[0,0,0],[1,0,0],[2,0,0]]],float)));r=verify(w,[0,1,2]);self.assertEqual(r['exactZeroAreaOriginalFaces'],[2]);self.assertEqual(r['completeOriginalBodyFaces'],[0,1,2])
 def test_mixed_winding_does_not_certify_upward_roof(self):
  w=self.quad();w[1]=w[1,::-1];r=verify(w,[0,1]);self.assertFalse(r['allSourceDefinedFullEdgeCoplanarPatches'][0]['allPatchFacesExactUpward'])
 def test_closed_body_can_contain_surface_patch_loops(self):
  w=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[0,0,0],[0,1,0],[1,0,0]],[[0,0,0],[0,0,1],[0,1,0]],[[1,0,0],[0,1,0],[0,0,1]]],float);r=verify(w,list(range(4)));self.assertEqual(len(r['allSourceDefinedFullEdgeCoplanarPatches']),4);self.assertTrue(all(p['completePatchBoundaryInventory']['completeIncidenceOneBoundaryEdges']==3 for p in r['allSourceDefinedFullEdgeCoplanarPatches']));self.assertFalse(r['visualRoleAccepted'])
 def test_changed_or_partial_body_rejects_frozen_binding(self):
  w=self.quad();r=verify(w,[0,1])
  with self.assertRaises(AssertionError):verify(w,[0],expected_binding=r['binding'])
  w[0,0,0]=.1
  with self.assertRaises(AssertionError):verify(w,[0,1],expected_binding=r['binding'])
if __name__=='__main__':unittest.main()
