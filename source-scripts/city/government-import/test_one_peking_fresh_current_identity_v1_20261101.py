"""Named identity never waives unrelated identity or physical failures."""
import copy,unittest
import one_peking_fresh_current_identity_v1_20261101 as b
class IdentityTests(unittest.TestCase):
 def setUp(self):
  self.raw=dict(uid=b.OWN,sourceSHA256=b.OWN_SHA,passed=False,reasons=list(b.RAW),proof=dict(identityAccepted=False),installationApproved=False)
  self.named=dict(foreignSilhouetteInterpretationPassed=True,identityAccepted=False,physicalAccepted=False,collisionExemption=False,ownUID=b.OWN,foreignUID=b.FOREIGN,ordinaryForeignLimitM2=1)
  self.rows=[dict(ownMode=a,foreignMode=c,target=d,allForeignEffectiveExcessM2=.022)for a in b.MODES for c in b.MODES for d in ['current','provider']]
 def run_case(self):return b.accept_named(self.raw,self.named,self.rows)
 def test_complete_named_identity_preserves_raw(self):
  raw=copy.deepcopy(self.raw);p=self.run_case();self.assertTrue(p['passed']);self.assertEqual(p['rawFullCellIdentity'],raw);self.assertEqual(self.raw,raw);self.assertFalse(p['proof']['identityAccepted'])
 def test_no_physical_or_publication_credit(self):
  p=self.run_case();self.assertFalse(p['physicalAccepted']);self.assertFalse(p['collisionExemption']);self.assertFalse(p['installationApproved'])
 def test_unknown_reason_rejected(self):self.raw['reasons'].append('different-source');self.assertRaises(AssertionError,self.run_case)
 def test_wrong_source_revision(self):self.raw['sourceSHA256']='x'*64;self.assertRaises(AssertionError,self.run_case)
 def test_wrong_source(self):self.raw['uid']=b.FOREIGN;self.assertRaises(AssertionError,self.run_case)
 def test_wrong_foreign(self):self.named['foreignUID']='landsd/1:0';self.assertRaises(AssertionError,self.run_case)
 def test_raised_limit_rejected(self):self.named['ordinaryForeignLimitM2']=2;self.assertRaises(AssertionError,self.run_case)
 def test_excess_over_one_metre_rejected(self):self.rows[0]['allForeignEffectiveExcessM2']=1.00001;self.assertRaises(AssertionError,self.run_case)
 def test_missing_coordinate_combination(self):self.rows.pop();self.assertRaises(AssertionError,self.run_case)
 def test_duplicate_coordinate_combination(self):self.rows[0]=self.rows[1];self.assertRaises(AssertionError,self.run_case)
 def test_nan_excess_rejected(self):self.rows[0]['allForeignEffectiveExcessM2']=float('nan');self.assertRaises(AssertionError,self.run_case)
 def test_preapproved_physical_input_rejected(self):self.named['physicalAccepted']=True;self.assertRaises(AssertionError,self.run_case)
if __name__=='__main__':unittest.main()
