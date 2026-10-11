"""Offline fixtures: exact schemas, rowid-linked bounds, blobs, holds and corruption."""
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

import inventory_sync as sync


class InventorySnapshotTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.source = self.root / 'source.sqlite'
        conn = sqlite3.connect(self.source)
        conn.executescript('''
            CREATE TABLE buildings(uid TEXT PRIMARY KEY, height REAL, payload BLOB, note TEXT);
            CREATE INDEX building_height ON buildings(height);
            CREATE VIRTUAL TABLE footprint_bounds USING rtree(id,min_x,max_x,min_z,max_z);
            CREATE TABLE batch_jobs(id TEXT PRIMARY KEY,status TEXT,owner TEXT,lease_until REAL,result TEXT);
            CREATE TABLE selection_members(name TEXT, uid TEXT, PRIMARY KEY(name,uid)) WITHOUT ROWID;
            CREATE TABLE generated(a INTEGER, b INTEGER GENERATED ALWAYS AS (a * 2) STORED);
            CREATE VIEW active_buildings AS SELECT uid FROM buildings;
            CREATE TRIGGER build_note AFTER INSERT ON buildings BEGIN UPDATE buildings SET note='trigger changed' WHERE uid=new.uid; END;
            PRAGMA user_version=7;
            PRAGMA application_id=1402;
        ''')
        conn.execute('INSERT INTO buildings(rowid,uid,height,payload,note) VALUES (?,?,?,?,?)', (17, 'landsd:1', 9.25, b'\x00\xff', '原始'))
        conn.execute('INSERT INTO buildings(rowid,uid,height,payload,note) VALUES (?,?,?,?,?)', (29, 'landsd:2', float('inf'), None, 'unchanged'))
        conn.execute("UPDATE buildings SET note='原始' WHERE rowid=17")
        conn.execute('INSERT INTO footprint_bounds VALUES(17,1.1,2.2,3.3,4.4)')
        conn.execute("INSERT INTO batch_jobs VALUES('held','pending','old-worker',1234.5,'{\"hold\":true}')")
        conn.execute("INSERT INTO selection_members VALUES('tourist','landsd:1')")
        conn.execute('INSERT INTO generated(a) VALUES (21)')
        conn.commit()
        conn.close()

    def tearDown(self):
        self.directory.cleanup()

    def snapshot(self):
        conn = sync.open_source(self.source)
        self.addCleanup(conn.close)
        snapshot = sync.inspect_source(conn)
        rows = {table['metadata']['name']: list(sync.source_rows(conn, table['metadata'])) for table in snapshot['tables']}
        return snapshot, rows

    def test_full_roundtrip_preserves_rowids_schema_bounds_and_historical_jobs(self):
        snapshot, rows = self.snapshot()
        output = self.root / 'restored.sqlite'
        sync.restore_sqlite(snapshot, lambda name: iter(rows[name]), output)
        restored = sync.open_source(output)
        self.addCleanup(restored.close)
        self.assertEqual(sync.inspect_source(restored), snapshot)
        self.assertEqual(restored.execute('SELECT b.uid FROM buildings b JOIN footprint_bounds f ON b.rowid=f.id').fetchall(), [('landsd:1',)])
        self.assertEqual(restored.execute('SELECT status,owner FROM batch_jobs').fetchone(), ('pending', 'old-worker'))
        self.assertEqual(restored.execute('SELECT b FROM generated').fetchone(), (42,))
        self.assertNotIn('footprint_bounds_node', rows)

    def test_missing_or_corrupted_row_cannot_publish(self):
        snapshot, rows = self.snapshot()
        rows['buildings'].pop()
        output = self.root / 'bad.sqlite'
        with self.assertRaisesRegex(ValueError, 'content mismatch'):
            sync.restore_sqlite(snapshot, lambda name: iter(rows[name]), output)
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob('*.tmp')), [])

    def test_refuses_destination_overwrite(self):
        snapshot, rows = self.snapshot()
        with self.assertRaises(FileExistsError):
            sync.restore_sqlite(snapshot, lambda name: iter(rows[name]), self.source)

    def test_read_transaction_stays_consistent_during_concurrent_sqlite_write(self):
        writer = sqlite3.connect(self.source)
        writer.execute('PRAGMA journal_mode=WAL')
        reader = sync.open_source(self.source)
        before = sync.inspect_source(reader)
        writer.execute("UPDATE batch_jobs SET status='complete'")
        writer.commit()
        self.assertEqual(sync.inspect_source(reader)['snapshot_id'], before['snapshot_id'])
        reader.close()
        new_reader = sync.open_source(self.source)
        self.assertNotEqual(sync.inspect_source(new_reader)['snapshot_id'], before['snapshot_id'])
        new_reader.close()
        writer.close()

    def test_all_rowid_aliases_shadowed_fails_explicitly(self):
        conn = sqlite3.connect(self.source)
        conn.execute('CREATE TABLE tricky(rowid INT,_rowid_ INT,oid INT)')
        conn.commit()
        with self.assertRaisesRegex(ValueError, 'all rowid aliases shadowed'):
            sync.inspect_source(conn)
        conn.close()

    def test_autoincrement_sequence_preserved(self):
        conn = sqlite3.connect(self.source)
        conn.execute('CREATE TABLE z_items(id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT)')
        conn.execute("INSERT INTO z_items(id,label) VALUES(40,'deleted')")
        conn.execute('DELETE FROM z_items')
        conn.execute("INSERT INTO z_items(id,label) VALUES(2,'retained')")
        conn.commit()
        conn.close()
        snapshot, rows = self.snapshot()
        output = self.root / 'sequence.sqlite'
        sync.restore_sqlite(snapshot, lambda name: iter(rows[name]), output)
        conn = sqlite3.connect(output)
        conn.execute("INSERT INTO z_items(label) VALUES('next')")
        self.assertEqual(conn.execute("SELECT id FROM z_items WHERE label='next'").fetchone(), (41,))
        conn.close()

    def test_value_codec_preserves_binary_and_float_values(self):
        for value in (None, b'\x00\xff', 2**63-1, '繁體\x00text', -0.0, 2.25, float('inf'), float('-inf')):
            decoded = sync.decode(json.loads(sync.packed(sync.encode(value))))
            self.assertEqual(decoded, value)
            if isinstance(value, float):
                self.assertEqual(decoded.hex(), value.hex())


@unittest.skipUnless(os.environ.get('ASTRA_TEST_LIVE_INVENTORY') == '1',
                     'Set ASTRA_TEST_LIVE_INVENTORY=1 for the pinned Neon branch')
class LiveInventorySnapshotTests(unittest.TestCase):
    def test_fixture_import_reuse_export_verify_and_indexed_lookup(self):
        from db import connect
        fixture = InventorySnapshotTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        with connect() as pg:
            imported = sync.import_snapshot(pg, fixture.source)
            reused = sync.import_snapshot(pg, fixture.source)
            self.assertTrue(reused['reused'])
            destination = fixture.root / 'neon-restored.sqlite'
            sync.export_snapshot(pg, imported['snapshot_id'], destination)
            self.assertTrue(sync.verify_snapshot(pg, imported['snapshot_id'], destination)['verified'])
            row = sync.lookup_row(pg, imported['snapshot_id'], 'buildings',
                                  {'primary_key': [['uid', 'landsd:1']]})
            self.assertEqual(row[:2], [17, 'landsd:1'])


if __name__ == '__main__':
    unittest.main()
