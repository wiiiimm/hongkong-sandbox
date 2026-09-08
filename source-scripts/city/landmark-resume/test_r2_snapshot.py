import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest
from r2_snapshot import LocalStore, digest, key_for, restore, safe_path, snapshot, r2_endpoint

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'repo'; self.root.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test', '-c', 'user.email=test@example.org', 'commit', '-qm', 'fixture', '--allow-empty'], check=True)
        self.store = LocalStore(self.base / 'objects')
        self.inventory = self.base / 'inventory.json'
        self.manifest = self.base / 'manifest.json'
    def prepare(self):
        (self.root / 'cache').mkdir()
        (self.root / 'cache/a.bin').write_bytes(b'government model')
        (self.root / 'cache/copy.bin').write_bytes(b'government model')
        with sqlite3.connect(self.root / 'cache/buildings.sqlite') as c:
            c.execute('create table buildings(id integer)'); c.execute('insert into buildings values (1)')
        (self.root / 'alias').symlink_to('cache')
        rows = [{'path': p, 'kind': 'file', 'gitTracked': False, 'profiles': ['unmodified-cli-restore']} for p in ['cache/a.bin', 'cache/copy.bin', 'cache/buildings.sqlite']]
        rows.append({'path': 'alias', 'kind': 'symlink', 'linkTarget': 'cache', 'gitTracked': False, 'profiles': ['unmodified-cli-restore']})
        self.inventory.write_text(json.dumps({'rows': rows}))
        return snapshot(self.root, self.inventory, self.store, self.manifest, ['unmodified-cli-restore'])
    def clone(self):
        target = self.base / 'clone'
        subprocess.run(['git', 'clone', '-q', str(self.root), str(target)], check=True)
        return target
    def test_endpoint_validation(self):
        account = 'a' * 32
        endpoint = 'https://' + account + '.r2.cloudflarestorage.com'
        self.assertEqual(r2_endpoint({'R2_ACCOUNT_ID': account}), endpoint)
        self.assertEqual(r2_endpoint({'R2_ENDPOINT_URL': endpoint + '/'}), endpoint)
        self.assertEqual(r2_endpoint({'R2_ENDPOINT_URL': endpoint.replace('.r2.', '.eu.r2.')}), endpoint.replace('.r2.', '.eu.r2.'))
        for bad in [endpoint.replace('https:', 'http:'), endpoint + '.evil.example', endpoint + '/bucket', endpoint + '?token=secret', endpoint.replace('https://', 'https://user:secret@'), 'https://localhost', 'https://evilr2.cloudflarestorage.com']:
            with self.assertRaises(ValueError): r2_endpoint({'R2_ENDPOINT_URL': bad})
        with self.assertRaises(ValueError): r2_endpoint({'R2_ACCOUNT_ID': '../bad'})
    def test_roundtrip_and_zero_upload_resume(self):
        result = self.prepare()
        self.assertEqual(result['uploadedObjects'], 2)
        again = snapshot(self.root, self.inventory, self.store, self.manifest, ['unmodified-cli-restore'])
        self.assertEqual(again['uploadedObjects'], 0)
        target = self.clone()
        restore(target, self.manifest, self.store, digest(self.manifest))
        self.assertEqual((target / 'cache/a.bin').read_bytes(), b'government model')
        self.assertTrue((target / 'alias').is_symlink())
        with sqlite3.connect(target / 'cache/buildings.sqlite') as c: self.assertEqual(c.execute('select * from buildings').fetchall(), [(1,)])
        restore(target, self.manifest, self.store, digest(self.manifest))
    def test_corrupt_object_writes_nothing(self):
        self.prepare()
        row = json.loads(self.manifest.read_text())['files'][0]
        (self.store.root / key_for(row['sha256'])).write_bytes(b'corrupt')
        target = self.clone()
        with self.assertRaisesRegex(ValueError, 'checksum'): restore(target, self.manifest, self.store, digest(self.manifest))
        self.assertFalse((target / 'cache').exists())
    def test_secret_and_escape_paths(self):
        for path in ['../secret', '/etc/passwd', '.env.local', 'cache/.aws/credentials', 'cache/key.pem', '..\\secret']:
            with self.assertRaises(ValueError): safe_path(self.root, path)
        (self.root / 'outside').symlink_to(self.base)
        with self.assertRaises(ValueError): safe_path(self.root, 'outside/secret')
    def test_refuses_conflicting_existing_material(self):
        self.prepare(); target = self.clone()
        (target / 'cache').mkdir(); (target / 'cache/a.bin').write_bytes(b'different')
        with self.assertRaisesRegex(ValueError, 'overwrite'): restore(target, self.manifest, self.store, digest(self.manifest))
        self.assertEqual((target / 'cache/a.bin').read_bytes(), b'different')
    def test_manifest_hash_and_duplicate_rejected(self):
        self.prepare(); target = self.clone()
        with self.assertRaisesRegex(ValueError, 'Manifest checksum'): restore(target, self.manifest, self.store, '0' * 64)
        data = json.loads(self.manifest.read_text()); data['files'].append(data['files'][0]); self.manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Duplicate'): restore(target, self.manifest, self.store, digest(self.manifest))

if __name__ == '__main__': unittest.main()
