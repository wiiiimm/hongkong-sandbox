import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from retained_grid_source_provenance import verified_files


class RetainedGridSourceTests(unittest.TestCase):
    def fixture(self, root, corrupt=False):
        folder = root / 'scripts/local/cache/sheets/11-NW-19B'
        name = 'TERRAIN(TB)/T1/original.gltf'
        data = b'original government geometry'
        digest = hashlib.sha256(data).hexdigest()
        target = folder / 'terrain' / name
        target.parent.mkdir(parents=True)
        target.write_bytes(b'changed' if corrupt else data)
        receipt = {'terrainGeometryIncluded': True, 'directorySHA256': 'directory',
                   'sheet': '11-NW-19B', 'entries': [{'name': name, 'sha256': digest}]}
        for relative, value in [('original/download.json', receipt),
                                ('directory/result.json', {'sheet': '11-NW-19B', 'directorySHA256': 'directory'})]:
            path = folder / relative
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(value))
        patch = {'renderedElev': [1, 2, 3, 4], 'meta': {'source': {'nativeSources': [
            {'sheet': '11-NW-19B', 'files': [{'path': 'absent/original.gltf', 'sha256': digest}]}]}}}
        return patch, folder

    def test_missing_legacy_path_resolves_only_identical_receipted_bytes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            patch, _ = self.fixture(root)
            before = json.dumps(patch)
            refs, proof = verified_files(patch, root, root / 'scripts')
            self.assertEqual(len(refs), 1)
            self.assertTrue(proof['rows'][0]['byteIdentical'])
            self.assertEqual(json.dumps(patch), before)
            self.assertEqual(len(proof['rows'][0]['receiptRefs']), 2)

    def test_rejects_changed_source_bytes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            patch, _ = self.fixture(root, corrupt=True)
            with self.assertRaisesRegex(AssertionError, 'Missing exact original'):
                verified_files(patch, root, root / 'scripts')

    def test_rejects_mismatched_directory_receipt(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            patch, folder = self.fixture(root)
            (folder / 'directory/result.json').write_text(json.dumps(
                {'sheet': '11-NW-19B', 'directorySHA256': 'different'}))
            with self.assertRaisesRegex(AssertionError, 'Missing exact original'):
                verified_files(patch, root, root / 'scripts')


if __name__ == '__main__':
    unittest.main()
