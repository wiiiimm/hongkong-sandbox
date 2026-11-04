"""The optional native scanner must still run for closed-bound contacts."""
import unittest
from run_original_scene_checks_v2_20261026 import needs_native_finite_contacts


def scene(bounds=None):
    return dict(rows=[dict(completeSourceFourWorldBounds=[[0, 0, 0], [1, 1, 1]],
                           nearbyNativeActors=[] if bounds is None else [dict(completeFourWorldBounds=bounds)])])


class NativeBranch(unittest.TestCase):
    def test_empty_native_nomination_uses_basic_only_checks(self):
        self.assertFalse(needs_native_finite_contacts(scene()))

    def test_strict_gap_can_skip_triangle_scan(self):
        self.assertFalse(needs_native_finite_contacts(scene([[1.00000001, 0, 0], [2, 1, 1]])))

    def test_touching_closed_bounds_requires_exact_scan(self):
        self.assertTrue(needs_native_finite_contacts(scene([[1, 0, 0], [2, 1, 1]])))

    def test_overlapping_bounds_requires_exact_scan(self):
        self.assertTrue(needs_native_finite_contacts(scene([[.5, .5, .5], [2, 2, 2]])))


if __name__ == '__main__':
    unittest.main()
