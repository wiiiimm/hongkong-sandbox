import unittest
from hk1980_geotiff_matrix_window_v1_20261103 import matrix_window


class MatrixTests(unittest.TestCase):
    def tags(self):
        return {34264: (.25, 0, 0, 845000, 0, -.25, 0, 827000, 0, 0, 1, 0, 0, 0, 0, 1),
                34735: (1, 1, 0, 2, 1024, 0, 1, 1, 3072, 0, 1, 2326)}
    world = '.25\n0\n0\n-.25\n845000.125\n826999.875\n'
    bounds = (845636.41015625, 826788.603515625, 845702.58984375, 826856.7734375)

    def test_actual_dated_tile_metadata(self):
        result = matrix_window(self.tags(), (15000, 12000), self.bounds, self.world)
        self.assertEqual(result['pixelWindow'], [2545, 572, 2811, 846])
        self.assertEqual(result['hk1980Extent'], [845636.25, 845702.75, 826788.5, 826857])
        self.assertFalse(result['rawSourceTagsChanged'])

    def test_half_pixel_and_missing_world_file_fail(self):
        for world in ['', self.world.replace('845000.125', '845000')]:
            with self.assertRaises(AssertionError):
                matrix_window(self.tags(), (15000, 12000), self.bounds, world)

    def test_rotation_wrong_crs_and_extra_matrix_transform_fail(self):
        for target in ['rotation', 'crs', 'z']:
            tags = {k: list(v) for k, v in self.tags().items()}
            if target == 'rotation': tags[34264][1] = .01
            if target == 'crs': tags[34735][-1] = 3857
            if target == 'z': tags[34264][11] = 1
            with self.assertRaises(AssertionError):
                matrix_window(tags, (15000, 12000), self.bounds, self.world)


if __name__ == '__main__':
    unittest.main()
