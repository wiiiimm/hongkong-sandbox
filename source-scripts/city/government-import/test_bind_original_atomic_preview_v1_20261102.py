import unittest,copy
from bind_original_atomic_preview_v1_20261102 import atomic_catalogue
class AtomicBindingTests(unittest.TestCase):
 def setUp(self):
  self.c={'models':[dict(uid='landsd/1:0',sha256='a'*64,buildingCSUID='a',proceduralWindows=False,publicationApproved=False,placementReviewed=False),dict(uid='landsd/2:0',sha256='b'*64,buildingCSUID='b',proceduralWindows=False,publicationApproved=False,placementReviewed=False,supportDependencies=[dict(uid='landsd/1:0',sha256='a'*64,buildingCSUID='a',state='installed')])]}
 def test_only_atomic_field_changes_input_immutable(self):
  original=copy.deepcopy(self.c);r=atomic_catalogue(self.c);self.assertEqual(self.c,original)
  for m in r['models']:self.assertEqual(m.pop('activationGroup'),['landsd/1:0','landsd/2:0'])
  self.assertEqual(r,original)
 def test_reject_wrong_source_support(self):
  self.c['models'][1]['supportDependencies'][0]['sha256']='c'*64
  with self.assertRaises(AssertionError):atomic_catalogue(self.c)
 def test_reject_existing_atomic_declaration(self):
  self.c['models'][0]['activationGroup']=['landsd/1:0']
  with self.assertRaises(AssertionError):atomic_catalogue(self.c)
 def test_reject_approved_fixture(self):
  self.c['models'][0]['publicationApproved']=True
  with self.assertRaises(AssertionError):atomic_catalogue(self.c)
if __name__=='__main__':unittest.main()
