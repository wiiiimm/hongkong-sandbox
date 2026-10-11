import unittest
import numpy as np
from original_tin_point_diagnostic import indexed_surface, point_heights


class OriginalTINPointTests(unittest.TestCase):
    def test_slope_and_boundary_on_exact_planes(self):
        tri = [[[0, 1, 0], [2, 3, 0], [0, 5, 2]]]
        si, heights, highest = point_heights([[.5, 0, .5], [1, 0, 1], [3, 0, 3]], indexed_surface(tri))
        np.testing.assert_array_equal(si, [0, 1])
        np.testing.assert_allclose(heights, [2.5, 4])
        self.assertTrue(np.isneginf(highest[2]))

    def test_highest_facet_is_not_any_compatible_lower_facet(self):
        tri = [[[0, 1, 0], [2, 1, 0], [0, 1, 2]], [[0, 4, 0], [2, 4, 0], [0, 4, 2]]]
        si, heights, highest = point_heights([[.5, 2, .5]], indexed_surface(tri))
        self.assertEqual(set(heights), {1, 4})
        self.assertEqual(highest[0], 4)

    def test_vertical_faces_do_not_define_height_field(self):
        tri = [[[0, 1, 0], [0, 4, 0], [0, 1, 2]]]
        si, heights, highest = point_heights([[0, 0, 1]], indexed_surface(tri))
        self.assertEqual(len(si), 0)
        self.assertTrue(np.isneginf(highest[0]))

    def test_duplicate_shared_boundary_keeps_same_plane(self):
        tri = [[[0, 2, 0], [2, 2, 0], [0, 2, 2]], [[2, 2, 2], [0, 2, 2], [2, 2, 0]]]
        si, heights, highest = point_heights([[1, 0, 1]], indexed_surface(tri))
        self.assertEqual(len(si), 2)
        np.testing.assert_allclose(highest, [2])


if __name__ == '__main__':
    unittest.main()
