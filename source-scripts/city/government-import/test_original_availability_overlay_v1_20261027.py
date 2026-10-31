import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from original_availability_overlay_v1_20261027 import stage


class ImmutableAvailabilityOverlay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        folder = self.root / '3d-viewer/city/data/models'
        (folder / 'assets').mkdir(parents=True)
        asset = b'unchanged-original'
        self.group = ['landsd/1:0', 'landsd/2:0', 'landsd/3:0']
        self.before = {'models': [{'uid': self.group[-1], 'asset': 'assets/original.gz',
                                  'sha256': hashlib.sha256(asset).hexdigest(), 'bytes': len(asset),
                                  'publicationApproved': False}], 'counts': {'packedModels': 1}}
        self.after = copy.deepcopy(self.before)
        self.after['models'][0]['activationGroup'] = self.group
        (folder / 'assets/original.gz').write_bytes(asset)
        self.old = folder / 'catalogue.json'
        self.old.write_text(json.dumps(self.before))
        self.source = self.root / 'private.json'
        self.source.write_text(json.dumps(self.after))
        self.spec = dict(url='city/data/models/catalogue.json', destination='city/data/models/catalogue-group.json',
                         source='private.json', uid=self.group[-1], activationGroup=self.group,
                         beforeSHA256=hashlib.sha256(self.old.read_bytes()).hexdigest(),
                         afterSHA256=hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.manifest = {'officialModelCatalogues': ['other.json', self.spec['url']], 'counts': {'a': 9}}
        self.edits = {}

    def run_stage(self):
        return stage(self.root, self.spec, self.manifest, self.edits, Path.read_bytes)

    def rejected(self):
        before = copy.deepcopy(self.manifest)
        with self.assertRaises(AssertionError):
            self.run_stage()
        self.assertEqual(before, self.manifest)
        self.assertFalse(self.edits)

    def test_exact_annotation_is_staged_only(self):
        result = self.run_stage()
        self.assertFalse(result['publicationApprovedByThisHelper'])
        self.assertEqual(json.loads(self.old.read_bytes()), self.before)
        new = self.root / '3d-viewer' / self.spec['destination']
        self.assertFalse(new.exists())
        self.assertEqual(json.loads(self.edits[new]), self.after)
        self.assertEqual(self.manifest, {'officialModelCatalogues': ['other.json', self.spec['destination']], 'counts': {'a': 9}})

    def test_moved_directory_rejected(self):
        self.spec['destination'] = 'city/data/elsewhere/new.json'
        self.rejected()

    def test_changed_old_catalogue_rejected(self):
        self.old.write_text('{}')
        self.rejected()

    def test_changed_source_rejected(self):
        self.source.write_text('{}')
        self.rejected()

    def test_approval_change_rejected_even_with_matching_hash(self):
        self.after['models'][0]['publicationApproved'] = True
        self.source.write_text(json.dumps(self.after))
        self.spec['afterSHA256'] = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.rejected()

    def test_changed_asset_rejected(self):
        (self.old.parent / 'assets/original.gz').write_bytes(b'corrupt')
        self.rejected()

    def test_existing_destination_rejected(self):
        (self.old.parent / 'catalogue-group.json').write_text('{}')
        self.rejected()

    def test_duplicate_manifest_entry_rejected(self):
        self.manifest['officialModelCatalogues'].append(self.spec['url'])
        self.rejected()

    def test_escaping_destination_rejected(self):
        self.spec['destination'] = '../escape.json'
        self.rejected()


if __name__ == '__main__':
    unittest.main()
