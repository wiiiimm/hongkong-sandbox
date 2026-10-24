import copy
import unittest
from provisional_original_review import validate_decision, DECISIONS_PATH, DECISIONS_SHA, SUFFIX

class ProvisionalTests(unittest.TestCase):
    def setUp(self):
        self.uid='landsd/74569:0';self.sha='a'*64
        self.row={'uid':self.uid,'sha256':self.sha,'status':'held-source-component-placement',
            'native1x':True,'sourceIdentityVerifiedByRuntimeLoader':True,'placementApproved':False,
            'publicationApproved':False,'supportDependencies':[],'knownHold':None,'rimCounts':{'samples':42,'noContact':42}}
        self.result={'commit':None,'sha256':DECISIONS_SHA,'evidence':DECISIONS_PATH,
            'observation':'Provisional source-placement hold: '+str(self.row['rimCounts'])+SUFFIX,
            'productionPublished':False,'wholeLandmarkComplete':False}
        self.actual=('s1','held',self.sha,self.result)
    def check(self,row=None,actual=None):
        return validate_decision(self.uid,self.sha,actual or self.actual,row or self.row)
    def test_preserves_exact_existing_hold(self):
        result=self.check();self.assertEqual(result['result'],self.result);self.assertEqual(result['state'],'held')
    def test_substantive_decision_rejected(self):
        changed=copy.deepcopy(self.result);changed['observation']='Identity is ambiguous; requires a decision'
        with self.assertRaises(AssertionError):self.check(actual=('s1','held',self.sha,changed))
    def test_changed_original_rejected(self):
        with self.assertRaises(AssertionError):self.check(actual=('s1','held','b'*64,self.result))
    def test_review_state_change_rejected(self):
        for state in ('pending','approved-for-integration','installed-verified'):
            with self.subTest(state=state),self.assertRaises(AssertionError):self.check(actual=('s1',state,self.sha,self.result))
    def test_evidence_change_rejected(self):
        for key,value in [('sha256','b'*64),('evidence','other.json'),('commit','new'),('productionPublished',True),('wholeLandmarkComplete',True)]:
            r=copy.deepcopy(self.result);r[key]=value
            with self.subTest(key=key),self.assertRaises(AssertionError):self.check(actual=('s1','held',self.sha,r))
    def test_unresolved_dependency_rejected(self):
        r=copy.deepcopy(self.row);r['supportDependencies']=['source-other']
        with self.assertRaises(AssertionError):self.check(row=r)
    def test_non_terrain_known_hold_rejected(self):
        r=copy.deepcopy(self.row);r['knownHold']={'classification':'source-identity'}
        with self.assertRaises(AssertionError):self.check(row=r)
    def test_existing_terrain_hold_still_needs_full_new_checks(self):
        r=copy.deepcopy(self.row);r['knownHold']={'classification':'rendered-terrain-contact'}
        self.assertEqual(self.check(row=r)['state'],'held')
    def test_missing_review_rejected(self):
        with self.assertRaises(AssertionError):validate_decision(self.uid,self.sha,None,self.row)
    def test_out_of_scope_rejected(self):
        with self.assertRaises(AssertionError):validate_decision('landsd/134332:0',self.sha,self.actual,self.row)

if __name__=='__main__':unittest.main()
