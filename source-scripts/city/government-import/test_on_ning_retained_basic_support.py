"""The legacy basic-support route must reject stale or unapproved dependencies."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import on_ning_retained_basic_support as policy
from run import digest, save


class RetainedBasicSupportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.here = self.root / 'source-scripts/city/government-import'
        self.here.mkdir(parents=True)
        (self.here / 'on_ning_retained_basic_support.py').write_text('fixture')
        self.legacy = self.root / 'docs/legacy'
        self.doc = self.root / 'docs/current'
        self.cat = self.root / '3d-viewer/city/data/official-models/government-xl-on-ning-20260925/catalogue.json'
        self.form = {'uid': policy.PODIUM, 'buildingCSUID': '4513719625P20060323', 'base': 6.9, 'height': 5.7}
        self.tower = {'uid': policy.TOWER, 'asset': 'source.glb.gz', 'sha256': digest(b'original'), **{k: True for k in ['sourceIdentityReviewed', 'identityReviewApproved', 'placementReviewed', 'publicationApproved']}}
        save(self.cat, {'models': [self.tower]})
        (self.cat.parent / 'source.glb.gz').write_bytes(b'original')
        save(self.root / '3d-viewer/city/data/manifest.json', {'officialModelCatalogues': [str(self.cat.relative_to(self.root / '3d-viewer'))]})
        self.support = {'rows': [{'uid': policy.TOWER, 'podiumUid': policy.PODIUM, 'accepted': True}]}
        save(self.legacy / 'support-resolution.json', self.support)
        for name in ['staged-browser.json', 'live-browser.json']:
            save(self.legacy / name, {'passed': True})
        self.installed = {'geometryChanges': 0, 'aiCalls': 0, 'catalogueSHA256': digest(self.cat.read_bytes()), 'sourceSHA256s': {policy.TOWER: self.tower['sha256']}, **{key: digest((self.legacy / name).read_bytes()) for name, key in [('support-resolution.json', 'supportResolutionSHA256'), ('staged-browser.json', 'stagedBrowserSHA256'), ('live-browser.json', 'liveBrowserSHA256')]}}
        save(self.legacy / 'installed-acceptance.json', self.installed)
        save(self.legacy / 'neighbour-inputs.json.gz', {'rows': [{'building': self.form}]})
        tile = self.root / '3d-viewer/city/data/tiles/test.json'
        save(tile, {'buildings': [self.form]})
        self.neighbours = {'rows': [{'building': self.form}], 'candidateIds': ['landsd/31718:0'], 'inputHashes': {str(tile.relative_to(self.root)): digest(tile.read_bytes())}}
        save(self.doc / 'neighbour-inputs.json.gz', self.neighbours)
        save(self.root / 'docs/astra-city/model-integration-20260909/current-source-review.json', {'snapshotId': 'current'})
        self.review = ('installed-verified', self.tower['sha256'], {'evidence': str((self.legacy / 'installed-acceptance.json').relative_to(self.root))})

    def verify(self):
        class Connection:
            def __enter__(inner): return inner
            def __exit__(inner, *args): pass
            def execute(inner, *args): return inner
            def fetchone(inner): return self.review
        with patch.multiple(policy, ROOT=self.root, HERE=self.here, LEGACY=self.legacy), patch.object(policy, 'connect', Connection):
            return policy.verify(self.doc)

    def test_exact_installed_receipt_and_unchanged_basic_source_can_be_rebound(self):
        proof = self.verify()
        self.assertEqual(proof['supportUid'], policy.PODIUM)
        self.assertFalse(proof['publication'])

    def test_source_geometry_mutation_is_rejected(self):
        (self.cat.parent / 'source.glb.gz').write_bytes(b'changed')
        with self.assertRaises(AssertionError): self.verify()

    def test_stale_support_receipt_is_rejected(self):
        self.support['rows'][0]['podiumUid'] = 'landsd/other:0'
        save(self.legacy / 'support-resolution.json', self.support)
        with self.assertRaises(AssertionError): self.verify()

    def test_missing_current_installed_review_is_rejected(self):
        self.review = None
        with self.assertRaises(AssertionError): self.verify()

    def test_changed_current_neon_source_is_rejected(self):
        self.review = ('installed-verified', 'wrong', self.review[2])
        with self.assertRaises(AssertionError): self.verify()

    def test_changed_basic_podium_height_is_rejected(self):
        self.neighbours['rows'][0]['building'] = {**self.form, 'height': 6.7}
        save(self.doc / 'neighbour-inputs.json.gz', self.neighbours)
        with self.assertRaises(AssertionError): self.verify()

    def test_suppressed_basic_podium_is_rejected(self):
        self.tower['suppressesBuildingUids'] = [policy.PODIUM]
        save(self.cat, {'models': [self.tower]})
        self.installed['catalogueSHA256'] = digest(self.cat.read_bytes())
        save(self.legacy / 'installed-acceptance.json', self.installed)
        with self.assertRaises(AssertionError): self.verify()

    def test_other_candidate_cannot_use_this_scoped_route(self):
        self.neighbours['candidateIds'] = ['landsd/other:0']
        save(self.doc / 'neighbour-inputs.json.gz', self.neighbours)
        with self.assertRaises(AssertionError): self.verify()


if __name__ == '__main__': unittest.main()
