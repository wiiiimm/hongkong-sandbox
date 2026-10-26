import unittest
from bind_exact_unapproved_recorded_top_v1_20261026 import exact_recorded_top


class ExactRecordedTop(unittest.TestCase):
    def test_adjacent_binary_sum_matches_exact_decimal_record(self):
        self.assertEqual(exact_recorded_top(dict(recordedBaseHeight=4.9, recordedTopHeight=4.9+5.2),
                                           dict(baseHeightHKPD=4.9, height=5.2, topHeightHKPD=10.1)), (10.1, True))

    def test_exact_binding_is_preserved(self):
        self.assertEqual(exact_recorded_top(dict(recordedBaseHeight=4.9, recordedTopHeight=10.1),
                                           dict(baseHeightHKPD=4.9, height=5.2, topHeightHKPD=10.1)), (10.1, False))

    def test_millimetre_record_change_is_rejected(self):
        with self.assertRaises(AssertionError):
            exact_recorded_top(dict(recordedBaseHeight=4.9, recordedTopHeight=4.9+5.2),
                               dict(baseHeightHKPD=4.9, height=5.2, topHeightHKPD=10.101))

    def test_rounded_inconsistent_decimal_height_is_rejected(self):
        with self.assertRaises(AssertionError):
            exact_recorded_top(dict(recordedBaseHeight=4.9, recordedTopHeight=10.100000000000001),
                               dict(baseHeightHKPD=4.9, height=5.200000000000001, topHeightHKPD=10.1))


if __name__ == '__main__':
    unittest.main()
