import unittest,numpy as np
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces
class Winding(unittest.TestCase):
 def test_negative_zero_y_does_not_trigger_renderer_swap(self):
  f,p=drawn_native_faces(dict(position=[0,2,0,1,2,-0.0,1,2,0],index=[0,1,2]));self.assertEqual(p['onlyRendererRequiredBCSwapFaceIDs'],[]);self.assertTrue(np.signbit(f[0,1,2]))
 def test_negative_y_only_swaps_bc(self):
  f,p=drawn_native_faces(dict(position=[0,2,0,1,2,0,0,2,1],index=[0,1,2]));np.testing.assert_array_equal(f,[[[0,2,0],[0,2,1],[1,2,0]]]);self.assertEqual(p['onlyRendererRequiredBCSwapFaceIDs'],[0])
 def test_positive_y_winding_remains_exact(self):
  f,p=drawn_native_faces(dict(position=[0,2,0,0,2,1,1,2,0],index=[0,1,2]));np.testing.assert_array_equal(f,[[[0,2,0],[0,2,1],[1,2,0]]]);self.assertEqual(p['onlyRendererRequiredBCSwapFaceIDs'],[])
 def test_zero_y_face_retained_with_original_order(self):
  f,p=drawn_native_faces(dict(position=[0,0,0,0,1,0,0,1,1],index=[0,1,2]));np.testing.assert_array_equal(f,[[[0,0,0],[0,1,0],[0,1,1]]]);self.assertEqual(p['onlyRendererRequiredBCSwapFaceIDs'],[])
 def test_complete_unused_vertices_are_accounted(self):
  _,p=drawn_native_faces(dict(position=[0,2,0,1,2,0,0,2,1,40,50,60],index=[0,1,2]));self.assertEqual(p['completePOSITIONVertices'],4);self.assertEqual(p['unusedPOSITIONVertices'],1)
 def test_float32_cast_precedes_winding_and_returns_literal_xyz(self):
  v=[0,2.00000001,0,1,2.00000001,0,0,2.00000001,1];f,_=drawn_native_faces(dict(position=v,index=[0,1,2]));self.assertTrue(np.array_equal(f,f.astype(np.float32).astype(float)));self.assertTrue((f[:,:,1]==2).all())
 def test_invalid_index_not_rounded(self):
  with self.assertRaises(AssertionError):drawn_native_faces(dict(position=[0,2,0,1,2,0,0,2,1],index=[0,1,2.5]))
 def test_nonfinite_or_missing_position_rejected(self):
  with self.assertRaises(AssertionError):drawn_native_faces(dict(position=[0,float('nan'),0,1,2,0,0,2,1],index=[0,1,2]))
 def test_duplicate_triangles_keep_multiplicity(self):
  f,p=drawn_native_faces(dict(position=[0,2,0,1,2,0,0,2,1],index=[0,1,2,0,1,2]));self.assertEqual(len(f),2);np.testing.assert_array_equal(f[0],f[1]);self.assertEqual(p['onlyRendererRequiredBCSwapFaceIDs'],[0,1])
if __name__=='__main__':unittest.main()
