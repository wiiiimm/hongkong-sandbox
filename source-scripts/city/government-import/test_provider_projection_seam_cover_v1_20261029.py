import unittest
import numpy as np
import shapely
from provider_projection_seam_cover_v1_20261029 import cover


def rectangle(x0, x1, length, height=5.):
    def point(x, z):
        return [x, height + z * .01, z]
    return [[point(x0, 0), point(x1, 0), point(x1, length)],
            [point(x0, 0), point(x1, length), point(x0, length)]]


class ProviderSeamTests(unittest.TestCase):
    def source(self, width=.00390625, length=31., height=5.):
        return np.asarray(rectangle(2999., 3000. - width, length, height)
                          + rectangle(3000., 3001., length, height))

    def test_measured_width_is_within_unchanged_nearest_edge_bound(self):
        source = self.source()
        before = source.copy()
        result, planes, proof = cover(source, shapely.box(2999., 0, 3001., 31.))
        self.assertTrue(np.array_equal(source, before))
        self.assertTrue(np.array_equal(result[:len(source)], source))
        self.assertGreater(len(result), len(source))
        self.assertEqual(proof['maximumSeamDistanceM'], .002)
        self.assertAlmostEqual(proof['beforeMissingAreaM2'], .00390625 * 31.)
        self.assertEqual(proof['afterMissingAreaM2'], 0.)
        self.assertEqual(len(planes), len(result) - len(source))
        np.testing.assert_allclose(result[len(source):, :, 1], 5 + result[len(source):, :, 2] * .01)

    def test_wider_hole_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'distance'):
            cover(self.source(width=.005), shapely.box(2999., 0, 3001., 31.))

    def test_large_area_rejected_even_if_narrow(self):
        with self.assertRaisesRegex(AssertionError, 'area'):
            cover(self.source(length=100.), shapely.box(2999., 0, 3001., 100.))

    def test_clamp_unchanged(self):
        with self.assertRaisesRegex(AssertionError, 'clamp'):
            cover(self.source(height=1.), shapely.box(2999., 0, 3001., 31.))

    def test_no_hole_adds_nothing(self):
        source = np.asarray(rectangle(2999., 3001., 31.))
        result, planes, proof = cover(source, shapely.box(2999., 0, 3001., 31.))
        self.assertTrue(np.array_equal(source, result))
        self.assertEqual(planes, [])
        self.assertEqual(proof['addedTerrainFaces'], 0)


if __name__ == '__main__':
    unittest.main()
