import copy,unittest
from exact_single_terrain_replacement_v1_20261102 import replacement
class ReplacementTests(unittest.TestCase):
    def setUp(self):
        self.one=dict(url='city/data/old.json',sha256='a'*64,retainedUids=['landsd/1:0'])
        self.many=dict(url=self.one['url'],path='3d-viewer/'+self.one['url'],sha256=self.one['sha256'],targetUids=self.one['retainedUids'])
    def test_equal_schemas_and_input_immutable(self):
        entry=dict(replaces=copy.deepcopy(self.one),replacesMany=[copy.deepcopy(self.many)]);before=copy.deepcopy(entry)
        self.assertEqual(replacement(entry),self.one);self.assertEqual(entry,before)
        self.assertEqual(replacement(dict(replacesMany=[self.many])),self.one)
    def test_conflicting_hash_rejected(self):
        other=dict(self.many,sha256='b'*64)
        with self.assertRaises(AssertionError):replacement(dict(replaces=self.one,replacesMany=[other]))
    def test_multiple_old_terrains_rejected(self):
        with self.assertRaises(AssertionError):replacement(dict(replacesMany=[self.many,self.many]))
    def test_wrong_path_rejected(self):
        with self.assertRaises(AssertionError):replacement(dict(replacesMany=[dict(self.many,path='3d-viewer/city/data/wrong.json')]))
    def test_duplicate_retained_targets_rejected(self):
        with self.assertRaises(AssertionError):replacement(dict(replaces=dict(self.one,retainedUids=['landsd/1:0']*2)))
    def test_missing_descriptor_rejected(self):
        with self.assertRaises(AssertionError):replacement({})
if __name__=='__main__':unittest.main()
