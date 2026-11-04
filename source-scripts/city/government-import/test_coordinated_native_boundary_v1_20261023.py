import unittest
from fractions import Fraction as F
import numpy as np
from coordinated_native_boundary_v1_20261023 import seam_segments,compatible_seam


def segment(a,b,ya,yb):return tuple(map(F,[a,b,ya,yb]))+(0,)


class BoundaryProof(unittest.TestCase):
    def setUp(self):self.flat=[segment(0,2,3,3)]
    def test_equal_surface_different_segmentation(self):
        p=compatible_seam(self.flat,[segment(0,1,3,3),segment(1,2,3,3)],0,2)
        self.assertEqual(p['maximumErrorM'],0)
    def test_internal_upper_envelope_kink_cannot_hide_mismatch(self):
        with self.assertRaises(AssertionError):compatible_seam([segment(0,2,0,2),segment(0,2,2,0)],[segment(0,2,2,2)],0,2)
    def test_isolated_point_spike_rejected(self):
        with self.assertRaises(AssertionError):compatible_seam(self.flat,self.flat+[segment(1,1,5,5)],0,2)
    def test_point_spikes_cannot_hide_open_interval_gap(self):
        right=[segment(0,2,2,2),segment(0,0,3,3),segment(2,2,3,3)]
        with self.assertRaises(AssertionError):compatible_seam(self.flat,right,0,2)
    def test_missing_interval_rejected(self):
        with self.assertRaises(AssertionError):compatible_seam(self.flat,[segment(0,F(9,10),3,3),segment(F(11,10),2,3,3)],0,2)
    def test_one_centimetre_is_not_accepted(self):
        with self.assertRaises(AssertionError):compatible_seam(self.flat,[segment(0,2,F(301,100),F(301,100))],0,2)
    def test_smaller_existing_tolerance_difference_measured(self):
        p=compatible_seam(self.flat,[segment(0,2,F(3001,1000),F(3001,1000))],0,2)
        self.assertAlmostEqual(p['maximumErrorM'],.001)
    def test_vertical_faces_do_not_bridge_missing_surface(self):
        tri=np.array([[[0,1,0],[0,2,0],[0,1,2]]],float)
        self.assertEqual(seam_segments(tri,0,0,0,2),[])
    def test_exact_finite_triangle_boundary(self):
        tri=np.array([[[0,3,0],[1,3,0],[0,3,2]]],float)
        self.assertEqual(seam_segments(tri,0,0,0,2)[0][:4],tuple(map(F,[0,2,3,3])))
    def test_plane_touches_boundary_at_isolated_vertex(self):
        tri=np.array([[[0,5,1],[1,4,0],[1,4,2]]],float)
        self.assertEqual(seam_segments(tri,0,0,0,2)[0][:4],tuple(map(F,[1,1,5,5])))
    def test_nan_is_rejected(self):
        with self.assertRaises(AssertionError):seam_segments(np.array([[[0,3,0],[1,float('nan'),0],[0,3,2]]]),0,0,0,2)


if __name__=='__main__':unittest.main()
