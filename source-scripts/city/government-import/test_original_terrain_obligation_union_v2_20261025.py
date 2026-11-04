import copy
import unittest
import test_original_terrain_point_contact_v1_20261025 as fixtures
from original_terrain_point_contact_v2_20261025 import verify
from original_terrain_obligation_union_v2_20261025 import merge


class ObligationUnionTests(unittest.TestCase):
    def setUp(self):
        f=fixtures.PointContactTests(); f.setUp()
        self.scope=dict(f.scope,currentNativeActors=10,uids=['landsd/1:0'],intersectingForms=2)
        self.proof=verify(self.scope,f.new,f.root,{'old.json':f.old})
        self.forms=[dict(uid='landsd/1:0',base=15),dict(uid='landsd/2:0',base=16)]

    def merge(self, **extra):
        return merge({self.forms[0]['uid']:self.forms[0]},self.forms,self.scope,
                     native_count=10,target_uids=['landsd/1:0'],expected_count=2,**extra)

    def test_point_cannot_be_admitted_without_replay(self):
        with self.assertRaises(AssertionError): self.merge()

    def test_replayed_corner_keeps_every_obligation(self):
        result=self.merge(point_context=self.proof,replayed_point_contacts=self.proof)
        self.assertEqual(set(result),{r['uid']for r in self.forms})

    def test_changed_corner_record_is_rejected(self):
        changed=copy.deepcopy(self.proof);changed['rows'][0]['sharedPoint'][1]+=1
        with self.assertRaises(AssertionError): self.merge(point_context=changed,replayed_point_contacts=self.proof)

    def test_changed_current_form_is_not_overwritten(self):
        with self.assertRaises(AssertionError):
            merge({'landsd/1:0':dict(uid='landsd/1:0',base=99)},self.forms,self.scope,
                  native_count=10,target_uids=['landsd/1:0'],expected_count=2,
                  point_context=self.proof,replayed_point_contacts=self.proof)


if __name__ == '__main__': unittest.main()
