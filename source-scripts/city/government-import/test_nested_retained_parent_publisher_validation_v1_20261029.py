"""Check private dispatch restoration and preservation of canonical checks."""
import unittest
from pathlib import Path
from types import SimpleNamespace
from primrose_compound_foundation_v2_20261015 import module
from nested_retained_parent_publisher_validation_v1_20261029 import private_validator, unchanged_checks, nested_validate


class DispatchTests(unittest.TestCase):
    def publisher(self):
        return module('test_retained_parent_publisher', Path(__file__).parent.parent/'island-detail-integration/publish.py')

    def test_canonical_assertions_retained(self):
        unchanged_checks()

    def test_dispatch_restored(self):
        p = self.publisher(); old = p.validate_patch
        with private_validator(p):
            self.assertIs(p.validate_patch, nested_validate)
        self.assertIs(p.validate_patch, old)

    def test_dispatch_restored_on_failure(self):
        p = self.publisher(); old = p.validate_patch
        with self.assertRaises(RuntimeError):
            with private_validator(p):
                raise RuntimeError('test failure')
        self.assertIs(p.validate_patch, old)

    def test_unknown_publisher_validator_rejected(self):
        def replacement(a,b): pass
        p = SimpleNamespace(validate_patch=replacement)
        with self.assertRaises(AssertionError):
            with private_validator(p):
                self.fail('Unverified publisher accepted')
        self.assertIs(p.validate_patch, replacement)


if __name__ == '__main__':
    unittest.main()
