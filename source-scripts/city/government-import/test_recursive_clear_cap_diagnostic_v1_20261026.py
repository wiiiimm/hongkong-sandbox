import unittest
import numpy as np
from original_recursive_clear_cap_diagnostic_v1_20261026 import expand


class ExactContinuationTests(unittest.TestCase):
    wall = [[0., 0., 0.], [0., 2., 0.], [0., 2., 1.]]
    roof = [[0., 2., 0.], [0., 2., 1.], [1., 2., 0.]]

    def test_positive_line_reaches_clear_cap(self):
        result = expand(np.asarray([self.wall, self.roof]), [0], [0])
        self.assertEqual(result['rows'][0]['originalFacePath'], [0, 1])

    def test_point_contact_never_bridges(self):
        point_roof = [[0., 2., 1.], [0., 2., 2.], [1., 2., 1.]]
        result = expand(np.asarray([self.wall, point_roof]), [0], [0])
        self.assertFalse(result['allUnresolvedHavePaths'])

    def test_ground_negative_roof_cannot_be_cap(self):
        result = expand(np.asarray([self.wall, self.roof]), [0, 1], [0])
        self.assertFalse(result['allUnresolvedHavePaths'])


if __name__ == '__main__':
    unittest.main()
