import copy,unittest
from interrupted_acceptance import verify_retry

class RetryTests(unittest.TestCase):
 def setUp(self):
  self.review={'snapshot_id':'orphan','review_state':'approved-for-integration','source_sha256':'original','result':{'evidence':'prior/acceptance.json','sha256':'proof','source_sha256':'original','productionPublished':False,'effort':{'method':'scripted','ai_model':None}}}
  self.args={'uid':'landsd/1:0','source_sha':'original','prior_path':'prior/acceptance.json','prior_sha':'proof','prior_decision':{'passed':True,'checksPassed':True,'uids':['landsd/1:0'],'sourceSHA256':'original'},'browser_passed':True,'prior_installed':False,'current_review':None,'prior_released':True}
 def test_exact_orphan_allows_only_fresh_retry(self):self.assertEqual(verify_retry(self.review,**self.args)['priorApprovalSnapshot'],'orphan')
 def test_changed_source_or_evidence_rejected(self):
  for field,value in [('source_sha','changed'),('prior_sha','changed')]:
   with self.subTest(field=field),self.assertRaises(AssertionError):verify_retry(self.review,**{**self.args,field:value})
 def test_live_worker_current_decision_or_installed_rejected(self):
  for field,value in [('prior_released',False),('current_review','held'),('prior_installed',True),('browser_passed',False)]:
   with self.subTest(field=field),self.assertRaises(AssertionError):verify_retry(self.review,**{**self.args,field:value})
 def test_different_review_state_rejected(self):
  for state in ['held','installed-verified','identity-unresolved']:
   with self.subTest(state=state),self.assertRaises(AssertionError):verify_retry({**self.review,'review_state':state},**self.args)

if __name__=='__main__':unittest.main()
