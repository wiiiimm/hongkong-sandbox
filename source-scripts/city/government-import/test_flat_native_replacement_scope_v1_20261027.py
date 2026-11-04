import copy
import unittest
from flat_native_replacement_scope_v1_20261027 import verify


class ExactReplacement(unittest.TestCase):
    def setUp(self):
        self.old = dict(nativeMesh={}, meta=dict(parentTerrain='city/data/terrain.json', parentSha256='root', targetUids=['old']), coarseCells=[1, 1, 2, 2])
        # Real mesh presence is explicit; an empty dict must never pass.
        self.old['nativeMesh'] = {'position': [0, 1, 0], 'index': [0]}
        self.new = copy.deepcopy(self.old)
        self.new['meta']['targetUids'] = ['old', 'new']
        self.new['coarseCells'] = [0, 0, 3, 3]
        record = dict(url='old.json', sha256='exact', coarseCells=[1, 1, 2, 2], targetUids=['old'])
        self.receipt = dict(uids=['new'], replacedNativeTerrain=[record])
        self.scope = dict(uids=['old', 'new'], positiveAreaTerrainOverlaps=1,
                          regionalCoarseCells=[0, 0, 3, 3], terrainContacts=[dict(url='old.json', coarseOverlapAreaM2=1, packedContacts=[])])

    def check(self):
        return verify(self.scope, self.receipt, self.old, self.new)

    def test_exact_complete_retention(self):
        self.assertEqual(self.check(), dict(url='old.json', sha256='exact', retainedUids=['old']))

    def test_unrelated_overlap_rejected(self):
        self.scope['terrainContacts'][0]['url'] = 'other.json'
        with self.assertRaises(AssertionError): self.check()

    def test_additional_overlap_rejected(self):
        self.scope['terrainContacts'].append(dict(url='other.json', coarseOverlapAreaM2=0, packedContacts=[dict(overlapAreaM2=1)]))
        with self.assertRaises(AssertionError): self.check()

    def test_lost_or_extra_targets_rejected(self):
        for ids in [['new'], ['old', 'new', 'other'], ['old', 'new', 'new']]:
            self.new['meta']['targetUids'] = ids
            with self.subTest(ids=ids), self.assertRaises(AssertionError): self.check()

    def test_partial_domain_or_wrong_root_rejected(self):
        self.new['coarseCells'] = [0, 0, 1, 3]
        with self.assertRaises(AssertionError): self.check()
        self.new['coarseCells'] = [0, 0, 3, 3]
        self.new['meta']['parentSha256'] = 'other'
        with self.assertRaises(AssertionError): self.check()

    def test_changed_original_obligations_rejected(self):
        self.old['meta']['targetUids'] = ['different']
        with self.assertRaises(AssertionError): self.check()

    def test_ambiguous_replacement_rejected(self):
        self.receipt['replacedNativeTerrain'] *= 2
        with self.assertRaises(AssertionError): self.check()


if __name__ == '__main__': unittest.main()
