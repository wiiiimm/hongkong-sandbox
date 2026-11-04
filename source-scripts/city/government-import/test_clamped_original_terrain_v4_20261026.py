import unittest
import numpy as np
import shapely
from clamped_original_terrain_v4_20261026 import clamp_surface, surface_plane
plane = surface_plane


class ClampSurfaceTests(unittest.TestCase):
    def verify_surface(self, face):
        original = np.asarray([face], float)
        frozen = original.copy()
        output, proof = clamp_surface(original, floor=1.2)
        np.testing.assert_array_equal(original, frozen)
        expected_plane = plane(original[0])
        for triangle in output:
            actual_plane = plane(triangle)
            for weights in [[1/3]*3, [.7,.2,.1], [.1,.7,.2], [.2,.1,.7]]:
                point = np.asarray(weights) @ triangle
                expected = max(1.2, point[[0,2]] @ expected_plane[:2]+expected_plane[2])
                self.assertAlmostEqual(point[[0,2]] @ actual_plane[:2]+actual_plane[2], expected, places=9)
        self.assertFalse(proof['installationApproved'])
        return output

    def test_unchanged_high_surface(self):
        face=[[0,2,0],[4,3,0],[0,4,4]]
        np.testing.assert_array_equal(self.verify_surface(face), [face])

    def test_fully_low_surface(self):
        output=self.verify_surface([[0,-2,0],[4,1,0],[0,0,4]])
        np.testing.assert_array_equal(output[:,:,1], np.full(output.shape[:2],1.2))

    def test_one_low_vertex(self):
        self.verify_surface([[0,0,0],[4,4,0],[0,4,4]])

    def test_two_low_vertices(self):
        self.verify_surface([[0,0,0],[4,0,0],[0,4,4]])

    def test_level_vertex_and_reversed_winding(self):
        self.verify_surface([[0,1.2,0],[0,4,4],[4,-2,0]])

    def test_positive_small_facet_preserved(self):
        self.verify_surface([[0,0,0],[1e-6,4,0],[0,4,1e-6]])

    def test_real_narrow_terrain_crossing(self):
        # Polygon difference created a microscopic sliver retaining the low
        # original vertex in the high piece. Direct opposite clips avoid it.
        self.verify_surface([[1651.0625,1.3122997283862787,-930.25],
            [1649.5625,1.169799804680224,-928.875],
            [1651.0625,4.118499755852099,-930.1875]])

    def test_wrong_inherited_plane_refused(self):
        with self.assertRaises(AssertionError):
            clamp_surface([[[0,0,0],[4,4,0],[0,4,4]]],floor=1.2,
                          source_planes=[[0.,0.,10.]])

    def test_arbitrary_floor_refused(self):
        with self.assertRaises(AssertionError):
            clamp_surface([[[0,0,0],[1,2,0],[0,3,1]]],floor=0.)

    def test_duplicate_projection_refused(self):
        face=[[0,2,0],[4,3,0],[0,4,4]]
        with self.assertRaises(AssertionError):clamp_surface([face,face],floor=1.2)


if __name__=='__main__':unittest.main()
