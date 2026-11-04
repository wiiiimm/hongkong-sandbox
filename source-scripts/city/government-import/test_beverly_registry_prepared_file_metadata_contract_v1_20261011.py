"""DRAFT counterexamples for narrowly typed registry root-verifier contract."""
import copy,unittest
from run import ROOT,read
from beverly_registry_prepared_file_metadata_contract_v1_20261011 import validated_pointer_map,check_boundary
R='docs/astra-city/government-import/government-xl-beverly-elm-exact-reference-resolution-v3-20261011/resolution.json'
class Guards(unittest.TestCase):
 def setUp(self):self.c=read(ROOT/R)['metadataLeafJsonPointers']
 def reject(self,change):
  c=copy.deepcopy(self.c);change(c)
  with self.assertRaises(AssertionError):validated_pointer_map(c)
 def test_actual_exact_four(self):self.assertEqual(len(validated_pointer_map(self.c)),4)
 def test_missing_contract(self):self.reject(lambda c:c.pop())
 def test_duplicate_contract(self):self.reject(lambda c:c.__setitem__(1,c[0]))
 def test_other_origin(self):self.reject(lambda c:c[0].__setitem__('path','unrelated.json'))
 def test_wrong_document_bytes(self):self.reject(lambda c:c[0].__setitem__('documentSHA256','0'*64))
 def test_body_pointer_cannot_exempt(self):self.reject(lambda c:c[0]['boundary'].__setitem__('pointer','/exactNativeResult/models'))
 def test_namespace_count_tampering(self):self.reject(lambda c:c[0]['namespaceRecomputed'].__setitem__('modelCount',1))
 def test_wrong_boundary_hash(self):self.reject(lambda c:c[0]['boundary'].__setitem__('canonicalSHA256','0'*64))
 def test_unlisted_pointer_still_recurse(self):self.assertFalse(check_boundary(validated_pointer_map(self.c),self.c[0]['path'],'/exactNativeResult/models',[]))
 def test_boundary_value_tampering(self):
  with self.assertRaises(AssertionError):check_boundary(validated_pointer_map(self.c),self.c[0]['path'],'/exactNativeResult/terrain/0/preparedFiles',[])
if __name__=='__main__':unittest.main()
