import unittest
from retained_cell_partition import validate_partition


class RetainedPartitionTests(unittest.TestCase):
    parent = {'w': 100, 'h': 100}

    @staticmethod
    def extent(cells, parent):
        return [value * 70 for value in cells]

    def check(self, cells, world=None, retained=None):
        return validate_partition(cells, world or [[[75, 0, 75], [120, 40, 120]]],
                                  retained or [0, 0, 2, 2], self.parent, self.extent)

    def test_valid_transition_and_full_retained_extent(self):
        self.assertEqual(self.check([0, 0, 2, 2]), [0, 0, 2, 2])

    def test_missing_retained_cells_rejected_even_when_source_fits(self):
        with self.assertRaises(AssertionError):
            self.check([0, 0, 2, 2], retained=[0, 0, 3, 2])

    def test_all_sources_need_original_transition_margin(self):
        with self.assertRaises(AssertionError):
            self.check([0, 0, 2, 2], world=[[[75, 0, 75], [120, 40, 120]],
                                        [[90, 0, 90], [135, 40, 120]]])

    def test_outside_root_grid_rejected(self):
        with self.assertRaises(AssertionError):
            self.check([0, 0, 100, 2])

    def test_fractional_and_reversed_cell_bounds_rejected(self):
        for cells in [[0, 0, 2.0, 2], [2, 0, 0, 2], [0, 2, 2, 0]]:
            with self.subTest(cells=cells), self.assertRaises(AssertionError):
                self.check(cells)


if __name__ == '__main__':
    unittest.main()
