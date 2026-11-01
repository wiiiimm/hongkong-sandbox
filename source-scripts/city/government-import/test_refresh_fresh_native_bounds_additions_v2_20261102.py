"""Regression checks for missing/conflicting actors in incremental inventory chains."""
import copy
import unittest
from refresh_fresh_native_bounds_additions_v2_20261102 import complete_inputs

class Census(unittest.TestCase):
    def setUp(self):
        self.base={'uid':'a','rawCurrentEntry':{'uid':'a','sha256':'x','placementReviewed':True},'currentBuilding':{'uid':'a'},'source':{'path':'a','sha256':'x'}}
        self.add={'uid':'b','entry':{'uid':'b','sha256':'y'},'building':{'uid':'b'},'path':'b'}
        self.bounds=[{'uid':'a','sourceSHA256':'x'},{'uid':'b','sourceSHA256':'y'}]
    def test_merge_preserves_complete_metadata_without_mutating_inputs(self):
        before=copy.deepcopy([self.base,self.add]);r=complete_inputs([self.base],[self.add],self.bounds)
        self.assertEqual(set(r),{'a','b'});self.assertTrue(r['a']['rawCurrentEntry']['placementReviewed'])
        self.assertEqual([self.base,self.add],before)
    def test_missing_actor_is_rejected(self):
        with self.assertRaises(AssertionError):complete_inputs([self.base],[],self.bounds)
    def test_repeated_actor_is_rejected(self):
        with self.assertRaises(AssertionError):complete_inputs([self.base,self.base],[],self.bounds)
    def test_changed_source_is_rejected(self):
        self.add['entry']['sha256']='z'
        with self.assertRaises(AssertionError):complete_inputs([self.base],[self.add],self.bounds)
    def test_cross_wired_form_is_rejected(self):
        self.add['building']['uid']='c'
        with self.assertRaises(AssertionError):complete_inputs([self.base],[self.add],self.bounds)
    def test_duplicate_bound_is_rejected(self):
        with self.assertRaises(AssertionError):complete_inputs([self.base],[self.add],self.bounds+[self.bounds[0]])

if __name__=='__main__':unittest.main()
