"""Full-cohort adverse checks retain both NULL sources and unrelated rows."""
import copy
import unittest
from run import read
from silvercord_lippo_installed_readback_v1_20261103 import BASE,PREVIOUS,GROUND,verify_fixed_cohort


class WholeXLReadback(unittest.TestCase):
    def setUp(self):
        self.before=read(BASE/PREVIOUS)
        self.after=copy.deepcopy(self.before)
        self.sources={r['uid']:r['indexedSourceSHA256']for r in self.before['rows']if r['uid']in GROUND}
        self.after['counts']=dict(total=521,installedVerified=429,remaining=92)
        for row in self.after['rows']:
            if row['uid']in GROUND:
                row['installedVerified']=True;row['runtimeSourceSHA256']=self.sources[row['uid']]

    def test_exact_full_cohort_transition(self):
        self.assertTrue(verify_fixed_cohort(self.before,self.after,self.sources))

    def test_missing_null_duplicate_key_and_unrelated_change_rejected(self):
        for kind in ['null','duplicate','unrelated','source','count']:
            changed=copy.deepcopy(self.after)
            if kind=='null':changed['rows']=[r for r in changed['rows']if r['uid']is not None]
            elif kind=='duplicate':changed['rows'][0]['sourceKey']=changed['rows'][1]['sourceKey']
            elif kind=='unrelated':next(r for r in changed['rows']if r['uid']not in GROUND)['unexpected']=True
            elif kind=='source':next(r for r in changed['rows']if r['uid']in GROUND)['runtimeSourceSHA256']='different'
            else:changed['counts']['installedVerified']=430
            with self.assertRaises(AssertionError,msg=kind):verify_fixed_cohort(self.before,changed,self.sources)


if __name__=='__main__':unittest.main()
