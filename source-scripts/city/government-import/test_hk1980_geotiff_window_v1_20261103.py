import unittest
from hk1980_geotiff_window_v1_20261103 import window


class GeoTIFFWindowTests(unittest.TestCase):
    def tags(self):
        return {34735: (1, 1, 0, 3, 1024, 0, 1, 1, 1025, 0, 1, 1, 3072, 0, 1, 2326),
                33550: (.2, .2, 0), 33922: (0, 0, 0, 1000, 2000, 0)}

    def test_outward_crop_exact_unfitted_extent(self):
        value = window(self.tags(), (100, 100), (1001.01, 1997.01, 1002.99, 1998.99))
        self.assertEqual(value['pixelWindow'], [5, 5, 15, 15])
        self.assertEqual(value['hk1980Extent'], [1001, 1003, 1997, 1999])
        self.assertFalse(value['fittedTransform'])

    def test_wrong_crs_and_point_pixels_fail(self):
        for key, value in [(3072, 3857), (1025, 2)]:
            tags = self.tags(); keys = list(tags[34735]); i = keys.index(key); keys[i + 3] = value; tags[34735] = keys
            with self.assertRaises(AssertionError):
                window(tags, (100, 100), (1001, 1997, 1003, 1999))

    def test_clipping_and_rotation_fail(self):
        with self.assertRaises(AssertionError):
            window(self.tags(), (100, 100), (999, 1997, 1003, 1999))
        tags = self.tags(); tags[34264] = tuple(range(16))
        with self.assertRaises(AssertionError):
            window(tags, (100, 100), (1001, 1997, 1003, 1999))

    def test_unbounded_decode_and_invalid_scale_fail(self):
        with self.assertRaises(AssertionError):
            window(self.tags(), (400_000_001, 1), (1001, 1997, 1003, 1999))
        tags = self.tags(); tags[33550] = (.2, -.2, 0)
        with self.assertRaises(AssertionError):
            window(tags, (100, 100), (1001, 1997, 1003, 1999))


if __name__ == '__main__':
    unittest.main()
