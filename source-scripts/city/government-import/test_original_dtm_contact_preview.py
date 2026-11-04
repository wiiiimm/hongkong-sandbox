"""Protect source-grid registration and interpolation in contact diagnostics."""
import importlib.util
import unittest
from pathlib import Path
import numpy as np

spec = importlib.util.spec_from_file_location('dtm_preview', Path(__file__).with_name('xl-original-dtm-contact-preview.py'))
dtm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dtm)


class OriginalGridTests(unittest.TestCase):
    def points(self, coordinates):
        return np.array([[-34500 + c * 5, 0, -31500 + r * 5] for c, r in coordinates])

    def test_ascii_corner_is_not_the_first_sample_centre(self):
        # ESRI ASCII lower-left corner precedes its first centre by half a cell.
        points = self.points([(0, 0), (12750, 9600)])
        np.testing.assert_equal(dtm.grid_coordinates(points), [[0, 0], [12750, 9600]])

    def test_original_first_triangle_plane(self):
        grid = np.array([[10, 20], [30, 100]], dtype=float)
        result = dtm.heights(self.points([(.2, .3)]), grid, [0, 0, 1, 1])
        np.testing.assert_allclose(result, [18])

    def test_original_second_triangle_plane(self):
        grid = np.array([[10, 20], [30, 100]], dtype=float)
        result = dtm.heights(self.points([(.7, .8)]), grid, [0, 0, 1, 1])
        np.testing.assert_allclose(result, [63])

    def test_missing_original_grid_values_are_rejected(self):
        with self.assertRaises(AssertionError):
            dtm.heights(self.points([(.2, .3)]), np.array([[10, 20], [30, -9999]]), [0, 0, 1, 1])

    def test_diagnostic_uses_existing_contact_limits(self):
        passing = {'minSurfaceGap': -.5, 'minLowGap': .1, 'maxLowGap': 1}
        self.assertTrue(dtm.eligible(passing))
        for key, value in [('minSurfaceGap', -.50001), ('minLowGap', .10001), ('maxLowGap', 1.00001)]:
            self.assertFalse(dtm.eligible({**passing, key: value}))


if __name__ == '__main__':
    unittest.main()
