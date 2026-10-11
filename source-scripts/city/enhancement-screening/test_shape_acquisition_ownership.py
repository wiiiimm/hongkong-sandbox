"""Acquisition retains a caller's live full source scope; no double claim/release."""
import gzip, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import shape_prepare as source


class ExistingAcquisitionOwnership(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.out = self.root / 'out'; self.out.mkdir()
        manifest = self.root / '3d-viewer/city/data/manifest.json'; manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({'officialModelCatalogues': []}))
        self.uid = 'landsd/1234:0'
        self.receipt = {'resources': ['building:' + self.uid], 'owner': 'outer-process', 'token': 'outer'}
        self.evidence = self.root / 'inputs.json.gz'
        self.evidence.write_bytes(gzip.compress(json.dumps({'rows': [self.uid], 'sources': {}, 'native': [{'sheet': 'sheet', 'cacheKey': 'stage', 'model': {'matching': {'viewerMatches': [{'uid': self.uid}]}, 'asset': {'sha256': '0' * 64, 'bytes': 50}}}]}).encode()))
        (self.out / 'source-metadata.json').write_text(json.dumps({'directories': {'sheet': {}}, 'stages': {'stage': {'artifacts': []}}}))
        self.addCleanup(patch.stopall)
        patch.object(source, 'ROOT', self.root).start()
        patch.object(source, 'R2Store', side_effect=ValueError('No remote storage for this fixture')).start()
        self.claim = patch.object(source.reservations, 'claim').start()
        self.release = patch.object(source.reservations, 'release').start()
        self.owns = patch.object(source.reservations, 'owns', return_value=True).start()
        self.database = patch.object(source, 'connect', side_effect=AssertionError('No database lookup expected')).start()

    def test_complete_external_scope_survives_failed_source_lookup(self):
        result = source.prepare(self.evidence, self.out, reservation_receipt=self.receipt)
        self.assertEqual(result['errors'], {self.uid: 'native-cache-unavailable'})
        self.claim.assert_not_called(); self.release.assert_not_called()
        self.owns.assert_called_once_with(self.receipt)

    def test_unowned_required_source_is_rejected_without_takeover(self):
        with self.assertRaisesRegex(ValueError, 'does not own all'):
            source.prepare(self.evidence, self.out, reservation_receipt={**self.receipt, 'resources': []})
        self.claim.assert_not_called(); self.release.assert_not_called()

    def test_expired_external_scope_is_rejected_without_takeover(self):
        self.owns.return_value = False
        with self.assertRaisesRegex(ValueError, 'does not own all'):
            source.prepare(self.evidence, self.out, reservation_receipt=self.receipt)
        self.claim.assert_not_called(); self.release.assert_not_called()

    def test_internally_owned_acquisition_releases_its_own_scope(self):
        self.claim.return_value = {'ok': True, 'reservation': self.receipt}
        source.prepare(self.evidence, self.out)
        self.claim.assert_called_once(); self.release.assert_called_once_with(self.receipt)

if __name__ == '__main__': unittest.main()
