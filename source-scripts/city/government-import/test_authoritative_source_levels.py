import unittest
from authoritative_source_levels import bind_source_levels


class RecordedLevels(unittest.TestCase):
    def setUp(self):
        self.b = dict(uid='landsd/71329:0', objectId=71329, buildingCSUID='2231833933P20060222',
                      base=4.9, height=5.2, baseHeightHKPD=4.9, topHeightHKPD=10.1)
        self.e = {k: self.b[k] for k in ('uid', 'objectId', 'buildingCSUID')}
        self.e.update(recordedBaseHeight=4.9, recordedTopHeight=4.9 + 5.2)

    def test_real_pok_oi_literal_is_preserved(self):
        new, changes = bind_source_levels(self.e, self.b)
        self.assertEqual(new['recordedTopHeight'], 10.1)
        self.assertEqual(len(changes), 1)
        self.assertEqual(self.e['recordedTopHeight'], 10.100000000000001)

    def test_current_literal_is_unchanged(self):
        e = {**self.e, 'recordedTopHeight': 10.1}
        self.assertEqual(bind_source_levels(e, self.b), (e, []))

    def test_material_height_change_rejects(self):
        with self.assertRaises(ValueError):
            bind_source_levels({**self.e, 'recordedTopHeight': 10.2}, self.b)

    def test_material_derived_height_change_rejects(self):
        with self.assertRaises(ValueError):
            bind_source_levels({**self.e, 'recordedTopHeight': 10.2}, {**self.b, 'height': 5.3})

    def test_changed_identity_rejects(self):
        with self.assertRaises(ValueError):
            bind_source_levels({**self.e, 'objectId': 1}, self.b)

    def test_missing_or_nonfinite_source_height_rejects(self):
        for value in (None, float('nan'), float('inf'), True):
            with self.assertRaises(ValueError):
                bind_source_levels(self.e, {**self.b, 'topHeightHKPD': value})


if __name__ == '__main__':
    unittest.main()
