"""Keep cross-source or missing component evidence out of Neon followups."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('component_followups',
    Path(__file__).with_name('xl-original-component-followups.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class SourceBindings(unittest.TestCase):
    def setUp(self):
        self.old = {'sourceSHA256': 'tower'}
        self.sources = {'landsd/1:0': self.old, 'landsd/2:0': {'sourceSHA256': 'support'}}
        self.checks = [{'uid': 'landsd/1:0', 'supportUid': 'landsd/2:0',
                        'sourceSHA256': 'tower', 'supportSHA256': 'support'}]

    def test_identical_source_receipt(self):
        self.assertEqual(runner.source_interfaces('landsd/1:0', self.old, self.sources, self.checks), self.checks)

    def test_changed_source_record_rejected(self):
        with self.assertRaises(AssertionError):
            runner.source_interfaces('landsd/1:0', self.old,
                {**self.sources, 'landsd/1:0': {'sourceSHA256': 'different'}}, self.checks)

    def test_missing_interface_rejected(self):
        with self.assertRaises(AssertionError):
            runner.source_interfaces('landsd/1:0', self.old, self.sources, [])

    def test_different_tower_receipt_rejected(self):
        with self.assertRaises(AssertionError):
            runner.source_interfaces('landsd/1:0', self.old, self.sources,
                [{**self.checks[0], 'sourceSHA256': 'different'}])

    def test_different_support_receipt_rejected(self):
        with self.assertRaises(AssertionError):
            runner.source_interfaces('landsd/1:0', self.old, self.sources,
                [{**self.checks[0], 'supportSHA256': 'different'}])


if __name__ == '__main__':
    unittest.main()
