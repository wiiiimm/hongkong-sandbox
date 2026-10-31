import unittest
from original_four_world_degenerate_partition_v1_20261026 import primitive_dimension

class PrimitiveDimensionTests(unittest.TestCase):
    def test_point(self):
        self.assertEqual(primitive_dimension([[1, 2, 3]] * 3), 0)
    def test_collinear_distinct_vertices(self):
        self.assertEqual(primitive_dimension([[0, 0, 0], [1, 2, 3], [2, 4, 6]]), 1)
    def test_tiny_positive_area_is_not_degenerate(self):
        self.assertEqual(primitive_dimension([[0, 0, 0], [1, 0, 0], [2, 2**-100, 0]]), 2)
    def test_nonfinite_rejected(self):
        with self.assertRaises(AssertionError):
            primitive_dimension([[0, 0, 0], [1, 0, 0], [2, float('nan'), 0]])

if __name__ == '__main__':
    unittest.main()
