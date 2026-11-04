import unittest
from fractions import Fraction as F
from exact_grade_segment_column_gap_v1_20261023 import verify

class ExactGradeSegmentTests(unittest.TestCase):
    def test_vertical_facet_above_grade_rejected(self):
        r = verify([0, 2, 0], [1, 2, 0], [[0, 3, 0], [1, 3, 0], [F(1, 2), 4, 0]])
        self.assertTrue(r['exactClosedProjectionsMeet'])
        self.assertEqual(F(r['exactMinimumColumnGapM']), -2)
        self.assertFalse(r['segmentOnOrAboveWholeGroundFacet'])
    def test_vertical_facet_below_grade(self):
        r = verify([0, 2, 0], [1, 2, 0], [[0, 0, 0], [1, 0, 0], [F(1, 2), 1, 0]])
        self.assertTrue(r['segmentOnOrAboveWholeGroundFacet'])
        self.assertEqual(F(r['exactMinimumColumnGapM']), 1)
    def test_disjoint_vertical_projection(self):
        r = verify([0, 2, 0], [1, 2, 0], [[0, 3, 1], [1, 3, 1], [F(1, 2), 4, 1]])
        self.assertFalse(r['exactClosedProjectionsMeet'])
        self.assertTrue(r['segmentOnOrAboveWholeGroundFacet'])
    def test_collapsed_high_point_is_not_omitted(self):
        p = [F(1, 2), 3, 0]
        r = verify([0, 2, 0], [1, 2, 0], [p, p, p])
        self.assertFalse(r['segmentOnOrAboveWholeGroundFacet'])
        self.assertEqual(F(r['exactMinimumColumnGapM']), -1)
    def test_non_dyadic_grade_coordinates_stay_exact(self):
        p = [F(1, 2), 1, 0]
        r = verify([F(1, 3), F(1, 3), 0], [F(2, 3), F(1, 3), 0], [p, p, p])
        self.assertEqual(F(r['exactMinimumColumnGapM']), F(-2, 3))
        self.assertTrue(all(F(v['exactSegmentPoint'][1]) == F(1, 3) for v in r['exactBasicFeasibleVertices']))
    def test_equal_ground_is_accepted_without_tolerance(self):
        r = verify([0, 2, 0], [1, 2, 0], [[0, 2, 0], [1, 2, 0], [F(1, 2), 2, 1]])
        self.assertTrue(r['segmentOnOrAboveWholeGroundFacet'])
        self.assertEqual(F(r['exactMinimumColumnGapM']), 0)

if __name__ == '__main__':
    unittest.main()
