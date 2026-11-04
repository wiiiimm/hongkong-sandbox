"""Higher-parent selection must preserve the original clearance interval."""
import importlib.util
from pathlib import Path
import unittest
import shapely

spec = importlib.util.spec_from_file_location('contact_parent', Path(__file__).with_name('xl-green18-original-parent-contact.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Sampler:
    g = {'bE': 834500, 'bN': 816500, 'aE': 2, 'aN': -2}
    dem = {'h': 2}
    w = 2

    def __init__(self, height, slope=0):
        self.height = height
        self.slope = slope

    def ground(self, x, z):
        return self.height + self.slope * x


def patch(height):
    return {'nativeMesh': {'position': [0, height, 0, 2, height, 0, 0, height, 2,
                                       2, height, 0, 2, height, 2, 0, height, 2],
                           'index': [0, 1, 2, 3, 4, 5]}}


class SelectionTests(unittest.TestCase):
    def select(self, parent, native=0):
        return module.select(patch(native), [0, 0, 2, 2], shapely.box(0, 0, 2, 2), parent, 4, 5.5)[0]

    def test_higher_original_parent_inside_band_is_kept(self):
        self.assertAlmostEqual(self.select(Sampler(5)).area, 4)

    def test_parent_above_ceiling_is_rejected(self):
        self.assertTrue(self.select(Sampler(6)).is_empty)

    def test_parent_below_floor_is_rejected(self):
        self.assertTrue(self.select(Sampler(3)).is_empty)

    def test_lower_parent_does_not_qualify_for_floating_rim(self):
        self.assertTrue(self.select(Sampler(5), native=6).is_empty)

    def test_sloped_parent_is_clipped_at_exact_band_boundary(self):
        selected = self.select(Sampler(4, slope=1))
        self.assertAlmostEqual(selected.area, 3)
        self.assertAlmostEqual(selected.bounds[2], 1.5)

    def test_parent_cannot_extend_outside_original_projection(self):
        projection = shapely.box(0, 0, 1, 1)
        selected, _ = module.select(patch(0), [0, 0, 2, 2], projection, Sampler(5), 4, 5.5)
        self.assertTrue(projection.covers(selected))
        self.assertAlmostEqual(selected.area, 1)


if __name__ == '__main__':
    unittest.main()
