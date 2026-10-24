"""Source provenance boundaries for fresh revisions and immutable legacy runs."""
import copy, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import native_source_receipt as source
from run import digest


class Connection:
    def __init__(self, value): self.value = value
    def execute(self, *_): return self
    def fetchone(self): return self.value


class SourceReceiptTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(); self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name); self.patcher = patch.object(source, 'ROOT', self.root)
        self.patcher.start(); self.addCleanup(self.patcher.stop)
        asset = self.root / 'local/new.glb.gz'; asset.parent.mkdir(); asset.write_bytes(b'new official source')
        sha = digest(asset.read_bytes()); model = {'asset': {'sha256': sha}, 'modelId': 'B347431642801063C1'}
        original = {'uid': 'landsd/213352:0', 'modelId': model['modelId'], 'sourceSHA256': sha,
            'source': {'building': {'objectId': 213352}}, 'model': model, 'assetPath': 'local/new.glb.gz',
            'priorModelId': 'B347431642801063C0', 'priorSourceSHA256': 'old'}
        self.receipt = {'jobId': 'job', 'publication': False, 'newlyInstalled': 0,
            'evidenceRefs': [], 'rows': [original]}
        self.path = self.root / 'docs/astra-city/government-import/government-xl-test/result.json'
        self.path.parent.mkdir(parents=True); self.row = {**original,
            'candidate': {'path': 'local/new.glb.gz'}, 'native': {'model': model}}
        self.write()

    def write(self):
        self.path.write_text(json.dumps(self.receipt))
        self.row['native']['revisionAcquisition'] = {'path': str(self.path.relative_to(self.root)),
            'sha256': digest(self.path.read_bytes()), 'jobId': 'job'}

    def con(self, status='complete', stage='explicit-current-government-revision-acquisition-v1'):
        return Connection((stage, status, self.receipt))

    def test_fresh_original_has_its_own_receipt_without_legacy_membership(self):
        source.verify(self.con(), self.row)

    def test_pending_or_other_stage_cannot_supply_a_revision(self):
        for con in (self.con(status='running'), self.con(stage='some-other-complete-job'), Connection(None)):
            with self.assertRaises(AssertionError): source.verify(con, self.row)

    def test_wrong_uid_or_model_metadata_cannot_inherit_receipt(self):
        row = copy.deepcopy(self.row); row['native']['model']['asset']['sha256'] = 'forged'
        with self.assertRaises(AssertionError): source.verify(self.con(), row)
        row = copy.deepcopy(self.row); row['uid'] = 'landsd/122298:0'
        with self.assertRaises(AssertionError): source.verify(self.con(), row)

    def test_ambiguous_originals_and_tampered_asset_are_rejected(self):
        self.receipt['rows'].append(copy.deepcopy(self.receipt['rows'][0])); self.write()
        with self.assertRaises(AssertionError): source.verify(self.con(), self.row)
        self.receipt['rows'].pop(); self.write()
        (self.root / 'local/new.glb.gz').write_bytes(b'altered geometry')
        with self.assertRaises(AssertionError): source.verify(self.con(), self.row)

    def test_changed_pinned_evidence_is_rejected(self):
        self.receipt['evidenceRefs'] = [{'path': 'local/new.glb.gz', 'sha256': 'wrong'}]; self.write()
        with self.assertRaises(AssertionError): source.verify(self.con(), self.row)

    def test_legacy_result_still_requires_exact_immutable_sha(self):
        row = {'native': {'cacheKey': 'old-key', 'resultSha': 'old-sha'}}
        source.verify(Connection(('old-sha',)), row)
        source.verify(Connection({'result_sha': 'old-sha'}), row)
        with self.assertRaises(AssertionError): source.verify(Connection(('different',)), row)


if __name__ == '__main__': unittest.main()
