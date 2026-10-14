import unittest,numpy as np
from aqua_saved_context_display_v1_20261014 import plot_xyz,exact_coordinate_context,closed_display_crop
class Display(unittest.TestCase):
    def test_y_is_vertical_without_coordinate_recast(self):
        a=np.array([[[1.,170.7,-2.],[3.,5.,4.]]],dtype='<f8')
        b=plot_xyz(a);self.assertEqual(b.tolist(),[[[1.,-2.,170.7],[3.,4.,5.]]]);self.assertEqual(b.dtype,a.dtype)
    def test_duplicate_source_vertices_find_exact_continuation(self):
        a=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[1,0,0],[0,0,0],[0,-1,0]],[[1,0,0],[2,0,0],[2,1,0]],[[1+1e-12,0,0],[3,0,0],[3,1,0]]],dtype=float)
        r=exact_coordinate_context(a,[0])[0];self.assertEqual(r['exactXYZSharedVertexFaceIDs'],[0,1,2]);self.assertEqual(r['exactXYZWholeEdgeFaceIDs'],[0,1]);self.assertTrue(r['coordinateIncidenceOnlyNotAuthoredRoleOrTopology'])
    def test_nonfinite_context_rejected(self):
        with self.assertRaises(AssertionError):exact_coordinate_context(np.full((1,3,3),np.nan),[0])
    def test_closed_crop_includes_touch_and_crossing(self):
        a=np.array([[[0,0,0],[1,0,0],[0,1,0]],[[2,0,0],[3,0,0],[2,1,0]],[[.5,-2,0],[.5,2,0],[.5,0,2]]]);self.assertEqual(closed_display_crop(a,np.array([0,0,0]),np.array([1,1,1])).tolist(),[0,2])
if __name__=='__main__':unittest.main()
