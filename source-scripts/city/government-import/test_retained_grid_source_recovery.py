import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from retained_grid_source_recovery import verified_files
import test_retained_grid_source_provenance as fixtures

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class HistoricWrapperTests(unittest.TestCase):
    def fixture(self, directory):
        return fixtures.RetainedGridSourceTests().fixture(Path(directory))

    def test_reproduces_exact_wrapper_without_changing_geometry(self):
        with TemporaryDirectory(dir=HERE / 'local') as directory:
            task = Path(directory)
            patch, folder = self.fixture(directory)
            name = 'TERRAIN(TB)/T1/original.gltf'
            original = {'asset': {'version': '2.0'}, 'nodes': [{'matrix': list(range(16))}],
                'accessors': [{'count': 3}], 'buffers': [{'uri': 'original.bin'}],
                'images': [{'uri': 'photo.jpg'}], 'samplers': [{}], 'textures': [{}],
                'materials': [{'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}, 'roughnessFactor': .7}}]}
            raw = json.dumps(original).encode()
            (folder / 'terrain' / name).write_bytes(raw)
            receipt_path = folder / 'original/download.json'
            receipt = json.loads(receipt_path.read_text())
            receipt['entries'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
            receipt_path.write_text(json.dumps(receipt))
            expected = json.loads(raw)
            for key in ['images', 'samplers', 'textures']:
                expected.pop(key)
            expected['materials'][0]['pbrMetallicRoughness'].pop('baseColorTexture')
            digest = hashlib.sha256(json.dumps(expected, separators=(',', ':')).encode()).hexdigest()
            patch['meta']['source']['nativeSources'][0]['files'] = [
                {'path': 'absent/original-geometry.gltf', 'sha256': digest}]
            before = json.dumps(patch)
            refs, proof = verified_files(patch, ROOT, task / 'scripts')
            value = json.loads((ROOT / refs[0]['path']).read_text())
            for key in ['nodes', 'accessors', 'buffers']:
                self.assertEqual(value[key], original[key])
            self.assertEqual(json.dumps(patch), before)
            self.assertEqual(proof['rows'][0]['derivedWrapper']['geometryChanges'], 0)
            self.assertEqual(refs[0]['sha256'], digest)

    def test_rejects_wrapper_when_expected_hash_differs(self):
        with TemporaryDirectory(dir=HERE / 'local') as directory:
            task = Path(directory)
            patch, folder = self.fixture(directory)
            path = folder / 'terrain/TERRAIN(TB)/T1/original.gltf'
            path.write_text(json.dumps({'asset': {'version': '2.0'}}))
            receipt_path = folder / 'original/download.json'
            receipt = json.loads(receipt_path.read_text())
            receipt['entries'][0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt_path.write_text(json.dumps(receipt))
            patch['meta']['source']['nativeSources'][0]['files'][0]['path'] = 'absent/original-geometry.gltf'
            with self.assertRaisesRegex(AssertionError, 'Missing exact original'):
                verified_files(patch, ROOT, task / 'scripts')


if __name__ == '__main__':
    unittest.main()
