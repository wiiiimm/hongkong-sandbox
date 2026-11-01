"""Counterexamples derived from the completed actual three-case browser report."""
import copy
import unittest
from run import ROOT, read
from one_peking_cycle_runtime_contract_v1_20261101 import verify_atomic

class RuntimeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        batch = 'government-xl-one-peking-after-twin-cycle-atomic-lifecycle-v1-20261101'
        cls.report = read(ROOT / 'docs/astra-city/government-import' / batch / 'report.json')
        desktop = read(ROOT / 'docs/astra-city/government-import/government-xl-one-peking-after-twin-cycle-private-browser-v4-20261101/1280/staged-browser.json')
        by_uid = {v['uid']: dict(uid=v['uid'], sha256=v['sourceSHA256'], triangles=v['originalTriangles']) for v in desktop['views'] if 'time' in v}
        cls.models = list(by_uid.values())
    def test_actual_complete_report(self):
        self.assertTrue(verify_atomic(self.report, self.models))
    def rejected(self, edit):
        report = copy.deepcopy(self.report)
        edit(report)
        with self.assertRaises(AssertionError):
            verify_atomic(report, self.models)
    def test_missing_member_failure(self):
        self.rejected(lambda r: r['cases'].pop())
    def test_duplicate_member_failure(self):
        self.rejected(lambda r: r['cases'][2].update(failedUid=r['cases'][1]['failedUid']))
    def test_changed_source_bytes(self):
        self.rejected(lambda r: r['cases'][1]['sources'][0].update(sha256='0'*64))
    def test_hidden_basic_fallback(self):
        self.rejected(lambda r: r['cases'][1].update(failureKeptAllBasics=False))
    def test_partial_group_transition(self):
        self.rejected(lambda r: r['cases'][1]['audit']['transitions'].append(dict(active=['landsd/233985:0'])))
    def test_recorded_atomic_violation(self):
        self.rejected(lambda r: r['cases'][1]['audit']['violations'].append(dict(kind='partial-native-group')))

if __name__ == '__main__':
    unittest.main()
