"""Reject incomplete, stale or damaged original terrain caches before reuse."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('indexed_terrain', HERE / 'xl-indexed-terrain-continuation.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)


class TerrainCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / '6-SW-11D'
        self.entries = []
        for name, raw in [('TERRAIN/original.gltf', b'{"asset":{"version":"2.0"}}'), ('TERRAIN/original.bin', b'original-mesh-buffer')]:
            path = self.folder / 'terrain' / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            self.entries.append({'name': name, 'sha256': runner.digest(raw)})
        self.receipt = {'sheet': self.folder.name, 'directorySHA256': 'pinned-directory',
                        'terrainGeometryIncluded': True, 'entries': self.entries}
        self.directory = {'sheet': self.folder.name, 'directorySHA256': 'pinned-directory'}
        self.write_metadata()

    def write_metadata(self):
        for name, data in [('original/download.json', self.receipt), ('directory/result.json', self.directory)]:
            path = self.folder / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data))

    def test_intact_receipt_reuses_original_files(self):
        self.assertIsNotNone(runner.verified_terrain(self.folder))

    def test_corrupt_mesh_buffer_is_not_reused(self):
        (self.folder / 'terrain/TERRAIN/original.bin').write_bytes(b'changed')
        self.assertIsNone(runner.verified_terrain(self.folder))

    def test_missing_buffer_is_not_reused(self):
        (self.folder / 'terrain/TERRAIN/original.bin').unlink()
        self.assertIsNone(runner.verified_terrain(self.folder))

    def test_model_only_receipt_is_not_terrain_proof(self):
        self.receipt['terrainGeometryIncluded'] = False; self.write_metadata()
        self.assertIsNone(runner.verified_terrain(self.folder))

    def test_directory_hash_drift_is_not_reused(self):
        self.directory['directorySHA256'] = 'changed-directory'; self.write_metadata()
        self.assertIsNone(runner.verified_terrain(self.folder))

    def test_wrong_sheet_receipt_is_not_reused(self):
        self.receipt['sheet'] = '6-SW-12C'; self.write_metadata()
        self.assertIsNone(runner.verified_terrain(self.folder))


if __name__ == '__main__': unittest.main()
