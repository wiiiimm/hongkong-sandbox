import copy
import unittest
from june_garden_reuse_completed_live_v1_20261103 import OLD, OLD_LOCAL, read, validate_mobile


class ActualMobileReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = read(OLD / 'viewport-390/live-browser.json')
        cls.config = read(OLD_LOCAL / 'browser-config-390.json')
        cls.sources = {r['uid']: r for r in read(OLD / 'ROOT-MOBILE-RUNTIME-READBACK.json')['all75CurrentSourceAssetsRehashed']}

    def test_complete_actual_mobile_report(self):
        own, held = validate_mobile(self.report, self.config, self.sources)
        self.assertEqual((len(own), len(held)), (12, 138))

    def test_missing_duplicate_and_wrong_time_rejected(self):
        for mutate in [lambda r: r['retainedNativeOwnViews'].pop(),
                       lambda r: r['views'].__setitem__(0, r['views'][1]),
                       lambda r: r['views'][0].__setitem__('time', '12:00')]:
            value = copy.deepcopy(self.report); mutate(value)
            with self.assertRaises(AssertionError): validate_mobile(value, self.config, self.sources)

    def test_changed_hash_unframed_or_occluded_rejected(self):
        for key, value in [('sourceSHA256', '0' * 64), ('fullyFramed', False), ('fallbackFaces', 1)]:
            report = copy.deepcopy(self.report); report['retainedNativeOwnViews'][0][key] = value
            with self.assertRaises(AssertionError): validate_mobile(report, self.config, self.sources)
        report = copy.deepcopy(self.report); report['views'][0]['sourcePixelVisibility']['visiblePixels'] = 0
        with self.assertRaises(AssertionError): validate_mobile(report, self.config, self.sources)

    def test_missing_joint_or_unrestored_basic_rejected(self):
        report = copy.deepcopy(self.report); report['jointViews'].pop()
        with self.assertRaises(AssertionError): validate_mobile(report, self.config, self.sources)
        report = copy.deepcopy(self.report); report['retainedDeselectionFallbacks'][0]['basicHidden'] = True
        with self.assertRaises(AssertionError): validate_mobile(report, self.config, self.sources)

    def test_current_source_revision_change_rejected(self):
        sources = copy.deepcopy(self.sources); sources[next(iter(sources))]['sha256'] = '0' * 64
        with self.assertRaises(AssertionError): validate_mobile(self.report, self.config, sources)


if __name__ == '__main__': unittest.main()
