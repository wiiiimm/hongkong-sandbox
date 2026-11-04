import copy
import unittest
from north_pair_remaining_mobile_v1_20261027 import check_report


class CompleteRetainedMobileCoverage(unittest.TestCase):
    def setUp(self):
        self.uids = ['landsd/1:0', 'landsd/2:0']
        self.expected = {u: str(i) * 64 for i, u in enumerate(self.uids)}
        self.report = dict(passed=True, errors=[], retainedOnly=True, newSourceAcceptance=False, views=[],
                           retainedNativeOwnViews=[dict(uid=u, time=t, width=390, active=True, visible=True,
                                                       fullyFramed=True, fallbackFaces=0, overflow=False,
                                                       sourceSHA256=self.expected[u], sourcePixelVisibility={'visiblePixels': 100})
                                                   for u in self.uids for t in ['15:00', '22:00']])

    def test_complete_exact_pairs_pass(self):
        self.assertTrue(check_report(self.report, self.uids, self.expected))

    def test_one_missing_night_is_not_coverage(self):
        self.report['retainedNativeOwnViews'].pop()
        with self.assertRaises(AssertionError):
            check_report(self.report, self.uids, self.expected)

    def test_duplicate_day_cannot_replace_night(self):
        self.report['retainedNativeOwnViews'][-1] = copy.deepcopy(self.report['retainedNativeOwnViews'][-2])
        with self.assertRaises(AssertionError):
            check_report(self.report, self.uids, self.expected)

    def test_hidden_target_rejected(self):
        self.report['retainedNativeOwnViews'][0]['sourcePixelVisibility']['visiblePixels'] = 0
        with self.assertRaises(AssertionError):
            check_report(self.report, self.uids, self.expected)

    def test_changed_source_rejected(self):
        self.report['retainedNativeOwnViews'][0]['sourceSHA256'] = 'changed'
        with self.assertRaises(AssertionError):
            check_report(self.report, self.uids, self.expected)

    def test_browser_error_cannot_be_waived(self):
        self.report['errors'] = ['timeout']
        with self.assertRaises(AssertionError):
            check_report(self.report, self.uids, self.expected)


if __name__ == '__main__':
    unittest.main()
