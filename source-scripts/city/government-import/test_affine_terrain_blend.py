import unittest
import numpy as np
from affine_terrain_blend_v1 import sector, evaluate


class BlendTests(unittest.TestCase):
    def test_positive_tiny_area_is_not_vertical(self):
        xz = np.array([[1000., 2000.], [1000.000001, 2000.], [1000., 2000.000001]])
        weights = np.array([0., 1., 0.])
        value = sector(xz, weights)
        np.testing.assert_allclose(evaluate(xz, value), weights, atol=1e-12)
        self.assertAlmostEqual(float(evaluate(xz.mean(0), value)), 1/3, places=6)

    def test_translation_preserves_blend(self):
        xz = np.array([[0., 0.], [3., 0.], [0., 4.]])
        weights = [0., 1., 1.]
        for offset in [np.array([0., 0.]), np.array([12000., -18000.])]:
            value = sector(xz + offset, weights)
            self.assertAlmostEqual(float(evaluate(np.array([1., 1.]) + offset, value)), 7/12)

    def test_true_collinear_is_rejected(self):
        with self.assertRaises((AssertionError, np.linalg.LinAlgError)):
            sector([[0., 0.], [1., 1.], [2., 2.]], [0., 1., 0.])
