import copy
import unittest
from june_garden_reuse_completed_live_v2_20261103 import ROOT, OLD, OLD_LOCAL, read, validate_mobile, validate_publication


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

    def publication_inputs(self):
        folder = ROOT / 'docs/astra-city/model-integration-20260909' / OLD.name
        return read(folder / 'publication-plan.json'), read(folder / 'publication.json'), read(OLD / 'command-001.json')

    def test_actual_dry_plan_and_successful_apply_receipt(self):
        plan, publication, command = self.publication_inputs()
        self.assertFalse(plan['published'])
        self.assertTrue(validate_publication(plan, publication, command))

    def test_dry_run_or_failed_command_cannot_count_as_apply(self):
        for key, value in [('exitCode', 1), ('stderr', 'failed')]:
            plan, publication, command = self.publication_inputs(); command[key] = value
            with self.assertRaises(AssertionError): validate_publication(plan, publication, command)
        plan, publication, command = self.publication_inputs(); command['command'].pop()
        with self.assertRaises(AssertionError): validate_publication(plan, publication, command)

    def test_changed_published_outputs_rejected(self):
        plan, publication, command = self.publication_inputs()
        publication['after']['3d-viewer/city/data/manifest.json'] = '0' * 64
        with self.assertRaises(AssertionError): validate_publication(plan, publication, command)


if __name__ == '__main__': unittest.main()
