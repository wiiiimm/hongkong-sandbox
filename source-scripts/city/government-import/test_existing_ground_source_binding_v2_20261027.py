import unittest
from selected_original_existing_ground_runtime_v2_20261027 import bind_recorded_heights


class SourceHeightBinding(unittest.TestCase):
    def setUp(self):
        self.entry = dict(uid='landsd/173532:0', objectId=173532, buildingCSUID='exact', publicationApproved=False)
        self.form = dict(uid='landsd/173532:0', objectId=173532, buildingCSUID='exact', baseHeightHKPD=21.3, topHeightHKPD=100.4)

    def test_only_missing_fields_added_without_mutating_input(self):
        bound, added = bind_recorded_heights(self.entry, self.form)
        self.assertEqual(added, dict(recordedBaseHeight=21.3, recordedTopHeight=100.4))
        self.assertNotIn('recordedBaseHeight', self.entry)
        self.assertFalse(bound['publicationApproved'])
        self.assertEqual(set(bound) - set(self.entry), set(added))

    def test_existing_correct_fields_unchanged(self):
        bound, _ = bind_recorded_heights(self.entry, self.form)
        again, added = bind_recorded_heights(bound, self.form)
        self.assertEqual(again, bound)
        self.assertEqual(added, {})

    def test_existing_wrong_or_null_fields_rejected(self):
        for value in [None, 0, 21.30001]:
            with self.assertRaises(AssertionError):
                bind_recorded_heights(dict(self.entry, recordedBaseHeight=value), self.form)

    def test_wrong_component_identity_rejected(self):
        for key in ['uid', 'objectId', 'buildingCSUID']:
            with self.assertRaises(AssertionError):
                bind_recorded_heights({**self.entry, key: 'other'}, self.form)


if __name__ == '__main__':
    unittest.main()
