import json
import pathlib
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import inventory


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.db = self.root/'inventory.sqlite'
        self.building = dict(uid='landsd/1:0', id='landsd/1', objectId=1, buildingCSUID='source1',
                             tile='0_0', centre=[1, 1], rings=[[[0, 0], [2, 0], [1, 2]]],
                             base=0, height=5, baseHeightHKPD=None, topHeightHKPD=None)
        self.manifest = dict(counts={'buildings': 1}, tiles=[dict(id='0_0', url='city/data/tile.json', counts={'buildings': 1})])
        self.write('city/data/manifest.json', self.manifest)
        self.write('city/data/tile.json', dict(id='0_0', buildings=[self.building]))
        self.write('city/data/review-sections.json', dict(sections=[dict(id='01.1')]))

    def write(self, path, data):
        dest = self.root/path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(data))

    def run_sync(self):
        return inventory.sync(self.root, self.db)

    def test_repeat_skips_and_preserves_selection(self):
        self.assertEqual(self.run_sync()['updatedBuildings'], 1)
        with sqlite3.connect(self.db) as c:
            c.execute("INSERT INTO selections VALUES('trial','landsd/1:0','landmark',1)")
        result = self.run_sync()
        self.assertEqual(result['updatedBuildings'], 0)
        self.assertEqual(result['skippedTiles'], 1)
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM selections').fetchone()[0], 1)

    def test_change_and_removal_preserve_history(self):
        self.run_sync()
        self.building['height'] = 9
        self.write('city/data/tile.json', dict(id='0_0', buildings=[self.building]))
        self.assertEqual(self.run_sync()['updatedBuildings'], 1)
        self.manifest.update(tiles=[], counts={'buildings': 0})
        self.write('city/data/manifest.json', self.manifest)
        self.assertEqual(self.run_sync()['buildings'], 0)
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('SELECT height,active FROM buildings').fetchone(), (9, 0))

    def test_duplicate_rolls_back(self):
        self.run_sync()
        self.manifest['tiles'][0]['counts']['buildings'] = 2
        self.manifest['counts']['buildings'] = 2
        self.write('city/data/manifest.json', self.manifest)
        self.write('city/data/tile.json', dict(id='0_0', buildings=[self.building]*2))
        with self.assertRaisesRegex(ValueError, 'Duplicate active UID'):
            self.run_sync()
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM buildings WHERE active=1').fetchone()[0], 1)

    def test_interrupt_rolls_back(self):
        self.run_sync()
        self.building['height'] = 99
        self.write('city/data/tile.json', dict(id='0_0', buildings=[self.building]))
        original = inventory.local
        def interrupt(viewer, relative):
            if relative.endswith('review-sections.json'):
                raise KeyboardInterrupt()
            return original(viewer, relative)
        with patch.object(inventory, 'local', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_sync()
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('SELECT height FROM buildings').fetchone()[0], 5)
        self.assertEqual(self.run_sync()['updatedBuildings'], 1)

    def test_missing_input_rejected(self):
        self.run_sync()
        (self.root/'city/data/tile.json').unlink()
        with self.assertRaises(FileNotFoundError):
            self.run_sync()

    def test_model_hash_and_identity(self):
        asset = self.root/'city/data/a.glb'
        asset.write_bytes(b'fixture-model')
        model = dict(uid=self.building['uid'], objectId=1, buildingCSUID='source1', asset='a.glb',
                     sha256=inventory.digest(asset.read_bytes()), bytes=asset.stat().st_size)
        self.manifest['officialModelCatalogues'] = ['city/data/models.json']
        self.write('city/data/manifest.json', self.manifest)
        self.write('city/data/models.json', {'models': [model]})
        self.assertEqual(self.run_sync()['progressiveModels'], 1)
        asset.write_bytes(b'corrupt-model')
        with self.assertRaisesRegex(ValueError, 'checksum/size'):
            self.run_sync()
        asset.write_bytes(b'fixture-model')
        model['buildingCSUID'] = 'wrong'
        self.write('city/data/models.json', {'models': [model]})
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.run_sync()


if __name__ == '__main__':
    unittest.main()
