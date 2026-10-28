"""Reject incomplete live evidence and verify exact byte rollback."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import elegant_live_install_v1_20261028 as install


class LiveEvidence(unittest.TestCase):
    def setUp(self):
        self.models = install.read(install.stage.STAGE / 'catalogue.json')['models']
        private = install.read(install.BASE / (install.stage.P + 'supported-activation-browser-v3-20261028') / 'browser/report.json')
        self.report = copy.deepcopy(private)
        self.report.update(passed=True, liveInstalledHTTP=True, catalogueAndTerrainSubstitution=False)
        for row in self.report['cases']:
            for field, original in [('activeFallbackContract', 'activeSuppression'),
                                    ('baseFallbackContract', 'baseSuppression'),
                                    ('recoveredFallbackContract', 'restoredSuppression')]:
                row[field] = copy.deepcopy(row[original])
            row['evictedFallbackContract'] = copy.deepcopy(row['baseSuppression'])

    def test_complete_contract(self):
        self.assertTrue(install.verify_live(self.report, self.models))

    def reject(self, change):
        report = copy.deepcopy(self.report)
        change(report)
        with self.assertRaises(AssertionError):
            install.verify_live(report, self.models)

    def test_private_substitution_rejected(self):
        self.reject(lambda r: r.update(catalogueAndTerrainSubstitution=True))

    def test_missing_peer_failure_case(self):
        self.reject(lambda r: r['cases'].pop())

    def test_partial_transition_rejected(self):
        self.reject(lambda r: r['cases'][0]['audit']['violations'].append({'kind': 'partial-native-group'}))

    def test_wrong_native_bytes(self):
        self.reject(lambda r: r['cases'][0]['sources'][0].update(sha256='0' * 64))

    def test_missing_retained_basic_root(self):
        self.reject(lambda r: r['cases'][0]['baseFallbackContract'].update(retainedBasicSupports=[]))

    def test_failed_suppression_contract(self):
        self.reject(lambda r: r['cases'][0]['activeFallbackContract'].update(suppressionMatchesActivation=False))

    def test_rollback_restores_bytes_and_removes_new_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'tile.json').write_bytes(b'changed tile')
            (root / 'new.glb').write_bytes(b'new original')
            with patch.object(install, 'ROOT', root):
                errors = install.restore({'tile.json': b'original bytes\n', 'new.glb': None})
            self.assertEqual(errors, [])
            self.assertEqual((root / 'tile.json').read_bytes(), b'original bytes\n')
            self.assertFalse((root / 'new.glb').exists())


if __name__ == '__main__':
    unittest.main()
