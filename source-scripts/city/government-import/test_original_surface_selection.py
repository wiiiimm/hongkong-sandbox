"""Exact rendered facet selection keeps source heights and clips plane crossings."""
import copy
import unittest
import numpy as np
import shapely
from original_surface_selection_bounded import lower_original_surface_projection


class Surface:
    def __init__(self, heights):
        self.faces = np.array([[[0, heights[0], 0], [1, heights[1], 0], [0, heights[2], 1]]])
        self.calls = 0

    def surface_faces(self, mask):
        self.calls += 1
        return self.faces


class LowerOriginalFacetsTests(unittest.TestCase):
    def select(self, old, new, mask=None):
        patch = {'nativeMesh': {'position': [0, old[0], 0, 1, old[1], 0, 0, old[2], 1], 'index': [0, 1, 2]}}
        original = copy.deepcopy(patch)
        surface = Surface(new)
        before = surface.faces.copy()
        region, proof = lower_original_surface_projection(patch, [0, 0, 1, 1], shapely.box(0, 0, 1, 1) if mask is None else mask, surface)
        self.assertEqual(patch, original)
        np.testing.assert_array_equal(surface.faces, before)
        return region, proof, surface

    def test_lower_exact_native_facets_need_no_grid_metadata(self):
        region, proof, surface = self.select([2]*3, [1]*3)
        self.assertAlmostEqual(region.area, .5)
        self.assertEqual(surface.calls, 1)
        self.assertEqual(proof['planePairs'], 1)

    def test_equal_or_higher_alternative_is_excluded(self):
        for heights in ([2]*3, [3]*3):
            self.assertTrue(self.select([2]*3, heights)[0].is_empty)

    def test_crossing_original_planes_are_clipped(self):
        region, _, _ = self.select([0, 2, 0], [1]*3)
        self.assertAlmostEqual(region.area, .125, places=7)
        self.assertGreater(region.bounds[0], .5)

    def test_selection_is_bounded_to_supplied_region(self):
        region, _, _ = self.select([2]*3, [1]*3, shapely.box(.75, 0, 1, 1))
        self.assertAlmostEqual(region.area, .03125)

    def test_outside_mask_does_not_read_source(self):
        region, _, surface = self.select([2]*3, [1]*3, shapely.box(2, 2, 3, 3))
        self.assertTrue(region.is_empty)
        self.assertEqual(surface.calls, 0)


if __name__ == '__main__':
    unittest.main()
