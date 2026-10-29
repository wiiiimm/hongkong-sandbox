import copy
import unittest
from retained_parent_install_contract_v1_20261029 import terrain_delta, retained_views

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.before=[dict(url='keep',sha256='a'),dict(url='old',sha256='b')]
        self.plan=[dict(replaces=dict(url='old',sha256='b'),destination='new',sha256='c',area='area',resolution=5)]
        self.after=[dict(url='keep',sha256='a'),dict(url='new',sha256='c',area='area',resolution=5)]
        self.expected={'one':'s1','two':'s2'}
        self.rows=[dict(uid=u,sourceSHA256=s,width=w,time=t,active=True,visible=True,fullyFramed=True,fallbackFaces=0)for u,s in self.expected.items()for w in [390,1280]for t in ['15:00','22:00']]
    def test_exact_replacement(self):terrain_delta(self.before,self.after,self.plan)
    def test_retained_metadata_change_rejected(self):
        self.after[0]['sha256']='changed'
        with self.assertRaises(AssertionError):terrain_delta(self.before,self.after,self.plan)
    def test_wrong_predecessor_hash_rejected(self):
        self.plan[0]['replaces']['sha256']='changed'
        with self.assertRaises(AssertionError):terrain_delta(self.before,self.after,self.plan)
    def test_extra_removal_rejected(self):
        self.after.pop(0)
        with self.assertRaises(AssertionError):terrain_delta(self.before,self.after,self.plan)
    def test_old_patch_still_drawn_rejected(self):
        self.after.insert(1,self.before[1])
        with self.assertRaises(AssertionError):terrain_delta(self.before,self.after,self.plan)
    def test_missing_replacement_rejected(self):
        self.after[-1]=self.before[-1]
        with self.assertRaises(AssertionError):terrain_delta(self.before,self.after,self.plan)
    def test_retained_views(self):retained_views(self.rows,self.expected,[390,1280])
    def test_missing_actor_rejected(self):
        with self.assertRaises(AssertionError):retained_views(self.rows[:-1],self.expected,[390,1280])
    def test_duplicate_view_rejected(self):
        self.rows[-1]=copy.deepcopy(self.rows[0])
        with self.assertRaises(AssertionError):retained_views(self.rows,self.expected,[390,1280])
    def test_changed_asset_rejected(self):
        self.rows[-1]['sourceSHA256']='changed'
        with self.assertRaises(AssertionError):retained_views(self.rows,self.expected,[390,1280])
    def test_invisible_actor_rejected(self):
        self.rows[-1]['visible']=False
        with self.assertRaises(AssertionError):retained_views(self.rows,self.expected,[390,1280])
    def test_fallback_rejected(self):
        self.rows[-1]['fallbackFaces']=1
        with self.assertRaises(AssertionError):retained_views(self.rows,self.expected,[390,1280])

if __name__=='__main__':unittest.main()
