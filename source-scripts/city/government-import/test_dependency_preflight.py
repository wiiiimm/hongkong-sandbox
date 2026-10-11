import unittest
from dependency_preflight import inspect_dependencies


def model(uid, dependencies=None):
    return {'uid': uid, 'sha256': uid + '-source', 'supportDependencies': dependencies or []}


class DependencyPreflightTests(unittest.TestCase):
    def test_citywalk_style_replacement_catches_all_towers(self):
        towers = [model(str(i), [{'uid': 'podium', 'state': 'surveyed-footprint-fallback'}]) for i in range(5)]
        row = inspect_dependencies(towers, [model('podium')])['rows'][0]
        self.assertEqual(row['fallbackDependents'], ['0', '1', '2', '3', '4'])
        self.assertTrue(row['requiresAssemblyInvestigation'])
        self.assertFalse(row['installationApproved'])

    def test_native_support_closure_and_missing_transitive_source(self):
        result = inspect_dependencies([model('podium', [{'uid': 'foundation', 'state': 'installed'}])],
                                      [model('tower', [{'uid': 'podium', 'state': 'installed'}])])
        row = result['rows'][0]
        self.assertEqual(row['nativeSupportClosure'], ['foundation', 'podium'])
        self.assertEqual(row['blockers'][0]['affectedUids'], ['foundation'])

    def test_complete_native_pair_has_no_metadata_blocker_but_no_approval(self):
        result = inspect_dependencies([], [model('podium'), model('tower', [{'uid': 'podium', 'state': 'candidate'}])])
        self.assertEqual(result['requiresAssemblyInvestigation'], 0)
        self.assertFalse(result['publication'])
        self.assertTrue(all(not r['installationApproved'] for r in result['rows']))

    def test_candidate_cycle_is_reported(self):
        result = inspect_dependencies([], [model('a', [{'uid': 'b', 'state': 'candidate'}]),
                                           model('b', [{'uid': 'a', 'state': 'candidate'}])])
        self.assertTrue(all(any(b['reason'] == 'cyclic-native-support' for b in r['blockers']) for r in result['rows']))

    def test_string_fallback_and_unchanged_inputs(self):
        import copy
        original = [model('tower', ['podium'])]
        before = copy.deepcopy(original)
        result = inspect_dependencies(original, [model('podium')])
        self.assertEqual(result['rows'][0]['fallbackDependents'], ['tower'])
        self.assertEqual(original, before)

    def test_duplicate_uids_and_unknown_states_fail_closed(self):
        with self.assertRaises(ValueError):
            inspect_dependencies([model('a'), model('a')], [])
        with self.assertRaises(AssertionError):
            inspect_dependencies([], [model('a', [{'uid': 'b', 'state': 'probably'}])])


if __name__ == '__main__':
    unittest.main()
