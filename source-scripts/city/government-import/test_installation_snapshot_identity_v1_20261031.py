"""Regression for the actual identical-payload V1/V2 retry collision."""
import copy,unittest
from run import ROOT,read
from installation_snapshot_identity_v1_20261031 import identity
P=ROOT/'docs/astra-city/government-import/government-xl-villa-premiere89917-'

class InstallationIdentityTests(unittest.TestCase):
    def setUp(self):
        base=ROOT/'docs/astra-city/government-import'
        self.a=read(base/'government-xl-villa-premiere89917-five-original-installed-v1-20261031/acceptance.json')
        self.b=read(base/'government-xl-villa-premiere89917-five-original-installed-v2-20261031/acceptance.json')
        self.parts=[dict(uid=u,sourceSHA256=s)for u,s in sorted(self.a['sourceSHA256ByUid'].items())]
    def test_actual_old_colliding_payloads_rejected(self):
        self.assertEqual(self.a,self.b)
        with self.assertRaises(ValueError):identity(self.parts,self.a,'government-xl-villa-attempt-v3')
    def test_distinct_transactions_separate_without_mutating_source_evidence(self):
        a={**self.a,'transactionBatch':'government-xl-villa-attempt-v3'};b={**self.a,'transactionBatch':'government-xl-villa-attempt-v4'};before=copy.deepcopy((self.parts,a,b))
        self.assertNotEqual(identity(self.parts,a,a['transactionBatch']),identity(self.parts,b,b['transactionBatch']));self.assertEqual((self.parts,a,b),before)
    def test_same_bound_attempt_is_stable_and_changed_source_is_distinct(self):
        a={**self.a,'transactionBatch':'government-xl-villa-attempt-v3'};one=identity(self.parts,a,a['transactionBatch']);self.assertEqual(one,identity(self.parts,a,a['transactionBatch']))
        changed=copy.deepcopy(self.parts);changed[0]['sourceSHA256']='0'*64;self.assertNotEqual(one,identity(changed,a,a['transactionBatch']))

if __name__=='__main__':unittest.main()
