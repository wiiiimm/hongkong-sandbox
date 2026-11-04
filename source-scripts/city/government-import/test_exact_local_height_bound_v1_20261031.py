from fractions import Fraction
import unittest

import numpy as np

from exact_local_height_bound_v1_20261031 import height_fraction, cannot_have_negative_gap
from exact_original_triangle_pair_column_gap_20261010 import verify


class ExactHeightBound(unittest.TestCase):
    def test_threshold_is_exact_and_inclusive(self):
        self.assertTrue(cannot_have_negative_gap(Fraction(1), Fraction(3, 2)))
        self.assertFalse(cannot_have_negative_gap(Fraction(1), Fraction(3, 2)+Fraction(1, 10**30)))

    def test_one_ulp_below_threshold_is_not_pruned(self):
        self.assertFalse(cannot_have_negative_gap(height_fraction(np.nextafter(1., -np.inf)), height_fraction(1.5)))

    def test_sloping_source_and_ground_agree_with_independent_exact_solver(self):
        ground = np.array([[0., 0., 0.], [1., 1., 0.], [0., .5, 1.]])
        for floor in [.5, 1., 10., 1e8]:
            source = ground.copy()
            source[:, 1] += floor
            bound = cannot_have_negative_gap(height_fraction(source[:, 1].min()), height_fraction(ground[:, 1].max()))
            if bound:
                proof = verify(source, ground)
                self.assertTrue(proof['exactClosedHorizontalProjectionsMeet'])
                self.assertGreaterEqual(Fraction(proof['exactMinimumFiniteColumnGapM']), Fraction(-1, 2))

    def test_vertical_and_collapsed_primitives_remain_in_scope(self):
        terrain = np.array([[0., 0., 0.], [0., 1., 0.], [0., .5, 0.]])
        for source in [np.array([[0., 2., 0.]] * 3),
                       np.array([[0., 2., 0.], [1., 3., 0.], [0., 2., 1.]])]:
            self.assertTrue(cannot_have_negative_gap(height_fraction(source[:, 1].min()), height_fraction(terrain[:, 1].max())))
            proof = verify(source, terrain)
            self.assertGreaterEqual(Fraction(proof['exactMinimumFiniteColumnGapM']), Fraction(-1, 2))

    def test_uncertain_pair_is_sent_to_exact_solver(self):
        self.assertFalse(cannot_have_negative_gap(Fraction(0), Fraction(2)))

    def test_nonfinite_heights_are_rejected(self):
        for value in [float('nan'), float('inf'), -float('inf')]:
            with self.assertRaises(AssertionError):
                height_fraction(value)


if __name__ == '__main__':
    unittest.main()
