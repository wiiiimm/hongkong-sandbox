"""Reject unreviewed changes while allowing the actual exact owner migration."""
import copy
import unittest
from run import ROOT,read
from refresh_fresh_native_bounds_additions_v3_20261103 import prior_entry_equal


class ExactSupportOnlyUpdate(unittest.TestCase):
    def setUp(self):
        p=ROOT/'docs/astra-city/government-import/government-xl-silvercord-lippo-five-original-source-review-v1-20261103/ROOT-SOURCE-REVIEW.json'
        self.update=read(p)['installedSupportUpdate']
        self.before=copy.deepcopy(self.update['beforeEntry']);self.after=copy.deepcopy(self.update['afterEntry'])
        self.uid=self.update['ownerUid']

    def test_actual_reviewed_update(self):
        self.assertTrue(prior_entry_equal(self.before,self.after,self.uid,self.update))
        self.assertTrue(prior_entry_equal(self.before,self.before,self.uid,None))

    def test_changed_pose_source_unknown_field_and_missing_review_rejected(self):
        for key,value in [('sha256','wrong'),('rootTranslation',[0,0,0]),('worldBounds',[]),
                          ('partialSource',True),('surpriseField',True)]:
            after=copy.deepcopy(self.after);after[key]=value
            with self.assertRaises(AssertionError,msg=key):prior_entry_equal(self.before,after,self.uid,self.update)
        with self.assertRaises(AssertionError):prior_entry_equal(self.before,self.after,self.uid,None)
        with self.assertRaises(AssertionError):prior_entry_equal(self.before,self.after,'landsd/other:0',self.update)

    def test_declared_extra_changed_fields_rejected(self):
        update=copy.deepcopy(self.update);update['changedFields'].append('worldBounds')
        with self.assertRaises(AssertionError):prior_entry_equal(self.before,self.after,self.uid,update)


if __name__=='__main__':unittest.main()
