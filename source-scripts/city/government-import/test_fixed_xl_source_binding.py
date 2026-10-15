import unittest
from fixed_xl_source_binding import resolve_uid
class BindingTests(unittest.TestCase):
 def setUp(self):
  self.row=dict(uid=None,sourceKey='sheet/B123',indexedSourceSHA256='abc')
  self.model=dict(uid='landsd/1:0',originalSourceKey='sheet/B123',modelId='B123',sha256='abc',sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True)
 def test_exact(self):self.assertEqual(resolve_uid(self.row,[self.model]),'landsd/1:0')
 def test_absent_no_credit(self):self.assertIsNone(resolve_uid(self.row,[]))
 def test_other_key_no_credit(self):self.assertIsNone(resolve_uid(self.row,[{**self.model,'originalSourceKey':'other/B123'}]))
 def test_duplicate_rejected(self):
  with self.assertRaises(AssertionError):resolve_uid(self.row,[self.model,self.model])
 def test_changed_identity_or_bytes_rejected(self):
  for field,value in [('sha256','def'),('modelId','B456'),('identityReviewApproved',False),('placementReviewed',False),('publicationApproved',False)]:
   with self.subTest(field=field),self.assertRaises(AssertionError):resolve_uid(self.row,[{**self.model,field:value}])
 def test_existing_binding_preserved(self):self.assertEqual(resolve_uid({**self.row,'uid':'landsd/2:0'},[self.model]),'landsd/2:0')
if __name__=='__main__':unittest.main()
