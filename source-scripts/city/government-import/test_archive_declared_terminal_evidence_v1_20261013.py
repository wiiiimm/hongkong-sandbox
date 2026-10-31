import tempfile
import unittest
from pathlib import Path
from hashlib import sha256
from archive_declared_terminal_evidence_v1_20261013 import archive_declared_external


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'repo'
        self.root.mkdir()
        self.archive = self.root / 'archive'
        self.external = self.base / 'terminal.log'
        self.external.write_bytes(b'actual terminal\nexit 1\n')
        self.pin = dict(path=str(self.external), sha256=sha256(self.external.read_bytes()).hexdigest())

    def test_archive_is_byte_identical_and_freezer_paths_are_inside_root(self):
        inside = self.root / 'source.json'
        inside.write_bytes(b'{}')
        paths, records = archive_declared_external({inside, self.external}, self.root, self.archive, [self.pin])
        self.assertIn(inside, paths)
        self.assertTrue(all(p.is_relative_to(self.root) for p in paths))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['originalReference'], self.pin)
        target = self.root / records[0]['archivedReference']['path']
        self.assertEqual(target.read_bytes(), self.external.read_bytes())
        self.assertEqual(archive_declared_external({inside, self.external}, self.root, self.archive, [self.pin]), (paths, records))

    def test_undeclared_external_fails_before_writes(self):
        with self.assertRaises(AssertionError):
            archive_declared_external({self.external}, self.root, self.archive, [])
        self.assertFalse(self.archive.exists())

    def test_changed_original_fails_before_writes(self):
        self.external.write_bytes(b'changed')
        with self.assertRaises(AssertionError):
            archive_declared_external({self.external}, self.root, self.archive, [self.pin])
        self.assertFalse(self.archive.exists())

    def test_existing_different_archive_is_not_overwritten(self):
        self.archive.mkdir()
        dest = self.archive / (self.pin['sha256'] + '-' + self.external.name)
        dest.write_bytes(b'wrong')
        with self.assertRaises(AssertionError):
            archive_declared_external({self.external}, self.root, self.archive, [self.pin])
        self.assertEqual(dest.read_bytes(), b'wrong')

    def test_same_basename_with_different_bytes_keeps_both(self):
        folder = self.base / 'another'
        folder.mkdir()
        other = folder / self.external.name
        other.write_bytes(b'other terminal')
        pin = dict(path=str(other), sha256=sha256(other.read_bytes()).hexdigest())
        paths, records = archive_declared_external({self.external, other}, self.root, self.archive, [self.pin, pin])
        self.assertEqual(len(paths), 2)
        self.assertEqual(len(records), 2)

    def test_repository_symlink_to_undeclared_external_is_rejected(self):
        link = self.root / 'external-link'
        link.symlink_to(self.external)
        with self.assertRaises(AssertionError):
            archive_declared_external({link}, self.root, self.archive, [self.pin])

    def test_archive_outside_repository_is_rejected(self):
        with self.assertRaises(AssertionError):
            archive_declared_external({self.external}, self.root, self.base / 'outside', [self.pin])


if __name__ == '__main__':
    unittest.main()
