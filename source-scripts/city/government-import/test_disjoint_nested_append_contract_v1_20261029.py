from copy import deepcopy
import unittest
from disjoint_nested_append_contract_v1_20261029 import POLICY,FIELD,verify_append
class ContractTests(unittest.TestCase):
    def setUp(self):
        self.old=dict(w=20,h=20,elev=[1,2],renderedElev=[1,2],meta=dict(targetUids=['landsd/1:0'],georef=dict(aE=5)),patchExclusions=[[0,0,1,1]],patches=[dict(coarseCells=[2,2,4,4],meta=dict(targetUids=['landsd/1:0']),nativeMesh=dict(position=[1,2,3],source={}))])
        self.child=dict(coarseCells=[8,8,10,10],meta=dict(targetUids=['landsd/2:0']),nativeMesh=dict(position=[4,5,6],index=[0],source={}))
        self.proof=dict(policy=POLICY,beforeParent='old',child='child',newTargetUids=['landsd/2:0'])
        self.refs=dict(old=self.old,child=self.child,proof=self.proof)
        self.new=deepcopy(self.old);self.new['patches'].append(deepcopy(self.child));self.new['meta']['targetUids']=['landsd/1:0','landsd/2:0'];self.new['meta'][FIELD]=dict(policy=POLICY,proof='proof')
    def check(self):return verify_append(self.new,self.refs.__getitem__)
    def test_exact_append_preserves_original(self):self.assertEqual(self.check(),self.old)
    def test_grid_edit_rejected(self):
        self.new['elev'][0]=9
        with self.assertRaises(AssertionError):self.check()
    def test_rendered_grid_edit_rejected(self):
        self.new['renderedElev'][0]=9
        with self.assertRaises(AssertionError):self.check()
    def test_old_child_edit_rejected(self):
        self.new['patches'][0]['nativeMesh']['position'][0]=9
        with self.assertRaises(AssertionError):self.check()
    def test_child_removal_rejected(self):
        self.new['patches'].pop(0)
        with self.assertRaises(AssertionError):self.check()
    def test_new_child_edit_rejected(self):
        self.new['patches'][1]['nativeMesh']['position'][0]=9
        with self.assertRaises(AssertionError):self.check()
    def test_overlap_rejected_even_if_bound(self):
        self.child['coarseCells']=[3,3,5,5];self.new['patches'][1]=deepcopy(self.child)
        with self.assertRaises(AssertionError):self.check()
    def test_prior_exclusion_rejected(self):
        self.child['coarseCells']=[0,0,2,2];self.new['patches'][1]=deepcopy(self.child)
        with self.assertRaises(AssertionError):self.check()
    def test_target_drop_rejected(self):
        self.new['meta']['targetUids']=['landsd/2:0']
        with self.assertRaises(AssertionError):self.check()
    def test_unrelated_metadata_change_rejected(self):
        self.new['meta']['changed']=True
        with self.assertRaises(AssertionError):self.check()
    def test_unproven_marker_rejected(self):
        self.new['meta'][FIELD]['policy']='anything'
        with self.assertRaises(AssertionError):self.check()
    def test_reused_target_rejected(self):
        self.proof['newTargetUids']=['landsd/1:0']
        with self.assertRaises(AssertionError):self.check()
    def test_added_coordinated_exception_rejected(self):
        self.child['nativeMesh']['source']['coordinatedBoundary']={};self.new['patches'][1]=deepcopy(self.child)
        # A marker with any value, including empty, must not grant an exception.
        with self.assertRaises(AssertionError):self.check()
if __name__=='__main__':unittest.main()
