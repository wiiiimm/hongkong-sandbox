"""Bounded extrapolation must retain source clearance and unchanged terrain guards."""
import unittest
import numpy as np
import shapely
from bounded_original_upward_floor_return_v1_20261029 import inset
from test_bounded_original_ramp_return_v1_20261025 import square, heights


class SourceFloorReturn(unittest.TestCase):
    def setUp(self):
        self.terrain = square(10., lambda x, z: 6.)
        self.source = square(.1, lambda x, z: 4.5 + 1.5*x)
        self.before = self.source.copy()
        self.out, self.proof = inset(self.terrain, self.source)

    def test_steep_extrapolation_cannot_dig_below_source_floor(self):
        floor = self.source[:, :, 1].min() - .25
        self.assertGreaterEqual(self.out[:, :, 1].min(), floor - 1e-9)
        self.assertLessEqual(self.proof['maximumLoweringM'], 6. - floor + 1e-9)

    def test_closed_source_edges_keep_quarter_metre_clearance(self):
        for x, z in [(-.1, -.1), (-.1, 0.), (.1, -.1), (.1, .1), (0., .1)]:
            h = heights(self.out, [x, z])
            self.assertTrue(h)
            self.assertLessEqual(max(h), 4.5 + 1.5*x - .25 + 1e-8)

    def test_inputs_remote_ground_coverage_and_complexity(self):
        np.testing.assert_array_equal(self.source, self.before)
        np.testing.assert_array_equal(self.terrain, square(10., lambda x, z: 6.))
        self.assertAlmostEqual(max(heights(self.out, [9., 0.])), 6.)
        self.assertAlmostEqual(shapely.union_all(shapely.polygons(self.out[:, :, [0, 2]])).area, 400., places=6)
        self.assertAlmostEqual(self.proof['removedProjectedAreaM2'], self.proof['insertedProjectedAreaM2'], places=6)
        self.assertLessEqual(len(self.out), 25000)
        self.assertLessEqual(self.out[:, :, 1].max(), 6. + 1e-9)

    def test_closed_return_edges_do_not_step(self):
        for point in np.unique(self.out[:, :, [0, 2]].reshape(-1, 2), axis=0):
            h = heights(self.out, point)
            self.assertTrue(h)
            self.assertLess(max(h) - min(h), 1e-8)

    def test_absolute_height_floor_still_rejects(self):
        with self.assertRaises(AssertionError):
            inset(self.terrain, square(.1, lambda x, z: 1.3))


if __name__ == '__main__':
    unittest.main()
