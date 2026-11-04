import json
import tempfile
import unittest
from pathlib import Path
from byte_exact_evidence import pack, restore, verify


class ByteExactEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.original = self.root / 'frozen.json.gz'
        self.data = bytes(range(256)) * 3
        self.original.write_bytes(self.data)
        self.manifest = pack(self.original, root=self.root, chunk_bytes=113)

    def edit(self, mutate):
        d = json.loads(self.manifest.read_text())
        mutate(d)
        self.manifest.write_text(json.dumps(d))

    def test_exact_roundtrip_and_existing_original(self):
        self.original.unlink()
        self.assertEqual(restore(self.manifest, root=self.root).read_bytes(), self.data)
        self.assertEqual(restore(self.manifest, root=self.root).read_bytes(), self.data)

    def test_corrupt_chunk_never_publishes_original(self):
        self.original.unlink()
        (self.manifest.parent / 'part-00000.bin').write_bytes(b'broken')
        with self.assertRaises(ValueError): restore(self.manifest, root=self.root)
        self.assertFalse(self.original.exists())
        self.assertFalse(list(self.root.glob('*.restore-*')))

    def test_missing_chunk_rejects(self):
        (self.manifest.parent / 'part-00001.bin').unlink()
        with self.assertRaises(FileNotFoundError): verify(self.manifest, root=self.root)

    def test_changed_order_rejects(self):
        self.edit(lambda d: d['chunks'].reverse())
        with self.assertRaises(ValueError): verify(self.manifest, root=self.root)

    def test_truncated_inventory_rejects_complete_hash(self):
        self.edit(lambda d: d['chunks'].pop())
        with self.assertRaises(ValueError): verify(self.manifest, root=self.root)

    def test_escape_rejects(self):
        self.edit(lambda d: d.update(originalPath='../outside.json.gz'))
        with self.assertRaises(ValueError): restore(self.manifest, root=self.root)

    def test_never_overwrite_changed_original(self):
        self.original.write_bytes(b'other evidence')
        with self.assertRaises(ValueError): restore(self.manifest, root=self.root)
        self.assertEqual(self.original.read_bytes(), b'other evidence')


if __name__ == '__main__': unittest.main()
