import unittest
from retained_terrain_scope import retained_scope


class RetainedScopeTests(unittest.TestCase):
    def test_coverage_target_does_not_invent_installed_model(self):
        result = retained_scope(['a', 'b'], {'a': {}}, [{'uid': 'a'}, {'uid': 'b'}])
        self.assertEqual(result['nativeUids'], ['a'])
        self.assertEqual(result['basicUids'], ['b'])
        self.assertEqual(result['declaredTargetUids'], ['a', 'b'])

    def test_missing_target_blocks_complete_scope(self):
        with self.assertRaisesRegex(AssertionError, 'missing'):
            retained_scope(['a', 'b'], {'a': {}}, [{'uid': 'a'}])

    def test_inline_native_cannot_be_relabelled_basic(self):
        with self.assertRaisesRegex(AssertionError, 'Inline native'):
            retained_scope(['a', 'b'], {'a': {}}, [{'uid': 'a'}, {'uid': 'b', 'modelGeometry': {'index': [0]}}])

    def test_no_installed_native_cannot_use_replacement_contract(self):
        with self.assertRaisesRegex(AssertionError, 'No installed native'):
            retained_scope(['b'], {}, [{'uid': 'b'}])


if __name__ == '__main__':
    unittest.main()
