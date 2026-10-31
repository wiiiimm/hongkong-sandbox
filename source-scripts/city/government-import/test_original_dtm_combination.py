"""Original terrain selection must keep valid facets and reject invalid heights."""
import importlib.util
import unittest
from pathlib import Path
import shapely

spec = importlib.util.spec_from_file_location('dtm_combo', Path(__file__).with_name('xl-original-dtm-combined-terrain-followthrough.py'))
combo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(combo)


class OriginalSurfaceSelectionTests(unittest.TestCase):
    def mesh(self, heights):
        return {'nativeMesh': {'position': [0, heights[0], 0, 1, heights[1], 0, 0, heights[2], 1], 'index': [0, 1, 2]}}

    def selected(self, old, new, floor=.5, ceiling=1.5):
        return combo.select_original_dtm(self.mesh(old), self.mesh(new), shapely.box(0, 0, 1, 1), floor, ceiling)

    def test_valid_original_plane_is_kept(self):
        self.assertTrue(self.selected([1]*3, [1]*3).is_empty)

    def test_original_dtm_can_cover_a_too_low_or_high_plane(self):
        for old in [0, 2]:
            self.assertAlmostEqual(self.selected([old]*3, [1]*3).area, .5)

    def test_outside_band_dtm_cannot_be_selected(self):
        for new in [0, 2]:
            self.assertTrue(self.selected([0]*3, [new]*3).is_empty)

    def test_sloping_original_plane_is_clipped_without_height_edits(self):
        region = self.selected([0]*3, [.25, 1.25, .25], .75, 1.5)
        self.assertAlmostEqual(region.area, .125)
        self.assertGreaterEqual(region.bounds[0], .5)


if __name__ == '__main__':
    unittest.main()
