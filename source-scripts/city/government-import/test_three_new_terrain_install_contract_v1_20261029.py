import unittest
from copy import deepcopy
from three_new_terrain_install_contract_v1_20261029 import terrain_delta


class NewTerrainTests(unittest.TestCase):
    def setUp(self):
        self.before = [dict(url='old', sha256='old-source', resolution=5, area='old-area')]
        self.plan = [dict(destination=str(i), sha256='sha' + str(i), resolution=5, area='new') for i in range(3)]
        self.after = deepcopy(self.before) + [dict(url=p['destination'], sha256=p['sha256'], resolution=p['resolution'], area=p['area']) for p in self.plan]

    def check(self): terrain_delta(self.before, self.after, self.plan)
    def test_exact_append(self): self.check()
    def test_old_metadata_change_rejected(self):
        self.after[0]['area'] = 'changed'
        with self.assertRaises(AssertionError): self.check()
    def test_missing_old_entry_rejected(self):
        self.after.pop(0)
        with self.assertRaises(AssertionError): self.check()
    def test_missing_member_rejected(self):
        self.after.pop()
        with self.assertRaises(AssertionError): self.check()
    def test_wrong_source_rejected(self):
        self.after[-1]['sha256'] = 'changed'
        with self.assertRaises(AssertionError): self.check()
    def test_duplicate_member_rejected(self):
        self.plan[1]['destination'] = self.plan[0]['destination']
        with self.assertRaises(AssertionError): self.check()
    def test_implicit_replacement_rejected(self):
        self.plan[0]['replaces'] = dict(url='old')
        with self.assertRaises(AssertionError): self.check()
    def test_reused_destination_rejected(self):
        self.plan[0]['destination'] = 'old'
        with self.assertRaises(AssertionError): self.check()


if __name__ == '__main__': unittest.main()
